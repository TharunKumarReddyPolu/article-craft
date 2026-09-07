# Article Craft

**An AI editorial workflow for writing better articles.**

Article Craft is an open-source AI editorial workflow for writers who want to research, structure, review, fact-check, and improve articles while keeping themselves in the driver's seat.

It is not an article generator. It is an experienced technical editor living inside your AI coding agent — one that asks who your reader is, demands sources for your claims, warns you before you paraphrase too closely, and checks your draft against Medium's actual published policies before you hit publish.

```
Human ideas
+ Human experience
+ AI-assisted research
+ AI-assisted editing
========================
Better writing
```

## What it looks like

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

## The Article Workflow

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

## Install

Article Craft works as an **Agent Skill** (the portable `SKILL.md` standard) with an optional Python CLI for deterministic analysis.

**Claude Code** — via plugin marketplace:

```bash
/plugin marketplace add <your-org>/article-craft
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

## Quick start

```bash
# One-time: set up your personal editorial workspace
article-craft init

# Start an article from an idea (brief only — you stay the author)
article-craft new --idea "Kafka exactly-once semantics" \
  --audience "backend engineers" --type technical-explainer --platform medium

# Review a draft
article-craft review my-article.md --platform medium

# Fact-check scaffold (claims classified; your agent verifies with web access)
article-craft factcheck my-article.md

# Improvement plan without a rewrite
article-craft improve my-article.md --section "introduction"

# Teach it your voice from your own past articles
article-craft learn ./my-articles/
```

Then, in your agent: *"Review this draft like my editor"* — the skill activates, runs the deterministic analysis, and adds the judgment layer on top.

## What's inside

**7 workflows** — `new-article`, `outline`, `review`, `improve`, `fact-check`, `originality`, `medium-check` — each a step-by-step editorial method, not a prompt template.

**10 article types** — technical tutorial, technical explainer, system design, architecture deep dive, case study, personal experience, opinion, beginner guide, advanced guide, listicle — each with purpose, structure, quality checklist, and common failure modes.

**9 Medium policy references** — distribution, AI policy, plagiarism, formatting, titles, images, publishing, canonical links, topics — each sourced from official Medium Help Center pages with URLs and verification dates in [`sources.yaml`](skills/article-craft/references/platforms/medium/sources.yaml). Policies are versioned reference material, not hardcoded logic, because Medium's policies change.

**8 templates, 4 checklists** — one template per article type; editorial, originality, fact-check, and Medium checklists.

**Editorial Quality Score** — Reader Value 20, Originality 15, Clarity 15, Structure 10, Technical Accuracy 15, Evidence 10, Voice/Human Contribution 10, Platform Compatibility 5. Every deduction requires a written reason.

**Platform abstraction** — a small `PlatformAdapter` protocol with a production-quality `MediumAdapter`. DEV.to, LinkedIn, and Substack adapters are documented stubs (they raise honest `NotImplementedError`s, they don't pretend to work). See [`docs/roadmap.md`](docs/roadmap.md).

## Philosophy

**What Article Craft IS:** a writing coach, editorial assistant, research assistant, fact-checking assistant, originality assistant, technical writing reviewer, and Medium publishing-preparation assistant.

**What Article Craft is NOT:** an AI spam generator, content farm, AI-detector bypass, plagiarism rewriter, "humanizer", clickbait generator, or Medium algorithm gaming tool.

The rules that follow from this:

- The user remains the author. Personal experiences are never invented.
- No "rewrite this so it doesn't look copied" — the originality workflow demands independent structure, and explains why mosaic plagiarism is a Medium suspension offense.
- No AI-detection evasion, ever. AI usage follows Medium's disclosure policy instead.
- No distribution prediction. No "this will get Boosted." Ever.
- Claims without sources get flagged, not fabricated.

## Privacy

Local-first, by design:

- No database, no telemetry, no analytics, no hosted backend.
- Your articles and your `.article-craft/` workspace never leave your machine.
- The CLI performs no network calls. Fact-checking against live sources happens through *your* agent's web access, under your direction.
- Nothing is uploaded automatically — publishing is a manual human act.

## Documentation

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

## Troubleshooting

- **`python` opens the Microsoft Store** (Windows): your PATH has the Store alias, not a real Python. Install Python 3.11+ from [python.org](https://www.python.org/downloads/) or use `uv tool install article-craft`, which manages its own Python.
- **`article-craft: command not found` after pip install**: your Python `Scripts`/`bin` directory isn't on PATH. Use `python -m article_craft.cli.main` as a fallback, or install with `uv tool install` which handles PATH.
- **Antivirus flags uv**: some AV engines flag unsigned Rust binaries (uv is Astral's, used by major projects). Verify the checksum from the [uv releases page](https://github.com/astral-sh/uv/releases) before whitelisting.
- **`Could not parse article.md because the file is not valid UTF-8`**: re-save the file as UTF-8 (in VS Code: bottom-right encoding → "Save with encoding → UTF-8").
- **Review says my article has no sections**: Article Craft reads H2 (`##`) headings as sections. If your headings are bold text (`**Like This**`), convert them to real headings.

## Limitations (honest ones)

- The deterministic checks are heuristics. They catch common failure modes; they don't replace a human editor, and they don't evaluate deep technical correctness — your agent's judgment layer does that, with the skill's references as its method.
- Originality analysis is risk-surfacing between documents you supply, not a plagiarism *detector* and not a clearance certificate.
- The Medium adapter reflects the Help Center pages verified on the dates in `sources.yaml`. Medium changes its policies; re-verify before relying on any single rule. The tool tells you the date each rule was last verified.
- V1 supports Medium and generic targets only. Other platforms are stubs with roadmap notes.
- The CLI never fetches web content; fact-check verification requires an agent with web access, or manual verification.

## Contributing

Contributions welcome — editorial workflows, article types, platform adapters, tests, and reference material. For **Medium policy changes**, CONTRIBUTING requires the official source URL, the date checked, the affected rule, and a description of the change. See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/contributing.md](docs/contributing.md).

## License

[Apache-2.0](LICENSE). The Medium policy summaries in the skill's references quote from Medium's public Help Center for informational purposes; Medium's own pages remain the authoritative source.
