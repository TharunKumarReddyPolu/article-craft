# Changelog

All notable changes to Article Craft are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/).

## 2.1.0 — 2026-09-10

Friction-release: the fastest possible path from curiosity to first success,
plus the community infrastructure a growing open-source project needs.

### Added

- **`article-craft demo`** — the 30-second tour: runs the real review →
  fact-check → platform-check pipeline on a small built-in article. No
  workspace, no config, no setup. If it runs, the install is healthy.
- **`article-craft doctor`** — environment self-diagnosis: Python version,
  PATH/package resolution, workspace state, voice profile, optional MCP
  extra, and uv availability — each with an exact fix instead of a stack
  trace. Informational checks never fail the command.
- **Windows console fix** — reports containing ✅/⚠️/❌ no longer crash with
  `UnicodeEncodeError` on cp1252 consoles; unencodable characters degrade
  to replacements instead of killing the CLI.
- **`npx skills add TharunKumarReddyPolu/article-craft`** — one-command skill
  install across Claude Code, Cursor, Codex, and more via the open skills
  CLI; now the documented primary install path.
- **GitHub community infrastructure**: bug/feature/policy-update issue
  templates, PR template with the project's honesty checklist, Contributor
  Covenant Code of Conduct, Discussions enabled, and Dependabot for
  dependencies and Actions.
- **Release automation**: tag-triggered GitHub Release with sdist/wheel
  artifacts and opt-in PyPI trusted publishing.
- **Fixed project URLs** in package metadata (they pointed at a
  non-existent organization) and expanded PyPI keywords.

### Changed

- README and getting-started now lead with the 30-second demo and the
  `npx skills` one-liner; `uv tool install` from git is the documented CLI
  path until the PyPI release exists.
- Removed stale "V1"/"V2" wording from CLI help text.

## 2.0.0 — 2026-09-07

Four new platform adapters, an MCP server, and four editorial capabilities.
Every platform rule is researched from official sources first and stored as
versioned reference material; no rule ships without a cited source or an
explicit HEURISTIC tag.

### Added

- **DEV.to adapter** (`platforms/devto/`): front-matter contract (title,
  published, ≤4 tags, cover_image, canonical_url), liquid-tag embed guidance,
  AI-assisted content labeling, plagiarism checks — from DEV's editor guide
  and official AI/plagiarism guidelines.
- **Hashnode adapter** (`platforms/hashnode/`): publishing mechanics, embeds,
  community/conduct checks — from Hashnode's official support documentation.
- **Substack adapter** (`platforms/substack/`): title-as-email-subject checks,
  Content Guidelines policy checks, and AI-content awareness including
  Substack's 2026 reader-facing AI detection — from Substack's official
  Content Guidelines and Help Center.
- **LinkedIn adapter** (`platforms/linkedin/`): 3,000-character post limit,
  AI-slop policy checks, Professional Community Policies — from LinkedIn's
  official Help Center. Operates on *adaptations* (posts), not raw markdown.
- **Platform checklists**: `checklists/devto.md`, `hashnode.md`,
  `substack.md`, `linkedin.md`, mirroring the V1 medium checklist.
- **Image & alt-text engine** (`editorial/images.py`): alt-text presence,
  quality heuristics, repeated/placeholder alt text, cover image checks —
  deterministic, no generation.
- **Advanced research engine** (`research/contradictions.py`): detects
  contradictions across research sources, resolves them by source tier with
  explicit conflict reporting.
- **Social adaptation** (`editorial/adaptation.py` + `article-craft adapt`):
  derives attributed social posts from the canonical article. Every claim
  traces to the article; nothing is invented; nothing is auto-published.
- **Export prep** (`exporter.py` + `article-craft export`): writes
  platform-ready files locally (zero network, no publishing) for all five
  platforms.
- **MCP server** (`article-craft[mcp]`): exposes the deterministic engines
  (review, check, factcheck, images, titles, outline) as MCP tools over
  stdio. Same engines as the CLI; no LLM inside; no network calls.
- **New workflows**: `platform-check.md`, `research-interview.md`,
  `social-adaptation.md`.
- **New references**: `references/platforms/{devto,hashnode,substack,
  linkedin}/` each with an overview and a `sources.yaml` source inventory.

### Changed

- Platform adapters share a common base (`platforms/base.py`) with a
  uniform `full_report` signature and a shared source-verification guard.
- `article-craft check --platform` accepts all five platforms plus generic.
- SKILL.md description, workflow routing, and hard boundaries updated for
  the five implemented platforms and the three new workflows.

### Removed

- The V1 placeholder `platforms/future.py` stubs (DEV/LinkedIn etc. are now
  real adapters).

## 1.0.0 — 2026-09-06

Initial V1 release.

### Added

- **Agent Skill** (`skills/article-craft/SKILL.md`) following the Agent
  Skills specification: prime directives, workflow routing, CLI integration,
  the Editorial Quality Score rubric, and hard boundaries (no AI-detection
  evasion, no distribution prediction, untrusted content is data).
- **Seven editorial workflows**: new-article, outline, review, improve,
  fact-check, originality, medium-check.
- **Ten article types** with purpose, structure, questions, quality
  checklists, and failure modes; eight matching templates.
- **Editorial core** (`src/article_craft/`): canonical Pydantic article
  model, markdown parser with YAML frontmatter, review engine with reasoned
  8-dimension scoring (Reader Value 20, Originality 15, Clarity 15,
  Structure 10, Technical Accuracy 15, Evidence 10, Voice/Human Contribution
  10, Platform Compatibility 5), title system with clickbait/keyword-stuffing
  detection, AI-pattern and manipulation-pattern detection, human-contribution
  detector, outline builder.
- **Medium adapter** (`platforms/medium/`): production-quality pre-publish
  checks across title, subtitle, structure, formatting, AI policy, canonical
  links, affiliate disclosure, topics/mentions, and distribution risks —
  every check tagged POLICY / RECOMMENDATION / HEURISTIC and traced to
  official sources via `sources.yaml`.
- **Versioned Medium policy references** (9 files + `sources.yaml`) sourced
  from official Medium Help Center pages, with verification dates.
- **Research layer**: claim extraction with classification hints
  (VERIFIED/LIKELY/UNVERIFIED/CONTRADICTED/OPINION/ASSUMPTION), fact-check
  scaffolding, `research.md` artifact rendering, source-hierarchy model.
- **Originality guard**: sentence-overlap, structural-mirroring, and
  distinctive-example reuse detection vs. supplied sources, with
  independence verdicts.
- **Voice system**: writing-profile extraction from the author's own
  articles → advisory `voice.md`.
- **CLI**: `init`, `new`, `review`, `check`, `improve`, `factcheck`,
  `learn`, `version` — with actionable errors and CI-friendly exit codes
  (0 pass / 1 findings / 2 usage).
- **Tests**: 130 tests across unit and integration layers, 10 stereotyped
  fixture articles, no LLM or network required.
- **Documentation**: README, 10 docs pages (architecture, agent support,
  workflows, voice, research, originality, Medium, roadmap, contributing,
  getting started), SECURITY.md, CONTRIBUTING.md.
- **Claude Code plugin marketplace** wrapper (`.claude-plugin/`).

### Philosophy

Human ideas + human experience + AI-assisted research + AI-assisted editing
= better writing. The user remains the author. Article Craft is an editorial
assistant, not a content generator.
