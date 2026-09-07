"""The review engine: deterministic editorial analysis of an article.

Produces a ReviewResult with a reasoned Editorial Quality Score, issues,
critical issues, recommended changes, human-contribution assessment, and a
publish recommendation. LLM-appropriate judgments (tone critique, deep
technical correctness) are layered on top by the agent following
skills/article-craft/workflows/review.md — this engine provides the evidence.
"""

from __future__ import annotations

import re

from article_craft.editorial.ai_patterns import (
    ai_pattern_density_per_1000,
    find_ai_patterns,
    find_manipulation_patterns,
)
from article_craft.editorial.contribution import (
    contribution_is_sufficient,
    detect_human_contribution,
)
from article_craft.editorial.titles import analyze_subtitle, analyze_title
from article_craft.editorial.types import ArticleTypeSpec, get_article_type
from article_craft.models.article import Article
from article_craft.models.review import (
    Dimension,
    EditorialScore,
    HumanContribution,
    PublishRecommendation,
    ReviewIssue,
    ReviewResult,
    RuleClass,
    Severity,
    Verdict,
    verdict_for_score,
)
from article_craft.scoring import credit_strength, deduct, finalize, initial_score

# Patterns that signal unsupported factual assertions (for Evidence scoring).
_UNVERIFIED_CLUE_RE = re.compile(
    r"\b(studies show|research shows|experts say|it is (well )?known that|"
    r"most developers|most engineers|everyone knows|proven to|"
    r"\d+% of (developers|engineers|teams|users))\b",
    re.IGNORECASE,
)
_HEDGE_FACT_RE = re.compile(
    r"\b(approximately|roughly|about \d|on average|typically|usually)\b\s*\d", re.IGNORECASE
)


def review_article(article: Article) -> ReviewResult:
    """Run the full deterministic review."""
    score = initial_score()
    issues: list[ReviewIssue] = []
    spec = get_article_type(article.effective_article_type)

    _review_title_and_subtitle(article, score, issues)
    _review_structure(article, score, issues, spec)
    _review_readability(article, score, issues)
    _review_evidence(article, score, issues)
    _review_ai_patterns(article, score, issues)
    _review_manipulation(article, score, issues)
    _review_examples_and_code(article, score, issues, spec)
    _review_length(article, score, issues, spec)

    contribution = detect_human_contribution(article)
    _review_contribution(article, contribution, score, issues)
    finalize(score)
    critical = [i for i in issues if i.severity is Severity.CRITICAL]
    recommended = _recommended_changes(issues)
    verdict = verdict_for_score(score, len(critical))

    return ReviewResult(
        article_title=article.effective_title,
        article_path=article.path,
        article_type=article.effective_article_type,
        score=score,
        issues=issues,
        critical_issues=critical,
        recommended_changes=recommended,
        human_contribution=contribution,
        publish_recommendation=PublishRecommendation(
            verdict=verdict,
            explanation=_verdict_explanation(verdict, score, critical),
        ),
    )


# ---------------------------------------------------------------------------
# Dimension reviewers
# ---------------------------------------------------------------------------


