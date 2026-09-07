"""Future platform adapters — documented stubs only.

V1 implements Medium only. These stubs exist so the architecture's extension
path is visible and testable, without pretending DEV.to / LinkedIn / Substack
checks exist. Each raises NotImplementedError with a pointer to the roadmap.
See docs/roadmap.md for the V2 plan.
"""

from __future__ import annotations

from article_craft.models.article import Article
from article_craft.models.review import DimensionScore, PlatformCheck


class UnimplementedAdapter:
    """Base for adapters that are on the roadmap but deliberately not
    implemented in V1. Raises with an actionable message."""

    platform_id = "unimplemented"
    roadmap_ref = "docs/roadmap.md"

    def _not_implemented(self) -> NotImplementedError:
        return NotImplementedError(
            f"The {self.platform_id} adapter is not implemented in Article Craft "
            f"V1. Only Medium and generic checks are available. See {self.roadmap_ref} "
            "for the plan and CONTRIBUTING.md to add this adapter."
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


class DevToAdapter(UnimplementedAdapter):
    platform_id = "devto"
    """DEV.to adapter (roadmap V2). DEV.to has its own frontmatter contract
    (title, published, tags, cover_image, canonical_url) and a liquid-tag
    embed system — both need research against dev.to's official docs first."""


class LinkedInAdapter(UnimplementedAdapter):
    platform_id = "linkedin"
    """LinkedIn adapter (roadmap V2). LinkedIn articles differ fundamentally
    from blog posts (feed-first, length norms, no markdown) — needs its own
    editorial research before any rules are encoded."""


class SubstackAdapter(UnimplementedAdapter):
    platform_id = "substack"
    """Substack adapter (roadmap V2). Newsletter-specific checks (email
    rendering, subject lines vs. article titles) need official docs research."""


ALL_FUTURE_ADAPTERS: tuple[type[UnimplementedAdapter], ...] = (
    DevToAdapter,
    LinkedInAdapter,
    SubstackAdapter,
)
