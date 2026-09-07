# Roadmap

V1 is deliberately scoped: a platform-agnostic editorial core, a
production-quality Medium adapter, and the Agent Skill. Everything below is
a possibility, not a promise — and nothing here is implemented yet.

## V2 candidates

- **DEV.to adapter** — DEV.to has a frontmatter contract (`title`,
  `published`, `tags`, `cover_image`, `canonical_url`) and liquid-tag embeds.
  Needs research against dev.to's official docs before any rules are
  encoded. The canonical model already carries `canonical_url` and topics.
- **LinkedIn adapter** — fundamentally different: feed-first, no markdown,
  different length norms. Needs its own editorial research.
- **Substack adapter** — newsletter-specific checks (email rendering,
  subject line vs. article title, post vs. email sections).
- **Ghost / Hashnode adapters** — both markdown-native; likely the easiest
  ports once the adapter pattern is proven twice.
- **MCP server** — expose review/check/factcheck as MCP tools so non-CLI
  agents can call them directly.
- **Advanced research mode** — structured source-interview workflow,
  contradiction tracking across multiple sources, automatic research.md
  updates during drafting.
- **Image recommendations** — diagram/alt-text assistance (generation stays
  out of scope; captioning/alt-text checking is in spirit).
- **Social post adaptation** — derive a canonical article's summary thread
  *with attribution to the article*, keeping the canonical model primary.

## V3 possibilities

- **Personal knowledge base** — link your research.md artifacts across
  articles; reuse verified claims with their sources intact.
- **Article performance analysis** — if *you* choose to connect platform
  analytics, correlate editorial dimensions with outcomes. Strictly opt-in,
  local-first; would never feed an engagement-gaming loop.
- **Publication-specific style profiles** — learn a publication's house
  style (with permission) as a separate advisory profile alongside your
  voice.
- **Content repurposing** — article → talk outline → documentation, from
  the canonical model outward.
- **Multi-language workflows** — translation-aware originality checks
  (Medium's plagiarism guidelines treat unauthorized translation as
  plagiarism) and language-specific readability heuristics.

## Deliberately not on the roadmap

- AI-detection evasion or "humanizer" features.
- Plagiarism laundering of any kind.
- Mass article generation or content-farm tooling.
- Engagement automation (claps, follows, comments).
- Scraping Medium or unofficial API usage.
- A hosted SaaS with your articles on our servers.

The project's philosophy constrains its future: if a feature can't survive
"would an editor you respect put their name on this?", it doesn't get built.
