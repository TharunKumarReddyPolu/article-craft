"""The originality guard (spec §18).

When a source article is supplied, this module compares it with the draft
(heuristic only — not a plagiarism detector) and flags similarity risks:
sentence-level overlap, structural mirroring, and reuse of distinctive
examples without attribution. Its job is to encourage an *independently
structured article*, never to help disguise copying (see Medium's plagiarism
guidelines: mosaic plagiarism and AI-remix derivatives are violations).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from article_craft.models.article import Article


@dataclass
class OriginalityFinding:
    risk: str  # HIGH | MEDIUM | LOW
    kind: str  # sentence-overlap | structural | example-reuse | unattributed-quote
    detail: str
    location: str | None = None
    suggestion: str | None = None


@dataclass
class OriginalityReport:
    findings: list[OriginalityFinding] = field(default_factory=list)
    verdict: str = "INDEPENDENT"  # INDEPENDENT | NEEDS RESTRUCTURING | DERIVATIVE — RETHINK
    summary: str = ""

    @property
    def has_high_risks(self) -> bool:
        return any(f.risk == "HIGH" for f in self.findings)


def _sentences(text: str) -> list[str]:
    prose_lines = []
    in_fence = False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            prose_lines.append(line)
    prose = "\n".join(prose_lines)
    return [
        re.sub(r"\s+", " ", s.strip())
        for s in re.split(r"(?<=[.!?])\s+", prose)
        if s.strip() and len(s.strip()) > 20
    ]


def _normalize(sentence: str) -> str:
    words = re.findall(r"[a-z0-9']+", sentence.lower())
    stop = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "to",
        "of",
        "in",
        "on",
        "for",
        "with",
        "and",
        "or",
        "that",
        "this",
        "it",
        "as",
        "by",
        "at",
        "from",
        "not",
        "you",
        "your",
        "we",
        "our",
        "i",
        "my",
    }
    return " ".join(w for w in words if w not in stop)


def _shingles(sentence: str, n: int = 4) -> set[tuple[str, ...]]:
    words = _normalize(sentence).split()
    if len(words) < n:
        return {tuple(words)} if words else set()
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def assess_originality(
    article: Article, source_text: str, source_title: str = "source"
) -> OriginalityReport:
    """Compare a draft with a supplied source. Heuristic risk surfacing for
    human judgment — explicitly not a plagiarism detector."""
    findings: list[OriginalityFinding] = []
    draft_sentences = _sentences("\n".join(s.body for s in article.sections))
    source_sentences = _sentences(source_text)
    source_shingles = [_shingles(s) for s in source_sentences]

    # 1. Sentence-level overlap (mosaic plagiarism risk).
    for i, sentence in enumerate(draft_sentences):
        norm = _normalize(sentence)
        if not norm:
            continue
        draft_sh = _shingles(sentence)
        best, best_score = None, 0.0
        for src, sh in zip(source_sentences, source_shingles, strict=False):
            score = _jaccard(draft_sh, sh)
            if score > best_score:
                best, best_score = src, score
        if best_score >= 0.55:
            assert best is not None  # best_score > 0 implies a best match
            findings.append(
                OriginalityFinding(
                    risk="HIGH",
                    kind="sentence-overlap",
                    detail=f"Draft sentence closely matches the {source_title}: "
                    f'"{best[:120]}..." (similarity {best_score:.0%})',
                    location=f"line ~{i + 1}",
                    suggestion="Rewrite from your own understanding and experience, "
                    "or quote exactly and attribute. Synonym-swapping is still "
                    "mosaic plagiarism under Medium's guidelines.",
                )
            )
        elif best_score >= 0.35:
            findings.append(
                OriginalityFinding(
                    risk="MEDIUM",
                    kind="sentence-overlap",
                    detail=f"Draft sentence partially overlaps the {source_title} "
                    f"(similarity {best_score:.0%}).",
                    location=f"line ~{i + 1}",
                    suggestion="Restructure the sentence around your own point; "
                    "attribute if the idea originated there.",
                )
            )

    # 2. Structural mirroring (section order/count).
    draft_sections = [s.title.lower() for s in article.sections if s.title]
    source_sections = [
        m.group(1).lower() for m in re.finditer(r"^#{1,3}\s+(.+?)\s*$", source_text, re.MULTILINE)
    ]
    if draft_sections and source_sections:
        # Order-aware longest common subsequence similarity.
        common = _lcs_length(draft_sections, source_sections)
        coverage = common / max(len(source_sections), 1)
        if coverage >= 0.7 and len(draft_sections) >= 3:
            findings.append(
                OriginalityFinding(
                    risk="HIGH",
                    kind="structural",
                    detail=f"Section structure mirrors the {source_title} "
                    f"({common}/{len(source_sections)} sections in the same order).",
                    suggestion="Reorganize around YOUR questions and reader's need. "
                    "Structure imitation is flagged by Medium's plagiarism guidelines "
                    "('concept, structure, or essential elements').",
                )
            )
        elif coverage >= 0.5:
            findings.append(
                OriginalityFinding(
                    risk="MEDIUM",
                    kind="structural",
                    detail=f"Section structure partially mirrors the {source_title} "
                    f"({common}/{len(source_sections)} sections in order).",
                    suggestion="Merge/split/reorder sections to serve your own article's promise.",
                )
            )

    # 3. Distinctive example reuse (proper nouns/numbers from the source).
    source_distinctive = set(
        re.findall(
            r"\b([A-Z][a-z]+(?:[A-Z][a-z]+)+|\d{3,}(?:,\d{3})*|\d+(?:\.\d+)?\s?(?:ms|%|GB|MB))\b",
            source_text,
        )
    )
    draft_text = "\n".join(s.body for s in article.sections)
    reused = [d for d in source_distinctive if d in draft_text]
    if len(reused) >= 3:
        findings.append(
            OriginalityFinding(
                risk="MEDIUM",
                kind="example-reuse",
                detail=f"{len(reused)} distinctive proper nouns/numbers from the "
                f"{source_title} appear in the draft without obvious attribution: "
                f"{', '.join(sorted(reused)[:5])}.",
                suggestion="Use your OWN examples, or attribute these explicitly "
                "('according to <source>'). Check whether numbers still hold.",
            )
        )

    # 4. Verbatim quotes without attribution markers.
    for src_sentence in source_sentences:
        fragment = src_sentence[:60]
        if len(fragment) > 30 and fragment in draft_text and ">" not in draft_text:
            findings.append(
                OriginalityFinding(
                    risk="HIGH",
                    kind="unattributed-quote",
                    detail=f"Verbatim passage from the {source_title} appears in the "
                    "draft without quotation/attribution markers.",
                    suggestion="Quote exactly in a blockquote with attribution, or "
                    "paraphrase genuinely with a citation.",
                )
            )
            break

    if any(f.risk == "HIGH" for f in findings):
        verdict = "DERIVATIVE — RETHINK"
    elif findings:
        verdict = "NEEDS RESTRUCTURING"
    else:
        verdict = "INDEPENDENT"
    summary = (
        f"{len(findings)} originality risk finding(s) vs. {source_title}: "
        + ", ".join(sorted({f.kind for f in findings}))
        if findings
        else f"No similarity risks detected vs. {source_title}. Keep your own "
        "examples, structure, and experience at the center."
    )
    return OriginalityReport(findings=findings, verdict=verdict, summary=summary)


def _lcs_length(a: list[str], b: list[str]) -> int:
    """Length of the longest common subsequence (order-aware matching)."""
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[len(a)][len(b)]


def originality_report_markdown(report: OriginalityReport) -> str:
    lines = [
        "# Originality Review",
        "",
        f"**Verdict: {report.verdict}**",
        "",
        report.summary,
        "",
    ]
    if report.findings:
        lines += ["| Risk | Kind | Finding | Fix |", "|------|------|---------|-----|"]
        for f in report.findings:
            detail = f.detail.replace("|", "\\|")
            suggestion = (f.suggestion or "").replace("|", "\\|")
            lines.append(f"| {f.risk} | {f.kind} | {detail} | {suggestion} |")
        lines += [
            "",
            "## The independence test",
            "",
            "1. Can the article stand if the reader never sees the source?",
            "2. Does it contain something the source doesn't (your experience, "
            "your data, your angle)?",
            "3. Is the structure your own — built from your reader's questions?",
            "4. Are all borrowed facts attributed and verified?",
            "",
            "This is a heuristic risk review for human judgment, not a "
            "plagiarism detector or a clearance certificate.",
        ]
    return "\n".join(lines)
