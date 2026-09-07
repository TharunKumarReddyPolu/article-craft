"""The Hashnode adapter.

Rules summarized in ``skills/article-craft/references/platforms/hashnode/``
are enforced here, each tagged POLICY / RECOMMENDATION / HEURISTIC and
citing its ``source_id`` from that directory's ``sources.yaml``. Where
Hashnode publishes no official policy (e.g. AI content, as of
verification), the adapter says NOT CHECKED instead of inventing a rule.
"""

from __future__ import annotations

import re
from pathlib import Path

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
    / "hashnode"
    / "sources.yaml"
)

# Hashnode embeds via %[URL] (Embed.ly) per markdown-guidelines.
_EMBED_CANDIDATE = re.compile(r"^\s*<?(https?://\S+?)>?\s*$")
_EMBEDDABLE = re.compile(
    r"(youtube\.com|youtu\.be|twitter\.com|x\.com|github\.com|codepen\.io|soundcloud\.com|glitch\.com)",
    re.IGNORECASE,
)
# DEV-style liquid tags are NOT valid Hashnode markdown (markdown-guidelines
# documents %[URL] instead); they render as literal text.
_LIQUID = re.compile(r"\{%\s*(\w+)")
_FENCE = re.compile(r"^\s*```(\w*)")


@register_adapter
class HashnodeAdapter(SourcesBackedAdapter):
    platform_id = "hashnode"
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
        checks: list[PlatformCheck] = []
        analysis = analyze_title(article.effective_title)
        if not article.effective_title:
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.ERROR,
                    detail="No title. Hashnode's title is a dedicated editor field; "
                    "the export prep maps it from frontmatter/H1.",
                    rule_class=RuleClass.HEURISTIC,
                    source_id="hashnode-write-article",
                )
            )
        elif analysis.clickbait_risk == "high":
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.WARNING,
                    detail="Title has sensationalistic patterns. Hashnode's developer "
                    "audience rewards specific, honest titles.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.PASS,
                    detail=f'Title: "{article.effective_title}".',
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        checks.append(
            PlatformCheck(
                category="Subtitle",
                status=PlatformCheckStatus.WARNING
                if not article.effective_subtitle
                else PlatformCheckStatus.PASS,
                detail=(
                    "No subtitle — Hashnode supports one via the 'Add Subtitle' "
                    "button; it carries the promise in previews."
                    if not article.effective_subtitle
                    else f'Subtitle: "{article.effective_subtitle}".'
                ),
                rule_class=RuleClass.RECOMMENDATION,
                source_id="hashnode-write-article",
            )
        )
        return checks

    def review_structure(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        sections = [s for s in article.sections if s.title]
        checks.append(
            PlatformCheck(
                category="Structure",
                status=PlatformCheckStatus.PASS,
                detail=f"{len(sections)} section(s), ~{article.word_count} words, "
                f"~{article.reading_time_minutes:.0f} min read.",
                rule_class=RuleClass.HEURISTIC,
            )
        )
        # Title is a separate field on Hashnode, so a body H1 is legal but a
        # second title-like H1 usually duplicates it.
        h1_bodies = _h1_texts("\n".join(s.body for s in article.sections))
        if h1_bodies:
            if article.title and h1_bodies[0].strip().lower() == article.title.strip().lower():
                checks.append(
                    PlatformCheck(
                        category="Structure",
                        status=PlatformCheckStatus.WARNING,
                        detail=f"Body H1 (line of '{h1_bodies[0][:40]}…') duplicates the "
                        "title field — Hashnode renders the title separately, so the "
                        "H1 would appear twice.",
                        rule_class=RuleClass.HEURISTIC,
                    )
                )
            else:
                checks.append(
                    PlatformCheck(
                        category="Structure",
                        status=PlatformCheckStatus.WARNING,
                        detail=f"{len(h1_bodies)} H1 heading(s) in the body. The title "
                        "is a separate field on Hashnode; body headings should start "
                        "at H2.",
                        rule_class=RuleClass.HEURISTIC,
                    )
                )
        return checks

    def review_formatting(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        issues: list[str] = []
        body = "\n".join(s.body for s in article.sections)

        # DEV-style liquid tags are not Hashnode syntax.
        unknown = sorted({t for t in _LIQUID.findall(body)})
        if unknown:
            issues.append(
                f"{len(unknown)} liquid tag(s) ({', '.join('{% ' + t + ' %}' for t in unknown[:4])}) "
                "— Hashnode markdown has no liquid tags; they render as literal "
                "text. Use %[URL] embeds instead."
            )
        # Bare URLs on their own line could be rich %[URL] embeds.
        bare_embeds = [
            match.group(1)
            for line in body.splitlines()
            if (match := _EMBED_CANDIDATE.match(line)) and _EMBEDDABLE.search(match.group(1))
        ]
        if bare_embeds:
            issues.append(
                f"{len(bare_embeds)} bare embeddable URL(s) — Hashnode renders "
                "rich embeds with %[URL] syntax (markdown-guidelines)."
            )
        # Untagged code fences: manual language enables highlighting.
        untagged = [b for b in article.code_blocks if not b.language]
        if untagged:
            issues.append(
                f"{len(untagged)} code block(s) without a language tag — add one "
                "(e.g. ```python) for syntax highlighting."
            )
        # Images without alt text (no dedicated Hashnode page: best practice).
        findings = check_all(article)
        alt_issues = [f for f in findings if f.code in {"missing-alt", "filename-alt", "vague-alt"}]
        if alt_issues:
            issues.append(
                f"{len(alt_issues)} image alt-text problem(s), first at line {alt_issues[0].line}."
            )
        if issues:
            checks.append(
                PlatformCheck(
                    category="Formatting",
                    status=PlatformCheckStatus.WARNING,
                    detail=" · ".join(issues[:4]),
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="hashnode-markdown",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Formatting",
                    status=PlatformCheckStatus.PASS,
                    detail="No Hashnode-specific formatting issues detected.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="hashnode-markdown",
                )
            )
        return checks

    def review_policy(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        fm = article.frontmatter

        # AI policy: Hashnode publishes no AI-content policy (verified
        # 2026-09-07). Say so instead of inventing one.
        if fm.ai_assistance == "unspecified":
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.NOT_CHECKED,
                    detail="Hashnode's official support docs contain no published "
                    "AI-content policy as of the last verification (see sources.yaml). "
                    "Article Craft's platform-agnostic rules still apply: your "
                    "contribution, originality, and fact-checking.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.NOT_CHECKED,
                    detail=f"ai_assistance='{fm.ai_assistance}' recorded. No official "
                    "Hashnode AI policy exists to check against (verified "
                    "2026-09-07); editorial expectations are Article Craft's own.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )

        # Canonical: official mechanism is "Are you republishing? -> Add
        # Original Article".
        if fm.originally_published:
            if fm.canonical_url:
                checks.append(
                    PlatformCheck(
                        category="Canonical URL",
                        status=PlatformCheckStatus.PASS,
                        detail=f"canonical_url present ({fm.canonical_url}); map it to "
                        "the 'Add Original Article' setting when publishing.",
                        rule_class=RuleClass.RECOMMENDATION,
                        source_id="hashnode-write-article",
                    )
                )
            else:
                checks.append(
                    PlatformCheck(
                        category="Canonical URL",
                        status=PlatformCheckStatus.WARNING,
                        detail="Republished content without a canonical URL. Use "
                        "Hashnode's 'Are you republishing? -> Add Original Article' "
                        "setting so search engines credit the original.",
                        rule_class=RuleClass.RECOMMENDATION,
                        source_id="hashnode-write-article",
                    )
                )
        else:
            checks.append(
                PlatformCheck(
                    category="Canonical URL",
                    status=PlatformCheckStatus.NOT_APPLICABLE,
                    detail="Original article (no 'originally_published' in frontmatter).",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="hashnode-write-article",
                )
            )
        return checks

    def review_distribution(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        checks.append(
            PlatformCheck(
                category="Distribution Risks",
                status=PlatformCheckStatus.NOT_CHECKED,
                detail="Hashnode publishes no distribution/curation guidelines to "
                "check against (verified 2026-09-07). Note the platform option to "
                "hide an article from the Hashnode community (blog-only display). "
                "Originality and reader-value checks above still apply.",
                rule_class=RuleClass.HEURISTIC,
                source_id="hashnode-write-article",
            )
        )
        return checks

    def generate_platform_checklist(self, article: Article) -> list[str]:
        return [
            "Cover photo (recommended 1200x630) if the post deserves one",
            "Optional subtitle added via 'Add Subtitle'",
            "Custom OG image for social sharing if the cover won't crop well",
            "Embeds use %[URL] syntax — no liquid tags, no raw embed code",
            "Code blocks fenced with a language tag for highlighting",
            "Republished? Set 'Are you republishing? -> Add Original Article'",
            "Slug edited if the auto-generated one misleads",
            "Alt text on every image",
            "You can stand behind every claim and link in the post",
        ]

    def platform_compatibility_score(self, article: Article) -> DimensionScore:
        score = DimensionScore(
            dimension=Dimension.PLATFORM_COMPATIBILITY,
            score=DIMENSION_MAX[Dimension.PLATFORM_COMPATIBILITY],
        )
        all_checks = (
            self.review_title(article)
            + self.review_structure(article)
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
            score.strengths.append("No Hashnode formatting or metadata issues detected.")
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


def _h1_texts(body: str) -> list[str]:
    out: list[str] = []
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and (match := re.match(r"^#\s+(.+)$", line)):
            out.append(match.group(1))
    return out


def hashnode_pre_publish_check(article: Article) -> object:
    """Convenience entry point used by the CLI."""
    return HashnodeAdapter().full_report(article)
