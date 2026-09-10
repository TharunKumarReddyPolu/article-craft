"""Tests for the friction-reduction features: demo, doctor, and CLI wiring.

The demo is the first thing every new user runs — its contract is that it
exercises the real engines and never fails on a healthy install. Doctor is
the first thing they run when something feels off.
"""

from __future__ import annotations

from typer.testing import CliRunner

from article_craft.cli.main import app

runner = CliRunner()


class TestDemoCommand:
    def test_demo_runs_all_three_steps(self) -> None:
        result = runner.invoke(app, ["demo"])
        assert result.exit_code == 0, result.output
        assert "1. Editorial review" in result.output
        assert "2. Fact-check scaffold" in result.output
        assert "3. medium pre-publish check" in result.output
        # The demo must show real engine output, not placeholders.
        assert "Editorial Quality" in result.output
        assert "UNVERIFIED" in result.output

    def test_demo_next_steps_mention_skill_install(self) -> None:
        result = runner.invoke(app, ["demo"])
        assert result.exit_code == 0
        assert "npx skills add" in result.output

    def test_demo_rejects_unknown_platform(self) -> None:
        result = runner.invoke(app, ["demo", "--platform", "myspace"])
        assert result.exit_code == 2
        assert "Unknown platform" in result.output

    def test_demo_on_devto_platform(self) -> None:
        result = runner.invoke(app, ["demo", "--platform", "devto"])
        assert result.exit_code == 0, result.output
        assert "devto pre-publish check" in result.output


class TestDoctorCommand:
    def test_doctor_reports_healthy_environment(self) -> None:
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0, result.output
        assert "environment doctor" in result.output
        assert "Python" in result.output
        assert "article-craft demo" in result.output

    def test_doctor_marks_uninitialized_workspace_as_info(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0, result.output
        # Missing workspace is informational, not a failure: init is a choice.
        assert "not initialized yet" in result.output
        assert "article-craft init" in result.output
