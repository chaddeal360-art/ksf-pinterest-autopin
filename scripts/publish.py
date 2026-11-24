#!/usr/bin/env python3
"""Publish ready drafts from drafts/<slug>/ to Kindred Space Finds (WordPress).

Each draft folder holds:
  post.json     metadata (see drafts/README.md)
  content.html  the post body; {{HERO_URL}}, {{PIN_URL}} and {{<KEY>_URL}} for
                extra images are replaced with the uploaded media URLs.

For every draft whose "date" (Asia/Saigon) has arrived and that is not yet in
state/published.json, the script downloads the Unsplash photos, builds the
hero, any extra images and the 1000x1500 Pinterest image in the site's pin
style, uploads them as JPG, creates the post and records it.

Environment
  WP_USER            WordPress username (default "admin")
  WP_APP_PASSWORD    WordPress Application Password (required unless DRY_RUN)
  SITE_URL           default https://kindredspacefinds.com
  MAX_POSTS          posts per run, default 1
  DRY_RUN            "1" = build images into out/ and print, publish nothing
  ONLY_SLUG          optional: handle just this draft (ignores its date)
  CHECK_LOGIN        "1" = only test the WordPress login, publish nothing
"""
import base64
import datetime as dt
import io
import json
import os
import sys
import urllib.error
import urllib.request

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS = os.path.join(ROOT, "drafts")
STATE = os.path.join(ROOT, "state", "published.json")
OUT = os.path.join(ROOT, "out")
FONTS = os.path.join(ROOT, "fonts")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36 ksf-publisher/1.0")

CREAM = (245, 241, 230)
GREEN = (30, 58, 47)
FOOTER = (32, 58, 49)
RUST = (160, 82, 45)
GREY = (85, 85, 85)


# ---------------------------------------------------------------- helpers
def saigon_today():
    return (dt.datetime.utcnow() + dt.timedelta(hours=7)).date().isoformat()


def http(method, url, data=None, headers=None):
    headers = dict(headers or {})
    headers.setdefault("User-Agent", UA)
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def font(name, size, weight=b"Bold"):
    path = os.path.join(FONTS, name)
    try:
        f = ImageFont.truetype(path, size)
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
        return f
    except OSError:
        fallback = "DejaVuSerif-Bold.ttf" if "Gelasio" in name else "DejaVuSans-Bold.ttf"
        return ImageFont.truetype(fallback, size)


def unsplash(photo_id):
    url = f"https://images.unsplash.com/photo-{photo_id}?w=2400&q=90&fm=jpg"
    status, body = http("GET", url)
    if status != 200:
        sys.exit(f"Unsplash download failed for {photo_id}: {status}")
    return Image.open(io.BytesIO(body)).convert("RGB")


def crop_to(img, w, h, crop=None, focus_y=0.45):
    """Crop with fractional box [x, y, cw, ch] if given, else a centred crop
    at the target aspect (biased by focus_y), then resize to w x h."""
    W, H = img.size
    if crop:
        x, y, cw, ch = crop
        img = img.crop((int(x * W), int(y * H), int((x + cw) * W), int((y + ch) * H)))
        W, H = img.size
    target = w / h
    if W / H > target:  # too wide
        nw = int(H * target)
        left = (W - nw) // 2
        img = img.crop((left, 0, left + nw, H))
    else:  # too tall
        nh = int(W / target)
        top = int(max(0, min(H - nh, (H - nh) * focus_y)))
        img = img.crop((0, top, W, top + nh))
    return img.resize((w, h), Image.LANCZOS)


def build_hero(spec):
    img = unsplash(spec["unsplash"])
    w = 1400
    h = int(spec.get("height", 933))
    return crop_to(img, w, h, spec.get("crop"), spec.get("focus_y", 0.45))


def fit_lines(draw, lines, fnt_name, size, max_w):
    while size > 40:
        f = font(fnt_name, size)
        if all(draw.textlength(t, font=f) <= max_w for t in lines):
            return f
        size -= 4
    return font(fnt_name, size)


