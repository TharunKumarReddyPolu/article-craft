# Platform Adapters

Article Craft v2 implements **five** platform adapters behind one
`PlatformAdapter` protocol:

| Platform | `--platform` id | Grounded in |
|---|---|---|
| Medium | `medium` | Medium Help Center (9 reference files) |
| DEV.to | `devto` | DEV's Editor Guide + official AI & plagiarism guidelines |
| Hashnode | `hashnode` | Hashnode's official support documentation |
| Substack | `substack` | Substack Content Guidelines + Help Center |
| LinkedIn | `linkedin` | LinkedIn Help Center + Professional Community Policies |

Run any of them:

```bash
article-craft check my-article.md --platform devto
article-craft check my-article.md --platform hashnode
article-craft check my-article.md --platform substack
article-craft check my-article.md --platform linkedin
```

## Where the rules come from

Every adapter rule traces to a versioned reference file:

```
skills/article-craft/references/platforms/
├── medium/     overview + 8 topic files + sources.yaml
├── devto/      overview.md + sources.yaml
├── hashnode/   overview.md + sources.yaml
├── substack/   overview.md + sources.yaml
└── linkedin/   overview.md + sources.yaml
```

Each `sources.yaml` records, per source: the URL, the exact title, the
authority classification (OFFICIAL for everything cited by adapters), the
date the page was last updated when shown, and the date we verified it.

The adapters encode checks against these summaries — never against folklore
or blog hearsay. If a platform publishes no policy on a topic (Hashnode's AI
position, for example), the adapter reports **NOT CHECKED** with that
explanation instead of inventing a rule.

## Rule classification

Every check carries a rule class:

- **POLICY** — the platform's official requirement. Violations reported as
  WARNING or ERROR.
- **RECOMMENDATION** — advice sourced from official documentation.
- **HEURISTIC** — Article Craft's own editorial judgment, clearly labeled.

The shared adapter base refuses to emit a policy check whose `source_id`
doesn't exist in that platform's `sources.yaml` — the honesty guard that
keeps code from drifting away from documented sources.

## Platform notes

**DEV.to** — checks the front matter contract (`title`, `published`, at most
4 tags, `cover_image`, `canonical_url`), liquid-tag embed guidance, and the
AI-assisted content labeling requirement from DEV's official guidelines.

**Hashnode** — checks publishing mechanics (title, cover, canonical URL,
tags), embed sanity, and community/conduct expectations. Notes where the
platform publishes no explicit policy.

**Substack** — treats the post title as the email subject line (that's what
it is), checks Content Guidelines rules (editorial content, not email
marketing; original writing), and flags AI-pattern signals because Substack
now runs reader-facing AI-text detection. It cannot verify email rendering —
stated, not faked.

**LinkedIn** — reviews **adaptations** (post text), not raw markdown
articles: the documented 3,000-character limit, first-line hook quality,
AI-slop policy, and Professional Community Policies. If you want a LinkedIn
article rather than a post, say so — the checklist differs.

**Medium** — the V1 production adapter: title/subtitle, content quality, AI
disclosure and paywall rules, formatting, topics, canonical links, affiliate
disclosure, and distribution-signal warnings. See [medium.md](medium.md).

## Adding a platform

Ghost, personal blogs, and newsletter tools are intentionally *not*
implemented — the abstraction is ready, but each adapter needs real research
against that platform's official documentation first. The process is in
[contributing.md](contributing.md): build references and `sources.yaml`
first, adapter second, tests last.