def _review_title_and_subtitle(
    article: Article, score: EditorialScore, issues: list[ReviewIssue]
) -> None:
    analysis = analyze_title(article.effective_title)
    for item in analysis.issues:
        issues.append(
            ReviewIssue(
                dimension=Dimension.READER_VALUE,
                severity=Severity(item["severity"]),
                title=item["title"],
                detail=item["detail"],
                suggestion=item["suggestion"],
                rule_class=RuleClass(item["rule_class"]),
            )
        )
    for item in analyze_subtitle(article.effective_subtitle):
        issues.append(
            ReviewIssue(
                dimension=Dimension.READER_VALUE,
                severity=Severity(item["severity"]),
                title=item["title"],
                detail=item["detail"],
                suggestion=item["suggestion"],
                rule_class=RuleClass(item["rule_class"]),
            )
        )
    if not article.effective_subtitle:
        issues.append(
            ReviewIssue(
                dimension=Dimension.READER_VALUE,
                severity=Severity.MINOR,
                title="No subtitle",
                detail="The subtitle is what readers see under the title in feeds; "
                "without it the title has to carry the whole promise.",
                suggestion="Add a subtitle that adds the angle or scope the title can't fit.",
                rule_class=RuleClass.RECOMMENDATION,
            )
        )
        deduct(
            score,
            Dimension.READER_VALUE,
            2,
            reason="No subtitle: the title alone must carry the promise in feeds.",
            problem="Missing subtitle",
            recommendation="Add a subtitle with the angle or scope.",
        )
    if analysis.clickbait_risk == "high":
        deduct(
            score,
            Dimension.READER_VALUE,
            6,
            reason="Title has clickbait patterns; Medium disqualifies sensational "
            "titles from General Distribution.",
            problem="Clickbait title",
            recommendation="State the actual promise in the title.",
        )
    elif analysis.clickbait_risk == "medium":
        deduct(
            score,
            Dimension.READER_VALUE,
            3,
            reason="Title leans generic/clickbaity.",
            problem="Weak title",
            recommendation="Sharpen to the specific promise.",
        )
    if analysis.clarity == "vague":
        deduct(
            score,
            Dimension.READER_VALUE,
            2,
            reason="Title is generic ('Everything you need to know' class).",
            problem="Generic title",
            recommendation="Name the specific angle.",
        )
    if analysis.title and analysis.clickbait_risk == "low" and analysis.clarity == "good":
        credit_strength(
            score,
            Dimension.READER_VALUE,
            strength=f'Title is specific and accurate: "{analysis.title}"',
        )


