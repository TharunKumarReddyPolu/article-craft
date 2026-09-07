# Architecture

## The core principle

**One idea → one canonical article model → platform-specific adaptation.**

The editorial core knows about articles, authors, audiences, sections,
sources, claims, reviews, and voice. It knows nothing about Medium. Platform
adapters know nothing about each other. This is what makes DEV.to/LinkedIn/
Substack adapters straightforward later: they transform the same canonical
model and add their own policy references.

```
                Article Craft
                     |
         +-----------+-----------+
         |                       |
   Editorial Core          Platform Adapters
         |                       |
   +-----+-----+          +------+------+
   |     |     |          |      |      |
Research Voice Review   Medium  DEV*  LinkedIn*
   |     |     |                   (* stubs in V1)
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

## The engines

- **`editorial/`** — article-type registry (10 types with structures and
  failure modes), outline builder, review engine, title system (analysis +
  candidate generation), AI-pattern detection, manipulation-pattern
  detection, human-contribution detection.
- **`research/`** — claim extraction (deterministic candidates + hints),
  fact-check scaffolding, `research.md` artifact rendering.
- **`originality/`** — similarity-risk heuristics vs. a supplied source:
  sentence overlap (shingle Jaccard), structural mirroring (LCS on section
  titles), distinctive-example reuse, unattributed quotes.
- **`voice/`** — writing-profile extraction → `voice.md`.
- **`scoring/`** — the rubric: deductions are impossible without reasons
  (`deduct()` raises on an empty reason).

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

`MediumAdapter` implements it fully. Every check is tagged `POLICY`
(official platform policy), `RECOMMENDATION` (official-sourced advice), or
`HEURISTIC` (Article Craft's editorial judgment), and policy checks cite
their `source_id` from the Medium `sources.yaml` — the adapter raises if a
check cites a source id that doesn't exist there. That's the honesty guard:
code can't drift from documented sources silently.

Future adapters (`platforms/future.py`) raise `NotImplementedError` with a
roadmap pointer. They are registered nowhere; `check --platform devto`
fails with an honest usage error.

## Policy as versioned data

Medium's rules live in `skills/article-craft/references/platforms/medium/`
as markdown summaries with per-source metadata (URL, authority, dates
verified) in `sources.yaml`. The adapter encodes *checks against those
summaries*, not folklore. When Medium changes a page, you update the
reference file, bump `last_verified`, and adjust the check — the change is
reviewable in git.

## The skill ↔ CLI relationship

`skills/article-craft/SKILL.md` is the canonical product; the CLI is an
accelerator inside it. The skill works fully without the CLI (the agent
reads references and applies judgment); the CLI works fully without an
agent (deterministic checks for CI). Neither duplicates the other's logic:
the CLI computes evidence, the skill defines judgment.
