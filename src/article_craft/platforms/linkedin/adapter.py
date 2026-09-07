"""The LinkedIn adapter: reviews a *LinkedIn adaptation*, not raw markdown.

LinkedIn posts are plain text (no markdown) and articles use a rich-text
editor, so the canonical markdown article cannot be checked for LinkedIn
directly. This adapter therefore:

1. Reviews the **adaptation readiness** of the canonical article (what
   survives conversion, what must change), always labeled "Adaptation
   review"; and
2. Checks a produced :class:`SocialPost` artifact via
   ``review_social_post`` (character limit, attribution, engagement-bait).

Rules summarized in ``skills/article-craft/references/platforms/linkedin/``
are enforced with POLICY / RECOMMENDATION / HEURISTIC tags and source_id
citations. The adapter never predicts reach or feed placement.
"""

from __future__ import annotations

import re
from pathlib import Path

from article_craft.editorial.ai_patterns import ai_pattern_density_per_1000
from article_craft.models.adaptation import SocialPost
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
    / "linkedin"
    / "sources.yaml"
)

POST_CHAR_LIMIT = (
    3000  # linkedin-post-limits: official, "The character limit for a post is 3,000 characters"
)

_ADAPTATION_DISCLAIMER = (
    "These checks are based on current published guidance and editorial "
    "heuristics, and they review a LinkedIn adaptation (not the original "
    "markdown). They do not guarantee reach or distribution on LinkedIn."
)
_ENGAGEMENT_BAIT = re.compile(
    r"\b(comment (yes|\"?\w+\"? below)|like (and|&) (comment|subscribe)|tag \d+ (people|friends)|"
    r"repost if|agree\?|am i right)\b",
    re.IGNORECASE,
)


