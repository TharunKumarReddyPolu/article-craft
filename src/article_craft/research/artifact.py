"""Research artifact rendering (spec §23).

The research artifact stays separate from the final article: thesis, research
questions, sources with authority metadata, claims with confidence,
contradictions, statistics, and potential examples.
"""

from __future__ import annotations

from datetime import date

from article_craft.models.research import ClaimStatus, ResearchDoc, Source, SourceTier


def render_research_doc(
    doc: ResearchDoc,
    title: str = "Research",
) -> str:
    lines: list[str] = [f"# {title}", ""]

    lines += ["## Article Thesis", "", doc.thesis or "(not set)", ""]

    if doc.research_questions:
        lines += ["## Research Questions", ""]
        lines += [f"- {q}" for q in doc.research_questions]
        lines.append("")

    lines += ["## Sources", ""]
    if doc.sources:
        for i, source in enumerate(doc.sources, start=1):
            lines.append(f"### Source {i}")
            lines.append("")
            lines.append(f"Title: {source.title}")
            if source.url:
                lines.append(f"URL: {source.url}")
            lines.append(f"Authority: Tier {source.tier.value} — {source_tier_label(source.tier)}")
            if source.author:
                lines.append(f"Author: {source.author}")
            if source.publisher:
                lines.append(f"Publisher: {source.publisher}")
            if source.date_published:
                lines.append(f"Date published: {source.date_published.isoformat()}")
            lines.append(f"Date accessed: {(source.date_accessed or date.today()).isoformat()}")
            claims_for = [c for c in doc.claims if c.source_index == i - 1]
            if claims_for:
                lines.append("Claims:")
                for claim in claims_for:
                    lines.append(f"- {claim.text[:160]} ({claim.status.value})")
            lines.append(f"Confidence: {_confidence(claims_for, source)}")
            if source.notes:
                lines.append(f"Notes: {source.notes}")
            lines.append("")
    else:
        lines += [
            "_No sources recorded yet. Every source entry needs: title, URL, "
            "authority tier, dates, and claims it supports. Never invent a "
            "source — record only what you actually read._",
            "",
        ]

    if doc.contradictions:
        lines += ["## Contradictions", ""]
        lines += [f"- {c}" for c in doc.contradictions]
        lines.append("")

    if doc.statistics:
        lines += ["## Statistics", ""]
        lines += [f"- {s}" for s in doc.statistics]
        lines.append("")

    if doc.claims_requiring_verification:
        lines += ["## Claims Requiring Verification", ""]
        lines += [f"- {c}" for c in doc.claims_requiring_verification]
        lines.append("")

    if doc.potential_examples:
        lines += ["## Potential Examples", ""]
        lines += [f"- {e}" for e in doc.potential_examples]
        lines.append("")

    lines += [
        "---",
        "_This research artifact is working material. It stays separate from "
        "the final article. Claims marked UNVERIFIED must be resolved before "
        "publishing._",
    ]
    return "\n".join(lines)


def source_tier_label(tier: SourceTier) -> str:
    from article_craft.models.research import SOURCE_TIERS

    return SOURCE_TIERS.get(int(tier), "unknown authority")


def _confidence(claims: list, source: Source) -> str:
    if not claims:
        return "No claims attributed to this source yet."
    statuses = [c.status for c in claims]
    if ClaimStatus.CONTRADICTED in statuses:
        return "Low — a claim attributed to this source was contradicted elsewhere."
    if all(c.status is ClaimStatus.VERIFIED for c in claims):
        return "High — all attributed claims verified this session."
    if source.tier.value <= 2:
        return "Medium-high — official/professional source; verify dates."
    return "Medium — verify load-bearing claims against Tier 1 sources."
