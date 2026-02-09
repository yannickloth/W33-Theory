#!/usr/bin/env python3
"""Watch for new PART_CVII_dd_shrink_result_*.json files and auto-run:
  - scripts/register_dd_obstructions.py
  - scripts/clean_forbids.py
  - scripts/solve_e8_embedding_cpsat.py (with updated forbids)

Writes a simple log to checks/PART_CVII_dd_watch_log.txt and a state file checks/_watch_state.json
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Set, Tuple

BASE = Path.cwd()
CHECKS = BASE / "checks"
LOG = CHECKS / "PART_CVII_dd_watch_log.txt"
STATE = CHECKS / "_watch_state.json"

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--no-push",
    action="store_true",
    help="Disable pushing to origin after register commits",
)
parser.add_argument(
    "--verify-seed",
    type=int,
    default=212,
    help="Verification seed to use for register and solver runs",
)
args = parser.parse_args()

POLL_INTERVAL = int(os.environ.get("DD_WATCH_INTERVAL", "20"))
REGISTER_CMD = [
    "py",
    "-3",
    "scripts/register_dd_obstructions.py",
    "--k",
    "40",
    "--time-limit",
    "30",
    "--verify-seed",
    str(args.verify_seed),
    "--commit",
]
if not args.no_push:
    REGISTER_CMD.append("--push")
CLEAN_CMD = ["py", "-3", "scripts/clean_forbids.py"]
SOLVE_CMD = [
    "py",
    "-3",
    "scripts/solve_e8_embedding_cpsat.py",
    "--k",
    "40",
    "--time-limit",
    "30",
    "--forbid-json",
    str(CHECKS / "PART_CVII_forbids.json"),
    "--seed",
    str(args.verify_seed),
]


def log(msg: str):
    ts = time.time()
    line = f"{ts}: {msg}\n"
    print(line, end="")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line)


def load_state() -> Set[Tuple[int, ...]]:
    if not STATE.exists():
        return set()
    j = json.loads(STATE.read_text(encoding="utf-8"))
    pr = set()
    for k in j.get("processed", []):
        pr.add(tuple(k))
    return pr


def save_state(processed: Set[Tuple[int, ...]]):
    j = {"processed": [list(t) for t in sorted(processed)]}
    STATE.write_text(json.dumps(j, indent=2), encoding="utf-8")


def collect_results() -> Set[Tuple[int, ...]]:
    outs = glob.glob(str(CHECKS / "PART_CVII_dd_shrink_result_*.json"))
    s = set()
    for p in outs:
        try:
            j = json.loads(open(p, encoding="utf-8").read())
            r = j.get("result", []) or []
            if r:
                s.add(tuple(sorted(int(x) for x in r)))
        except Exception as e:
            log(f"Error reading {p}: {e}")
    return s


def run_cmd(cmd, timeout=120):
    log(f"Running: {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        log(
            f"Exit {proc.returncode} stdout(len)={len(proc.stdout)} stderr(len)={len(proc.stderr)}"
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        log(f"Timeout while running: {' '.join(cmd)}")
        return -1, "", ""


def check_claude_files():
    try:
        st = subprocess.run(
            ["git", "status", "--porcelain"], stdout=subprocess.PIPE, text=True
        ).stdout
        for f in ("README.md", "memory.md"):
            if any(line.endswith(f) or f in line for line in st.splitlines()):
                log(
                    f"WARNING: Detected changes to {f} in working tree; avoid pushing without review."
                )
    except Exception as e:
        log(f"Failed to check CLAUDE files: {e}")


def main():
    log("Watcher starting")
    processed = load_state()
    check_claude_files()

    # Initialize processed with existing verified sets (to avoid reprocessing old entries)
    try:
        pair_files = glob.glob(str(CHECKS / "PART_CVII_dd_pair_obstruction_*.json"))
        for p in pair_files:
            j = json.loads(open(p, encoding="utf-8").read())
            s = tuple(sorted(int(x) for x in j.get("set", []) or []))
            if s:
                processed.add(s)
    except Exception as e:
        log(f"Error pre-seeding processed sets: {e}")

    save_state(processed)

    try:
        while True:
            all_results = collect_results()
            new = [r for r in sorted(all_results) if r not in processed]
            if new:
                log(f"Found {len(new)} new unique result(s): {new}")
                # validate dd_shrink JSONs and quarantine malformed files before running register
                import shutil

                bad = []
                for p in glob.glob(str(CHECKS / "PART_CVII_dd_shrink_result_*.json")):
                    try:
                        json.load(open(p, "r", encoding="utf-8"))
                    except Exception as e:
                        bad.append((p, str(e)))
                if bad:
                    for p, e in bad:
                        target_dir = CHECKS / "archive"
                        target_dir.mkdir(parents=True, exist_ok=True)
                        target = target_dir / Path(p).name
                        log(
                            f"Quarantining malformed dd_shrink_result: {p} -> {target}: {e}"
                        )
                        try:
                            shutil.move(p, target)
                        except Exception as ee:
                            log(f"Failed to move {p} to archive: {ee}")
                    log(
                        "Found malformed dd_shrink_result files; they were quarantined. Will retry register on next poll."
                    )
                else:
                    # Run register (it groups by result) - faster than per-result invocations
                    rc, out, err = run_cmd(REGISTER_CMD, timeout=600)
                    if rc == 0:
                        # Clean forbids & re-run global solver
                        run_cmd(CLEAN_CMD, timeout=30)
                        rc2, out2, err2 = run_cmd(SOLVE_CMD, timeout=120)
                        # inspect solve output JSON
                        try:
                            sol = json.loads(
                                open(
                                    CHECKS / "PART_CVII_e8_embedding_cpsat.json",
                                    encoding="utf-8",
                                ).read()
                            )
                            log(
                                f"Global solver status after register: {sol.get('status')} time={sol.get('time_seconds')}"
                            )
                        except Exception as e:
                            log(f"Could not read solver JSON: {e}")
                    else:
                        log(f"Register script returned {rc}. Will retry on next poll.")
                # Update processed sets to include any we've just now processed (collect again)
                processed = load_state()  # reload
                all_results = collect_results()
                for r in all_results:
                    if r not in processed:
                        # conservative approach: mark everything considered
                        processed.add(r)
                save_state(processed)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        log("Watcher interrupted by user")
    except Exception as e:
        log(f"Watcher exception: {e}")


if __name__ == "__main__":
    main()
