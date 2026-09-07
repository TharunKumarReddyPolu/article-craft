# Test Fixtures

Articles used by the test suite. Each exercises specific detection paths.

| File | Purpose |
|---|---|
| `excellent_technical.md` | Strong case study: real experience, measured numbers, honest lessons. Should score high and READY. |
| `generic_ai.md` | Generic AI-cadence prose, undisclosed AI assistance. Should trigger AI-pattern and AI-policy findings. |
| `poor_structure.md` | Repetitive, sectionless filler. Should score low on Structure/Clarity. |
| `factual_errors.md` | Conspiracy-style misinformation + undisclosed AI. Should trigger critical evidence/accuracy findings. |
| `unsupported_claims.md` | Fabricated statistics and "studies show" claims. Should trigger Evidence + Technical Accuracy deductions. |
| `clickbait.md` | Tabloid title/subtitle. Should fail the Medium title check (ERROR). |
| `seo_spam.md` | Keyword stuffing + undisclosed affiliate links + undisclosed AI. Should fail affiliate + AI checks. |
| `strong_personal.md` | Genuine personal experience with specificity. Should score high on Voice. |
| `strong_system_design.md` | Full system-design treatment with labeled assumptions and trade-offs. |
| `originality_risk.md` | Derivative, structurally mirroring text (compare against its "source" in tests). |

Fixtures are deliberately stereotyped so assertions stay stable as the
heuristics evolve. They are test data, not writing advice.
