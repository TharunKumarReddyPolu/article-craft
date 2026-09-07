"""Unit tests for the markdown parser (article_craft.parsing)."""

from __future__ import annotations

import pytest

from article_craft.parsing import (
    ArticleParseError,
    count_sentences,
    parse_article_text,
    word_count,
)

FULL_ARTICLE = """---
title: Kafka for the impatient
subtitle: Exactly-once is not what you think
audience: backend engineers
article_type: technical-explainer
platform: medium
topics: [kafka, streaming]
ai_assistance: assistive
---

# Kafka for the impatient
**Exactly-once is not what you think**

Kafka's exactly-once semantics are widely misunderstood. I learned this the
hard way, and it cost us a weekend.

## How ordering actually works

Ordering is guaranteed only within a partition. Here is the setup:

```python
producer.send(topic, key=user_id, value=event)
```

See [the docs](https://kafka.apache.org/documentation/) for details.

### Sub-point

Something else entirely.

## Gotchas

Watch out for rebalances. ![diagram](https://example.com/d.png)
*Figure 1: partition layout.*

Ping @devrel if questions remain.
"""


def test_parse_full_article_frontmatter() -> None:
    article = parse_article_text(FULL_ARTICLE, path="test.md")
    assert article.effective_title == "Kafka for the impatient"
    assert article.effective_subtitle == "Exactly-once is not what you think"
    assert article.effective_article_type == "technical-explainer"
    assert article.frontmatter.ai_assistance == "assistive"
    assert article.frontmatter.topics == ["kafka", "streaming"]


def test_parse_sections() -> None:
    article = parse_article_text(FULL_ARTICLE)
    titles = [s.title for s in article.sections]
    assert titles[0] is None or titles[0]  # intro may be collapsed if empty
    assert "How ordering actually works" in [t for t in titles if t]
    assert "Gotchas" in [t for t in titles if t]
    # H3 stays inside its parent H2:
    ordering = article.section_by_title("How ordering")
    assert ordering is not None
    assert ordering.subheading_count == 1
    assert ordering.has_code


def test_code_excluded_from_word_count() -> None:
    with_code = "Hello world.\n\n```python\nx = 'a b c d e f g h i j k l m n o p'\n```\n"
    without_code = "Hello world."
    assert parse_article_text(with_code).word_count == parse_article_text(without_code).word_count


def test_links_images_mentions() -> None:
    article = parse_article_text(FULL_ARTICLE)
    assert article.links[0].text == "the docs"
    assert article.links[0].url == "https://kafka.apache.org/documentation/"
    assert article.images[0].alt == "diagram"
    assert article.images[0].caption == "Figure 1: partition layout."
    assert article.mentions == ["devrel"]


def test_subtitle_detection_bold_line() -> None:
    text = "# My Title\n**A bold subtitle here**\n\nBody starts."
    article = parse_article_text(text)
    assert article.effective_subtitle == "A bold subtitle here"


def test_no_subtitle_when_first_line_is_prose() -> None:
    text = "# My Title\n\nStraight into prose."
    article = parse_article_text(text)
    assert article.effective_subtitle is None


def test_frontmatter_without_delimiters_is_ignored() -> None:
    text = "No frontmatter here.\n\n# Title\n\nBody."
    article = parse_article_text(text)
    assert article.frontmatter.title is None
    assert article.title == "Title"


def test_malformed_frontmatter_raises_actionable_error() -> None:
    text = "---\ntitle: [unclosed\n---\n\nBody."
    with pytest.raises(ArticleParseError, match="frontmatter"):
        parse_article_text(text)


def test_frontmatter_non_mapping_raises() -> None:
    text = "---\n- just\n- a list\n---\n\nBody."
    with pytest.raises(ArticleParseError, match="mapping"):
        parse_article_text(text)


def test_word_count_and_sentences() -> None:
    assert word_count("Hello, world! One two-three.") == 4
    assert count_sentences("First one. Second one! Third?") == 3


def test_reading_time_is_sane() -> None:
    article = parse_article_text(FULL_ARTICLE)
    assert 0 < article.reading_time_minutes < 5


def test_empty_article() -> None:
    article = parse_article_text("")
    assert article.word_count == 0
    assert article.effective_title == "(untitled)"
    assert article.sections == []
