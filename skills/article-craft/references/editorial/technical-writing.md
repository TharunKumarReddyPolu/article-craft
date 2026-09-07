# Technical Writing (reference)

> Article Craft editorial craft guidance (INDUSTRY_BEST_PRACTICE), with
> Medium policy context where noted.

## Accuracy first

- **Test the code you publish.** Untested code in a tutorial is a promise
  you haven't kept. State versions: "Tested on Python 3.12, FastAPI 0.115."
- **Never fabricate benchmarks.** Numbers you didn't measure are
  hallucinations. If you cite someone's benchmark, cite them; if you ran
  it, describe the setup and its limits.
- **Clearly identify assumptions.** Capacity numbers, traffic patterns,
  hardware: mark them as assumptions in the text.
- **Pin versions** in tutorials; note when behavior is version-specific.
- Medium policy context (OFFICIAL_REQUIREMENT): hallucinated statistics and
  incorrect nonfactual information are explicitly prohibited by the AI
  content policy, and unverified claims that could cause harm disqualify a
  story from General Distribution.

## Explaining concepts

- **Mental model before mechanism.** Give the reader a correct intuition
  ("a Kafka partition is an append-only log; ordering exists only within a
  partition") before API details.
- **One new concept at a time.** If a paragraph introduces three terms, the
  reader retains none.
- **Concrete example → generalize**, not the reverse. Show the specific
  case first.
- **Error cases are content.** What breaks, what the error looks like, how
  to recover — this is where tutorials earn their keep.
- **Trade-offs, not verdicts.** "X beats Y at small scale; past 10k
  partitions Y wins" is more useful than "X is better."

## System design articles — checklist dimensions

Functional requirements · non-functional requirements · capacity
assumptions · API design · data model · architecture · storage · caching ·
messaging · consistency · availability · partitioning · scaling · failure
handling · observability · security · trade-offs.

A system design article that skips failure handling and trade-offs is a
diagram with words around it.

## Security & operations writing

- Never publish working exploit instructions for unpatched issues; describe
  the class of vulnerability and the fix.
- Include the observability angle: how would a reader know your advice is
  failing in their system?
- Prefer reproducible commands with expected output.

## Terminology discipline

- Use the official term the ecosystem uses; don't coin synonyms for
  searchable concepts.
- Consistency: pick "id" or "identifier" and stick with it.
- Link the canonical docs on first mention of a tool or concept.
