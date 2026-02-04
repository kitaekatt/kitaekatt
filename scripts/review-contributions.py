#!/usr/bin/env python3
"""Scan GitHub for contributions by kitaekatt and flag those needing review.

For each repository YAML in data/contributions/:
1. Query GitHub (via gh CLI) for all issues/PRs authored by kitaekatt
2. Compare against existing entries in the YAML file
3. Add new entries with review_status: not-reviewed
4. Flag changed entries (updated_at differs from last seen)
5. Print a summary of all items needing review

Usage:
    python3 scripts/review-contributions.py [--dry-run]
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" / "contributions"
USERNAME = "kitaekatt"


def gh_query(repo: str, kind: str) -> list[dict[str, Any]]:
    """Query GitHub for issues or PRs authored by USERNAME in repo."""
    if kind == "pr":
        fields = "number,title,state,updatedAt,isDraft,mergedAt"
    else:
        fields = "number,title,state,updatedAt"

    cmd = [
        "gh", kind, "list",
        "--repo", repo,
        "--author", USERNAME,
        "--state", "all",
        "--limit", "200",
        "--json", fields,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"  Warning: gh {kind} list failed for {repo}: {result.stderr.strip()}",
            file=sys.stderr,
        )
        return []
    return json.loads(result.stdout) if result.stdout.strip() else []


def gh_issue_state_reasons(repo: str) -> dict[int, str]:
    """Query stateReason for closed issues via GraphQL (not available in REST API)."""
    owner, name = repo.split("/")
    query = """
    {
      repository(owner: "%s", name: "%s") {
        issues(first: 100, filterBy: {createdBy: "%s", states: [CLOSED]}) {
          nodes { number stateReason }
        }
      }
    }
    """ % (owner, name, USERNAME)
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  Warning: GraphQL query failed for {repo}: {result.stderr.strip()}", file=sys.stderr)
        return {}
    data = json.loads(result.stdout)
    nodes = data.get("data", {}).get("repository", {}).get("issues", {}).get("nodes", [])
    return {n["number"]: n.get("stateReason", "") for n in nodes}


def normalize_state(item: dict[str, Any], kind: str) -> str:
    """Return a normalized status: open, draft, merged, closed."""
    if kind == "pr" and item.get("mergedAt"):
        return "merged"
    if item.get("isDraft"):
        return "draft"
    state = item.get("state", "").upper()
    if state == "OPEN":
        return "open"
    if state in ("CLOSED", "MERGED"):
        return state.lower()
    return state.lower()


def process_repo(yaml_path: Path, dry_run: bool) -> list[dict[str, Any]]:
    """Process one repository YAML. Returns list of items needing review."""
    data: dict[str, Any] = yaml.safe_load(yaml_path.read_text())

    repo: str = data["repository"]
    contributions: list[dict[str, Any]] = data.get("contributions") or []
    existing: dict[int, dict[str, Any]] = {c["number"]: c for c in contributions}
    needs_review: list[dict[str, Any]] = []

    print(f"\n== {repo} ==")

    # Query both issues and PRs, deduplicate by number
    seen: set[int] = set()
    unique_items: list[tuple[str, dict[str, Any]]] = []
    for kind in ("issue", "pr"):
        for item in gh_query(repo, kind):
            if item["number"] not in seen:
                seen.add(item["number"])
                unique_items.append((kind, item))

    # Fetch stateReason for closed issues via GraphQL
    state_reasons: dict[int, str] = gh_issue_state_reasons(repo)

    if not unique_items:
        print("  No contributions found.")
        return needs_review

    for kind, item in sorted(unique_items, key=lambda x: x[1]["number"]):
        num: int = item["number"]
        title: str = item["title"]
        status: str = normalize_state(item, kind)
        updated_at: str = item.get("updatedAt", "")

        # Attach state_reason for issues (COMPLETED, DUPLICATE, NOT_PLANNED, etc.)
        state_reason: str = state_reasons.get(num, "")

        if num in existing:
            entry = existing[num]
            entry["status"] = status
            entry["title"] = title
            if state_reason:
                entry["state_reason"] = state_reason
            if entry.get("review_status") == "not-reviewed":
                needs_review.append(entry)
            elif entry.get("last_seen_updated") != updated_at:
                entry["review_status"] = "not-reviewed"
                entry["last_seen_updated"] = updated_at
                needs_review.append(entry)
        else:
            entry: dict[str, Any] = {
                "number": num,
                "type": kind,
                "title": title,
                "status": status,
                "review_status": "not-reviewed",
                "last_seen_updated": updated_at,
                "summary": "",
            }
            if state_reason:
                entry["state_reason"] = state_reason
            contributions.append(entry)
            needs_review.append(entry)

    data["contributions"] = sorted(contributions, key=lambda c: c["number"])

    if not dry_run:
        yaml_path.write_text(
            yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        )

    return [{"repo": repo, **item} for item in needs_review]


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("DRY RUN — no files will be modified\n")

    all_review: list[dict[str, Any]] = []

    for yaml_path in sorted(DATA_DIR.glob("*.yaml")):
        all_review.extend(process_repo(yaml_path, dry_run))

    print(f"\n{'=' * 60}")
    print(f"Items needing review: {len(all_review)}")
    print(f"{'=' * 60}")

    for item in all_review:
        status = item["status"]
        reason = item.get("state_reason", "")
        if reason:
            flag = f"[{status}/{reason}]"
        else:
            flag = f"[{status}]"
        print(f"  #{item['number']:>6}  {flag:<28}  {item.get('repo', '')}: {item['title']}")


if __name__ == "__main__":
    main()
