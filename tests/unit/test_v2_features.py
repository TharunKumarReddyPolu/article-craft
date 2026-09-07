"""Unit tests for V2 features: image checks, contradiction tracking,
adaptation, export prep, and the four new platform adapters."""

from __future__ import annotations

from pathlib import Path

import pytest

from article_craft.editorial.adaptation import adapt_for_social
from article_craft.editorial.images import check_all
from article_craft.exporter import export_for_platform, supported_export_platforms
from article_craft.models.research import Claim, ClaimConflict, ResearchDoc, Source, SourceTier
from article_craft.parsing import parse_article_text
from article_craft.platforms.devto import DevToAdapter
from article_craft.platforms.hashnode import HashnodeAdapter
from article_craft.platforms.linkedin import LinkedInAdapter
from article_craft.platforms.substack import SubstackAdapter
from article_craft.research.contradictions import detect_conflicts, render_conflicts

WITH_IMAGES = """---
title: Testing Kafka consumer lag
ai_assistance: none
---

# Testing Kafka consumer lag

Our consumer fell behind and here is what we measured.

## Setup

![image.png](https://example.com/dashboard.png)

The dashboard showed lag climbing. I ran the benchmark myself: p99 fell
from 2.3s to 180ms.

```python
consumer.poll(timeout=1.0)
```
"""

TAGGED_CODE = """---
title: A simple guide
---

# A simple guide

Some text.

## Steps

```python
print("hello")
```
"""


class TestImageChecks:
    def test_filename_alt_flagged(self) -> None:
        article = parse_article_text(WITH_IMAGES)
        findings = check_all(article)
        codes = {f.code for f in findings}
        assert "filename-alt" in codes

    def test_no_code_screenshot_warning_when_code_blocks_exist(self) -> None:
        article = parse_article_text(WITH_IMAGES)
        findings = check_all(article)
        assert "prefer-code" not in {f.code for f in findings}

    def test_screenshot_without_code_flagged(self) -> None:
        md = WITH_IMAGES.replace("```python\nconsumer.poll(timeout=1.0)\n```", "").replace(
            "![image.png]", "![Screenshot of the metrics dashboard]"
        )
        article = parse_article_text(md)
        findings = check_all(article)
        assert "prefer-code" in {f.code for f in findings}

    def test_untagged_code_not_an_image_issue(self) -> None:
        article = parse_article_text(TAGGED_CODE)
        assert check_all(article) == []

    def test_missing_alt_flagged(self) -> None:
        md = WITH_IMAGES.replace("![image.png]", "![]")
        findings = check_all(parse_article_text(md))
        assert "missing-alt" in {f.code for f in findings}


def _doc(tier_a: SourceTier, tier_b: SourceTier) -> ResearchDoc:
    return ResearchDoc(
        sources=[Source(title="A", tier=tier_a), Source(title="B", tier=tier_b)],
        claims=[
            Claim(text="Kafka supports exactly-once semantics since version 0.11", source_index=0),
            Claim(text="Kafka supports exactly-once semantics since version 0.9", source_index=1),
        ],
    )


class TestContradictions:
    def test_higher_tier_wins(self) -> None:
        conflicts = detect_conflicts(_doc(SourceTier.OFFICIAL, SourceTier.LOW))
        assert len(conflicts) == 1
        assert conflicts[0].resolution == "a"

    def test_tie_stays_unresolved(self) -> None:
        conflicts = detect_conflicts(_doc(SourceTier.OFFICIAL, SourceTier.OFFICIAL))
        assert len(conflicts) == 1
        assert conflicts[0].resolution is None
        assert "cannot decide" in (conflicts[0].resolution_reason or "")

    def test_render_mentions_sources(self) -> None:
        doc = _doc(SourceTier.OFFICIAL, SourceTier.LOW)
        doc.conflicts = detect_conflicts(doc)
        rendered = render_conflicts(doc)
        assert rendered and "prefer A" in rendered[0]

    def test_no_shared_entity_no_conflict(self) -> None:
        doc = ResearchDoc(
            sources=[Source(title="A"), Source(title="B")],
            claims=[
                Claim(text="Python 3.12 shipped in October", source_index=0),
                Claim(text="Rust compiles fast in release mode", source_index=1),
            ],
        )
        assert detect_conflicts(doc) == []

    def test_claim_conflict_model_defaults(self) -> None:
        conflict = ClaimConflict(topic="x", claim_a="a", claim_b="b")
        assert conflict.resolution is None


