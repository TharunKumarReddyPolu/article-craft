"""Unit tests for configuration and the research/fact-check layer."""

from __future__ import annotations

import pytest

from article_craft.config import (
    WorkspaceConfig,
    init_workspace,
    load_config,
    save_config,
    workspace_dir,
)
from article_craft.models.research import ClaimStatus, ResearchDoc
from article_craft.parsing import parse_article_text
from article_craft.research.artifact import render_research_doc
from article_craft.research.claims import extract_claims


class TestConfig:
    def test_defaults_when_missing(self, tmp_path) -> None:
        config = load_config(tmp_path)
        assert config.version == 1
        assert config.platform.default == "medium"

    def test_save_and_load_roundtrip(self, tmp_path) -> None:
        config = WorkspaceConfig(audience="students")
        config.style.tone = "formal-technical"
        save_config(config, tmp_path)
        loaded = load_config(tmp_path)
        assert loaded.audience == "students"
        assert loaded.style.tone == "formal-technical"

    def test_malformed_config_actionable(self, tmp_path) -> None:
        d = workspace_dir(tmp_path)
        d.mkdir(parents=True)
        (d / "config.yaml").write_text("version: [unclosed\n", encoding="utf-8")
        with pytest.raises(ValueError, match="Could not parse"):
            load_config(tmp_path)

    def test_init_workspace_creates_files(self, tmp_path) -> None:
        directory, created = init_workspace(tmp_path, defaults=True)
        assert (directory / "config.yaml").exists()
        assert (directory / "voice.md").exists()
        assert (directory / "audience.md").exists()
        assert (directory / "topics.md").exists()
        assert (directory / "preferences.md").exists()
        assert set(created) == {
            "config.yaml",
            "voice.md",
            "audience.md",
            "topics.md",
            "preferences.md",
        }

    def test_init_preserves_existing(self, tmp_path) -> None:
        init_workspace(tmp_path, defaults=True)
        voice = workspace_dir(tmp_path) / "voice.md"
        voice.write_text("# Custom voice notes", encoding="utf-8")
        _directory, created = init_workspace(tmp_path, defaults=True)
        assert "voice.md" not in created
        assert voice.read_text(encoding="utf-8") == "# Custom voice notes"


class TestClaimExtraction:
    def _claims_for(self, text: str):
        return extract_claims(parse_article_text(text))

    def test_statistics_detected(self) -> None:
        text = "# T\n\nThe benchmark showed 95% of requests under 200ms.\n"
        claims = self._claims_for(text)
        assert claims
        assert all(c.status is ClaimStatus.UNVERIFIED for c in claims)
        assert any("statistic" in (c.reason or "") for c in claims)

    def test_opinion_classified(self) -> None:
        text = "# T\n\nI think Redis is the best choice for this workload.\n"
        claims = self._claims_for(text)
        assert any(c.status is ClaimStatus.OPINION for c in claims)

    def test_assumption_classified(self) -> None:
        text = "# T\n\nAssume the cluster has 10 nodes with 32GB each.\n"
        claims = self._claims_for(text)
        assert any(c.status is ClaimStatus.ASSUMPTION for c in claims)

    def test_attribution_flagged(self) -> None:
        text = "# T\n\nAccording to the official docs, the default timeout is 30 seconds.\n"
        claims = self._claims_for(text)
        assert any("attribution" in (c.reason or "") for c in claims)

    def test_no_claims_in_pure_narrative(self) -> None:
        text = "# T\n\nOnce upon a time there was a cache. It was loved by all.\n"
        claims = self._claims_for(text)
        assert claims == []

    def test_section_attribution(self) -> None:
        text = "# T\n\n## Benchmarks\n\nThe p99 latency was 12ms under load.\n"
        claims = self._claims_for(text)
        assert claims and claims[0].section_title == "Benchmarks"


class TestResearchArtifact:
    def test_render_contains_sections(self) -> None:
        from article_craft.models.research import ResearchDoc, Source, SourceTier

        doc = ResearchDoc(
            thesis="Test thesis",
            research_questions=["Q1?", "Q2?"],
            sources=[
                Source(title="Official docs", url="https://example.com", tier=SourceTier.OFFICIAL)
            ],
            claims_requiring_verification=["Claim A"],
            statistics=["95% under 200ms"],
        )
        md = render_research_doc(doc)
        assert "## Article Thesis" in md
        assert "## Research Questions" in md
        assert "### Source 1" in md
        assert "Tier 1" in md
        assert "## Claims Requiring Verification" in md
        assert "stays separate from the final article" in md

    def test_no_sources_honest_note(self) -> None:
        md = render_research_doc(ResearchDoc(thesis="t"))
        assert "Never invent a source" in md
