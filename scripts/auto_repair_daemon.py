#!/usr/bin/env python3
"""Auto-repair daemon: watch committed_artifacts for new 'best' bijection artifacts
and trigger a conservative `run_local_patch_campaign.py` to attempt local CP-SAT repairs.

Usage examples:
  # Dry-run once (show what would be done):
  py -3 scripts/auto_repair_daemon.py --watch committed_artifacts --once --dry-run

  # Run continuously (background):
  py -3 scripts/auto_repair_daemon.py --watch committed_artifacts --interval 10

Defaults & safety:
 - Conservative defaults: small time limits, few iterations, no automatic pushing.
 - Writes a small state file at `committed_artifacts/auto_repair_state.json` to track
   the last seen best_exact to avoid duplicate triggers.
 - Requires no external deps (uses subprocess to run the existing campaign script).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

PATTERNS = ["committed_PART_CVII_e8_bijection_trial_*.json", "committed_PART_CVII_e8_bijection_campaign_best_*.json", "PART_CVII_e8_bijection_campaign_best_*.json"]
STATE_FILE = Path("committed_artifacts") / "auto_repair_state.json"
LOG_FILE = Path("committed_artifacts") / "auto_repair.log"


def log(msg: str):
    ts = datetime.utcnow().isoformat() + 'Z'
    out = f"[{ts}] {msg}\n"
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(out)
    except Exception:
        pass
    print(out.strip())


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def save_state(s: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(s, indent=2), encoding='utf-8')


def find_candidate_files(watch_dir: Path):
    files = []
    for pat in PATTERNS:
        files.extend(sorted(watch_dir.glob(pat), key=os.path.getmtime))
    return files


def best_exact_from_file(path: Path) -> Optional[int]:
    try:
        obj = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None
    # Try common locations
    if isinstance(obj, dict):
        if 'trial' in obj and isinstance(obj['trial'], dict) and 'best_exact' in obj['trial']:
            return int(obj['trial']['best_exact'])
        if 'final_exact' in obj:
            return int(obj['final_exact'])
        # fallback to verification.triangle_cocycle.exact_match
        v = obj.get('verification', {})
        if isinstance(v, dict):
            tc = v.get('triangle_cocycle', {})
            if isinstance(tc, dict) and 'exact_match' in tc:
                return int(tc['exact_match'])
    return None


def run_repair(bij_file: Path, edge_sizes: str, k: int, time_limit: float, max_iter: int, auto_commit: bool, commit_branch: Optional[str], push_commits: bool):
    cmd = [
        "py",
        "-3",
        "-X",
        "utf8",
        "scripts/run_local_patch_campaign.py",
        "--bij",
        str(bij_file),
        "--edge-sizes",
        edge_sizes,
        "--k",
        str(k),
        "--time-limit",
        str(time_limit),
        "--max-iter",
        str(max_iter),
    ]
    if auto_commit:
        cmd.append("--auto-commit")
    if commit_branch:
        cmd += ["--commit-branch", commit_branch]
    if push_commits:
        cmd.append("--push-commits")

    log(f"Starting local patch campaign: {' '.join(cmd)}")
    # Run synchronously (blocking) so we don't spin multiple concurrent repair jobs
    try:
        subprocess.run(cmd, check=True)
        log("Local patch campaign finished successfully")
    except subprocess.CalledProcessError as exc:
        log(f"Local patch campaign failed: {exc}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--watch', type=str, default='committed_artifacts')
    parser.add_argument('--interval', type=float, default=10.0)
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--min-delta', type=int, default=1, help='Minimum improvement in best_exact to trigger repair')
    parser.add_argument('--edge-sizes', type=str, default='24', help='Comma-separated edge sizes to pass to local campaign')
    parser.add_argument('--k', type=int, default=40)
    parser.add_argument('--time-limit', type=float, default=120.0, help='Time limit passed to local solver (seconds)')
    parser.add_argument('--max-iter', type=int, default=2, help='Max iterations for local patch campaign')
    parser.add_argument('--auto-commit', action='store_true', help='Let local campaign auto-commit intermediate bijections')
    parser.add_argument('--commit-branch', type=str, default='auto-keep')
    parser.add_argument('--push-commits', action='store_true', help='Push commits made by local campaign')
    args = parser.parse_args()

    watch_dir = Path(args.watch)
    snapshot = {str(p): p.stat().st_mtime for p in watch_dir.glob('*') if p.is_file()} if watch_dir.exists() else {}

    state = load_state()
    last_best = int(state.get('last_best_exact', -1))
    log(f"Starting auto-repair (watch={args.watch}, last_best={last_best})")

    # One-shot only: find current best and optionally run repair
    if args.once:
        files = find_candidate_files(watch_dir)
        candidate = None
        candidate_best = last_best
        for f in files:
            be = best_exact_from_file(f)
            if be is not None and be > candidate_best:
                candidate_best = be
                candidate = f
        if candidate and candidate_best >= last_best + args.min_delta:
            log(f"Would trigger repair on {candidate} with best_exact={candidate_best}")
            if not args.dry_run:
                run_repair(candidate, args.edge_sizes, args.k, args.time_limit, args.max_iter, args.auto_commit, args.commit_branch, args.push_commits)
                state['last_best_exact'] = candidate_best
                save_state(state)
        else:
            log('No new best found (once)')
        return

    # Continuous loop
    try:
        while True:
            files = find_candidate_files(watch_dir)
            candidate = None
            candidate_best = last_best
            for f in files:
                be = best_exact_from_file(f)
                if be is not None and be > candidate_best:
                    candidate_best = be
                    candidate = f

            if candidate and candidate_best >= last_best + args.min_delta:
                log(f"New best detected: {candidate} best_exact={candidate_best} (prev={last_best})")
                # update state immediately to avoid duplicate triggers
                last_best = candidate_best
                state['last_best_exact'] = last_best
                state['last_trigger_file'] = str(candidate)
                save_state(state)
                if not args.dry_run:
                    run_repair(candidate, args.edge_sizes, args.k, args.time_limit, args.max_iter, args.auto_commit, args.commit_branch, args.push_commits)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        log('Auto-repair daemon stopped by user')


if __name__ == '__main__':
    main()
