#!/usr/bin/env python3
"""
Sync GitHub Issue Priority Field and Labels

Bidirectional synchronization between:
  - GitHub's "Priority" issue field (a project field)
  - Priority labels (priority-★★★, priority-★★☆, priority-★☆☆)

Mapping:
  Urgent  → priority-★★★
  High    → priority-★★☆
  Medium  → priority-★☆☆
  Low     → (no priority label)

Triggers:
  - Label event → update the Priority field to match
  - Scheduled run → update labels to match the Priority field
  - Other events → full bidirectional sync (field wins on conflict)

Requirements:
  - GITHUB_TOKEN with issues:write and pull_requests:write permissions
  - The repository must have a "Priority" field configured on issues
"""

import argparse
import os
import sys
import time
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

import requests
from github import Auth, Github, GithubException


# ---------------------------------------------------------------------------
# Priority mapping
# ---------------------------------------------------------------------------

PRIORITY_FIELD_NAME = "Priority"

# Field value → label(s)
PRIORITY_TO_LABELS: dict[str, list[str]] = {
    "Urgent": ["priority-★★★"],
    "High": ["priority-★★☆"],
    "Medium": ["priority-★☆☆"],
    "Low": [],
}

# Label → field value (reverse mapping)
LABEL_TO_PRIORITY: dict[str, str] = {}
for _priority, _labels in PRIORITY_TO_LABELS.items():
    for _label in _labels:
        LABEL_TO_PRIORITY[_label] = _priority

ALL_PRIORITY_LABELS: set[str] = {
    label for labels in PRIORITY_TO_LABELS.values() for label in labels
}

# GraphQL fragments used for project field operations
GET_PROJECT_FIELDS_QUERY = """
query($owner: String!, $repo: String!, $issueNumber: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $issueNumber) {
      id
      projectItems(first: 20) {
        nodes {
          id
          project {
            id
            title
          }
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                field {
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    options {
                      id
                      name
                    }
                  }
                }
                name
                optionId
              }
            }
          }
        }
      }
    }
  }
}
"""

UPDATE_FIELD_VALUE_MUTATION = """
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $valueId: String!) {
  updateProjectV2ItemFieldValue(
    input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { singleSelectOptionId: $valueId }
    }
  ) {
    clientMutationId
  }
}
"""

CLEAR_FIELD_VALUE_MUTATION = """
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!) {
  clearProjectV2ItemFieldValue(
    input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
    }
  ) {
    clientMutationId
  }
}
"""


# ---------------------------------------------------------------------------
# GraphQL helpers
# ---------------------------------------------------------------------------

