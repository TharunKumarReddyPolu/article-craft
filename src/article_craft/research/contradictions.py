"""Contradiction tracking across research sources (advanced research mode).

The engine compares claims made by different sources about the same topic
and builds :class:`ClaimConflict` records. Resolution follows the source
hierarchy (references/research/source-hierarchy.md): a higher-authority
source wins; ties stay unresolved and are surfaced to the author instead of
silently decided.

Topic matching is deliberately conservative: two claims conflict only when
they share a distinctive entity (an exact noun/number match on a salient
token) and use contradictory relations (different numbers, incompatible
quantifiers, or negation). This produces fewer, higher-precision conflicts
rather than noisy false positives.
"""

from __future__ import annotations

import re

from article_craft.models.research import (
    SOURCE_TIERS,
    ClaimConflict,
    ResearchDoc,
    Source,
)

_NUMBER = re.compile(r"\d+(?:\.\d+)?")
_STOP = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "for",
    "with",
    "is",
    "are",
    "was",
    "were",
    "be",
    "by",
    "at",
    "as",
    "it",
    "its",
    "that",
    "this",
    "these",
    "those",
    "can",
    "will",
    "may",
    "might",
    "should",
}

# Quantifier pairs that cannot both hold for the same subject.
_OPPOSED = {
    ("always", "never"),
    ("all", "none"),
    ("requires", "optional"),
    ("required", "optional"),
    ("sync", "async"),
    ("synchronous", "asynchronous"),
    ("free", "paid"),
    ("open source", "proprietary"),
}


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOP and len(t) > 2}


def _salient_entity(claim_a: str, claim_b: str) -> str | None:
    """The distinctive shared noun/number across two claims, if any."""
    a, b = _tokens(claim_a), _tokens(claim_b)
    shared = a & b
    if not shared:
        return None
    # Prefer numbers and rarer (longer) tokens: "5" or "kafka" over "support".
    numbers = [t for t in shared if _NUMBER.fullmatch(t)]
    if numbers:
        return sorted(numbers)[0]
    return sorted(shared, key=len, reverse=True)[0]


def _numbers(text: str) -> set[str]:
    return set(_NUMBER.findall(text))


def _opposition(claim_a: str, claim_b: str) -> bool:
    """Contradictory relations: differing numbers on the same topic, opposed
    quantifiers, or plain negation."""
    la, lb = claim_a.lower(), claim_b.lower()
    if _numbers(la) and _numbers(lb) and _numbers(la) != _numbers(lb):
        return True
    for pair in _OPPOSED:
        if (pair[0] in la and pair[1] in lb) or (pair[1] in la and pair[0] in lb):
            return True
    neg = ("not ", "cannot ", "can't ", "doesn't ", "does not ", "never ")
    return any((n in la) != (n in lb) for n in neg)


def _tier_of(source: Source | None) -> int:
    return source.tier.value if source is not None else 3


def tier_label(tier: int) -> str:
    return SOURCE_TIERS.get(tier, "unknown authority")


def detect_conflicts(doc: ResearchDoc) -> list[ClaimConflict]:
    """Pairwise-conflict scan over the research doc's claims. Only claims
    attributed to *different* sources are compared; same-source claims can't
    contradict each other in a resolvable way."""
    conflicts: list[ClaimConflict] = []
    claims = [c for c in doc.claims if c.source_index is not None]
    for i, claim_a in enumerate(claims):
        for claim_b in claims[i + 1 :]:
            if claim_a.source_index == claim_b.source_index:
                continue
            entity = _salient_entity(claim_a.text, claim_b.text)
            if entity is None or not _opposition(claim_a.text, claim_b.text):
                continue
            idx_a, idx_b = claim_a.source_index, claim_b.source_index
            src_a = (
                doc.sources[idx_a] if idx_a is not None and 0 <= idx_a < len(doc.sources) else None
            )
            src_b = (
                doc.sources[idx_b] if idx_b is not None and 0 <= idx_b < len(doc.sources) else None
            )
            tier_a, tier_b = _tier_of(src_a), _tier_of(src_b)
            conflict = ClaimConflict(
                topic=entity,
                claim_a=claim_a.text,
                claim_b=claim_b.text,
                source_a=claim_a.source_index,
                source_b=claim_b.source_index,
            )
            if tier_a < tier_b:
                conflict.resolution = "a"
                conflict.resolution_reason = (
                    f"Source A is Tier {tier_a} ({tier_label(tier_a)}); "
                    f"Source B is Tier {tier_b} ({tier_label(tier_b)})."
                )
            elif tier_b < tier_a:
                conflict.resolution = "b"
                conflict.resolution_reason = (
                    f"Source B is Tier {tier_b} ({tier_label(tier_b)}); "
                    f"Source A is Tier {tier_a} ({tier_label(tier_a)})."
                )
            else:
                conflict.resolution = None
                conflict.resolution_reason = (
                    f"Both sources are Tier {tier_a} ({tier_label(tier_a)}); the "
                    "hierarchy cannot decide. Verify against a primary source "
                    "before using either claim."
                )
            conflicts.append(conflict)
    return conflicts


def render_conflicts(doc: ResearchDoc) -> list[str]:
    """Human-readable conflict lines for research.md and fact-check output."""
    lines: list[str] = []
    for conflict in doc.conflicts:

        def _src(idx: int | None) -> str:
            if idx is None or not (0 <= idx < len(doc.sources)):
                return "unknown source"
            s = doc.sources[idx]
            return f"{s.title or 'Untitled'} (Tier {s.tier.value})"

        verdict = {
            "a": f"prefer A: {_src(conflict.source_a)}",
            "b": f"prefer B: {_src(conflict.source_b)}",
            None: "UNRESOLVED — verify against a primary source",
        }[conflict.resolution]
        lines.append(
            f'- [{conflict.topic}] "{conflict.claim_a}" ({_src(conflict.source_a)}) '
            f'vs "{conflict.claim_b}" ({_src(conflict.source_b)}) -> {verdict}. '
            f"{conflict.resolution_reason or ''}".strip()
        )
    return lines


def refresh_conflicts(doc: ResearchDoc) -> ResearchDoc:
    """Recompute doc.conflicts in place and return the doc (builder style)."""
    doc.conflicts = detect_conflicts(doc)
    return doc


__all__ = [
    "ClaimConflict",
    "detect_conflicts",
    "refresh_conflicts",
    "render_conflicts",
    "tier_label",
]
