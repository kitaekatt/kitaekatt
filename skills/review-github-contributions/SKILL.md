_schema_version: 1
required_skills: []
name: review-github-contributions
description: Review GitHub contributions across tracked repositories and maintain a structured database of contribution context

## Purpose

Scan GitHub for all issues/PRs by kitaekatt across tracked repositories, then review each contribution to build an AI-facing database of contribution context. This data informs README.md updates during profile-review.

**Behavioral mode**: Conversational — presents items for review one at a time.

## Tracked Repositories

- [anthropics/claude-code](https://github.com/anthropics/claude-code)
- [vllm-project/vllm](https://github.com/vllm-project/vllm)
- [huggingface/transformers](https://github.com/huggingface/transformers)

## Data Location

- YAML files: `data/contributions/<repo-name>.yaml`
- Scan script: `scripts/review-contributions.py`

## When to Use

- Before a profile-review, to ensure contribution data is current
- When new PRs/issues have been filed and need cataloguing
- Periodic refresh of contribution database

## When NOT to Use

- User wants to edit README directly without reviewing contributions
- Adding a new repository to track (update the script and add a new YAML file first)

## Activation Contexts

```yaml
activation_contexts:
  - "review contributions"
  - "scan contributions"
  - "update contribution data"
```

## Review Protocol

### Step 1: Scan

Run the scan script to discover new and changed items:

```
python3 scripts/review-contributions.py
```

This prints all items needing review and updates the YAML files with `review_status: not-reviewed` entries.

### Step 2: Review Each Item

For each item with `review_status: not-reviewed`, apply the following rules:

| Condition | Action | Set review_status to |
|-----------|--------|---------------------|
| Closed without changes (no merge, no fix) | Skip | `skipped` |
| Draft PR | Skip | `skipped` |
| Open issue/PR | Read the issue, write a contextual status summary | `reviewed` |
| Merged PR or closed-with-fix | Summarize the positive contribution | `reviewed` |

**For open items**: Read the issue/PR via `gh`, write a summary describing what the issue is about, current status, and any blockers.

**For merged/closed-with-fix items**: Summarize what value this contributed to the project. This is a database entry, not prose — write in an AI-facing manner that captures the technical contribution for later mining into README.md content.

Present each item to the user:
1. Show the item number, title, status, and repo
2. Show the proposed summary
3. Wait for user approval or edits
4. User says "next" to advance

### Step 3: Update YAML

After reviewing each item, update the corresponding YAML file with the summary and new review_status.

## Integration with profile-review

The contribution YAML files serve as a structured database that the profile-review skill can reference when reviewing the Open Source Contributions sections of README.md. Reviewed contributions with positive summaries are candidates for inclusion in the profile.