def _graphql_request(
    token: str, query: str, variables: dict[str, Any]
) -> dict[str, Any]:
    """Make a GitHub GraphQL API request with rate-limit handling."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=30,
    )
    _check_rate_limit(response)
    response.raise_for_status()
    body = response.json()
    if "errors" in body:
        raise RuntimeError(f"GraphQL errors: {body['errors']}")
    return body["data"]


def _check_rate_limit(response: requests.Response) -> None:
    """Check rate-limit headers and sleep if depleted."""
    remaining = response.headers.get("X-RateLimit-Remaining")
    reset_at = response.headers.get("X-RateLimit-Reset")
    if remaining is not None and int(remaining) == 0 and reset_at is not None:
        reset_time = datetime.fromtimestamp(int(reset_at), tz=timezone.utc)
        wait = (reset_time - datetime.now(tz=timezone.utc)).total_seconds() + 1
        if wait > 0:
            print(f"  ⏳ Rate limit reached. Sleeping {wait:.0f}s...")
            time.sleep(wait)


# ---------------------------------------------------------------------------
# Priority field discovery & helpers
# ---------------------------------------------------------------------------

def _find_priority_field(
    token: str, owner: str, repo: str
) -> tuple[str | None, str | None, dict[str, str] | None]:
    """
    Discover the V2 project field ID and the Priority single-select field ID.

    Uses a recent issue (if any exist) or walks the repo's projects.

    Returns (project_node_id, field_id, option_name_to_id) or (None, None, None).
    """
    # Strategy: use the repository's projectV2 connection to find a project
    # with a "Priority" field, then cache its ids.
    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        projectsV2(first: 10) {
          nodes {
            id
            title
            fields(first: 20) {
              nodes {
                ... on ProjectV2SingleSelectField {
                  id
                  name
                  options {
                    id
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    data = _graphql_request(token, query, {"owner": owner, "repo": repo})
    projects = data.get("repository", {}).get("projectsV2", {}).get("nodes", []) or []

    for project in projects:
        for field in project.get("fields", {}).get("nodes", []) or []:
            if (
                field
                and field.get("name") == PRIORITY_FIELD_NAME
                and field.get("options")
            ):
                options = {
                    opt["name"]: opt["id"] for opt in field["options"] if opt.get("name")
                }
                return project["id"], field["id"], options

    return None, None, None


def _get_issue_project_item(
    token: str,
    owner: str,
    repo: str,
    issue_number: int,
    project_node_id: str,
) -> tuple[str | None, str | None, dict[str, str] | None]:
    """Get the project item ID and current priority value for a specific issue."""
    query = """
    query($owner: String!, $repo: String!, $issueNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $issueNumber) {
          id
          projectItems(first: 20) {
            nodes {
              id
              project {
                id
              }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    field {
                      ... on ProjectV2SingleSelectField {
                        name
                      }
                    }
                    name
                    optionId
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    data = _graphql_request(
        token, query,
        {"owner": owner, "repo": repo, "issueNumber": issue_number},
    )
    issue = data.get("repository", {}).get("issue")
    if not issue:
        return None, None, None

    for item in (issue.get("projectItems", {}).get("nodes", []) or []):
        if not item:
            continue
        if item.get("project", {}).get("id") == project_node_id:
            # Find the priority field value
            priority_value = None
            priority_option_id = None
            for fv in item.get("fieldValues", {}).get("nodes", []) or []:
                if (
                    fv
                    and fv.get("field", {}).get("name") == PRIORITY_FIELD_NAME
                ):
                    priority_value = fv.get("name")
                    priority_option_id = fv.get("optionId")
            return item["id"], priority_value, priority_option_id

    return None, None, None


def _set_project_field(
    token: str,
    project_id: str,
    item_id: str,
    field_id: str,
    option_id: str,
    dry_run: bool = False,
) -> None:
    """Set a project item's single-select field to a specific option."""
    if dry_run:
        print(f"  [dry-run] Would set field {field_id} to option {option_id}")
        return

    _graphql_request(
        token,
        UPDATE_FIELD_VALUE_MUTATION,
        {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "valueId": option_id,
        },
    )


def _clear_project_field(
    token: str,
    project_id: str,
    item_id: str,
    field_id: str,
    dry_run: bool = False,
) -> None:
    """Clear a project item's single-select field value."""
    if dry_run:
        print(f"  [dry-run] Would clear field {field_id}")
        return

    _graphql_request(
        token,
        CLEAR_FIELD_VALUE_MUTATION,
        {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
        },
    )


# ---------------------------------------------------------------------------
# Sync logic
# ---------------------------------------------------------------------------

def _remove_stale_labels(
    issue: Any, current_labels: set[str], desired_labels: set[str],
    dry_run: bool = False,
) -> bool:
    """Remove priority labels that should not be on the issue. Returns True if changed."""
    stale_labels = current_labels & ALL_PRIORITY_LABELS - desired_labels
    if not stale_labels:
        return False

    for label in sorted(stale_labels):
        print(f"  Removing label: {label}")
        if not dry_run:
            try:
                issue.remove_from_labels(label)
            except GithubException as exc:
                print(f"  ⚠ Failed to remove label {label}: {exc}")
    return True


def _add_missing_labels(
    issue: Any, current_labels: set[str], desired_labels: set[str],
    dry_run: bool = False,
) -> bool:
    """Add priority labels that should be on the issue. Returns True if changed."""
    missing_labels = desired_labels - current_labels
    if not missing_labels:
        return False

    for label in sorted(missing_labels):
        print(f"  Adding label: {label}")
        if not dry_run:
            try:
                issue.add_to_labels(label)
            except GithubException as exc:
                print(f"  ⚠ Failed to add label {label}: {exc}")
    return True


def sync_labels_to_field(
    gh: Github,
    token: str,
    owner: str,
    repo_name: str,
    project_id: str,
    field_id: str,
    option_map: dict[str, str],
    dry_run: bool = False,
) -> None:
    """
    Sync direction: labels → Priority field.

    For every open issue/PR, if it has a priority label set but the Priority
    field doesn't match, update the field.
    """
    repo = gh.get_repo(f"{owner}/{repo_name}")
    # Process issues and PRs (GitHub treats PRs as issues with a pull_request)
    issues = repo.get_issues(state="open")

    for issue in issues:
        labels = {label.name for label in issue.labels}

        # Determine what priority field value the labels indicate
        desired_priority: str | None = None
        for label_name in labels:
            if label_name in LABEL_TO_PRIORITY:
                desired_priority = LABEL_TO_PRIORITY[label_name]
                break  # First match wins

        if desired_priority is None:
            continue  # No priority label on this issue

        # Check current field value
        item_id, current_priority, _ = _get_issue_project_item(
            token, owner, repo_name, issue.number, project_id
        )
        if item_id is None:
            continue  # Issue not in project

        if current_priority == desired_priority:
            continue  # Already in sync

        option_id = option_map.get(desired_priority)
        if option_id is None:
            print(f"  ⚠ No option ID found for priority '{desired_priority}'")
            continue

        direction = "→".join(
            [current_priority or "(none)", desired_priority]
        )
        print(f"  #{issue.number} field: {direction}")
        _set_project_field(token, project_id, item_id, field_id, option_id, dry_run)


def sync_field_to_labels(
    gh: Github,
    token: str,
    owner: str,
    repo_name: str,
    project_id: str,
    field_id: str,
    dry_run: bool = False,
) -> None:
    """
    Sync direction: Priority field → labels.

    For every open issue/PR, if the Priority field is set but its
    corresponding label(s) are missing (or wrong labels are present),
    fix the labels.
    """
    repo = gh.get_repo(f"{owner}/{repo_name}")
    issues = repo.get_issues(state="open")

    for issue in issues:
        item_id, priority_value, _ = _get_issue_project_item(
            token, owner, repo_name, issue.number, project_id
        )
        if item_id is None or priority_value is None:
            continue  # Issue not in project or no priority set

        desired_labels = set(PRIORITY_TO_LABELS.get(priority_value, []))
        current_labels = {label.name for label in issue.labels}

        if current_labels & ALL_PRIORITY_LABELS == desired_labels:
            continue  # Already in sync

        direction = "→".join(
            [
                ",".join(sorted(current_labels & ALL_PRIORITY_LABELS)) or "(none)",
                ",".join(sorted(desired_labels)) or "(none)",
            ]
        )
        print(f"  #{issue.number} labels: {direction}")

        changed = False
        changed |= _remove_stale_labels(issue, current_labels, desired_labels, dry_run)
        changed |= _add_missing_labels(issue, current_labels, desired_labels, dry_run)
        if not changed and dry_run:
            print("    (labels already in sync)")


def sync_bidirectional(
    gh: Github,
    token: str,
    owner: str,
    repo_name: str,
    project_id: str,
    field_id: str,
    option_map: dict[str, str],
    dry_run: bool = False,
) -> None:
    """
    Full bidirectional sync (field wins on conflict).

    For every open issue/PR, if either the labels or field are out of
    sync, bring them into agreement. When both are set but disagree,
    the Priority field value takes precedence.
    """
    repo = gh.get_repo(f"{owner}/{repo_name}")
    issues = repo.get_issues(state="open")

    for issue in issues:
        current_labels = {label.name for label in issue.labels}

        # Determine label-implied priority
        label_priority: str | None = None
        for label_name in current_labels:
            if label_name in LABEL_TO_PRIORITY:
                label_priority = LABEL_TO_PRIORITY[label_name]
                break

        # Get field-implied priority
        item_id, field_priority, field_option_id = _get_issue_project_item(
            token, owner, repo_name, issue.number, project_id
        )

        # Case 1: Neither is set → nothing to do
        if label_priority is None and field_priority is None:
            continue

        # Case 2: Only field is set → sync labels to match field
        if label_priority is None and field_priority is not None:
            desired_labels = set(PRIORITY_TO_LABELS.get(field_priority, []))
            print(f"  #{issue.number} (field-only) → labels: {','.join(sorted(desired_labels)) or '(none)'}")
            _remove_stale_labels(issue, current_labels, desired_labels, dry_run)
            _add_missing_labels(issue, current_labels, desired_labels, dry_run)
            continue

        # Case 3: Only labels are set → sync field to match labels
        if label_priority is not None and field_priority is None:
            option_id = option_map.get(label_priority)
            if option_id and item_id:
                direction = "→".join(["(none)", label_priority])
                print(f"  #{issue.number} field: {direction}")
                _set_project_field(token, project_id, item_id, field_id, option_id, dry_run)
            continue

        # Case 4: Both are set — field wins
        if label_priority != field_priority and field_priority is not None:
            desired_labels = set(PRIORITY_TO_LABELS.get(field_priority, []))
            print(
                f"  #{issue.number} conflict (field wins): "
                f"labels {label_priority or '(none)'} → {','.join(sorted(desired_labels)) or '(none)'}"
            )
            _remove_stale_labels(issue, current_labels, desired_labels, dry_run)
            _add_missing_labels(issue, current_labels, desired_labels, dry_run)
        elif label_priority == field_priority:
            # Both agree — ensure labels are exactly right
            desired_labels = set(PRIORITY_TO_LABELS.get(field_priority, []))
            if current_labels & ALL_PRIORITY_LABELS != desired_labels:
                print(f"  #{issue.number} cleanup labels")
                _remove_stale_labels(issue, current_labels, desired_labels, dry_run)
                _add_missing_labels(issue, current_labels, desired_labels, dry_run)


# ---------------------------------------------------------------------------
# Ensure priority labels exist in the repository
# ---------------------------------------------------------------------------

def ensure_labels_exist(gh: Github, owner: str, repo_name: str, dry_run: bool = False) -> None:
    """Create any missing priority labels in the repository."""
    repo = gh.get_repo(f"{owner}/{repo_name}")
    existing_labels = {label.name: label for label in repo.get_labels()}

    # Colors for priority labels
    COLORS: dict[str, str] = {
        "priority-★★★": "B60205",  # Red
        "priority-★★☆": "FBCA04",  # Yellow
        "priority-★☆☆": "0E8A16",  # Green
    }

    for label_name in ALL_PRIORITY_LABELS:
        if label_name not in existing_labels:
            color = COLORS.get(label_name, "D4C5F9")
            print(f"  Creating label: {label_name} (color: {color})")
            if not dry_run:
                try:
                    repo.create_label(name=label_name, color=color)
                except GithubException as exc:
                    print(f"  ⚠ Failed to create label {label_name}: {exc}")


# ---------------------------------------------------------------------------
# Determine what triggered the run
# ---------------------------------------------------------------------------

def _get_event_type() -> str:
    """Return the GitHub event type that triggered this workflow."""
    return os.environ.get("GITHUB_EVENT_NAME", "schedule")


def _get_event_action() -> str:
    """Return the action sub-type (e.g., 'labeled', 'opened') if available."""
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        return ""
    import json
    with open(event_path) as f:
        event = json.load(f)
    return event.get("action", "")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync GitHub issue Priority field and priority labels"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print what would be changed without making changes",
    )
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN environment variable is required")
        sys.exit(1)

    repo_full = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in repo_full:
        print(f"❌ Invalid GITHUB_REPOSITORY: {repo_full}")
        sys.exit(1)
    owner, repo_name = repo_full.split("/", 1)

    dry_run = args.dry_run
    if os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes"):
        dry_run = True

    event_type = _get_event_type()
    event_action = _get_event_action()

    print(f"🔍 Repo: {owner}/{repo_name}")
    print(f"📌 Event: {event_type}" + (f" ({event_action})" if event_action else ""))
    print(f"🧪 Dry run: {dry_run}")
    print()

    # Initialize GitHub clients
    auth = Auth.Token(token)
    gh = Github(auth=auth, per_page=100)

    try:
        # Discover the Priority field
        print("🔎 Discovering Priority project field...")
        project_id, field_id, option_map = _find_priority_field(token, owner, repo_name)

        if field_id is None:
            print(
                "⚠ Could not find a project with a 'Priority' field in this repository.\n"
                "   No project field sync will be performed. Only labels will be ensured."
            )
            # At minimum, ensure priority labels exist
            ensure_labels_exist(gh, owner, repo_name, dry_run)
            print("✅ Label check complete. Nothing else to sync.")
            return

        print(f"   Project: {project_id}")
        print(f"   Field: {field_id}")
        print(f"   Options: {option_map}")
        print()

        # Ensure labels exist before syncing
        print("🏷 Ensuring priority labels exist...")
        ensure_labels_exist(gh, owner, repo_name, dry_run)
        print()

        # Determine sync direction based on trigger
        if event_action == "labeled":
            print("🔄 Syncing direction: label → field (new label detected)")
            sync_labels_to_field(
                gh, token, owner, repo_name, project_id, field_id, option_map, dry_run
            )
        elif event_action == "unlabeled":
            print("🔄 Syncing direction: label → field (label removed)")
            sync_labels_to_field(
                gh, token, owner, repo_name, project_id, field_id, option_map, dry_run
            )
        elif event_type == "schedule":
            print("🔄 Syncing direction: field → labels (scheduled run)")
            sync_field_to_labels(
                gh, token, owner, repo_name, project_id, field_id, dry_run
            )
        else:
            print("🔄 Syncing direction: bidirectional (field wins on conflict)")
            sync_bidirectional(
                gh, token, owner, repo_name, project_id, field_id, option_map, dry_run
            )

        print()
        print("✅ Priority sync complete.")

    except Exception as exc:
        print(f"❌ Sync failed: {exc}")
        sys.exit(1)
    finally:
        gh.close()


if __name__ == "__main__":
    main()
