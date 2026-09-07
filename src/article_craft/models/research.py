"""Research models: sources, claims, and verification status.

These models back the fact-check and research workflows. See
``skills/article-craft/references/research/`` for the method.
"""

from __future__ import annotations

from datetime import date
from enum import Enum, StrEnum

from pydantic import BaseModel, Field

# Ordered by descending authority; see references/research/source-hierarchy.md.
SOURCE_TIERS: dict[int, str] = {
    1: "Official documentation, standards, primary research, academic papers",
    2: "Engineering blogs of relevant organizations, reputable technical documentation, professional editorial bodies",
    3: "Established writers, well-regarded community resources",
    4: "Forums, Reddit, Stack Overflow, GitHub issues",
    5: "Random blogs, SEO farms, AI-generated summary sites",
}


class SourceTier(int, Enum):
    OFFICIAL = 1
    PROFESSIONAL = 2
    COMMUNITY = 3
    FORUM = 4
    LOW = 5


class ClaimStatus(StrEnum):
    VERIFIED = "VERIFIED"
    LIKELY = "LIKELY"
    UNVERIFIED = "UNVERIFIED"
    CONTRADICTED = "CONTRADICTED"
    OPINION = "OPINION"
    ASSUMPTION = "ASSUMPTION"


class Source(BaseModel):
    """A research source with authority metadata. Never invent these."""

    title: str
    url: str | None = None
    tier: SourceTier = SourceTier.OFFICIAL
    author: str | None = None
    publisher: str | None = None
    date_published: date | None = None
    date_accessed: date | None = None
    notes: str | None = None


class Claim(BaseModel):
    """A single factual assertion extracted from an article."""

    text: str
    status: ClaimStatus = ClaimStatus.UNVERIFIED
    section_title: str | None = None
    source_index: int | None = None  # index into the research doc's sources
    reason: str | None = None  # why this classification; required for non-UNVERIFIED
    verification_note: str | None = None


class ClaimConflict(BaseModel):
    """Two sources making conflicting claims about the same fact.

    ``resolution`` names which claim the source hierarchy favors (higher
    authority wins per references/research/source-hierarchy.md); when tiers
    tie, resolution stays None and the conflict is surfaced to the author
    instead of silently decided.
    """

    topic: str
    claim_a: str
    claim_b: str
    source_a: int | None = None  # index into ResearchDoc.sources
    source_b: int | None = None
    resolution: str | None = None  # "a", "b", or None when unresolved
    resolution_reason: str | None = None


class ResearchDoc(BaseModel):
    """The research artifact. Stays separate from the final article."""

    thesis: str | None = None
    research_questions: list[str] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    conflicts: list[ClaimConflict] = Field(default_factory=list)
    statistics: list[str] = Field(default_factory=list)
    claims_requiring_verification: list[str] = Field(default_factory=list)
    potential_examples: list[str] = Field(default_factory=list)

    def summary(self) -> str:
        counts: dict[str, int] = {}
        for claim in self.claims:
            counts[claim.status.value] = counts.get(claim.status.value, 0) + 1
        parts = [f"{v} {k}" for k, v in sorted(counts.items())]
        return "; ".join(parts) if parts else "no claims classified"
