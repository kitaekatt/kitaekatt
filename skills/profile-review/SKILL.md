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

### Phase 1: Section-by-Section Review

For each section in order:

1. **Present** — Show the section content as quoted text
2. **Ask** — "Any changes for this section?"
3. **Collect** — Record requested changes. User may request multiple changes per section.
4. **Advance** — User says "next" to move to the next section. User may also say "skip" to accept a section as-is.

Accumulate all requested changes across sections. Do NOT make any edits during this phase.

### Phase 2: Change Proposal

After all sections have been reviewed:

1. Summarize the full list of collected changes
2. Enter plan mode with the proposed edits
3. Wait for user approval before making any changes

### Decision Gates

| Gate | Trigger | Action |
|------|---------|--------|
| Section gate | Each section | Present content, wait for "next" or "skip" |
| Final gate | All sections reviewed | Summarize changes, enter plan mode |

## Notes

- If a section has no content changes requested, do not include it in the final plan
- Preserve the existing tone: professional but personal
- Keep PR links accurate — verify URLs if adding or modifying contribution entries
