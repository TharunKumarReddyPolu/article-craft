# Medium Canonical Links (reference)

> Source: [Set a canonical link](https://help.medium.com/hc/en-us/articles/360033930293-Set-a-canonical-link)
> (official; verified 2026-09-06). See `sources.yaml`.

## Official guidance (OFFICIAL_REQUIREMENT)

- Only the story's **author** can set a canonical link.
- When posting the same content to multiple platforms (e.g., your website and
  Medium), designate a single authoritative source so search engines know
  which is the ultimate source of the content.
- Sites that publish abundant duplicate content **without** canonical
  indication may be penalized in search rankings.
- Medium's official import tool sets the canonical link automatically; you
  can also set it manually per story (Story settings → Advanced Settings →
  "This story was originally published elsewhere").

## What Article Craft does with this (HEURISTIC)

- `article-craft check --platform medium` reads optional frontmatter:
  `canonical_url: <url>` and `originally_published: true|false`.
- If the frontmatter indicates the article was first published elsewhere
  (or a `canonical_url` is present), the check confirms it and reminds the
  author to set the canonical link in Medium's story settings at publish
  time — Article Craft cannot and does not set it.
- If duplicate-content risk is detected (e.g., the same article appears to be
  prepared for multiple platforms) the check recommends designating one
  canonical source.
