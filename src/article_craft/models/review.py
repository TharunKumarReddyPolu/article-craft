"""Review models: issues, the Editorial Quality Score, and platform checks.

Every score deduction carries a written reason (spec: "Never produce
unexplained scores"). The score is called the **Editorial Quality Score** and
never claims to predict Medium distribution.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(StrEnum):
    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class RuleClass(StrEnum):
    """Where a rule comes from. Mirrors the knowledge classification used in
    skills/article-craft/references/."""

    POLICY = "POLICY"  # official platform policy (e.g., Medium Rules)
    RECOMMENDATION = "RECOMMENDATION"  # official-sourced advice
    HEURISTIC = "HEURISTIC"  # Article Craft editorial judgment
    BEST_PRACTICE = "BEST_PRACTICE"  # industry craft standard


class Dimension(StrEnum):
    READER_VALUE = "Reader Value"
    ORIGINALITY = "Originality"
    CLARITY = "Clarity"
    STRUCTURE = "Structure"
    TECHNICAL_ACCURACY = "Technical Accuracy"
    EVIDENCE = "Evidence"
    VOICE = "Author Voice/Human Contribution"
    PLATFORM_COMPATIBILITY = "Platform Compatibility"


# Maximum points per dimension (spec §17). Total = 100.
DIMENSION_MAX: dict[Dimension, int] = {
    Dimension.READER_VALUE: 20,
    Dimension.ORIGINALITY: 15,
    Dimension.CLARITY: 15,
    Dimension.STRUCTURE: 10,
    Dimension.TECHNICAL_ACCURACY: 15,
    Dimension.EVIDENCE: 10,
    Dimension.VOICE: 10,
    Dimension.PLATFORM_COMPATIBILITY: 5,
}


class DimensionScore(BaseModel):
    dimension: Dimension
    score: int  # 0..DIMENSION_MAX
    strengths: list[str] = Field(default_factory=list)
    problems: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)  # why points were deducted

    @property
    def max(self) -> int:
        return DIMENSION_MAX[self.dimension]

    @property
    def points_lost(self) -> int:
        return self.max - self.score


class Verdict(StrEnum):
    READY = "READY"
    READY_AFTER_CHANGES = "READY AFTER CHANGES"
    DO_NOT_PUBLISH_YET = "DO NOT PUBLISH YET"


class ReviewIssue(BaseModel):
    dimension: Dimension
    severity: Severity
    title: str
    detail: str
    location: str | None = None  # e.g. "Section 'Why Kafka' (lines 40-58)"
    suggestion: str | None = None
    rule_class: RuleClass = RuleClass.HEURISTIC


class HumanContribution(BaseModel):
    """What the author personally contributed. Never invented; derived from
    what the article itself contains."""

    present: bool = False
    kinds: list[str] = Field(default_factory=list)
    summary: str | None = None
    suggestions: list[str] = Field(default_factory=list)


class PlatformCheckStatus(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    NOT_CHECKED = "NOT CHECKED"
    NOT_APPLICABLE = "NOT APPLICABLE"


class PlatformCheck(BaseModel):
    category: str  # e.g. "Title", "AI Policy", "Canonical Link"
    status: PlatformCheckStatus
    detail: str
    rule_class: RuleClass = RuleClass.POLICY
    source_id: str | None = None  # id in platforms/medium/sources.yaml
    findings: list[str] = Field(default_factory=list)


class PlatformCheckReport(BaseModel):
    platform: str
    overall: PlatformCheckStatus
    checks: list[PlatformCheck] = Field(default_factory=list)
    fix_before_publishing: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "These checks are based on current published guidance and editorial "
        "heuristics. They do not guarantee Medium distribution."
    )

    @property
    def fix_items(self) -> list[str]:
        return self.fix_before_publishing


class EditorialScore(BaseModel):
    total: int
    dimensions: list[DimensionScore] = Field(default_factory=list)

    def dimension(self, name: Dimension) -> DimensionScore:
        for entry in self.dimensions:
            if entry.dimension is name:
                return entry
        raise KeyError(f"missing dimension {name}")


class PublishRecommendation(BaseModel):
    verdict: Verdict
    explanation: str


class ReviewResult(BaseModel):
    """Complete output of the review workflow."""

    article_title: str
    article_path: str | None = None
    article_type: str = "unknown"
    score: EditorialScore
    issues: list[ReviewIssue] = Field(default_factory=list)
    critical_issues: list[ReviewIssue] = Field(default_factory=list)
    recommended_changes: list[str] = Field(default_factory=list)
    human_contribution: HumanContribution = Field(default_factory=HumanContribution)
    platform_report: PlatformCheckReport | None = None
    publish_recommendation: PublishRecommendation

    @property
    def has_critical_issues(self) -> bool:
        return bool(self.critical_issues)


def verdict_for_score(score: EditorialScore, critical_count: int) -> Verdict:
    """Deterministic verdict mapping. Score alone never guarantees anything;
    this is an editorial triage rule (HEURISTIC)."""
    if critical_count > 0:
        return Verdict.DO_NOT_PUBLISH_YET
    if score.total >= 80:
        return Verdict.READY
    if score.total >= 70:
        return Verdict.READY_AFTER_CHANGES
    return Verdict.DO_NOT_PUBLISH_YET
