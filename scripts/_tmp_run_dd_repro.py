#!/usr/bin/env python3
"""Run dd_shrink_conflict.py for a list of seeds and preserve cpsat JSON outputs for analysis.
Usage: python scripts/_tmp_run_dd_repro.py <bij-path> [seed1 seed2 ...]
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python scripts/_tmp_run_dd_repro.py <bij-path> [seed1 seed2 ...]")
    raise SystemExit(2)

bij = sys.argv[1]
seeds = (
    [int(s) for s in sys.argv[2:]] if len(sys.argv) > 2 else [212, 213, 214, 215, 216]
)
bij_label = Path(bij).stem
for seed in seeds:
    stamp = int(time.time())
    cmd = [
        "py",
        "-3",
        "-X",
        "utf8",
        "scripts/dd_shrink_conflict.py",
        "--bij",
        bij,
        "--conf",
        "checks/PART_CVII_dd_shrink_input_pair_1770577580.json",
        "--index",
        "0",
        "--max-checks",
        "2000",
        "--k",
        "40",
        "--time-limit",
        "120",
        "--seed",
        str(seed),
    ]
    print("\n=== Running:", " ".join(cmd))
    proc = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    print(proc.stdout)
    if proc.stderr:
        print("STDERR:\n", proc.stderr)
    # preserve cpsat JSON if exists
    cpsat = Path("checks") / "PART_CVII_e8_embedding_cpsat.json"
    if cpsat.exists():
        dest = (
            Path("checks")
            / f"dd_repro_pair_1770577580_{bij_label}_seed{seed}_{stamp}_cpsat.json"
        )
        shutil.copyfile(str(cpsat), str(dest))
        print("Copied cpsat json to", dest)
    else:
        print("No cpsat json found")

    # short sleep to avoid race conditions
    time.sleep(1)

print("\nAll runs completed for", bij)
