# Workflow: Platform Check

Use when the author asks "is this ready for [platform]?" — for **Medium,
DEV.to, Hashnode, Substack, or LinkedIn**.

## Method

1. **Read the platform's reference overview** first
   (`references/platforms/<platform>/overview.md`) so every judgment cites
   current, verified policy rather than memory.
2. **Run the deterministic check** if the CLI is available:
   `article-craft check article.md --platform <platform>`. If not, do the
   equivalent analysis by hand from the reference files.
3. **Layer editorial judgment** on top: the deterministic layer catches
   mechanical violations; you assess reader value, technical accuracy, and
   the author's contribution.
4. **Report in categories** (Title, Structure, Formatting, AI Policy,
   Canonical, Distribution Risks, Images) with PASS / WARNING / ERROR /
   NOT CHECKED per category. For every policy finding, name the source
   (its `source_id` in the platform's `sources.yaml`).
5. **Never mark a category NOT CHECKED silently** — say why (e.g.
   "Hashnode publishes no AI policy; verified 2026-09-07").

## Platform notes

- **Medium**: distribution-guideline risk checks; canonical link set in
  story settings by the author.
- **DEV.to**: front matter contract (max 4 tags), `canonical_url` mandatory
  for cross-posts, H2-first sections, liquid-tag spelling.
- **Hashnode**: `%[URL]` embeds, "Add Original Article" canonical setting;
  no official AI policy — say so.
- **Substack**: title doubles as the email subject line; Content
  Guidelines ban publications whose primary purpose is marketing/SEO;
  readers can run "Scan for AI text" (Pangram) on posts since 2026-07-21.
- **LinkedIn**: reviews a **LinkedIn adaptation** (plain-text post ≤3,000
  chars or an article draft), never raw markdown — label every finding as
  an adaptation review.

## Output

Pre-publish check in the §format of the CLI: category statuses, findings,
"Fix Before Publishing" list, and the disclaimer that checks are based on
published guidance and heuristics and do not guarantee distribution.
