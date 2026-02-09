#!/usr/bin/env python3
"""Run dd_shrink_conflict.py sequentially for a set of targeted seeds.

Usage:
  python scripts/run_targeted_dd_shrink.py --seeds 212 213 214 --time-limit 10 --max-checks 200

If --seeds is omitted, the script scans checks/dd_targeted_50_51_seed*.json and
runs for all seeds whose status == 'INFEASIBLE'.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import time
from pathlib import Path

CHECKS = Path.cwd() / "checks"
LOG_DIR = CHECKS

parser = argparse.ArgumentParser()
parser.add_argument(
    "--seeds", type=int, nargs="*", help="Explicit list of numerical seeds to run"
)
parser.add_argument(
    "--start", type=int, default=None, help="Start seed (inclusive) if --seeds omitted"
)
parser.add_argument(
    "--end", type=int, default=None, help="End seed (inclusive) if --seeds omitted"
)
parser.add_argument(
    "--time-limit", type=int, default=10, help="Time limit passed to solver"
)
parser.add_argument("--max-checks", type=int, default=200, help="Max ddmin checks")
parser.add_argument("--workers", type=int, default=2, help="Workers to pass to solver")
parser.add_argument("--reps", type=int, default=1, help="Reps per subset test")
parser.add_argument(
    "--repro-threshold", type=float, default=1.0, help="Repro threshold"
)
args = parser.parse_args()

# Determine seeds to run
seeds = []
if args.seeds and len(args.seeds) > 0:
    seeds = list(dict.fromkeys(args.seeds))
else:
    # scan targeted files
    files = sorted(glob.glob(str(CHECKS / "dd_targeted_50_51_seed*.json")))
    for f in files:
        try:
            j = json.load(open(f, "r", encoding="utf-8"))
        except Exception:
            continue
        # extract seed from filename if possible
        m = re.search(r"seed(\d+)_", os.path.basename(f))
        seed_num = int(m.group(1)) if m else j.get("seed")
        if seed_num is None:
            continue
        if args.start is not None and seed_num < args.start:
            continue
        if args.end is not None and seed_num > args.end:
            continue
        if j.get("status") == "INFEASIBLE":
            seeds.append(int(seed_num))

# remove duplicates and sort
seeds = sorted(set(seeds))
if not seeds:
    print(
        "No targeted INFEASIBLE seeds found in checks or no seeds specified; exiting."
    )
    raise SystemExit(0)

print(f"Will run dd_shrink_conflict for seeds: {seeds}")

stamp = int(time.time())
logp = LOG_DIR / f"PART_CVII_dd_shrink_targeted_run_{stamp}.log"
with open(logp, "w", encoding="utf-8") as logf:
    logf.write(f"Run started at {time.time()}\n")

    for seed in seeds:
        print(f"=== Running dd_shrink for seed {seed} ===")
        logf.write(f"\n=== seed {seed} START {time.time()} ===\n")
        cmd = [
            "py",
            "-3",
            "scripts/dd_shrink_conflict.py",
            "--bij",
            "committed_artifacts/PART_CVII_e8_bijection_intermediate_1770491863.json",
            "--conf",
            "committed_artifacts/PART_CVII_infeasible_block_analysis_quick_merged_1770498926.json",
            "--index",
            "0",
            "--seed",
            str(seed),
            "--k",
            "40",
            "--time-limit",
            str(args.time_limit),
            "--max-checks",
            str(args.max_checks),
            "--reps",
            str(args.reps),
            "--workers",
            str(args.workers),
            "--repro-threshold",
            str(args.repro_threshold),
        ]
        print("CMD:", " ".join(cmd))
        try:
            proc = subprocess.run(
                cmd,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=max(30, args.time_limit + 30),
            )
            print(proc.stdout)
            if proc.stderr:
                print("ERR:", proc.stderr)
            logf.write("STDOUT:\n" + proc.stdout + "\n")
            logf.write("STDERR:\n" + proc.stderr + "\n")
        except subprocess.TimeoutExpired as e:
            print(f"Seed {seed}: dd_shrink execution timed out")
            logf.write(f"Seed {seed}: dd_shrink execution timed out\n")
        except Exception as e:
            print(f"Seed {seed}: dd_shrink execution failed: {e}")
            logf.write(f"Seed {seed}: dd_shrink execution failed: {e}\n")
        logf.write(f"=== seed {seed} END {time.time()} ===\n")

print("All seeds processed. Log:", logp)
