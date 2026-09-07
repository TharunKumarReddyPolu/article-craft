# Workflow: Research Interview & Contradiction Tracking

Use during the research phase when the author is gathering sources, and
especially when **sources disagree**.

## Method

1. **Build the research artifact** (`research.md`) per
   `references/research/source-hierarchy.md`: one entry per source with
   title, URL, authority tier (1 official → 5 avoid), date, and the
   specific claims it supports.
2. **Interview each source deliberately.** For every research question,
   ask: what does this source actually claim? What evidence does it give?
   Is the claim first-hand (they measured it) or repeated (they cite
   someone else)? First-hand Tier 1/2 claims outrank repeated claims.
3. **Track contradictions explicitly.** When two sources make conflicting
   claims about the same fact (different numbers, opposed quantifiers,
   negation), record a conflict entry:
   - topic (the shared entity, e.g. the version number)
   - claim A with its source, claim B with its source
   - resolution: the higher-authority tier wins; **if tiers tie, leave the
     conflict unresolved and say so** — never silently pick a winner.
4. **Update research.md as drafting proceeds.** New claims the author
   introduces get added with their sources; the fact-check workflow
   re-classifies them.
5. **CLI support** (if available): the research models support
   `conflicts` with tier-based resolution; `article-craft factcheck` flags
   CONTRADICTED claims. The MCP tool `factcheck_scaffold` does the same
   for agents without the CLI.

## Output

A research artifact where every claim traces to a source, every
contradiction is either resolved by the hierarchy or explicitly marked
UNRESOLVED, and every unresolved conflict carries a "verify against a
primary source before using either claim" note.
