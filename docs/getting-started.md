# Getting Started

From zero to a reviewed article in about 15 minutes.

## 1. Install the CLI (optional but recommended)

```bash
uv tool install article-craft
# or: pip install article-craft
```

Requires Python 3.11+. The CLI is an accelerator — every workflow also works
with agent reasoning alone.

## 2. Install the skill in your agent

Copy `skills/article-craft/` to wherever your agent reads skills from:

| Agent | Location |
|---|---|
| Claude Code | `.claude/skills/article-craft/` (project) or `~/.claude/skills/article-craft/` (user) |
| Codex CLI | `~/.codex/skills/article-craft/` or `.codex/skills/` in the repo |
| Cursor | Anywhere in the repo; reference from `.cursor/rules/` |
| Gemini CLI | Anywhere in the repo; reference from `GEMINI.md` |
| OpenCode / others | Anywhere; point the agent at `SKILL.md` |

See [agent-support.md](agent-support.md) for details and marketplace installs.

## 3. One-time workspace setup

```bash
article-craft init
```

This creates `.article-craft/` (config, voice, audience, topics, preferences).
It's personal to you and gitignored by default. Answer honestly — the
audience and tone settings shape every later workflow.

## 4. Start an article

```bash
article-craft new --idea "Kafka exactly-once semantics" \
  --audience "backend engineers" \
  --type technical-explainer \
  --platform medium \
  --output brief.md
```

The brief contains: title candidates (each with an accuracy note), the
reader promise, thesis, angle, an outline with per-section word targets,
research questions, and **author contribution prompts** — the part only you
can write.

Deliberately, `new` does not write the article.

## 5. Research with your agent

Give the brief to your agent and ask it to follow the skill's research
method: Tier 1 sources first (official docs, changelogs, standards), claims
classified, sources recorded with URLs and dates. The agent writes
`research.md` — a working artifact that stays separate from your article.

## 6. Draft it yourself

Write the article. Use the matching template from
`skills/article-craft/templates/` as a skeleton. Write your contribution
first — the experience, the benchmark, the decision — then the explanation
around it.

## 7. Review

```bash
article-craft review my-article.md --platform medium
```

You get the Editorial Quality Score (with a written reason for every
deduction), critical issues, recommended changes, the Medium check, and a
publish recommendation: READY / READY AFTER CHANGES / DO NOT PUBLISH YET.

## 8. Fact-check and originality

```bash
article-craft factcheck my-article.md   # claim scaffold; agent verifies
```

If you used source articles, ask your agent to run the originality workflow
against them: it flags close paraphrase, structural mirroring, and
unattributed reuse before Medium (or a reader) does.

## 9. Final check and publish checklist

```bash
article-craft check my-article.md --platform medium
```

Work through `skills/article-craft/checklists/medium.md` by hand. Then
publish yourself — Article Craft never automates publishing.

## Next steps

- Run `article-craft learn ./your-old-articles/` so reviews respect your voice.
- Read [writing-workflows.md](writing-workflows.md) for the full pipeline.
- Skim [medium.md](medium.md) to understand what the Medium checks verify.
