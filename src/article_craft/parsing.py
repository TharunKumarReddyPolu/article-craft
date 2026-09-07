"""Markdown parsing: turn an article markdown file into the canonical Article
model.

Deterministic and dependency-free. Handles:
- YAML frontmatter (``---`` delimited) via PyYAML
- H1 title and Medium-style subtitle detection
- H2 sections (H3+ stay inside their parent H2)
- prose statistics that exclude code blocks
- links, images (with alt-text detection), code blocks, @mentions
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from article_craft.models.article import (
    Article,
    ArticleFrontmatter,
    CodeBlock,
    ImageRef,
    Link,
    Section,
)

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n?---\s*\n?", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$", re.MULTILINE)
LINK_RE = re.compile(r"(?<!\!)\[([^\]\n]+)\]\(([^)\s]+)\)")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
MENTION_RE = re.compile(r"(?<![\w.])@([A-Za-z0-9_-]{2,})\b")
FENCE_RE = re.compile(r"^```(\w*)[ \t]*$", re.MULTILINE)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])[\"')\]]*\s+")
BOLD_LINE_RE = re.compile(r"^\*\*(.+?)\*\*\s*$")
ITALIC_LINE_RE = re.compile(r"^\*(.+?)\*\s*$")
CAPTION_RE = re.compile(r"^\*(.+?)\*\s*$")

# Words excluded from "top content words" in the voice profile.
STOPWORDS: frozenset[str] = frozenset(
    [
        "a",
        "about",
        "above",
        "after",
        "again",
        "against",
        "all",
        "am",
        "an",
        "and",
        "any",
        "are",
        "aren't",
        "as",
        "at",
        "be",
        "because",
        "been",
        "before",
        "being",
        "below",
        "between",
        "both",
        "but",
        "by",
        "can",
        "cannot",
        "could",
        "couldn't",
        "did",
        "didn't",
        "do",
        "does",
        "doesn't",
        "doing",
        "don't",
        "down",
        "during",
        "each",
        "few",
        "for",
        "from",
        "further",
        "had",
        "hadn't",
        "has",
        "hasn't",
        "have",
        "haven't",
        "having",
        "he",
        "her",
        "here",
        "hers",
        "herself",
        "him",
        "himself",
        "his",
        "how",
        "i",
        "i'd",
        "i'll",
        "i'm",
        "i've",
        "if",
        "in",
        "into",
        "is",
        "isn't",
        "it",
        "it's",
        "its",
        "itself",
        "let's",
        "me",
        "more",
        "most",
        "mustn't",
        "my",
        "myself",
        "no",
        "nor",
        "not",
        "of",
        "off",
        "on",
        "once",
        "only",
        "or",
        "other",
        "ought",
        "our",
        "ours",
        "ourselves",
        "out",
        "over",
        "own",
        "same",
        "shan't",
        "she",
        "should",
        "shouldn't",
        "so",
        "some",
        "such",
        "than",
        "that",
        "the",
        "their",
        "theirs",
        "them",
        "themselves",
        "then",
        "there",
        "these",
        "they",
        "this",
        "those",
        "through",
        "to",
        "too",
        "under",
        "until",
        "up",
        "very",
        "was",
        "wasn't",
        "we",
        "were",
        "weren't",
        "what",
        "when",
        "where",
        "which",
        "while",
        "who",
        "whom",
        "why",
        "with",
        "won't",
        "would",
        "wouldn't",
        "you",
        "your",
        "yours",
        "yourself",
        "yourselves",
        "it's",
        "they're",
        "we're",
        "you're",
        "that's",
        "there's",
    ]
)


class ArticleParseError(ValueError):
    """Raised when an article file cannot be parsed. Message is actionable."""


def read_article_text(path: str | Path) -> str:
    """Read a file with an actionable error for invalid UTF-8 / missing files."""
    file_path = Path(path)
    if not file_path.exists():
        raise ArticleParseError(
            f"Could not find '{file_path}'. "
            "Pass the path to an existing markdown article, e.g. 'article-craft review article.md'."
        )
    if file_path.is_dir():
        raise ArticleParseError(
            f"'{file_path}' is a directory, not an article file. Pass the path to a markdown file."
        )
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ArticleParseError(
            f"Could not parse '{file_path}' because the file is not valid UTF-8 "
            f"(byte offset {exc.start}). Re-save the file as UTF-8 and retry."
        ) from exc


def strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks (replaced with a placeholder line) so prose
    statistics and sentence splitting don't choke on code."""
    return FENCE_RE.sub("```", text)  # keep markers for splitting below


