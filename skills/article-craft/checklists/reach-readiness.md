# Reach-Readiness Checklist

Alignment with each platform's **own published** discoverability criteria.
Reference per platform: [../references/platforms/](../references/platforms/)
(see each platform's `reach.md` and `sources.yaml`).

This checklist improves the *inputs you control*. It does not guarantee Boost,
distribution, ranking, or virality — that is the platform's decision, and no
tool can promise it.

## All platforms

- [ ] Title accurately represents the story (curated platforms disqualify
      over-selling and generic headlines)
- [ ] Subtitle/preheader present and delivers the angle
- [ ] Tags/topics selected from the platform's own system, matching what the
      article is actually about
- [ ] Cover/social image present, correctly sized, with alt text
- [ ] The author's first-hand contribution is unmistakable (what did *you*
      build, measure, learn, or decide?)
- [ ] At least one first-hand artifact: code, data, screenshots, tables
- [ ] Generic-AI phrasing is low (the reach engine flags density >= 3/1000)
- [ ] Concrete deliverables present: steps, runnable code, examples, numbers
      you actually observed
- [ ] No hedging mush: each section lands a point

## Platform-specific mechanics (from official docs)

- [ ] **Medium** — up to 5 topics set; title/subtitle/cover represent the
      story; content is non-derivative (Boost hallmarks)
- [ ] **DEV.to** — up to 4 tags; cover_image 1000x420; `series:` if
      serialized
- [ ] **Hashnode** — tags from Hashnode's tag list; search description or
      subtitle set for search snippets; descriptive slug
- [ ] **Substack** — title works as the email subject line; consider the
      official title test (200+ subscribers); tags set; alt text everywhere
- [ ] **LinkedIn** — about your area of experience/expertise; focused on one
      topic; more than three paragraphs; media present

## Floor checks (reach assumes these pass)

- [ ] `article-craft check --platform <platform>`: no ERRORs outstanding
- [ ] AI assistance disclosed where the platform requires it
- [ ] Every claim sourced or labeled; nothing fabricated
- [ ] You can stand behind every sentence as your own work
