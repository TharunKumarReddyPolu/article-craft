"""Reach-readiness: alignment with platforms' own stated discoverability criteria.

Every platform officially publishes what it looks for — curation
criteria, tag/cover mechanics, subject-line guidance.
This engine checks an article's alignment with those *stated* criteria and
returns advisory signals only. It never predicts distribution, ranking, or
engagement: platform reach is the platform's decision, and every report that
uses these checks carries that disclaimer.

Each check cites the ``source_id`` registered in the platform's
``sources.yaml`` so the origin of every rule is auditable.
"""

from __future__ import annotations

import re

from article_craft.editorial.ai_patterns import (
    ai_pattern_density_per_1000,
    find_ai_patterns,
)
from article_craft.models.article import Article
from article_craft.models.review import PlatformCheck, PlatformCheckStatus, RuleClass


def _prose_of(article: Article) -> str:
    return "\n".join(s.body for s in article.sections)


def _body_prose_without_headlines(article: Article) -> str:
    """Section bodies with markdown ATX heading lines removed.

    Used by the parity check: section bodies retain their heading lines, and
    the first section contains the H1 headline — matching against it would
    prove only that the title matches itself.
    """
    lines: list[str] = []
    for s in article.sections:
        lines.extend(ln for ln in s.body.splitlines() if not ln.lstrip().startswith("#"))
    return "\n".join(lines)


def _subtitle_of(article: Article) -> str:
    fm = article.frontmatter
    return article.effective_subtitle or fm.subtitle or ""


def first_hand_experience_signal(article: Article, source_id: str) -> PlatformCheck:
    """Alignment with the official 'writer's experience / authorship' criterion.

    Official sources for several platforms ask for first-hand experience
    (Medium: "clear and compelling reason why this particular writer is
    writing about this particular topic"; LinkedIn: "write about specific
    areas in which you have experience and/or expertise"). This heuristic
    looks for the observable traces of first-hand contribution — the same
    signals the originality engine uses — and is advisory by design.
    """
    prose = _prose_of(article)
    lower = prose.lower()
    words = len(prose.split())
    if words == 0:
        return PlatformCheck(
            category="Reach — Authorship",
            status=PlatformCheckStatus.NOT_CHECKED,
            detail="No prose to inspect for first-hand-experience signals.",
            rule_class=RuleClass.HEURISTIC,
            advisory=True,
            source_id=source_id,
        )
    hits = find_ai_patterns(prose)
    density = ai_pattern_density_per_1000(article)
    personal_pattern = re.compile(
        r"\b(?:i|we|my|our)\b"
        r"|\bin my experience\b"
        r"|\bwhen (?:i|we)\b"
        r"|\bi(?:'ve|'d|'m)\b"
        r"|\bi (?:was|learned|built|tried|hit|found)\b"
    )
    personal = personal_pattern.findall(lower)
    specifics = sum(
        1
        for pat in (r"\b\d+(\.\d+)?(ms|s|x|%|k|m|gb|mb|qps|req)\b", r"v\d+\.\d+", r"```")
        if re.search(pat, lower)
    )
    signals = len(personal) + specifics
    findings: list[str] = []
    if signals == 0:
        findings.append(
            "No first-hand markers found: no first-person experience, no concrete "
            "numbers/versions, no code."
        )
    if density >= 3.0:
        findings.append(
            f"Generic-AI phrasing density is {density:.1f}/1000 words "
            f"({len(hits)} hits) — generic prose reads as derivative, the "
            "opposite of the 'fresh perspective' platforms ask for."
        )
    if not findings:
        status = PlatformCheckStatus.PASS
        detail = (
            f"{signals} authorship/specificity signal(s) detected and low generic "
            "phrasing — aligned with the official first-hand-experience criterion."
        )
    elif len(findings) == 1 and density < 3.0:
        status = PlatformCheckStatus.NOT_CHECKED
        detail = (
            "Weak authorship signals. Platforms officially favor demonstrable "
            "first-hand experience; make the piece unmistakably yours."
        )
    else:
        status = PlatformCheckStatus.WARNING
        detail = (
            "Authorship signals are weak or generic phrasing is dense — "
            "platforms' own criteria favor first-hand experience and fresh "
            "perspective."
        )
    return PlatformCheck(
        category="Reach — Authorship",
        status=status,
        detail=detail,
        rule_class=RuleClass.HEURISTIC,
        advisory=True,
        source_id=source_id,
        findings=findings,
    )


def reader_value_signal(article: Article, source_id: str) -> PlatformCheck:
    """Alignment with the official 'value and impact' criterion.

    Official curation guidelines (e.g. Medium's): "The reader's life is
    enriched by reading the
    story... it's an example of the kind of story that makes someone happy to
    pay for their Medium membership and/or want to share the story." The
    observable proxies: the article delivers something concrete (steps,
    code, data, comparisons) and respects the reader's time.
    """
    prose = _prose_of(article)
    words = len(prose.split())
    lower = prose.lower()
    deliverables = sum(
        1
        for pat in (
            r"```",  # runnable material
            r"^\s*(step|\d+\.|-\s\[)",
            r"\b(for example|for instance|in practice|as a result)\b",
            # observed metrics: "2.3s", "180ms", "p99", "3x", "40%", "v2.1"
            r"\b\d+(\.\d+)?\s?(ms|s|min|hours?|x|%|gb|mb|k|qps|req)\b",
            r"\bp(50|90|95|99)\b",
        )
        if re.search(pat, lower, re.MULTILINE)
    )
    hedging = len(re.findall(r"\b(maybe|perhaps|it depends|arguably)\b", lower))
    findings: list[str] = []
    if words < 300:
        findings.append(
            f"Only {words} words of prose — very short pieces rarely deliver "
            "the depth platforms describe as 'time well spent'."
        )
    if deliverables == 0:
        findings.append(
            "No concrete deliverables detected (no code, steps, examples, or "
            "data) — value must be carried by prose alone."
        )
    if hedging >= 4:
        findings.append(f"{hedging} hedge phrases — hedged writing dilutes the takeaway.")
    if not findings:
        status = PlatformCheckStatus.PASS
        detail = (
            "Concrete deliverables present and proportionate length — aligned "
            "with the official 'value and impact' criterion."
        )
    elif len(findings) == 1 and words >= 300:
        status = PlatformCheckStatus.NOT_CHECKED
        detail = "Limited observable value signals; judge this against your draft."
    else:
        status = PlatformCheckStatus.WARNING
        detail = (
            "Weak value signals. Official curation criteria (where a platform "
            "publishes them) ask that the reader's life is enriched and reading "
            "the piece is time well spent."
        )
    return PlatformCheck(
        category="Reach — Reader Value",
        status=status,
        detail=detail,
        rule_class=RuleClass.HEURISTIC,
        advisory=True,
        source_id=source_id,
        findings=findings,
    )


