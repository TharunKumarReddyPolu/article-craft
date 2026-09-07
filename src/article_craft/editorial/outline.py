"""Outline builder: idea + audience + type -> an editorial outline.

The outline is advice (HEURISTIC), grounded in the article-type registry and
the Medium distribution guidelines' emphasis on reader value. It never writes
the article.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from article_craft.editorial.types import ArticleTypeSpec, get_article_type


@dataclass
class OutlineSection:
    title: str
    question_it_answers: str
    purpose: str
    target_words: int

    def to_markdown(self) -> str:
        return (
            f"### {self.title}\n"
            f"- **Answers:** {self.question_it_answers}\n"
            f"- **Purpose:** {self.purpose}\n"
            f"- **Target length:** ~{self.target_words} words"
        )


@dataclass
class Outline:
    reader_promise: str
    thesis: str
    angle: str
    article_type: str
    audience: str
    sections: list[OutlineSection] = field(default_factory=list)
    research_questions: list[str] = field(default_factory=list)
    potential_sources: list[str] = field(default_factory=list)
    author_contribution_prompts: list[str] = field(default_factory=list)

    @property
    def total_target_words(self) -> int:
        return sum(s.target_words for s in self.sections)

    def to_markdown(self) -> str:
        lines = [
            "# Editorial outline",
            "",
            f"- **Article type:** {self.article_type}",
            f"- **Audience:** {self.audience}",
            "",
            "## Reader promise",
            "",
            self.reader_promise,
            "",
            "## Thesis",
            "",
            self.thesis,
            "",
            "## Angle",
            "",
            self.angle,
            "",
            "## Structure",
            "",
        ]
        for i, section in enumerate(self.sections, start=1):
            lines.append(f"{i}. {section.to_markdown()}")
            lines.append("")
        if self.research_questions:
            lines += ["## Research questions", ""]
            lines += [f"- {q}" for q in self.research_questions]
            lines.append("")
        if self.potential_sources:
            lines += ["## Potential source types to look for", ""]
            lines += [f"- {s}" for s in self.potential_sources]
            lines.append("")
        if self.author_contribution_prompts:
            lines += ["## Your contribution (required)", ""]
            lines += [f"- {p}" for p in self.author_contribution_prompts]
            lines.append("")
        return "\n".join(lines)


def build_outline(
    idea: str,
    audience: str,
    article_type: str,
    unique_angle: str | None = None,
    target_length_words: int | None = None,
) -> Outline:
    spec = get_article_type(article_type) or _default_spec()
    angle = unique_angle or f"a practitioner's honest walkthrough of {idea.strip()}"

    # Distribute the target length across the type's structure.
    total = target_length_words or (spec.min_reasonable_words + spec.max_reasonable_words) // 2
    n = len(spec.structure)
    weights = [1.2, 1.0, 1.0, 0.8][:n] + [1.0] * max(0, n - 4)
    weight_sum = sum(weights[:n])
    targets = [int(total * w / weight_sum) for w in weights[:n]]

    sections = [
        OutlineSection(
            title=stage,
            question_it_answers=q,
            purpose=_purpose_for_stage(stage, spec),
            target_words=target,
        )
        for stage, q, target in zip(
            spec.structure,
            _questions_for_stages(spec),
            targets,
            strict=False,
        )
    ]

    return Outline(
        reader_promise=f"After reading, a {audience} will be able to "
        f"{spec.purpose.split('Reader ', 1)[-1].rstrip('.').lower()} — specifically about {idea.strip()}.",
        thesis=_thesis_for(idea, angle, spec),
        angle=angle,
        article_type=spec.type_id,
        audience=audience,
        sections=sections,
        research_questions=_research_questions_for(idea, spec),
        potential_sources=_sources_for(spec),
        author_contribution_prompts=[
            "What did YOU observe about " + idea.strip() + " that a doc reader wouldn't?",
            "What did you measure, build, break, or decide?",
            "What did you get wrong first?",
        ],
    )


def _default_spec() -> ArticleTypeSpec:
    return get_article_type("technical-explainer")  # type: ignore[return-value]


def _purpose_for_stage(stage: str, spec: ArticleTypeSpec) -> str:
    stage_lower = stage.lower()
    if "prerequisite" in stage_lower or "build" in stage_lower:
        return "Set the promise and scope; state assumptions."
    if "step" in stage_lower or "instruction" in stage_lower:
        return "Deliver the procedure with verification points."
    if "mental model" in stage_lower:
        return "Give the reader the correct intuition before mechanisms."
    if "failure" in stage_lower or "error" in stage_lower:
        return "Cover the failure modes readers will actually hit."
    if "trade-off" in stage_lower or "reject" in stage_lower:
        return "Honest accounting of costs and alternatives."
    if "lesson" in stage_lower or "next" in stage_lower:
        return "Consolidate and point onward. No new claims."
    return spec.purpose


def _questions_for_stages(spec: ArticleTypeSpec) -> list[str]:
    qs = list(spec.questions)
    while len(qs) < len(spec.structure):
        qs.append("What does the reader need here to keep following?")
    return qs[: len(spec.structure)]


def _thesis_for(idea: str, angle: str, spec: ArticleTypeSpec) -> str:
    return (
        f"This article argues/demonstrates that {idea.strip()}, seen through "
        f"{angle}, and leaves the reader with {spec.purpose.lower().rstrip('.')}"
    )


def _research_questions_for(idea: str, spec: ArticleTypeSpec) -> list[str]:
    base = [
        f"What do the official {idea.strip()} docs actually guarantee (vs. what people assume)?",
        "Where is this version-sensitive? What changed in recent releases of the tools involved?",
        f"What are the known failure modes / post-mortems published about {idea.strip()}?",
    ]
    if spec.type_id in ("system-design", "architecture-deep-dive"):
        base.append("What published capacity/latency numbers exist, and under what assumptions?")
    if spec.type_id == "opinion":
        base.append("What is the strongest published counterargument to the thesis?")
    return base


def _sources_for(spec: ArticleTypeSpec) -> list[str]:
    return [
        "Official documentation for every tool named (Tier 1)",
        "Changelogs / release notes for version-specific behavior (Tier 1)",
        "Engineering blogs from the maintainers (Tier 2)",
        "Post-mortems / incident write-ups from practitioners (Tier 2-3)",
    ]
