# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **kitaekatt** — Christina Norman's GitHub profile repository. It contains a single `README.md` that serves as the public-facing profile on github.com/kitaekatt.

## Repository Structure

This is a documentation-only repository with no build system, dependencies, or tests. The entire content is `README.md`.

## Page Structure

The README follows a narrative arc: **identity** → **credibility** (past + present) → **evidence** (contributions) → **reinforcement** (tools, stats) → **call to action** (contact). Top-to-bottom is scroll order and importance; left-to-right is priority within a level.

See `.claude/skills/profile-review/SKILL.md` for the full structural diagram and section map.

## Related Projects

**`kitaekatt.github.io`** (`~/Dev/kitaekatt.github.io`) — The GitHub Pages site that renders at `https://kitaekatt.github.io`. It owns the front page presentation and all published articles. That project is responsible for staying in sync with `README.md` in this repo — how it achieves that is up to its own architecture (GitHub Action, manual sync, etc.).

When `README.md` changes here, note that `kitaekatt.github.io` may need updating.

## Update Process

Before editing the contributions section of README.md, run the contribution review skill to catch new and changed items:

```
Skill: review-github-contributions
```

This scans GitHub for new PRs and issues across tracked repos (claude-code, vllm, transformers), presents unreviewed items one at a time for approval, and maintains a structured YAML database in `data/contributions/`. Reviewed entries are the source of truth for what belongs in the README.

## Editing Guidelines

- The README uses GitHub-flavored markdown and renders as a GitHub profile page
- External images are loaded from `skillicons.dev` (tech stack icons) and `github-readme-stats.vercel.app` (stats card)
- The "Open Source Contributions" section lists PRs with direct GitHub links — keep links accurate and up to date
- The footer `<sub>` tag contains SEO/discoverability keywords
- Keep the tone professional but personal — this represents Christina's public identity