def headline_parity_check(article: Article, source_id: str) -> PlatformCheck:
    """Official disqualifier on curated platforms: the title/cover does not
    'represent the story well'.

    Medium: titles/subtitles/covers that are sensationalistic *or* overly
    generic/mysterious/formulaic disqualify a story from curation because
    readers can't tell what they're clicking into. The deterministic proxy:
    does the subtitle (the promise) and body actually contain what the title
    promises? We check the cheapest honest signal — shared keywords — and
    flag sensational/generic title patterns already detected by the title
    analyzer at the adapter level.
    """
    title = article.effective_title.lower()
    subtitle = _subtitle_of(article).lower()
    prose = _body_prose_without_headlines(article).lower()
    stopwords = {
        "the",
        "a",
        "an",
        "of",
        "to",
        "in",
        "for",
        "and",
        "or",
        "is",
        "are",
        "how",
        "why",
        "what",
        "with",
        "your",
        "you",
        "my",
        "we",
        "i",
        "it",
        "that",
        "this",
        "on",
        "at",
        "from",
        "guide",
        "tips",
    }
    title_terms = {t for t in re.findall(r"[a-z0-9+#.-]{3,}", title) if t not in stopwords}
    if not title_terms:
        return PlatformCheck(
            category="Reach — Headline Parity",
            status=PlatformCheckStatus.NOT_CHECKED,
            detail="Title too short to evaluate headline/content parity.",
            rule_class=RuleClass.HEURISTIC,
            advisory=True,
            source_id=source_id,
        )
    in_subtitle = sum(1 for t in title_terms if t in subtitle)
    in_body = sum(1 for t in title_terms if t in prose)
    parity = (in_subtitle + in_body) / (len(title_terms) * 2)
    findings: list[str] = []
    if parity < 0.34:
        findings.append(
            "Key title terms barely appear in the subtitle or body — the "
            "headline may over- or under-sell the story (curated platforms' "
            "guidelines disqualify stories whose title misrepresents them)."
        )
    if not subtitle:
        findings.append("No subtitle: the headline must carry the whole promise alone.")
    if not findings:
        status = PlatformCheckStatus.PASS
        detail = "Title terms are well represented in the subtitle/body."
    elif len(findings) == 1 and not subtitle:
        status = PlatformCheckStatus.NOT_CHECKED
        detail = findings[0] + " Consider adding one."
    else:
        status = PlatformCheckStatus.WARNING
        detail = (
            "Headline/story parity is weak — platforms that curate "
            "(see the cited source) disqualify stories whose title, subtitle, "
            "or cover don't represent the story."
        )
    return PlatformCheck(
        category="Reach — Headline Parity",
        status=status,
        detail=detail,
        rule_class=RuleClass.HEURISTIC,
        advisory=True,
        source_id=source_id,
        findings=findings,
    )


def non_derivative_signal(article: Article, source_id: str) -> PlatformCheck:
    """Alignment with the official 'non-derivative' criterion.

    Medium: the story "doesn't just paraphrase, recombine, or rehash
    information that is easily found elsewhere." Observable proxies: very
    high generic-AI density, listicle-without-argument structure, and
    absence of any first-hand artifact (code, data, screenshots).
    """
    prose = _prose_of(article)
    density = ai_pattern_density_per_1000(article)
    has_artifact = bool(re.search(r"```|!\[|\|\s*\w+\s*\|", prose))
    findings: list[str] = []
    if density >= 4.0:
        findings.append(
            f"Generic-AI phrasing density {density:.1f}/1000 — heavily recycled "
            "phrasing patterns read as 'rehashing what is easily found elsewhere'."
        )
    if not has_artifact:
        findings.append(
            "No code, data, images, or tables — nothing that could only come "
            "from doing the work yourself."
        )
    if not findings:
        status = PlatformCheckStatus.PASS
        detail = "Contains first-hand artifacts and low recycled phrasing."
    elif len(findings) == 1 and not has_artifact:
        status = PlatformCheckStatus.NOT_CHECKED
        detail = (
            "No first-hand artifacts detected. Official criterion: bring a "
            "fresh perspective rather than rehashing."
        )
    else:
        status = PlatformCheckStatus.WARNING
        detail = (
            "Strong derivative signals. Platforms' own guidelines consistently "
            "exclude recycled, derivative, and generic content from "
            "distribution and curation."
        )
    return PlatformCheck(
        category="Reach — Originality",
        status=status,
        detail=detail,
        rule_class=RuleClass.HEURISTIC,
        advisory=True,
        source_id=source_id,
        findings=findings,
    )
