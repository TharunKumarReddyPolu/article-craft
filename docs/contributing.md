# Contributing

Thanks for improving Article Craft. The project's value is trust — every
contribution either earns it or spends it.

## Ground rules

1. **No fabrication, ever.** No invented sources, statistics, quotes, URLs,
   benchmarks, or test fixtures that pretend real events happened.
2. **Classify your knowledge.** Anything that sounds like a platform rule
   must be labeled OFFICIAL_REQUIREMENT / OFFICIAL_RECOMMENDATION /
   INDUSTRY_BEST_PRACTICE / COMMUNITY_CONVENTION / EXPERIMENTAL — with the
   official source for the first two.
3. **No distribution claims.** No code, docs, or tests may predict Boost,
   reach, or ranking.
4. **Keep the deterministic/LLM split.** The CLI computes evidence; the
   skill defines judgment. Don't smuggle an LLM call into the library.
5. **Small, composable models.** If your feature needs a new abstraction,
   try to express it with the existing ones first.

## Development setup

```bash
git clone <repo> && cd article-craft
uv sync --extra dev
make check        # lint + typecheck + tests + skill validation
```

## Adding an article type

1. Add an `ArticleTypeSpec` to `src/article_craft/editorial/types.py`
   (purpose, structure, questions, checklist, failure modes).
2. Add a template in `skills/article-craft/templates/`.
3. Update the table in `skills/article-craft/references/editorial/article-types.md`.
4. Add a fixture + test asserting the type's expectations.

## Adding a platform adapter

1. Research the platform's **official** documentation first. Record sources
   in a `sources.yaml` for that platform (same schema as Medium's).
2. Implement the `PlatformAdapter` protocol in
   `src/article_craft/platforms/<platform>/adapter.py`. Use NOT CHECKED /
   NOT APPLICABLE honestly rather than guessing.
3. Tag every check POLICY / RECOMMENDATION / HEURISTIC; cite `source_id`s.
4. Register with `@register_adapter`; add CLI plumbing only if the platform
   has real checks.
5. Remove the stub from `platforms/future.py`; update README, roadmap, and
   the skill's hard-boundaries line.
6. Tests: one clean fixture, one violating fixture, per category.

## Medium policy updates

Medium's policies change; keeping them current is maintenance, not optional.
A policy PR must include:

- **Official source URL** (help.medium.com or official blog)
- **Date checked** (and the page's own last-updated date if shown)
- **Affected rule(s)** — which reference file(s) and adapter check(s)
- **Description of the change** — what the policy said, what it now says
- **Test updates** where the check behavior changed

Update the reference file (quote the new language), bump `last_verified` in
`sources.yaml`, adjust the adapter, update tests, note it in CHANGELOG.md.

## Adding editorial workflows / references

Workflows live in `skills/article-craft/workflows/`; craft references in
`references/editorial/`. A good workflow file: step-by-step method, what to
preserve, what never to do, and which references to load. Keep SKILL.md
under 500 lines — new detail goes in referenced files, not the main file.

## Tests

- Every engine change needs tests; fixtures are stereotyped on purpose
  (see `tests/fixtures/articles/README.md`).
- No test may require an LLM, network, or API keys.
- Run `make check` before submitting.

## PR checklist

- [ ] `make check` passes locally
- [ ] No new dependencies without discussion
- [ ] Knowledge claims classified; official sources linked where claimed
- [ ] Docs updated (README table, relevant docs/ page)
- [ ] CHANGELOG.md entry under Unreleased
