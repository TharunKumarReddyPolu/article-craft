# Workflow: Social Adaptation

Use when the author wants a **social post derived from an existing
article** (e.g. a LinkedIn post). The canonical article stays primary.

## Method

1. **Run the adaptation** if the CLI is available:
   `article-craft adapt article.md --platform linkedin` (or `--platform
   generic`). It derives the hook and key insight **from the article
   itself** — never invents claims or numbers — and attributes the source.
2. **Review the adaptation** with the platform check (LinkedIn runs
   adaptation checks: the 3,000-character limit, attribution presence,
   engagement-bait phrasing, hashtag wall).
3. **Add what only the author has**: a first-hand reaction, a lesson, a
   question for readers. The adaptation is a trailer, not the article.
4. **Guardrails (never violate):**
   - Every factual statement must trace to the source article.
   - The post must attribute the article (title + link).
   - No engagement bait ("comment yes", "tag 3 people", "repost if") —
     LinkedIn's official guidance explicitly covers attention-gaming in its
     "AI slop" definition.
   - Publishing is manual: the author copies the post into LinkedIn
     themselves. Never auto-post.
5. **Offer variants**: a pure-teaser post (hook + link) and an
   insight-carrier post (the article's best concrete number + link) — both
   derived only from what the article says.

## Output

The post text with metadata (character count vs the 3,000 limit,
hashtags, attribution), adaptation-check results, and a reminder that the
canonical article remains the primary work.
