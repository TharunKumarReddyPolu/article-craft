# Medium

What the Medium adapter checks, where each rule comes from, and the lines
Article Craft will not cross.

## Where the rules live

All Medium policy knowledge is **versioned reference material** in
[`skills/article-craft/references/platforms/medium/`](../skills/article-craft/references/platforms/medium/),
not hardcoded logic:

| File | Official source | Verified |
|---|---|---|
| `distribution.md` | [Distribution Guidelines](https://help.medium.com/hc/en-us/articles/360006362473-Medium-s-Distribution-Guidelines-How-curators-review-stories-for-Boost-General-and-Network-Distribution) | 2026-06-29 page date; checked 2026-09-06 |
| `ai-policy.md` | [AI content policy](https://help.medium.com/hc/en-us/articles/22576852947223-Artificial-Intelligence-AI-content-policy) | checked 2026-09-06 |
| `plagiarism.md` | [Plagiarism Guidelines](https://help.medium.com/hc/en-us/articles/360041640213-Plagiarism-Guidelines) | checked 2026-09-06 |
| `formatting.md` | [Writing and publishing your first story](https://help.medium.com/hc/en-us/articles/225168768-Writing-and-publishing-your-first-story) + [Medium Rules](https://help.medium.com/hc/en-us/articles/213477928-Medium-Rules) | checked 2026-09-06 |
| `titles.md` | Distribution Guidelines | checked 2026-09-06 |
| `images.md` | First-story guide + Distribution Guidelines | checked 2026-09-06 |
| `publishing.md` | First-story guide + Rules + Publications Best Practices | checked 2026-09-06 |
| `canonical-links.md` | [Set a canonical link](https://help.medium.com/hc/en-us/articles/360033930293-Set-a-canonical-link) | checked 2026-09-06 |
| `topics.md` | First-story guide + Distribution Guidelines | checked 2026-09-06 |

`sources.yaml` is the machine-readable inventory: every rule the adapter
enforces traces to a source id there, with URL, authority, and verification
dates. The adapter raises an error if a check cites an id that doesn't
exist — code can't silently drift from documented sources.

## Rule classification

Every check and reference is labeled:

- **POLICY** — from an official Medium page (requirement or explicit
  disqualifier).
- **RECOMMENDATION** — official-sourced advice (e.g., "ALT text is
  appreciated").
- **HEURISTIC** — Article Craft's editorial judgment (e.g., "35-word
  sentences usually need splitting"). Heuristics are never presented as
  Medium policy.

## What `check --platform medium` evaluates

| Category | Statuses it can produce | Rule class |
|---|---|---|
| Title | ERROR on clickbait patterns; WARNING on generic/formulaic | POLICY |
| Subtitle | WARNING when missing; ERROR on clickbait | POLICY/RECOMMENDATION |
| Structure | WARNING on sectionless long text, 30+ min reads | HEURISTIC/RECOMMENDATION |
| Formatting | WARNING on missing alt text, "click here" links, raw HTML | RECOMMENDATION/POLICY |
| AI Policy | ERROR on undisclosed generated text; WARNING on paywall implications, AI images without captions; NOT CHECKED when frontmatter is silent | POLICY |
| Canonical Link | WARNING reminder when cross-posting; NOT APPLICABLE otherwise | POLICY |
| Affiliate Disclosure | ERROR on likely affiliate links without FTC disclosure | POLICY |
| Topics & Mentions | WARNING on >5 topics, >3 mentions | POLICY/RECOMMENDATION |
| Distribution Risks | WARNING on clickbait, sales-pitch framing, link-farming, outrage-bait, Medium-meta topics | POLICY |

Plus: `review` folds these into the Platform Compatibility dimension (5
points of the Editorial Quality Score, deductions always explained).

## AI policy handling

The adapter distinguishes brainstorming/outlining/grammar (no disclosure
needed per the FAQ), AI-assisted text (disclosure required), and
AI-generated text (disclosure required; **cannot be paywalled** in the
Partner Program; undisclosed gets Network-only distribution). Frontmatter:

```yaml
ai_assistance: none | assistive | generated | unspecified
```

`unspecified` produces NOT CHECKED with the exact policy consequences
spelled out, so the author decides with full information. Article Craft
never provides advice for hiding AI usage or evading AI detection.

## The lines we don't cross

- No distribution prediction. Not "this will be Boosted", not a
  "boost-likelihood score", not reverse-engineered ranking rules. Every
  report carries the disclaimer.
- No publishing automation. No posting, scheduling, or engagement of any
  kind. Medium's Rules prohibit artificial interactions; Article Craft
  doesn't go near them.
- No scraping. Medium's Terms prohibit scraping; the tool reads articles
  *you* supply and official public policy pages.
- No unofficial APIs.

## When Medium changes a policy

1. Check the current Help Center page (URLs are in each reference file).
2. Update the reference file summary; quote the new language.
3. Update `sources.yaml` (`date_updated`, `last_verified`).
4. Adjust the adapter check if the rule changed; update tests.
5. Note the change in CHANGELOG.md.

CONTRIBUTING.md requires the official source URL, the date checked, and the
affected rule for any Medium policy PR.
