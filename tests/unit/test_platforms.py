"""Unit tests for the platform abstraction and the Medium adapter."""

from __future__ import annotations

import pytest

from article_craft.models.review import PlatformCheckStatus, RuleClass
from article_craft.parsing import parse_article_text
from article_craft.platforms.base import available_platforms, get_adapter
from article_craft.platforms.future import (
    DevToAdapter,
    LinkedInAdapter,
    SubstackAdapter,
)
from article_craft.platforms.medium import MediumAdapter, medium_pre_publish_check

CLEAN = """---
title: Why our Kafka consumer fell seven hours behind
subtitle: What we learned bounding fan-out during an incident
audience: backend engineers
article_type: case-study
ai_assistance: none
---

# Why our Kafka consumer fell seven hours behind
**What we learned bounding fan-out during an incident**

Last Black Friday our notification service fell seven hours behind. This is
what happened.

## The situation

We run a Kafka consumer that fans out per user. At 40x normal traffic, lag
climbed from minutes to hours. I watched the error rate tick up at minute
three and assumed the brokers were the problem.

## What actually broke

The consumer was fine. Our fan-out wasn't bounded: one hot user generated
50,000 notifications. I benchmarked the fix on staging: p99 went from 2.3s
to 180ms.

## What we changed

We bounded fan-out per partition key. See
[Kafka's ordering docs](https://kafka.apache.org/documentation/#ordering) —
ordering only exists within a partition, which made bounding safe.

## What I'd do differently

I should have added the lag alert at the design stage, not the incident
stage. If I built it again, I'd bound fan-out at the producer.
"""

PROBLEMATIC = """---
title: 7 SHOCKING Kafka hacks you won't believe
ai_assistance: generated
topics: [a, b, c, d, e, f]
canonical_url: "https://myblog.dev/kafka"
originally_published: true
---

# 7 SHOCKING Kafka hacks you won't believe

This story was written with the assistance of an AI writing program.

## Hacks

Buy my course now! Check [this deal](https://amzn.to/xyz?tag=me-20).

![midjourney render](https://cdn.midjourney.com/x.png)

## More

Ping @alice @bob @carol @dave @eve.
"""


class TestRegistry:
    def test_medium_registered(self) -> None:
        assert "medium" in available_platforms()
        assert get_adapter("medium") is MediumAdapter

    def test_future_platforms_not_registered(self) -> None:
        # Stubs must NOT be registered as if functional.
        assert "devto" not in available_platforms()
        assert "linkedin" not in available_platforms()
        assert "substack" not in available_platforms()

    @pytest.mark.parametrize("stub_cls", [DevToAdapter, LinkedInAdapter, SubstackAdapter])
    def test_stubs_raise_actionable(self, stub_cls: type) -> None:
        article = parse_article_text(CLEAN)
        with pytest.raises(NotImplementedError, match="not implemented in Article Craft"):
            stub_cls().review_title(article)


class TestMediumAdapterClean:
    def test_clean_article_passes(self) -> None:
        report = medium_pre_publish_check(parse_article_text(CLEAN))
        assert report.overall is PlatformCheckStatus.PASS
        categories = {c.category for c in report.checks}
        assert {
            "Title",
            "Subtitle",
            "Structure",
            "Formatting",
            "AI Policy",
            "Canonical Link",
            "Distribution Risks",
        } <= categories
        assert report.fix_items == []

    def test_platform_score_full(self) -> None:
        score = MediumAdapter().platform_compatibility_score(parse_article_text(CLEAN))
        assert score.score == 5

    def test_every_check_cites_known_source(self) -> None:
        # full_report raises if a check cites an unknown source_id
        report = medium_pre_publish_check(parse_article_text(CLEAN))
        assert all(c.source_id for c in report.checks if c.rule_class is RuleClass.POLICY)

    def test_disclaimer_present(self) -> None:
        report = medium_pre_publish_check(parse_article_text(CLEAN))
        assert "do not guarantee" in report.disclaimer


class TestMediumAdapterProblematic:
    @pytest.fixture
    def report(self) -> object:
        return medium_pre_publish_check(parse_article_text(PROBLEMATIC))

    def test_overall_error(self, report: object) -> None:
        assert report.overall is PlatformCheckStatus.ERROR  # type: ignore[attr-defined]

    def test_clickbait_title_is_error(self, report: object) -> None:
        title = next(c for c in report.checks if c.category == "Title")  # type: ignore[attr-defined]
        assert title.status is PlatformCheckStatus.ERROR  # type: ignore[attr-defined]
        assert title.rule_class is RuleClass.POLICY  # type: ignore[attr-defined]

    def test_generated_ai_policy(self, report: object) -> None:
        ai = [c for c in report.checks if c.category == "AI Policy"]  # type: ignore[attr-defined]
        # Disclosed generated: warning about paywall; and caption warning
        assert any(c.status is PlatformCheckStatus.WARNING for c in ai)  # type: ignore[attr-defined]
        assert any("paywall" in c.detail for c in ai)  # type: ignore[attr-defined]

    def test_affiliate_undisclosed_is_error(self, report: object) -> None:
        aff = next(c for c in report.checks if c.category == "Affiliate Disclosure")  # type: ignore[attr-defined]
        assert aff.status is PlatformCheckStatus.ERROR  # type: ignore[attr-defined]

    def test_canonical_reminder(self, report: object) -> None:
        canon = next(c for c in report.checks if c.category == "Canonical Link")  # type: ignore[attr-defined]
        assert canon.status is PlatformCheckStatus.WARNING  # type: ignore[attr-defined]
        assert "Only the author can set" in canon.detail  # type: ignore[attr-defined]

    def test_mentions_warning(self, report: object) -> None:
        topics = [c for c in report.checks if c.category == "Topics & Mentions"]  # type: ignore[attr-defined]
        assert any(c.status is PlatformCheckStatus.WARNING for c in topics)  # type: ignore[attr-defined]

    def test_fix_list_populated(self, report: object) -> None:
        assert len(report.fix_items) >= 5  # type: ignore[attr-defined]

    def test_platform_score_deducted(self, report: object) -> None:
        score = MediumAdapter().platform_compatibility_score(parse_article_text(PROBLEMATIC))
        assert score.score < 5
        assert score.reasons  # deductions explained


class TestAiAssistanceStates:
    def _check_for(self, markdown: str, category: str = "AI Policy"):
        report = medium_pre_publish_check(parse_article_text(markdown))
        return next(c for c in report.checks if c.category == category)

    def test_generated_without_disclosure_is_error(self) -> None:
        md = CLEAN.replace("ai_assistance: none", "ai_assistance: generated")
        check = self._check_for(md)
        assert check.status is PlatformCheckStatus.ERROR
        assert "disclosure" in check.detail.lower()

    def test_unspecified_is_not_checked(self) -> None:
        md = CLEAN.replace("ai_assistance: none", "ai_assistance: unspecified")
        check = self._check_for(md)
        assert check.status is PlatformCheckStatus.NOT_CHECKED

    def test_none_passes(self) -> None:
        check = self._check_for(CLEAN)
        assert check.status is PlatformCheckStatus.PASS
