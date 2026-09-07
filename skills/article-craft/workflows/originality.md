# Workflow: Originality

Use when the user asks to check plagiarism/originality risks — either before
writing (a source article is supplied as "reference") or after (a draft exists
plus its source material).

## Core stance

The goal is an **independently structured article**, not a disguised copy.
When a user asks to "rewrite this article so it doesn't look copied", refuse
that framing and say:

> "Use this source to understand the subject, verify its claims, then
> construct an independent explanation with original organization and
> examples."

Medium's plagiarism guidelines explicitly include "slightly rewriting or
paraphrasing someone else's work (mosaic plagiarism)" and using AI to
rephrase/summarize/remix content into a derivative work that closely
resembles the original in concept, structure, or essential elements.
Violations mean suspension with no appeal (see
[../references/platforms/medium/plagiarism.md](../references/platforms/medium/plagiarism.md)).

## Method (source supplied)

1. **Extract the source's**: central claims, supporting evidence, structure
   (section-by-section), distinctive examples, and anything requiring
   attribution (data, quotes, images, code).
2. **Compare with the draft** (or with the plan, if pre-writing):
   - Sentence-level: near-verbatim passages, close paraphrases with swapped
     synonyms.
   - Structure-level: section order/count mirroring the source.
   - Example-level: reusing the source's distinctive examples, scenarios,
     analogies, or diagrams without attribution.
   - Code-level: copied code blocks (license check: MIT/Apache need
     attribution; Stack Overflow snippets need attribution per CC BY-SA).
3. **Flag risks** with locations and a concrete fix each:
   - "Paragraph 3 mirrors the source's paragraph 2 claim-for-claim — rewrite
     from your own experience or cite and quote explicitly."
   - "Your section order matches the source 1:1 — reorganize around your own
     questions."
4. **Verify the claims you're keeping** via [fact-check.md](fact-check.md);
   don't inherit the source's errors.
5. Encourage the independence test: can the article stand if the reader never
   sees the source? Is there something in it — experience, data, angle — the
   source doesn't have?

## Method (no specific source)

Check for *de facto* derivation: heavily generic text, claims with no
citations, and any passages the author says came "from something I read"
(get the URL, verify, attribute).

## Output

A risk list (HIGH/MEDIUM/LOW per finding), required attributions, and a
recommendation: INDEPENDENT / NEEDS RESTRUCTURING / DERIVATIVE — RETHINK.
Also run the [../checklists/originality.md](../checklists/originality.md)
checklist.
