# DEV.to Reference

Rules and guidance for preparing articles for [DEV Community](https://dev.to),
verified against DEV's official documentation on **2026-09-07**. Sources and
their authority classification live in `sources.yaml`.

Rule classification used in this file (and in the adapter):

- **POLICY** — an official requirement (violating it can get a post removed or an account suspended).
- **RECOMMENDATION** — official advice from DEV's docs.
- **HEURISTIC** — Article Craft's own editorial judgment. Not a DEV rule.

## Front matter contract (OFFICIAL_REQUIREMENT — POLICY)

DEV's editor uses Jekyll-style front matter. Documented fields
(Editor Guide, `editor-guide`):

| Field | Meaning |
|---|---|
| `title` | The article title |
| `published` | Boolean; `false` until you publish |
| `tags` | **Max 4, comma-separated** |
| `canonical_url` | URL of the original version when cross-posting |
| `cover_image` | Cover image URL; **best size 1000 × 420** |
| `series` | Series name for linked articles |

Adapter checks: tag count > 4 is a POLICY error; `published: false` is
expected in export prep (never auto-publish); `cover_image` size guidance is
RECOMMENDATION; missing `canonical_url` on an article that is a republication
is a POLICY warning (see below).

## Canonical URLs (POLICY for cross-posts)

DEV Help states that setting a canonical URL tells search engines the
original source, "prevents any penalties for reposting," and boosts the
original article's ranking (`dev-help-writing`). Cross-posting is explicitly
encouraged: "We encourage folks to share articles from their personal and
company blogs!" An article republished from elsewhere without
`canonical_url` is flagged ERROR by the adapter.

## Markdown and formatting (RECOMMENDATION)

- Headings: DEV supports H1–H6, **but the post title is automatically an H1**.
  The Editor Guide's accessibility section says to avoid level-1 headings in
  content and start sections at H2 (OFFICIAL_RECOMMENDATION — adapter flags
  `# Heading` lines as WARNING).
- Image alt text: official accessibility guidance requires meaningful
  descriptions ("A pie chart showing 40% responded Yes…"), not filenames.
- Captions: HTML `<figcaption>` is supported.
- GIFs: limit of 200 megapixels per frame/page (POLICY technical limit).
- HTML may be written inline "most of the time."

## Liquid tags and embeds (RECOMMENDATION)

Use `{% embed https://... %}` for universal URL embeds (GitHub, YouTube,
CodePen, Twitter/X, Medium, Reddit, Stack Exchange, and more). DEV-specific
tags: `{% link %}`, `{% user %}`, `{% tag %}`, `{% comment %}`,
`{% podcast %}`, `{% organization %}`, `{% forem %}`. Non-URL tags:
`{% card %}`, `{% cta %}`, `{% details %}` / `{% spoiler %}` /
`{% collapsible %}`, `{% katex %}`.

The adapter flags URLs pasted bare where an embed would render richer, and
unknown `{% tag %}`-shaped syntax (a typo'd liquid tag renders as literal
text) as HEURISTIC warnings. It never rewrites embeds automatically.

## AI-assisted content (POLICY)

From DEV's Guidelines for AI-assisted Articles (`dev-ai-guidelines`,
updated 2024-04-08). AI-assisted and AI-generated articles are allowed if they:

1. Are created in good faith.
2. **Disclose** AI assistance — the tag `#ABotWroteThis` or any disclosure in
   the article copy (including the end) is acceptable.
3. Ideally add something to the conversation about AI use.
4. **Are checked for factual accuracy before publishing.**

They must NOT: promote a business/course; deceive readers; exist to build
clout; or publish educational content the human author doesn't understand.

Adapter checks: strong AI-pattern presence with zero first-person experience
→ WARNING suggesting disclosure review; unsupported claims → WARNING citing
the fact-check requirement. Article Craft never helps evade this disclosure.

## Plagiarism (POLICY)

From DEV's plagiarism guidelines (`dev-plagiarism`, updated 2023-07-19): DEV
names four types — direct, self, mosaic, accidental. Cite anything you did
not create; quote + cite for verbatim text; paraphrase still deserves a
citation. "In doubt, always provide a source + citation!" The originality
guard's findings map directly: mosaic risk → WARNING with fix suggestions.

## Other policy signals

- Profanity is allowed generally, **but posts with profanity in the title
  are not promoted** (dev-help-writing). Adapter: HEURISTIC warning on
  profane titles, citing that page.
- Authors own their content and can edit/remove it.
- Posts are subject to moderation under DEV's Code of Conduct.
- Backlink/SEO abuse (articles whose main purpose is building backlinks to
  another site) can lead to suspension — exceptions: personal blogs, and
  company blogs shared under that company's DEV organization.
- AI-generated comments are prohibited (exceptions: translation, grammar,
  assistive tools). Article Craft never generates comments — out of scope.
