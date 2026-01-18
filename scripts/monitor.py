import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

import httpx

from config import config


class GitHubMonitor:
    def __init__(self):
        self.headers = {
            "Authorization": f"token {config.GITHUB_TOKEN}" if config.GITHUB_TOKEN else "",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "MaiBot-docs-sync-bot",
        }
        self.base_url = f"https://api.github.com/repos/{config.REPO_NAME}"
        self.client = httpx.Client(headers=self.headers, timeout=30.0)

    def _load_state(self) -> Dict:
        try:
            with open(config.STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"last_commit_sha": "", "last_tag": ""}

    def _save_state(self, state: Dict) -> None:
        with open(config.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4, ensure_ascii=False)

    def get_latest_commits(self, since_sha: str = "") -> List[Dict]:
        """获取自 since_sha 之后的所有 commits（限定到指定分支）。"""
        url = f"{self.base_url}/commits"
        params = {"per_page": 100, "page": 1, "sha": config.UPSTREAM_BRANCH}

        new_commits: List[Dict] = []
        max_pages = 10
        while params["page"] <= max_pages:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            commits = response.json() or []
            if not commits:
                break

            for commit in commits:
                if since_sha and commit.get("sha") == since_sha:
                    return new_commits
                new_commits.append(commit)

            params["page"] += 1

        return new_commits

    def get_commits_since(self, since_iso: str) -> List[Dict]:
        url = f"{self.base_url}/commits"
        params = {"per_page": 100, "since": since_iso, "sha": config.UPSTREAM_BRANCH}
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json() or []

    def get_commit_diff(self, sha: str) -> str:
        """获取特定 commit 的 diff 内容"""
        url = f"{self.base_url}/commits/{sha}"
        response = self.client.get(url, headers={"Accept": "application/vnd.github.v3.diff"})
        response.raise_for_status()
        return response.text

    def get_latest_tags(self) -> List[Dict]:
        url = f"{self.base_url}/tags"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json() or []

    def check_for_updates(self, force_latest: bool = False) -> Tuple[List[Dict], Dict]:
        state = self._load_state()
        last_sha = state.get("last_commit_sha")
        last_tag = state.get("last_tag")

        print(f"Checking for updates in {config.REPO_NAME}@{config.UPSTREAM_BRANCH}...")

        # 1) Tags (only when snapshots are enabled; tags are repo-level)
        new_tags: List[Dict] = []
        if config.ENABLE_SNAPSHOTS:
            tags = self.get_latest_tags()
            if tags:
                current_latest_tag = tags[0].get("name")
                if current_latest_tag and current_latest_tag != last_tag:
                    if last_tag:
                        for tag in tags:
                            if tag.get("name") == last_tag:
                                break
                            new_tags.append(tag)
                    else:
                        # 初次运行避免生成历史海量快照：只取最新一个
                        new_tags = [tags[0]]

                    state["last_tag"] = current_latest_tag

        # 2) Commits (branch-scoped)
        commits: List[Dict] = []
        if force_latest:
            url = f"{self.base_url}/commits"
            params = {"per_page": 1, "sha": config.UPSTREAM_BRANCH}
            response = self.client.get(url, params=params)
            response.raise_for_status()
            commits = response.json() or []
        elif not last_sha:
            since_dt = datetime.now(timezone.utc) - timedelta(hours=config.SYNC_LOOKBACK_HOURS)
            commits = self.get_commits_since(since_dt.isoformat())
        else:
            commits = self.get_latest_commits(since_sha=last_sha)

        if commits:
            state["last_commit_sha"] = commits[0].get("sha")

        changes: List[Dict] = []

        # Releases (old -> new)
        for tag in reversed(new_tags):
            changes.append(
                {
                    "type": "release",
                    "title": f"New Release: {tag.get('name', '')}",
                    "tag_name": tag.get("name", ""),
                    "sha": (tag.get("commit") or {}).get("sha", ""),
                }
            )

        # Commits (old -> new)
        for commit in reversed(commits):
            sha = commit.get("sha", "")
            commit_obj = commit.get("commit") or {}
            message = (commit_obj.get("message") or "").strip()
            author = ((commit_obj.get("author") or {}).get("name") or "").strip()

            diff = self.get_commit_diff(sha) if sha else ""
            changes.append(
                {
                    "type": "commit",
                    "sha": sha,
                    "author": author,
                    "message": message,
                    "diff": diff,
                }
            )

        return changes, state

    def save_state(self, state: Dict) -> None:
        self._save_state(state)