PERSONAL_ARTICLE = """---
title: How I bounded our Kafka fan-out
subtitle: A case study from a Black Friday incident
topics: [kafka, backend]
canonical_url: "https://blog.example.com/kafka-fanout"
ai_assistance: none
---

# How I bounded our Kafka fan-out

Last Black Friday our consumer fell seven hours behind. I owned the fix.

## What broke

One hot user generated 50,000 notifications. I benchmarked the fix: p99
went from 2.3s to 180ms.

## What I changed

We bounded fan-out per partition key, which preserved ordering.
"""


class TestAdaptation:
    def test_attribution_present(self) -> None:
        post = adapt_for_social(parse_article_text(PERSONAL_ARTICLE))
        assert "How I bounded our Kafka fan-out" in post.attribution
        assert "blog.example.com" in post.text

    def test_no_fabricated_numbers(self) -> None:
        article = parse_article_text(PERSONAL_ARTICLE)
        post = adapt_for_social(article)
        # Every number in the post must exist in the source article.
        import re

        post_numbers = set(re.findall(r"\d+(?:\.\d+)?", post.text))
        source_text = str(article)
        for number in post_numbers:
            assert number in source_text, f"fabricated number {number}"

    def test_deterministic(self) -> None:
        article = parse_article_text(PERSONAL_ARTICLE)
        assert adapt_for_social(article).text == adapt_for_social(article).text

    def test_char_count_consistent(self) -> None:
        post = adapt_for_social(parse_article_text(PERSONAL_ARTICLE))
        assert post.char_count == len(post.text)
        assert not post.over_limit

    def test_over_limit_detected(self) -> None:
        post = adapt_for_social(parse_article_text(PERSONAL_ARTICLE))
        post.text = "x" * 3001
        post.char_count = 3001
        assert post.over_limit

    def test_hashtags_from_topics(self) -> None:
        post = adapt_for_social(parse_article_text(PERSONAL_ARTICLE))
        assert "#kafka" in post.hashtags


class TestExporter:
    def test_supported_platforms(self) -> None:
        assert supported_export_platforms() == ["devto", "hashnode", "linkedin", "substack"]

    def test_unknown_platform_raises(self, tmp_path) -> None:
        article = parse_article_text(PERSONAL_ARTICLE)
        with pytest.raises(ValueError, match="No export prep"):
            export_for_platform(article, "twitter", tmp_path)

    def test_devto_export(self, tmp_path) -> None:
        article = parse_article_text(PERSONAL_ARTICLE)
        result = export_for_platform(article, "devto", tmp_path)
        content = Path(result.output_path).read_text(encoding="utf-8")
        assert "published: false" in content  # never auto-publish
        assert 'title: "How I bounded our Kafka fan-out"' in content
        assert "canonical_url" in content
        assert result.canonical_url == "https://blog.example.com/kafka-fanout"

    def test_devto_truncates_tags_with_warning(self, tmp_path) -> None:
        md = PERSONAL_ARTICLE.replace(
            "topics: [kafka, backend]",
            "topics: [kafka, backend, streaming, events, data]",
        )
        result = export_for_platform(parse_article_text(md), "devto", tmp_path)
        assert any("maximum of 4" in w for w in result.warnings)

    def test_devto_republish_without_canonical_warns(self, tmp_path) -> None:
        md = PERSONAL_ARTICLE.replace(
            'canonical_url: "https://blog.example.com/kafka-fanout"\n', ""
        ).replace("ai_assistance: none", "ai_assistance: none\noriginally_published: true")
        result = export_for_platform(parse_article_text(md), "devto", tmp_path)
        assert any("canonical_url" in w for w in result.warnings)

    def test_hashnode_export(self, tmp_path) -> None:
        result = export_for_platform(parse_article_text(PERSONAL_ARTICLE), "hashnode", tmp_path)
        content = Path(result.output_path).read_text(encoding="utf-8")
        assert "tags: [kafka, backend]" in content
        assert any("GitHub as Source" in w for w in result.warnings)

    def test_substack_export(self, tmp_path) -> None:
        result = export_for_platform(parse_article_text(PERSONAL_ARTICLE), "substack", tmp_path)
        content = Path(result.output_path).read_text(encoding="utf-8")
        assert "# How I bounded our Kafka fan-out" in content
        assert any("subject line" in w for w in result.warnings)

    def test_linkedin_export_is_plain_post(self, tmp_path) -> None:
        result = export_for_platform(parse_article_text(PERSONAL_ARTICLE), "linkedin", tmp_path)
        content = Path(result.output_path).read_text(encoding="utf-8")
        assert "LinkedIn adaptation" in content
        assert result.frontmatter.get("shape") == "feed-post"

    def test_liquid_tags_flagged_for_portability(self, tmp_path) -> None:
        md = PERSONAL_ARTICLE.replace(
            "## What I changed",
            "## What I changed\n\n{% embed https://youtube.com/watch?v=1 %}",
        )
        result = export_for_platform(parse_article_text(md), "hashnode", tmp_path)
        assert any("liquid tag" in w for w in result.warnings)


