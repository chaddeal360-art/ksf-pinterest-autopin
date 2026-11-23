#!/usr/bin/env python3
"""Create Pinterest pins for new Kindred Space Finds posts.

Reads published posts from the WordPress REST API, finds the vertical
Pinterest image each post carries (<figure class="ksf-pinsave"><img ...>),
and creates one pin per post through the Pinterest API v5. Posts already
pinned are recorded in state/posted.json so they are never pinned twice.

Environment variables
  PINTEREST_APP_ID, PINTEREST_APP_SECRET, PINTEREST_REFRESH_TOKEN
      Used to get a fresh access token on every run (recommended).
  PINTEREST_ACCESS_TOKEN
      Alternative to the three above (expires after about 30 days).
  PINTEREST_BOARD_ID      Default board for every pin (required).
  BOARD_MAP               Optional JSON: {"<category id>": "<board id>"}.
  SITE_URL                Default https://kindredspacefinds.com
  MAX_PINS_PER_RUN        Default 2.
  ONLY_AFTER              Optional ISO date: ignore posts published before it.
  PINTEREST_API_BASE      Set to https://api-sandbox.pinterest.com/v5 to test
                          with a Trial-access app (sandbox token).
  DRY_RUN                 "1" to print what would be pinned without posting.
"""
import base64
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

API = "https://api.pinterest.com/v5"
# Trial-access apps can only create pins in the sandbox (visible only to you).
PIN_API = os.environ.get("PINTEREST_API_BASE") or API
UA = "ksf-autopin/1.0 (+https://kindredspacefinds.com)"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(ROOT, "state", "posted.json")


def http(method, url, data=None, headers=None, form=False):
    headers = dict(headers or {})
    headers.setdefault("User-Agent", UA)
    body = None
    if data is not None:
        if form:
            body = urllib.parse.urlencode(data).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = json.dumps(data).encode()
            headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {"raw": raw[:500]}


class PinFigureParser(HTMLParser):
    """Finds the first <img> inside <figure class="... ksf-pinsave ...">."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.img = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "figure" and "ksf-pinsave" in (a.get("class") or "").split():
            self.depth += 1
        elif tag == "figure" and self.depth:
            self.depth += 1
        elif tag == "img" and self.depth and self.img is None:
            self.img = a

    def handle_endtag(self, tag):
        if tag == "figure" and self.depth:
            self.depth -= 1


def extract_pin(content_html):
    p = PinFigureParser()
    p.feed(content_html or "")
    if not p.img or not p.img.get("src"):
        return None
    return {
        "image": p.img["src"],
        "alt": p.img.get("alt", ""),
        "description": p.img.get("data-pin-description", ""),
    }


def clean(text, limit):
    text = re.sub(r"<[^>]+>", "", html.unescape(text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut.rstrip(",;:") + "…"


def access_token():
    app_id = os.environ.get("PINTEREST_APP_ID")
    secret = os.environ.get("PINTEREST_APP_SECRET")
    refresh = os.environ.get("PINTEREST_REFRESH_TOKEN")
    if app_id and secret and refresh:
        basic = base64.b64encode(f"{app_id}:{secret}".encode()).decode()
        status, data = http(
            "POST",
            f"{API}/oauth/token",
            {"grant_type": "refresh_token", "refresh_token": refresh},
            {"Authorization": f"Basic {basic}"},
            form=True,
        )
        if status == 200 and data.get("access_token"):
            return data["access_token"]
        sys.exit(f"Could not refresh the Pinterest token ({status}): {data}")
    token = os.environ.get("PINTEREST_ACCESS_TOKEN")
    if token:
        return token
    sys.exit("Set PINTEREST_APP_ID/APP_SECRET/REFRESH_TOKEN or PINTEREST_ACCESS_TOKEN.")


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


def fetch_posts(site):
    posts, page = [], 1
    while page <= 5:  # newest 250 posts is plenty
        url = (f"{site}/wp-json/wp/v2/posts?status=publish&per_page=50&page={page}"
               "&orderby=date&order=desc&_fields=id,date_gmt,link,title,excerpt,content,categories")
        status, data = http("GET", url)
        if status == 400 or not data:
            break
        if status != 200 or not isinstance(data, list):
            sys.exit(f"WordPress API error {status}: {str(data)[:300]}")
        posts.extend(data)
        if len(data) < 50:
            break
        page += 1
    return posts


def main():
    site = os.environ.get("SITE_URL", "https://kindredspacefinds.com").rstrip("/")
    dry = os.environ.get("DRY_RUN") == "1"
    max_pins = int(os.environ.get("MAX_PINS_PER_RUN", "2"))
    only_after = os.environ.get("ONLY_AFTER", "")
    default_board = os.environ.get("PINTEREST_BOARD_ID", "")
    board_map = json.loads(os.environ.get("BOARD_MAP") or "{}")
    if not default_board and not board_map and not dry:
        sys.exit("Set PINTEREST_BOARD_ID.")

    state = load_state()
    done = state.setdefault("posted", {})
    candidates = []
    for post in fetch_posts(site):
        if str(post["id"]) in done:
            continue
        if only_after and post.get("date_gmt", "") < only_after:
            continue
        pin = extract_pin(post.get("content", {}).get("rendered", ""))
        if not pin:
            continue
        board = next((board_map[str(c)] for c in post.get("categories", []) if str(c) in board_map),
                     default_board)
        candidates.append((post, pin, board))

    # Oldest first, so a backlog goes out in publishing order.
    candidates.sort(key=lambda c: c[0].get("date_gmt", ""))
    batch = candidates[:max_pins]
    print(f"{len(candidates)} post(s) waiting for a pin; pinning {len(batch)} this run.")
    if not batch:
        return

    token = None if dry else access_token()
    for post, pin, board in batch:
        title = clean(post["title"]["rendered"], 100)
        description = clean(pin["description"] or post["excerpt"]["rendered"], 800)
        body = {
            "board_id": board,
            "title": title,
            "description": description,
            "link": post["link"],
            "alt_text": clean(pin["alt"], 500),
            "media_source": {"source_type": "image_url", "url": pin["image"]},
        }
        if dry:
            print("DRY RUN:", json.dumps(body, ensure_ascii=False, indent=2))
            continue
        status, data = http("POST", f"{PIN_API}/pins", body, {"Authorization": f"Bearer {token}"})
        if status in (200, 201) and data.get("id"):
            done[str(post["id"])] = {
                "pin_id": data["id"],
                "board_id": board,
                "link": post["link"],
                "pinned_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            save_state(state)
            print(f"Pinned post {post['id']} -> pin {data['id']}: {title}")
            time.sleep(5)
        else:
            print(f"Failed to pin post {post['id']} ({status}): {data}", file=sys.stderr)
            if status in (401, 403):
                sys.exit(1)


if __name__ == "__main__":
    main()
