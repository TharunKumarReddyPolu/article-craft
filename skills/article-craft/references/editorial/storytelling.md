# Storytelling (reference)

> Article Craft editorial craft guidance (INDUSTRY_BEST_PRACTICE).

## Why story belongs in technical writing

Readers remember what happened to you, not what the documentation says.
Story is how first-hand experience becomes Reader Value — which is exactly
what Medium's Boost criteria describe: "credible, first-hand experience...
communicated effectively."

## The minimal story unit

1. **Situation**: enough context to feel the stakes ("Black Friday, traffic
   40x normal, we were on-call").
2. **Complication**: what went wrong or surprised you ("the cache didn't
   save us — it made it worse").
3. **Turn**: what you did or learned ("the fix wasn't adding cache, it was
   bounding the fan-out").
4. **Resolution + lesson**: the transferable takeaway ("bound fan-out at
   the design stage, not the incident stage").

Four sentences. Use it for the intro, for section openers, for the
conclusion.

## Honest storytelling rules

- **Real events only.** Never manufacture a personal story. Fabricated
  experience is both dishonest and (per Medium's AI/hallucination policy
  context) distribution poison.
- **You are a character, not a hero** — unless you earned it. Readers trust
  writers who admit the mistake they made.
- **Specificity beats drama.** "The deploy took 47 minutes and I watched
  the error rate tick up at minute 3" beats "it was a disaster."
- **Composite examples must be labeled.** "A composite example based on
  two production incidents" is honest; an implied real event that isn't is
  not.
- **Privacy**: strip or generalize identifying details of employers,
  colleagues, and customers unless you have permission.

## Where story does NOT belong

- API reference material.
- The middle of a step-by-step procedure (put it before or after).
- As a substitute for the actual explanation ("let me tell you about my
  journey" articles that never explain anything).

## The test

After any story element, ask: what does the reader take away that they
wouldn't have from the docs? If the answer is "nothing," cut it. If the
answer is "they'll remember the lesson," keep it.