class TestDevToAdapter:
    def test_tag_limit_error(self) -> None:
        md = PERSONAL_ARTICLE.replace(
            "topics: [kafka, backend]",
            "topics: [a, b, c, d, e]",
        )
        problems = DevToAdapter().validate_article(parse_article_text(md))
        assert any("maximum of 4" in p for p in problems)

    def test_h1_body_warning(self) -> None:
        article = parse_article_text(PERSONAL_ARTICLE)
        report = DevToAdapter().full_report(article)
        structure = [c for c in report.checks if c.category == "Structure"]
        assert any(c.status.value == "WARNING" for c in structure)

    def test_republish_without_canonical_is_error(self) -> None:
        md = PERSONAL_ARTICLE.replace(
            'canonical_url: "https://blog.example.com/kafka-fanout"\n', ""
        ).replace("ai_assistance: none", "ai_assistance: none\noriginally_published: true")
        report = DevToAdapter().full_report(parse_article_text(md))
        assert report.overall.value == "ERROR"
        canonical = next(c for c in report.checks if c.category == "Canonical URL")
        assert canonical.status.value == "ERROR"
        assert canonical.source_id == "dev-help-writing"

    def test_ai_generated_without_disclosure_is_error(self) -> None:
        md = PERSONAL_ARTICLE.replace("ai_assistance: none", "ai_assistance: generated")
        report = DevToAdapter().full_report(parse_article_text(md))
        ai = next(c for c in report.checks if c.category == "AI Policy")
        assert ai.status.value == "ERROR"
        assert "ABotWroteThis" in ai.detail

    def test_disclosure_tag_satisfies_policy(self) -> None:
        md = PERSONAL_ARTICLE.replace(
            "topics: [kafka, backend]", "topics: [kafka, backend, abotwrotethis]"
        ).replace("ai_assistance: none", "ai_assistance: generated")
        report = DevToAdapter().full_report(parse_article_text(md))
        ai = next(c for c in report.checks if c.category == "AI Policy")
        assert ai.status.value == "PASS"

    def test_clean_article_scores_full(self) -> None:
        score = DevToAdapter().platform_compatibility_score(parse_article_text(PERSONAL_ARTICLE))
        assert score.score == 5


