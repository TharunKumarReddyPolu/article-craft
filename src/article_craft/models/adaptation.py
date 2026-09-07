"""Adaptation and export models.

The canonical article stays primary: a :class:`SocialPost` or a
:class:`PlatformExport` is always derived *from* an Article, carries
attribution back to it, and is never published automatically. Export prep
writes files locally only (zero network calls).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SocialPlatform = Literal["linkedin", "generic"]


class SocialPost(BaseModel):
    """A social adaptation derived from the canonical article.

    Guardrails (enforced by the adaptation engine, not just convention):
    ``text`` must attribute the article, and the engine never fabricates
    claims — every factual statement traces to the source article.
    """

    platform: SocialPlatform = "generic"
    text: str
    hook: str | None = None
    key_insight: str | None = None
    attribution: str  # e.g. "From my article: <title> (<url>)"
    source_title: str | None = None
    source_url: str | None = None
    hashtags: list[str] = Field(default_factory=list)
    char_count: int = 0

    @property
    def over_limit(self) -> bool:
        # LinkedIn's hard feed-post limit is 3000 characters (official
        # help documentation; enforced client-side). Generic posts get the
        # same ceiling as a conservative default.
        return self.char_count > 3000


class PlatformExport(BaseModel):
    """The result of export prep: a platform-ready file written locally.

    ``warnings`` collects everything that could not be converted
    deterministically (unsupported syntax, unknown liquid tags, missing
    metadata the author must supply). Export never sets ``published: true``.
    """

    platform: str
    output_path: str
    frontmatter: dict[str, object] = Field(default_factory=dict)
    body_path: str | None = None  # for adapters whose shape differs (LinkedIn)
    warnings: list[str] = Field(default_factory=list)
    is_republish: bool = False
    canonical_url: str | None = None
