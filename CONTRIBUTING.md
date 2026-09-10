# Contributing to Article Craft

Thank you for helping build an editorial tool people can trust.

Before anything else, read [docs/contributing.md](docs/contributing.md) — it
has the full details on adding article types, platform adapters, workflows,
and Medium policy updates.

## The short version

```bash
git clone <repo> && cd article-craft
uv sync --extra dev
make check   # lint + typecheck + tests + skill validation
```

Please open an issue before large changes — use the **platform policy update**
template when a platform's published rules changed (it asks for exactly what
the project requires: source URL, verification date, and the rule diff), or
start a Discussion for feature ideas.

PRs should:

- Pass `make check` (ruff, mypy, pytest, skill validation).
- Classify knowledge claims (official vs. best-practice vs. heuristic) and
  link official sources for anything policy-shaped.
- Include tests; fixtures stay deterministic (no LLM, no network).
- Update docs and CHANGELOG.md.

## Special requirement for Medium policy changes

Every Medium policy PR must include: the **official source URL**, the
**date checked**, the **affected rule(s)**, a **description of the change**,
and **test updates** where relevant. This is how the project keeps its
policy references honest as Medium evolves.

## What we don't accept

Features that conflict with the project's philosophy (see README): AI
detection evasion, plagiarism laundering, engagement automation, mass
generation, distribution prediction, or anything that treats the reader as
a target rather than a guest.

## Reporting issues

Include: the command run, the article/fixture involved (redact private
content), the full output, and what you expected. For security-sensitive
reports (prompt injection via content, secrets exposure), see
[SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions are licensed under
Apache-2.0 (see [LICENSE](LICENSE)).
