"""CLI integration tests using Typer's CliRunner.

Covers: every command's happy path, exit codes (0/1/2), actionable errors,
missing files, malformed frontmatter, and CI-friendly output files.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from article_craft.cli.main import app

runner = CliRunner()
FIXTURES = Path(__file__).parent.parent / "fixtures" / "articles"


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestVersionAndHelp:
    def test_version(self) -> None:
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "article-craft" in result.output

    def test_help_lists_all_commands(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        for command in ("init", "new", "review", "check", "improve", "factcheck", "learn"):
            assert command in result.output

    @pytest.mark.parametrize(
        "command", ["init", "new", "review", "check", "improve", "factcheck", "learn"]
    )
    def test_command_help(self, command: str) -> None:
        result = runner.invoke(app, [command, "--help"])
        assert result.exit_code == 0


class TestInit:
    def test_defaults_creates_workspace(self, workspace: Path) -> None:
        result = runner.invoke(app, ["init", "--defaults"])
        assert result.exit_code == 0, result.output
        ws = workspace / ".article-craft"
        for name in ("config.yaml", "voice.md", "audience.md", "topics.md", "preferences.md"):
            assert (ws / name).exists()

    def test_with_options(self, workspace: Path) -> None:
        result = runner.invoke(
            app,
            [
                "init",
                "--defaults",
                "--audience",
                "students",
                "--topics",
                "rust, testing",
            ],
        )
        assert result.exit_code == 0
        config = (workspace / ".article-craft" / "config.yaml").read_text(encoding="utf-8")
        assert "students" in config


class TestNew:
    def test_brief_generated(self, workspace: Path) -> None:
        result = runner.invoke(
            app,
            [
                "new",
                "--idea",
                "Postgres partitioning",
                "--audience",
                "backend engineers",
                "--type",
                "technical-explainer",
                "--platform",
                "medium",
                "-o",
                "brief.md",
            ],
        )
        assert result.exit_code == 0, result.output
        brief = Path("brief.md").read_text(encoding="utf-8")
        assert "Title candidates" in brief
        assert "Editorial outline" in brief
        assert "Reader promise" in brief

    def test_invalid_type_fails_with_usage_error(self, workspace: Path) -> None:
        result = runner.invoke(
            app,
            [
                "new",
                "--idea",
                "x",
                "--type",
                "poem",
                "--platform",
                "medium",
            ],
        )
        assert result.exit_code == 2
        assert "Unknown article type" in result.output

    def test_invalid_platform_fails(self, workspace: Path) -> None:
        result = runner.invoke(
            app,
            [
                "new",
                "--idea",
                "x",
                "--type",
                "opinion",
                "--platform",
                "devto",
            ],
        )
        assert result.exit_code == 2
        assert "V1 supports" in result.output


class TestReview:
    def test_excellent_article_ready(self, workspace: Path, tmp_path: Path) -> None:
        result = runner.invoke(app, ["review", str(FIXTURES / "excellent_technical.md")])
        assert result.exit_code == 0
        assert "Editorial Quality" in result.output
        assert "READY" in result.output
        assert "do not guarantee" in result.output

    def test_generic_ai_fails(self, workspace: Path) -> None:
        result = runner.invoke(app, ["review", str(FIXTURES / "generic_ai.md")])
        assert result.exit_code == 1
        assert "DO NOT PUBLISH YET" in result.output

    def test_missing_file_actionable(self, workspace: Path) -> None:
        result = runner.invoke(app, ["review", "nope.md"])
        assert result.exit_code == 2
        assert "Could not find" in result.output

    def test_malformed_frontmatter_actionable(self, workspace: Path, tmp_path: Path) -> None:
        bad = tmp_path / "bad.md"
        bad.write_text("---\ntitle: [unclosed\n---\n\nBody.", encoding="utf-8")
        result = runner.invoke(app, ["review", str(bad)])
        assert result.exit_code == 2
        assert "frontmatter" in result.output

    def test_invalid_utf8_actionable(self, workspace: Path, tmp_path: Path) -> None:
        bad = tmp_path / "binary.md"
        bad.write_bytes(b"\xff\xfe not utf8")
        result = runner.invoke(app, ["review", str(bad)])
        assert result.exit_code == 2
        assert "not valid UTF-8" in result.output

    def test_directory_is_actionable_error(self, workspace: Path) -> None:
        result = runner.invoke(app, ["review", str(FIXTURES)])
        assert result.exit_code == 2
        assert "directory" in result.output

    def test_output_file(self, workspace: Path, tmp_path: Path) -> None:
        out = tmp_path / "review.md"
        result = runner.invoke(
            app,
            [
                "review",
                str(FIXTURES / "excellent_technical.md"),
                "--platform",
                "medium",
                "-o",
                str(out),
            ],
        )
        assert result.exit_code == 0
        content = out.read_text(encoding="utf-8")
        assert "Medium Pre-Publish Check" in content


class TestCheck:
    def test_clean_article_passes(self, workspace: Path) -> None:
        result = runner.invoke(app, ["check", str(FIXTURES / "excellent_technical.md")])
        assert result.exit_code == 0
        assert "PASS" in result.output

    def test_clickbait_fails(self, workspace: Path) -> None:
        result = runner.invoke(app, ["check", str(FIXTURES / "clickbait.md")])
        assert result.exit_code == 1
        assert "ERROR" in result.output

    def test_unknown_platform_usage_error(self, workspace: Path) -> None:
        result = runner.invoke(
            app,
            [
                "check",
                str(FIXTURES / "excellent_technical.md"),
                "--platform",
                "linkedin",
            ],
        )
        assert result.exit_code == 2
        assert "roadmap" in result.output

    def test_generic_platform_ok(self, workspace: Path) -> None:
        result = runner.invoke(
            app,
            [
                "check",
                str(FIXTURES / "excellent_technical.md"),
                "--platform",
                "generic",
            ],
        )
        assert result.exit_code == 0


class TestImprove:
    def test_plan_generated(self, workspace: Path) -> None:
        result = runner.invoke(app, ["improve", str(FIXTURES / "excellent_technical.md")])
        assert result.exit_code == 0
        assert "Improvement Plan" in result.output
        assert "Ground rules" in result.output

    def test_unknown_section_actionable(self, workspace: Path) -> None:
        result = runner.invoke(
            app,
            [
                "improve",
                str(FIXTURES / "excellent_technical.md"),
                "--section",
                "zzz-not-here",
            ],
        )
        assert result.exit_code == 2
        assert "No section matching" in result.output


class TestFactcheck:
    def test_report_with_honest_banner(self, workspace: Path) -> None:
        result = runner.invoke(app, ["factcheck", str(FIXTURES / "unsupported_claims.md")])
        assert result.exit_code == 0
        assert "External verification was not available" in result.output
        assert "94%" in result.output

    def test_missing_file(self, workspace: Path) -> None:
        result = runner.invoke(app, ["factcheck", "ghost.md"])
        assert result.exit_code == 2


class TestLearn:
    def test_profile_from_directory(self, workspace: Path, tmp_path: Path) -> None:
        articles = tmp_path / "mine"
        articles.mkdir()
        (articles / "a.md").write_text(
            (FIXTURES / "excellent_technical.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = runner.invoke(app, ["learn", str(articles)])
        assert result.exit_code == 0, result.output
        voice = workspace / ".article-craft" / "voice.md"
        assert voice.exists()
        assert "Writing Voice Profile" in voice.read_text(encoding="utf-8")

    def test_missing_directory_actionable(self, workspace: Path) -> None:
        result = runner.invoke(app, ["learn", "./does-not-exist"])
        assert result.exit_code == 2
        assert "not a directory" in result.output
