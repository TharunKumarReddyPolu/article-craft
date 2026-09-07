# Roadmap

Version 1 delivered the platform-agnostic editorial core, a production-quality
Medium adapter, and the Agent Skill. **Version 2 (released 2026-09-07)** added
the DEV.to, Hashnode, Substack, and LinkedIn adapters, the MCP server, and
four editorial capabilities — everything in the first list below is now
implemented. What remains is a possibility, not a promise.

## Shipped in V2

- **DEV.to adapter** — frontmatter contract, liquid-tag embeds, AI-labeling
  and plagiarism checks from DEV's official guidelines.
- **Hashnode adapter** — publishing mechanics and community/conduct checks
  from Hashnode's official support documentation.
- **Substack adapter** — title-as-subject checks, Content Guidelines, and
  Substack's 2026 AI-detection awareness.
- **LinkedIn adapter** — post-length limit, AI-slop policy, Professional
  Community Policies; operates on adaptations, not raw markdown.
- **MCP server** — `article-craft-mcp` exposes the deterministic engines as
  MCP tools over stdio (`article-craft[mcp]`).
- **Advanced research mode** — contradiction tracking across sources with
  authority-based resolution, plus the research-interview workflow.
- **Image & alt-text checks** — deterministic review of image references,
  alt-text presence and quality.
- **Social post adaptation** — attributed posts derived from the canonical
  article; every claim traces back; nothing auto-published.
- **Export prep** — platform-ready files written locally for all five
  platforms (zero network calls).

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
