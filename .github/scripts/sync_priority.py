#!/usr/bin/env python3
"""
Sync GitHub Issue Priority Field and Labels

Bidirectional sync between the "Priority" issue field (GitHub's new issue
fields feature) and priority labels, using the REST API.

Mapping:
  Urgent  -> priority-★★★
  High    -> priority-★★☆
  Medium  -> priority-★☆☆
  Low     -> (no priority label)

API docs: https://docs.github.com/en/rest/issues/issue-field-values
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any

import requests

API_BASE = "https://api.github.com"
PRIORITY_FIELD_NAME = "Priority"

PRIORITY_TO_LABELS: dict[str, list[str]] = {
    "Urgent": ["priority-★★★"],
    "High": ["priority-★★☆"],
    "Medium": ["priority-★☆☆"],
    "Low": [],
}

LABEL_TO_PRIORITY: dict[str, str] = {}
for _pri, _labels in PRIORITY_TO_LABELS.items():
    for _lbl in _labels:
        LABEL_TO_PRIORITY[_lbl] = _pri

ALL_PRIORITY_LABELS: set[str] = {lbl for labels in PRIORITY_TO_LABELS.values() for lbl in labels}

LABEL_COLORS: dict[str, str] = {
    "priority-★★★": "B60205",
    "priority-★★☆": "FBCA04",
    "priority-★☆☆": "0E8A16",
}


# ---------------------------------------------------------------------------
# GitHub REST helpers
# ---------------------------------------------------------------------------

def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _check_rate_limit(response: requests.Response) -> None:
    remaining = response.headers.get("X-RateLimit-Remaining")
    reset_at = response.headers.get("X-RateLimit-Reset")
    if remaining is not None and int(remaining) == 0 and reset_at is not None:
        reset_time = datetime.fromtimestamp(int(reset_at), tz=timezone.utc)
        wait = (reset_time - datetime.now(tz=timezone.utc)).total_seconds() + 1
        if wait > 0:
            print(f"  Rate limit reached. Sleeping {wait:.0f}s...")
            time.sleep(wait)


def _get(token: str, path: str) -> requests.Response:
    resp = requests.get(f"{API_BASE}{path}", headers=_headers(token), timeout=30)
    _check_rate_limit(resp)
    resp.raise_for_status()
    return resp


def _post(token: str, path: str, body: dict | None = None) -> requests.Response:
    resp = requests.post(f"{API_BASE}{path}", headers=_headers(token), json=body, timeout=30)
    _check_rate_limit(resp)
    resp.raise_for_status()
    return resp


def _delete(token: str, path: str) -> requests.Response:
    resp = requests.delete(f"{API_BASE}{path}", headers=_headers(token), timeout=30)
    _check_rate_limit(resp)
    resp.raise_for_status()
    return resp


def _paginate(token: str, path: str, per_page: int = 100) -> list[dict]:
    """Collect all pages from a paginated REST endpoint."""
    items: list[dict] = []
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        resp = _get(token, f"{path}{sep}per_page={per_page}&page={page}")
        data = resp.json()
        if isinstance(data, list):
            items.extend(data)
        else:
            return [data]  # single object
        if len(data) < per_page:
            break
        page += 1
    return items


# ---------------------------------------------------------------------------
# Issue field helpers (REST API, not GraphQL/Projects)
# ---------------------------------------------------------------------------

def _get_issue_field_values(token: str, owner: str, repo: str, issue_number: int) -> list[dict]:
    """Get all issue field values for an issue."""
    path = f"/repos/{owner}/{repo}/issues/{issue_number}/issue-field-values"
    return _paginate(token, path)


def _set_issue_field_value(
    token: str, owner: str, repo: str, issue_number: int,
    field_id: int, value: str, dry_run: bool = False,
) -> None:
    """Set a single issue field value on an issue."""
    if dry_run:
        print(f"    [dry-run] Would set field {field_id} to '{value}'")
        return
    _post(
        token,
        f"/repos/{owner}/{repo}/issues/{issue_number}/issue-field-values",
        {"issue_field_id": field_id, "value": value},
    )


def _discover_priority_field_id(token: str, owner: str, repo: str) -> int | None:
    """Find the issue_field_id for the 'Priority' field by inspecting open issues."""
    issues = _paginate(token, f"/repos/{owner}/{repo}/issues?state=all", per_page=30)
    for issue in issues:
        try:
            fields = _get_issue_field_values(token, owner, repo, issue["number"])
        except Exception:
            continue
        for fv in fields:
            name = fv.get("name") or fv.get("field_name") or ""
            if name.lower() == PRIORITY_FIELD_NAME.lower():
                return fv["issue_field_id"]
    return None


# ---------------------------------------------------------------------------
# Label helpers
# ---------------------------------------------------------------------------

def _get_labels(token: str, owner: str, repo: str, issue_number: int) -> list[str]:
    """Return label names for an issue."""
    labels = _paginate(token, f"/repos/{owner}/{repo}/issues/{issue_number}/labels")
    return [lbl["name"] for lbl in labels]


def _add_label(token: str, owner: str, repo: str, issue_number: int,
               label: str, dry_run: bool = False) -> None:
    """Add a label to an issue."""
    print(f"    Adding label: {label}")
    if not dry_run:
        _post(token, f"/repos/{owner}/{repo}/issues/{issue_number}/labels", {"labels": [label]})


def _remove_label(token: str, owner: str, repo: str, issue_number: int,
                  label: str, dry_run: bool = False) -> None:
    """Remove a label from an issue."""
    print(f"    Removing label: {label}")
    if not dry_run:
        _delete(token, f"/repos/{owner}/{repo}/issues/{issue_number}/labels/{label}")


def _ensure_labels_exist(token: str, owner: str, repo: str, dry_run: bool = False) -> None:
    """Create any missing priority labels."""
    existing = {lbl["name"] for lbl in _paginate(token, f"/repos/{owner}/{repo}/labels")}
    for label_name in ALL_PRIORITY_LABELS:
        if label_name not in existing:
            print(f"  Creating label: {label_name}")
            if not dry_run:
                _post(token, f"/repos/{owner}/{repo}/labels", {
                    "name": label_name,
                    "color": LABEL_COLORS.get(label_name, "D4C5F9"),
                })


# ---------------------------------------------------------------------------
# Sync logic
# ---------------------------------------------------------------------------

def _sync_labels(
    token: str, owner: str, repo: str, issue_number: int,
    current_labels: set[str], desired_labels: set[str], dry_run: bool,
) -> bool:
    """Add/remove labels to match desired set. Returns True if changed."""
    changed = False
    for lbl in sorted(current_labels & ALL_PRIORITY_LABELS - desired_labels):
        _remove_label(token, owner, repo, issue_number, lbl, dry_run)
        changed = True
    for lbl in sorted(desired_labels - current_labels):
        _add_label(token, owner, repo, issue_number, lbl, dry_run)
        changed = True
    return changed


def _sync_field(
    token: str, owner: str, repo: str, issue_number: int,
    field_id: int, current_value: str | None, desired_value: str | None,
    dry_run: bool,
) -> bool:
    """Update the Priority field if it doesn't match. Returns True if changed."""
    if current_value == desired_value:
        return False
    if desired_value is None:
        # Can't "clear" a single-select field via REST — skip
        return False
    direction = f"{current_value or '(none)'} -> {desired_value}"
    print(f"  #{issue_number} field: {direction}")
    _set_issue_field_value(token, owner, repo, issue_number, field_id, desired_value, dry_run)
    return True


