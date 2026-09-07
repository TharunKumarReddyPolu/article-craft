# Medium Publishing (reference)

> Sources: [Writing and publishing your first story](https://help.medium.com/hc/en-us/articles/225168768-Writing-and-publishing-your-first-story),
> [Medium Rules](https://help.medium.com/hc/en-us/articles/213477928-Medium-Rules),
> [Publications Best Practices](https://help.medium.com/hc/en-us/articles/41530252213655-Medium-Publications-Best-Practices-and-Guidelines)
> (official; verified 2026-09-06). See `sources.yaml`.

## Publishing mechanics (OFFICIAL_REQUIREMENT)

- Drafts save automatically; publish from the web editor or mobile app.
- At publish time you can: add topics (up to 5 tags), customize title/subtitle
  and preview image, schedule, submit to a publication, and toggle the
  paywall if you're in the Partner Program.
- Published stories appear on your profile, in followers' feeds/digests, and
  in publications per their settings.

## Rules that affect publishing (OFFICIAL_REQUIREMENT)

- **Duplicate content**: no posting duplicate copies of the same content to
  Medium across accounts or as unlisted stories. Cross-posting your own blog
  content is allowed if you own the rights (set a canonical link — see
  `canonical-links.md`).
- **Spam/misuse** (removed without notification): content posted primarily to
  drive traffic or raise search rankings of an external site; scraping and
  reposting others' content; content clipped to force readers off-site;
  re-using content templates with slight modifications across multiple posts
  or accounts; bulk/automated interactions.
- **Ads and promotion**: third-party advertising/sponsorship is not allowed.
  First-party promotion of your own business, website, mailing list, or
  fundraiser is allowed. Affiliate links are allowed with FTC disclosure.
- **Paid interactions**: buying/selling views, reads, follows, claps; services
  that inflate engagement; automated posting/interaction — all prohibited.
- **Stories about Medium** (Partner Program, earnings, Boost) are set to
  Network Distribution; tag them `medium-meta`.

## Publications (OFFICIAL_RECOMMENDATION)

- Prefer each publication's open-submissions flow; respect closed
  publications and follow their stated process.
- Match the publication's topic and tone before submitting.

## What Article Craft does with this (HEURISTIC)

`article-craft check --platform medium` surfaces a publishing checklist
(topics chosen, paywall/Partner Program implications of AI assistance, cross-
post canonical link, affiliate disclosure, no engagement automation) — it
never automates publishing itself.
