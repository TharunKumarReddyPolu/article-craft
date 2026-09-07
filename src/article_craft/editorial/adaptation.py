"""Social adaptation: derive an attributed post from the canonical article.

The canonical article stays primary: every factual statement in the
generated post traces to the article itself, the post always attributes
the source, and nothing is published automatically. No engagement bait,
no fabricated numbers, no invented quotes.
"""

from __future__ import annotations

import re

from article_craft.models.adaptation import SocialPost
from article_craft.models.article import Article

# Hook budget: the first ~2 sentences fit LinkedIn's "see more" fold.
HOOK_MAX_CHARS = 280
POST_MAX_CHARS = 3000  # official LinkedIn post limit (linkedin-post-limits)

_CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)
_MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
_HEADING = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_SENTENCE = re.compile(r"(?<=[.!?])\s+")


def _plain_prose(article: Article) -> list[str]:
    """Paragraphs of the article with markdown constructs flattened to text
    (links keep their anchor text; code fences and images drop out)."""
    paragraphs: list[str] = []
    for section in article.sections:
        for block in re.split(r"\n\s*\n", section.body):
            text = _CODE_FENCE.sub(" ", block)
            text = _MARKDOWN_IMAGE.sub(" ", text)
            text = _MARKDOWN_LINK.sub(r"\1", text)
            text = _HEADING.sub("", text)
            text = re.sub(r"[*_`>#]", "", text)
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                paragraphs.append(text)
    return paragraphs


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE.split(text) if s.strip()]


def _pick_hook(paragraphs: list[str]) -> str:
    """The opening paragraph's first sentence(s), truncated cleanly."""
    if not paragraphs:
        return ""
    hook = paragraphs[0]
    sentences = _sentences(hook)
    candidate = ""
    for sentence in sentences:
        if len(candidate) + len(sentence) + 1 > HOOK_MAX_CHARS and candidate:
            break
        candidate = f"{candidate} {sentence}".strip()
    return candidate or hook[:HOOK_MAX_CHARS].rsplit(" ", 1)[0]


def _pick_insight(paragraphs: list[str]) -> str | None:
    """A substantive middle paragraph — preferably one with a number (a
    measured result from the article) or first-person experience. Never
    invents one; only picks what the article contains."""
    scored: list[tuple[int, str]] = []
    for paragraph in paragraphs[1:]:
        score = 0
        if re.search(r"\d", paragraph):
            score += 2  # concrete numbers/measures
        if re.search(r"\b(i|we|my|our)\b", paragraph, re.IGNORECASE):
            score += 2  # first-hand experience
        if len(paragraph.split()) >= 15:
            score += 1
        scored.append((score, paragraph))
    if not scored:
        return None
    scored.sort(key=lambda pair: -pair[0])
    best = scored[0][1]
    if len(best) > 600:
        best = _sentences(best)[0] if _sentences(best) else best[:600]
    return best


def _hashtags(topics: list[str]) -> list[str]:
    tags: list[str] = []
    for topic in topics[:5]:
        tag = "#" + re.sub(r"[^a-z0-9]", "", topic.lower())
        if len(tag) > 1 and tag not in tags:
            tags.append(tag)
    return tags


def adapt_for_social(article: Article, platform: str = "linkedin") -> SocialPost:
    """Build the attribution-carrying social post from the canonical article.

    Deterministic: same article in, same post out. Claims come only from
    the article; the attribution line names it; nothing is auto-posted.
    """
    paragraphs = _plain_prose(article)
    hook = _pick_hook(paragraphs)
    insight = _pick_insight(paragraphs)
    title = article.effective_title
    url = article.frontmatter.canonical_url

    attribution = f'From my article: "{title}"'
    if url:
        attribution += f"\n{url}"

    hashtags = _hashtags(article.frontmatter.topics)
    platform_label = "linkedin" if platform == "linkedin" else "generic"

    parts = [part for part in (hook, insight) if part]
    text = "\n\n".join(parts)
    if not text:
        text = f'New article: "{title}"'
    text = f"{text}\n\n{attribution}"
    if hashtags:
        tag_line = " ".join(hashtags)
        if len(text) + 1 + len(tag_line) <= POST_MAX_CHARS:
            text = f"{text}\n\n{tag_line}"
        else:
            # Never silently drop: note the trim in the attribution block.
            text += "\n\n(tags omitted to fit the 3,000-character limit)"
    if len(text) > POST_MAX_CHARS:
        text = text[: POST_MAX_CHARS - 1].rstrip() + "…"

    return SocialPost(
        platform=platform_label,  # type: ignore[arg-type]
        text=text,
        hook=hook or None,
        key_insight=insight,
        attribution=attribution,
        source_title=title,
        source_url=url,
        hashtags=hashtags,
        char_count=len(text),
    )


def render_social_post(post: SocialPost, checks: list[str] | None = None) -> str:
    """Markdown rendering for CLI/file output."""
    lines = [
        f"# Social Post ({post.platform})",
        "",
        "> Adapted from the canonical article — the article stays primary.",
        "Nothing is published automatically; copy this into the platform yourself.",
        "",
        "## Post",
        "",
        post.text,
        "",
        "## Metadata",
        "",
        f"- Source article: {post.source_title or '(unknown)'}",
        f"- Source URL: {post.source_url or '(none set)'}",
        f"- Characters: {post.char_count} / 3,000"
        + ("  **OVER LIMIT**" if post.over_limit else ""),
        f"- Hashtags: {' '.join(post.hashtags) if post.hashtags else '(none)'}",
    ]
    if checks:
        lines += ["", "## Adaptation checks", ""] + [f"- {item}" for item in checks]
    return "\n".join(lines) + "\n"
