# Workflow: Outline

Use when the user wants to structure or outline an article (standalone, or
after new-article).

## Method

1. Establish (ask if unknown): topic, audience, article type, target length,
   unique angle.
2. Load the type's expected structure from
   [../references/editorial/article-types.md](../references/editorial/article-types.md)
   or the CLI's type registry.
3. Build the outline where **each section title states a claim or question**,
   not a topic. "Kafka" is a topic; "Why Kafka's ordering guarantee breaks
   across partitions" is a section.
4. For each section give: the question it answers, its purpose, and a target
   word count that sums to the requested length.
5. Sanity-check the outline against
   [../references/editorial/structure.md](../references/editorial/structure.md):
   - ordered by the reader's need, not your discovery order
   - progressive disclosure (simple → specific → advanced)
   - no orphan sections; explicit transitions
   - conclusions consolidate, they don't introduce
6. Add: research questions to answer before drafting, potential source types
   (Tier 1 first), and author-contribution prompts.
7. Offer the matching template from [../templates/](../templates/) as a
   starting skeleton.

## Anti-patterns to refuse

- An outline that is a table of contents of an existing article the user wants
  "restructured" — that's the originality workflow's job.
- Sections named "Introduction / Body / Conclusion" with no claims.
- A section per bullet of a source article's structure (structure imitation).
