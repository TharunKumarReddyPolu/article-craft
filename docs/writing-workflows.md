# Writing Workflows

The full editorial pipeline in practice, with the judgment each step needs.

## The pipeline

```
idea → brief → research → outline → DRAFT (you) → review → fact-check
     → originality → medium-check → checklist → publish (you)
```

Steps before and after the draft are where the tooling helps most; the draft
itself is yours.

## 1. Brief (`article-craft new`)

The brief forces the three decisions that make or break an article:

- **Reader promise** — "After reading, a backend engineer will be able
  to..." If you can't finish that sentence, you're not ready to write.
- **Angle** — what this article offers that the current top results don't.
  "A clear explanation" is not an angle; everyone claims that.
- **Author contribution** — the experience, experiment, decision, or
  position only you have. The brief asks for it up front because it should
  shape the article, not decorate it.

Title candidates come in seven approaches (descriptive, problem-oriented,
outcome-oriented, curiosity-driven, technical, beginner-friendly,
experience-based), each with clarity/specificity/promise scores and an
**accuracy note** — the thing you must verify before using it.

## 2. Research

Follow `references/research/source-hierarchy.md`:

- Tier 1 first: official docs, changelogs, standards, papers.
- One claim, one source minimum; two independent sources for load-bearing
  numbers.
- Date every source. Version-sensitive claims rot.
- Record everything in `research.md` — thesis, questions, sources with
  authority and dates, claims with confidence, contradictions, statistics.

The research artifact stays separate from the article. It's your evidence
locker, not prose to copy from.

## 3. Outline

Section titles state claims or questions, not topics:

- Topic: "Kafka ordering" — weak.
- Claim: "Why Kafka's ordering guarantee breaks across partitions" — strong.

Each section gets: the question it answers, its purpose, a target word
count. The outline is falsifiable — you should be able to tell, section by
section, whether the draft delivered.

## 4. Draft (the human part)

Write your contribution first. Use the type template as a skeleton, not a
straitjacket. Practical rules from the references:

- Introductions: earn paragraph two, establish the promise and your
  credibility, set scope. No throat-clearing.
- One idea per sentence/paragraph; define terms on first use.
- Code you publish must be code you ran; state versions.
- Failure modes are content, not appendix.

## 5. Review (`article-craft review`)

The review engine scores eight dimensions with written reasons. Read the
*reasons*, not just the number: a 85 with "title leans generic" needs a
different fix than an 85 with "evidence thin in section 3".

The agent layer adds what heuristics can't: whether the analogy actually
works, whether the trade-off analysis is honest, whether the intro sounds
like you.

## 6. Fact-check (`article-craft factcheck`)

The CLI extracts candidate claims (statistics, benchmarks, version
behavior, attributions, superlatives, causal claims, security claims) and
marks them UNVERIFIED with verification hints. Your agent — with web access
— verifies against primary sources and upgrades statuses with evidence.
Without web access, the report says so explicitly and everything stays
UNVERIFIED. The CLI never invents verification results.

## 7. Originality

If source articles informed your draft, run the originality workflow
against them. It flags sentence-level overlap, structural mirroring,
distinctive-example reuse, and unattributed quotes — with fixes. The goal
is an article that stands without the source, not one that hides it.

## 8. Medium check (`article-craft check --platform medium`)

Policy-grounded categories: title, subtitle, structure, formatting, AI
policy, canonical link, affiliate disclosure, topics/mentions, distribution
risks. Each finding is tagged POLICY / RECOMMENDATION / HEURISTIC with its
official source. Output ends with the standing disclaimer — checks don't
guarantee distribution.

## 9. Final checklist and publish

Work `checklists/medium.md` by hand. The last items are deliberately human:
read it top to bottom, confirm the voice is yours, confirm every factual
claim, final proofread. Then click Publish yourself.
