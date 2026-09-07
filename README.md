# Article Craft

**An AI editorial workflow for writing better articles.**

Article Craft is an open-source AI editorial workflow for writers who want to research, structure, review, fact-check, and improve articles while keeping themselves in the driver's seat. It ships as a portable [Agent Skill](https://agentskills.io/specification) plus an optional Python CLI.

[![License](https://img.shields.io/github/license/TharunKumarReddyPolu/article-craft)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![CI](https://github.com/TharunKumarReddyPolu/article-craft/actions/workflows/ci.yml/badge.svg)](https://github.com/TharunKumarReddyPolu/article-craft/actions/workflows/ci.yml)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

It is not an article generator. It is an experienced technical editor living inside your AI coding agent — one that asks who your reader is, demands sources for your claims, warns you before you paraphrase too closely, and checks your draft against Medium's actual published policies before you hit publish.

```
Human ideas
+ Human experience
+ AI-assisted research
+ AI-assisted editing
========================
Better writing
```

## 📋 Table of Contents

- [🎯 About Article Craft](#-about-article-craft)
- [✨ Key Features](#-key-features)
- [⚡ Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [📖 The Article Workflow](#-the-article-workflow)
- [🎬 What It Looks Like](#-what-it-looks-like)
- [🧰 What's Inside](#-whats-inside)
- [🧭 Philosophy](#-philosophy)
- [🔒 Privacy](#-privacy)
- [📚 Documentation](#-documentation)
- [🚧 Limitations](#-limitations)
- [⚠️ Troubleshooting](#️-troubleshooting)
- [🤝 Contributing](#-contributing)
- [⭐ Support the Project](#-support-the-project)
- [📄 License](#-license)

## 🎯 About Article Craft

Article Craft is built for developers, engineers, students, and new writers who want to publish better articles but don't yet know how to:

- choose an article angle or structure one
- write a strong introduction and conclusion
- research properly and cite sources
- avoid plagiarism while using sources honestly
- maintain a consistent voice
- prepare an article for Medium

Each editorial workflow is presented in a step-by-step method covering:

- 🧑‍⚖️ **Reasoned review** — an 8-dimension editorial score where every deduction carries a written reason
- 🔎 **Fact-check scaffold** — every claim classified (VERIFIED / LIKELY / UNVERIFIED / CONTRADICTED / OPINION / ASSUMPTION)
- 🛡️ **Originality guard** — mosaic-plagiarism risk, structural mirroring, and unattributed reuse flagged with concrete fixes
- 🏷️ **Medium pre-publish check** — policy-grounded PASS/WARNING/ERROR categories with source receipts
- 🎭 **Voice profiles** — an advisory style profile learned from *your own* past articles
- 📐 **10 article types** — tutorials, explainers, system design, case studies, and more, each with structure and failure modes
- 🔌 **Platform adapters** — a production-quality Medium adapter behind a small platform interface
- 🏠 **Local-first** — no database, no telemetry, no hosted backend; your articles never leave your machine

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧑‍⚖️ Editorial Review | 8-dimension Editorial Quality Score (Reader Value, Originality, Clarity, Structure, Technical Accuracy, Evidence, Voice, Platform) — every deduction explained |
| 🔎 Fact-Check Workflow | Claims extracted and classified; external verification happens through *your* agent's web access under your direction |
| 🛡️ Originality Guard | Flags close paraphrasing and structural mirroring; demands independent structure instead of "rewrites that don't look copied" |
| 🏷️ Medium Check | Pre-publish check grounded in official Medium Help Center policy, with each rule traced to a URL and verification date |
| 🎭 Voice Profiles | `article-craft learn ./my-articles/` builds an advisory profile of tone, sentence length, formatting, and habits from your own writing |
| 📐 Article Types | 10 types (tutorial, explainer, system design, case study, personal experience, opinion, beginner guide, listicle…) with templates and failure modes |
| 🤝 Agent Skill Standard | Works across Claude Code, Codex, Cursor, Gemini CLI, and any agent that reads `SKILL.md` — one canonical skill, no per-agent forks |
| 🏠 Local-First Privacy | No database, no telemetry, no analytics, no SaaS. Publishing stays a manual human act |

## ⚡ Quick Start

1. Install the CLI: `uv tool install article-craft` (or `pip install article-craft`)
2. Install the skill in your agent: copy `skills/article-craft/` into your agent's skills directory (see [Installation](#-installation))
3. Create your editorial workspace: `article-craft init`
4. Start an article from an idea: `article-craft new --idea "..."` — you get a brief, not a ghostwritten draft
5. **Draft the article yourself** — your experience and voice are the point
6. Review it: `article-craft review my-article.md --platform medium`
7. Verify claims: `article-craft factcheck my-article.md`
8. Pre-publish check: `article-craft check my-article.md --platform medium`
9. Work through the publish checklist, fix what it finds, and publish manually

## 📦 Installation

Article Craft works as an **Agent Skill** (the portable `SKILL.md` standard) with an optional Python CLI for deterministic analysis.

**Claude Code** — via plugin marketplace:

```bash
/plugin marketplace add TharunKumarReddyPolu/article-craft
/plugin install article-craft@article-craft
```

Or manually: copy `skills/article-craft/` into your project's `.claude/skills/` directory, or `~/.claude/skills/` for user-wide availability.

**Claude.ai / Claude Desktop** — upload the skill: Settings → Capabilities → Skills → upload `skills/article-craft/` (zipped).

**Codex CLI** — copy `skills/article-craft/` into `~/.codex/skills/` (or `.codex/skills/` in your repo). Codex reads `SKILL.md` per the open Agent Skills standard.

**Cursor** — copy the skill folder into your repo and reference it from `.cursor/rules/`, or point your agent at `skills/article-craft/SKILL.md` in project rules.

**Gemini CLI** — copy `skills/article-craft/` into your project and reference the path from `GEMINI.md`.

**OpenCode / other agents** — any agent that reads markdown instructions can use the skill: point it at `skills/article-craft/SKILL.md`. The skill follows the [Agent Skills specification](https://agentskills.io/specification), so agents with native skills support load it automatically.

> Exact commands evolve per agent release; the canonical artifact is always `skills/article-craft/SKILL.md`. If an agent documents a different install path for skills, follow the agent's docs — the skill itself needs no changes.

**The CLI** (optional, works alongside any agent):

```bash
# with uv (recommended)
uv tool install article-craft

# or with pip
pip install article-craft
```

## 📖 The Article Workflow

One idea → one canonical article → platform-specific preparation:

| Step | Command / workflow | What you get |
|---|---|---|
| 1. Start from an idea | `article-craft new` | Reader promise, thesis, angle, title candidates, research questions — never a ghostwritten article |
| 2. Research | `factcheck` workflow + agent web access | Sources ranked by authority tier (official docs → forums), claims classified |
| 3. Outline | `outline` workflow | Sections that answer questions, ordered by reader need |
| 4. Draft | you (the author) | Your experience, your voice, your mistakes |
| 5. Review | `article-craft review article.md` | 8-dimension reasoned score, critical issues, publish recommendation |
| 6. Fact-check | `article-craft factcheck article.md` | Every claim classified: VERIFIED / LIKELY / UNVERIFIED / CONTRADICTED / OPINION / ASSUMPTION |
| 7. Originality | originality workflow | Mosaic-plagiarism risk, structural mirroring, unattributed reuse flagged with fixes |
| 8. Medium check | `article-craft check article.md --platform medium` | Policy-grounded pre-publish check with PASS/WARNING/ERROR per category |
| 9. Publish checklist | `medium` checklist | The final human pass — including the things only you can verify |

Then, in your agent: *"Review this draft like my editor"* — the skill activates, runs the deterministic analysis, and adds the judgment layer on top.

## 🎬 What It Looks Like

Real output from `article-craft review` on a draft (trimmed):

```markdown
# Editorial Review

# Overall Editorial Quality: 95/100

## Reader Value: 18/20
**Score reasons:**
- -2: Length (178 words) below the type's deliverable range for a case study.

## Structure: 7/10
...

# Critical Issues
_None._

# Recommended Changes
1. [MEDIUM] Expand or merge stub sections...
2. [LOW] Tag fenced blocks (```python, ```bash, ...).

# Publish Recommendation
## READY
Editorial Quality Score 95/100. Meets Article Craft's editorial bar.
This is an editorial judgment, not a prediction of Medium distribution.

> These checks are based on current published guidance and editorial
> heuristics. They do not guarantee Medium distribution.
```

Every deduction carries a written reason. The score is called the **Editorial Quality Score** — never a "boost score" or "virality score", because Article Craft does not attempt to reverse-engineer Medium's ranking system and never predicts distribution.

## 🧰 What's Inside

**7 workflows** — `new-article`, `outline`, `review`, `improve`, `fact-check`, `originality`, `medium-check` — each a step-by-step editorial method, not a prompt template.

**10 article types** — technical tutorial, technical explainer, system design, architecture deep dive, case study, personal experience, opinion, beginner guide, advanced guide, listicle — each with purpose, structure, quality checklist, and common failure modes.

**9 Medium policy references** — distribution, AI policy, plagiarism, formatting, titles, images, publishing, canonical links, topics — each sourced from official Medium Help Center pages with URLs and verification dates in [`sources.yaml`](skills/article-craft/references/platforms/medium/sources.yaml). Policies are versioned reference material, not hardcoded logic, because Medium's policies change.

**8 templates, 4 checklists** — one template per article type; editorial, originality, fact-check, and Medium checklists.

**Editorial Quality Score** — Reader Value 20, Originality 15, Clarity 15, Structure 10, Technical Accuracy 15, Evidence 10, Voice/Human Contribution 10, Platform Compatibility 5. Every deduction requires a written reason.

**Platform abstraction** — a small `PlatformAdapter` protocol with a production-quality `MediumAdapter`. DEV.to, LinkedIn, and Substack adapters are documented stubs (they raise honest `NotImplementedError`s, they don't pretend to work). See [`docs/roadmap.md`](docs/roadmap.md).

## 🧭 Philosophy

**What Article Craft IS:** a writing coach, editorial assistant, research assistant, fact-checking assistant, originality assistant, technical writing reviewer, and Medium publishing-preparation assistant.

**What Article Craft is NOT:** an AI spam generator, content farm, AI-detector bypass, plagiarism rewriter, "humanizer", clickbait generator, or Medium algorithm gaming tool.

The rules that follow from this:

- The user remains the author. Personal experiences are never invented.
- No "rewrite this so it doesn't look copied" — the originality workflow demands independent structure, and explains why mosaic plagiarism is a Medium suspension offense.
- No AI-detection evasion, ever. AI usage follows Medium's disclosure policy instead.
- No distribution prediction. No "this will get Boosted." Ever.
- Claims without sources get flagged, not fabricated.

## 🔒 Privacy

Local-first, by design:

- No database, no telemetry, no analytics, no hosted backend.
- Your articles and your `.article-craft/` workspace never leave your machine.
- The CLI performs no network calls. Fact-checking against live sources happens through *your* agent's web access, under your direction.
- Nothing is uploaded automatically — publishing is a manual human act.

## 📚 Documentation

| Doc | What it covers |
|---|---|
| [Getting started](docs/getting-started.md) | Install, first article in 15 minutes |
| [Architecture](docs/architecture.md) | The canonical model, engines, adapters |
| [Agent support](docs/agent-support.md) | Per-agent install details and behavior |
| [Writing workflows](docs/writing-workflows.md) | The full editorial pipeline in practice |
| [Custom voice](docs/custom-voice.md) | Voice profiles from your own writing |
| [Research](docs/research.md) | Source hierarchy, fact-checking, citations |
| [Originality](docs/originality.md) | The originality guard and how to use sources honestly |
| [Medium](docs/medium.md) | The Medium adapter, policies, and their sources |
| [Roadmap](docs/roadmap.md) | V2/V3 possibilities (DEV.to, Substack, MCP server…) |
| [Contributing](docs/contributing.md) | How to add adapters, workflows, policy updates |

## 🚧 Limitations

- The deterministic checks are heuristics. They catch common failure modes; they don't replace a human editor, and they don't evaluate deep technical correctness — your agent's judgment layer does that, with the skill's references as its method.
- Originality analysis is risk-surfacing between documents you supply, not a plagiarism *detector* and not a clearance certificate.
- The Medium adapter reflects the Help Center pages verified on the dates in `sources.yaml`. Medium changes its policies; re-verify before relying on any single rule. The tool tells you the date each rule was last verified.
- V1 supports Medium and generic targets only. Other platforms are stubs with roadmap notes.
- The CLI never fetches web content; fact-check verification requires an agent with web access, or manual verification.

## ⚠️ Troubleshooting

- **`python` opens the Microsoft Store** (Windows): your PATH has the Store alias, not a real Python. Install Python 3.11+ from [python.org](https://www.python.org/downloads/) or use `uv tool install article-craft`, which manages its own Python.
- **`article-craft: command not found` after pip install**: your Python `Scripts`/`bin` directory isn't on PATH. Use `python -m article_craft.cli.main` as a fallback, or install with `uv tool install` which handles PATH.
- **Antivirus flags uv**: some AV engines flag unsigned Rust binaries (uv is Astral's, used by major projects). Verify the checksum from the [uv releases page](https://github.com/astral-sh/uv/releases) before whitelisting.
- **`Could not parse article.md because the file is not valid UTF-8`**: re-save the file as UTF-8 (in VS Code: bottom-right encoding → "Save with encoding → UTF-8").
- **Review says my article has no sections**: Article Craft reads H2 (`##`) headings as sections. If your headings are bold text (`**Like This**`), convert them to real headings.

## 🤝 Contributing

Contributions are welcome! Please check [CONTRIBUTING.md](CONTRIBUTING.md) for details on:

- 🧩 Adding editorial workflows and article types
- 🔌 Adding platform adapters (DEV.to, LinkedIn, Substack…)
- 🏷️ Updating Medium policy references
- 🧪 Tests, writing references, and CLI features

For **Medium policy changes**, CONTRIBUTING requires the official source URL, the date checked, the affected rule, and a description of the change. Before contributing, please open an issue to discuss your idea so it aligns with the project's goals. See also [docs/contributing.md](docs/contributing.md).

## ⭐ Support the Project

If Article Craft helps you write and publish better articles, please consider:

- ⭐ Starring the repository so other writers can find it
- 🐛 [Opening issues](https://github.com/TharunKumarReddyPolu/article-craft/issues) for bugs or policy pages that have changed
- 🔀 Contributing a platform adapter or editorial workflow
- ✍️ Writing about your experience using it — with attribution, of course

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=TharunKumarReddyPolu/article-craft&type=Date)](https://star-history.com/#TharunKumarReddyPolu/article-craft&Date)

## 📄 License

[Apache-2.0](LICENSE). The Medium policy summaries in the skill's references quote from Medium's public Help Center for informational purposes; Medium's own pages remain the authoritative source.

---

**Research better, write clearer, publish with confidence — while you stay the author.** ✍️
