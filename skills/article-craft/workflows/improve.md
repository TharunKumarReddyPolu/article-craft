# Workflow: Improve

Use when the user asks to improve, edit, tighten, or clarify an article —
without rewriting it wholesale.

## Method

1. Read the article. Run `article-craft review <file>` if available; focus on
   the highest-severity findings.
2. Produce, in order:
   1. **Diagnosis** — 2-4 sentences on what's holding the piece back.
   2. **Priority problems** — ranked list, most impactful first, each tied to
      specific lines/sections.
   3. **Suggested changes** — for each: what to change, why, and how it
      preserves the author's meaning.
   4. **Proposed rewrites** — only for selected passages, and only if useful;
      present as options ("Option A keeps your rhythm..."), never as silent
      replacements.
3. If the user names a section (`--section`, "just the intro", "the caching
   part"), scope the work to it.
4. Offer the next action: apply changes, or move to
   [fact-check.md](fact-check.md) / [medium-check.md](medium-check.md).

## What to preserve (never remove or alter without asking)

- The author's meaning, claims, and conclusions.
- Their personal experiences and anecdotes (you may flag unsupported ones for
  verification — never replace them).
- Their voice: sentence rhythm, level of formality, humor, first-person usage.
  If `.article-craft/voice.md` exists (from `article-craft learn`), treat it
  as the reference for what sounds like *them*.
- The intended audience and technical depth.

## What never to do

- Introduce facts, statistics, or citations the author didn't provide — flag
  the gap instead ("this paragraph needs a source; want me to list candidates
  to verify?").
- Flatten personality into "professional tone" unless asked.
- Pad, repeat, or add an AI-cadence conclusion ("In conclusion, ...").
- Rewrite the whole piece when asked to improve one section.
