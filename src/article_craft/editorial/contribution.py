"""Human contribution detection (spec §19).

Determines what the *author* personally contributed to the article — from
evidence in the article itself. Article Craft never invents personal
experiences; it can only detect their presence and suggest where the author
might add their own.
"""

from __future__ import annotations

import re

from article_craft.editorial.types import ArticleTypeSpec, get_article_type
from article_craft.models.article import Article
from article_craft.models.review import HumanContribution

# (kind, pattern). Each match is evidence of a distinctive author contribution.
_CONTRIBUTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "personal experience",
        re.compile(
            r"\b(i (built|migrated|deployed|hit|ran|broke|fixed|spent|learned|watched|"
            r"noticed|struggled|tried|rewrote|shipped|measured)|we (built|migrated|"
            r"deployed|hit|ran|broke|fixed|learned|noticed|struggled|tried|shipped|"
            r"measured)|in my experience|when i |when we |at my (job|company|work)|"
            r"on my team|in production,? we)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "experiment",
        re.compile(
            r"\b(i (benchmarked|profiled|tested|measured|compared)|we (benchmarked|"
            r"profiled|tested|measured|compared)|my benchmark|our benchmark|"
            r"i ran (a|the) (test|benchmark|experiment)|p(50|95|99) (of|was|for our))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "implementation",
        re.compile(
            r"\b(i (wrote|implemented|open-?sourced|published) (the|a|my)|my implementation|"
            r"the code i wrote|you can find (the|my) (code|source) (at|here|on github))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "unique observation",
        re.compile(
            r"\b(i noticed|what surprised me|the strange part|the interesting part|"
            r"what (most|nobody|nearly everyone) (miss|misses|get wrong|gets wrong)|"
            r"counterintuitively|the non-?obvious part)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "original example",
        re.compile(
            r"\b(let'?s (say|imagine) (our|we|my)|consider (a|an) (service|system|app) i |"
            r"a (real|actual) (example|case) from my|i'?ll use (the )?example of my)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "architecture/design decision",
        re.compile(
            r"\b(i (chose|decided|designed|rejected)|we (chose|decided|designed|rejected)|"
            r"our (decision|trade-?off|architecture)|i argued (for|against))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "opinion",
        re.compile(
            r"\b(i (think|believe|argue|would argue|'m convinced)|in my opinion|"
            r"my (take|position|view|hypothesis)|i disagree|i would push back)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "lesson learned",
        re.compile(
            r"\b(the lesson (i|we) learned|what i'?d do differently|if i (started|did) (it )?"
            r"again|my biggest mistake|the hard way|i was wrong about)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "comparison",
        re.compile(
            r"\b(i compared|we compared|my comparison|when i switched (from|to)|"
            r"i (moved|migrated) from)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "research synthesis",
        re.compile(
            r"\b(i read|i dug through|after reading (the|a|several|five)|i spent (hours|days|weeks) reading|"
            r"i went through (the|the entire))\b",
            re.IGNORECASE,
        ),
    ),
]


def detect_human_contribution(article: Article) -> HumanContribution:
    """Detect author contribution from the article text itself."""
    prose = "\n".join(s.body for s in article.sections)
    found_kinds: list[str] = []
    evidence: list[str] = []
    for kind, pattern in _CONTRIBUTION_PATTERNS:
        matches = pattern.findall(prose)
        if matches:
            found_kinds.append(kind)
            first = matches[0] if isinstance(matches[0], str) else matches[0][0]
            evidence.append(f'{kind}: e.g. "{first}"')
    present = bool(found_kinds)
    summary = (
        f"Detected author contribution: {', '.join(found_kinds)}."
        if present
        else "No distinctive author contribution detected."
    )
    suggestions: list[str] = (
        []
        if present
        else [
            "Add what YOU experienced: a specific moment this topic bit you (build, incident, migration, benchmark).",
            "Include a result only you could have: a number you measured, a screenshot of your run, your repo.",
            "State your position and what would change your mind.",
            "Describe the alternative you rejected and why.",
        ]
    )
    return HumanContribution(
        present=present,
        kinds=found_kinds,
        summary=summary + (" Evidence: " + "; ".join(evidence[:4]) if evidence else ""),
        suggestions=suggestions,
    )


def contribution_is_sufficient(
    contribution: HumanContribution, spec: ArticleTypeSpec | None
) -> bool:
    """Whether the detected contribution meets the type's expectations."""
    if contribution.present:
        return True
    if spec and spec.expects_first_person:
        return False
    # Even for impersonal types, some contribution is expected per spec §19.
    return False


def missing_contribution_warning(article: Article) -> str | None:
    """The standard warning text when a distinctive contribution is absent."""
    contribution = detect_human_contribution(article)
    spec = get_article_type(article.effective_article_type)
    if contribution_is_sufficient(contribution, spec):
        return None
    return (
        "This article currently lacks a distinctive author contribution. "
        "Readers (and Medium's distribution guidelines) look for first-hand "
        "experience, original examples, or a defensible position. "
        + " ".join(contribution.suggestions[:2])
    )
