# Medium AI Content Policy (reference)

> Source: [Artificial Intelligence (AI) content policy](https://help.medium.com/hc/en-us/articles/22576852947223-Artificial-Intelligence-AI-content-policy)
> (official; verified 2026-09-06). See `sources.yaml` → `medium-ai-content-policy`.

## Definitions (OFFICIAL_REQUIREMENT)

- **AI-generated writing**: writing where the majority of the content has been
  created by an AI writing program with little or no edits, improvements,
  fact-checking, or changes.
- **AI-assistive technology**: AI used for outlining, spelling/grammar
  checking, fact-checking, and similar support. Allowed when used responsibly.

## The rules (OFFICIAL_REQUIREMENT)

1. AI-generated writing — disclosed or not — **may not be paywalled** in the
   Partner Program. Stories found violating this may be removed from the
   paywall and/or the writer's Partner Program enrollment revoked.
2. **Undisclosed** AI-generated writing gets **Network Only** distribution
   (followers only, no wider reach).
3. Any story incorporating AI assistance must be **clearly labeled**. Undisclosed
   AI-assisted text is likewise restricted to the author's personal network.
4. **AI-generated images** are allowed but must include a caption identifying
   them as such, and must not violate Medium Rules.
5. Not allowed: AI-generated content created **solely to rank in SEO results**
   to promote affiliate links (e.g., spammy book summaries, product reviews).
6. Not allowed: using AI to rephrase, summarize, remix, or otherwise modify
   existing content into a derivative work closely resembling the original in
   concept, structure, or essential elements (see `plagiarism.md`).
7. Not allowed: easily disprovable AI-hallucinated stories, statistics,
   events, or nonfactual information.

## Disclosure guidance (OFFICIAL_RECOMMENDATION)

- FAQ: you do **not** need to disclose grammar/spell checkers, outline
  assistance, or fact-verification help. You **must** disclose AI-generated
  text or images.
- For AI-generated text: a simple sentence within the first two paragraphs,
  e.g. *"This story was written with the assistance of an AI writing program."*
- For AI-generated images: note it in the image caption.
- Medium uses a wide variety of tools plus human review to detect AI content.

## What Article Craft does with this (POLICY + HEURISTIC)

- `article-craft check --platform medium` reads the article's frontmatter
  (e.g. `ai_assistance: none | assistive | generated`) and surfaces the
  relevant policy consequence: paywall ineligibility for generated text,
  required disclosure, image captioning.
- Article Craft **never** offers advice for hiding AI usage or bypassing AI
  detection, and never helps generate undisclosed AI text.
- Brainstorming, outlining, editing, fact-checking, and research help are
  assistive uses; wholesale drafting that ends up as the majority of the
  story is generated content under Medium's definition — the review workflow
  warns about this distinction because it changes paywall and distribution
  eligibility.
