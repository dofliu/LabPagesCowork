#!/usr/bin/env python3
"""Refresh public GitHub data used by DOF Lab pages."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
API = "https://api.github.com"


def today() -> str:
    return datetime.now(UTC).date().isoformat()


def get_json(url: str) -> object:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "DOF-Lab-site-sync",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(request, timeout=30) as response:  # nosec B310: fixed HTTPS API URL
        return json.load(response)


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return data


def dump_json(data: dict[str, object]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def same_without_updated(left: dict[str, object], right: dict[str, object]) -> bool:
    left_copy = dict(left)
    right_copy = dict(right)
    left_copy.pop("_updated", None)
    right_copy.pop("_updated", None)
    return left_copy == right_copy


def write_if_changed(path: Path, payload: dict[str, object]) -> bool:
    rendered = dump_json(payload)
    previous = path.read_text(encoding="utf-8") if path.exists() else ""
    if rendered == previous:
        return False
    path.write_text(rendered, encoding="utf-8")
    return True


def classify_repo(repo: dict[str, object]) -> str:
    text = " ".join(
        str(repo.get(key) or "")
        for key in ("name", "description", "language")
    ).lower()
    topics = repo.get("topics")
    if isinstance(topics, list):
        text += " " + " ".join(str(topic).lower() for topic in topics)

    if any(word in text for word in ("mcp", "modbus", "opc", "plc")):
        return "mcp_tools"
    if any(word in text for word in ("wind", "scada", "turbine", "maintenance", "om")):
        return "wind_energy"
    if any(word in text for word in ("rag", "llm", "langchain", "knowledge", "agent")):
        return "rag_knowledge"
    if any(word in text for word in ("industrial", "inspection", "automation")):
        return "industrial_ai"
    if any(word in text for word in ("course", "edu", "exam", "teaching", "student")):
        return "edtech"
    return "personal_tools"


def repo_project(repo: dict[str, object]) -> dict[str, object]:
    name = str(repo.get("name") or "")
    pushed_at = str(repo.get("pushed_at") or "")
    updated = pushed_at[:10] if pushed_at else ""
    language = repo.get("language")
    topics = repo.get("topics") if isinstance(repo.get("topics"), list) else []
    technologies = [str(language)] if language else []
    technologies.extend(str(topic) for topic in topics[:2])

    return {
        "name": name,
        "name_zh": name,
        "category": classify_repo(repo),
        "status": "active",
        "source": "github",
        "github_pushed_at": pushed_at,
        "last_updated": updated,
        "url": repo.get("html_url") or f"https://github.com/dofliu/{name}",
        "description": repo.get("description") or "GitHub public repository",
        "description_zh": repo.get("description") or "GitHub public repository",
        "technologies": technologies[:3],
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "key_metrics": f"GitHub updated {updated}" if updated else "GitHub public repository",
    }


def refresh_cache(output: Path, username: str, payload: dict[str, object]) -> bool:
    previous = load_json(output) if output.exists() else {}
    next_payload = dict(payload)
    next_payload["_updated"] = (
        previous.get("_updated", today())
        if previous and same_without_updated(previous, next_payload)
        else today()
    )
    return write_if_changed(output, next_payload)


def refresh_project_data(data_json: Path, username: str, repos: list[dict[str, object]], limit: int) -> bool:
    data = load_json(data_json)
    recent_projects = [repo_project(repo) for repo in repos[:limit]]

    if data.get("github_recent_projects") == recent_projects:
        return False

    # 將 GitHub 動態資料放在獨立欄位，避免覆蓋人工維護的專案成果。
    data["github_projects_source"] = f"https://github.com/{username}"
    data["github_projects_updated"] = today()
    data["github_recent_projects"] = recent_projects
    return write_if_changed(data_json, data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh DOF Lab public GitHub data.")
    parser.add_argument("--username", default="dofliu", help="GitHub account to cache")
    parser.add_argument("--output", type=Path, default=ROOT / "github-data.json")
    parser.add_argument("--data-json", type=Path, default=ROOT / "data.json")
    parser.add_argument("--project-limit", type=int, default=9)
    args = parser.parse_args()

    try:
        profile = get_json(f"{API}/users/{args.username}")
        repos = get_json(
            f"{API}/users/{args.username}/repos?per_page=100&sort=pushed&type=owner"
        )
        events = get_json(f"{API}/users/{args.username}/events/public?per_page=30")
    except (HTTPError, URLError, TimeoutError) as error:
        print(f"Unable to refresh GitHub data: {error}", file=sys.stderr)
        return 1

    if not isinstance(profile, dict) or not isinstance(repos, list) or not isinstance(events, list):
        print("Unexpected GitHub API response.", file=sys.stderr)
        return 1

    owner_repos = [
        repo for repo in repos
        if isinstance(repo, dict) and not repo.get("fork") and not repo.get("archived")
    ]
    payload = {
        "_source": f"https://github.com/{args.username}",
        "profile": profile,
        "repos": owner_repos,
        "events": events,
    }

    cache_changed = refresh_cache(args.output, args.username, payload)
    projects_changed = refresh_project_data(args.data_json, args.username, owner_repos, args.project_limit)

    if cache_changed:
        print(f"Updated {args.output.relative_to(ROOT)} ({len(owner_repos)} repositories).")
    else:
        print("GitHub cache is already current.")
    if projects_changed:
        print(f"Updated {args.data_json.relative_to(ROOT)} GitHub recent projects.")
    else:
        print("GitHub recent projects are already current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
