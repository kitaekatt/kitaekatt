_schema_version: 1
required_skills: []
name: profile-review
description: Section-by-section guided review of the GitHub profile README

## Purpose

Walk through the profile README one section at a time, presenting each section's content and collecting requested changes. After all sections are reviewed, enter plan mode to propose the full set of changes.

**Behavioral mode**: Conversational — pauses at every section for user feedback.

## When to Use

- User wants to review or revise their profile
- User wants to audit what the profile says
- User wants to make targeted edits across multiple sections

## When NOT to Use

- User knows exactly what to change and states it directly — just make the edit
- Structural/architectural changes to the repo itself (not README content)

## Activation Contexts

```yaml
activation_contexts:
  - "review my profile"
  - "let's go through my profile"
  - "profile review"
```

## Structural Diagram

The README follows a top-to-bottom narrative arc. Within each level, items read left-to-right in priority order. Each box is a review step.

```
                    ┌───────────────┐
                    │   Who I Am    │
                    │  name + role  │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              ▼                           ▼
      ┌──────────────┐           ┌──────────────┐
      │  Past        │           │  Present     │
      │  game design │           │  AI/ML infra │
      │  career      │           │  focus       │
      └──────────────┘           └──────┬───────┘
                                        │
                                        ▼
                               ┌────────────────┐
                               │  Proof of Work │
                               │  PRs, repos,   │
                               │  contributions │
                               └────────┬───────┘
                                        │
                        ┌───────────────┼───────────────┐
                        ▼               ▼               ▼
                  ┌─────────┐     ┌─────────┐     ┌─────────┐
                  │ Claude  │     │  vLLM   │     │ HF      │
                  │ Code    │     │         │     │ Transf. │
                  └─────────┘     └─────────┘     └─────────┘
                                        │
                                        ▼
                               ┌────────────────┐
                               │  Credibility   │
                               │  signals       │
                               ├────────────────┤
                               │  tools I use   │
                               │  activity stats│
                               └────────┬───────┘
                                        │
                                        ▼
                               ┌────────────────┐
                               │  How to reach  │
                               │  me            │
                               └────────────────┘
```

## Section Map

Each box in the diagram maps to a review step. Review proceeds top-to-bottom, left-to-right:

1. **Who I Am** — Name, role, one-liner (first line of README)
2. **Past** — Game design career background (within the intro paragraph)
3. **Present** — `## Current Focus`
4. **Proof of Work** — `## Open Source Contributions` header/intro
5. **Claude Code** — `### Claude Code` subsection
6. **vLLM** — `### vLLM` subsection (merged + in progress)
7. **HF Transformers** — `### Hugging Face Transformers` subsection
8. **Tech Stack** — `## Tech Stack`
9. **GitHub Stats** — `## GitHub Stats`
10. **Connect** — `## Connect`
11. **Keywords** — Footer `<sub>` tag

## Review Protocol

### Section-by-Section Review

For each section in order:

1. **Present** — Show the section content as quoted text
2. **Ask** — "Any changes for this section?"
3. **Iterate** — User requests changes until satisfied
4. **Advance** — User says "next" or "skip"

### Applying Edits

When the user says "next" and there are approved changes for the current section:

1. **Delegate** — Launch a background Haiku agent via the Task tool with:
   - The exact `old_string` to replace (copied from the current README)
   - The exact `new_string` to use (the approved revision)
   - The file path (`README.md`)
2. **Continue** — Immediately present the next section without waiting

This keeps the review moving while edits happen in parallel. If "skip" or no changes, just advance.

### After All Sections

Verify all background edits completed successfully. Report any failures for manual resolution.

## Contribution Description Protocol

When writing or revising descriptions for open source contributions (issues and PRs):

1. **Lead with the concrete user symptom**, not the technical root cause — what broke or was missing from the user's perspective
2. **State impact** — who was affected and how their workflow broke
3. **Describe what the filing contributed** — testing matrices, design proposals, frameworks, reproduction steps
4. **Show how the fix manifests for users** — what changed in their experience
5. **Avoid internal process details** — don't mention auto-close bots, resubmissions, or "Closed as completed"

### Attribution ordering

When attribution is known, order contributions by specificity:

1. **Known fixer** first — include `@username` (e.g., "Fixed by @ltawfik")
2. **Known version** second — include version number (e.g., "Fixed in v2.0.76")
3. **Everything else** third — behavioral description of the resolution

### Tone

- Professional and factual — no superlatives or self-promotion
- Describe what happened, not how impressive it was
- Use the contribution's actual scope — don't inflate a bug report into "engineering a solution"

## Notes

- If a section has no content changes requested, do not include it in the final plan
- Preserve the existing tone: professional but personal
- Keep PR links accurate — verify URLs if adding or modifying contribution entries
