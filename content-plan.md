# Kindred Space Finds — content plan

Publishing runs on GitHub, no laptop needed: the scheduled Claude task writes each row as a draft in
drafts/<slug>/ a few days ahead (status `drafted`), and the "Publish ready drafts to WordPress"
workflow (.github/workflows/publish.yml, daily 08:23 Saigon) builds the images and publishes one due
draft per day using the WP_APP_PASSWORD secret. Pinterest picks new posts up from the category RSS feeds.
Dates are Asia/Saigon. Before writing, always search the site for a near-duplicate post; tighten
the title or angle (or swap the row) if one exists.

## How posts are built (match post 1346 /pet-food-storage/)

- Raw HTML inside `<!-- wp:html -->`: `div.ksf.ksf-article` with `p.intro`, `p.ksf-meta` (By Avery Linden · Updated <Month Year> · <Category>),
  hero `figure` (1400px wide JPG, Unsplash credit in figcaption), `div.ksf-summary`, numbered `h2` steps, `div.ksf-table`,
  `div.ksf-callout` worked example, affiliate disclosure `p.ksf-source`, Amazon-search callout (tag `shoppingd0151-20`,
  rel="sponsored nofollow noopener"), `div.ksf-checklist`, `details.ksf-faq` x3-4, Sources `p.ksf-source`.
  After the article div: `figure.ksf-pinsave` (pin image + data-pin-description), then `section.ksf.ksf-more` with 3 related posts.
  Then `<!-- /wp:html -->` and `<!-- wp:block {"ref":103} /-->`.
- Pin image 1000x1500 JPG: photo top 0-881, cream #F5F1E6 panel, rust kicker caps 26px, title Georgia bold 70px #1E3A2F
  (two lines), grey 30px subtitle, footer bar #203A31 from y=1376 with "K" logo tile + kindredspacefinds.com.
  scripts/publish.py builds it with Pillow (fonts/ Gelasio + Arimo) and uploads it as JPG.
- Set featured_media to the hero, Yoast focus keyword + meta description, excerpt, categories.
- For hands-on fixes from a live chat: WordPress admin is logged in on the laptop Chrome profile of Google account a16cuong2025.

| # | Date | Category (WP id) | Title | Status | URL | Notes |
|---|------|------------------|-------|--------|-----|-------|
| 1 | 2026-11-24 | Kids & Pets (15) + Kitchen & Pantry (7) | Pet Food Storage: 7 Ways to Keep Kibble Fresh, Bug-Free and Off the Kitchen Floor | published | https://kindredspacefinds.com/pet-food-storage/ | post 1346 |
| 2 | 2026-11-26 | Kids & Pets (15) + Laundry & Cleaning (13) | Pet Hair Everywhere? A 15-Minute Daily Routine and the Tools That Actually Pick It Up | published | https://kindredspacefinds.com/pet-hair-removal/ | post 1366 (drafts/pet-hair-removal) |
| 3 | 2026-11-28 | Meal Prep & Recipes (18) | How to Store Christmas Cookies: Which Kinds Stay Fresh, Which Freeze and How Long Each Lasts | drafted | | drafts/how-to-store-christmas-cookies; replaces Holiday Baking Pantry (duplicate of organize-baking-supplies) |
| 4 | 2026-11-30 | Kids & Pets (15) | Litter Box Hideaway Ideas: 9 Spots That Cut the Smell (and the Ones Cats Refuse to Use) | drafted | | drafts/litter-box-hideaway-ideas |
| 5 | 2026-12-02 | Kitchen & Pantry (7) | Spice Cabinet Organization: 6 Setups That Fit Your Cabinet, Plus How Long Spices Really Last | planned | | |
| 6 | 2026-12-04 | Kids & Pets (15) | Dog Entryway Station: One Wall for Leashes, Coats, Treats and Muddy Paws | planned | | link small-entryway-storage |
| 7 | 2026-12-06 | Kitchen & Pantry (7) | Under-Sink Kitchen Cabinet Organization: Plan Around the Pipes and the Disposal, Then Pick Bins | planned | | check for duplicate with bathroom under-sink post; kitchen angle only |
| 8 | 2026-12-08 | Kids & Pets (15) | Pet Toy Storage: 8 Bins and Baskets Sized for Chews, Plush Toys and Balls | planned | | link toy-rotation, avoid overlap |
| 9 | 2027-01-14 | Living Room & Bedroom (14) | Valentine's Decor on a Budget: 12 Dollar-Store Ideas That Don't Look Cheap | planned | | |

Dropped on 2026-11-24 because the site already covers them: Christmas decoration storage
(best-christmas-ornament-storage, how-to-store-christmas-lights, how-to-store-wreaths-and-garland),
gift wrap station (best-gift-wrap-organizers), holiday guest room (make-room-for-holiday-guests),
after-Christmas declutter (declutter-after-christmas).

## Care log

- 2026-11-24: Published /pet-food-storage/ (post 1346, media 1344 hero, 1345 pin). Checked live page: hero, pin, table, FAQ, related cards render. Rewrote plan to drop 4 duplicate seasonal titles and add kitchen/food titles. Pinterest RSS auto-publish now has 3 feeds: meal-prep-recipes → "Easy Meal Prep & Freezer Recipes", kitchen-pantry → "Kitchen & Pantry Organization", kids-pets → new board "Pet & Kid-Friendly Home Ideas" (created and saved with user OK).
- 2026-11-24 (later run): Not published — Claude in Chrome / laptop was not reachable from this cloud run (no desktop bridge). Next planned row stays `planned` for the next run.
- 2026-11-25: No new draft written. Row 3 (Holiday Baking Pantry, due 2026-11-28) needs research, a site duplicate check and an Unsplash photo, but this cloud run had no web page access (kindredspacefinds.com, unsplash.com and source sites blocked by the egress proxy; WebFetch permission prompts timed out). Not written from memory to avoid unsourced claims; row stays `planned` for the next run (must be drafted by 2026-11-27). Publish workflow: 2026-11-25 scheduled run OK (nothing due); dry run of pet-hair-removal OK, images build, no missing placeholders, goes live 2026-11-26 08:23. 7 rows still `planned`, no new titles needed.
- 2026-11-27: No drafts written again. Rows 3 (Holiday Baking Pantry, due 11-28) and 4 (Litter Box Hideaway, due 11-30) are in the 4-day window, but WebFetch permission prompts for kindredspacefinds.com timed out in this unattended run (shell egress to the site and unsplash.com also blocked), so no duplicate check, source reading or Unsplash photo was possible; WebSearch returns titles only. Not written from memory. Row 3 will miss 11-28. Publish workflow: 11-26 scheduled run published pet-hair-removal (post 1366, media 1364 hero, 1365 pin) per run log; row 2 marked published. Live page not re-checked (no page access). 11-27 run OK, nothing due. 7 rows still `planned`, no new titles needed.
- 2026-11-28 (live chat): Found that the other Claude account schedules 1 clean pin per post with Pinterest's own scheduler (method pin_scheduling, 15 queued). The kitchen-pantry and kids-pets RSS feeds added on 11-24 were creating 2-26 duplicate pins per post (feed_crawler): both feeds removed, 94 duplicate pins deleted, one 1000x1500 pin kept per post that had no scheduled pin. Meal-prep RSS feed left as it was (pre-existing). Unattended runs cannot use WebFetch, so drafts are written in live chats: wrote how-to-store-christmas-cookies (11-28) and litter-box-hideaway-ideas (11-30).
