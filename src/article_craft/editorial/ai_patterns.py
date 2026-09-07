"""Detection of generic AI writing patterns.

These are patterns readers have learned to skim past (and that Medium's
distribution guidelines describe as "generic" content). Detection exists to
make the author's own writing clearer — never to disguise AI usage. See
``skills/article-craft/references/platforms/medium/ai-policy.md``: the
discipline is disclosure, not concealment.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from article_craft.models.article import Article
from article_craft.models.review import RuleClass, Severity


@dataclass(frozen=True)
class PatternHit:
    phrase: str
    line: int
    pattern_name: str


# (pattern_name, compiled regex). Word-boundary anchored, case-insensitive.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "cliche-opener",
        re.compile(
            r"\b(in today's (fast-?paced|ever-?(changing|evolving)) (world|landscape))\b"
            r"|\b(in the (ever-?evolving|rapidly evolving) (landscape|world))\b"
            r"|\b(in the (world|realm) of)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "filler-transition",
        re.compile(
            r"\b(let's (dive|jump|dive right) in\b(!|\.)?|let's get started\b(!|\.)?"
            r"|without further ado|buckle up)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "hedging-filler",
        re.compile(
            r"\b(it('s| is) important to note that|it('s| is) worth noting that"
            r"|needless to say|at the end of the day)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "vague-superlative",
        re.compile(
            r"\b(game-?changer|revolutioni[sz]e|cutting-?edge|seamless(ly)?"
            r"|next-?level|paradigm shift|synerg(y|istic)|unlock the (power|full potential))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "corporate-verb",
        re.compile(
            r"\b(leverage|utili[sz]e|delve (deeper )?into|embark on|navigate the complexities)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "conclusion-filler",
        re.compile(
            r"^(in conclusion|to sum( it)? up|in summary|as we've seen|wrapping up)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "empty-adjective",
        re.compile(
            r"\b(robust|powerful|amazing|incredible|fantastic|massive(ly)?)\b", re.IGNORECASE
        ),
    ),
    (
        "marketing-voice",
        re.compile(
            r"\b(best-?in-?class|world-?class|state-?of-?the-?art|10x (engineer|developer|productivity))\b",
            re.IGNORECASE,
        ),
    ),
]


def find_ai_patterns(text: str) -> list[PatternHit]:
    """Find generic AI-sounding phrases with their line numbers."""
    hits: list[PatternHit] = []
    for line_no, line in enumerate(text.split("\n"), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            continue
        for name, pattern in _PATTERNS:
            for match in pattern.finditer(line):
                hits.append(PatternHit(phrase=match.group(0), line=line_no, pattern_name=name))
    return hits


# Manipulative/conspiracy framing: the rhetoric of misinformation. Medium's
# distribution guidelines disqualify misleading content and unconstructive
# negativity; these patterns also correlate with fabricated claims.
_MANIPULATION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "hidden-truth",
        re.compile(
            r"\b(hidden truth|the (real )?truth about|what (they|the (docs|documentation|vendors?|media)) "
            r"don'?t want you to know|nobody tells you|they'?re hiding)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "conspiracy",
        re.compile(
            r"\b(follow the money|the (big )?(lie|racket|scam|conspiracy)|inside(r|rs) know|"
            r"they don'?t want|suppressed|banned (by|from)|before it gets taken down|"
            r"they'?ll hate (this|me)|cover-?up)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "false-urgency",
        re.compile(
            r"\b(share this (article|before)|before it'?s? (too late|taken down)|"
            r"you'?ve been lied to|everything you know is wrong)\b",
            re.IGNORECASE,
        ),
    ),
]


def find_manipulation_patterns(text: str) -> list[PatternHit]:
    """Find misinformation-style/manipulative rhetoric with line numbers."""
    hits: list[PatternHit] = []
    for line_no, line in enumerate(text.split("\n"), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            continue
        for name, pattern in _MANIPULATION_PATTERNS:
            for match in pattern.finditer(line):
                hits.append(PatternHit(phrase=match.group(0), line=line_no, pattern_name=name))
    return hits


def ai_pattern_density_per_1000(article: Article) -> float:
    """Cliche hits per 1000 prose words."""
    if article.word_count == 0:
        return 0.0
    return len(find_ai_patterns(_prose_of(article))) * 1000.0 / article.word_count


def _prose_of(article: Article) -> str:
    """Article text without code blocks."""
    lines = []
    in_fence = False
    source = "\n".join(s.body for s in article.sections) if article.sections else ""
    for line in source.split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def ai_pattern_issues(article: Article) -> list[dict[str, str]]:
    """Structured findings for the review engine. Returns dicts with
    severity/detail/suggestion; the review engine converts them to issues."""
    hits = find_ai_patterns(_prose_of(article))
    issues: list[dict[str, str]] = []
    if not hits:
        return issues
    density = ai_pattern_density_per_1000(article)
    from collections import Counter

    by_name = Counter(hit.pattern_name for hit in hits)
    worst = by_name.most_common(3)
    severity = Severity.MAJOR if density >= 3 else Severity.MINOR if density >= 1 else Severity.INFO
    examples = ", ".join(f"'{hit.phrase}' (line {hit.line})" for hit in hits[:3])
    issues.append(
        {
            "severity": severity.value,
            "title": f"Generic AI-sounding phrasing detected ({len(hits)} hits, "
            f"{density:.1f} per 1000 words)",
            "detail": f"Most frequent patterns: {', '.join(f'{n} ({c}x)' for n, c in worst)}. "
            f"Examples: {examples}",
            "suggestion": "Replace generic phrasing with your own specifics: concrete "
            "numbers, named tools, what you actually observed. Say it the way you'd "
            "say it to a colleague.",
            "rule_class": RuleClass.HEURISTIC.value,
        }
    )
    return issues
