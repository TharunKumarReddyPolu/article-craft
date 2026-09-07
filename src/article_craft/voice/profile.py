"""Voice profile extraction (spec §20).

Analyzes the author's own existing articles and produces an advisory
WritingProfile + voice.md. Statistical and heuristic — the profile describes
patterns, it doesn't imitate anyone. The voice system is intended for the
user's OWN writing; never use it to imitate another person's style from a
copyrighted source.
"""

from __future__ import annotations

import itertools
import re
import statistics
from collections import Counter
from pathlib import Path

from article_craft.models.voice import WritingProfile
from article_craft.parsing import ArticleParseError, parse_article_text, sentences_of

FIRST_PERSON_RE = re.compile(r"\b(I|me|my|mine|we|our|us)\b", re.IGNORECASE)
SECOND_PERSON_RE = re.compile(r"\b(you|your|yours)\b", re.IGNORECASE)
HEDGE_RE = re.compile(
    r"\b(maybe|perhaps|possibly|arguably|somewhat|kind of|sort of|might|may|"
    r"it seems|probably|presumably)\b",
    re.IGNORECASE,
)
FILLER_ADVERB_RE = re.compile(
    r"\b(very|really|quite|extremely|actually|basically|literally|simply|just|totally)\b",
    re.IGNORECASE,
)
EXAMPLE_RE = re.compile(
    r"\b(for example|for instance|e\.g\.|let'?s (say|take)|suppose|consider (a|the)|"
    r"in practice|a real (example|case))\b",
    re.IGNORECASE,
)
ANALOGY_RE = re.compile(
    r"\b(like a|like an|as if|think of it (as|like)|it's (kind of )?like|"
    r"analogous to|similar to)\b",
    re.IGNORECASE,
)
QUESTION_RE = re.compile(r"\?\s*$", re.MULTILINE)
PERSONAL_STORY_RE = re.compile(
    r"\b(last (year|week|month)|when i (worked|was|built|joined)|at my|in my (last|previous|current)|"
    r"a few (years|months|weeks) ago)\b",
    re.IGNORECASE,
)


def _prose(text: str) -> str:
    """Body text without code fences."""
    lines = []
    in_fence = False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def build_profile_from_text(texts: list[tuple[str, str]]) -> WritingProfile:
    """Build a profile from (name, markdown_text) pairs."""
    all_sentences: list[str] = []
    total_words = 0
    total_first = 0
    total_second = 0
    total_hedge = 0
    total_adverb = 0
    total_examples = 0
    total_analogies = 0
    total_questions = 0
    total_lists = 0
    total_code = 0
    total_images = 0
    section_lengths: list[int] = []
    paragraph_sizes: list[list[str]] = []
    headings: list[str] = []
    words_counter: Counter[str] = Counter()
    personal_markers = 0

    for _name, text in texts:
        article = parse_article_text(text)
        prose = _prose(text)
        word_list = re.findall(r"\b[\w'-]+\b", prose)
        words = len(word_list)
        total_words += words
        words_counter.update(w.lower().strip(".,!?;:'\"()") for w in word_list)
        all_sentences.extend(sentences_of(prose))
        total_first += len(FIRST_PERSON_RE.findall(prose))
        total_second += len(SECOND_PERSON_RE.findall(prose))
        total_hedge += len(HEDGE_RE.findall(prose))
        total_adverb += len(FILLER_ADVERB_RE.findall(prose))
        total_examples += len(EXAMPLE_RE.findall(prose))
        total_analogies += len(ANALOGY_RE.findall(prose))
        total_questions += len(QUESTION_RE.findall(prose))
        total_lists += len(re.findall(r"^\s*[-*+] \S", prose, re.MULTILINE))
        total_code += len(article.code_blocks)
        total_images += len(article.images)
        headings.extend(re.findall(r"^#{2,3}\s+(.+?)\s*$", prose, re.MULTILINE))
        for section in article.sections:
            if section.title:
                section_lengths.append(section.word_count)
        paragraphs = [
            p for p in re.split(r"\n\s*\n", prose) if p.strip() and not p.strip().startswith("#")
        ]
        for p in paragraphs:
            paragraph_sizes.append([s for s in re.split(r"(?<=[.!?])\s+", p.strip()) if s.strip()])
        personal_markers += len(PERSONAL_STORY_RE.findall(prose))

    profile = WritingProfile(files_analyzed=len(texts), total_words=total_words)
    if all_sentences:
        lengths = [len(s.split()) for s in all_sentences]
        profile.avg_sentence_length = round(statistics.mean(lengths), 1)
        profile.median_sentence_length = float(statistics.median(lengths))
        profile.long_sentence_ratio = round(
            sum(1 for length in lengths if length > 35) / len(lengths), 3
        )
    if paragraph_sizes:
        profile.avg_paragraph_sentences = round(statistics.mean(len(p) for p in paragraph_sizes), 1)
    if total_words:
        per100 = 100.0 / total_words
        per1000 = 1000.0 / total_words
        profile.first_person_rate = round(total_first * per100, 2)
        profile.second_person_rate = round(total_second * per100, 2)
        profile.hedging_rate = round(total_hedge * per100, 2)
        profile.adverb_rate = round(total_adverb * per100, 2)
        profile.example_markers_per_1000_words = round(total_examples * per1000, 2)
        profile.analogy_markers_per_1000_words = round(total_analogies * per1000, 2)
        profile.questions_per_1000_words = round(total_questions * per1000, 2)
        profile.list_usage_per_1000_words = round(total_lists * per1000, 2)
        profile.code_blocks_per_1000_words = round(total_code * per1000, 2)
        profile.images_per_1000_words = round(total_images * per1000, 2)
    if section_lengths:
        profile.avg_words_per_1000_between_headings = round(statistics.mean(section_lengths), 0)
    profile.heading_style = _heading_style(headings)

    # Derived tone label (heuristic).
    if total_words == 0:
        profile.tone = "unknown"
    elif profile.first_person_rate >= 4.0 or personal_markers >= 2:
        profile.tone = "personal-narrative"
    elif profile.second_person_rate >= 2.0 or profile.first_person_rate >= 1.0:
        profile.tone = "conversational-technical"
    else:
        profile.tone = "formal-technical"

    # Derived technical depth (heuristic from code density + jargon surface).
    if profile.code_blocks_per_1000_words >= 4 or total_code >= 5:
        profile.technical_depth = "advanced"
    elif profile.code_blocks_per_1000_words >= 1:
        profile.technical_depth = "intermediate"
    else:
        profile.technical_depth = "beginner"

    stop = _stopwords()
    profile.top_content_words = [
        w for w, _c in words_counter.most_common(40) if len(w) > 3 and w not in stop
    ][:12]
    # Signature phrases: recurring 2-grams that aren't stopword pairs.
    profile.signature_phrases = _signature_phrases(texts)
    return profile


