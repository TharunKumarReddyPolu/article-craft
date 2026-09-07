"""The Substack adapter.

Rules summarized in ``skills/article-craft/references/platforms/substack/``
are enforced here, each tagged POLICY / RECOMMENDATION / HEURISTIC and
citing its ``source_id`` from that directory's ``sources.yaml``. The
adapter never predicts open rates, subscriber growth, or boost-type
outcomes (Substack does not operate a curation program to predict).
"""

from __future__ import annotations

import re
from pathlib import Path

from article_craft.editorial.ai_patterns import ai_pattern_density_per_1000
from article_craft.editorial.images import check_all
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
    / "substack"
    / "sources.yaml"
)

# Official Content Guidelines (2026-07-20): the platform is for editorial
# content; publications whose primary purpose is advertising, driving
# third-party traffic, or SEO are not permitted. These are density
# heuristics implementing that clause (the clause is the POLICY).
_PROMO = re.compile(
    r"\b(sign up (now|today)|subscribe to my|buy (now|my)|limited time offer|"
    r"discount code|coupon|click (here|the link) to (buy|shop)|use my link)\b",
    re.IGNORECASE,
)


@register_adapter
class SubstackAdapter(SourcesBackedAdapter):
    platform_id = "substack"
    _sources_path = _SOURCES_PATH

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
        """On Substack the title IS the email subject line — review it with
        both audiences in mind (official mechanics: substack-title-testing)."""
        checks: list[PlatformCheck] = []
        analysis = analyze_title(article.effective_title)
        if not article.effective_title:
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.ERROR,
                    detail="No title. On Substack the title doubles as the email "
                    "subject line, so there is nothing to send.",
                    rule_class=RuleClass.POLICY,
                    source_id="substack-title-testing",
                )
            )
            return checks
        if analysis.clickbait_risk == "high":
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.WARNING,
                    detail="Title has sensationalistic patterns. As an email subject "
                    "line this burns subscriber trust — opens bought with a "
                    "misleading subject are not returned.",
                    rule_class=RuleClass.HEURISTIC,
                    source_id="substack-title-testing",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.PASS,
                    detail=f'Title/subject line: "{article.effective_title}".',
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="substack-title-testing",
                )
            )
        checks.append(
            PlatformCheck(
                category="Title Testing",
                status=PlatformCheckStatus.NOT_APPLICABLE,
                detail="Substack's 'Run a title test' can A/B test alternate subject "
                "lines (official feature; requires 200+ subscribers) — a note, not "
                "a check this tool performs.",
                rule_class=RuleClass.RECOMMENDATION,
                source_id="substack-title-testing",
            )
        )
        return checks

    def review_structure(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        sections = [s for s in article.sections if s.title]
        if article.word_count >= 800 and not sections:
            checks.append(
                PlatformCheck(
                    category="Structure",
                    status=PlatformCheckStatus.WARNING,
                    detail=f"{article.word_count} words with no H2 sections. Long "
                    "emails read better with skimmable sections.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Structure",
                    status=PlatformCheckStatus.PASS,
                    detail=f"{len(sections)} section(s), ~{article.word_count} words, "
                    f"~{article.reading_time_minutes:.0f} min read.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        return checks

    def review_formatting(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        issues: list[str] = []
        findings = check_all(article)
        alt_issues = [f for f in findings if f.code in {"missing-alt", "filename-alt", "vague-alt"}]
        if alt_issues:
            issues.append(
                f"{len(alt_issues)} image alt-text problem(s), first at line "
                f"{alt_issues[0].line} — Substack images support alt text via "
                "the image menu ('Edit alt text')."
            )
        untagged = [b for b in article.code_blocks if not b.language]
        if untagged:
            issues.append(
                f"{len(untagged)} code block(s) without a language tag — Substack's "
                "code blocks auto-detect language, but explicit tags render "
                "reliably in email."
            )
        if issues:
            checks.append(
                PlatformCheck(
                    category="Formatting",
                    status=PlatformCheckStatus.WARNING,
                    detail=" · ".join(issues),
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="substack-alt-text",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Formatting",
                    status=PlatformCheckStatus.PASS,
                    detail="No Substack-specific formatting issues detected.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="substack-alt-text",
                )
            )
        return checks

    def review_policy(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        fm = article.frontmatter
        body = "\n".join(s.body for s in article.sections)
        body_lower = body.lower()

        # --- Content Guidelines: Marketing & Promotion (POLICY) --------------
        promo_hits = _PROMO.findall(body_lower)
        promo_links = [
            link
            for link in article.links
            if re.search(r"(utm_|affiliate|tag=)", link.url, re.IGNORECASE)
        ]
        promo_density = len(promo_hits) + len(promo_links)
        if promo_density >= 5:
            checks.append(
                PlatformCheck(
                    category="Content Guidelines",
                    status=PlatformCheckStatus.ERROR,
                    detail=f"{promo_density} promotional signals (pitch phrases, "
                    "tracked/affiliate links). Substack's Content Guidelines: the "
                    "platform is 'intended for high quality editorial content, not "
                    "conventional email marketing'; publications whose primary "
                    "purpose is advertising or driving third-party traffic are not "
                    "permitted.",
                    rule_class=RuleClass.POLICY,
                    source_id="substack-content-guidelines",
                )
            )
        elif promo_density > 0:
            checks.append(
                PlatformCheck(
                    category="Content Guidelines",
                    status=PlatformCheckStatus.WARNING,
                    detail=f"{promo_density} promotional signal(s). Keep promotional "
                    "content incidental — a publication that reads as marketing "
                    "violates Substack's Content Guidelines.",
                    rule_class=RuleClass.POLICY,
                    source_id="substack-content-guidelines",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Content Guidelines",
                    status=PlatformCheckStatus.PASS,
                    detail="No promotional-density signals. Editorial content as the "
                    "clear primary purpose.",
                    rule_class=RuleClass.POLICY,
                    source_id="substack-content-guidelines",
                )
            )

        # --- AI exposure (official mechanics) --------------------------------
        density = ai_pattern_density_per_1000(article)
        if fm.ai_assistance == "generated" or (density >= 8.0 and fm.ai_assistance != "none"):
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.WARNING,
                    detail="Substack readers can run 'Scan for AI text' (Pangram) on "
                    "posts published after 2026-07-21 and see an AI-percentage "
                    "estimate; members can also flag posts as 'Seems like AI'. "
                    "None of this is proof of anything, but the exposure is real. "
                    "The durable response is the honest one: add your own "
                    "experience, voice, and verified claims — not evasion.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="substack-ai-detection",
                )
            )
        elif fm.ai_assistance == "unspecified":
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.NOT_CHECKED,
                    detail="No 'ai_assistance' in frontmatter. Context: readers can "
                    "scan posts for AI text (official feature). Set ai_assistance in "
                    "frontmatter for a precise check.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="substack-ai-detection",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.PASS,
                    detail="Declared human-written. Substack's scan tool is an "
                    "estimate; your authorship claim is yours to stand behind.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="substack-ai-detection",
                )
            )

        # --- Canonical --------------------------------------------------------
        checks.append(
            PlatformCheck(
                category="Canonical Link",
                status=PlatformCheckStatus.NOT_CHECKED,
                detail="No official Substack documentation on canonical URLs was "
                "found during verification (2026-09-07). If this content lives on "
                "your own domain too, consult Substack's current import/SEO "
                "settings — do not rely on this tool for that decision.",
                rule_class=RuleClass.HEURISTIC,
            )
        )
        return checks

    def review_distribution(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        checks.append(
            PlatformCheck(
                category="Distribution Risks",
                status=PlatformCheckStatus.PASS,
                detail="Substack has no curation program to predict; distribution "
                "is the author's own list plus Substack's network features. The "
                "Content Guidelines checks above are the policy floor.",
                rule_class=RuleClass.HEURISTIC,
                source_id="substack-content-guidelines",
            )
        )
        return checks

    def generate_platform_checklist(self, article: Article) -> list[str]:
        return [
            "Title works as both web headline and email subject line",
            "Subtitle present (it shows in previews and the archive)",
            "First paragraph earns the open — it's what subscribers see first",
            "Images have alt text (image menu -> 'Edit alt text')",
            "Code blocks use the code-block embed (renders in email and app)",
            "Tags added in post settings",
            "Content is editorial, not marketing (Content Guidelines)",
            "AI usage is something you can own when readers scan or flag it",
            "Send test email to yourself before publishing",
        ]

    def platform_compatibility_score(self, article: Article) -> DimensionScore:
        score = DimensionScore(
            dimension=Dimension.PLATFORM_COMPATIBILITY,
            score=DIMENSION_MAX[Dimension.PLATFORM_COMPATIBILITY],
        )
        all_checks = (
            self.review_title(article)
            + self.review_formatting(article)
            + self.review_policy(article)
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
            score.strengths.append("No Substack policy or formatting issues detected.")
        score.recommendations = [
            c.detail
            for c in all_checks
            if c.status in (PlatformCheckStatus.ERROR, PlatformCheckStatus.WARNING)
        ][:5]
        return score

    def full_report(
        self,
        article: Article,
        extra_checks: list[PlatformCheck] | None = None,
        disclaimer: str | None = None,
        **kwargs: object,
    ) -> PlatformCheckReport:
        return super().full_report(article, extra_checks=extra_checks, disclaimer=disclaimer)


def substack_pre_publish_check(article: Article) -> PlatformCheckReport:
    """Convenience entry point used by the CLI."""
    return SubstackAdapter().full_report(article)
