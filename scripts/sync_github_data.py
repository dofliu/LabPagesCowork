#!/usr/bin/env python3
"""Create an offline cache of the public GitHub profile used by github.html.

The page still asks GitHub for fresh data in a visitor's browser.  This cache
is a graceful fallback for rate-limited or offline visitors and is refreshed by
the scheduled GitHub Actions workflow.
"""

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


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh the DOF Lab GitHub cache.")
    parser.add_argument("--username", default="dofliu", help="GitHub account to cache")
    parser.add_argument("--output", type=Path, default=ROOT / "github-data.json")
    args = parser.parse_args()

    try:
        profile = get_json(f"{API}/users/{args.username}")
        repos = get_json(
            f"{API}/users/{args.username}/repos?per_page=100&sort=pushed&type=owner"
        )
        events = get_json(f"{API}/users/{args.username}/events/public?per_page=30")
    except (HTTPError, URLError, TimeoutError) as error:
        print(f"Unable to refresh GitHub cache: {error}", file=sys.stderr)
        return 1

    if not isinstance(profile, dict) or not isinstance(repos, list) or not isinstance(events, list):
        print("Unexpected GitHub API response.", file=sys.stderr)
        return 1

    payload = {
        "_source": f"https://github.com/{args.username}",
        "_updated": datetime.now(UTC).date().isoformat(),
        "profile": profile,
        "repos": [repo for repo in repos if not repo.get("fork")],
        "events": events,
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    previous = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
    if rendered == previous:
        print("GitHub cache is already current.")
        return 0

    args.output.write_text(rendered, encoding="utf-8")
    try:
        display_path = args.output.relative_to(ROOT)
    except ValueError:
        display_path = args.output
    print(f"Updated {display_path} ({len(payload['repos'])} repositories).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
