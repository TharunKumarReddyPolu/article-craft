"""Unit tests for the editorial engine."""

from __future__ import annotations

from article_craft.editorial.ai_patterns import find_ai_patterns
from article_craft.editorial.contribution import detect_human_contribution
from article_craft.editorial.outline import build_outline
from article_craft.editorial.review import review_article
from article_craft.editorial.titles import (
    analyze_title,
    generate_title_candidates,
)
from article_craft.editorial.types import (
    all_article_types,
    classify_article,
    get_article_type,
)
from article_craft.models.review import Severity, Verdict
from article_craft.parsing import parse_article_text

GOOD_ARTICLE = """---
title: Why our Kafka consumer fell seven hours behind
subtitle: What we learned bounding fan-out during a Black Friday incident
audience: backend engineers
article_type: case-study
---

# Why our Kafka consumer fell seven hours behind
**What we learned bounding fan-out during a Black Friday incident**

Last Black Friday our notification service fell seven hours behind. This is
what happened, and the fix that surprised us.

## The situation

We run a Kafka consumer that fans out to per-user notification channels. At
40x normal traffic, lag climbed from minutes to hours. I watched the error
rate tick up at minute three and assumed the brokers were the problem.

## What actually broke

The consumer was fine. Our fan-out wasn't bounded: one hot user generated
50,000 notifications in an hour. I benchmarked the fix on staging: p99 went
from 2.3s to 180ms with the same hardware.

## What we changed

We bounded fan-out per partition key. See
[Kafka's ordering docs](https://kafka.apache.org/documentation/#ordering) —
ordering only exists within a partition, which is what made bounding safe for
our use case. Here is the core of the change:

```python
# Bound notifications per user per poll cycle
for user, events in partition_batch:
    emit(events[:MAX_PER_USER])
```

## What I'd do differently

I should have added the lag alert at the design stage, not the incident
stage. If I built it again, I'd bound fan-out at the producer.
"""

BAD_ARTICLE = """# Some Thoughts on Kafka

In today's fast-paced world of software development, Kafka is a powerful
tool. It's important to note that Kafka is a distributed streaming platform.
Let's dive in!

Kafka is robust. It's seamless and cutting-edge. Most engineers agree that
it's the best. Studies show that 90% of developers leverage Kafka
successfully.

## Introduction

Kafka has many features. It is very very robust and amazing.

## History

Kafka was created at LinkedIn. It is widely used by everyone. It's
incredible.

## Conclusion

In conclusion, Kafka is amazing and you should use it. It will revolutionize
your architecture seamlessly.
"""


class TestTitleAnalysis:
    def test_clickbait_detected(self) -> None:
        analysis = analyze_title("7 SHOCKING Kubernetes hacks you won't believe")
        assert analysis.clickbait_risk == "high"
        assert analysis.issues

    def test_generic_detected(self) -> None:
        analysis = analyze_title("Some Thoughts on Kubernetes")
        assert analysis.clarity == "vague"

    def test_good_title_passes(self) -> None:
        analysis = analyze_title("Why our Kafka consumer fell seven hours behind")
        assert analysis.clickbait_risk == "low"
        assert analysis.clarity == "good"
        assert analysis.issues == []

    def test_missing_title(self) -> None:
        analysis = analyze_title(None)
        assert any(i["severity"] == Severity.MAJOR.value for i in analysis.issues)

    def test_candidates_generated(self) -> None:
        candidates = generate_title_candidates(
            topic="Kafka exactly-once semantics",
            angle="partition ordering pitfalls",
            audience="backend engineers",
            article_type="technical-explainer",
        )
        assert len(candidates) >= 5
        approaches = {c.approach for c in candidates}
        assert "descriptive" in approaches
        assert "problem-oriented" in approaches
        assert all(c.accuracy_note for c in candidates)


