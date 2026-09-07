"""The title system: title/subtitle analysis and candidate generation.

Official grounding: Medium's Distribution Guidelines disqualify titles and
subtitles that are "sensationalistic" or "overly generic, mysterious, or
formulaic" (see skills/article-craft/references/platforms/medium/titles.md).
Article Craft never recommends a title that misrepresents the article.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from article_craft.models.review import RuleClass, Severity

CLICKBAIT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("all-caps-shouting", re.compile(r"\b[A-Z]{4,}\b")),
    (
        "you-wont-believe",
        re.compile(r"you won'?t believe|shocking(ly)?|jaw-?dropping", re.IGNORECASE),
    ),
    (
        "miracle-claim",
        re.compile(
            r"\b(secret|hack(s|ed)?) (that|to)\b|one (weird|simple) trick|this one trick",
            re.IGNORECASE,
        ),
    ),
    ("death-urgency", re.compile(r"\b(die|dying|killing|destroy(s|ed|ing)?)\b", re.IGNORECASE)),
    (
        "number-hype",
        re.compile(r"^\d+ (shocking|insane|crazy|mind-?blowing|amazing)", re.IGNORECASE),
    ),
    ("insanity", re.compile(r"\b(insane(ly)?|crazy(ly)?|wild(ly)?)\b", re.IGNORECASE)),
    (
        "nobody-talks",
        re.compile(r"nobody (is )?talking about|they don'?t want you to know", re.IGNORECASE),
    ),
]

GENERIC_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("everything-you-need", re.compile(r"^(everything )?you need to know about", re.IGNORECASE)),
    ("thoughts-on", re.compile(r"^(some )?thoughts on\b", re.IGNORECASE)),
    ("ultimate-guide", re.compile(r"^the (ultimate|complete|definitive) guide", re.IGNORECASE)),
    (
        "vague-noun",
        re.compile(r"^(a look at|an overview of|exploring|understanding) ", re.IGNORECASE),
    ),
    ("part-of-series", re.compile(r"^part \d+\b", re.IGNORECASE)),
]

SUPPORTED_SUPERLATIVES = re.compile(
    r"\b(fastest|best|worst|simplest|most (efficient|scalable|secure)|always|never|everyone|nobody)\b",
    re.IGNORECASE,
)


@dataclass
class TitleAnalysis:
    title: str | None
    issues: list[dict[str, str]] = field(default_factory=list)
    clickbait_risk: str = "low"  # low | medium | high
    clarity: str = "good"  # good | vague | unknown

    @property
    def length(self) -> int:
        return len(self.title or "")


def analyze_subtitle(subtitle: str | None) -> list[dict[str, str]]:
    """Analyze a subtitle with the same standards as the title (Medium
    evaluates title, subtitle, AND cover image together)."""
    if not subtitle:
        return []
    issues: list[dict[str, str]] = []
    for name, pattern in CLICKBAIT_PATTERNS:
        match = pattern.search(subtitle)
        if match:
            issues.append(
                {
                    "severity": Severity.MAJOR.value,
                    "title": f"Clickbait pattern in subtitle: {name}",
                    "detail": f"Subtitle matched '{match.group(0)}'. Medium evaluates "
                    "title AND subtitle together; a sensationalistic subtitle "
                    "disqualifies the story just like the title does.",
                    "suggestion": "Make the subtitle state the actual promise or angle.",
                    "rule_class": RuleClass.POLICY.value,
                }
            )
            break
    if len(subtitle) > 140:
        issues.append(
            {
                "severity": Severity.MINOR.value,
                "title": f"Subtitle is long ({len(subtitle)} chars)",
                "detail": "Long subtitles truncate in feeds and previews.",
                "suggestion": "Trim to the core promise (under ~140 chars).",
                "rule_class": RuleClass.RECOMMENDATION.value,
            }
        )
    return issues


def analyze_title(title: str | None) -> TitleAnalysis:
    """Deterministic title analysis. Clickbait rules are HEURISTIC; the
    underlying expectation (title must represent the story) is POLICY."""
    if not title:
        return TitleAnalysis(
            title=None,
            issues=[
                {
                    "severity": Severity.MAJOR.value,
                    "title": "No title",
                    "detail": "The article has no H1 title and no frontmatter title.",
                    "suggestion": "Add a title that states the article's promise. "
                    "Run 'article-craft new' for candidates.",
                    "rule_class": RuleClass.HEURISTIC.value,
                }
            ],
            clickbait_risk="low",
            clarity="unknown",
        )
    issues: list[dict[str, str]] = []
    risk = "low"
    for name, pattern in CLICKBAIT_PATTERNS:
        match = pattern.search(title)
        if match:
            risk = "high" if risk != "high" else risk
            issues.append(
                {
                    "severity": Severity.MAJOR.value,
                    "title": f"Clickbait pattern in title: {name}",
                    "detail": f"Matched '{match.group(0)}'. Medium's distribution "
                    "guidelines disqualify sensationalistic titles from General "
                    "Distribution.",
                    "suggestion": "Rewrite to state the actual promise, e.g. name the "
                    "concrete outcome or the specific problem solved.",
                    "rule_class": RuleClass.POLICY.value,
                }
            )
            break  # one clickbait finding is enough
    for name, pattern in GENERIC_PATTERNS:
        match = pattern.search(title)
        if match:
            issues.append(
                {
                    "severity": Severity.MINOR.value,
                    "title": f"Generic title pattern: {name}",
                    "detail": f"Matched '{match.group(0)}'. Medium treats overly "
                    "generic titles the same as sensationalistic ones.",
                    "suggestion": "Replace with the specific angle: what exactly will "
                    "the reader get that they can't get elsewhere?",
                    "rule_class": RuleClass.POLICY.value,
                }
            )
            break
    if len(title) > 95:
        issues.append(
            {
                "severity": Severity.MINOR.value,
                "title": f"Title is long ({len(title)} chars)",
                "detail": "Long titles get truncated in feeds and search results.",
                "suggestion": "Move detail into the subtitle; keep the title under "
                "~60 characters when possible.",
                "rule_class": RuleClass.RECOMMENDATION.value,
            }
        )
    if title.islower() and len(title.split()) > 5:
        issues.append(
            {
                "severity": Severity.INFO.value,
                "title": "Title is all lowercase",
                "detail": "Reads as careless on a profile page.",
                "suggestion": "Use sentence case at minimum.",
                "rule_class": RuleClass.HEURISTIC.value,
            }
        )
    # Keyword stuffing: the same content word repeated to game ranking.
    words = [w.lower() for w in re.findall(r"[a-z0-9]+", title) if len(w) > 2]
    if words:
        from collections import Counter

        word_counts = Counter(words)
        most_common_word, count = word_counts.most_common(1)[0]
        if count >= 3 and len(words) >= 5:
            issues.append(
                {
                    "severity": Severity.MAJOR.value,
                    "title": f"Keyword stuffing: '{most_common_word}' appears {count} times",
                    "detail": "Repeating keywords to game search ranking reads as "
                    "spam and erodes reader trust.",
                    "suggestion": "Write the title for a human; state the actual "
                    "subject once, precisely.",
                    "rule_class": RuleClass.POLICY.value,
                }
            )
    if issues and any(i["severity"] == Severity.MAJOR.value for i in issues):
        risk = "high"
    elif issues and any(i["severity"] == Severity.MINOR.value for i in issues):
        risk = "medium"
    clarity = "vague" if any("Generic" in i["title"] for i in issues) else "good"
    return TitleAnalysis(title=title, issues=issues, clickbait_risk=risk, clarity=clarity)


# ---------------------------------------------------------------------------
# Candidate generation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TitleCandidate:
    title: str
    subtitle: str
    approach: str  # descriptive | problem-oriented | outcome-oriented | ...
    clarity: int  # 1-5
    specificity: int  # 1-5
    reader_promise: int  # 1-5
    accuracy_note: str  # what the author must verify before using it
    clickbait_risk: str = "low"


def generate_title_candidates(
    topic: str,
    angle: str,
    audience: str,
    article_type: str,
) -> list[TitleCandidate]:
    """Generate title candidates across different approaches.

    These are starting points for the author. Each candidate carries an
    accuracy note: the author must confirm the title doesn't promise more
    than the article delivers.
    """
    topic_short = topic.strip().rstrip(".")
    angle_short = angle.strip().rstrip(".")
    candidates = [
        TitleCandidate(
            title=f"{topic_short.capitalize()}: what {audience} actually need to know",
            subtitle=f"A {article_type.replace('-', ' ')} focused on {angle_short}",
            approach="descriptive",
            clarity=5,
            specificity=3,
            reader_promise=4,
            accuracy_note="Confirm the article really covers the essentials, not everything.",
        ),
        TitleCandidate(
            title=f"The {topic_short} problem nobody names until production",
            subtitle=f"How {angle_short} changes the failure modes",
            approach="problem-oriented",
            clarity=3,
            specificity=4,
            reader_promise=4,
            clickbait_risk="medium",
            accuracy_note="Only use if the article genuinely discusses a production failure mode.",
        ),
        TitleCandidate(
            title=f"What I learned {angle_short}",
            subtitle=f"A personal {article_type.replace('-', ' ')} about {topic_short}",
            approach="experience-based",
            clarity=4,
            specificity=3,
            reader_promise=3,
            accuracy_note="Requires real personal experience in the article; never invent it.",
        ),
        TitleCandidate(
            title=f"How to {angle_short} without the usual {topic_short} mistakes",
            subtitle=f"A practical {article_type.replace('-', ' ')} for {audience}",
            approach="outcome-oriented",
            clarity=5,
            specificity=4,
            reader_promise=5,
            accuracy_note="The article must deliver the 'how', not just theory.",
        ),
        TitleCandidate(
            title=f"{topic_short.capitalize()}, explained with {angle_short}",
            subtitle=f"Building the mental model {audience} are usually missing",
            approach="curiosity-driven",
            clarity=4,
            specificity=4,
            reader_promise=4,
            accuracy_note="Keep the explanation honest: no mystery-mongering.",
        ),
        TitleCandidate(
            title=f"A working {topic_short} walkthrough",
            subtitle="Every step tested, with the failure cases the docs skip",
            approach="technical",
            clarity=5,
            specificity=4,
            reader_promise=5,
            accuracy_note="Every code sample must actually run as published.",
        ),
        TitleCandidate(
            title=f"{topic_short.capitalize()} for people who've been burned before",
            subtitle=f"Start here if the official {topic_short} docs left you confused",
            approach="beginner-friendly",
            clarity=3,
            specificity=3,
            reader_promise=4,
            clickbait_risk="medium",
            accuracy_note="Match the tone of the article; drop the edge if the piece is formal.",
        ),
    ]
    return candidates


def title_candidates_to_markdown(candidates: list[TitleCandidate]) -> str:
    lines = ["# Title candidates", ""]
    for i, c in enumerate(candidates, start=1):
        lines.append(f"## {i}. {c.approach.replace('-', ' ').capitalize()}")
        lines.append("")
        lines.append(f"- **Title:** {c.title}")
        lines.append(f"- **Subtitle:** {c.subtitle}")
        lines.append(
            f"- **Scores:** clarity {c.clarity}/5, specificity {c.specificity}/5, "
            f"reader promise {c.reader_promise}/5, clickbait risk {c.clickbait_risk}"
        )
        lines.append(f"- **Accuracy check:** {c.accuracy_note}")
        lines.append("")
    return "\n".join(lines)