def build_pin(spec):
    img = unsplash(spec["unsplash"])
    pin = Image.new("RGB", (1000, 1500), CREAM)
    pin.paste(crop_to(img, 1000, 881, spec.get("crop"), spec.get("focus_y", 0.45)), (0, 0))
    d = ImageDraw.Draw(pin)

    kicker = spec.get("kicker", "").upper()
    kf = font("Arimo.ttf", 26)
    # letter-spaced kicker
    widths = [d.textlength(c, font=kf) for c in kicker]
    total = sum(widths) + 3 * max(0, len(kicker) - 1)
    x = 500 - total / 2
    for c, cw in zip(kicker, widths):
        d.text((x, 955), c, font=kf, fill=RUST, anchor="ls")
        x += cw + 3

    lines = spec["title_lines"][:2]
    tf = fit_lines(d, lines, "Gelasio.ttf", 70, 900)
    for i, t in enumerate(lines):
        d.text((500, 1055 + i * 82), t, font=tf, fill=GREEN, anchor="ms")

    sub = spec.get("subtitle", "")
    if sub:
        sf = font("Arimo.ttf", 30, b"Regular")
        while d.textlength(sub, font=sf) > 900 and sf.size > 20:
            sf = font("Arimo.ttf", sf.size - 2, b"Regular")
        y = 1055 + len(lines) * 82 + 1
        d.text((500, y), sub, font=sf, fill=GREY, anchor="ms")

    d.rectangle((0, 1376, 1000, 1500), fill=FOOTER)
    df = font("Arimo.ttf", 30)
    label = "kindredspacefinds.com"
    tw = d.textlength(label, font=df)
    sx = 500 - (56 + 18 + tw) / 2
    d.rounded_rectangle((sx, 1410, sx + 56, 1466), radius=10, fill=CREAM)
    d.text((sx + 28, 1451), "K", font=font("Gelasio.ttf", 38), fill=FOOTER, anchor="ms")
    d.text((sx + 74, 1449), label, font=df, fill=(255, 255, 255), anchor="ls")
    return pin


def jpeg(img, quality=86):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return buf.getvalue()


# ---------------------------------------------------------------- WordPress
class WP:
    def __init__(self, site, user, password):
        self.site = site
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        self.auth = {"Authorization": f"Basic {token}"}

    def json(self, method, path, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        headers = dict(self.auth)
        if data is not None:
            headers["Content-Type"] = "application/json"
        status, body = http(method, f"{self.site}/wp-json/wp/v2/{path}", data, headers)
        try:
            return status, json.loads(body or b"{}")
        except ValueError:
            return status, {"raw": body[:300].decode(errors="replace")}

    def upload(self, data, filename, alt):
        headers = dict(self.auth)
        headers["Content-Type"] = "image/jpeg"
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        status, body = http("POST", f"{self.site}/wp-json/wp/v2/media", data, headers)
        media = json.loads(body or b"{}")
        if status not in (200, 201):
            sys.exit(f"Media upload failed ({status}): {str(media)[:300]}")
        self.json("POST", f"media/{media['id']}", {"alt_text": alt})
        # make sure the stored file decodes completely
        st, got = http("GET", media["source_url"] + "?v=check")
        if st != 200 or len(got) != len(data):
            print(f"Warning: uploaded {filename} came back {len(got)} bytes (sent {len(data)}).")
        Image.open(io.BytesIO(got)).load()
        return media["id"], media["source_url"]


# ---------------------------------------------------------------- main
def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"published": {}}


def save_state(state):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def drafts():
    if not os.path.isdir(DRAFTS):
        return []
    out = []
    for name in sorted(os.listdir(DRAFTS)):
        meta = os.path.join(DRAFTS, name, "post.json")
        if os.path.isfile(meta):
            with open(meta) as f:
                post = json.load(f)
            post["_dir"] = os.path.join(DRAFTS, name)
            out.append(post)
    return sorted(out, key=lambda p: p.get("date", ""))


