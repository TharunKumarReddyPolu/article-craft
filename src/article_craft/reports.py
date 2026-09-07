"""Report renderers: deterministic markdown output for the CLI.

These reports are the *deterministic* layer. The agent adds editorial
judgment on top per the skill workflows; the disclaimer about distribution
prediction travels with every Medium-related report.
"""

from __future__ import annotations

from article_craft.editorial.review import review_article
from article_craft.models.article import Article
from article_craft.models.review import (
    Dimension,
    PlatformCheck,
    PlatformCheckReport,
    PlatformCheckStatus,
    ReviewResult,
    RuleClass,
    Severity,
)
from article_craft.platforms.base import available_platforms, get_adapter

SEVERITY_ORDER = {Severity.CRITICAL: 0, Severity.MAJOR: 1, Severity.MINOR: 2, Severity.INFO: 3}
STATUS_EMOJI = {
    PlatformCheckStatus.PASS: "PASS",
    PlatformCheckStatus.WARNING: "WARNING",
    PlatformCheckStatus.ERROR: "ERROR",
    PlatformCheckStatus.NOT_CHECKED: "NOT CHECKED",
    PlatformCheckStatus.NOT_APPLICABLE: "NOT APPLICABLE",
}

DISCLAIMER = (
    "These checks are based on current published guidance and editorial "
    "heuristics. They do not guarantee distribution on any platform."
)


def images_platform_check(article: Article) -> PlatformCheck:
    """The deterministic image/alt-text findings as one platform check."""
    from article_craft.editorial.images import check_all
    from article_craft.models.review import PlatformCheckStatus

    findings = check_all(article)
    majors = [f for f in findings if f.severity.value in ("major", "critical")]
    minors = [f for f in findings if f.severity.value == "minor"]
    if not article.images:
        status = PlatformCheckStatus.NOT_APPLICABLE
    elif majors or minors:
        status = PlatformCheckStatus.WARNING
    else:
        status = PlatformCheckStatus.PASS
    if not article.images:
        detail = "No images in the article."
    elif majors:
        detail = (
            f"{len(majors)} significant image issue(s): alt text missing, "
            "filename-like, or too vague to be useful."
        )
    elif minors:
        detail = f"{len(minors)} minor image issue(s) (vague alt, captions, screenshots)."
    else:
        detail = "All images have usable, descriptive alt text."
    return PlatformCheck(
        category="Images",
        status=status,
        detail=detail,
        rule_class=RuleClass.BEST_PRACTICE,
        findings=[f"line {f.line}: {f.message}" for f in findings[:8]],
    )


def render_platform_check_for(article: Article, platform: str) -> str:
    """Pre-publish check for any registered platform adapter."""
    adapter_cls = get_adapter(platform)
    if adapter_cls is None:
        raise ValueError(
            f"No adapter registered for '{platform}'. Available: "
            + ", ".join(available_platforms())
        )
    adapter = adapter_cls()
    extra = [images_platform_check(article)] if platform == "medium" else None
    report = adapter.full_report(article, extra_checks=extra)
    return "\n".join(render_platform_check(report))


