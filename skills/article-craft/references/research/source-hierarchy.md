# Source Hierarchy (reference)

> Article Craft working standard (INDUSTRY_BEST_PRACTICE). Not a Medium rule.

When you research for an article, weigh sources by authority. Prefer the
highest available tier for each factual claim, and record which tier each
claim rests on.

| Tier | Kind of source | Use for |
|---|---|---|
| 1 | Official documentation (e.g., Medium Help Center, language/framework docs, standards bodies, RFCs), primary research, academic papers, official specs | Facts, policy claims, technical behavior |
| 2 | Engineering blogs of the relevant organizations, reputable technical publications, professional editorial bodies | Practice, context, trade-offs |
| 3 | Established individual writers, well-regarded community resources | Perspective, craft technique, opinion grounding |
| 4 | Forums, Reddit, Stack Overflow, GitHub issues | Pointers to real problems; verify claims elsewhere |
| 5 | Random blogs, SEO farms, AI-generated summary sites | Avoid as claim support; use only as a last pointer to a Tier 1–3 source |

## Rules

1. **Never represent a lower tier as a higher one.** If Medium's Help Center
   says X, cite Medium. If a popular blog says X, say "practitioners
   commonly recommend X" — don't call it official.
2. **When official sources conflict, prefer the newer official source**, and
   note the conflict in the research artifact.
3. **Date every source.** Technical claims rot: a 2019 post about Kubernetes
   defaults may describe behavior that changed.
4. **Prefer primary over commentary.** A changelog entry beats a blog post
   about the changelog.
5. **One claim, one source minimum** — and for load-bearing claims
   (numbers, benchmarks, safety, security), two independent sources.
6. Record metadata for each source: title, URL, author, publisher, date
   published/updated, date accessed, tier.

See `citations.md` for how to present sources in the article itself and
`fact-checking.md` for how claims are classified.
