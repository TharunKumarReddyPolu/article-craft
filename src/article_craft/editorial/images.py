"""Image and alt-text checks (deterministic; no generation).

Every finding is checked, not guessed: this module only inspects the
markdown the author wrote. Alt-text guidance is grounded in official
platform accessibility documentation where it exists (e.g., DEV's Editor
Guide accessibility section, Substack's alt-text help page) and flagged
HEURISTIC elsewhere.

Nothing here generates, fetches, or rewrites images — inspection only.
"""

from __future__ import annotations

import re

from pydantic import BaseModel

from article_craft.models.article import Article
from article_craft.models.review import RuleClass, Severity

# A filename masquerading as alt text: "image.png", "screenshot 2024-05-12",
# "Screen Shot 2023 at 10.44.11 AM", "Untitled design (3)". These carry no
# information for a screen-reader user.
_FILENAME_LIKE = re.compile(
    r"^[\w\-. ()]*\.(png|jpe?g|gif|webp|svg|avif)$|^(screenshot|screen shot|image|picture|untitled)\b",
    re.IGNORECASE,
)

# Common "vague" alt texts that technically exist but say nothing useful.
_VAGUE_ALT = re.compile(
    r"^(diagram|graph|chart|architecture|logo|icon|photo|pic|img|figure|fig)\.?\s*\d*$",
    re.IGNORECASE,
)

ALT_WORD_MIN = 3  # fewer words than this is "vague" territory
ALT_CHAR_MAX = 250  # screen readers truncate rambling alt text


class ImageFinding(BaseModel):
    """One concrete, locatable image issue."""

    code: str  # missing-alt | filename-alt | vague-alt | long-alt | no-caption | prefer-code
    severity: Severity
    message: str
    line: int
    url: str
    rule_class: RuleClass = RuleClass.HEURISTIC
    source_id: str | None = None  # id in a platform sources.yaml, when official


def check_images(article: Article) -> list[ImageFinding]:
    """Inspect every image reference in the article. Deterministic; no
    network. Returns findings sorted by line."""
    findings: list[ImageFinding] = []
    for image in article.images:
        alt = image.alt.strip()
        if not alt:
            findings.append(
                ImageFinding(
                    code="missing-alt",
                    severity=Severity.MAJOR,
                    message=(
                        f"Image at line {image.line} has empty alt text. Screen-reader "
                        "users get nothing from this image; describe what it shows."
                    ),
                    line=image.line,
                    url=image.url,
                    rule_class=RuleClass.BEST_PRACTICE,
                )
            )
        elif _FILENAME_LIKE.match(alt):
            findings.append(
                ImageFinding(
                    code="filename-alt",
                    severity=Severity.MAJOR,
                    message=(
                        f'Alt text at line {image.line} is a filename ("{alt}"). '
                        "Replace it with a description of what the image shows."
                    ),
                    line=image.line,
                    url=image.url,
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        elif _VAGUE_ALT.match(alt) or len(alt.split()) < ALT_WORD_MIN:
            findings.append(
                ImageFinding(
                    code="vague-alt",
                    severity=Severity.MINOR,
                    message=(
                        f'Alt text at line {image.line} ("{alt}") is too vague to be '
                        "useful. Say what the image actually shows, as you would "
                        "explain it aloud."
                    ),
                    line=image.line,
                    url=image.url,
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        elif len(alt) > ALT_CHAR_MAX:
            findings.append(
                ImageFinding(
                    code="long-alt",
                    severity=Severity.MINOR,
                    message=(
                        f"Alt text at line {image.line} is {len(alt)} characters. "
                        f"Keep it under ~{ALT_CHAR_MAX}; move detail into the body "
                        "or a caption."
                    ),
                    line=image.line,
                    url=image.url,
                    rule_class=RuleClass.HEURISTIC,
                )
            )
        if image.caption is None and alt:
            findings.append(
                ImageFinding(
                    code="no-caption",
                    severity=Severity.INFO,
                    message=(
                        f"Image at line {image.line} has no caption. Captions are "
                        "read more than body text; consider one if the image needs "
                        "explanation."
                    ),
                    line=image.line,
                    url=image.url,
                    rule_class=RuleClass.HEURISTIC,
                )
            )
    return sorted(findings, key=lambda f: f.line)


def screenshot_instead_of_code(article: Article) -> ImageFinding | None:
    """Flag articles that explain code via screenshots while never showing a
    real code block: screenshots can't be copied, searched, or diffed."""
    if not article.images or article.code_blocks:
        return None
    screenshot_words = ("screenshot", "screen shot", "snippet", "terminal", "console")
    screenshot_images = [
        image
        for image in article.images
        if any(word in image.alt.lower() for word in screenshot_words)
    ]
    if not screenshot_images:
        return None
    lines = ", ".join(str(image.line) for image in screenshot_images)
    return ImageFinding(
        code="prefer-code",
        severity=Severity.MINOR,
        message=(
            f"The article shows code only as screenshots (lines {lines}). Screenshots "
            "can't be copied, searched, or maintained; use fenced code blocks instead."
        ),
        line=screenshot_images[0].line,
        url=screenshot_images[0].url,
        rule_class=RuleClass.BEST_PRACTICE,
    )


def check_all(article: Article) -> list[ImageFinding]:
    """All image findings: per-image checks plus the screenshot heuristic."""
    findings = check_images(article)
    code_finding = screenshot_instead_of_code(article)
    if code_finding is not None:
        findings.append(code_finding)
    return findings