def render_review(article: Article, platform: str | None = None) -> str:
    """Full Editorial Review (spec §16 format)."""
    result = review_article(article)
    platform_report: PlatformCheckReport | None = None
    if platform is not None and get_adapter(platform) is not None:
        adapter_cls = get_adapter(platform)
        assert adapter_cls is not None
        adapter = adapter_cls()
        extra = [images_platform_check(article)] if platform == "medium" else None
        platform_report = adapter.full_report(article, extra_checks=extra)
    result.platform_report = platform_report

    lines: list[str] = [
        "# Editorial Review",
        "",
        f"**Article:** {result.article_title}",
        f"**Type:** {result.article_type}" + (f"  |  **Platform:** {platform}" if platform else ""),
        "",
        f"# Overall Editorial Quality: {result.score.total}/100",
        "",
    ]
    if platform_report is not None:
        lines += [
            f"Platform Compatibility: {_platform_points(result)}",
            "",
        ]
    for dim in result.score.dimensions:
        lines.append(f"## {dim.dimension.value}: {dim.score}/{dim.max}")
        lines.append("")
        if dim.strengths:
            lines.append("**Strengths:**")
            lines += [f"- {s}" for s in dim.strengths]
            lines.append("")
        if dim.problems:
            lines.append("**Problems:**")
            lines += [f"- {p}" for p in dim.problems]
            lines.append("")
        if dim.recommendations:
            lines.append("**Recommendations:**")
            lines += [f"- {r}" for r in dim.recommendations]
            lines.append("")
        if dim.reasons:
            lines.append("**Score reasons:**")
            lines += [f"- {r}" for r in dim.reasons]
            lines.append("")
        if not (dim.strengths or dim.problems or dim.recommendations or dim.reasons):
            lines.append("_No issues detected by the deterministic checks._")
            lines.append("")
    lines.append("# Critical Issues")
    lines.append("")
    if result.critical_issues:
        for i, issue in enumerate(result.critical_issues, start=1):
            lines.append(f"{i}. **{issue.title}** — {issue.detail}")
            if issue.suggestion:
                lines.append(f"   Fix: {issue.suggestion}")
    else:
        lines.append("_None._")
    lines.append("")

    lines.append("# Recommended Changes")
    lines.append("")
    if result.recommended_changes:
        lines += [f"{i}. {c}" for i, c in enumerate(result.recommended_changes, start=1)]
    else:
        lines.append("_None._")
    lines.append("")

    if platform_report is not None:
        lines += render_platform_check(platform_report)
    else:
        lines.append("# Platform Check")
        lines.append("")
        lines += _render_images_section(article)
        lines.append(
            "_No platform check run. Re-run with `--platform medium|devto|hashnode|"
            "substack|linkedin` for the platform-specific pre-publish check._"
        )
        lines.append("")

    if not result.human_contribution.present:
        lines.append("# Author Contribution")
        lines.append("")
        lines.append(f"⚠️ {result.human_contribution.summary}")
        lines += [f"- {s}" for s in result.human_contribution.suggestions[:3]]
        lines.append("")

    lines.append("# Publish Recommendation")
    lines.append("")
    lines.append(f"## {result.publish_recommendation.verdict.value}")
    lines.append("")
    lines.append(result.publish_recommendation.explanation)
    lines.append("")
    lines.append(f"> {DISCLAIMER}")
    return "\n".join(lines)


def _platform_points(result: ReviewResult) -> str:
    if result.platform_report is None:
        return "n/a"
    dim = result.score.dimension(Dimension.PLATFORM_COMPATIBILITY)
    return f"{dim.score}/{dim.max}"


def _render_images_section(article: Article) -> list[str]:
    check = images_platform_check(article)
    lines = [f"## Images — **{STATUS_EMOJI[check.status]}**", "", check.detail, ""]
    lines += [f"- {f}" for f in check.findings]
    if check.findings:
        lines.append("")
    return lines


def render_platform_check(report: PlatformCheckReport) -> list[str]:
    lines = [
        f"# {report.platform.capitalize()} Pre-Publish Check",
        "",
        f"**Overall: {STATUS_EMOJI[report.overall]}**",
        "",
    ]
    for check in report.checks:
        lines.append(f"## {check.category}")
        lines.append("")
        lines.append(
            f"**{STATUS_EMOJI[check.status]}** ({check.rule_class.value}"
            + (f", source: {check.source_id}" if check.source_id else "")
            + ")"
        )
        lines.append("")
        lines.append(check.detail)
        if check.findings:
            lines += [f"- {f}" for f in check.findings]
        lines.append("")
    if report.fix_items:
        lines.append("# Fix Before Publishing")
        lines.append("")
        lines += [f"{i}. {fix}" for i, fix in enumerate(report.fix_items, start=1)]
        lines.append("")
    lines.append(f"> {report.disclaimer}")
    return lines


