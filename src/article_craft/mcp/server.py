"""Article Craft MCP server.

Exposes the deterministic editorial engines as MCP tools over stdio so any
MCP-capable agent can call them directly. The server contains no LLM and
makes no network calls — it runs the same engines as the CLI. Install with
the optional extra: ``pip install article-craft[mcp]``.

Run with: ``article-craft-mcp`` (stdio transport, local-first).
"""

from __future__ import annotations

# Support both MCP SDK generations via importlib: with the optional extra
# absent (e.g. CI without article-craft[mcp]) the modules resolve to Any
# through the mypy ignore_missing_imports override, and static import
# conflicts between the two SDK layouts never arise.
import importlib
from pathlib import Path

from article_craft.editorial.adaptation import adapt_for_social, render_social_post
from article_craft.exporter import export_for_platform, render_export_report
from article_craft.models.article import Article
from article_craft.parsing import ArticleParseError, parse_article_file
from article_craft.platforms.base import available_platforms, get_adapter
from article_craft.reports import images_platform_check, render_platform_check_for, render_review
from article_craft.research.claims import factcheck_report_markdown


def _load_server_cls() -> type:
    for module_name, attr in (
        ("mcp.server.mcpserver", "MCPServer"),
        ("mcp.server.fastmcp", "FastMCP"),
    ):
        try:
            return getattr(importlib.import_module(module_name), attr)
        except ImportError:
            continue
    raise ImportError(
        "The MCP SDK is not installed. Install it with: pip install 'article-craft[mcp]'"
    )


_Server = _load_server_cls()

mcp = _Server(
    "article-craft",
    instructions=(
        "Deterministic editorial engines for reviewing, fact-checking, and "
        "preparing articles for publishing platforms. All tools read local "
        "markdown files and make no network calls. Judgment stays with you: "
        "these tools surface findings; you decide."
    ),
)


def _parse(path: str) -> Article:
    try:
        return parse_article_file(Path(path))
    except ArticleParseError as exc:
        raise ValueError(f"Could not parse {path}: {exc}") from exc


@mcp.tool()
def review_article(path: str, platform: str | None = None) -> str:
    """Full editorial review of an article: 8-dimension reasoned score,
    critical issues, recommended changes, optional platform check.
    Platforms: medium, devto, hashnode, substack, linkedin."""
    article = _parse(path)
    if platform and platform != "generic" and platform not in available_platforms():
        raise ValueError(
            f"Unknown platform '{platform}'. Supported: {', '.join(available_platforms())}"
        )
    return render_review(article, platform=platform)


@mcp.tool()
def platform_check(path: str, platform: str) -> str:
    """Pre-publish check for one platform (medium, devto, hashnode,
    substack, linkedin). LinkedIn reviews a LinkedIn adaptation."""
    if platform not in available_platforms():
        raise ValueError(
            f"Unknown platform '{platform}'. Supported: {', '.join(available_platforms())}"
        )
    article = _parse(path)
    return render_platform_check_for(article, platform)


@mcp.tool()
def factcheck_scaffold(path: str) -> str:
    """Extract claims from an article and classify them (VERIFIED / LIKELY /
    UNVERIFIED / CONTRADICTED / OPINION / ASSUMPTION). The CLI/agent verifies
    externally; this never invents citations."""
    article = _parse(path)
    return factcheck_report_markdown(article)


@mcp.tool()
def check_images(path: str) -> str:
    """Image and alt-text findings: missing/vague/filename alt text,
    captions, screenshots-instead-of-code."""
    article = _parse(path)
    check = images_platform_check(article)
    lines = [f"# Images — {check.status.value}", "", check.detail, ""]
    lines += [f"- {f}" for f in check.findings] or ["- No findings."]
    return "\n".join(lines)


@mcp.tool()
def adapt_social_post(path: str, platform: str = "linkedin") -> str:
    """Derive an attributed social post from the canonical article.
    The article stays primary; nothing is published automatically."""
    if platform not in ("linkedin", "generic"):
        raise ValueError("Supported social platforms: linkedin, generic.")
    article = _parse(path)
    post = adapt_for_social(article, platform=platform)
    checks: list[str] = []
    if platform == "linkedin":
        adapter_cls = get_adapter("linkedin")
        assert adapter_cls is not None
        report = adapter_cls().full_report(article, post=post)
        checks = [
            f"{c.category}: {c.status.value} — {c.detail}"
            for c in report.checks
            if c.category in {"Post Length", "Attribution", "Engagement Bait", "Hashtags"}
        ]
    return render_social_post(post, checks)


@mcp.tool()
def export_prep(path: str, platform: str, out_dir: str = "exports") -> str:
    """Write a platform-ready file locally (devto, hashnode, substack,
    linkedin). Zero network calls; nothing is published. Returns the
    report including all warnings."""
    article = _parse(path)
    try:
        result = export_for_platform(article, platform, Path(out_dir))
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
    return render_export_report(result)


@mcp.tool()
def supported_platforms() -> list[str]:
    """List the platforms with implemented adapters."""
    return available_platforms()


def main() -> None:
    """Entry point for the stdio MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
