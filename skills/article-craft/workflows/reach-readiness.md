# Workflow: Reach readiness

Use when the user asks "how do I give this the best chance on
Medium/DEV/Hashnode/Substack/LinkedIn?", "check reach readiness", "is my
article aligned with Medium's Boost criteria?", or wants the article optimized
for a platform's own published discoverability mechanics.

## The honest framing (non-negotiable)

Every platform officially publishes what it looks for — Medium's Boost
criteria, DEV's tag/cover guidance, Substack's title-testing mechanics,
LinkedIn's expertise guidance, Hashnode's tag/SEO fields. This workflow checks
**alignment with those stated criteria**. It never predicts reach:

- Never say a change "will go viral", "will get Boosted", or "will rank".
- Do say: "these are the platforms' own published criteria; meeting them is
  the part you control; the platform decides distribution".
- If the user asks to game an algorithm, bait engagement, or manufacture
  popularity signals, refuse and reframe toward the official criteria.

## How to run it

If the CLI is installed:

```bash
article-craft reach article.md --platform medium   # also devto, hashnode, substack, linkedin
```

This runs the deterministic reach checks; each result cites the official
source id from that platform's `references/platforms/<platform>/sources.yaml`.
Layer judgment on top; if the CLI is absent, read the platform's
`reach.md` reference and the article directly and reason through the same
checks.

## What each platform officially publishes (and what the engine checks)

- **Medium** — the Boost/Distribution guidelines name the hallmarks of
  boosted stories: a clear, compelling reason *why this writer* is writing
  this; reader value ("time well spent"); title/subtitle/cover that represent
  the story; non-derivative content. Discoverability mechanics: topics (up to
  five) match stories to readers who follow them. Sources:
  `medium-distribution-guidelines`, `medium-using-topics`.
- **DEV.to** — documented mechanics: up to four tags (primary discovery
  surface: tag pages and followed-tag feeds), cover image as the feed card
  (1000x420), series for serialized reading. Sources: `dev-editor-guide`,
  `dev-help-writing`.
- **Hashnode** — documented mechanics: tags from Hashnode's tag list,
  blog-level SEO fields (display title, search description, social image),
  descriptive slugs. Sources: `hashnode-tags`, `hashnode-seo`,
  `hashnode-write-article`.
- **Substack** — documented mechanics: the title doubles as the email subject
  line (the reach surface), official A/B title testing for publications with
  200+ subscribers, keyword tags, alt text (email clients often block
  images). Sources: `substack-title-testing`, `substack-tags`,
  `substack-alt-text`.
- **LinkedIn** — official guidance: write about areas where you have
  experience/expertise, stay focused on one topic, deliver substance (best
  received: more than three paragraphs), use media to showcase examples.
  Sources: `linkedin-article-tips`, `linkedin-pcp`.

## The cross-cutting signals (advisory heuristics)

The reach engine computes four deterministic signals used by several
platforms' criteria. Each is a *proxy*, not a verdict:

1. **First-hand experience** — first-person markers, concrete numbers and
   versions, code. Platforms' own criteria favor demonstrable first-hand
   contribution; generic prose reads as derivative.
2. **Reader value** — concrete deliverables (code, steps, examples, data),
   proportionate length, low hedging. Official phrasing: the reader's life is
   enriched; time well spent.
3. **Headline parity** — key title terms appear in the subtitle/body. Curated
   platforms disqualify stories whose headline misrepresents them.
4. **Non-derivative** — low generic-AI phrasing density plus at least one
   first-hand artifact (code, data, image, table). Platforms' guidelines
   consistently exclude recycled content.

## Improving reach-readiness the right way

- Tighten the title/subtitle until they accurately promise what the body
  delivers (parity), without sensationalism or genericness.
- Surface the author's own contribution: what did *they* measure, build,
  learn, or decide? If that material isn't in the draft, interview the author
  rather than inventing it.
- Make sure deliverables are concrete: code that runs, numbers the author
  actually observed, comparisons they actually made.
- Align tags/topics with what the article is actually about (that is what
  the platforms match readers on).
- Fix images: covers and alt text are documented reach surfaces on every
  platform.

Never: keyword-stuff, add engagement bait, fabricate experience or data, or
mass-produce derivative posts. Those fail the policy floors checked by
`platform-check.md` — and on every platform, policy action is the fastest way
to lose reach.

## Relation to other workflows

- Policy floors (plagiarism, AI disclosure, spam) live in
  [platform-check.md](platform-check.md); reach readiness assumes those pass.
- The Editorial Quality Score is editorial craft, not reach — never present
  it as a reach or boost score.
