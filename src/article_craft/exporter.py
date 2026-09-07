"""Export prep: convert the canonical article into platform-ready files.

Zero network calls. Nothing is published, scheduled, or uploaded — export
writes markdown files locally with ``published: false`` (or no publish
state at all) and collects honest warnings for everything that could not
be converted deterministically.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from article_craft.editorial.adaptation import adapt_for_social
from article_craft.models.adaptation import PlatformExport
from article_craft.models.article import Article

_FRONTMATTER_FIELDS = ("title", "subtitle", "author", "topics")


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "article"


def _yaml_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _frontmatter_block(fields: list[tuple[str, object]]) -> str:
    lines = ["---"]
    for key, value in fields:
        if isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif isinstance(value, list):
            lines.append(f"{key}: [{', '.join(str(v) for v in value)}]")
        elif isinstance(value, str):
            lines.append(f"{key}: {_yaml_str(value)}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def _body(article: Article) -> str:
    """The article body without its frontmatter (sections already exclude it)."""
    return "\n\n".join(
        (f"## {section.title}\n\n{section.body}" if section.title else section.body)
        for section in article.sections
    ).strip()


def _strip_dev_liquid(body: str) -> tuple[str, list[str]]:
    """DEV liquid tags are not portable; flag them, keep the text untouched."""
    warnings: list[str] = []
    found = re.findall(r"\{%[^%]*%\}", body)
    for tag in sorted(set(found)):
        warnings.append(
            f"DEV liquid tag {tag} is not portable — convert it manually for the "
            "target platform (e.g. to a plain link or %[URL] embed on Hashnode)."
        )
    return body, warnings


def _export_devto(article: Article, out_dir: object) -> PlatformExport:
    warnings: list[str] = []
    fm = article.frontmatter
    topics = list(fm.topics)
    if len(topics) > 4:
        warnings.append(
            f"{len(topics)} tags present; DEV allows a maximum of 4. The export "
            f"keeps the first 4 ({', '.join(topics[:4])}) — reorder before "
            "publishing if these aren't the ones you want."
        )
        topics = topics[:4]
    canonical = fm.canonical_url
    if fm.originally_published and not canonical:
        warnings.append(
            "Marked as originally published elsewhere but no canonical_url in "
            "frontmatter. DEV requires it for reposts to avoid SEO penalties — "
            "add canonical_url before publishing."
        )
    cover = fm.extra.get("cover_image")
    if not cover:
        warnings.append("No cover_image set (DEV's Editor Guide recommends 1000x420).")
    body, liquid_warnings = _strip_dev_liquid(_body(article))
    warnings.extend(liquid_warnings)

    fields: list[tuple[str, object]] = [
        ("title", article.effective_title),
        ("published", False),
        ("description", (fm.subtitle or "")[:140]),
        ("tags", topics),
    ]
    if canonical:
        fields.append(("canonical_url", canonical))
    if cover:
        fields.append(("cover_image", str(cover)))
    content = f"{_frontmatter_block(fields)}\n\n{body}\n"

    out_path = out_dir / f"{_slugify(article.effective_title)}-devto.md"  # type: ignore[operator]
    out_path.write_text(content, encoding="utf-8")
    return PlatformExport(
        platform="devto",
        output_path=str(out_path),
        frontmatter=dict(fields),
        warnings=warnings,
        is_republish=fm.originally_published,
        canonical_url=canonical,
    )


def _export_hashnode(article: Article, out_dir: object) -> PlatformExport:
    warnings: list[str] = [
        "Hashnode has no single documented front matter contract for its "
        "editor; this export targets the 'GitHub as Source' flow (official "
        "TownHall guide). Verify field names against Hashnode's template "
        "repository before publishing."
    ]
    fm = article.frontmatter
    canonical = fm.canonical_url
    if fm.originally_published and not canonical:
        warnings.append(
            "Republished content without canonical_url: on Hashnode, set the "
            "original via 'Are you republishing? -> Add Original Article'."
        )
    if not fm.extra.get("cover_image") and not fm.extra.get("cover_photo"):
        warnings.append("No cover image in frontmatter (Hashnode recommends 1200x630).")
    body, liquid_warnings = _strip_dev_liquid(_body(article))
    warnings.extend(liquid_warnings)

    fields: list[tuple[str, object]] = [
        ("title", article.effective_title),
        ("tags", [re.sub(r"[^a-z0-9]", "", t.lower()) for t in fm.topics]),
        ("enableToc", True),
    ]
    if canonical:
        fields.append(("canonicalUrl", canonical))
    content = f"{_frontmatter_block(fields)}\n\n{body}\n"

    out_path = out_dir / f"{_slugify(article.effective_title)}-hashnode.md"  # type: ignore[operator]
    out_path.write_text(content, encoding="utf-8")
    return PlatformExport(
        platform="hashnode",
        output_path=str(out_path),
        frontmatter=dict(fields),
        warnings=warnings,
        is_republish=fm.originally_published,
        canonical_url=canonical,
    )


def _export_substack(article: Article, out_dir: object) -> PlatformExport:
    warnings = [
        "Substack has no markdown/front matter import contract in its editor: "
        "paste the body into the post editor and set title/subtitle in the UI.",
        "The title doubles as the email subject line — review it with both audiences in mind.",
        "Images must be re-uploaded through Substack's editor and given alt "
        "text ('Edit alt text' on each image).",
    ]
    fm = article.frontmatter
    body = _body(article)
    header = f"# {article.effective_title}\n"
    if article.effective_subtitle:
        header += f"\n*{article.effective_subtitle}*\n"
    content = f"{header}\n{body}\n"

    out_path = out_dir / f"{_slugify(article.effective_title)}-substack.md"  # type: ignore[operator]
    out_path.write_text(content, encoding="utf-8")
    return PlatformExport(
        platform="substack",
        output_path=str(out_path),
        frontmatter={"title": article.effective_title},
        warnings=warnings,
        is_republish=fm.originally_published,
        canonical_url=fm.canonical_url,
    )


def _export_linkedin(article: Article, out_dir: object) -> PlatformExport:
    warnings: list[str] = []
    post = adapt_for_social(article, platform="linkedin")
    if post.char_count > 3000:
        warnings.append(
            f"Post adaptation is {post.char_count} characters; LinkedIn's "
            "documented limit is 3,000. Trim before posting."
        )
    warnings += [
        "LinkedIn posts are plain text: markdown does not carry over.",
        "Code blocks need the article editor's code-snippet tool, or must be "
        "described in text for the post shape.",
        "For the article shape, fill the SEO title/description in LinkedIn's editor settings.",
    ]
    content = (
        f"# LinkedIn adaptation of: {article.effective_title}\n\n"
        "> Plain-text feed post (3,000-char limit). The canonical article stays "
        "primary; attribute it when posting. Publishing is manual.\n\n"
        f"{post.text}\n"
    )
    out_path = out_dir / f"{_slugify(article.effective_title)}-linkedin.md"  # type: ignore[operator]
    out_path.write_text(content, encoding="utf-8")
    return PlatformExport(
        platform="linkedin",
        output_path=str(out_path),
        frontmatter={"title": article.effective_title, "shape": "feed-post"},
        warnings=warnings,
        is_republish=article.frontmatter.originally_published,
        canonical_url=article.frontmatter.canonical_url,
    )


_EXPORTERS = {
    "devto": _export_devto,
    "hashnode": _export_hashnode,
    "substack": _export_substack,
    "linkedin": _export_linkedin,
}


def supported_export_platforms() -> list[str]:
    return sorted(_EXPORTERS)


def export_for_platform(article: Article, platform: str, out_dir: Path) -> PlatformExport:
    """Export the article for a platform. Writes files locally only."""
    exporter = _EXPORTERS.get(platform)
    if exporter is None:
        supported = ", ".join(supported_export_platforms())
        raise ValueError(
            f"No export prep for platform '{platform}'. Supported: {supported}. "
            "Publishing automation is out of scope by design."
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    return exporter(article, out_dir)


def render_export_report(export: PlatformExport) -> str:
    lines = [
        f"# Export prep: {export.platform}",
        "",
        f"Written to: `{export.output_path}`",
        f"Republish: {'yes — canonical URL needed' if export.is_republish else 'no'}",
        f"Canonical URL: {export.canonical_url or '(none)'}",
        "",
        "## Warnings",
        "",
    ]
    lines += [f"- {w}" for w in export.warnings] or ["- None."]
    lines += [
        "",
        "Nothing was published or uploaded — export writes files locally only. "
        f"Generated {date.today().isoformat()}.",
    ]
    return "\n".join(lines) + "\n"