def main():
    site = os.environ.get("SITE_URL", "https://kindredspacefinds.com").rstrip("/")
    dry = os.environ.get("DRY_RUN") == "1"
    only = os.environ.get("ONLY_SLUG", "").strip()
    max_posts = int(os.environ.get("MAX_POSTS", "1"))
    today = saigon_today()
    state = load_state()
    done = state.setdefault("published", {})

    if os.environ.get("CHECK_LOGIN") == "1":
        pw = os.environ.get("WP_APP_PASSWORD", "").strip()
        if not pw:
            sys.exit("WP_APP_PASSWORD is not set.")
        st, me = WP(site, os.environ.get("WP_USER", "admin"), pw).json("GET", "users/me?context=edit")
        if st != 200:
            sys.exit(f"WordPress login failed ({st}): {str(me)[:300]}")
        print(f"WordPress login OK as {me.get('username')} ({', '.join(me.get('roles', []))}).")
        return

    ready = [p for p in drafts()
             if p["slug"] not in done and (p["slug"] == only if only else p.get("date", "9999") <= today)]
    print(f"Today (Asia/Saigon) {today}: {len(ready)} draft(s) ready; handling up to {max_posts}.")
    if not ready:
        return

    wp = None
    if not dry:
        pw = os.environ.get("WP_APP_PASSWORD", "").strip()
        if not pw:
            sys.exit("WP_APP_PASSWORD is not set.")
        wp = WP(site, os.environ.get("WP_USER", "admin"), pw)
        st, me = wp.json("GET", "users/me?context=edit")
        if st != 200:
            sys.exit(f"WordPress login failed ({st}): {str(me)[:300]}")

    for post in ready[:max_posts]:
        slug = post["slug"]
        with open(os.path.join(post["_dir"], "content.html")) as f:
            html = f.read()

        if wp:
            st, existing = wp.json("GET", f"posts?slug={slug}&status=publish,draft,future,pending&context=edit")
            if st == 200 and existing:
                done[slug] = {"post_id": existing[0]["id"], "link": existing[0]["link"],
                              "note": "already on site, skipped"}
                save_state(state)
                print(f"{slug}: already on the site (post {existing[0]['id']}), skipped.")
                continue

        images = {"HERO": (build_hero(post["hero"]), post["hero"])}
        for extra in post.get("images", []):
            images[extra["key"].upper()] = (build_hero(extra), extra)
        images["PIN"] = (build_pin(post["pin"]), post["pin"])

        if dry:
            os.makedirs(OUT, exist_ok=True)
            for key, (img, spec) in images.items():
                path = os.path.join(OUT, f"{slug}-{key.lower()}.jpg")
                img.save(path, "JPEG", quality=88)
                print("Built", path, img.size)
            missing = [k for k in images if "{{%s_URL}}" % k not in html]
            print(f"DRY RUN {slug}: title={post['title']!r}; placeholders missing: {missing or 'none'}")
            continue

        ids = {}
        for key, (img, spec) in images.items():
            fname = spec.get("filename") or f"{slug}-{key.lower()}.jpg"
            if key == "PIN" and not spec.get("filename"):
                fname = f"pin-{slug}.jpg"
            mid, url = wp.upload(jpeg(img, 88 if key == "PIN" else 86), fname, spec["alt"])
            ids[key] = mid
            html = html.replace("{{%s_URL}}" % key, url)
            print(f"Uploaded {key}: media {mid} {url}")

        body = {
            "title": post["title"],
            "slug": slug,
            "status": post.get("status", "publish"),
            "categories": post["categories"],
            "featured_media": ids["HERO"],
            "content": html,
            "excerpt": post.get("excerpt", ""),
            "meta": {
                "_yoast_wpseo_focuskw": post.get("focus_keyword", ""),
                "_yoast_wpseo_metadesc": post.get("meta_description", ""),
            },
        }
        st, created = wp.json("POST", "posts", body)
        if st not in (200, 201):
            sys.exit(f"Creating {slug} failed ({st}): {str(created)[:400]}")
        done[slug] = {
            "post_id": created["id"],
            "link": created["link"],
            "media": ids,
            "published_at": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        save_state(state)
        print(f"Published {slug}: post {created['id']} {created['link']}")


if __name__ == "__main__":
    main()
