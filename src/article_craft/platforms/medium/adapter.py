"""The Medium adapter: production-quality pre-publish checks.

Rules summarized in ``skills/article-craft/references/platforms/medium/``
are enforced here, each tagged POLICY / RECOMMENDATION / HEURISTIC and
citing its ``source_id`` from ``sources.yaml``. The adapter never predicts
distribution or Boost outcomes.
"""

from __future__ import annotations

import re
from pathlib import Path

from article_craft.editorial.titles import analyze_title
from article_craft.models.article import Article
from article_craft.models.review import (
    DIMENSION_MAX,
    Dimension,
    DimensionScore,
    PlatformCheck,
    PlatformCheckReport,
    PlatformCheckStatus,
    RuleClass,
)
from article_craft.platforms.base import SourcesBackedAdapter, register_adapter

_SOURCES_PATH = (
    Path(__file__).resolve().parents[4]
    / "skills"
    / "article-craft"
    / "references"
    / "platforms"
    / "medium"
    / "sources.yaml"
)

_MEDIUM_DISCLAIMER = (
    "These checks are based on current published guidance and editorial "
    "heuristics. They do not guarantee Medium distribution."
)


@register_adapter
class MediumAdapter(SourcesBackedAdapter):
    platform_id = "medium"
    _sources_path = _SOURCES_PATH

    # ------------------------------------------------------------------ #
    # API
    # ------------------------------------------------------------------ #

    def validate_article(self, article: Article) -> list[str]:
        problems: list[str] = []
        if not article.effective_title:
            problems.append("No title found (H1 or frontmatter 'title').")
        if article.word_count < 40:
            problems.append(
                f"Article has only {article.word_count} words of prose; too short "
                "to review meaningfully."
            )
        return problems

    def review_title(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        analysis = analyze_title(article.effective_title)
        if not article.effective_title:
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.ERROR,
                    detail="No title. Medium stories need a title; the title and "
                    "subtitle are what readers judge in feeds.",
                    rule_class=RuleClass.POLICY,
                    source_id="medium-distribution-guidelines",
                )
            )
        elif analysis.clickbait_risk == "high":
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.ERROR,
                    detail="Title has sensationalistic/clickbait patterns. Medium's "
                    "distribution guidelines disqualify these from General "
                    "Distribution: " + "; ".join(i["detail"] for i in analysis.issues[:2]),
                    rule_class=RuleClass.POLICY,
                    source_id="medium-distribution-guidelines",
                    findings=[f'"{article.effective_title}"'],
                )
            )
        elif analysis.clickbait_risk == "medium" or analysis.clarity == "vague":
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.WARNING,
                    detail="Title leans generic or formulaic — Medium treats 'overly "
                    "generic, mysterious, or formulaic' titles the same as "
                    "sensationalistic ones.",
                    rule_class=RuleClass.POLICY,
                    source_id="medium-distribution-guidelines",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.PASS,
                    detail=f'Title is specific and accurate: "{article.effective_title}".',
                    rule_class=RuleClass.POLICY,
                    source_id="medium-distribution-guidelines",
                )
            )
        if article.effective_subtitle:
            checks.append(
                PlatformCheck(
                    category="Subtitle",
                    status=PlatformCheckStatus.PASS,
                    detail="Subtitle present — it carries extra promise in feeds.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="medium-distribution-guidelines",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Subtitle",
                    status=PlatformCheckStatus.WARNING,
                    detail="No subtitle. The subtitle is your second impression in "
                    "feeds and previews; add the angle/scope the title can't fit.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="medium-distribution-guidelines",
                )
            )
        return checks

    def review_structure(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        sections = [s for s in article.sections if s.title]
        if article.word_count >= 800 and len(sections) == 0:
            checks.append(
                PlatformCheck(
                    category="Structure",
                    status=PlatformCheckStatus.WARNING,
                    detail=f"{article.word_count} words with no sections — hard to "
                    "navigate on Medium. Add H2 sections.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        elif len(sections) >= 1:
            avg = article.word_count // max(1, len(sections))
            checks.append(
                PlatformCheck(
                    category="Structure",
                    status=PlatformCheckStatus.PASS,
                    detail=f"{len(sections)} section(s), ~{avg} words each. Length "
                    f"reads in ~{article.reading_time_minutes:.0f} min.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        if article.reading_time_minutes > 30:
            checks.append(
                PlatformCheck(
                    category="Structure",
                    status=PlatformCheckStatus.WARNING,
                    detail=f"~{article.reading_time_minutes:.0f} min read. Medium Boost "
                    "guidelines say length should serve the story — verify every "
                    "section earns its place or split the piece.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="medium-distribution-guidelines",
                )
            )
        return checks

    def review_formatting(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        findings: list[str] = []
        # Images without alt text.
        missing_alt = [img for img in article.images if not img.alt.strip()]
        if missing_alt:
            findings.append(
                f"{len(missing_alt)} image(s) without alt text (first at line "
                f"{missing_alt[0].line})"
            )
        # Uncaptioned images are fine; uncaptioned AI images are a policy issue
        # handled in review_policy. Here: descriptive link text.
        bad_links = [
            link
            for link in article.links
            if link.text.strip().lower() in {"click here", "here", "link", "this"}
        ]
        if bad_links:
            findings.append(
                f"{len(bad_links)} link(s) with non-descriptive text like "
                f"'click here' (first at line {bad_links[0].line})"
            )
        # Raw HTML that Medium's editor doesn't support.
        if re.search(
            r"<(script|style|iframe|div|span)\b",
            "\n".join(s.body for s in article.sections),
            re.IGNORECASE,
        ):
            findings.append(
                "Raw HTML (script/style/iframe/div/span) — Medium's "
                "editor does not support it; it will be stripped."
            )
        # Embeds: URLs on their own line work as embeds.
        if findings:
            checks.append(
                PlatformCheck(
                    category="Formatting",
                    status=PlatformCheckStatus.WARNING,
                    detail="Formatting issues found: " + " · ".join(findings),
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="medium-first-story",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Formatting",
                    status=PlatformCheckStatus.PASS,
                    detail="No formatting issues detected at the Markdown level.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="medium-first-story",
                )
            )
        return checks

    def review_policy(self, article: Article) -> list[PlatformCheck]:
        """AI policy, duplicate/canonical, affiliate, mentions, topics."""
        checks: list[PlatformCheck] = []
        fm = article.frontmatter
        body = "\n".join(s.body for s in article.sections)
        body_lower = body.lower()

        # --- AI policy -----------------------------------------------------
        disclosure_present = bool(
            re.search(
                r"\b(this (story|article|post) (was|is) written (with|using) (the assistance of|"
                r"help from) (an )?ai|written with the assistance of an ai|ai (writing )?"
                r"(program|tool|assistant) (was|is) used)\b",
                body_lower,
            )
        )
        ai_caption_present = any(
            img.caption and re.search(r"\bai\b|artificial intelligence", img.caption, re.IGNORECASE)
            for img in article.images
        )
        if fm.ai_assistance == "generated":
            if not disclosure_present:
                checks.append(
                    PlatformCheck(
                        category="AI Policy",
                        status=PlatformCheckStatus.ERROR,
                        detail="Frontmatter marks this as AI-generated but no disclosure "
                        "was found. Undisclosed AI-generated writing gets Network-only "
                        "distribution. Add one sentence in the first two paragraphs, "
                        "e.g. 'This story was written with the assistance of an AI "
                        "writing program.'",
                        rule_class=RuleClass.POLICY,
                        source_id="medium-ai-content-policy",
                    )
                )
            else:
                checks.append(
                    PlatformCheck(
                        category="AI Policy",
                        status=PlatformCheckStatus.WARNING,
                        detail="Disclosed AI-generated content: disclosure found. "
                        "Reminder: AI-generated writing may not be paywalled in the "
                        "Partner Program, and stories that appear AI-generated are not "
                        "Boost-eligible. Only you can verify the label matches reality.",
                        rule_class=RuleClass.POLICY,
                        source_id="medium-ai-content-policy",
                    )
                )
        elif fm.ai_assistance == "assistive":
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.PASS
                    if disclosure_present
                    else PlatformCheckStatus.WARNING,
                    detail=(
                        "AI-assisted and disclosed."
                        if disclosure_present
                        else "Frontmatter marks AI assistance. Medium requires stories "
                        "incorporating AI assistance to be clearly labeled; pure "
                        "grammar/spell-check does not need disclosure. Disclose in "
                        "the first two paragraphs if AI wrote any text."
                    ),
                    rule_class=RuleClass.POLICY,
                    source_id="medium-ai-content-policy",
                )
            )
        elif fm.ai_assistance == "unspecified":
            # Heuristic signals only; the author knows the truth.
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.NOT_CHECKED,
                    detail="No 'ai_assistance' in frontmatter. If AI generated text or "
                    "images in this story, Medium requires disclosure (one sentence in "
                    "the first two paragraphs; captions for AI images). Set "
                    "ai_assistance: none | assistive | generated in frontmatter so this "
                    "check can be precise.",
                    rule_class=RuleClass.POLICY,
                    source_id="medium-ai-content-policy",
                )
            )
        else:  # "none"
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.PASS,
                    detail="Frontmatter declares no AI-generated content. Keep it that "
                    "way — accuracy here is your responsibility under Medium's policy.",
                    rule_class=RuleClass.POLICY,
                    source_id="medium-ai-content-policy",
                )
            )
        ai_images_needing_caption = [
            img
            for img in article.images
            if "ai" in img.alt.lower()
            or "midjourney" in img.url.lower()
            or "dall-e" in img.url.lower()
            or "stable-diffusion" in img.url.lower()
        ]
        if ai_images_needing_caption and not ai_caption_present:
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.WARNING,
                    detail=f"{len(ai_images_needing_caption)} image(s) look AI-generated "
                    "(by alt text/URL) but have no caption identifying them as such. "
                    "Medium requires AI-generated images to be captioned.",
                    rule_class=RuleClass.POLICY,
                    source_id="medium-ai-content-policy",
                    findings=[f"first at line {ai_images_needing_caption[0].line}"],
                )
            )

        # --- Canonical / duplicate content -----------------------------------
        if fm.canonical_url or fm.originally_published:
            checks.append(
                PlatformCheck(
                    category="Canonical Link",
                    status=PlatformCheckStatus.WARNING,
                    detail="Marked as originally published elsewhere: set the canonical "
                    "link in Medium's story settings (Advanced settings → 'This story "
                    "was originally published elsewhere'). Only the author can set it; "
                    "Article Craft cannot set it for you.",
                    rule_class=RuleClass.POLICY,
                    source_id="medium-canonical-link",
                    findings=[fm.canonical_url] if fm.canonical_url else [],
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Canonical Link",
                    status=PlatformCheckStatus.NOT_APPLICABLE,
                    detail="No canonical_url in frontmatter and not marked as "
                    "republished. If this content will exist on your blog too, set "
                    "one — duplicates without a canonical link can hurt search "
                    "ranking for both copies.",
                    rule_class=RuleClass.POLICY,
                    source_id="medium-canonical-link",
                )
            )

        # --- Affiliate disclosure -------------------------------------------
        affiliate_links = [
            link
            for link in article.links
            if re.search(r"(tag=|affiliate|amzn\.to|aff\.)", link.url, re.IGNORECASE)
        ]
        if affiliate_links:
            disclosed = bool(re.search(r"\b(affiliate|commission|disclosure)\b", body_lower))
            checks.append(
                PlatformCheck(
                    category="Affiliate Disclosure",
                    status=PlatformCheckStatus.PASS if disclosed else PlatformCheckStatus.ERROR,
                    detail=(
                        ""
                        if disclosed
                        else f"{len(affiliate_links)} likely affiliate link(s) but no "
                        "disclosure found. FTC rules (via Medium Rules) require a "
                        "simple disclosure sentence, e.g. in the footer."
                    ),
                    rule_class=RuleClass.POLICY,
                    source_id="medium-rules",
                )
            )

        # --- Mentions / topic spam ------------------------------------------
        if len(article.mentions) > 3:
            checks.append(
                PlatformCheck(
                    category="Topics & Mentions",
                    status=PlatformCheckStatus.WARNING,
                    detail=f"{len(article.mentions)} @mentions — stories with large "
                    "numbers of mentions are not eligible for General Distribution. "
                    "Mention people only when they'd appreciate it.",
                    rule_class=RuleClass.POLICY,
                    source_id="medium-distribution-guidelines",
                    findings=article.mentions[:5],
                )
            )
        if len(fm.topics) > 5:
            checks.append(
                PlatformCheck(
                    category="Topics & Mentions",
                    status=PlatformCheckStatus.WARNING,
                    detail=f"{len(fm.topics)} topics listed; Medium allows up to 5.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="medium-first-story",
                )
            )
        return checks

    def review_distribution(self, article: Article) -> list[PlatformCheck]:
        """Distribution-guideline risk signals. Advisory; never a prediction."""
        checks: list[PlatformCheck] = []
        body = "\n".join(s.body for s in article.sections)
        body_lower = body.lower()
        risks: list[str] = []

        title_analysis = analyze_title(article.effective_title)
        if title_analysis.clickbait_risk == "high":
            risks.append("Clickbait title (disqualifies from General Distribution).")

        if re.search(
            r"\b(sign up (now|today)|subscribe to my|buy (now|my)|limited time|dm me for)\b",
            body_lower,
        ):
            risks.append(
                "Sales/signup pitch language — stories whose primary point "
                "is gathering signups/traffic/sales are low-value content."
            )

        if (
            re.search(r"\b(top \d+ (links|resources)|link round-?up|weekly links)\b", body_lower)
            and len(article.links) > 15
        ):
            risks.append("Looks like a link round-up (link-farming is low-value content).")

        outrage = re.findall(r"\b(outrageous|disgusting|unbelievable|sickening)\b", body_lower)
        if len(outrage) >= 3:
            risks.append(
                "High outrage-language density — 'unconstructive negativity' "
                "is a General Distribution disqualifier."
            )

        if not risks:
            checks.append(
                PlatformCheck(
                    category="Distribution Risks",
                    status=PlatformCheckStatus.PASS,
                    detail="No obvious disqualifiers found (clickbait, sales-pitch "
                    "primary purpose, link-farming, outrage-bait). Distribution "
                    "remains Medium's editorial call — these checks do not predict it.",
                    rule_class=RuleClass.POLICY,
                    source_id="medium-distribution-guidelines",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Distribution Risks",
                    status=PlatformCheckStatus.WARNING,
                    detail="Potential distribution risks: " + " · ".join(risks),
                    rule_class=RuleClass.POLICY,
                    source_id="medium-distribution-guidelines",
                    findings=risks,
                )
            )

        # Medium-meta: stories about Medium itself.
        if re.search(
            r"\b(medium partner program|how i (make|earn) money on medium|"
            r"medium (boost|curation) (tips|program))\b",
            body_lower,
        ):
            checks.append(
                PlatformCheck(
                    category="Distribution Risks",
                    status=PlatformCheckStatus.WARNING,
                    detail="This story appears to be about Medium/the Partner Program: "
                    "these are set to Network Distribution only. Consider tagging "
                    "'medium-meta'.",
                    rule_class=RuleClass.POLICY,
                    source_id="medium-distribution-guidelines",
                )
            )
        return checks

    def generate_platform_checklist(self, article: Article) -> list[str]:
        return [
            "Title accurately represents the story (no sensationalism, no genericness)",
            "Subtitle adds the promise or angle",
            "Topics chosen (up to 5) match the content",
            "Cover image (optional): original or carefully chosen; AI images captioned",
            "AI usage disclosed per Medium's AI policy if applicable",
            "Canonical link set in story settings if cross-posting",
            "Affiliate links disclosed (FTC via Medium Rules)",
            "Alt text on images; credits where required",
            "Code blocks tagged with language",
            "Proofread the final preview exactly as readers will see it",
            "Remember: these steps do not guarantee Boost or distribution",
        ]

    def platform_compatibility_score(self, article: Article) -> DimensionScore:
        """Platform Compatibility dimension (max 5), reasons required."""
        score = DimensionScore(
            dimension=Dimension.PLATFORM_COMPATIBILITY,
            score=DIMENSION_MAX[Dimension.PLATFORM_COMPATIBILITY],
        )
        all_checks = (
            self.review_title(article)
            + self.review_structure(article)
            + self.review_formatting(article)
            + self.review_policy(article)
            + self.review_distribution(article)
        )
        errors = [c for c in all_checks if c.status is PlatformCheckStatus.ERROR]
        warnings = [c for c in all_checks if c.status is PlatformCheckStatus.WARNING]
        if errors:
            score.score -= min(4, 2 * len(errors))
            score.reasons.append(
                f"-{min(4, 2 * len(errors))}: {len(errors)} policy ERROR(s): "
                + "; ".join(f"{c.category}" for c in errors[:3])
            )
        if warnings:
            penalty = min(5 - score.score if score.score > 0 else 1, len(warnings))
            if penalty > 0 and score.score - penalty >= 0:
                score.score -= penalty
                score.reasons.append(
                    f"-{penalty}: {len(warnings)} warning(s): "
                    + "; ".join(f"{c.category}" for c in warnings[:3])
                )
        score.score = max(0, score.score)
        if score.score == DIMENSION_MAX[Dimension.PLATFORM_COMPATIBILITY]:
            score.strengths.append("No Medium policy or formatting issues detected.")
        score.recommendations = [
            c.detail
            for c in all_checks
            if c.status in (PlatformCheckStatus.ERROR, PlatformCheckStatus.WARNING)
        ][:5]
        return score

    # ------------------------------------------------------------------ #

    def full_report(
        self,
        article: Article,
        extra_checks: list[PlatformCheck] | None = None,
        disclaimer: str | None = None,
        **kwargs: object,
    ) -> PlatformCheckReport:
        """Aggregate all categories into a PlatformCheckReport."""
        return super().full_report(
            article, extra_checks=extra_checks, disclaimer=disclaimer or _MEDIUM_DISCLAIMER
        )


def medium_pre_publish_check(article: Article) -> PlatformCheckReport:
    """Convenience entry point used by the CLI."""
    return MediumAdapter().full_report(article)