def _review_structure(
    article: Article,
    score: EditorialScore,
    issues: list[ReviewIssue],
    spec: ArticleTypeSpec | None,
) -> None:
    sections = [s for s in article.sections if s.title]
    if not sections:
        issues.append(
            ReviewIssue(
                dimension=Dimension.STRUCTURE,
                severity=Severity.MAJOR,
                title="No sections",
                detail="The article has no H2 sections; long undifferentiated text is "
                "hard to navigate.",
                suggestion="Break the body into H2 sections that each answer a question.",
                rule_class=RuleClass.HEURISTIC,
            )
        )
        deduct(
            score,
            Dimension.STRUCTURE,
            5,
            reason="No section structure at all.",
            problem="No H2 sections",
        )
        return

    # Very short sections are usually stubs.
    stubs = [s for s in sections if s.word_count < 40]
    for stub in stubs:
        issues.append(
            ReviewIssue(
                dimension=Dimension.STRUCTURE,
                severity=Severity.MINOR,
                title=f"Stub section: '{stub.title}'",
                detail=f"Only {stub.word_count} words (lines {stub.start_line}-{stub.end_line}).",
                suggestion="Expand with substance or merge into a neighboring section.",
                location=f"'{stub.title}' (lines {stub.start_line}-{stub.end_line})",
                rule_class=RuleClass.HEURISTIC,
            )
        )
    if stubs:
        deduct(
            score,
            Dimension.STRUCTURE,
            min(3, len(stubs)),
            reason=f"{len(stubs)} section(s) are stubs with under 40 words.",
            problem="Stub sections",
            recommendation="Expand or merge stub sections.",
        )

    # Heading stuffing: too many headings relative to body (only meaningful
    # once the article is long enough for the ratio to mean something).
    if article.word_count >= 600:
        headings_per_1000 = (
            (len(sections) + sum(s.subheading_count for s in article.sections))
            * 1000
            / article.word_count
        )
        if headings_per_1000 > 6:
            issues.append(
                ReviewIssue(
                    dimension=Dimension.STRUCTURE,
                    severity=Severity.MINOR,
                    title="Heading stuffing",
                    detail=f"{headings_per_1000:.1f} headings per 1000 words — the article "
                    "is mostly skeleton.",
                    suggestion="Consolidate headings; move detail into prose.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
            deduct(
                score,
                Dimension.STRUCTURE,
                2,
                reason="Heading density too high; structure is decorative.",
                problem="Heading stuffing",
            )

    # Type-specific structural expectations.
    if spec:
        missing_stages = _missing_structure_stages(article, spec)
        for stage in missing_stages[:2]:
            issues.append(
                ReviewIssue(
                    dimension=Dimension.STRUCTURE,
                    severity=Severity.MINOR,
                    title=f"Expected '{stage}' content is missing for a {spec.label.lower()}",
                    detail=f"The {spec.label} structure expects: {', '.join(spec.structure)}.",
                    suggestion=f"Add or expand a section covering {stage}.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        if len(missing_stages) >= 2:
            deduct(
                score,
                Dimension.STRUCTURE,
                3,
                reason=f"Missing {len(missing_stages)} expected elements of the "
                f"{spec.label} structure ({', '.join(missing_stages[:3])}).",
                problem="Incomplete type structure",
                recommendation="Cover the type's expected structure.",
            )


def _missing_structure_stages(article: Article, spec: ArticleTypeSpec) -> list[str]:
    """Heuristically detect which expected structural stages are absent."""
    text = "\n".join(s.body for s in article.sections).lower()
    markers: dict[str, str] = {
        "failure handling": r"\b(fail|error|goes wrong|breaks|gotcha|pitfall|caveat|"
        r"troubleshoot|what if|edge case)\w*\b",
        "trade-offs": r"\b(trade-?off|downside|drawback|disadvantage|versus|vs\.?|"
        r"alternative|instead of)\w*\b",
        "prerequisites/assumptions": r"\b(prerequisite|you'?ll need|assum\w+|"
        r"before (you|we) (start|begin)|requirements)\b",
        "next steps": r"\b(next steps|where to go|further reading|what next|going further)\b",
        "worked example": r"\b(for example|let'?s|suppose|consider a|in practice|walkthrough)\b",
    }
    required_by_type: dict[str, tuple[str, ...]] = {
        "technical-tutorial": ("prerequisites/assumptions", "failure handling"),
        "system-design": ("trade-offs", "prerequisites/assumptions"),
        "architecture-deep-dive": ("trade-offs",),
        "opinion": ("trade-offs",),  # counterargument handling
        "advanced-guide": ("failure handling",),
    }
    required = required_by_type.get(spec.type_id, ())
    missing = []
    for stage in required:
        pattern = markers.get(stage)
        if pattern and not re.search(pattern, text):
            missing.append(stage)
    return missing


def _review_readability(article: Article, score: EditorialScore, issues: list[ReviewIssue]) -> None:
    prose_lines: list[str] = []
    for section in article.sections:
        in_fence = False
        for line in section.body.split("\n"):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if not in_fence:
                prose_lines.append(line)
    prose = "\n".join(prose_lines)
    sentences = [s for s in re.split(r"(?<=[.!?])[\"')\]]*\s+", prose) if s.strip()]
    long_sentences = [s for s in sentences if len(s.split()) > 35]
    if sentences and len(long_sentences) / len(sentences) > 0.25:
        issues.append(
            ReviewIssue(
                dimension=Dimension.CLARITY,
                severity=Severity.MINOR,
                title="Many overlong sentences",
                detail=f"{len(long_sentences)} of {len(sentences)} sentences exceed 35 words "
                f"({len(long_sentences) * 100 // max(1, len(sentences))}%).",
                suggestion="Split sentences over ~35 words; front-load the subject and verb.",
                rule_class=RuleClass.HEURISTIC,
            )
        )
        deduct(
            score,
            Dimension.CLARITY,
            3,
            reason=f"{len(long_sentences)}/{len(sentences)} sentences exceed 35 words.",
            problem="Overlong sentences",
            recommendation="Split and simplify the worst offenders.",
        )
    # Wall-of-text paragraphs.
    paragraphs = [
        p for p in re.split(r"\n\s*\n", prose) if p.strip() and not p.strip().startswith("#")
    ]
    walls = [p for p in paragraphs if len(p.split()) > 150]
    if walls:
        issues.append(
            ReviewIssue(
                dimension=Dimension.CLARITY,
                severity=Severity.MINOR,
                title="Wall-of-text paragraphs",
                detail=f"{len(walls)} paragraph(s) exceed 150 words.",
                suggestion="Split into 3-6 sentence paragraphs; one idea per paragraph.",
                rule_class=RuleClass.HEURISTIC,
            )
        )
        deduct(
            score,
            Dimension.CLARITY,
            2,
            reason=f"{len(walls)} wall-of-text paragraph(s).",
            problem="Wall-of-text paragraphs",
        )
    if article.sentence_count > 0:
        avg = article.word_count / article.sentence_count
        if avg > 28:
            deduct(
                score,
                Dimension.CLARITY,
                2,
                reason=f"Average sentence length {avg:.0f} words is high.",
                problem="Dense prose",
                recommendation="Aim for varied rhythm; average under ~22 words.",
            )


def _review_evidence(article: Article, score: EditorialScore, issues: list[ReviewIssue]) -> None:
    prose = "\n".join(s.body for s in article.sections)
    unverified = [m.group(0) for m in _UNVERIFIED_CLUE_RE.finditer(prose)]
    if unverified:
        issues.append(
            ReviewIssue(
                dimension=Dimension.EVIDENCE,
                severity=Severity.MAJOR,
                title="Unsupported appeal-to-authority claims",
                detail=f"Found {len(unverified)} phrase(s) like 'studies show' / 'most "
                f"engineers' without a source: {', '.join(sorted(set(unverified))[:4])}.",
                suggestion="Cite the actual study/source, or soften the claim and mark it "
                "as your observation.",
                rule_class=RuleClass.HEURISTIC,
            )
        )
        deduct(
            score,
            Dimension.EVIDENCE,
            4,
            reason=f"{len(unverified)} unsupported appeal-to-authority phrase(s).",
            problem="Unsupported claims",
            recommendation="Cite or soften.",
        )
        issues.append(
            ReviewIssue(
                dimension=Dimension.TECHNICAL_ACCURACY,
                severity=Severity.MAJOR,
                title="Factual-sounding claims presented without verifiable support",
                detail="Claims in the 'studies show' class read as fact but cannot be "
                "checked by the reader.",
                suggestion="Either cite the primary source or rephrase as an explicit "
                "observation/assumption.",
                rule_class=RuleClass.HEURISTIC,
            )
        )
        deduct(
            score,
            Dimension.TECHNICAL_ACCURACY,
            3,
            reason=f"{len(unverified)} factual-sounding claim(s) without verifiable support.",
            problem="Unverifiable claims stated as fact",
            recommendation="Cite or rephrase as observation.",
        )
    numbers = re.findall(
        r"\b\d+(?:\.\d+)?(?:%|ms|s\b|x faster|qps|rps|GB|MB|users|requests)\b", prose, re.IGNORECASE
    )
    # The author's own measurements are evidence, not a sourcing problem.
    own_measurement = bool(
        re.search(
            r"\b(i benchmarked|we benchmarked|i measured|we measured|our benchmark|"
            r"my benchmark|i profiled|we profiled|on (my|our) (staging|test|laptop|machine)|"
            r"in (my|our) (tests?|benchmark))\b",
            prose,
            re.IGNORECASE,
        )
    )
    linked_claims = len(article.links)
    if len(numbers) >= 4 and linked_claims == 0 and not own_measurement:
        issues.append(
            ReviewIssue(
                dimension=Dimension.EVIDENCE,
                severity=Severity.MAJOR,
                title="Numbers without sources",
                detail=f"{len(numbers)} numeric claims but zero links/citations in the article.",
                suggestion="Add sources for quantitative claims, or mark them as your own "
                "measurements with the setup described.",
                rule_class=RuleClass.HEURISTIC,
            )
        )
        deduct(
            score,
            Dimension.EVIDENCE,
            4,
            reason=f"{len(numbers)} numeric claims with no linked evidence.",
            problem="Numbers without sources",
        )
    elif len(numbers) >= 2 and linked_claims <= 1 and not own_measurement:
        deduct(
            score,
            Dimension.EVIDENCE,
            2,
            reason=f"{len(numbers)} numeric claims with at most one source link.",
            problem="Thin sourcing",
            recommendation="Cite primary sources for load-bearing numbers.",
        )


def _review_ai_patterns(article: Article, score: EditorialScore, issues: list[ReviewIssue]) -> None:
    density = ai_pattern_density_per_1000(article)
    if density < 3:
        return
    # Tier the finding: heavy generic phrasing is also an originality problem
    # (Medium lists "unoriginal, derivative, and generic content" as a General
    # Distribution disqualifier), and extreme density is critical.
    if density >= 100:
        severity, clarity_pts, originality_pts = Severity.CRITICAL, 6, 10
    elif density >= 50:
        severity, clarity_pts, originality_pts = Severity.MAJOR, 5, 7
    elif density >= 20:
        severity, clarity_pts, originality_pts = Severity.MAJOR, 4, 4
    else:
        severity, clarity_pts, originality_pts = Severity.MINOR, 2, 0
    hits = find_ai_patterns(_prose_of(article))
    examples = ", ".join(f"'{h.phrase}' (line {h.line})" for h in hits[:3])
    title = (
        f"Generic AI-sounding phrasing detected ({len(hits)} hits, {density:.1f} per 1000 words)"
    )
    suggestion = (
        "Replace generic phrasing with your own specifics: concrete numbers, "
        "named tools, what you actually observed. Say it the way you'd say "
        "it to a colleague."
    )
    issues.append(
        ReviewIssue(
            dimension=Dimension.CLARITY,
            severity=severity,
            title=title,
            detail=f"Most frequent patterns; examples: {examples}",
            suggestion=suggestion,
            rule_class=RuleClass.HEURISTIC,
        )
    )
    deduct(
        score,
        Dimension.CLARITY,
        clarity_pts,
        reason=f"Generic AI-sounding phrasing at {density:.0f} per 1000 words.",
        problem="Generic AI-sounding phrasing",
        recommendation=suggestion,
    )
    if originality_pts:
        issues.append(
            ReviewIssue(
                dimension=Dimension.ORIGINALITY,
                severity=severity,
                title="Generic content risks the distribution-disqualifier bucket",
                detail="Medium's distribution guidelines list 'unoriginal, derivative, "
                "and generic content' as ineligible for General Distribution. Generic "
                "AI-cadence phrasing is the most common way strong ideas end up there.",
                suggestion=suggestion,
                rule_class=RuleClass.POLICY,
            )
        )
        deduct(
            score,
            Dimension.ORIGINALITY,
            originality_pts,
            reason=f"Generic phrasing density {density:.0f}/1000 words.",
            problem="Generic content risk",
            recommendation=suggestion,
        )


def _prose_of(article: Article) -> str:
    lines: list[str] = []
    in_fence = False
    for section in article.sections:
        for line in section.body.split("\n"):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if not in_fence:
                lines.append(line)
    return "\n".join(lines)


def _review_manipulation(
    article: Article, score: EditorialScore, issues: list[ReviewIssue]
) -> None:
    """Misinformation-style rhetoric: hidden-truth framing, conspiracy
    claims, false urgency. These are distribution disqualifiers on Medium
    (misleading content) and always accompany weak evidence."""
    prose = "\n".join(s.body for s in article.sections)
    hits = find_manipulation_patterns(prose)
    if not hits:
        return
    examples = ", ".join(f"'{h.phrase}' (line {h.line})" for h in hits[:3])
    issues.append(
        ReviewIssue(
            dimension=Dimension.TECHNICAL_ACCURACY,
            severity=Severity.CRITICAL,
            title="Misinformation-style framing detected",
            detail=f"{len(hits)} manipulation pattern(s): {examples}. Hidden-truth/"
            "conspiracy framing is a hallmark of fabricated claims and is treated "
            "as misleading content under Medium's distribution guidelines.",
            suggestion="Remove the conspiracy framing entirely. If there is a real "
            "problem, state it plainly with verifiable evidence and name the "
            "trade-offs honestly.",
            rule_class=RuleClass.POLICY,
        )
    )
    deduct(
        score,
        Dimension.TECHNICAL_ACCURACY,
        10,
        reason=f"Misinformation-style framing ({len(hits)} manipulation patterns).",
        problem="Conspiracy/hidden-truth framing",
        recommendation="Rewrite plainly with verifiable evidence.",
    )
    deduct(
        score,
        Dimension.EVIDENCE,
        4,
        reason="Conspiracy framing substitutes narrative for evidence.",
        problem="Narrative instead of evidence",
    )
    deduct(
        score,
        Dimension.READER_VALUE,
        4,
        reason="Manipulative framing wastes the reader's time and erodes trust.",
        problem="Manipulative framing",
    )


def _review_examples_and_code(
    article: Article,
    score: EditorialScore,
    issues: list[ReviewIssue],
    spec: ArticleTypeSpec | None,
) -> None:
    if spec and spec.expects_examples and not article.code_blocks and not article.images:
        issues.append(
            ReviewIssue(
                dimension=Dimension.EVIDENCE,
                severity=Severity.MINOR,
                title="No examples or code",
                detail=f"A {spec.label.lower()} is expected to show, not just tell.",
                suggestion="Add at least one concrete example, code sample, or diagram.",
                rule_class=RuleClass.HEURISTIC,
            )
        )
        deduct(
            score,
            Dimension.EVIDENCE,
            3,
            reason="No examples/code/images in an example-driven type.",
            problem="Nothing concrete shown",
        )
    if spec and spec.expects_actionable_steps and article.code_blocks:
        # Check for verification points near code blocks ("you should see").
        text = "\n".join(s.body for s in article.sections).lower()
        if not re.search(
            r"\b(you should see|expected output|verify|check that|should now)\b", text
        ):
            issues.append(
                ReviewIssue(
                    dimension=Dimension.TECHNICAL_ACCURACY,
                    severity=Severity.MINOR,
                    title="No verification points after code/steps",
                    detail="Tutorials earn trust by telling readers what success looks like "
                    "after each step.",
                    suggestion="After key steps, add 'you should see ...' verification.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
            deduct(
                score,
                Dimension.TECHNICAL_ACCURACY,
                2,
                reason="Tutorial steps lack verification points.",
                problem="No verification points",
            )
    # Unlabeled code blocks.
    unlabeled = [c for c in article.code_blocks if not c.language]
    if unlabeled:
        issues.append(
            ReviewIssue(
                dimension=Dimension.TECHNICAL_ACCURACY,
                severity=Severity.INFO,
                title=f"{len(unlabeled)} code block(s) without a language tag",
                detail="Medium renders tagged code blocks with highlighting.",
                suggestion="Tag fenced blocks (```python, ```bash, ...).",
                rule_class=RuleClass.RECOMMENDATION,
            )
        )


def _review_length(
    article: Article, score: EditorialScore, issues: list[ReviewIssue], spec: ArticleTypeSpec | None
) -> None:
    if spec and article.word_count > 0:
        if article.word_count < spec.min_reasonable_words:
            issues.append(
                ReviewIssue(
                    dimension=Dimension.READER_VALUE,
                    severity=Severity.MINOR,
                    title=f"Short for a {spec.label.lower()}",
                    detail=f"{article.word_count} words; the type usually needs "
                    f"{spec.min_reasonable_words}+ to deliver on its purpose.",
                    suggestion="Either expand the substance or narrow the promise.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )
            deduct(
                score,
                Dimension.READER_VALUE,
                2,
                reason=f"Length ({article.word_count} words) below the type's "
                f"deliverable range for a {spec.label.lower()}.",
                problem="Thin for the type",
            )
        elif article.word_count > spec.max_reasonable_words * 1.5:
            issues.append(
                ReviewIssue(
                    dimension=Dimension.READER_VALUE,
                    severity=Severity.INFO,
                    title=f"Very long for a {spec.label.lower()}",
                    detail=f"{article.word_count} words vs. a typical range of "
                    f"{spec.min_reasonable_words}-{spec.max_reasonable_words}.",
                    suggestion="Check every section earns its length; consider splitting.",
                    rule_class=RuleClass.HEURISTIC,
                )
            )


def _review_contribution(
    article: Article,
    contribution: HumanContribution,
    score: EditorialScore,
    issues: list[ReviewIssue],
) -> None:
    spec = get_article_type(article.effective_article_type)
    if contribution_is_sufficient(contribution, spec):
        credit_strength(
            score,
            Dimension.VOICE,
            strength=f"Author contribution present ({', '.join(contribution.kinds[:3])}).",
        )
    else:
        issues.append(
            ReviewIssue(
                dimension=Dimension.VOICE,
                severity=Severity.MAJOR,
                title="This article currently lacks a distinctive author contribution",
                detail="No first-hand experience, experiment, original example, decision, "
                "or defensible position was detected in the text.",
                suggestion="; ".join(contribution.suggestions[:3]),
                rule_class=RuleClass.HEURISTIC,
            )
        )
        deduct(
            score,
            Dimension.VOICE,
            6,
            reason="No distinctive author contribution detected.",
            problem="Missing author contribution",
            recommendation="Add your experience, data, or position.",
        )
    # First-person mismatch with the type.
    if spec and not spec.expects_first_person:
        prose = "\n".join(s.body for s in article.sections)
        first_person = len(re.findall(r"\b(I|we|my|our)\b", prose))
        if first_person == 0:
            deduct(
                score,
                Dimension.VOICE,
                2,
                reason="No author presence at all; even technical explainers benefit "
                "from one honest 'I measured / I chose'.",
                problem="No author presence",
                recommendation="Add one place where your judgment enters.",
            )


def _recommended_changes(issues: list[ReviewIssue]) -> list[str]:
    """Deduplicated, priority-ordered actionable changes."""
    seen: set[str] = set()
    changes: list[str] = []
    for issue in issues:
        if issue.suggestion and issue.suggestion not in seen:
            seen.add(issue.suggestion)
            label = {
                Severity.CRITICAL: "CRITICAL",
                Severity.MAJOR: "HIGH",
                Severity.MINOR: "MEDIUM",
                Severity.INFO: "LOW",
            }[issue.severity]
            changes.append(f"[{label}] {issue.suggestion}")
    return changes


def _verdict_explanation(
    verdict: Verdict, score: EditorialScore, critical: list[ReviewIssue]
) -> str:
    if verdict is Verdict.DO_NOT_PUBLISH_YET and critical:
        return (
            f"{len(critical)} critical issue(s) must be fixed before publishing: "
            + "; ".join(i.title for i in critical[:3])
            + "."
        )
    if verdict is Verdict.DO_NOT_PUBLISH_YET:
        return (
            f"Editorial Quality Score {score.total}/100 is below the publish "
            "threshold (70). Address the recommended changes first."
        )
    if verdict is Verdict.READY_AFTER_CHANGES:
        return (
            f"Editorial Quality Score {score.total}/100. Solid foundation; fix the "
            "high-priority items, then publish."
        )
    return (
        f"Editorial Quality Score {score.total}/100. Meets Article Craft's "
        "editorial bar. This is an editorial judgment, not a prediction of "
        "Medium distribution."
    )


__all__ = ["review_article"]
