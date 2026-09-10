"""The 30-second demo: proof the whole pipeline works, zero setup.

Every ``article-craft demo`` run executes the real engines on a small
embedded article and prints the live output. No network, no workspace, no
configuration required — if any step fails, something is genuinely wrong
with the installation, and the error is the honest result.
"""

from __future__ import annotations

from article_craft.models.article import Article
from article_craft.models.review import PlatformCheckReport

DEMO_ARTICLE_TEXT = """\
---
title: Why our API rate limiter used 40% more memory than expected
subtitle: A token-bucket surprise, traced and fixed
audience: backend engineers
article_type: case-study
platform: medium
ai_assistance: assistive
ai_assistance_note: "Outline and copy-edit assistance; all measurements and code are the author's."
---

# Why our API rate limiter used 40% more memory than expected
**A token-bucket surprise, traced and fixed**

We shipped a token-bucket rate limiter and its memory use was 40% above
our estimate. This is how we traced the discrepancy to one data-structure
choice, and what we changed.

> Disclosure: this article was drafted with AI assistance for outlining and
> copy-editing. Every measurement, decision, and code sample is mine.

## The situation

Our gateway limits each API key to 100 requests per second. The design
stored one bucket per key in a dict, and at 200,000 active keys the
container hovered around 180 MB — our estimate said 128 MB.

## What the estimate missed

The estimate assumed one small object per bucket. In reality each bucket
held a deque plus a lock, and per-object overhead in CPython dominated:
measured with ``tracemalloc``, allocator overhead was 61% of the total.

## The fix

We switched idle buckets to a compact struct packed into a flat array and
kept a small dict only for keys with recent traffic. Memory dropped to
104 MB — 42% below the naive design — with no measurable latency change.

## Takeaways

- Estimate allocator overhead, not just payload size.
- Measure with the profiler before optimizing by intuition.
- Compact representations for idle state beat clever eviction here.
"""


def demo_article() -> Article:
    """Parse the embedded demo article with the real parser."""
    import tempfile
    from pathlib import Path

    from article_craft.parsing import parse_article_file

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "demo-article.md"
        path.write_text(DEMO_ARTICLE_TEXT, encoding="utf-8")
        return parse_article_file(path)


def run_demo(platform: str = "medium") -> list[tuple[str, str]]:
    """Run the full pipeline on the demo article.

    Returns a list of ``(title, output)`` steps. Raises on any engine
    failure — a broken install should fail loudly here, not quietly.
    """
    from article_craft.platforms.base import get_adapter
    from article_craft.reports import images_platform_check, render_review
    from article_craft.research.claims import factcheck_report_markdown

    article = demo_article()

    review_output = render_review(article, platform=None)

    factcheck = factcheck_report_markdown(article)
    adapter_cls = get_adapter(platform)
    assert adapter_cls is not None  # registry guarantees known platforms
    check = adapter_cls().full_report(article, extra_checks=[images_platform_check(article)])

    return [
        ("1. Editorial review (real output, trimmed)", _trim(review_output, 22)),
        ("2. Fact-check scaffold (claim extraction)", _trim(factcheck, 16)),
        (f"3. {platform} pre-publish check", _trim(_check_as_markdown(check), 14)),
    ]


def _check_as_markdown(check: PlatformCheckReport) -> str:
    """Compact ASCII rendering of a platform check report (demo-safe)."""
    icon_for = {"pass": "[ok]", "warning": "[warn]", "error": "[fail]", "not_checked": "[n/a]"}
    lines = [f"# {check.platform.title()} check — overall: {check.overall.value.upper()}"]
    for item in check.checks:
        icon = icon_for.get(item.status.value, "•")
        lines.append(f"- {icon} **{item.category}** — {item.status.value}: {item.detail}")
    lines.append(
        f"\nVerdict: {icon_for.get(check.overall.value, '•')} {check.overall.value.upper()}"
    )
    return "\n".join(lines)


def _trim(text: str, max_lines: int) -> str:
    """Keep the head of a report and mark any trimmed tail honestly."""
    lines = text.rstrip().splitlines()
    if len(lines) <= max_lines:
        return text.rstrip()
    kept = lines[:max_lines]
    omitted = len(lines) - max_lines
    kept.append(f"… ({omitted} more lines in the full output)")
    return "\n".join(kept)