def split_prose_and_code(text: str) -> tuple[str, int]:
    """Return (prose-only text, number of fenced code blocks)."""
    lines = text.split("\n")
    prose_lines: list[str] = []
    in_fence = False
    code_count = 0
    for line in lines:
        if line.strip().startswith("```"):
            if not in_fence:
                code_count += 1
            in_fence = not in_fence
            continue
        if not in_fence:
            prose_lines.append(line)
    return "\n".join(prose_lines), code_count


def parse_frontmatter(text: str) -> tuple[ArticleFrontmatter, str]:
    """Split frontmatter from body. Malformed YAML raises ArticleParseError."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return ArticleFrontmatter(), text
    raw = match.group(1)
    body = text[match.end() :]
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ArticleParseError(
            f"Could not parse the YAML frontmatter: {exc}. "
            "Fix the frontmatter block between the opening and closing '---' lines."
        ) from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ArticleParseError(
            "Frontmatter must be a YAML mapping (key: value lines), got "
            f"{type(data).__name__}. Example:\n---\ntitle: My article\n---"
        )
    known = {
        key: data.pop(key)
        for key in (
            "title",
            "subtitle",
            "author",
            "audience",
            "article_type",
            "platform",
            "topics",
            "canonical_url",
            "originally_published",
            "ai_assistance",
            "ai_assistance_note",
            "research_file",
        )
        if key in data
    }
    if "topics" in known and known["topics"] is None:
        known["topics"] = []
    if "originally_published" in known and isinstance(known["originally_published"], str):
        known["originally_published"] = known["originally_published"].lower() in ("true", "yes")
    try:
        frontmatter = ArticleFrontmatter(**known, extra=data)
    except Exception as exc:
        raise ArticleParseError(f"Invalid frontmatter value: {exc}") from exc
    return frontmatter, body


def count_sentences(prose: str) -> int:
    """Count sentences, skipping headings and list markers."""
    body_lines = [
        line
        for line in prose.split("\n")
        if line.strip()
        and not line.strip().startswith("#")
        and not line.strip().startswith(("-", "*", "+", ">"))
    ]
    joined = " ".join(line.strip() for line in body_lines)
    if not joined.strip():
        return 0
    candidates = [s for s in SENTENCE_SPLIT_RE.split(joined) if s.strip()]
    return max(1, len(candidates)) if candidates else 0


def sentences_of(prose: str) -> list[str]:
    """Split prose into sentences (used by the voice profile)."""
    body_lines = [
        line
        for line in prose.split("\n")
        if line.strip()
        and not line.strip().startswith("#")
        and not line.strip().startswith(("-", "*", "+", ">"))
    ]
    joined = " ".join(line.strip() for line in body_lines)
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(joined) if s.strip()]


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def detect_subtitle(body: str, h1_match: re.Match[str] | None) -> str | None:
    """Medium-style subtitle: a short bold/italic line, or a short H2
    immediately after the H1 with body content following it."""
    if h1_match is None:
        return None
    after = body[h1_match.end() :].lstrip("\n")
    lines = after.split("\n")
    for line in lines[:3]:  # only look at the first few lines after H1
        stripped = line.strip()
        if not stripped:
            continue
        bold = BOLD_LINE_RE.match(stripped)
        if bold and 0 < len(bold.group(1)) <= 200:
            return bold.group(1)
        italic = ITALIC_LINE_RE.match(stripped)
        if italic and 0 < len(italic.group(1)) <= 200:
            return italic.group(1)
        h2 = re.match(r"^##\s+(.+?)\s*$", stripped)
        if h2 and 0 < len(h2.group(1)) <= 200:
            # Only treat as subtitle if it doesn't look like a section heading
            # (heuristic: subtitle lines rarely end with ':' or start with a number).
            text = h2.group(1)
            if not text.endswith(":") and not re.match(r"^\d+[.)]", text):
                return text
        return None  # first real line is neither subtitle marker nor H2 -> no subtitle
    return None


def build_sections(body: str) -> list[Section]:
    """Split the body into intro + H2 sections. H3+ remain in the parent body."""
    lines = body.split("\n")
    boundaries: list[tuple[int, str | None]] = []  # (line_index, title)
    boundaries.append((0, None))
    for idx, line in enumerate(lines):
        h2 = re.match(r"^##\s+(?!#)(.+?)\s*$", line)
        if h2:
            boundaries.append((idx, h2.group(1)))
            h2.group(1)
    sections: list[Section] = []
    for i, (start, title) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(lines)
        chunk = "\n".join(lines[start:end])
        prose, _ = split_prose_and_code(chunk)
        subheadings = len(re.findall(r"^###\s+", chunk, re.MULTILINE))
        sections.append(
            Section(
                title=title,
                body=chunk,
                word_count=word_count(prose),
                start_line=start + 1,
                end_line=end,
                has_code=bool(re.search(r"^```", chunk, re.MULTILINE)),
                has_image=bool(IMAGE_RE.search(chunk)),
                subheading_count=subheadings,
            )
        )
    # Drop sections that have no content at all (e.g. an empty intro before
    # the first H2, or trailing whitespace-only chunks).
    sections = [s for s in sections if s.body.strip()]
    return sections


def detect_heading_style(body: str) -> str:
    headings = re.findall(r"^#{2,3}\s+(.+?)\s*$", body, re.MULTILINE)
    if not headings:
        return "none"
    title_case = sum(1 for h in headings if h == h.title() and any(c.isupper() for c in h))
    sentence_case = sum(
        1
        for h in headings
        if h == h.lower().capitalize() or (h[:1].isupper() and sum(c.isupper() for c in h) <= 2)
    )
    if title_case >= len(headings) * 0.7:
        return "Title Case"
    if sentence_case >= len(headings) * 0.7:
        return "sentence case"
    return "mixed"


def parse_article_text(text: str, path: str | None = None) -> Article:
    """Parse article markdown text into the canonical Article model."""
    frontmatter, body = parse_frontmatter(text)
    h1_match = H1_RE.search(body)
    title = h1_match.group(1) if h1_match else None
    subtitle = detect_subtitle(body, h1_match)

    prose, _code_count = split_prose_and_code(body)
    sections = build_sections(body)

    links = [
        Link(text=link_text, url=url, line=body[: match.start()].count("\n") + 1)
        for match in LINK_RE.finditer(body)
        for link_text, url in [match.groups()]
    ]
    images = []
    for match in IMAGE_RE.finditer(body):
        alt, url = match.groups()
        line_no = body[: match.start()].count("\n") + 1
        caption = None
        # Medium convention: an italic line right after the image is a caption.
        following = body[match.end() :].lstrip(" \n").split("\n")
        if following:
            cap = CAPTION_RE.match(following[0].strip())
            if cap:
                caption = cap.group(1)
        images.append(ImageRef(alt=alt, url=url, line=line_no, caption=caption))
    code_blocks = []
    for match in FENCE_RE.finditer(body):
        chunk = _fenced_block(body, match.start())
        if not chunk:
            continue
        fence_match = FENCE_RE.match(chunk)
        language: str | None = None
        if fence_match:
            language = fence_match.group(1) or None
        code_blocks.append(
            CodeBlock(
                language=language,
                line_count=max(1, chunk.count("\n")),
                line=body[: match.start()].count("\n") + 1,
            )
        )
    mentions = sorted({m.group(1) for m in MENTION_RE.finditer(body)})

    words = word_count(prose)
    return Article(
        path=path,
        frontmatter=frontmatter,
        title=title,
        subtitle=subtitle,
        sections=sections,
        word_count=words,
        sentence_count=count_sentences(prose),
        paragraph_count=len(
            [p for p in re.split(r"\n\s*\n", prose) if p.strip() and not p.strip().startswith("#")]
        ),
        links=links,
        images=images,
        code_blocks=code_blocks,
        mentions=mentions,
        reading_time_minutes=round(words / 220.0, 1),
    )


def _fenced_block(body: str, fence_start: int) -> str | None:
    """Return the code block content for a fence starting at fence_start."""
    closing = body.find("\n```", fence_start + 3)
    if closing == -1:
        return None
    inner_start = body.find("\n", fence_start)
    if inner_start == -1 or inner_start > closing:
        return None
    return body[inner_start + 1 : closing]


def parse_article_file(path: str | Path) -> Article:
    """Read + parse a markdown article file. Raises ArticleParseError with an
    actionable message on unreadable/malformed input."""
    file_path = Path(path)
    text = read_article_text(file_path)
    return parse_article_text(text, path=str(file_path))
