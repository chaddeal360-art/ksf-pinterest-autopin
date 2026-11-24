#!/usr/bin/env python3
"""Post the pins in schedule/pins.csv on their scheduled day.

Each row of the CSV is one pin: id, date (YYYY-MM-DD, UTC), board (name),
title, description, link, image, alt. A row is posted on or after its date,
once, and only when:
  * it has an image: the `image` column, or a file pins/<id>.jpg|.jpeg|.png|.webp
    in this repo (served from raw.githubusercontent.com, so the repo must be public);
  * its link is live (a scheduled WordPress post returns 404 until it publishes).
Rows that aren't ready wait for a later run. Posted rows are recorded in
state/scheduled.json, so a pin is never posted twice.

Environment variables (besides the Pinterest credentials autopin.py reads)
  BOARD_IDS          Optional JSON {"<board name>": "<board id>"}. Without it,
                     board names are looked up in the account's boards.
  MAX_SCHEDULED_PER_RUN  Default 1.
  TODAY              Optional YYYY-MM-DD override, for testing.
  DRY_RUN            "1" to print what would be posted without posting.
"""
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from autopin import API, PIN_API, UA, access_token, clean, http  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEDULE = os.path.join(ROOT, "schedule", "pins.csv")
STATE_FILE = os.path.join(ROOT, "state", "scheduled.json")
PIN_DIR = os.path.join(ROOT, "pins")
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"posted": {}}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
        f.write("\n")


def load_schedule():
    with open(SCHEDULE, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("id") or "").strip()]
    ids = [r["id"] for r in rows]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        sys.exit(f"Duplicate ids in schedule/pins.csv: {', '.join(sorted(dupes))}")
    return rows


def image_for(row):
    if (row.get("image") or "").strip():
        return row["image"].strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "chaddeal360-art/ksf-pinterest-autopin")
    branch = os.environ.get("IMAGE_BRANCH", "main")
    for ext in IMAGE_EXTS:
        name = row["id"] + ext
        if os.path.exists(os.path.join(PIN_DIR, name)):
            return f"https://raw.githubusercontent.com/{repo}/{branch}/pins/{urllib.parse.quote(name)}"
    return None


def link_is_live(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return 200 <= r.status < 300
    except Exception:
        return False


def account_boards(token):
    """{board name (lowercase): board id} for every board on the account."""
    boards, bookmark = {}, None
    for _ in range(10):
        url = f"{API}/boards?page_size=100" + (f"&bookmark={bookmark}" if bookmark else "")
        status, data = http("GET", url, headers={"Authorization": f"Bearer {token}"})
        if status != 200:
            print(f"Could not list boards ({status}): {data}", file=sys.stderr)
            break
        for b in data.get("items", []):
            boards[b.get("name", "").strip().lower()] = b["id"]
        bookmark = data.get("bookmark")
        if not bookmark:
            break
    return boards


def has_credentials():
    env = os.environ
    return bool((env.get("PINTEREST_APP_ID") and env.get("PINTEREST_APP_SECRET")
                 and env.get("PINTEREST_REFRESH_TOKEN")) or env.get("PINTEREST_ACCESS_TOKEN"))


def main():
    dry = os.environ.get("DRY_RUN") == "1"
    today = os.environ.get("TODAY") or time.strftime("%Y-%m-%d", time.gmtime())
    max_pins = int(os.environ.get("MAX_SCHEDULED_PER_RUN", "1"))
    board_ids = {k.strip().lower(): v for k, v in json.loads(os.environ.get("BOARD_IDS") or "{}").items()}

    state = load_state()
    done = state.setdefault("posted", {})
    due = sorted((r for r in load_schedule() if r["date"] <= today and r["id"] not in done),
                 key=lambda r: (r["date"], r["id"]))
    print(f"Today (UTC) {today}: {len(due)} scheduled pin(s) due and not yet posted.")

    ready = []
    for row in due:
        if len(ready) >= max_pins:
            break
        image = image_for(row)
        if not image:
            print(f"  {row['id']}: waiting for an image (add pins/{row['id']}.jpg or fill the image column).")
            continue
        if not link_is_live(row["link"]):
            print(f"  {row['id']}: post not live yet ({row['link']}).")
            continue
        ready.append((row, image))

    if not ready:
        print("Nothing ready to post this run.")
        return
    if not dry and not has_credentials():
        print("Pinterest credentials are not set yet (see README); nothing posted.")
        return

    token = None if dry else access_token()
    names = account_boards(token) if token else {}

    for row, image in ready:
        board_name = row["board"].strip()
        board = board_ids.get(board_name.lower()) or names.get(board_name.lower())
        body = {
            "board_id": board or f"<board '{board_name}'>",
            "title": clean(row["title"], 100),
            "description": clean(row["description"], 800),
            "link": row["link"],
            "alt_text": clean(row.get("alt") or row["title"], 500),
            "media_source": {"source_type": "image_url", "url": image},
        }
        if dry:
            print(f"DRY RUN {row['id']}:", json.dumps(body, ensure_ascii=False, indent=2))
            continue
        if not board:
            print(f"  {row['id']}: no board named '{board_name}' on the account; create it or set BOARD_IDS.",
                  file=sys.stderr)
            continue
        status, data = http("POST", f"{PIN_API}/pins", body, {"Authorization": f"Bearer {token}"})
        if status in (200, 201) and data.get("id"):
            done[row["id"]] = {
                "pin_id": data["id"],
                "board_id": board,
                "link": row["link"],
                "pinned_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            save_state(state)
            print(f"Pinned {row['id']} -> pin {data['id']}: {body['title']}")
            time.sleep(5)
        else:
            print(f"Failed to pin {row['id']} ({status}): {data}", file=sys.stderr)
            if status in (401, 403):
                sys.exit(1)


if __name__ == "__main__":
    main()
