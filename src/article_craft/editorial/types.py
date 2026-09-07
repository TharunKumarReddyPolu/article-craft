"""Article type registry.

Each type has: purpose, recommended structure, questions the article must
answer, a quality checklist, and common failure modes. The writer-facing
summary lives in ``skills/article-craft/references/editorial/article-types.md``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ArticleTypeSpec:
    type_id: str
    label: str
    purpose: str
    structure: tuple[str, ...]
    questions: tuple[str, ...]
    quality_checklist: tuple[str, ...]
    failure_modes: tuple[str, ...]
    expects_first_person: bool = False
    expects_examples: bool = True
    expects_actionable_steps: bool = False
    min_reasonable_words: int = 500
    max_reasonable_words: int = 3500


_REGISTRY: dict[str, ArticleTypeSpec] = {
    "technical-tutorial": ArticleTypeSpec(
        type_id="technical-tutorial",
        label="Technical tutorial",
        purpose="Reader completes a concrete task by the end.",
        structure=(
            "What you'll build + prerequisites",
            "Step-by-step instructions with verification after each step",
            "Common errors and fixes",
            "What to try next",
        ),
        questions=(
            "What exactly will the reader have built?",
            "What versions/assumptions does every step rely on?",
            "What breaks most often, and what does that look like?",
        ),
        quality_checklist=(
            "Every code sample tested as published",
            "Versions pinned and stated",
            "Each step has a verification ('you should see...')",
            "Failure cases covered",
        ),
        failure_modes=(
            "Untested code",
            "Steps that only work on the author's machine",
            "No verification points",
            "Skipped error handling",
        ),
        expects_actionable_steps=True,
        min_reasonable_words=700,
    ),
    "technical-explainer": ArticleTypeSpec(
        type_id="technical-explainer",
        label="Technical explainer",
        purpose="Reader gains a correct mental model of a concept.",
        structure=(
            "Hook: why this matters now",
            "Mental model before mechanism",
            "Build-up from simple to complete",
            "Worked example",
            "Limits and edge cases",
        ),
        questions=(
            "What misconception does this correct?",
            "What is the one-sentence mental model?",
            "Where does the model break down?",
        ),
        quality_checklist=(
            "Mental model stated explicitly",
            "Concepts introduced one at a time",
            "Concrete example before generalization",
            "Edge cases and limits addressed",
        ),
        failure_modes=(
            "Restating documentation instead of explaining",
            "Jargon without definition",
            "No worked example",
            "No limits discussed",
        ),
    ),
    "system-design": ArticleTypeSpec(
        type_id="system-design",
        label="System design",
        purpose="Reader can reason about (or defend) this architecture.",
        structure=(
            "Functional + non-functional requirements",
            "Constraints and capacity assumptions (explicit!)",
            "High-level architecture",
            "Deep dives: data model, storage, messaging, caching",
            "Consistency, availability, partitioning choices",
            "Failure handling, scaling, observability, security",
            "Trade-offs and rejected alternatives",
        ),
        questions=(
            "What are the explicit capacity assumptions?",
            "What fails first, and what happens then?",
            "What was rejected, and why?",
        ),
        quality_checklist=(
            "Assumptions labeled as assumptions",
            "Failure handling covered",
            "Trade-offs stated on both sides",
            "No fabricated benchmark numbers",
            "Observability addressed",
        ),
        failure_modes=(
            "Buzzword architecture",
            "Capacity numbers with no basis",
            "Happy-path only",
            "Missing trade-offs",
        ),
        min_reasonable_words=900,
        max_reasonable_words=5000,
    ),
    "architecture-deep-dive": ArticleTypeSpec(
        type_id="architecture-deep-dive",
        label="Architecture deep dive",
        purpose="Reader understands why a real system is built this way.",
        structure=(
            "Context and forces at the time",
            "The decision",
            "Rejected alternatives",
            "Consequences (good and bad)",
            "What changed since",
        ),
        questions=(
            "What constraints drove the decision?",
            "What alternatives were rejected?",
            "What would you do differently now?",
        ),
        quality_checklist=(
            "Rejected alternatives documented",
            "Consequences honest, including costs",
            "Decision dated/versioned",
        ),
        failure_modes=(
            "Hindsight bias",
            "No rejected alternatives",
            "Not admitting costs",
        ),
        expects_first_person=True,
        min_reasonable_words=900,
    ),
    "case-study": ArticleTypeSpec(
        type_id="case-study",
        label="Case study",
        purpose="Reader learns reusable lessons from a real project.",
        structure=(
            "Situation",
            "Task",
            "Actions",
            "Results (including what went wrong)",
            "Lessons you'd give another team",
        ),
        questions=(
            "What was the real constraint?",
            "What failed?",
            "What is transferable to the reader?",
        ),
        quality_checklist=(
            "Failures included",
            "Results specific and honest",
            "Lessons reusable",
            "Privacy respected (employers, clients anonymized where needed)",
        ),
        failure_modes=(
            "Cherry-picked results",
            "No failures mentioned",
            "Lessons nobody can reuse",
        ),
        expects_first_person=True,
    ),
    "personal-experience": ArticleTypeSpec(
        type_id="personal-experience",
        label="Personal experience",
        purpose="Reader gains insight (and company) from your story.",
        structure=(
            "Scene-setting with stakes",
            "What happened (complication first)",
            "What it meant",
            "What changed for you",
        ),
        questions=(
            "Why will a stranger care?",
            "What did you get wrong before you got it right?",
            "What is the transferable takeaway?",
        ),
        quality_checklist=(
            "Real events only — never manufactured",
            "Specificity beats drama",
            "Takeaway present",
            "You are a character, not (only) a hero",
        ),
        failure_modes=(
            "Diary without takeaway",
            "Manufactured drama",
            "No relevance to the reader",
        ),
        expects_first_person=True,
    ),
    "opinion": ArticleTypeSpec(
        type_id="opinion",
        label="Opinion",
        purpose="Reader gains a defensible position worth debating.",
        structure=(
            "Position stated up front",
            "Strongest evidence",
            "Strongest counterargument (steel-manned)",
            "Your response",
            "What would change your mind",
        ),
        questions=(
            "What is the falsifiable claim?",
            "What is the best argument against you?",
            "What evidence would change your mind?",
        ),
        quality_checklist=(
            "Position stated in the first 150 words",
            "Counterargument addressed honestly",
            "Evidence for the position",
            "No strawmanning",
        ),
        failure_modes=(
            "Evidence-free assertion",
            "Strawman counterargument",
            "Rage-bait framing (distribution poison)",
        ),
        expects_first_person=True,
    ),
    "beginner-guide": ArticleTypeSpec(
        type_id="beginner-guide",
        label="Beginner guide",
        purpose="Beginner reaches first real competence, fast.",
        structure=(
            "Who this is for + what you'll have at the end",
            "The 3-5 concepts that matter",
            "First success within the first third",
            "Progressive depth",
            "Where to go next",
        ),
        questions=(
            "What prerequisite knowledge is assumed?",
            "Where does the reader get their first win?",
            "What should they learn next?",
        ),
        quality_checklist=(
            "Assumed knowledge stated",
            "First success early",
            "Acronyms defined on first use",
            "Cover less, cover it well",
        ),
        failure_modes=(
            "Assuming prerequisite knowledge",
            "Wall of text",
            "Trying to cover everything",
        ),
        expects_actionable_steps=True,
    ),
    "advanced-guide": ArticleTypeSpec(
        type_id="advanced-guide",
        label="Advanced guide",
        purpose="Practitioner levels up on something most skip.",
        structure=(
            "Assumed knowledge stated precisely",
            "The gap most practitioners have",
            "The technique, with why it works",
            "When NOT to use it",
        ),
        questions=(
            "What does the reader already know?",
            "What's the non-obvious insight?",
            "When is this the wrong tool?",
        ),
        quality_checklist=(
            "Baseline stated",
            "Non-obvious insight present (not a basics recap)",
            "Failure modes and anti-use-cases covered",
        ),
        failure_modes=(
            "Rehashing basics",
            "No baseline stated",
            "No failure modes",
        ),
    ),
    "listicle": ArticleTypeSpec(
        type_id="listicle",
        label="Listicle",
        purpose="Reader gets scannable, genuinely distinct items.",
        structure=(
            "Framing: what qualifies an item for this list",
            "Items, each with substance (why it matters, when it doesn't)",
            "Honest closer",
        ),
        questions=(
            "What is the selection criterion?",
            "Does each item earn its place?",
            "Is the number real or padding?",
        ),
        quality_checklist=(
            "Selection criterion stated",
            "Each item distinct and substantive",
            "No ad items",
            "Number not padded",
        ),
        failure_modes=(
            "Padding to hit a number",
            "Items that are ads",
            "No selection criteria",
        ),
    ),
}


def get_article_type(type_id: str | None) -> ArticleTypeSpec | None:
    if not type_id:
        return None
    return _REGISTRY.get(type_id.strip().lower())


def all_article_types() -> list[ArticleTypeSpec]:
    return list(_REGISTRY.values())


def type_ids() -> list[str]:
    return list(_REGISTRY.keys())


def classify_article(article: object) -> str | None:
    """Heuristic classification from the article's own signals when
    frontmatter doesn't declare a type. Returns a type_id or None."""
    from article_craft.models.article import Article  # local import: typing only

    if not isinstance(article, Article):
        return None
    text = "\n".join(s.body for s in article.sections).lower()
    if not text.strip():
        return None
    scores: dict[str, int] = {}
    step_markers = len(
        re.findall(
            r"\b(step \d|first,|second,|next,|then,|finally,|run the following|"
            r"install |create a new |open (a|the) terminal)\b",
            text,
        )
    )
    if step_markers >= 3 or (article.code_blocks and len(article.code_blocks) >= 3):
        scores["technical-tutorial"] = step_markers + 3 * len(article.code_blocks)
    if explainer_markers := re.findall(
        r"\b(what is|how does|how do|why does|the difference between|"
        r"explained|understanding|mental model)\b",
        text,
    ):
        scores["technical-explainer"] = len(explainer_markers)
    if design_markers := re.findall(
        r"\b(requirements|trade-?offs?|scal(e|ing|ability)|availability|"
        r"consistency|partition|throughput|latency|capacity|bottleneck)\b",
        text,
    ):
        scores["system-design"] = len(design_markers)
    first_person = len(re.findall(r"\b(i|we|my|our)\b", text))
    lesson_markers = len(re.findall(r"\b(lesson|learned the hard way|in retrospect)\b", text))
    if first_person > 10 and lesson_markers >= 1:
        scores["case-study"] = first_person + lesson_markers * 5
    opinion_markers = len(
        re.findall(
            r"\b(i (think|believe|argue)|in my opinion|wrong about|overrated|underrated)\b", text
        )
    )
    if opinion_markers >= 2:
        scores["opinion"] = opinion_markers * 5
    listicle_markers = len(re.findall(r"^\s*#{2,3}\s+\d+[\.\)]\s", text, re.MULTILINE))
    if listicle_markers >= 3:
        scores["listicle"] = listicle_markers * 5
    if not scores:
        return None
    best = max(scores.items(), key=lambda kv: kv[1])
    return best[0] if best[1] >= 3 else None
