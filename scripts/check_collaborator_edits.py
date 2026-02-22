#!/usr/bin/env python3
"""Write a short activity summary of recent git commits (useful to 'check in' on collaborators).

Writes `checks/PART_CVII_collaborator_activity_<timestamp>.json` with recent commit info.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List


def get_recent_commits(n: int = 10) -> List[Dict[str, Any]]:
    try:
        proc = subprocess.run(
            ["git", "log", "-n", str(n), "--pretty=format:%h|%an|%ad|%s"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        lines = [l for l in proc.stdout.splitlines() if l.strip()]
        commits = []
        for line in lines:
            parts = line.split("|", 3)
            if len(parts) < 4:
                continue
            h, author, date, subject = parts
            # list files changed in commit
            proc2 = subprocess.run(
                ["git", "show", "--name-only", "--pretty=format:", h],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            files = [f for f in proc2.stdout.splitlines() if f.strip()]
            commits.append(
                {
                    "hash": h,
                    "author": author,
                    "date": date,
                    "subject": subject,
                    "files": files,
                }
            )
        return commits
    except Exception:
        return []


def write_summary(n: int = 10) -> Path:
    commits = get_recent_commits(n)
    stamp = int(time.time())
    outp = Path.cwd() / "checks" / f"PART_CVII_collaborator_activity_{stamp}.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps({"commits": commits}, indent=2), encoding="utf-8")
    print("Wrote", outp)
    return outp


if __name__ == "__main__":
    write_summary()
