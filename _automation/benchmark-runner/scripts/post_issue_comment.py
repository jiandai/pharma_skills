import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

DEFAULT_REPO = os.environ.get("PHARMA_SKILLS_GITHUB_REPO", "RConsortium/pharma-skills")


def get_github_token() -> Optional[str]:
    return os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


def post_issue_comment(repo: str, issue_number: str, body: str) -> str:
    token = get_github_token()
    if not token:
        raise RuntimeError("GH_TOKEN or GITHUB_TOKEN is not set")

    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments",
        data=json.dumps({"body": body}).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "pharma-skills-benchmark-runner",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get("html_url", "")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Post a GitHub issue comment through REST API without gh."
    )
    parser.add_argument("issue_number", help="GitHub issue number to comment on")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="Repository in owner/name form")
    parser.add_argument("--body-file", required=True, help="Markdown file to post")
    args = parser.parse_args()

    try:
        body = Path(args.body_file).read_text()
        comment_url = post_issue_comment(args.repo, args.issue_number, body)
    except (OSError, RuntimeError, urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"Error posting issue comment: {e}", file=sys.stderr)
        sys.exit(1)

    print(comment_url or "Comment posted")


if __name__ == "__main__":
    main()
