# DEV.to Checklist

Policy references: [../references/platforms/devto/](../references/platforms/devto/).
Reminders where each rule comes from are inline; when in doubt, re-read the
reference before claiming a rule.

## Front matter
- [ ] `title:` present (required) and matches the article
- [ ] `published: true` only when intentionally live (draft default: false)
- [ ] `tags:` at most 4 tags, all actually matching the content
- [ ] `cover_image:` points at a suitable, rights-cleared image (or omitted)
- [ ] `canonical_url:` set if this is a cross-post from another platform

## Formatting
- [ ] Markdown is valid; code blocks have language hints
- [ ] Liquid tags used deliberately: `{% embed ... %}`, `{% github ... %}`,
      `{% link ... %}` for embeds — no raw embed code
- [ ] No HTML that DEV's front matter/parser would reject

## Content quality
- [ ] Reader gets real value, not a thin rehash or sales pitch
- [ ] Author contribution present (experience, benchmarks you ran, opinion)
- [ ] Title is honest — no clickbait, matches the content

## Policy
- [ ] AI-assisted? Article labeled per DEV's AI-assisted content guidelines
- [ ] No plagiarism: copied text/attribution issues resolved before publishing
- [ ] Images and code rights cleared
- [ ] External links are descriptive (no "click here")

## Final
- [ ] All claims either verified or honestly hedged
- [ ] Run `article-craft check article.md --platform devto` (CLI) — fixes or
      acknowledges every reported issue
