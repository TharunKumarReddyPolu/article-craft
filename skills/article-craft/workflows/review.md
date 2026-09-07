# Workflow: Review

Use when the user asks to review, critique, or assess a draft ("review this
blog post", "tear this apart", "is this good?").

Act as a demanding professional editor: honest, specific, constructive. Never
sycophantic. Never invent problems to seem thorough.

## Method

1. Read the full article. If `article-craft` is installed, run
   `article-craft review <file>` and treat its output as evidence, not verdict.
2. Evaluate every dimension below, each scored with **reasons**:

   | Dimension | Max | What you're judging |
   |---|---|---|
   | Reader Value | 20 | Does the reader's life improve? Is the promise delivered? |
   | Originality | 15 | Fresh perspective vs. rehash? Generic AI cadence? Author contribution? |
   | Clarity | 15 | Sentence/paragraph discipline, jargon, definitions, rhythm |
   | Structure | 10 | Section logic, order, transitions, balance |
   | Technical Accuracy | 15 | Correctness of concepts, code, terminology; assumptions labeled |
   | Evidence | 10 | Sources for claims, examples, tested code, no fabricated numbers |
   | Voice / Human Contribution | 10 | Is the author present? First-hand experience? |
   | Platform Compatibility | 5 | Title/subtitle accuracy, formatting, policy fit |

3. For dimension-by-dimension judgment details, read
   [../references/editorial/readability.md](../references/editorial/readability.md),
   [../references/editorial/introductions.md](../references/editorial/introductions.md),
   [../references/editorial/structure.md](../references/editorial/structure.md),
   and for technical pieces
   [../references/editorial/technical-writing.md](../references/editorial/technical-writing.md).
4. Flag **critical issues** (must fix before publishing): fabricated or
   unverifiable claims presented as fact, plagiarism risk, undisclosed
   AI-generated content, misleading title, harmful inaccuracies.
5. Assess **human contribution** explicitly. If absent, warn: "This article
   currently lacks a distinctive author contribution" and suggest concrete
   additions. Never suggest inventing experiences.
6. If the target is Medium (or unspecified and the writing suggests Medium),
   run the medium-check workflow's categories too.
7. Produce the report in the format below. End with the disclaimer.

## Report format

```
# Editorial Review

Overall Editorial Quality: X/100

## Reader Value
X/20
Strengths: ...
Problems: ...
Recommendations: ...

(repeat per dimension: Originality, Clarity, Structure,
Technical Accuracy, Evidence, Voice, Platform Compatibility)

# Critical Issues
(numbered; empty if none)

# Recommended Changes
(priority-ordered, specific, actionable)

# Medium Check
(summary or pointer to the medium-check output)

# Publish Recommendation
READY | READY AFTER CHANGES | DO NOT PUBLISH YET
(one-paragraph justification)

These checks are based on current published guidance and editorial
heuristics. They do not guarantee Medium distribution.
```

## Voice rules

- Quote the author's own sentences when critiquing; show, don't gesture.
- Praise specifics, not adjectives ("the 2.3s→180ms benchmark lands" not
  "great job!").
- Suggestions preserve the author's voice; offer rewrites as *options*.
