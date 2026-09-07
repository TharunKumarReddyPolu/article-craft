"""Future platform adapters — documented stubs only.

V2 implements Medium, DEV.to, Hashnode, Substack, and LinkedIn. This module
keeps the honest-stub pattern visible for the next platform (Ghost) so the
extension path stays tested without pretending checks exist.
See docs/roadmap.md for the plan.
"""

from __future__ import annotations

from article_craft.models.article import Article
from article_craft.models.review import DimensionScore, PlatformCheck


class UnimplementedAdapter:
    """Base for adapters that are on the roadmap but deliberately not
    implemented. Raises with an actionable message."""

    platform_id = "unimplemented"
    roadmap_ref = "docs/roadmap.md"

    def _not_implemented(self) -> NotImplementedError:
        return NotImplementedError(
            f"The {self.platform_id} adapter is not implemented in Article Craft. "
            f"Available platforms: medium, devto, hashnode, substack, linkedin. "
            f"See {self.roadmap_ref} for the plan and CONTRIBUTING.md to add "
            "this adapter."
        )

    def validate_article(self, article: Article) -> list[str]:
        raise self._not_implemented()

    def review_title(self, article: Article) -> list[PlatformCheck]:
        raise self._not_implemented()

    def review_structure(self, article: Article) -> list[PlatformCheck]:
        raise self._not_implemented()

    def review_formatting(self, article: Article) -> list[PlatformCheck]:
        raise self._not_implemented()

    def review_policy(self, article: Article) -> list[PlatformCheck]:
        raise self._not_implemented()

    def review_distribution(self, article: Article) -> list[PlatformCheck]:
        raise self._not_implemented()

    def generate_platform_checklist(self, article: Article) -> list[str]:
        raise self._not_implemented()

    def platform_compatibility_score(self, article: Article) -> DimensionScore:
        raise self._not_implemented()


class GhostAdapter(UnimplementedAdapter):
    platform_id = "ghost"
    """Ghost adapter (roadmap V3). Ghost is markdown-native; likely the
    easiest port once the adapter pattern has been proven five times."""


ALL_FUTURE_ADAPTERS: tuple[type[UnimplementedAdapter], ...] = (GhostAdapter,)