class TestHashnodeAdapter:
    def test_liquid_tag_portability_warning(self) -> None:
        md = PERSONAL_ARTICLE.replace(
            "## What I changed",
            "## What I changed\n\n{% katex %}x{% endkatex %}",
        )
        report = HashnodeAdapter().full_report(parse_article_text(md))
        formatting = next(c for c in report.checks if c.category == "Formatting")
        assert "liquid tag" in formatting.detail

    def test_ai_policy_honestly_not_checked(self) -> None:
        report = HashnodeAdapter().full_report(parse_article_text(PERSONAL_ARTICLE))
        ai = next(c for c in report.checks if c.category == "AI Policy")
        assert ai.status.value == "NOT CHECKED"
        assert "No official Hashnode AI policy" in ai.detail

    def test_republish_canonical_maps_to_setting(self) -> None:
        report = HashnodeAdapter().full_report(parse_article_text(PERSONAL_ARTICLE))
        canonical = next(c for c in report.checks if c.category == "Canonical URL")
        assert canonical.status.value == "NOT APPLICABLE"

    def test_no_invented_tag_limit(self) -> None:
        md = PERSONAL_ARTICLE.replace("topics: [kafka, backend]", "topics: [a, b, c, d, e, f, g]")
        problems = HashnodeAdapter().validate_article(parse_article_text(md))
        assert not any("tag" in p.lower() for p in problems)


class TestSubstackAdapter:
    def test_title_doubles_as_subject(self) -> None:
        report = SubstackAdapter().full_report(parse_article_text(PERSONAL_ARTICLE))
        title = next(c for c in report.checks if c.category == "Title")
        assert "subject line" in title.detail
        assert title.source_id == "substack-title-testing"

    def test_marketing_density_is_policy_error(self) -> None:
        md = PERSONAL_ARTICLE.replace(
            "We bounded fan-out per partition key, which preserved ordering.",
            "Sign up now! Limited time offer. Use my link. Discount code SAVE20. "
            "Buy my course. Click here to buy!",
        )
        report = SubstackAdapter().full_report(parse_article_text(md))
        policy = next(c for c in report.checks if c.category == "Content Guidelines")
        assert policy.status.value == "ERROR"
        assert policy.source_id == "substack-content-guidelines"

    def test_ai_scan_exposure_mentioned(self) -> None:
        md = PERSONAL_ARTICLE.replace("ai_assistance: none", "ai_assistance: generated")
        report = SubstackAdapter().full_report(parse_article_text(md))
        ai = next(c for c in report.checks if c.category == "AI Policy")
        assert "Scan for AI" in ai.detail
        assert ai.source_id == "substack-ai-detection"

    def test_canonical_honestly_not_checked(self) -> None:
        report = SubstackAdapter().full_report(parse_article_text(PERSONAL_ARTICLE))
        canonical = next(c for c in report.checks if c.category == "Canonical Link")
        assert canonical.status.value == "NOT CHECKED"
        assert "No official Substack documentation" in canonical.detail


class TestLinkedInAdapter:
    def test_adaptation_review_label(self) -> None:
        report = LinkedInAdapter().full_report(parse_article_text(PERSONAL_ARTICLE))
        assert any(c.category == "Adaptation review" for c in report.checks)
        assert "adaptation" in report.disclaimer.lower()

    def test_post_length_limit(self) -> None:
        from article_craft.models.adaptation import SocialPost

        adapter = LinkedInAdapter()
        over = SocialPost(
            platform="linkedin",
            text="x" * 3001,
            attribution="From: t",
            source_title="t",
            char_count=3001,
        )
        checks = adapter.review_social_post(over)
        length = next(c for c in checks if c.category == "Post Length")
        assert length.status.value == "ERROR"
        assert length.source_id == "linkedin-post-limits"

    def test_engagement_bait_flagged(self) -> None:
        from article_craft.models.adaptation import SocialPost

        adapter = LinkedInAdapter()
        post = SocialPost(
            platform="linkedin",
            text="Great news! Comment yes below if you agree! Tag 3 people!",
            attribution="From: t",
            source_title="t",
            char_count=60,
        )
        checks = adapter.review_social_post(post)
        assert any(c.category == "Engagement Bait" for c in checks)

    def test_slop_warning_quotes_official_definition(self) -> None:
        article = parse_article_text(PERSONAL_ARTICLE)
        report = LinkedInAdapter().full_report(article)
        ai = next(c for c in report.checks if c.category == "AI Policy")
        assert "AI" in ai.detail

    def test_validate_article_requires_adaptation(self) -> None:
        problems = LinkedInAdapter().validate_article(parse_article_text(PERSONAL_ARTICLE))
        assert any("adapt" in p.lower() for p in problems)
