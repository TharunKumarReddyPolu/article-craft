# LinkedIn Reference

Rules and guidance for preparing content for [LinkedIn](https://linkedin.com),
verified against LinkedIn's official Help Center on **2026-09-07**. Sources
and authority classifications live in `sources.yaml`.

Rule classification:

- **POLICY** — an official requirement (Professional Community Policies /
  User Agreement).
- **RECOMMENDATION** — official advice from LinkedIn's Help Center.
- **HEURISTIC** — Article Craft's own editorial judgment. Not a LinkedIn rule.

## The adaptation model (design decision)

LinkedIn has two content shapes (`linkedin-posting`, `linkedin-articles`):

1. **Posts** — short updates in the feed share box. No markdown; plain
   text with limited rich media.
2. **Articles** — long-form pieces via the "Write article" publishing tool
   (desktop only), with a title field, cover image/video, rich-text
   toolbar (bold/italic, lists, blockquotes, dividers, links, code
   snippets, embeds), and SEO settings (article URL, SEO title, SEO
   description).

Article Craft's canonical article is a markdown long-form document, so the
LinkedIn adapter does **not** review the markdown article directly. It
reviews a **LinkedIn adaptation artifact** (a plain-text post or a
restructured article draft produced by `article-craft adapt` /
`article-craft export --platform linkedin`). Any check output is labeled
"adaptation review" — we never claim the markdown original was validated
for LinkedIn. Publishing remains a manual human act.

## Articles (RECOMMENDATION)

From `linkedin-articles` and `linkedin-article-tips`:

- Articles are "longer, in-depth pieces" — updates vs. articles is an
  explicit official distinction.
- "Write about specific areas in which you have experience and/or
  expertise" (OFFICIAL_RECOMMENDATION — maps 1:1 to the author-contribution
  dimension).
- "Keep your writing focused. Avoid covering too many topics in the same
  article."
- "Don't shy away from expressing your opinion," kept professional — no
  obscene, shocking, hateful, intimidating content (POLICY boundary).
- "There are no limits on word count, but the articles that are best
  received are more than three paragraphs."
- Media (pictures, videos, presentations, documents) is officially
  recommended to showcase concrete examples.
- Article SEO settings (SEO title/description, article URL) are first-class
  editor features.
- Commenting can be disabled; drafts can be shared for review.

## AI content (POLICY + OFFICIAL mechanics)

From `linkedin-ai-best-practices` — LinkedIn's "Best practices for content
created with the help of AI":

- Content "should still reflect the member's own voice, perspective, and
  experience."
- LinkedIn defines **"AI slop"**: "low-effort, likely AI-generated content
  that may sound polished on the surface but lacks a clear point of view,
  unique perspective, or substance… generic, repetitive, recycled, or
  designed primarily to game attention."
- LinkedIn's stated distinction: "AI-assisted content is welcome when it
  reflects a real person's perspective, experience, or expertise. Content
  that feels generic, repetitive, or lacks a clear point of view is less
  likely to be widely distributed."
- LinkedIn "urge[s]" review/edit/approval of AI-assisted content and
  recommends disclosure "if it isn't obvious from the context" when you
  "relied heavily on AI."
- Members can report posts via the **"Seems like AI slop"** feed option;
  enough community feedback surfaces a tip in Post analytics. LinkedIn
  states this is not a takedown or policy decision.

Adapter checks: generic-AI-pattern density → WARNING citing the "AI slop"
definition; missing first-person experience in the adaptation → WARNING;
attention-gaming phrasing (engagement-bait) → HEURISTIC error. The adapter
quotes the official definition and never helps evade community feedback.

## Professional Community Policies (POLICY)

From `linkedin-pcp`: the baseline content contract (be safe, be
trustworthy, be professional, respect others' IP and privacy). The adapter
treats plagiarism and IP-infringement risk as POLICY-grade checks here,
same as on every other platform.

## What the LinkedIn adapter deliberately does NOT check

No reach prediction, no algorithm modeling, no posting-time or engagement
optimization. LinkedIn's distribution statement above is the closest
official language and it is quoted, not extrapolated.
