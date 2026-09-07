# Custom Voice

How `article-craft learn` builds a voice profile from **your own** writing,
and what it's for.

## What it does

```bash
article-craft learn ./my-articles/
# → .article-craft/voice.md
```

It analyzes your existing markdown articles and extracts an advisory
profile:

- **Rhythm** — average/median sentence length, long-sentence ratio,
  paragraph length.
- **Voice signals** — first-person and second-person rates, hedging, filler
  adverbs, example/analogy/question density.
- **Structure** — section length, heading style (Title Case vs sentence
  case), list/code/image density.
- **Vocabulary** — recurring content words and signature phrases (recurring
  2-grams).
- **Derived labels** — tone (personal-narrative / conversational-technical /
  formal-technical) and technical depth.

## What it's for

The profile keeps the agent honest about *your* voice during improve/review
workflows: suggestions should sound like you, not like the model's default
register. It answers "is this sentence mine?" statistically — and it's
explicitly advisory, a description of your existing patterns rather than a
style mandate.

## Rules the tool enforces on itself

- **Your own writing only.** The voice system exists to model the user's own
  style. Using it to imitate another person's style from copyrighted
  sources is out of scope and against the project's principles.
- **Never fabricate experience.** A profile can describe how often you use
  first person; it cannot and will not invent stories to fill that quota.
- **No "humanizer" behavior.** The goal is clarity in your voice, not
  disguising AI text as human-written. See the Medium AI policy reference
  for what disclosure requires.

## Practical tips

- Feed it 3+ articles for stable statistics; one article is a snapshot,
  not a profile.
- Keep the corpus representative: if you want casual blog voice, don't
  teach it exclusively from formal docs.
- `voice.md` is yours — edit it. Add lines like "avoid 'leverage'" or
  "prefer British spelling"; the agent treats the whole file as advisory
  context.
- Re-run `learn` after your style evolves. The workspace file is
  overwritten; version the directory if you want history.

## How it's used in workflows

- `improve` — proposed rewrites match your rhythm and vocabulary; the plan
  explicitly tells the agent to check `voice.md`.
- `review` — the Voice dimension considers author presence; the profile
  helps the agent distinguish "lost your voice" from "polished your voice".
- `new` — the brief's tone guidance comes from your config + profile.

## Limitations

- Statistical, not semantic: it can tell you your average sentence length,
  not whether your metaphors land.
- English-centric patterns for tone labels; the raw statistics are
  language-agnostic.
- It won't catch deliberate style shifts (an intentionally formal guest
  post will skew the profile if you include it).
