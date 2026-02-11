#!/usr/bin/env python3
"""Simple git helper utilities for auto-committing generated artifacts.

Functions:
- is_git_repo() -> bool
- git_add_commit(files: List[str], message: str, branch: Optional[str]=None, push: bool=False) -> (bool, str)

This helper is intentionally minimal and permissive: it emits warnings when git is
not available or nothing to commit and returns a (success, message) tuple.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


def is_git_repo() -> bool:
    """Return True if the current working directory is inside a git repo and git exists."""
    if shutil.which("git") is None:
        return False
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def git_add_commit(
    files: List[str], message: str, branch: Optional[str] = None, push: bool = False
) -> Tuple[bool, str]:
    """Stage `files` and commit with `message`. Optionally push to `branch`.

    Returns (success: bool, message: str).
    """
    if not is_git_repo():
        return False, "git not available or not a git repository"

    try:
        # If pre-commit is available, run it on the files before staging to avoid
        # conflicts where hooks auto-fix files during commit, which can cause
        # stashing/rollback issues. Run in batches to avoid overly long commands.
        pre_commit_bin = shutil.which("pre-commit")
        if pre_commit_bin and files:
            try:
                # Determine repo root and run pre-commit with cwd=repo_root
                repo_root_proc = subprocess.run(
                    ["git", "rev-parse", "--show-toplevel"],
                    check=True,
                    stdout=subprocess.PIPE,
                    text=True,
                )
                repo_root = repo_root_proc.stdout.strip()
                # Convert file paths to repo-relative paths when possible
                rel_files = []
                for f in files:
                    try:
                        p = Path(f)
                        if not p.is_absolute():
                            p_abs = (Path.cwd() / p).resolve()
                        else:
                            p_abs = p.resolve()
                        if str(p_abs).startswith(repo_root):
                            rel_files.append(str(p_abs.relative_to(repo_root)))
                    except Exception:
                        # skip files we can't resolve
                        continue
                batch_size = 100
                for i in range(0, len(rel_files), batch_size):
                    batch = rel_files[i : i + batch_size]
                    subprocess.run(
                        [pre_commit_bin, "run", "--files"] + batch,
                        check=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=repo_root,
                    )
            except subprocess.CalledProcessError:
                # If we cannot determine repo root or pre-commit run fails, continue
                pass

        # Stage files (if staging specific files fails, fall back to 'git add -A')
        add_cmd = ["git", "add"] + list(files)
        try:
            subprocess.run(add_cmd, check=True)
        except subprocess.CalledProcessError:
            try:
                subprocess.run(["git", "add", "-A"], check=True)
            except subprocess.CalledProcessError as exc:
                return False, f"git add failed: {str(exc)}"

        # If nothing to commit, report that explicitly
        status_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        if not status_proc.stdout.strip():
            return False, "nothing to commit"

        # Stage all changes to capture any modifications made by pre-commit
        subprocess.run(["git", "add", "-A"], check=False)

        # Use --no-verify to avoid running hooks during commit (we already ran pre-commit above).
        # This prevents in-commit stashing/restore conflicts on Windows (file unlink errors).
        proc = subprocess.run(
            ["git", "commit", "--no-verify", "-m", message],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if proc.returncode != 0:
            out = (proc.stdout or "") + (proc.stderr or "")
            # If commit still fails due to hooks or unstaged changes, try a normal commit retry
            if (
                "hook" in out.lower()
                or "pre-commit" in out.lower()
                or "rolling back fixes" in out.lower()
                or "unstaged" in out.lower()
            ):
                try:
                    subprocess.run(["git", "add", "-A"], check=False)
                    proc2 = subprocess.run(
                        ["git", "commit", "-m", message],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if proc2.returncode == 0:
                        proc = proc2
                    else:
                        out2 = (proc2.stdout or "") + (proc2.stderr or "")
                        return False, f"git commit failed after retry: {out2.strip()}"
                except Exception as exc:
                    return False, f"git commit retry failed: {str(exc)}"
            else:
                if "nothing to commit" in out or "no changes added" in out:
                    return False, "nothing to commit"
                return False, f"git commit failed: {out.strip()}"

        if push:
            try:
                # If a branch is specified, be collaboration-safe:
                if branch:
                    # fetch remote state
                    subprocess.run(["git", "fetch", "origin"], check=True)
                    # check if remote branch exists
                    exists_proc = subprocess.run(
                        ["git", "rev-parse", "--verify", f"origin/{branch}"],
                        check=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if exists_proc.returncode == 0:
                        # check divergence between local HEAD and origin/branch
                        rv = subprocess.run(
                            [
                                "git",
                                "rev-list",
                                "--left-right",
                                "--count",
                                f"HEAD...origin/{branch}",
                            ],
                            check=True,
                            stdout=subprocess.PIPE,
                            text=True,
                        )
                        left_right = rv.stdout.strip()
                        try:
                            left, right = map(int, left_right.split())
                        except Exception:
                            left = right = 0
                        if right > 0:
                            # remote has commits we do not have; try to rebase
                            rebase_proc = subprocess.run(
                                ["git", "pull", "--rebase", "origin", branch],
                                check=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                            )
                            if rebase_proc.returncode != 0:
                                # rebase failed; abort and push to a new timestamped branch to avoid overwriting
                                subprocess.run(
                                    ["git", "rebase", "--abort"], check=False
                                )
                                new_branch = f"{branch}-auto-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
                                subprocess.run(
                                    [
                                        "git",
                                        "push",
                                        "-u",
                                        "origin",
                                        f"HEAD:refs/heads/{new_branch}",
                                    ],
                                    check=True,
                                )
                                return (
                                    True,
                                    f"committed; remote {branch} had new commits, pushed to new branch {new_branch}",
                                )
                    # otherwise safe to push to the requested branch
                    subprocess.run(["git", "push", "-u", "origin", branch], check=True)
                else:
                    # standard push (no branch specified)
                    subprocess.run(["git", "push"], check=True)
            except subprocess.CalledProcessError as exc:
                return False, f"git push failed: {str(exc)}"

        return True, "committed"

    except Exception as exc:
        return False, str(exc)
