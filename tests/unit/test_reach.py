"""Unit tests for the reach-readiness layer.

The reach engine checks alignment with platforms' own published
discoverability criteria. These tests pin the honest contract: every check
cites a registered source_id, statuses are advisory, and the shared engine
carries no platform-specific wording that could be misattributed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from article_craft.editorial.reach import (
    first_hand_experience_signal,
    headline_parity_check,
    non_derivative_signal,
    reader_value_signal,
)
from article_craft.models.review import PlatformCheckStatus
from article_craft.parsing import parse_article_text
from article_craft.platforms.base import available_platforms, get_adapter

STRONG_ARTICLE = """---
title: How we cut Kafka consumer lag from 2.3s to 180ms
subtitle: The consumer-group rebalance mistake behind our p99 spike
topics:
  - apache-kafka
  - python
cover_image: https://example.com/dashboard.png
ai_assistance: none
---

# How we cut Kafka consumer lag from 2.3s to 180ms

Our consumer fell behind and here is exactly what we measured, what was
wrong, and the settings change that fixed it.

## What we saw

The dashboard showed lag climbing every morning. I ran the benchmark myself:
p99 fell from 2.3s to 180ms after the fix.

## The cause

When we deployed, the consumer group rebalanced and sessions timed out.
We had set `max.poll.interval.ms` too low for our batch size.

## The fix

```python
consumer = KafkaConsumer(
    "events",
    max_poll_interval_ms=600000,
)
```

After this change, the rebalance storm stopped and lag stayed flat for
three weeks in production.
"""

WEAK_ARTICLE = """---
title: Some Thoughts About Things
ai_assistance: none
---

# Some Thoughts About Things

## Overview

Software is important. In today's fast-paced world, developers need to
leverage synergies. It depends. Maybe this works for you, perhaps not.

## More

 delving into the landscape of modern solutions, it is crucial to
understand the pivotal role of robust frameworks in unlocking seamless
experiences.


## Conclusion

In conclusion, these insights can hopefully empower your journey.
"""


MISMATCHED_ARTICLE = """---
title: Zero-downtime Postgres migrations at scale
subtitle: A field report from 40-shard cutover
ai_assistance: none
---

# Zero-downtime Postgres migrations at scale

## Overview

Sourdough starters reward patience. The hydration ratio shapes the crumb,
and the fridge retard overnight deepens the flavor considerably.

## Method

Fold the dough four times at half-hour intervals, then shape and proof.
"""


def _known_sources(platform: str) -> frozenset[str]:
    """The registered source ids for a platform's sources.yaml."""
    import yaml

    path = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "article-craft"
        / "references"
        / "platforms"
        / platform
        / "sources.yaml"
    )
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return frozenset(entry["id"] for entry in data["sources"])


class TestReachSignals:
    def test_strong_article_passes_authorship(self) -> None:
        article = parse_article_text(STRONG_ARTICLE)
        check = first_hand_experience_signal(article, "medium-distribution-guidelines")
        assert check.status is PlatformCheckStatus.PASS
        assert check.findings == []

    def test_weak_article_warns_on_authorship(self) -> None:
        article = parse_article_text(WEAK_ARTICLE)
        check = first_hand_experience_signal(article, "medium-distribution-guidelines")
        assert check.status in (PlatformCheckStatus.WARNING, PlatformCheckStatus.NOT_CHECKED)
        assert check.findings

    def test_reader_value_flags_no_deliverables(self) -> None:
        article = parse_article_text(WEAK_ARTICLE)
        check = reader_value_signal(article, "medium-distribution-guidelines")
        assert check.status is PlatformCheckStatus.WARNING

    def test_headline_parity_flags_mismatch(self) -> None:
        article = parse_article_text(MISMATCHED_ARTICLE)
        check = headline_parity_check(article, "medium-distribution-guidelines")
        assert check.status is PlatformCheckStatus.WARNING
        assert check.findings

    def test_headline_parity_passes_on_alignment(self) -> None:
        article = parse_article_text(STRONG_ARTICLE)
        check = headline_parity_check(article, "medium-distribution-guidelines")
        assert check.status is PlatformCheckStatus.PASS

    def test_non_derivative_passes_with_artifact(self) -> None:
        article = parse_article_text(STRONG_ARTICLE)
        check = non_derivative_signal(article, "medium-distribution-guidelines")
        assert check.status is PlatformCheckStatus.PASS

    def test_every_check_cites_source_id(self) -> None:
        article = parse_article_text(STRONG_ARTICLE)
        for fn in (
            first_hand_experience_signal,
            reader_value_signal,
            headline_parity_check,
            non_derivative_signal,
        ):
            check = fn(article, "some-source")
            assert check.source_id == "some-source"
            assert check.rule_class.value == "HEURISTIC"

    def test_engine_has_no_platform_specific_wording(self) -> None:
        """The shared engine must not hardcode one platform's program names."""
        import article_craft.editorial.reach as reach_mod

        src = Path(reach_mod.__file__).read_text(encoding="utf-8")
        assert "Boost" not in src


class TestAdapterReachWiring:
    @pytest.mark.parametrize(
        ("platform", "expected_source_id"),
        [
            ("medium", "medium-distribution-guidelines"),
            ("devto", "dev-editor-guide"),
            ("hashnode", "hashnode-tags"),
            ("substack", "substack-content-guidelines"),
            ("linkedin", "linkedin-article-tips"),
        ],
    )
    def test_all_platforms_emit_reach_checks(self, platform: str, expected_source_id: str) -> None:
        adapter_cls = get_adapter(platform)
        assert adapter_cls is not None, platform
        article = parse_article_text(STRONG_ARTICLE)
        checks = adapter_cls().review_reach(article)
        assert checks, f"{platform} emitted no reach checks"
        known = _known_sources(platform)
        for check in checks:
            assert check.source_id in known, (
                f"{platform} reach check cites unregistered source {check.source_id}"
            )
            assert check.category.startswith("Reach")
        assert any(c.source_id == expected_source_id for c in checks)

    def test_reach_checks_flow_into_full_report(self) -> None:
        adapter_cls = get_adapter("medium")
        assert adapter_cls is not None
        article = parse_article_text(STRONG_ARTICLE)
        report = adapter_cls().full_report(article)
        reach = [c for c in report.checks if c.category.startswith("Reach")]
        assert len(reach) >= 5  # 4 signals + topics check

    def test_reach_checks_are_advisory(self) -> None:
        """Reach checks never produce ERRORs — they are readiness signals."""
        article = parse_article_text(WEAK_ARTICLE)
        for platform in available_platforms():
            adapter_cls = get_adapter(platform)
            assert adapter_cls is not None
            for check in adapter_cls().review_reach(article):
                assert check.status is not PlatformCheckStatus.ERROR, (
                    f"{platform}/{check.category} reached ERROR severity"
                )
