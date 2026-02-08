#!/usr/bin/env python3
"""Auto-keep daemon: watch directories and run `git_auto_keep.git_add_commit` on changed files.

Usage examples:
  # Dry-run once (show what would be committed):
  py -3 scripts/auto_keep_daemon.py --watch committed_artifacts,checks --once --dry-run

  # Run continuously (background):
  py -3 scripts/auto_keep_daemon.py --watch committed_artifacts,checks --interval 10

  # Run and push commits to a branch named 'auto-keep' (careful):
  py -3 scripts/auto_keep_daemon.py --watch committed_artifacts,checks --interval 10 --branch auto-keep --push

Defaults & safety:
 - Default watch dirs are `committed_artifacts` and `checks`.
 - Does NOT push by default (use --push to enable push).
 - Has --dry-run and --once modes for safe testing.
 - Ignores common unwanted patterns, configurable via --exclude.

This is intentionally minimal (no external deps) and uses mtimes to detect file additions/changes.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

# import local helper
try:
    import git_auto_keep
except Exception:  # pragma: no cover - permissive import
    git_auto_keep = None

DEFAULT_WATCH = ["committed_artifacts", "checks"]
# Add common temporary/check artifacts to exclude to avoid noisy commits and
# pre-commit conflicts on Windows (e.g., checks/_tmp_seed_shrink_*.json).
DEFAULT_EXCLUDE = [".git", "*.bak", "*.localbak", "*.tmp", "*~", "checks/_tmp_*", "checks/*_tmp_*"]
LOG_PATH = Path("committed_artifacts") / "auto_keep.log"


def scan_dir_files(dirs: List[Path], exclude_patterns: List[str]) -> Dict[str, float]:
    """Return a map of file_path -> mtime for files inside dirs (recursive)."""
    files = {}
    for d in dirs:
        if not d.exists():
            continue
        for root, _, filenames in os.walk(d):
            for fn in filenames:
                path = Path(root) / fn
                rel = str(path)
                skip = False
                for pat in exclude_patterns:
                    if fnmatch.fnmatch(path.name, pat) or fnmatch.fnmatch(rel, pat) or pat in rel:
                        skip = True
                        break
                if skip:
                    continue
                try:
                    m = path.stat().st_mtime
                except OSError:
                    continue
                files[rel] = m
    return files


def commit_files(files: List[str], branch: str | None = None, push: bool = False) -> Tuple[bool, str]:
    """
    Commit files, skipping ignored ones. For files ignored by git (e.g., in checks/),
    copy them to `committed_artifacts/<filename>` and commit the copy instead.
    """
    if git_auto_keep is None:
        return False, "git_auto_keep module not available"

    import subprocess

    to_commit: List[str] = []
    copied: List[str] = []

    for f in files:
        p = Path(f)
        # check if file is ignored by git
        try:
            res = subprocess.run(["git", "check-ignore", "-q", "--", str(p)], check=False)
            is_ignored = (res.returncode == 0)
        except Exception:
            is_ignored = False

        if is_ignored:
            # if file is under `checks/`, copy to committed_artifacts and commit the copy
            if p.parts and p.parts[0] == "checks":
                dest = Path("committed_artifacts") / p.name
                try:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(p.read_bytes())
                    to_commit.append(str(dest))
                    copied.append(str(dest))
                except Exception:
                    # couldn't copy; skip this file
                    continue
            else:
                # skip other ignored files
                continue
        else:
            to_commit.append(str(p))

    if not to_commit:
        return False, "No non-ignored files to commit"

    # Commit files in batches to avoid overly long git commands or very large commits
    BATCH_SIZE = 100
    successes = 0
    messages = []
    try:
        chunks = [to_commit[i : i + BATCH_SIZE] for i in range(0, len(to_commit), BATCH_SIZE)]
        for idx, chunk in enumerate(chunks):
            msg = f"auto-keep: {len(chunk)} file(s) changed ({idx+1}/{len(chunks)}): " + ", ".join(Path(f).name for f in chunk[:5])
            ok, out = git_auto_keep.git_add_commit(chunk, msg, branch=branch, push=push)
            if ok:
                successes += 1
            # annotate copied files in this chunk
            copied_in_chunk = sum(1 for f in chunk if f in copied)
            if copied_in_chunk:
                out = f"{out}; copied {copied_in_chunk} ignored file(s) to committed_artifacts"
            messages.append(out)
        overall_ok = successes > 0
        return overall_ok, "; ".join(messages)
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", type=str, default=','.join(DEFAULT_WATCH), help="Comma-separated list of directories to watch")
    parser.add_argument("--interval", type=float, default=10.0, help="Polling interval in seconds")
    parser.add_argument("--exclude", type=str, default=','.join(DEFAULT_EXCLUDE), help="Comma-separated exclude patterns")
    parser.add_argument("--branch", type=str, default=None, help="Optional branch name to push to")
    parser.add_argument("--push", action="store_true", help="Push commits to remote branch after committing (opt-in)")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be committed")
    parser.add_argument("--once", action="store_true", help="Run one scan and exit")
    args = parser.parse_args()

    watch_dirs = [Path(p.strip()) for p in args.watch.split(',') if p.strip()]
    exclude_patterns = [p.strip() for p in args.exclude.split(',') if p.strip()]
    interval = float(args.interval)

    # initial snapshot
    snapshot = scan_dir_files(watch_dirs, exclude_patterns)
    print(f"Watching: {[str(p) for p in watch_dirs]} (interval={interval}s) -> {len(snapshot)} files seen")

    def log(msg: str):
        ts = datetime.utcnow().isoformat() + 'Z'
        out = f"[{ts}] {msg}\n"
        try:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(out)
        except Exception:
            pass
        print(out.strip())

    # single pass: just show what would be committed
    if args.dry_run and args.once:
        current = scan_dir_files(watch_dirs, exclude_patterns)
        added_or_changed = [p for p, m in current.items() if p not in snapshot or snapshot[p] < m]
        if added_or_changed:
            print("Dry-run: would commit the following files:")
            for p in added_or_changed:
                print("  ", p)
        else:
            print("Dry-run: no changes detected")
        return

    if args.once:
        current = scan_dir_files(watch_dirs, exclude_patterns)
        added_or_changed = [p for p, m in current.items() if p not in snapshot or snapshot[p] < m]
        if added_or_changed:
            if args.dry_run:
                print("Dry-run once: would commit:")
                for p in added_or_changed:
                    print("  ", p)
            else:
                ok, msg = commit_files(added_or_changed, branch=args.branch, push=args.push)
                log(f"Once commit: ok={ok} msg={msg} files={len(added_or_changed)}")
        else:
            print("Once: no changes detected")
        return

    # continuous loop
    try:
        while True:
            current = scan_dir_files(watch_dirs, exclude_patterns)
            added_or_changed = [p for p, m in current.items() if p not in snapshot or snapshot[p] < m]
            removed = [p for p in snapshot.keys() if p not in current]
            if added_or_changed:
                if args.dry_run:
                    print("Dry-run: would commit:")
                    for p in added_or_changed:
                        print("  ", p)
                else:
                    ok, msg = commit_files(added_or_changed, branch=args.branch, push=args.push)
                    log(f"Committed {len(added_or_changed)} files (ok={ok}): {msg}")
                # update snapshot for committed files
                for p in added_or_changed:
                    snapshot[p] = current.get(p, snapshot.get(p))
            # update snapshot for removed files
            for p in removed:
                snapshot.pop(p, None)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Auto-keep daemon stopped by user")


if __name__ == '__main__':
    main()
