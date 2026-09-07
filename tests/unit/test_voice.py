"""Unit tests for the voice profile system."""

from __future__ import annotations

import pytest

from article_craft.parsing import ArticleParseError
from article_craft.voice import build_profile_from_directory, build_profile_from_text

CONVERSATIONAL = """---
title: My take on caching
---

# My take on caching

I spent last week debugging our cache. Have you ever watched a cache make
things *slower*? I hadn't, until now.

Here's the thing: a cache is like a shortcut that only works if people take
the same path. When everyone wanders, the shortcut is just overhead.

What surprised me: our hit rate looked great, but p99 got worse. Think of
it like a restaurant with a great buffet that nobody eats from.

So what would I do differently? Measure per-key hit rates, not global ones.
Maybe you've hit this too — I'd love to hear how you handled it.
"""

FORMAL = """---
title: Cache eviction policy analysis
---

# Cache eviction policy analysis

Cache eviction policies determine which entries are removed under memory
pressure. This document analyzes the trade-offs between LRU, LFU, and ARC
policies under heterogeneous access patterns.

## Policy definitions

Least Recently Used (LRU) evicts the least recently accessed entry. LFU
evicts the least frequently accessed entry. Adaptive Replacement Cache
(ARC) balances recency and frequency dynamically.

## Comparative results

Under scan-heavy workloads, LRU exhibits cache pollution. LFU resists
pollution but adapts slowly to shifting distributions. ARC demonstrates
superior performance in mixed workloads.
"""


class TestProfileExtraction:
    def test_conversational_detected(self) -> None:
        profile = build_profile_from_text([("a.md", CONVERSATIONAL)])
        assert profile.first_person_rate > 2.0
        assert profile.second_person_rate > 1.0
        assert profile.tone == "personal-narrative"

    def test_formal_detected(self) -> None:
        profile = build_profile_from_text([("a.md", FORMAL)])
        assert profile.first_person_rate < 0.5
        assert profile.tone in ("formal-technical", "conversational-technical")

    def test_metrics_are_sane(self) -> None:
        profile = build_profile_from_text([("a.md", CONVERSATIONAL), ("b.md", FORMAL)])
        assert profile.files_analyzed == 2
        assert profile.total_words > 50
        assert 0 < profile.avg_sentence_length < 60
        assert 0 <= profile.long_sentence_ratio <= 1
        assert profile.heading_style in ("Title Case", "sentence case", "mixed")

    def test_markdown_renders(self) -> None:
        profile = build_profile_from_text([("a.md", CONVERSATIONAL)])
        md = profile.as_markdown()
        assert "# Writing Voice Profile" in md
        assert "Advisory profile" in md
        assert "How to use this profile" in md

    def test_empty_corpus(self) -> None:
        profile = build_profile_from_text([])
        assert profile.files_analyzed == 0
        assert profile.tone == "unknown"


class TestDirectoryInput:
    def test_missing_directory_actionable(self) -> None:
        with pytest.raises(ArticleParseError, match="not a directory"):
            build_profile_from_directory("/nonexistent/path/xyz")

    def test_empty_directory_actionable(self, tmp_path) -> None:
        with pytest.raises(ArticleParseError, match="No markdown files"):
            build_profile_from_directory(tmp_path)

    def test_analyzes_valid_files(self, tmp_path) -> None:
        (tmp_path / "one.md").write_text(CONVERSATIONAL, encoding="utf-8")
        (tmp_path / "two.md").write_text(FORMAL, encoding="utf-8")
        profile, parsed, skipped = build_profile_from_directory(tmp_path)
        assert profile.files_analyzed == 2
        assert len(parsed) == 2
        assert skipped == []

    def test_skips_unreadable_files(self, tmp_path) -> None:
        (tmp_path / "good.md").write_text(CONVERSATIONAL, encoding="utf-8")
        (tmp_path / "bad.md").write_bytes(b"\xff\xfe\x00binary")
        profile, _parsed, skipped = build_profile_from_directory(tmp_path)
        assert profile.files_analyzed == 1
        assert len(skipped) == 1 and "bad.md" in skipped[0]
