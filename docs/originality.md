# Originality

The originality guard: what it checks, what it refuses to do, and how to
use sources honestly.

## The core stance

The goal is an **independently structured article** — not a disguised copy.
When someone asks Article Craft to "rewrite this article so it doesn't look
copied", the tool refuses that framing and answers:

> "Use this source to understand the subject, verify its claims, then
> construct an independent explanation with original organization and
> examples."

This isn't squeamishness. Medium's plagiarism guidelines explicitly include
"slightly rewriting or paraphrasing someone else's work (mosaic plagiarism)"
and "using artificial intelligence tools to rephrase, summarize, remix, or
otherwise modify existing content in a manner that results in a derivative
work which closely resembles the original content in concept, structure, or
essential elements." Violations mean suspension with no appeal.

## What the guard checks (with a supplied source)

1. **Sentence-level overlap** — shingle-based similarity between draft and
   source sentences. HIGH at ≥55% Jaccard similarity, MEDIUM at ≥35%.
2. **Structural mirroring** — order-aware matching of section titles. If
   your sections follow the source's outline 1:1, that's structure
   imitation, which Medium's definition explicitly covers.
3. **Distinctive-example reuse** — proper nouns, product names, and
   specific numbers from the source appearing in your draft without
   attribution.
4. **Unattributed quotes** — verbatim passages without quotation/attribution
   markers.

Every finding comes with a concrete fix. The verdict scale:

- **INDEPENDENT** — no significant risks found.
- **NEEDS RESTRUCTURING** — medium risks; reorganize/attribute.
- **DERIVATIVE — RETHINK** — high risks; the article needs a different
  skeleton, not cosmetic edits.

## What it is NOT

- Not a plagiarism *detector*. It compares documents you supply; it can't
  know about articles you didn't give it.
- Not a clearance certificate. A clean report means "no mechanical
  similarity to the sources you provided", nothing more.
- Not a spinner. It will not paraphrase-for-disguise, ever.

## Using sources honestly (the method)

1. **Read to understand, then close the source.** Outline your article from
   your own questions about the topic, not the source's table of contents.
2. **Verify independently.** Don't inherit the source's claims — check them
   against primary sources (fact-check workflow).
3. **Attribute everything borrowed**: data, quotes, images, code, distinctive
   examples. Credit doesn't replace permission for copyrighted material.
4. **Add what the source doesn't have**: your experience, your measurements,
   your failure stories, your position. That's the part that makes the
   article yours — and, per Medium's distribution guidelines, the part
   curators look for.
5. **Run the independence test**: could the article stand if the reader
   never saw the source? Does it contain something the source doesn't?

## Code and images

- Code snippets have licenses. MIT/Apache require attribution; Stack
  Overflow snippets are CC BY-SA (attribute and link). Copying code into an
  article without checking the license is a copyright risk, not just a
  politeness issue.
- Images: owned, licensed (Unsplash etc.), or credited. AI-generated images
  must be captioned as such on Medium.

## Self-plagiarism and cross-posting

Republishing your own work across platforms is allowed on Medium (with a
canonical link — see the Medium references), but duplicating the *same*
article across multiple Medium accounts or as unlisted stories is a Rules
violation. Article Craft's canonical-model design supports adaptation
(rewriting for a platform's audience), not copy-paste distribution.
