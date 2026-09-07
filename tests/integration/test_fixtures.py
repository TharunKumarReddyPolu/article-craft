"""Integration tests over the fixture articles.

These lock in the *directional* behavior of the engines: good fixtures score
well, bad fixtures get caught. Deliberately stereotyped fixtures keep
assertions stable as heuristics evolve.
"""

from __future__ import annotations

from pathlib import Path

from article_craft.editorial.review import review_article
from article_craft.models.review import PlatformCheckStatus, Verdict
from article_craft.originality.guard import assess_originality
from article_craft.parsing import parse_article_file
from article_craft.platforms.medium import medium_pre_publish_check
from article_craft.research.claims import extract_claims

FIXTURES = Path(__file__).parent.parent / "fixtures" / "articles"


def load(name: str):
    return parse_article_file(FIXTURES / f"{name}.md")


class TestExcellentTechnical:
    def test_scores_high_and_ready(self) -> None:
        result = review_article(load("excellent_technical"))
        assert result.score.total >= 80
        assert result.publish_recommendation.verdict is Verdict.READY
        assert not result.critical_issues

    def test_contribution_detected(self) -> None:
        result = review_article(load("excellent_technical"))
        assert result.human_contribution.present
        assert "experiment" in result.human_contribution.kinds

    def test_medium_check_passes(self) -> None:
        report = medium_pre_publish_check(load("excellent_technical"))
        assert report.overall is PlatformCheckStatus.PASS


class TestGenericAi:
    def test_caught_by_review(self) -> None:
        result = review_article(load("generic_ai"))
        assert result.score.total < 70
        assert result.publish_recommendation.verdict is Verdict.DO_NOT_PUBLISH_YET

    def test_ai_patterns_flagged(self) -> None:
        result = review_article(load("generic_ai"))
        assert any("Generic AI-sounding phrasing" in i.title for i in result.issues)

    def test_ai_policy_warning(self) -> None:
        report = medium_pre_publish_check(load("generic_ai"))
        ai = [c for c in report.checks if c.category == "AI Policy"]
        assert ai
        assert all(c.status is not PlatformCheckStatus.PASS for c in ai)


class TestPoorStructure:
    def test_low_structure_score(self) -> None:
        result = review_article(load("poor_structure"))
        structure = result.score.dimension(
            __import__("article_craft.models.review", fromlist=["Dimension"]).Dimension.STRUCTURE
        )
        assert structure.score < 8

    def test_no_contribution(self) -> None:
        result = review_article(load("poor_structure"))
        assert not result.human_contribution.present


class TestFactualErrors:
    def test_critical_findings(self) -> None:
        result = review_article(load("factual_errors"))
        assert result.critical_issues
        assert result.publish_recommendation.verdict is Verdict.DO_NOT_PUBLISH_YET

    def test_undisclosed_ai_flagged(self) -> None:
        report = medium_pre_publish_check(load("factual_errors"))
        ai = [c for c in report.checks if c.category == "AI Policy"]
        assert any(c.status in (PlatformCheckStatus.WARNING, PlatformCheckStatus.ERROR) for c in ai)


class TestUnsupportedClaims:
    def test_evidence_deducted(self) -> None:
        result = review_article(load("unsupported_claims"))
        evidence = result.score.dimension(
            __import__("article_craft.models.review", fromlist=["Dimension"]).Dimension.EVIDENCE
        )
        assert evidence.points_lost >= 4

    def test_claims_extracted(self) -> None:
        claims = extract_claims(load("unsupported_claims"))
        assert len(claims) >= 5
        assert any("94%" in c.text for c in claims)


class TestClickbait:
    def test_title_error(self) -> None:
        report = medium_pre_publish_check(load("clickbait"))
        title = next(c for c in report.checks if c.category == "Title")
        assert title.status is PlatformCheckStatus.ERROR

    def test_review_fails_title(self) -> None:
        result = review_article(load("clickbait"))
        assert result.score.total < 85


class TestSeoSpam:
    def test_affiliate_error(self) -> None:
        report = medium_pre_publish_check(load("seo_spam"))
        aff = next(c for c in report.checks if c.category == "Affiliate Disclosure")
        assert aff.status is PlatformCheckStatus.ERROR

    def test_ai_generated_flagged(self) -> None:
        report = medium_pre_publish_check(load("seo_spam"))
        ai = [c for c in report.checks if c.category == "AI Policy"]
        assert ai
        assert any(c.status is not PlatformCheckStatus.PASS for c in ai)

    def test_low_reader_value(self) -> None:
        result = review_article(load("seo_spam"))
        rv = result.score.dimension(
            __import__("article_craft.models.review", fromlist=["Dimension"]).Dimension.READER_VALUE
        )
        assert rv.points_lost >= 2


class TestStrongPersonal:
    def test_voice_scored_well(self) -> None:
        result = review_article(load("strong_personal"))
        voice = result.score.dimension(
            __import__("article_craft.models.review", fromlist=["Dimension"]).Dimension.VOICE
        )
        assert voice.score >= 8

    def test_medium_check_clean(self) -> None:
        report = medium_pre_publish_check(load("strong_personal"))
        assert report.overall is PlatformCheckStatus.PASS


class TestStrongSystemDesign:
    def test_recognized_and_scored(self) -> None:
        result = review_article(load("strong_system_design"))
        assert result.article_type == "system-design"
        assert result.score.total >= 70

    def test_assumptions_present(self) -> None:
        article = load("strong_system_design")
        text = "\n".join(s.body for s in article.sections).lower()
        assert "assumption" in text  # the fixture labels its assumptions


class TestOriginalityRisk:
    SOURCE = """# Understanding Kafka's ordering guarantees
**A complete guide to partition ordering**

Kafka is a distributed streaming platform. Kafka guarantees ordering
within a partition. Kafka does not guarantee ordering across partitions.
This article explains Kafka ordering.

## What is Kafka

Kafka is a distributed streaming platform that is used by thousands of
companies. Kafka stores records in topics. Topics are divided into
partitions. Each partition is an ordered, immutable sequence of records.

## Ordering within a partition

Kafka guarantees ordering within a partition. Records with the same key
go to the same partition. This means ordering is preserved for records
with the same key. Producers can configure the partitioner to control
which partition receives each record.

## Ordering across partitions

Kafka does not guarantee ordering across partitions. If you need
ordering across partitions, you must design your application differently.
This is a common source of confusion for developers new to Kafka.

## Consumer ordering

Consumers read partitions in order. A consumer group assigns partitions
to consumers. Each partition is consumed by exactly one consumer in the
group. This preserves ordering within the partition during consumption.

## Conclusion

Kafka ordering is guaranteed within partitions but not across partitions.
Understanding this distinction is essential for building correct
applications with Kafka. Design your applications with this constraint
in mind.
"""

    def test_derivative_detected(self) -> None:
        report = assess_originality(load("originality_risk"), self.SOURCE, "source article")
        assert report.verdict != "INDEPENDENT"
        assert report.has_high_risks or report.findings

    def test_independent_article_passes(self) -> None:
        report = assess_originality(load("excellent_technical"), self.SOURCE, "source article")
        assert report.verdict == "INDEPENDENT"
        assert not report.has_high_risks

    def test_findings_carry_suggestions(self) -> None:
        report = assess_originality(load("originality_risk"), self.SOURCE)
        for finding in report.findings:
            assert finding.suggestion