# ---------------------------------------------------------------------------
# Main sync functions
# ---------------------------------------------------------------------------

def sync_full(
    token: str, owner: str, repo: str, field_id: int, dry_run: bool = False,
) -> None:
    """Bidirectional sync: field wins on conflict, fill in whichever side is missing."""
    issues = _paginate(token, f"/repos/{owner}/{repo}/issues?state=open")
    print(f"  Scanning {len(issues)} open issues/PRs...")

    for issue in issues:
        issue_number = issue["number"]
        current_labels = set(_get_labels(token, owner, repo, issue_number))

        # What priority do the labels imply?
        label_priority: str | None = None
        for lbl in current_labels:
            if lbl in LABEL_TO_PRIORITY:
                label_priority = LABEL_TO_PRIORITY[lbl]
                break

        # What priority does the field say?
        field_priority: str | None = None
        try:
            field_values = _get_issue_field_values(token, owner, repo, issue_number)
            for fv in field_values:
                if fv.get("issue_field_id") == field_id:
                    field_priority = fv.get("value")
                    break
        except Exception:
            continue

        # Case: both unset -> skip
        if label_priority is None and field_priority is None:
            continue

        # Case: only field set -> add labels
        if label_priority is None and field_priority is not None:
            desired = set(PRIORITY_TO_LABELS.get(field_priority, []))
            print(f"  #{issue_number} (field-only) -> labels: {','.join(sorted(desired)) or '(none)'}")
            _sync_labels(token, owner, repo, issue_number, current_labels, desired, dry_run)
            continue

        # Case: only labels set -> set field
        if label_priority is not None and field_priority is None:
            _sync_field(token, owner, repo, issue_number, field_id, None, label_priority, dry_run)
            continue

        # Case: both set, field wins
        if label_priority != field_priority and field_priority is not None:
            desired = set(PRIORITY_TO_LABELS.get(field_priority, []))
            print(f"  #{issue_number} conflict (field wins): labels {label_priority} -> {','.join(sorted(desired)) or '(none)'}")
            _sync_labels(token, owner, repo, issue_number, current_labels, desired, dry_run)
        elif label_priority == field_priority:
            # Agree — just ensure labels are exact
            desired = set(PRIORITY_TO_LABELS.get(field_priority, []))
            if current_labels & ALL_PRIORITY_LABELS != desired:
                print(f"  #{issue_number} cleanup labels")
                _sync_labels(token, owner, repo, issue_number, current_labels, desired, dry_run)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Sync GitHub issue Priority field and labels")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without making them")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is required", file=sys.stderr)
        sys.exit(1)

    repo_full = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in repo_full:
        print(f"Invalid GITHUB_REPOSITORY: {repo_full}", file=sys.stderr)
        sys.exit(1)
    owner, repo = repo_full.split("/", 1)

    dry_run = args.dry_run or os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")

    event = os.environ.get("GITHUB_EVENT_NAME", "schedule")

    print(f"Repo: {owner}/{repo}")
    print(f"Event: {event}")
    print(f"Dry run: {dry_run}")
    print()

    # Ensure labels exist
    print("Ensuring priority labels exist...")
    _ensure_labels_exist(token, owner, repo, dry_run)
    print()

    # Discover Priority field
    print("Discovering Priority issue field...")
    field_id = _discover_priority_field_id(token, owner, repo)

    if field_id is None:
        print("Could not find a 'Priority' issue field in this repository.")
        print("Label check complete. Nothing else to sync.")
        return

    print(f"  Priority field ID: {field_id}")
    print()

    # Sync
    print("Syncing Priority field <-> labels...")
    sync_full(token, owner, repo, field_id, dry_run)
    print()
    print("Priority sync complete.")


if __name__ == "__main__":
    main()