@register_adapter
class LinkedInAdapter(SourcesBackedAdapter):
    platform_id = "linkedin"
    _sources_path = _SOURCES_PATH

    def validate_article(self, article: Article) -> list[str]:
        problems: list[str] = [
            "LinkedIn checks review a LinkedIn ADAPTATION (plain-text post or "
            "article draft), not raw markdown. Produce one with "
            "'article-craft adapt' or 'article-craft export --platform linkedin'."
        ]
        if not article.effective_title:
            problems.append("No title found (H1 or frontmatter 'title').")
        if article.word_count < 40:
            problems.append(
                f"Article has only {article.word_count} words of prose; too short "
                "to review meaningfully."
            )
        return problems

    def review_title(self, article: Article) -> list[PlatformCheck]:
        """Adaptation readiness of the title; article shape has SEO settings."""
        checks: list[PlatformCheck] = []
        checks.append(
            PlatformCheck(
                category="Adaptation review",
                status=PlatformCheckStatus.WARNING,
                detail="LinkedIn has two shapes: feed posts (plain text, 3,000-char "
                "limit) and articles (rich-text editor with title + SEO settings). "
                "This markdown article must be adapted before publishing — see the "
                "checklist for what converts and what doesn't.",
                rule_class=RuleClass.HEURISTIC,
                source_id="linkedin-posting",
            )
        )
        if article.effective_title:
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.PASS,
                    detail=f'Working title: "{article.effective_title}". For the '
                    "article shape, also fill LinkedIn's SEO title/description in "
                    "the editor's settings.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="linkedin-articles",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.ERROR,
                    detail="No title to adapt from.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="linkedin-articles",
                )
            )
        return checks

    def review_structure(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        # Official: articles are the long-form shape; "no limits on word count,
        # but the articles that are best received are more than three paragraphs."
        if article.word_count >= 800:
            checks.append(
                PlatformCheck(
                    category="Structure",
                    status=PlatformCheckStatus.PASS,
                    detail=f"~{article.word_count} words: use LinkedIn's ARTICLE shape "
                    "(long-form, no word-count limit; official guidance notes well-"
                    "received articles are 'more than three paragraphs'). A 3,000-char "
                    "feed post cannot hold this.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="linkedin-article-tips",
                )
            )
        # Official: "Keep your writing focused. Avoid covering too many topics."
        sections = [s for s in article.sections if s.title]
        if len(sections) > 8:
            checks.append(
                PlatformCheck(
                    category="Structure",
                    status=PlatformCheckStatus.WARNING,
                    detail=f"{len(sections)} sections cover a lot of ground. LinkedIn's "
                    "official advice: 'Keep your writing focused. Avoid covering too "
                    "many topics in the same article.' Consider splitting.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="linkedin-article-tips",
                )
            )
        return checks

    def review_formatting(self, article: Article) -> list[PlatformCheck]:
        """What survives conversion to LinkedIn's shapes."""
        checks: list[PlatformCheck] = []
        conversions: list[str] = []
        if article.code_blocks:
            conversions.append(
                f"{len(article.code_blocks)} code block(s): use the article editor's "
                "code-snippet tool, or describe the code in the post shape"
            )
        if article.images:
            conversions.append(
                f"{len(article.images)} image(s): upload via the editor's media tool "
                "(markdown links don't carry over)"
            )
        if any(s.subheading_count for s in article.sections):
            conversions.append(
                "H3+ subheadings: the article editor styles text but has no heading "
                "levels — restructure into bold lead-ins or dividers"
            )
        if conversions:
            checks.append(
                PlatformCheck(
                    category="Adaptation review",
                    status=PlatformCheckStatus.WARNING,
                    detail="Markdown that needs manual conversion for LinkedIn: "
                    + " · ".join(conversions[:3]),
                    rule_class=RuleClass.HEURISTIC,
                    source_id="linkedin-articles",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Adaptation review",
                    status=PlatformCheckStatus.PASS,
                    detail="No complex markdown constructs; adapts cleanly.",
                    rule_class=RuleClass.HEURISTIC,
                    source_id="linkedin-articles",
                )
            )
        return checks

    def review_policy(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        fm = article.frontmatter
        density = ai_pattern_density_per_1000(article)

        # --- AI slop (official definition; POLICY-adjacent guidance) ---------
        if density >= 8.0 and fm.ai_assistance != "none":
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.WARNING,
                    detail="High generic-AI pattern density. LinkedIn defines 'AI "
                    "slop' as 'low-effort, likely AI-generated content that may "
                    "sound polished on the surface but lacks a clear point of view, "
                    "unique perspective, or substance', and says such content 'is "
                    "less likely to be widely distributed'. Members can report "
                    "'Seems like AI slop' from the feed. Fix by adding your own "
                    "experience and judgment — not by paraphrasing.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="linkedin-ai-best-practices",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.PASS,
                    detail="AI-pattern density within normal range. LinkedIn welcomes "
                    "AI-assisted content 'when it reflects a real person's "
                    "perspective, experience, or expertise'.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="linkedin-ai-best-practices",
                )
            )
        # Official: disclosure recommended when relying heavily on AI.
        if fm.ai_assistance in ("generated", "assistive"):
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.PASS,
                    detail="AI assistance declared in frontmatter. LinkedIn recommends "
                    "letting readers know (when it isn't obvious) if you relied "
                    "heavily on AI to create or modify content.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="linkedin-ai-best-practices",
                )
            )

        # --- Professional Community Policies ---------------------------------
        checks.append(
            PlatformCheck(
                category="Community Policies",
                status=PlatformCheckStatus.NOT_CHECKED,
                detail="LinkedIn's Professional Community Policies (safety, "
                "trustworthiness, professionalism, IP respect) govern all content. "
                "Article Craft checks originality and sourcing; only you can "
                "confirm the content respects others' IP and privacy.",
                rule_class=RuleClass.POLICY,
                source_id="linkedin-pcp",
            )
        )
        return checks

    def review_distribution(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        checks.append(
            PlatformCheck(
                category="Distribution Risks",
                status=PlatformCheckStatus.NOT_CHECKED,
                detail="LinkedIn does not publish distribution criteria that could "
                "be checked. The closest official statement: AI-assisted content "
                "reflecting 'a real person's perspective, experience, or expertise' "
                "is welcome; generic content 'is less likely to be widely "
                "distributed' (see the AI Policy check). No prediction is made.",
                rule_class=RuleClass.RECOMMENDATION,
                source_id="linkedin-ai-best-practices",
            )
        )
        return checks

    # ------------------------------------------------------------------ #
    # SocialPost shape (feed adaptation)
    # ------------------------------------------------------------------ #

    def review_social_post(self, post: SocialPost) -> list[PlatformCheck]:
        """Checks for a produced plain-text post adaptation."""
        checks: list[PlatformCheck] = []
        if post.char_count > POST_CHAR_LIMIT:
            checks.append(
                PlatformCheck(
                    category="Post Length",
                    status=PlatformCheckStatus.ERROR,
                    detail=f"{post.char_count} characters; LinkedIn's documented "
                    f"limit is {POST_CHAR_LIMIT:,}. Trim to the essential insight "
                    "and link the article.",
                    rule_class=RuleClass.POLICY,
                    source_id="linkedin-post-limits",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Post Length",
                    status=PlatformCheckStatus.PASS,
                    detail=f"{post.char_count} of {POST_CHAR_LIMIT:,} characters.",
                    rule_class=RuleClass.POLICY,
                    source_id="linkedin-post-limits",
                )
            )
        if not post.attribution or not post.source_title:
            checks.append(
                PlatformCheck(
                    category="Attribution",
                    status=PlatformCheckStatus.WARNING,
                    detail="The adaptation should name the source article — the "
                    "canonical article stays primary.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Attribution",
                    status=PlatformCheckStatus.PASS,
                    detail=f"Attributes the source article: {post.source_title}.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        bait = _ENGAGEMENT_BAIT.search(post.text)
        if bait:
            checks.append(
                PlatformCheck(
                    category="Engagement Bait",
                    status=PlatformCheckStatus.WARNING,
                    detail=f'Engagement-bait phrasing ("{bait.group(0)}"). LinkedIn\'s '
                    "'AI slop' definition explicitly covers content 'designed "
                    "primarily to game attention'; make the hook earn the read "
                    "instead.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="linkedin-ai-best-practices",
                )
            )
        if len(post.hashtags) > 5:
            checks.append(
                PlatformCheck(
                    category="Hashtags",
                    status=PlatformCheckStatus.WARNING,
                    detail=f"{len(post.hashtags)} hashtags. LinkedIn publishes no "
                    "official count guidance (verified 2026-09-07); a handful of "
                    "specific tags reads better than a wall of them.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        return checks

    def generate_platform_checklist(self, article: Article) -> list[str]:
        return [
            "Choose the shape: feed post (plain text, 3,000 chars) vs article "
            "(long-form editor with title + SEO settings)",
            "Article shape: fill SEO title and description in editor settings",
            "Code via the editor's code-snippet tool; images via the media tool",
            "First two lines carry the hook — that's what shows before 'see more'",
            "Content reflects your own voice, perspective, and experience (official AI guidance)",
            "Disclose heavy AI reliance when it isn't obvious from context",
            "No engagement bait ('comment yes', 'tag 3 people', 'repost if')",
            "Claim/verify every factual statement before posting",
            "Publishing is manual — Article Craft never posts for you",
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
            score.strengths.append("Adapts cleanly for LinkedIn's shapes.")
        score.recommendations = [
            c.detail
            for c in all_checks
            if c.status in (PlatformCheckStatus.ERROR, PlatformCheckStatus.WARNING)
        ][:5]
        return score

    def full_report(  # type: ignore[override]  # narrows base's **kwargs to `post`
        self,
        article: Article,
        extra_checks: list[PlatformCheck] | None = None,
        disclaimer: str | None = None,
        post: SocialPost | None = None,
        **kwargs: object,
    ) -> PlatformCheckReport:
        """Extended with ``post`` for adaptation review."""
        extra = (extra_checks or []) + (self.review_social_post(post) if post is not None else [])
        return super().full_report(
            article, extra_checks=extra or None, disclaimer=disclaimer or _ADAPTATION_DISCLAIMER
        )


def linkedin_pre_publish_check(
    article: Article, post: SocialPost | None = None
) -> PlatformCheckReport:
    """Convenience entry point used by the CLI."""
    return LinkedInAdapter().full_report(article, post=post)
