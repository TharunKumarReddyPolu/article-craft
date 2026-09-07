# Architecture

## The core principle

**One idea → one canonical article model → platform-specific adaptation.**

The editorial core knows about articles, authors, audiences, sections,
sources, claims, reviews, and voice. It knows nothing about any platform.
Platform adapters know nothing about each other. This is what made the
DEV.to/Hashnode/Substack/LinkedIn adapters (V2) straightforward: each
transforms the same canonical model and adds its own policy references.

```
                Article Craft
                     |
         +-----------+-----------+
         |                       |
   Editorial Core          Platform Adapters
         |                       |
   +-----+-----+          +------+------+------+------+
   |     |     |          |      |         |         |  |
Research Voice Review   Medium  DEV.to  Hashnode Substack LinkedIn
   |     |     |
   +-----+-----+
         |
    Article Model
```

## The canonical model

`src/article_craft/models/` — Pydantic models, deliberately small:

- **`Article`** — the canonical article: frontmatter metadata (title,
  subtitle, audience, type, platform, topics, `ai_assistance`,
  `canonical_url`), sections, prose statistics, links, images, code blocks,
  mentions. Built by `parsing.py` from Markdown + YAML frontmatter.
- **`Section`** — an H2-level chunk with word count, line range, code/image
  presence, and subheading count.
- **`Source` / `Claim`** — research layer: sources with authority tiers
  (1 official → 5 avoid), claims with status
  (VERIFIED/LIKELY/UNVERIFIED/CONTRADICTED/OPINION/ASSUMPTION).
- **`ReviewIssue` / `ReviewResult` / `EditorialScore`** — review layer:
  issues with severity and rule class, the 8-dimension reasoned score,
  verdicts.
- **`PlatformCheck` / `PlatformCheckReport`** — adapter output: category,
  PASS/WARNING/ERROR/NOT CHECKED/NOT APPLICABLE, rule class, source id.
- **`WritingProfile`** — voice layer: statistical signals from the author's
  own corpus.
- **`SocialPost`** (V2) — an attributed social adaptation derived *from* an
  Article; carries `source_article_id` and a claim-traceability invariant.
- **`PlatformExport`** (V2) — a locally-written platform-ready artifact:
  file path, platform id, warnings. Never a publish action.

## The engines

- **`editorial/`** — article-type registry (10 types with structures and
  failure modes), outline builder, review engine, title system (analysis +
  candidate generation), AI-pattern detection, manipulation-pattern
  detection, human-contribution detection, image & alt-text checks (V2),
  social adaptation (V2).
- **`research/`** — claim extraction (deterministic candidates + hints),
  fact-check scaffolding, `research.md` artifact rendering, contradiction
  detection with authority-based resolution (V2).
- **`originality/`** — similarity-risk heuristics vs. a supplied source:
  sentence overlap (shingle Jaccard), structural mirroring (LCS on section
  titles), distinctive-example reuse, unattributed quotes.
- **`voice/`** — writing-profile extraction → `voice.md`.
- **`scoring/`** — the rubric: deductions are impossible without reasons
  (`deduct()` raises on an empty reason).
- **`exporter.py`** (V2) — renders platform-ready files to disk for all five
  platforms; zero network calls.
- **`mcp/`** (V2, optional extra) — a FastMCP stdio server exposing the
  deterministic engines as MCP tools. No LLM, no network.

## The deterministic-vs-LLM split

The CLI does only what's deterministic: parsing, statistics, pattern
matching, structural checks, policy-state checks (frontmatter), and report
rendering. Everything requiring judgment — tone critique, technical
correctness, whether a claim is actually true, whether a paraphrase is too
close *in meaning* — belongs to the agent following the skill's workflows.

This split is why the test suite needs no LLM and no network, and why the
tool is honest about what it can verify: the CLI never claims to have
verified anything it hasn't.

## Platform adapters

`platforms/base.py` defines a small `Protocol`:

```python
class PlatformAdapter(Protocol):
    platform_id: str
    def validate_article(self, article) -> list[str]: ...
    def review_title(self, article) -> list[PlatformCheck]: ...
    def review_structure(self, article) -> list[PlatformCheck]: ...
    def review_formatting(self, article) -> list[PlatformCheck]: ...
    def review_policy(self, article) -> list[PlatformCheck]: ...
    def review_distribution(self, article) -> list[PlatformCheck]: ...
    def generate_platform_checklist(self, article) -> list[str]: ...
    def platform_compatibility_score(self, article) -> DimensionScore: ...
```

`MediumAdapter` implements it fully; the V2 adapters (DEV.to, Hashnode,
Substack, LinkedIn) share the same base. Every check is tagged `POLICY`
(official platform policy), `RECOMMENDATION` (official-sourced advice), or
`HEURISTIC` (Article Craft's editorial judgment), and policy checks cite
their `source_id` from the platform's `sources.yaml` — the shared base
raises if a check cites a source id that doesn't exist there. That's the
honesty guard: code can't drift from documented sources silently.

Two adapters have documented scope limits that are stated in output rather
than papered over: the LinkedIn adapter reviews *adaptations* (posts), not
raw markdown articles; and Substack's adapter cannot verify email rendering.

## Adaptation and export (V2)

Two derived artifacts keep the canonical article primary:

- **`article-craft adapt`** (`editorial/adaptation.py`) builds a
  `SocialPost` from the article: an attributed hook, the article's key
  points, and the link. Post text respects LinkedIn's documented 3,000-
  character limit; every factual statement must trace to the article —
  the engine refuses to add claims. Nothing is published.
- **`article-craft export`** (`exporter.py`) writes platform-ready files:
  frontmatter-composed markdown for DEV.to/Hashnode/Medium, and post text
  for LinkedIn/Substack. Files land locally; publishing remains manual.

## Policy as versioned data

Each platform's rules live in
`skills/article-craft/references/platforms/<platform>/` as markdown
summaries with per-source metadata (URL, authority, dates verified) in
`sources.yaml`. The adapters encode *checks against those summaries*, not
folklore. When a platform changes a page, you update the reference file,
bump `last_verified`, and adjust the check — the change is reviewable in
git. Where a platform publishes no relevant policy, its adapter emits
`NOT CHECKED` with that explanation rather than guessing.

## The skill ↔ CLI relationship

`skills/article-craft/SKILL.md` is the canonical product; the CLI is an
accelerator inside it. The skill works fully without the CLI (the agent
reads references and applies judgment); the CLI works fully without an
agent (deterministic checks for CI). Neither duplicates the other's logic:
the CLI computes evidence, the skill defines judgment.
