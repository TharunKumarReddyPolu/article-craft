"""The DEV.to adapter.

Rules summarized in ``skills/article-craft/references/platforms/devto/``
are enforced here, each tagged POLICY / RECOMMENDATION / HEURISTIC and
citing its ``source_id`` from that directory's ``sources.yaml``. The
adapter never predicts feed placement or reach.
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
    / "devto"
    / "sources.yaml"
)

MAX_TAGS = 4  # dev-editor-guide: "tags: max of four tags"

# Liquid tags documented in the DEV Editor Guide (dev-editor-guide).
KNOWN_LIQUID_TAGS = frozenset(
    {
        "embed",
        "link",
        "user",
        "tag",
        "comment",
        "podcast",
        "organization",
        "forem",
        "card",
        "cta",
        "details",
        "spoiler",
        "collapsible",
        "katex",
        "raw",
    }
)

_LIQUID = re.compile(r"\{%\s*(\w+)")
_DISCLOSURE = re.compile(
    r"\babotwrotethis\b|\bgenerated (by|with) (an )?ai\b|\b(with|using) the (help|assistance) of ai\b"
    r"|\bcreated with the help of ai\b",
    re.IGNORECASE,
)
_PROFANITY = re.compile(r"\b(shit|piss|fuck|dick|asshole|bastard|bitch)\b", re.IGNORECASE)
_SALES_PITCH = re.compile(
    r"\b(sign up (now|today)|buy (now|my)|limited time|dm me for|coupon code)\b",
    re.IGNORECASE,
)


@register_adapter
class DevToAdapter(SourcesBackedAdapter):
    platform_id = "devto"
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
        if len(article.frontmatter.topics) > MAX_TAGS:
            problems.append(
                f"{len(article.frontmatter.topics)} tags in frontmatter; DEV allows a "
                f"maximum of {MAX_TAGS}, comma-separated (dev.to Editor Guide)."
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
                    detail="No title. DEV posts need a title (frontmatter 'title' or H1).",
                    rule_class=RuleClass.POLICY,
                    source_id="dev-editor-guide",
                )
            )
        elif analysis.clickbait_risk == "high":
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.WARNING,
                    detail="Title has sensationalistic patterns. DEV's community "
                    "rewards honest, specific titles; sensational titles also read "
                    "as low-effort to moderators.",
                    rule_class=RuleClass.HEURISTIC,
                    source_id="dev-editor-guide",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.PASS,
                    detail=f'Title is specific and accurate: "{article.effective_title}".',
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="dev-editor-guide",
                )
            )
        # Official: posts with profanity in the title are not promoted.
        if _PROFANITY.search(article.effective_title):
            checks.append(
                PlatformCheck(
                    category="Title",
                    status=PlatformCheckStatus.WARNING,
                    detail="Title contains profanity. DEV does not disallow profanity, "
                    "but has an internal policy of not promoting posts that have "
                    "profanity in the title.",
                    rule_class=RuleClass.POLICY,
                    source_id="dev-help-writing",
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
                    detail=f"{article.word_count} words with no H2 sections — hard to "
                    "navigate; DEV renders a table of contents from headings.",
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
        # Official accessibility guidance: the title is an automatic H1; content
        # should start at H2.
        h1_lines = [line_no for s in article.sections for line_no in _h1_lines(s.body)]
        if h1_lines:
            checks.append(
                PlatformCheck(
                    category="Structure",
                    status=PlatformCheckStatus.WARNING,
                    detail=f"H1 heading(s) in the article body (line {h1_lines[0]}). The "
                    "post title automatically becomes a level-one heading on DEV; "
                    "start sections at H2 to keep the outline readable (and "
                    "screen-reader friendly).",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="dev-editor-guide",
                )
            )
        return checks

    def review_formatting(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        issues: list[str] = []

        # Liquid tags: unknown {% tag %} syntax renders as literal text.
        body = "\n".join(s.body for s in article.sections)
        unknown = sorted(
            {tag for tag in _LIQUID.findall(body) if tag.lower() not in KNOWN_LIQUID_TAGS}
        )
        if unknown:
            issues.append(
                f"unknown liquid tag(s) {{% {', '.join(unknown[:4])} %}} — these render "
                "as literal text on DEV; check spelling against the Editor Guide"
            )
        # Bare URLs that DEV could embed richly via {% embed URL %}.
        bare_embeddable = [
            link
            for link in article.links
            if re.search(
                r"(youtube\.com|youtu\.be|github\.com|twitter\.com|x\.com|codepen\.io)",
                link.url,
                re.IGNORECASE,
            )
            and not _LIQUID.search(body)
        ]
        if bare_embeddable:
            issues.append(
                f"{len(bare_embeddable)} URL(s) from embeddable platforms — consider "
                "{% embed <url> %} so they render as rich cards"
            )
        # Images without alt text (official accessibility guidance).
        findings = check_all(article)
        alt_issues = [f for f in findings if f.code in {"missing-alt", "filename-alt", "vague-alt"}]
        if alt_issues:
            issues.append(
                f"{len(alt_issues)} image alt-text problem(s), first at line "
                f"{alt_issues[0].line}: DEV's Editor Guide asks for descriptive alt "
                "text so screen-reader users can understand images"
            )
        if findings and all(f.code == "prefer-code" for f in findings):
            issues.extend(f.message for f in findings)
        if issues:
            checks.append(
                PlatformCheck(
                    category="Formatting",
                    status=PlatformCheckStatus.WARNING,
                    detail=" · ".join(issues[:4]),
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="dev-editor-guide",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Formatting",
                    status=PlatformCheckStatus.PASS,
                    detail="No DEV-specific formatting issues detected.",
                    rule_class=RuleClass.RECOMMENDATION,
                    source_id="dev-editor-guide",
                )
            )
        return checks

    def review_policy(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        fm = article.frontmatter
        body = "\n".join(s.body for s in article.sections)

        # --- AI policy (official: disclosure + fact-check) -------------------
        disclosure_present = bool(_DISCLOSURE.search(body)) or "abotwrotethis" in {
            t.lower() for t in fm.topics
        }
        if fm.ai_assistance in ("generated", "assistive"):
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.PASS
                    if disclosure_present
                    else PlatformCheckStatus.ERROR,
                    detail=(
                        "AI assistance disclosed (frontmatter tag or in-copy note)."
                        if disclosure_present
                        else "AI-assisted/-generated articles on DEV must disclose: add "
                        "the #ABotWroteThis tag or a disclosure sentence anywhere in "
                        "the copy (e.g. 'This article was created with the help of "
                        "AI'). They must also be fact-checked before publishing — "
                        "see the factcheck workflow."
                    ),
                    rule_class=RuleClass.POLICY,
                    source_id="dev-ai-guidelines",
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="AI Policy",
                    status=PlatformCheckStatus.NOT_CHECKED,
                    detail="No 'ai_assistance' in frontmatter. If AI generated text "
                    "here, DEV requires disclosure (#ABotWroteThis or in-copy) — set "
                    "ai_assistance in frontmatter for a precise check.",
                    rule_class=RuleClass.POLICY,
                    source_id="dev-ai-guidelines",
                )
            )

        # --- Canonical / cross-posting ---------------------------------------
        if fm.originally_published:
            if fm.canonical_url:
                checks.append(
                    PlatformCheck(
                        category="Canonical URL",
                        status=PlatformCheckStatus.PASS,
                        detail=f"Republished with canonical_url set ({fm.canonical_url}). "
                        "DEV notes this prevents SEO penalties for reposting.",
                        rule_class=RuleClass.POLICY,
                        source_id="dev-help-writing",
                    )
                )
            else:
                checks.append(
                    PlatformCheck(
                        category="Canonical URL",
                        status=PlatformCheckStatus.ERROR,
                        detail="Marked as originally published elsewhere but no "
                        "canonical_url. Set it in the front matter (or editor gear "
                        "icon) — it tells search engines where the original lives "
                        "and prevents reposting penalties.",
                        rule_class=RuleClass.POLICY,
                        source_id="dev-help-writing",
                    )
                )
        else:
            checks.append(
                PlatformCheck(
                    category="Canonical URL",
                    status=PlatformCheckStatus.NOT_APPLICABLE,
                    detail="Original article (no 'originally_published' in frontmatter).",
                    rule_class=RuleClass.POLICY,
                    source_id="dev-help-writing",
                )
            )
        return checks

    def review_distribution(self, article: Article) -> list[PlatformCheck]:
        checks: list[PlatformCheck] = []
        body = "\n".join(s.body for s in article.sections)
        body_lower = body.lower()
        risks: list[str] = []

        # Official: backlink-building articles can be suspended (exceptions:
        # personal blogs, company org posts).
        external_domains = {
            re.sub(r"^https?://(www\.)?([^/]+).*", r"\2", link.url.lower())
            for link in article.links
            if not re.search(r"(dev\.to|github\.com|docs\.|localhost)", link.url, re.IGNORECASE)
        }
        if len(external_domains) <= 2 and len(article.links) >= 8:
            risks.append(
                f"{len(article.links)} links concentrated on {len(external_domains)} "
                "external domain(s) reads as backlink-building, which DEV can "
                "suspend accounts for (personal-blog links are fine)."
            )
        if _SALES_PITCH.search(body_lower):
            risks.append("Sales/signup pitch language detected.")

        if risks:
            checks.append(
                PlatformCheck(
                    category="Distribution Risks",
                    status=PlatformCheckStatus.WARNING,
                    detail=" · ".join(risks) + " (DEV decides placement via community "
                    "moderation; these checks do not predict it.)",
                    rule_class=RuleClass.POLICY,
                    source_id="dev-ai-guidelines",
                    findings=risks,
                )
            )
        else:
            checks.append(
                PlatformCheck(
                    category="Distribution Risks",
                    status=PlatformCheckStatus.PASS,
                    detail="No backlink-farming or sales-pitch patterns detected. "
                    "DEV placement is a community-moderation outcome these checks "
                    "do not predict.",
                    rule_class=RuleClass.POLICY,
                    source_id="dev-ai-guidelines",
                )
            )
        return checks

    def generate_platform_checklist(self, article: Article) -> list[str]:
        items = [
            "Tags: at most 4, comma-separated, matching DEV's tag list",
            "Cover image (best size 1000x420) if the post deserves one",
            "Alt text describing each image (DEV Editor Guide accessibility section)",
            "Sections start at H2 — the title is already an H1",
            "AI assistance disclosed (#ABotWroteThis or in-copy) if applicable",
            "canonical_url set if this was published anywhere else first",
            "Liquid tags spelled correctly — unknown tags render as literal text",
            "Code blocks fenced with a language tag",
            "You can stand behind every claim and link in the post",
        ]
        return items

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
            score.strengths.append("No DEV policy or formatting issues detected.")
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


def _h1_lines(body: str) -> list[int]:
    """Line numbers (relative to the section body) that start an H1."""
    out = []
    in_fence = False
    for i, line in enumerate(body.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and re.match(r"^#\s+\S", line):
            out.append(i)
    return out


def devto_pre_publish_check(article: Article) -> object:
    """Convenience entry point used by the CLI."""
    return DevToAdapter().full_report(article)
