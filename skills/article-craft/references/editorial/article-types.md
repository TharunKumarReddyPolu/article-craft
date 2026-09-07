# Article Types (reference)

Ten article types Article Craft supports. Each has a purpose, a recommended
structure, and common failure modes. The full registry lives in
`src/article_craft/editorial/types.py` (authoritative for tooling); this file
is the writer-facing summary.

| Type | Purpose | Core structure | Common failure modes |
|---|---|---|---|
| Technical tutorial | Reader completes a task by the end | What you'll build → prerequisites → steps with verification → troubleshooting → next steps | Skipping failure cases; untested code; steps that only work on the author's machine |
| Technical explainer | Reader understands a concept | Hook (why care) → mental model → build-up from simple → worked example → limits/edge cases | Explaining the spec instead of the understanding; no mental model; jargon without definition |
| System design | Reader can reason about the architecture | Requirements (functional + non-functional) → constraints → high-level design → deep dives → trade-offs → failure modes | Capacity numbers with no basis; ignoring failure; missing trade-offs; buzzword architecture |
| Architecture deep dive | Reader understands why a system is built this way | Context → forces → decisions → rejected alternatives → consequences | No rejected alternatives; hindsight bias; no versioning of the decision |
| Case study | Reader learns from a real project | Situation → task → actions → results → lessons (what you'd do differently) | Cherry-picked results; no failures; lessons nobody can reuse |
| Personal experience | Reader gains insight from your story | Scene-setting → what happened → what it meant → what it changed for you | Diary without takeaway; manufactured drama; no relevance to reader |
| Opinion | Reader gains a defensible position worth debating | Position up front → strongest evidence → strongest counterargument → response → qualification | Strawmanning; evidence-free assertion; no counterargument; rage-bait framing |
| Beginner guide | Beginner reaches first competence | Who this is for → what you'll have at the end → concepts → first success fast → progressive depth → where to go next | Assuming prerequisite knowledge; wall-of-text; covering everything; no early win |
| Advanced guide | Practitioner levels up | Assumed knowledge stated → the gap most practitioners have → the technique → why it works → when NOT to use it | No assumed-knowledge baseline; rehashing basics; no failure modes |
| Listicle | Reader gets scannable, genuinely distinct items | Framing (what qualifies an item for the list) → items with substance → honest closer | Padding to hit a number; items that are ads; no selection criteria |

## Choosing a type

- If the reader must **do** something after reading → tutorial.
- If the reader must **understand** something → explainer or deep dive.
- If the reader must **decide** something → opinion or case study.
- If the reader must **feel less alone / learn from your scar** → personal
  experience.
- If the reader is **starting from zero** → beginner guide.

Article Craft will not let a "listicle" with one real item and nine ads score
well on Reader Value — the type itself carries quality expectations.
