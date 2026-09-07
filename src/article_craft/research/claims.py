"""Claim extraction and fact-check classification scaffolding.

The extractor finds *candidate* factual claims deterministically (numbers,
superlatives, attributions, causal assertions, quotes). Classification into
VERIFIED/LIKELY/UNVERIFIED/CONTRADICTED/OPINION/ASSUMPTION requires judgment:
the CLI marks everything UNVERIFIED with category hints, and the agent (with
web access when available) upgrades/downgrades with evidence. The CLI never
invents verification results, citations, or URLs.
"""

from __future__ import annotations

import re

from article_craft.models.article import Article
from article_craft.models.research import Claim, ClaimStatus

# (label, pattern, hint) — hint tells the agent what kind of verification to do.
_CLUE_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "statistic",
        re.compile(
            r"\b\d+(?:\.\d+)?\s?(?:%|percent)\b"
            r"|\b\d+(?:\.\d+)?\s?(?:ms|s|kB|KB|MB|GB|TB)\b"
            r"|\b\d+x\b"
        ),
        "Verify the number and its source; check the date.",
    ),
    (
        "benchmark",
        re.compile(
            r"\b(benchmark|p\d{2}|latency|throughput|qps|rps|ops/sec|"
            r"\bfaster than|outperforms)\b",
            re.IGNORECASE,
        ),
        "Benchmarks need a setup description or a citation. Never fabricate.",
    ),
    (
        "version-behavior",
        re.compile(
            r"\b(since (version )?\d|as of \d{4}|in \w+ \d+\.\d+|default (to|is|in)|"
            r"no longer|deprecated|removed in)\b",
            re.IGNORECASE,
        ),
        "Check the changelog / official docs for the exact version.",
    ),
    (
        "attribution",
        re.compile(
            r"\b(according to|said|says|stated|reported|per the|"
            r"studies show|research shows|survey)\b",
            re.IGNORECASE,
        ),
        "Verify the named source actually exists and says this.",
    ),
    (
        "superlative",
        re.compile(
            r"\b(fastest|best|most (scalable|secure|efficient)|only|first|"
            r"always|never|everyone|nobody|guaranteed)\b",
            re.IGNORECASE,
        ),
        "Absolute claims are rarely true as stated; scope or soften them.",
    ),
    (
        "causal",
        re.compile(r"\b(because|causes?|leads? to|results? in|due to|thanks to)\b", re.IGNORECASE),
        "Causal claims need evidence of mechanism, not just correlation.",
    ),
    (
        "security",
        re.compile(
            r"\b(secure|insecure|vulnerab\w+|encrypt\w*|safe from|protects? against|"
            r"CVE-\d{4}-\d+)\b",
            re.IGNORECASE,
        ),
        "Security claims are load-bearing: verify against primary sources.",
    ),
]

OPINION_RE = re.compile(
    r"\b(i (think|believe|prefer|like|hate|love|argue)|in my opinion|"
    r"i'?m convinced|should (really )?(use|be))\b",
    re.IGNORECASE,
)
ASSUMPTION_RE = re.compile(
    r"\b(assume|assuming|suppose|for (the sake of )?simplicity|"
    r"imagine that|let'?s pretend)\b",
    re.IGNORECASE,
)
QUOTE_RE = re.compile(r"\"([^\"]{25,})\"")


def extract_claims(article: Article) -> list[Claim]:
    """Extract candidate claims, each UNVERIFIED with a category hint.

    Personal-experience sentences and clearly marked opinions stay out of the
    factual pipeline (they're the author's to confirm).
    """
    claims: list[Claim] = []
    seen_texts: set[str] = set()
    for section in article.sections:
        prose_lines = []
        in_fence = False
        for line in section.body.split("\n"):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if not in_fence:
                prose_lines.append(line)
        prose = "\n".join(prose_lines)
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", prose) if s.strip()]
        for sentence in sentences:
            clean = re.sub(r"[#*`\[\]()>-]", "", sentence).strip()
            if len(clean) < 25 or clean in seen_texts:
                continue
            if OPINION_RE.search(clean):
                claims.append(
                    Claim(
                        text=clean,
                        status=ClaimStatus.OPINION,
                        section_title=section.title,
                        reason="Phrase reads as the author's own judgment. Confirm it's "
                        "meant as opinion, not fact.",
                    )
                )
                seen_texts.add(clean)
                continue
            if ASSUMPTION_RE.search(clean):
                claims.append(
                    Claim(
                        text=clean,
                        status=ClaimStatus.ASSUMPTION,
                        section_title=section.title,
                        reason="Stated as an assumption — make sure the article marks "
                        "it as one in the final text.",
                    )
                )
                seen_texts.add(clean)
                continue
            matched = [
                (label, hint) for label, pattern, hint in _CLUE_PATTERNS if pattern.search(clean)
            ]
            if matched:
                labels = ", ".join(label for label, _ in matched)
                hints = " ".join(dict.fromkeys(hint for _, hint in matched))
                claims.append(
                    Claim(
                        text=clean,
                        status=ClaimStatus.UNVERIFIED,
                        section_title=section.title,
                        reason=f"Claim type(s): {labels}. {hints}",
                    )
                )
                seen_texts.add(clean)
    return claims


def scaffold_factcheck(article: Article) -> tuple[list[Claim], str]:
    """Produce the claim list and the honest header for a fact-check report.

    Without web access, everything stays UNVERIFIED and the header says so.
    """
    claims = extract_claims(article)
    header = (
        "External verification was not available. Verify these claims before publication."
        if not _web_available()
        else ""
    )
    return claims, header


def _web_available() -> bool:
    """The CLI library never fetches web content itself; agents with web
    access run the verification. This keeps tests deterministic and honest."""
    return False


def factcheck_report_markdown(article: Article) -> str:
    claims, header = scaffold_factcheck(article)
    lines = [
        f"# Fact-Check Report: {article.effective_title}",
        "",
    ]
    if header:
        lines += [f"> **{header}**", ""]
    if not claims:
        lines += [
            "No checkable factual claims detected. This article appears to be "
            "framing/analysis — still confirm any examples are accurate.",
            "",
        ]
        return "\n".join(lines)
    lines += [
        "| # | Claim | Status | Type & verification hint | Section |",
        "|---|-------|--------|--------------------------|---------|",
    ]
    for i, claim in enumerate(claims, start=1):
        text = claim.text.replace("|", "\\|")
        reason = (claim.reason or "").replace("|", "\\|")
        section = claim.section_title or "(intro)"
        lines.append(f"| {i} | {text[:140]} | {claim.status.value} | {reason} | {section} |")
    unverified = [c for c in claims if c.status is ClaimStatus.UNVERIFIED]
    lines += [
        "",
        "## Before you publish",
        "",
        f"- {len(unverified)} claim(s) need verification (web access + primary "
        "sources: official docs, changelogs, papers).",
        "- Claims attributed to your own experience stay yours to confirm — "
        "the tool marks them LIKELY at most, never VERIFIED.",
        "- Never invent a source for a claim; remove or soften instead.",
    ]
    return "\n".join(lines)
