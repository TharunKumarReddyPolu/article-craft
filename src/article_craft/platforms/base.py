"""Platform adapter abstraction.

A small Protocol (spec: "Do NOT over-engineer this"). The editorial core
never imports a concrete adapter; adapters implement this protocol and are
selected by platform id.

Contract:
- Return ``PlatformCheck`` items with a category, status, and detail.
- Tag every check with its ``RuleClass``: POLICY (official platform policy),
  RECOMMENDATION (official-sourced advice), or HEURISTIC (Article Craft's
  editorial judgment).
- Cite the official source via ``source_id`` when the check enforces a
  documented policy (ids live in the platform's sources.yaml).
- Never claim to predict distribution, ranking, or reach.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

import yaml

from article_craft.models.article import Article
from article_craft.models.review import (
    DimensionScore,
    PlatformCheck,
    PlatformCheckReport,
    PlatformCheckStatus,
)


@runtime_checkable
class PlatformAdapter(Protocol):
    """The platform adapter interface. Implement only what you can honestly
    check; use NOT CHECKED / NOT APPLICABLE statuses rather than guessing."""

    platform_id: str  # e.g. "medium"

    def validate_article(self, article: Article) -> list[str]:
        """Fatal problems that make publishing on this platform wrong or
        impossible (e.g., unknown required metadata). Empty list = OK."""
        ...

    def review_title(self, article: Article) -> list[PlatformCheck]:
        """Title/subtitle checks."""
        ...

    def review_structure(self, article: Article) -> list[PlatformCheck]:
        """Section/format structural checks specific to the platform."""
        ...

    def review_formatting(self, article: Article) -> list[PlatformCheck]:
        """Markdown-level formatting checks for the platform's editor."""
        ...

    def review_policy(self, article: Article) -> list[PlatformCheck]:
        """Policy checks: AI disclosure, plagiarism/duplicate content, spam,
        affiliate disclosure, copyright signals."""
        ...

    def review_distribution(self, article: Article) -> list[PlatformCheck]:
        """Distribution-guideline risk checks. Advisory only; never predicts
        outcomes."""
        ...

    def generate_platform_checklist(self, article: Article) -> list[str]:
        """Platform-specific checklist items for the author's final pass."""
        ...

    def platform_compatibility_score(self, article: Article) -> DimensionScore:
        """The Platform Compatibility dimension (max 5) of the Editorial
        Quality Score, with reasons for any deduction."""
        ...


_ADAPTERS: dict[str, type] = {}  # platform_id -> adapter class (registered)


def register_adapter(cls: type) -> type:
    """Register an adapter class under its platform_id."""
    platform_id = getattr(cls, "platform_id", None)
    if not platform_id:
        raise ValueError("adapter class must define a platform_id class attribute")
    _ADAPTERS[platform_id] = cls
    return cls


def get_adapter(platform_id: str) -> type[SourcesBackedAdapter] | None:
    """Return a registered adapter class, or None if unknown."""
    return _ADAPTERS.get(platform_id)


def available_platforms() -> list[str]:
    return sorted(_ADAPTERS)


class SourcesBackedAdapter:
    """Shared plumbing for adapters whose rules live in a per-platform
    ``sources.yaml``. Subclasses set ``_sources_path``; ``full_report``
    aggregates checks, computes the overall status, collects fixes, and
    refuses to emit a check citing an unknown source id (the honesty guard
    against drifting from documented sources).
    """

    platform_id = "unset"
    _sources_path: Path

    # -- review hooks (declared to satisfy the PlatformAdapter protocol) -- #

    def validate_article(self, article: Article) -> list[str]:
        """Fatal problems making publishing here wrong or impossible."""
        raise NotImplementedError

    def review_title(self, article: Article) -> list[PlatformCheck]:
        """Title/subtitle checks."""
        raise NotImplementedError

    def review_structure(self, article: Article) -> list[PlatformCheck]:
        """Section/structure checks specific to the platform."""
        raise NotImplementedError

    def review_formatting(self, article: Article) -> list[PlatformCheck]:
        """Markdown-level formatting checks for the platform's editor."""
        raise NotImplementedError

    def review_policy(self, article: Article) -> list[PlatformCheck]:
        """Policy checks (AI disclosure, plagiarism, spam, disclosure)."""
        raise NotImplementedError

    def review_distribution(self, article: Article) -> list[PlatformCheck]:
        """Distribution-guideline risk checks. Advisory only."""
        raise NotImplementedError

    def generate_platform_checklist(self, article: Article) -> list[str]:
        """Platform-specific checklist items for the author's final pass."""
        raise NotImplementedError

    def platform_compatibility_score(self, article: Article) -> DimensionScore:
        """The Platform Compatibility dimension (max 5) with reasons."""
        raise NotImplementedError

    # -- shared machinery -- #

    def _known_source_ids(self) -> frozenset[str]:
        try:
            data = yaml.safe_load(self._sources_path.read_text(encoding="utf-8"))
            return frozenset(entry["id"] for entry in data.get("sources", []))
        except (OSError, yaml.YAMLError):
            return frozenset()

    def full_report(
        self,
        article: Article,
        extra_checks: list[PlatformCheck] | None = None,
        disclaimer: str | None = None,
        **kwargs: object,
    ) -> PlatformCheckReport:
        """Aggregate all review hooks into one report.

        ``**kwargs`` lets subclasses extend the signature (e.g. LinkedIn's
        ``post=``) while keeping a uniform call surface for the CLI/MCP.
        """
        checks = (
            self.review_title(article)
            + self.review_structure(article)
            + self.review_formatting(article)
            + self.review_policy(article)
            + self.review_distribution(article)
            + (extra_checks or [])
        )
        if any(c.status is PlatformCheckStatus.ERROR for c in checks):
            overall = PlatformCheckStatus.ERROR
        elif any(c.status is PlatformCheckStatus.WARNING for c in checks):
            overall = PlatformCheckStatus.WARNING
        else:
            overall = PlatformCheckStatus.PASS
        fixes = [
            f"{c.category}: {c.detail}"
            for c in checks
            if c.status in (PlatformCheckStatus.ERROR, PlatformCheckStatus.WARNING)
        ]
        known = self._known_source_ids()
        for check in checks:
            if check.source_id and known and check.source_id not in known:
                raise ValueError(
                    f"Adapter cites unknown source_id '{check.source_id}' — add it "
                    f"to skills/article-craft/references/platforms/{self.platform_id}/sources.yaml"
                )
        report = PlatformCheckReport(
            platform=self.platform_id,
            overall=overall,
            checks=checks,
            fix_before_publishing=fixes,
        )
        if disclaimer is not None:
            report.disclaimer = disclaimer
        return report
