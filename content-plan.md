# Kindred Space Finds — content plan

The scheduled task reads this file on every run, publishes the first row whose date has arrived
and whose status is `planned`, then updates the row (status, URL, notes) and pushes this file.
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
  Build it with a canvas in the wp-admin tab and upload through /wp-json/wp/v2/media as image/jpeg; check it decodes.
- Set featured_media to the hero, Yoast focus keyword + meta description, excerpt, categories.
- WordPress admin is logged in on the laptop Chrome profile shown as "Browser 3" (Google account a16cuong2025).

| # | Date | Category (WP id) | Title | Status | URL | Notes |
|---|------|------------------|-------|--------|-----|-------|
| 1 | 2026-11-24 | Kids & Pets (15) + Kitchen & Pantry (7) | Pet Food Storage: 7 Ways to Keep Kibble Fresh, Bug-Free and Off the Kitchen Floor | published | https://kindredspacefinds.com/pet-food-storage/ | post 1346 |
| 2 | 2026-11-26 | Kids & Pets (15) + Laundry & Cleaning (13) | Pet Hair Everywhere? A 15-Minute Daily Routine and the Tools That Actually Pick It Up | drafted | | drafts/pet-hair-removal |
| 3 | 2026-11-28 | Kitchen & Pantry (7) | Holiday Baking Pantry: What to Stock Before December, How Long Each Keeps and Where It Goes | planned | | link brownie/cookie-mix-in-a-jar posts |
| 4 | 2026-11-30 | Kids & Pets (15) | Litter Box Hideaway Ideas: 9 Spots That Cut the Smell (and the Ones Cats Refuse to Use) | planned | | |
| 5 | 2026-12-02 | Kitchen & Pantry (7) | Spice Cabinet Organization: 6 Setups That Fit Your Cabinet, Plus How Long Spices Really Last | planned | | |
| 6 | 2026-12-04 | Kids & Pets (15) | Dog Entryway Station: One Wall for Leashes, Coats, Treats and Muddy Paws | planned | | link small-entryway-storage |
| 7 | 2026-12-06 | Meal Prep & Recipes (18) | How to Store Christmas Cookies: Which Kinds Stay Fresh, Which Freeze and How Long Each Lasts | planned | | not the same as freeze-cookie-dough |
| 8 | 2026-12-08 | Kids & Pets (15) | Pet Toy Storage: 8 Bins and Baskets Sized for Chews, Plush Toys and Balls | planned | | link toy-rotation, avoid overlap |
| 9 | 2027-01-14 | Living Room & Bedroom (14) | Valentine's Decor on a Budget: 12 Dollar-Store Ideas That Don't Look Cheap | planned | | |

Dropped on 2026-11-24 because the site already covers them: Christmas decoration storage
(best-christmas-ornament-storage, how-to-store-christmas-lights, how-to-store-wreaths-and-garland),
gift wrap station (best-gift-wrap-organizers), holiday guest room (make-room-for-holiday-guests),
after-Christmas declutter (declutter-after-christmas).

## Care log

- 2026-11-24: Published /pet-food-storage/ (post 1346, media 1344 hero, 1345 pin). Checked live page: hero, pin, table, FAQ, related cards render. Rewrote plan to drop 4 duplicate seasonal titles and add kitchen/food titles. Pinterest RSS auto-publish now has 3 feeds: meal-prep-recipes → "Easy Meal Prep & Freezer Recipes", kitchen-pantry → "Kitchen & Pantry Organization", kids-pets → new board "Pet & Kid-Friendly Home Ideas" (created and saved with user OK).
- 2026-11-24 (later run): Not published — Claude in Chrome / laptop was not reachable from this cloud run (no desktop bridge). Next planned row stays `planned` for the next run.
