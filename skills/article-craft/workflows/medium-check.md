# Workflow: Medium check

Use when the user asks "is this ready for Medium?", wants a pre-publish
check, or asks about Medium policies/formatting.

## Source of truth

Read the policy references under
[../references/platforms/medium/](../references/platforms/medium/) as needed —
they carry the official source URLs and verification dates. Never state a
Medium rule from memory that contradicts the reference files; if the files
look stale, say so and recommend checking the Help Center.

## Categories to check

Run each category and mark PASS / WARNING / ERROR / NOT CHECKED / NOT
APPLICABLE. If `article-craft` is installed, `article-craft check <file>
--platform medium` produces the deterministic part; layer judgment on top.

1. **Title** — accurate, specific, not sensationalistic/generic (Medium
   disqualifies both), represents the story.
2. **Subtitle** — adds the promise/angle; not clickbait.
3. **Structure** — sections, flow, no heading stuffing, reasonable length for
   the type.
4. **Reader Value** — promise delivered, insight present.
5. **Originality** — no mosaic-plagiarism risk, author contribution present.
6. **AI Policy** — from frontmatter `ai_assistance:` or the conversation:
   - `generated` (majority AI-written with little human edit): cannot be
     paywalled (Partner Program); must be disclosed in the first two
     paragraphs or it gets Network-only distribution. Warn clearly.
   - `assistive` (outlining/grammar/fact-check help): disclosure required for
     AI-assisted text per policy; no disclosure needed for pure
     grammar/spell-check.
   - AI-generated images: caption identifying them as AI-generated required.
7. **Formatting** — heading hierarchy, code blocks tagged, links descriptive,
   no raw HTML the editor will mangle, embeds by URL not code.
8. **Evidence** — claims classified, sources cited, no hallucinated
   statistics.
9. **Images** — alt text present, captions, credits; AI images captioned;
   no unlicensed copyrighted images.
10. **Canonical Link** — if `originally_published: true` or `canonical_url:`
    set: remind the author to set the canonical link in story settings (only
    the author can). If cross-posting is planned: same.
11. **Topics** — 5 max, actually matching content, no topic-stuffing, no
    excessive @mentions.
12. **Distribution Risks** — clickbait, unconstructive negativity, low-value
    patterns (link round-ups, SEO-driven affiliate content), unverified
    dangerous claims, stories about Medium/Partner Program (Network-only;
    tag `medium-meta`).

## Output format

```
# Medium Pre-Publish Check

Overall: PASS | WARNING | ERROR

## Title
STATUS
(findings)

(repeat per category)

# Fix Before Publishing
1. ...
2. ...
3. ...

These checks are based on current published guidance and editorial
heuristics. They do not guarantee Medium distribution.
```

## Hard rules

- Never predict a Boost. Never say "this will be Boosted" or score
  "boost likelihood".
- Never advise hiding AI usage or evading AI detection.
- Never automate publishing; the author clicks Publish.
