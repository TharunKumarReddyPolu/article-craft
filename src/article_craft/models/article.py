"""Core article models: the canonical, platform-agnostic article representation.

Design principle (one idea -> one canonical article model -> platform-specific
adaptation): nothing in this module knows about Medium or any other platform.
Platform concerns live in ``article_craft.platforms``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

AiAssistance = Literal["none", "assistive", "generated", "unspecified"]

ARTICLE_TYPES: tuple[str, ...] = (
    "technical-tutorial",
    "technical-explainer",
    "system-design",
    "architecture-deep-dive",
    "case-study",
    "personal-experience",
    "opinion",
    "beginner-guide",
    "advanced-guide",
    "listicle",
)

PLATFORMS: tuple[str, ...] = ("medium", "generic")


class Audience(BaseModel):
    """Who the article is for. Free-form so authors can be specific."""

    description: str
    experience_level: Literal["beginner", "intermediate", "advanced", "mixed"] = "mixed"
    primary_goal: str | None = None  # what should the reader be able to do/know


class AuthorProfile(BaseModel):
    """The author's self-declared context (from ``.article-craft/config.yaml``)."""

    name: str | None = None
    experience_level: str | None = None
    topics: list[str] = Field(default_factory=list)
    voice_notes: str | None = None


class Link(BaseModel):
    text: str
    url: str
    line: int


class ImageRef(BaseModel):
    alt: str
    url: str
    line: int
    caption: str | None = None


class CodeBlock(BaseModel):
    language: str | None
    line_count: int
    line: int


class Section(BaseModel):
    """A top-level (H2) section of the article. The intro is a section with
    ``title=None``. H3+ subheadings stay inside their parent H2's body."""

    title: str | None
    body: str
    word_count: int
    start_line: int
    end_line: int
    has_code: bool = False
    has_image: bool = False
    subheading_count: int = 0


class ArticleFrontmatter(BaseModel):
    """Optional YAML frontmatter of an article markdown file."""

    title: str | None = None
    subtitle: str | None = None
    author: str | None = None
    audience: str | None = None
    article_type: str | None = None
    platform: str | None = None
    topics: list[str] = Field(default_factory=list)
    canonical_url: str | None = None
    originally_published: bool = False
    ai_assistance: AiAssistance = "unspecified"
    ai_assistance_note: str | None = None
    research_file: str | None = None
    extra: dict[str, object] = Field(default_factory=dict)


class Article(BaseModel):
    """The canonical article model. Built by ``article_craft.parsing``."""

    path: str | None = None
    frontmatter: ArticleFrontmatter = Field(default_factory=ArticleFrontmatter)
    title: str | None = None
    subtitle: str | None = None
    sections: list[Section] = Field(default_factory=list)
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    links: list[Link] = Field(default_factory=list)
    images: list[ImageRef] = Field(default_factory=list)
    code_blocks: list[CodeBlock] = Field(default_factory=list)
    mentions: list[str] = Field(default_factory=list)
    reading_time_minutes: float = 0.0

    @property
    def effective_title(self) -> str:
        """Frontmatter title, falling back to the H1, falling back to '(untitled)'."""
        return self.frontmatter.title or self.title or "(untitled)"

    @property
    def effective_subtitle(self) -> str | None:
        return self.frontmatter.subtitle or self.subtitle

    @property
    def effective_article_type(self) -> str:
        return self.frontmatter.article_type or "unknown"

    def section_by_title(self, title_substring: str) -> Section | None:
        """Case-insensitive substring match on section titles; 1-based friendly."""
        needle = title_substring.lower()
        for section in self.sections:
            if section.title and needle in section.title.lower():
                return section
        return None