class TestAiPatterns:
    def test_detects_cliche(self) -> None:
        hits = find_ai_patterns("In today's fast-paced world of software, let's dive in!")
        names = {h.pattern_name for h in hits}
        assert "cliche-opener" in names
        assert "filler-transition" in names

    def test_ignores_normal_prose(self) -> None:
        assert find_ai_patterns("We bounded fan-out per partition key and measured p99.") == []

    def test_line_numbers(self) -> None:
        text = "line one\n\ndelve deeper into this\n"
        hits = find_ai_patterns(text)
        assert hits and hits[0].line == 3


class TestContribution:
    def test_detects_experience(self) -> None:
        article = parse_article_text(GOOD_ARTICLE)
        contribution = detect_human_contribution(article)
        assert contribution.present
        assert "personal experience" in contribution.kinds
        assert "experiment" in contribution.kinds

    def test_flags_absence(self) -> None:
        article = parse_article_text(BAD_ARTICLE)
        contribution = detect_human_contribution(article)
        assert not contribution.present
        assert contribution.suggestions  # always suggests concrete ways to add one


class TestReviewEngine:
    def test_good_article_scores_high(self) -> None:
        result = review_article(parse_article_text(GOOD_ARTICLE, "good.md"))
        assert result.score.total >= 85
        assert result.publish_recommendation.verdict is Verdict.READY
        assert not result.critical_issues
        assert result.human_contribution.present

    def test_bad_article_scores_low_with_critical(self) -> None:
        result = review_article(parse_article_text(BAD_ARTICLE, "bad.md"))
        assert result.score.total < 70
        assert result.publish_recommendation.verdict is Verdict.DO_NOT_PUBLISH_YET
        assert result.critical_issues  # extreme generic density
        assert any(i.severity is Severity.MAJOR for i in result.issues)

    def test_every_deduction_has_reasons(self) -> None:
        result = review_article(parse_article_text(GOOD_ARTICLE))
        for dim in result.score.dimensions:
            if dim.points_lost > 0:
                assert dim.reasons, f"{dim.dimension} lost points with no reason"

    def test_recommended_changes_deduped_and_labeled(self) -> None:
        result = review_article(parse_article_text(BAD_ARTICLE))
        changes = result.recommended_changes
        assert len(changes) == len(set(changes))
        assert all(c.startswith("[") for c in changes)

    def test_score_dimensions_sum_to_100(self) -> None:
        result = review_article(parse_article_text(GOOD_ARTICLE))
        assert sum(d.max for d in result.score.dimensions) == 100
        assert result.score.total == sum(d.score for d in result.score.dimensions)


class TestOutline:
    def test_outline_for_tutorial(self) -> None:
        outline = build_outline(
            idea="setting up PostgreSQL logical replication",
            audience="backend engineers",
            article_type="technical-tutorial",
            unique_angle="the failure cases the docs skip",
        )
        assert outline.article_type == "technical-tutorial"
        assert len(outline.sections) >= 4
        assert outline.total_target_words > 300
        assert outline.research_questions
        assert outline.author_contribution_prompts
        md = outline.to_markdown()
        assert "Editorial outline" in md
        assert "Reader promise" in md

    def test_outline_respects_target_length(self) -> None:
        outline = build_outline(
            idea="x",
            audience="engineers",
            article_type="opinion",
            target_length_words=1000,
        )
        assert 700 <= outline.total_target_words <= 1400


class TestTypes:
    def test_registry_complete(self) -> None:
        assert len(all_article_types()) == 10
        assert all(spec.purpose and spec.structure for spec in all_article_types())

    def test_get_unknown_returns_none(self) -> None:
        assert get_article_type("nonexistent-type") is None

    def test_classify_tutorial(self) -> None:
        text = """---
article_type: null
---

# How to deploy

First, install the CLI. Then, create a new config. Next, run the deploy
command. Finally, verify the pod is running.

## Steps

Run the following commands.
"""
        article = parse_article_text(text)
        assert classify_article(article) in ("technical-tutorial", None)

    def test_personality_types_expect_first_person(self) -> None:
        for type_id in ("personal-experience", "opinion", "case-study"):
            spec = get_article_type(type_id)
            assert spec is not None and spec.expects_first_person
