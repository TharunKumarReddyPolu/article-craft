# Hashnode Reference

Rules and guidance for preparing articles for [Hashnode](https://hashnode.com),
verified against Hashnode's official documentation on **2026-09-07**.
Hashnode's help center lives as a Docusaurus site in the official
[`Hashnode/support`](https://github.com/Hashnode/support) GitHub repository;
its articles are cited by repo path. Sources and authority classifications
live in `sources.yaml`.

Rule classification:

- **POLICY** — an official requirement.
- **RECOMMENDATION** — official advice from Hashnode's docs.
- **HEURISTIC** — Article Craft's own editorial judgment. Not a Hashnode rule.

## Publishing mechanics (OFFICIAL_REQUIREMENT — POLICY)

From `write-an-article` (Hashnode Support):

- Articles are written in Hashnode's Markdown editor; the title is a separate
  field (not an in-content heading).
- **Tags** are selected in the editor's "Select tags" section (from
  Hashnode's tag list; comma-separated slugs in the GitHub-as-source flow).
- **Cover photo**: recommended dimensions **1200 × 630 px**.
- **Subtitle**: optional, added via the "Add Subtitle" button.
- **Custom OG image**: recommended 1200 × 630 px, used when the article is
  shared on social platforms.
- **Slug**: editable before publishing.
- **Canonical URL**: set via the "Are you republishing? → Add Original
  Article" setting when republishing content from elsewhere.
- **Hide from Hashnode Community**: an option to display the article on your
  blog only, excluding it from Hashnode feeds.
- Blog-level SEO controls (meta tags, keywords, sitemap, AMP) are separate
  from per-article settings (`seo`).

Adapter checks: a republished article (detectable via export provenance the
author supplies) without a canonical URL → WARNING citing the "Are you
republishing?" setting; missing cover image → RECOMMENDATION with the
1200×630 guidance; missing alt text → WARNING (accessibility, HEURISTIC
grounded in general web accessibility — Hashnode's docs do not have a
dedicated alt-text page).

## Markdown and embeds (RECOMMENDATION)

From `markdown-guidelines`:

- ATX-style headings H1–H6. Unlike DEV, Hashnode's title is a separate
  field, so H1 headings in the body are syntactically valid; the adapter
  still flags duplicate H1s as HEURISTIC (an article should have one title).
- **Embeds use the `%[URL]` syntax** (via Embed.ly): tweets, YouTube videos,
  GitHub repos, CodePen, Glitch, SoundCloud, or "any article on the web."
  No platform-specific embed code is needed.
- Code blocks: triple-backtick fences with a language tag for manual syntax
  highlighting; generic highlighting otherwise.
- Quotes via `>`; bold/italics inside most block-level elements.

The adapter flags bare URLs that Hashnode would render as rich embeds
(`%[URL]` candidates) as HEURISTIC suggestions, and unknown liquid-style
`{% %}` tags (DEV syntax that Hashnode renders as literal text) as a
portability warning during export.

## Community and conduct (POLICY)

From `community-code-of-conduct`: respectful behavior is required;
derailing, unconstructive criticism, snarking, and microaggressions are
called out as destructive behaviors. Content moderation and copyright
reporting paths exist (`report-posts-and-users`,
`report-copyright-infringement`).

## AI content

Hashnode's support docs (as verified 2026-09-07) contain **no published
AI-content policy equivalent to DEV's or Medium's**. The adapter therefore
applies Article Craft's platform-agnostic rules (author contribution,
originality, fact-checking) and reports "no official AI policy found —
verify before relying on any disclosure practice" rather than inventing one.
This is an explicit NOT CHECKED, per the adapter contract.
