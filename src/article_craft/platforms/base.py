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

from typing import Protocol, runtime_checkable

from article_craft.models.article import Article
from article_craft.models.review import (
    DimensionScore,
    PlatformCheck,
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


def get_adapter(platform_id: str) -> type | None:
    return _ADAPTERS.get(platform_id)


def available_platforms() -> list[str]:
    return sorted(_ADAPTERS)
