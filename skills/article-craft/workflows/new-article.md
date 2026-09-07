# Workflow: New article

Use when the user wants to start an article from an idea.

## Method

1. **Ask the ten questions** (skip any the user already answered). If the
   user's idea is thin, ask before outlining:

   1. What do you want to write about?
   2. Who is the audience? (beginners / practitioners / your team / general)
   3. What problem does the article solve for that reader?
   4. What should readers learn or be able to do afterwards?
   5. What is your unique perspective or angle?
   6. What experience do you have with the topic? (Be concrete — this becomes
      the article's credibility backbone.)
   7. What article type is this? (see
      [../references/editorial/article-types.md](../references/editorial/article-types.md)
      for the ten types)
   8. Desired length?
   9. Desired tone?
   10. Target platform? **V1 options: Medium or generic.** (DEV.to, LinkedIn,
       Substack etc. are roadmap items — say so honestly.)

2. **Generate the editorial brief** (use the CLI `article-craft new` if
   installed, otherwise produce it yourself):
   - Reader promise ("After reading, you will...")
   - Thesis (one sentence, falsifiable if opinion)
   - Angle (what makes this different from the top search results)
   - Research questions (3-5, from [../references/research/source-hierarchy.md](../references/research/source-hierarchy.md))
   - Title candidates across approaches (descriptive, problem-oriented,
     outcome-oriented, curiosity-driven, technical, beginner-friendly,
     experience-based) — each with clarity/specificity/promise/accuracy notes.
     Never recommend a title that misrepresents the planned article.
   - Recommended structure from the article type
   - **Author contribution prompts**: what the user personally brings
     (experience, experiment, benchmark, decision, lesson).

3. **Present the brief and wait.** Do NOT write the article. The next step is
   the user's decision (research first, outline first, or draft sections
   themselves).

## Output template

Use [../templates/](../templates/) matching the chosen type as the skeleton
for the eventual draft — the template is structure, not prose.

## Guardrails

- If the user has no personal connection to the topic, say so plainly and
  offer the explainer/guide path where research depth can substitute for
  experience — while warning that Medium's distribution guidelines favor
  first-hand experience.
- If the idea is a rewrite of an existing article ("like this one but
  different words"), route to [originality.md](originality.md) first.
