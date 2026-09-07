"""Editorial Quality Score assembly.

Weights (spec §17): Reader Value 20, Originality 15, Clarity 15, Structure 10,
Technical Accuracy 15, Evidence 10, Voice/Human Contribution 10,
Platform Compatibility 5. Total 100.

Every deduction requires a written reason — the rubric raises if you try to
deduct points silently. The score is the "Editorial Quality Score"; it never
predicts Medium distribution.
"""

from __future__ import annotations

from article_craft.models.review import (
    DIMENSION_MAX,
    Dimension,
    DimensionScore,
    EditorialScore,
)


def initial_score() -> EditorialScore:
    """Start at full marks and deduct with reasons."""
    return EditorialScore(
        total=100,
        dimensions=[
            DimensionScore(dimension=dim, score=max_points)
            for dim, max_points in DIMENSION_MAX.items()
        ],
    )


def deduct(
    score: EditorialScore,
    dimension: Dimension,
    points: int,
    reason: str,
    strength: str | None = None,
    problem: str | None = None,
    recommendation: str | None = None,
) -> None:
    """Deduct points from a dimension. `reason` is mandatory and appears in
    the report so the author sees exactly why points were lost."""
    if points <= 0:
        raise ValueError("deduct() requires points > 0")
    if not reason or not reason.strip():
        raise ValueError(
            f"deduct({dimension}) requires a non-empty reason — never produce unexplained scores"
        )
    entry = score.dimension(dimension)
    entry.score = max(0, entry.score - points)
    entry.reasons.append(f"-{points}: {reason}")
    if strength:
        entry.strengths.append(strength)
    if problem:
        entry.problems.append(problem)
    if recommendation:
        entry.recommendations.append(recommendation)


def credit_strength(
    score: EditorialScore,
    dimension: Dimension,
    strength: str,
    recommendation: str | None = None,
) -> None:
    """Record a strength without changing the score."""
    entry = score.dimension(dimension)
    entry.strengths.append(strength)
    if recommendation:
        entry.recommendations.append(recommendation)


def finalize(score: EditorialScore) -> EditorialScore:
    """Recompute the total from the dimension scores."""
    score.total = sum(d.score for d in score.dimensions)
    return score