def _heading_style(headings: list[str]) -> str:
    if not headings:
        return "unknown"
    title_case = sum(1 for h in headings if h == h.title() and any(c.isupper() for c in h))
    sentence_case = sum(1 for h in headings if h[:1].isupper() and sum(c.isupper() for c in h) <= 2)
    if title_case >= len(headings) * 0.7:
        return "Title Case"
    if sentence_case >= len(headings) * 0.7:
        return "sentence case"
    return "mixed"


def _signature_phrases(texts: list[tuple[str, str]]) -> list[str]:
    bigrams: Counter[str] = Counter()
    for _name, text in texts:
        prose = _prose(text).lower()
        words = re.findall(r"[a-z']+", prose)
        for a, b in itertools.pairwise(words):
            if len(a) > 3 and len(b) > 3 and a not in _stopwords() and b not in _stopwords():
                bigrams[f"{a} {b}"] += 1
    return [phrase for phrase, count in bigrams.most_common(8) if count >= 3]


_STOP_CACHE: frozenset[str] | None = None


def _stopwords() -> frozenset[str]:
    global _STOP_CACHE
    if _STOP_CACHE is None:
        from article_craft.parsing import STOPWORDS

        _STOP_CACHE = STOPWORDS
    return _STOP_CACHE


def build_profile_from_directory(
    directory: str | Path,
) -> tuple[WritingProfile, list[str], list[str]]:
    """Build a profile from a directory of markdown articles.

    Returns (profile, parsed_files, skipped_files). Raises ArticleParseError
    only for systemic problems (e.g. directory missing); individual bad files
    are skipped with a note.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise ArticleParseError(
            f"Could not analyze '{dir_path}' because it is not a directory. "
            "Pass a folder containing your markdown articles, e.g. "
            "'article-craft learn ./my-articles/'."
        )
    md_files = sorted(dir_path.rglob("*.md"))
    md_files = [p for p in md_files if p.name.upper() != "README.MD"]
    if not md_files:
        raise ArticleParseError(
            f"No markdown files found in '{dir_path}'. Add .md articles and retry."
        )
    texts: list[tuple[str, str]] = []
    parsed: list[str] = []
    skipped: list[str] = []
    for path in md_files:
        try:
            texts.append((path.name, path.read_text(encoding="utf-8")))
            parsed.append(str(path))
        except (ArticleParseError, UnicodeDecodeError) as exc:
            skipped.append(f"{path}: {exc}")
    if not texts:
        raise ArticleParseError(
            f"None of the {len(md_files)} markdown files in '{dir_path}' could be "
            "parsed. Check that they are UTF-8 markdown files."
        )
    return build_profile_from_text(texts), parsed, skipped
