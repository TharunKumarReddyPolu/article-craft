"""Article Craft CLI.

Commands: init, new, review, check, improve, factcheck, learn, version.

Exit codes (spec §37): 0 = pass, 1 = findings (warnings/errors depending on
command), 2 = invalid usage.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from article_craft import __version__

app = typer.Typer(
    name="article-craft",
    help="An AI editorial workflow for writing better articles.",
    no_args_is_help=True,
    add_completion=False,
)

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2


def _fail(message: str, code: int = EXIT_USAGE) -> None:
    typer.secho(message, fg=typer.colors.RED, err=True)
    raise typer.Exit(code)


def _interactive() -> bool:
    """True when stdin is a TTY. In non-interactive contexts (CI, agents,
    piped input) prompts are skipped and defaults are used — an aborted
    prompt should never be the failure mode."""
    try:
        return sys.stdin.isatty()
    except (ValueError, OSError):
        return False


@app.command()
def version() -> None:
    """Show the Article Craft version."""
    typer.echo(f"article-craft {__version__}")


@app.command()
def init(
    defaults: bool = typer.Option(
        False, "--defaults", help="Create the workspace with defaults and no prompts."
    ),
    audience: str = typer.Option(None, "--audience", help="Your primary audience."),
    topics: str = typer.Option(None, "--topics", help="Comma-separated topics you write about."),
    tone: str = typer.Option(None, "--tone", help="Tone, e.g. conversational-technical."),
    platform: str = typer.Option(None, "--platform", help="Default platform: medium|generic."),
) -> None:
    """Create the .article-craft/ workspace (config, voice, audience, topics,
    preferences). Personal to you; never shipped with the skill."""
    from article_craft.config import init_workspace, load_config, save_config

    answers: dict = {}
    if not defaults and _interactive():
        if audience is None:
            audience = typer.prompt(
                "Primary audience (e.g. 'software engineers')", default="software engineers"
            )
        if topics is None:
            topics = typer.prompt("Topics you write about (comma-separated)", default="")
        if tone is None:
            tone = typer.prompt("Preferred tone", default="conversational-technical")
        if platform is None:
            platform = typer.prompt("Default platform (medium/generic)", default="medium")
    answers = {
        "audience": audience,
        "topics": topics,
        "tone": tone,
        "platform": platform,
    }
    directory, created = init_workspace(defaults=defaults, answers=answers)
    # Persist interactive answers into config.yaml as well.
    config = load_config()
    if audience:
        config.audience = str(audience)
    if topics:
        config.author.topics = [t.strip() for t in str(topics).split(",") if t.strip()]
    if tone:
        config.style.tone = str(tone)
    if platform:
        config.platform.default = str(platform)
    save_config(config)
    typer.secho(f"Workspace ready: {directory}", fg=typer.colors.GREEN)
    for name in created:
        typer.echo(f"  created {name}")
    if not created:
        typer.echo("  (existing files were preserved)")
    typer.echo(
        "\nNext: 'article-craft new' to start an article, or "
        "'article-craft learn ./your-articles/' to build your voice profile."
    )


@app.command()
def new(
    idea: str | None = typer.Option(None, "--idea", help="What you want to write about."),
    audience: str | None = typer.Option(None, "--audience", help="Who this is for."),
    article_type: str = typer.Option(
        None,
        "--type",
        help="technical-tutorial|technical-explainer|system-design|"
        "architecture-deep-dive|case-study|personal-experience|opinion|"
        "beginner-guide|advanced-guide|listicle",
    ),
    angle: str | None = typer.Option(None, "--angle", help="Your unique angle."),
    length: int | None = typer.Option(None, "--length", help="Target length in words."),
    platform: str | None = typer.Option(None, "--platform", help="medium|generic (V1)."),
    output: Path = typer.Option(None, "--output", "-o", help="Write the brief to a file."),
) -> None:
    """Start a new article: produces a brief (promise, thesis, angle, title
    candidates, outline, research questions). Never writes the article."""
    from article_craft.config import load_config
    from article_craft.editorial.types import type_ids
    from article_craft.reports import render_new_article_brief

    config = load_config()
    # Validate explicit options BEFORE any prompting so bad flags fail fast
    # with exit code 2 even in non-interactive contexts.
    if article_type is not None and article_type not in type_ids():
        _fail(f"Unknown article type '{article_type}'. Valid types:\n  " + "\n  ".join(type_ids()))
    if platform is not None and platform not in ("medium", "generic"):
        _fail(f"Unknown platform '{platform}'. V1 supports: medium, generic.")
    if not idea:
        idea = typer.prompt("What do you want to write about?")
    if not audience:
        audience = typer.prompt("Who is the audience?", default=config.audience)
    if not article_type:
        typer.echo("Article types: " + ", ".join(type_ids()))
        article_type = typer.prompt("Article type", default="technical-explainer")
        if article_type not in type_ids():
            _fail(
                f"Unknown article type '{article_type}'. Valid types:\n  " + "\n  ".join(type_ids())
            )
    if not angle and _interactive():
        prompted = typer.prompt("Your unique angle/perspective (Enter to skip)", default="")
        angle = prompted or None
    if platform is None:
        platform = config.platform.default
    assert idea is not None and audience is not None and article_type is not None
    brief = render_new_article_brief(idea, audience, article_type, angle, length, platform)
    if output:
        output.write_text(brief, encoding="utf-8")
        typer.secho(f"Brief written to {output}", fg=typer.colors.GREEN)
    else:
        typer.echo(brief)
    typer.echo("\nThis brief is scaffolding — the article itself is yours to write.")


@app.command()
def review(
    article_path: Path = typer.Argument(..., help="Path to the article markdown file."),
    platform: str = typer.Option(None, "--platform", help="Run the platform check too (medium)."),
    output: Path = typer.Option(None, "--output", "-o", help="Write the review to a file."),
) -> None:
    """Editorial review of a draft: reasoned scores, issues, publish
    recommendation."""
    from article_craft.parsing import ArticleParseError, parse_article_file
    from article_craft.reports import render_review

    try:
        article = parse_article_file(article_path)
    except ArticleParseError as exc:
        _fail(str(exc))
        return
    if platform and platform not in ("medium", "generic"):
        _fail(f"Unknown platform '{platform}'. V1 supports: medium, generic.")
    report = render_review(article, platform=platform)
    _emit(report, output)
    from article_craft.editorial.review import review_article

    result = review_article(article)
    raise typer.Exit(
        EXIT_OK if result.publish_recommendation.verdict.value == "READY" else EXIT_FINDINGS
    )


@app.command()
def check(
    article_path: Path = typer.Argument(..., help="Path to the article markdown file."),
    platform: str = typer.Option("medium", "--platform", help="Platform to check (V1: medium)."),
    output: Path = typer.Option(None, "--output", "-o", help="Write the check to a file."),
) -> None:
    """Pre-publish check for a platform. V1 implements Medium; generic is a
    no-op summary."""
    from article_craft.models.review import PlatformCheckStatus
    from article_craft.parsing import ArticleParseError, parse_article_file
    from article_craft.reports import render_medium_check

    if platform not in ("medium", "generic"):
        _fail(
            f"Unknown platform '{platform}'. V1 supports: medium, generic "
            "(DEV.to/LinkedIn/Substack are roadmap items)."
        )
    try:
        article = parse_article_file(article_path)
    except ArticleParseError as exc:
        _fail(str(exc))
        return
    if platform == "generic":
        typer.echo(
            "Generic check: no platform-specific rules. Editorial review "
            "covers the platform-agnostic dimensions."
        )
        raise typer.Exit(EXIT_OK)
    report_text = render_medium_check(article)
    _emit(report_text, output)
    from article_craft.platforms.medium import medium_pre_publish_check

    report = medium_pre_publish_check(article)
    if report.overall is PlatformCheckStatus.ERROR:
        raise typer.Exit(EXIT_FINDINGS)
    if report.overall is PlatformCheckStatus.WARNING:
        raise typer.Exit(EXIT_FINDINGS)
    raise typer.Exit(EXIT_OK)


@app.command()
def improve(
    article_path: Path = typer.Argument(..., help="Path to the article markdown file."),
    section: str = typer.Option(
        None, "--section", help="Restrict to a section (substring of its title)."
    ),
    output: Path = typer.Option(None, "--output", "-o", help="Write the plan to a file."),
) -> None:
    """Improvement plan: diagnosis + priority problems + suggested changes.
    Never rewrites the article wholesale."""
    from article_craft.parsing import ArticleParseError, parse_article_file
    from article_craft.reports import render_improve_plan

    try:
        article = parse_article_file(article_path)
    except ArticleParseError as exc:
        _fail(str(exc))
        return
    try:
        plan = render_improve_plan(article, section_filter=section)
    except ValueError as exc:
        _fail(str(exc))
        return
    _emit(plan, output)
    raise typer.Exit(EXIT_OK)


@app.command()
def factcheck(
    article_path: Path = typer.Argument(..., help="Path to the article markdown file."),
    output: Path = typer.Option(None, "--output", "-o", help="Write the report to a file."),
) -> None:
    """Fact-check scaffold: extracts claims, classifies what's checkable,
    and marks everything that needs external verification."""
    from article_craft.parsing import ArticleParseError, parse_article_file
    from article_craft.research.claims import factcheck_report_markdown

    try:
        article = parse_article_file(article_path)
    except ArticleParseError as exc:
        _fail(str(exc))
        return
    report = factcheck_report_markdown(article)
    _emit(report, output)
    typer.echo(
        "\nNote: the CLI does not fetch web content. With web access, your agent "
        "verifies these claims against primary sources and upgrades statuses "
        "with evidence.",
        err=True,
    )
    raise typer.Exit(EXIT_OK)


@app.command()
def learn(
    directory: Path = typer.Argument(..., help="Directory containing YOUR markdown articles."),
    output: Path = typer.Option(
        None, "--output", "-o", help="Where to write voice.md (default: .article-craft/voice.md)."
    ),
) -> None:
    """Learn a writing-voice profile from your own existing articles.

    Advisory only; intended for your own writing. Never use it to imitate
    another person's style from copyrighted sources.
    """
    from article_craft.config import workspace_dir
    from article_craft.parsing import ArticleParseError
    from article_craft.voice import build_profile_from_directory

    try:
        profile, parsed, skipped = build_profile_from_directory(directory)
    except ArticleParseError as exc:
        _fail(str(exc))
        return
    target = output or (workspace_dir() / "voice.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(profile.as_markdown(), encoding="utf-8")
    typer.secho(f"Voice profile written to {target}", fg=typer.colors.GREEN)
    typer.echo(f"  analyzed {len(parsed)} file(s), {profile.total_words:,} words")
    if skipped:
        typer.secho(f"  skipped {len(skipped)} file(s):", fg=typer.colors.YELLOW)
        for note in skipped[:5]:
            typer.echo(f"    {note}")
    typer.echo(
        "\nThe profile is advisory: it helps the agent keep YOUR voice, not imitate anyone else's."
    )
    raise typer.Exit(EXIT_OK)


def _emit(text: str, output: Path | None) -> None:
    if output:
        output.write_text(text, encoding="utf-8")
        typer.secho(f"Report written to {output}", fg=typer.colors.GREEN)
    else:
        typer.echo(text)


if __name__ == "__main__":
    app()