def render_medium_check(article: Article) -> str:
    adapter_cls = get_adapter("medium")
    if adapter_cls is None:  # pragma: no cover - medium is always registered
        raise RuntimeError("Medium adapter not registered")
    report = adapter_cls().full_report(article)
    return "\n".join(render_platform_check(report))


def render_improve_plan(article: Article, section_filter: str | None = None) -> str:
    """Improve workflow (spec §21): diagnosis first, never wholesale rewrite."""
    result = review_article(article)
    target_sections = article.sections
    if section_filter:
        matched = article.section_by_title(section_filter)
        if matched is None:
            available = ", ".join(s.title for s in article.sections if s.title) or "(none)"
            raise ValueError(f"No section matching '{section_filter}'. Sections: {available}.")
        target_sections = [matched]
    lines = [
        f"# Improvement Plan: {article.effective_title}",
        "",
    ]
    if section_filter:
        lines += [f"_Scoped to section matching '{section_filter}'._", ""]
    lines += [
        "## Diagnosis",
        "",
        f"Editorial Quality Score {result.score.total}/100 "
        f"({result.publish_recommendation.verdict.value}). "
        + (
            result.publish_recommendation.explanation
            if result.publish_recommendation.verdict
            is not __import__("article_craft.models.review", fromlist=["Verdict"]).Verdict.READY
            else "The article meets the editorial bar; the plan below is polish."
        ),
        "",
        "## Priority problems",
        "",
    ]
    issues = sorted(result.issues, key=lambda i: SEVERITY_ORDER[i.severity])
    scoped = issues
    if section_filter and target_sections:
        names = [s.title or "(intro)" for s in target_sections]
        scoped = [i for i in issues if i.location and any(n in i.location for n in names)] or issues
    if scoped:
        for i, issue in enumerate(scoped[:8], start=1):
            label = issue.severity.value.upper()
            lines.append(f"{i}. **[{label}] {issue.title}** — {issue.detail}")
            if issue.suggestion:
                lines.append(f"   Suggested change: {issue.suggestion}")
    else:
        lines.append(
            "_No deterministic issues in scope. Judgment-layer "
            "suggestions come from the agent workflow._"
        )
    lines += [
        "",
        "## Ground rules for the rewrite",
        "",
        "- Preserve the author's meaning, perspective, factual claims, "
        "personal experiences, and intended audience.",
        "- Proposed rewrites are options, applied only where the author agrees.",
        "- Do not introduce facts the author didn't provide; flag gaps instead.",
        "- Match the author's voice (see `.article-craft/voice.md` if present).",
    ]
    return "\n".join(lines)


def render_new_article_brief(
    idea: str,
    audience: str,
    article_type: str,
    angle: str | None = None,
    target_words: int | None = None,
    platform: str = "medium",
) -> str:
    """The `new` workflow brief (spec §14): never writes the article."""
    from article_craft.editorial.outline import build_outline
    from article_craft.editorial.titles import (
        generate_title_candidates,
        title_candidates_to_markdown,
    )

    outline = build_outline(idea, audience, article_type, angle, target_words)
    candidates = generate_title_candidates(idea, angle or outline.angle, audience, article_type)
    lines = [
        "# New Article Brief",
        "",
        f"**Idea:** {idea}",
        f"**Audience:** {audience}",
        f"**Type:** {article_type}",
        f"**Platform:** {platform}",
        "",
        title_candidates_to_markdown(candidates),
        outline.to_markdown(),
        "## Next steps",
        "",
        "1. Pick/adjust title + subtitle (accuracy note per candidate).",
        "2. Answer the research questions using Tier 1-2 sources; record them in `research.md`.",
        "3. Write your contribution first — the part only you can write.",
        "4. Draft section by section (templates in the skill), or ask the "
        "agent to help with a specific section.",
        "5. Run `article-craft review`, then `article-craft factcheck`, then "
        "`article-craft check --platform medium`.",
        "",
        "_The article itself is yours to write. This brief is scaffolding, not content._",
    ]
    return "\n".join(lines)
