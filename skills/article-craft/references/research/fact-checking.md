# Fact-Checking (reference)

> Article Craft working standard (INDUSTRY_BEST_PRACTICE), plus Medium policy
> context where noted.

## Claim classes

| Class | Meaning |
|---|---|
| VERIFIED | Confirmed against a Tier 1–2 source in this session |
| LIKELY | Consistent with author's stated experience and multiple Tier 3+ sources, not directly verified |
| UNVERIFIED | No verification performed or possible in this session |
| CONTRADICTED | A retrieved source contradicts the claim |
| OPINION | Value judgment, clearly the author's own |
| ASSUMPTION | Unstated premise that must be made explicit |

## Method

1. **Extract claims** — assertions of fact: statistics, version behaviors,
   API signatures, performance numbers, dates, quotes, security properties.
2. **Classify each** using the table above.
3. **Verify with primary sources** when web access is available: official
   docs, changelogs, papers. A vendor blog is better than a forum; the
   product's own docs are better than the vendor blog.
4. **Mark every assumption.** Capacity numbers, default configurations,
   workload characteristics: say they are assumptions, in the article.
5. **Never invent** citations, statistics, URLs, quotes, or benchmark
   numbers. If you cannot verify, write UNVERIFIED and tell the author.

## Medium context (OFFICIAL_REQUIREMENT)

Medium's AI content policy prohibits "easily disprovable AI-hallucinated
stories, statistics, events, or otherwise incorrect or nonfactual
information," and the Distribution Guidelines make stories with unverified
claims that could be dangerous, illegal, or cause harm (including health
claims) ineligible for General Distribution. Medium curation does not
fact-check — accuracy is the author's responsibility.

## Honesty rules

- When external verification was unavailable, the output must say so
  explicitly and list the claims that remain unverified.
- A claim attributed to the author's own experience stays the author's
  responsibility to confirm — Article Craft marks it LIKELY, never VERIFIED.
- Do not silently downgrade CONTRADICTED claims; report them as findings.
