# Substack Reference

Rules and guidance for preparing articles for [Substack](https://substack.com),
verified against Substack's official documentation on **2026-09-07**.
Sources and their authority classification live in `sources.yaml`.

Rule classification:

- **POLICY** — an official requirement (Content Guidelines violation can
  remove content or restrict a publication).
- **RECOMMENDATION** — official advice from Substack's help center.
- **HEURISTIC** — Article Craft's own editorial judgment. Not a Substack rule.

## Title = email subject line (OFFICIAL_REQUIREMENT)

Substack sends the post title as the email subject line by default; title
testing ("Run a title test") A/B tests alternate subject lines on a random
recipient subset, available to publishers with **at least 200 subscribers**
(`substack-title-testing`). Consequences the adapter encodes:

- The title serves two audiences at once (web reader + inbox). The adapter
  reviews titles with both in mind (HEURISTIC built on official mechanics).
- A title that misrepresents the article is not just clickbait — it burns
  email trust. Distribution-risk checks weight this higher for Substack.

## Content Guidelines (POLICY)

From `substack-content-guidelines` (Last Updated **July 20, 2026**):

- **Plagiarism**: "Do not publish any material that was written or created
  by someone else and claim it as your own." (POLICY)
- **Spam and phishing**: importing purchased/scraped email lists is banned;
  no spam in comments or replies. (POLICY)
- **Marketing and Promotion**: "Substack is intended for high quality
  editorial content, not conventional email marketing. We don't permit
  publications whose primary purpose is to advertise external products or
  services, drive traffic to third party sites, distribute offers and
  promotions, enhance search engine optimization, or similar activities."
  (POLICY) — This is stricter than Medium's distribution guidance: an
  article that is primarily an ad or SEO vehicle risks the publication
  itself. The adapter flags excessive promotional/external-link density as
  ERROR-grade distribution risk, citing this clause.
- Legal/IP responsibilities sit with the publisher; impersonation is banned.

## AI content (OFFICIAL, 2026)

Substack launched **"Scan for AI text"** (powered by Pangram) — readers can
estimate how much of a post/note is AI-assisted, for posts published on or
after **July 21, 2026** (`substack-ai-detection`). Substack also offers a
"Block AI training" crawler toggle in publication settings.

Adapter implications (OFFICIAL mechanics, HEURISTIC conclusions):

- Readers can run AI-detection on your post. Substack's own framing notes
  the tool "estimates" — it is not proof of anything — but the exposure is
  real. The adapter surfaces this fact verbatim; it never offers evasion.
- Strong generic-AI patterns plus weak author contribution → WARNING
  recommending the author add genuine experience and their own voice.
- Article Craft's philosophy already forbids AI-slop production; this
  feature is why that philosophy matters concretely on Substack.

## Formatting features (RECOMMENDATION)

From the Publishing-a-post help section:

- **Alt text**: images support alt text via the image menu
  ("Edit alt text") — clear, concise descriptions recommended
  (`substack-alt-text`). Adapter: missing alt text → WARNING.
- **Tags**: keyword labels on posts; create per-publication custom tags in
  settings or per draft (`substack-tags`). No documented maximum.
- **Code blocks**: dedicated code-block embed with syntax highlighting and
  automatic language detection; renders in email, web, and the app
  (`substack-code-blocks`). Adapter: untagged fenced code → HEURISTIC
  suggestion to let the editor detect the language.
- Teaser posts, audience-specific sections, and paywalled archives exist;
  paywall choices are the author's (out of adapter scope).

## What the Substack adapter deliberately does NOT check

Email-client rendering, deliverability, and send-time optimization are out
of scope — they require sending infrastructure and would pull Article Craft
toward engagement tooling. Newsletter-specific editorial judgment (subject
line clarity, single-topic focus) is covered as HEURISTIC review items.
