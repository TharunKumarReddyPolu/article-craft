# Reach: Substack's Official Discoverability Mechanics

What Substack officially documents about how posts get found — summarized
from Substack's own support documentation so the adapter checks alignment
with documented mechanics, not folklore.

Sources: `substack-title-testing`, `substack-tags`, `substack-alt-text`,
`substack-content-guidelines` (verified 2026-09-07). Substack's primary
distribution channel is the writer's own email list; on-platform discovery
(recommendations, notes, search) compounds on top of it.

## Official mechanics

- **Email is the channel** — the post title doubles as the email subject
  line by default; that one string decides whether subscribers open.
  Substack documents title/subject-line duality and an official A/B
  "title test" (50% of recipients for one hour, publishers with 200+
  subscribers) — substack-title-testing.
- **Tags** — keyword tags organize posts on-platform (substack-tags);
  no official maximum is documented, and the adapter does not invent one.
- **Alt text** — Substack officially supports image alt text and recommends
  "clear, concise description" (substack-alt-text); email clients and
  screen readers both depend on it.
- **Content guidelines** — substack-content-guidelines is the baseline;
  spam reports are the fastest documented way to lose email deliverability,
  which is Substack reach.

## What the reach engine checks (and why)

Advisory signals only: subject-line strength of the title (the email
preview is the reach surface), presence of a subtitle/preheader content,
tag presence, and image alt text. None of it predicts opens, ranking, or
recommendations.
