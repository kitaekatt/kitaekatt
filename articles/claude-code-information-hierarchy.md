---
title: The Claude Code Information Hierarchy
description: Where you put guidance in Claude Code determines whether it's recalled, whether it's followed, and how much it costs. Here's the framework.
tags: [claudecode, ai, llm, productivity]
published: false
---

Every piece of information you give Claude Code can be evaluated on three axes:

1. **Recall** — Likelihood Claude will load this information into context at all. *Claude can't apply information it doesn't recall.*
2. **Attention** — Likelihood Claude will skillfully apply the information once it's loaded. *If Claude ignores information, it might as well not recall it.*
3. **Context Load** — How much token budget this information consumes. *Higher context load means higher cost, worse attention, slower speed.*

No single tier of the hierarchy wins on all three dimensions. That's why you need the hierarchy rather than putting everything in one place.

---

## The Hierarchy

| Tier | Recall | Attention | Context Load |
|------|--------|-----------|--------------|
| **Root CLAUDE.md** | Highest — always loaded | Degrades with context size | High — always consuming tokens |
| **Sub-dir CLAUDE.md** | High — loaded on file access | Higher — less noise than root | Medium — only when relevant |
| **Skills** | Lower — but user can manually invoke | Highest — fresh, focused context | Lowest — on-demand only |

---

## Loading Triggers

| Mechanism | When It's Loaded | Who Triggers It |
|-----------|-----------------|-----------------|
| Root CLAUDE.md | Always | Automatic |
| Sub-dir CLAUDE.md | Claude reads a file in that directory or below | Claude's file access |
| Skill (claude-invoked) | Claude decides the skill is valuable based on its description | Claude's judgment |
| Skill (user-invoked) | User runs a command (e.g., `/review-work-before-submit`) | User |

---

## Progressive Disclosure (Skills)

Skills can contain reference documents that are conditionally loaded into context, adding further efficiency within the most efficient tier:

![Progressive disclosure layers — Layer 1: Skill Description (cheap, always visible for routing), Layer 2: Skill Content (moderate, loaded on invocation), Layer 3: Referenced Documents (expensive, loaded on-demand)](https://kitaekatt.github.io/claude-code-information-hierarchy/images/progressive-disclosure.png)

---

## Practical Decision Flow

When adding new information, ask:

![Decision flow: Does Claude need this on most interactions? YES → Root CLAUDE.md. NO → Does Claude need this to work with most files in this directory? YES → Sub-dir CLAUDE.md. NO → Skill](https://kitaekatt.github.io/claude-code-information-hierarchy/images/decision-flow.png)

---

## CLAUDE.md Maintenance

When CLAUDE.md grows too large, audit each item: "Is this always needed?"

![CLAUDE.md maintenance flow: CLAUDE.md grows too large → audit each item → NO directory → Sub-dir CLAUDE.md, NO workflow → Skill, YES → Keep in root](https://kitaekatt.github.io/claude-code-information-hierarchy/images/claudemd-maintenance.png)

> Sub-dir CLAUDE.md files are loaded less often, so are lower priority to optimize.

---

## Skill Maintenance

When a skill grows too large, audit each item: "Always needed when this skill is invoked?"

![Skill maintenance flow: Skill grows too large → audit each item → NO → Referenced document, YES → Keep in skill](https://kitaekatt.github.io/claude-code-information-hierarchy/images/skill-maintenance.png)

---

## Key Tradeoff Summary

| | Recall | Attention | Context Load | Design Effort |
|--|--------|-----------|--------------|---------------|
| **Root CLAUDE.md** | Highest — always in context | Degrades with context size | High — always loaded | Low |
| **Sub-dir CLAUDE.md** | High — loaded on file access | Higher — less noise | Medium | Low |
| **Skills** | Lower — but user can manually invoke | Highest — fresh, focused | Lowest — on-demand | Highest |
