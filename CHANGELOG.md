# Changelog

All notable changes to Article Craft are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/).

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
