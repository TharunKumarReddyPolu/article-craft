# Medium Images (reference)

> Sources: [Writing and publishing your first story](https://help.medium.com/hc/en-us/articles/225168768-Writing-and-publishing-your-first-story)
> and [Distribution Guidelines](https://help.medium.com/hc/en-us/articles/360006362473-Medium-s-Distribution-Guidelines-How-curators-review-stories-for-Boost-General-and-Network-Distribution)
> (official; verified 2026-09-06). See `sources.yaml`.

## Official guidance (OFFICIAL_REQUIREMENT / OFFICIAL_RECOMMENDATION)

- Upload your own images or insert them from Unsplash.
- "Images, if any, add value to the story. We like to see ALT text that makes
  images more accessible, along with appropriate credits."
- AI-generated images must include a caption identifying them as such.
- Copyrighted images used without permission or accredited fair use are a
  Rules violation.
- Original cover images help represent the story; stock photos work if chosen
  with care; AI-generated cover art "sometimes works (if properly credited as
  such) but is often a turn-off to readers." A story is **not required** to
  use a cover image — a poorly chosen one is worse than none.
- NSFW images are not eligible for General Distribution or Boost.

## What Article Craft does with this (HEURISTIC)

- Flags Markdown images without alt text: `![alt text](url)`.
- Flags images that appear decorative-only (same generic URL patterns
  repeated, no caption, unrelated naming) as "check relevance."
- Reminds about captioning AI-generated images and crediting sources.
- V1 checks Markdown only; it does not fetch or analyze image content.
