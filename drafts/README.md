# Drafts

One folder per post: `drafts/<slug>/post.json` + `drafts/<slug>/content.html`.
`.github/workflows/publish.yml` runs every day at 08:23 Asia/Saigon and publishes the
oldest draft whose `date` has arrived (one per run) and that is not in `state/published.json`.

## post.json

```json
{
  "date": "2026-11-26",                 // publish on/after this day (Asia/Saigon)
  "title": "…", "slug": "…",
  "categories": [15, 13],               // WordPress category IDs (see README)
  "excerpt": "…", "focus_keyword": "…", "meta_description": "…",
  "hero":  {"unsplash": "<photo id after 'photo-'>", "crop": [x, y, w, h], "height": 933,
            "alt": "…", "filename": "….jpg"},
  "images": [ {"key": "IMG2", "unsplash": "…", "crop": [...], "alt": "…"} ],   // optional
  "pin":   {"unsplash": "…", "crop": [x, y, w, h], "kicker": "Pets + Cleaning",
            "title_lines": ["line 1", "line 2"], "subtitle": "…", "alt": "…", "description": "…"}
}
```

`crop` is optional and uses fractions of the original photo (x, y, width, height). The script then
centre-crops to the target shape: hero 1400 x `height` (default 933), pin photo 1000 x 881.
Only use photos marked "Free to use under the Unsplash License" (not Unsplash+), and credit the
photographer in the hero figcaption.

## content.html

Same HTML structure as live posts (see content-plan.md). Use `{{HERO_URL}}`, `{{PIN_URL}}` and
`{{IMG2_URL}}` (etc.) where the uploaded image URLs go.

Test a draft without publishing: Actions → "Publish ready drafts to WordPress" → Run workflow,
dry_run = 1, only_slug = the slug. The built images are attached to the run as "preview-images".
