# Reach: DEV.to's Official Discoverability Mechanics

What DEV officially documents about how posts get found — summarized from
DEV's own help material so the adapter checks alignment with documented
mechanics, not folklore.

Sources: `dev-editor-guide` (verified 2026-09-07), `dev-help-writing`,
`dev-ai-guidelines`. DEV publishes no "boost" program; reach on DEV follows
from the documented feed mechanics: tag pages, followed tags, and the
cover image as the post's card in feeds and social previews.

## Official mechanics

- **Tags (max four, comma-separated)** — the primary discoverability
  mechanism. Posts surface on tag pages and in feeds of members following
  those tags. dev-editor-guide: "tags: max of four tags, needs to be
  comma-separated". Irrelevant tags trade real discoverability for fake
  breadth — DEV serves posts to tag followers, so mismatched tags reach the
  wrong readers.
- **Cover image (1000×420)** — "The best size is 1000 x 420"
  (dev-editor-guide). The cover is the card shown in feeds and social-card
  previews; missing or wrong-aspect covers reduce click-through surface.
- **Alt text** — DEV's editor guide has an explicit accessibility section:
  "Providing alternative descriptions for images... helps make sure that
  everyone can understand your post". Accessible posts are also
  machine-interpretable posts.
- **Canonical URL** — `canonical_url` in front matter keeps search
  authority with the original when cross-posting, protecting long-term
  search-engine discoverability instead of splitting it.
- **Series** — `series:` groups related posts; serialized readers return.
- **Liquid embeds** — rich embeds ({% embed %}, {% link %}, {% user %} etc.)
  make posts interactive and connect them to the wider DEV graph.
- **AI content** — dev-ai-guidelines governs disclosure; undisclosed
  machine-generated content risks moderation action, which is the single
  fastest way to lose reach on any platform.

## What the reach engine checks (and why)

Each of the above becomes an advisory readiness signal: tag count/coverage,
cover-image presence and stated size, alt-text quality, canonical presence
when cross-posting, and heading structure (title is h1; content starts at
h2). None of it predicts feed placement.
