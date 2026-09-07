# Research

How Article Craft researches, classifies claims, and cites sources — and
the honesty rules it won't break.

## The source hierarchy

| Tier | Kind | Use for |
|---|---|---|
| 1 | Official documentation, standards, primary research, papers | Facts, policy claims, technical behavior |
| 2 | Engineering blogs of the relevant orgs, reputable technical docs | Practice, context, trade-offs |
| 3 | Established writers, well-regarded community resources | Perspective, craft |
| 4 | Forums, Reddit, Stack Overflow, GitHub issues | Pointers to real problems; verify elsewhere |
| 5 | Random blogs, SEO farms, AI-generated summaries | Avoid as claim support |

Rules:

1. Never represent a lower tier as a higher one. Community advice is never
   "official policy".
2. When official sources conflict, prefer the newer official source and
   note the conflict in `research.md`.
3. Date every source; technical claims rot.
4. Prefer primary over commentary — the changelog beats the blog about the
   changelog.
5. Load-bearing claims (numbers, benchmarks, safety, security) want two
   independent sources.

## Claim classification

| Class | Meaning |
|---|---|
| VERIFIED | Confirmed against a Tier 1–2 source this session |
| LIKELY | Consistent with the author's stated experience and multiple Tier 3+ sources; not directly verified |
| UNVERIFIED | No verification performed or possible |
| CONTRADICTED | A retrieved source contradicts it |
| OPINION | Value judgment, clearly the author's own |
| ASSUMPTION | Unstated premise that must be made explicit |

The CLI extracts *candidate* claims deterministically (statistics,
benchmarks, version behavior, attributions, superlatives, causal claims,
security claims) and marks them UNVERIFIED with hints. Upgrading statuses
requires evidence: your agent with web access, checking primary sources,
recording URLs and access dates.

## The research artifact (`research.md`)

```markdown
# Research
## Article Thesis
## Research Questions
## Sources
### Source 1
Title / URL / Authority / Date / Claims / Confidence
## Contradictions
## Statistics
## Claims Requiring Verification
## Potential Examples
```

It stays separate from the final article. It's working material: the place
where "I think this is true" becomes "this is true as of <date>, per
<source>" — or gets cut.

## Honesty rules (non-negotiable)

- **Never invent** citations, statistics, URLs, quotes, or benchmark
  numbers. Not "plausible placeholders", not "for illustration". If it
  can't be verified, it's UNVERIFIED, full stop.
- If external verification was unavailable, the output says exactly that
  and lists what remains unverified.
- The author's own measurements stay LIKELY at most — the tool never
  upgrades them to VERIFIED on the author's behalf.
- CONTRADICTED claims are reported as findings, never silently softened.
- Medium context: hallucinated statistics and incorrect nonfactual
  information are explicitly prohibited by Medium's AI policy, and
  unverified claims that could cause harm disqualify a story from General
  Distribution. Accuracy is the author's responsibility.

## Citations in the article

- Cite facts you didn't experience; cite at the point of use.
- Prefer the primary source over commentary about it.
- Quote sparingly and exactly; paraphrase genuinely in your own structure.
- Date-protect version-sensitive claims ("as of Python 3.12").
- Medium mechanics: inline links are standard; numbered superscript
  citations are explicitly acknowledged in Medium's plagiarism guidelines.
- Never cite AI chat output as a source; cite what it cited, after checking.
