# Workflow: Fact-check

Use when the user asks to fact-check, verify, or audit claims in a draft.

## Method

1. Extract every checkable claim: statistics, version behaviors, API
   signatures, performance numbers, dates, quotes, security properties,
   attributions ("X said..."), and causal assertions.
2. Classify each claim (details in
   [../references/research/fact-checking.md](../references/research/fact-checking.md)):

   | Class | Meaning |
   |---|---|
   | VERIFIED | Confirmed against a Tier 1-2 source this session |
   | LIKELY | Consistent with the author's stated experience and multiple Tier 3+ sources; not directly verified |
   | UNVERIFIED | No verification performed or possible |
   | CONTRADICTED | A retrieved source contradicts it |
   | OPINION | Value judgment, clearly the author's own |
   | ASSUMPTION | Unstated premise — make it explicit in the text |

3. If you have web access: verify against **primary sources** first (official
   docs, changelogs, papers, standards). Record the URL, the tier, and the
   access date for every source consulted. Prefer the newer official source
   when official sources conflict.
4. If you have no web access (or retrieval fails), you MUST state:
   "External verification was not available. Verify these claims before
   publication." and list every UNVERIFIED claim. Do not guess.
5. Never invent citations, statistics, URLs, quotes, or benchmark numbers —
   not even "plausible" ones for illustration. If you can't verify, say
   UNVERIFIED.
6. Mark the author's own measurements LIKELY at most (they are the author's
   responsibility to confirm); never upgrade them to VERIFIED yourself.
7. Output the classification table, then:

   - Claims requiring verification before publish
   - Contradictions found (claim vs. source, with URLs)
   - Assumptions that should be explicit in the article text
   - Suggested wording fixes for CONTRADICTED claims (offer, don't apply)

8. Save the artifact as `research.md` (structure in
   [../../skills/article-craft/references/research/fact-checking.md](../references/research/fact-checking.md))
   or let the CLI's factcheck emit the scaffold. The research artifact stays
   separate from the article.

## Medium context

Medium prohibits "easily disprovable AI-hallucinated stories, statistics,
events, or otherwise incorrect or nonfactual information", and unverified
claims that could cause harm (including health claims) disqualify a story
from General Distribution (see
[../references/platforms/medium/ai-policy.md](../references/platforms/medium/ai-policy.md)
and `distribution.md`). Accuracy is the author's responsibility.
