#!/usr/bin/env python3
"""Extended targeted dd_shrink sweep for pair (50,51).
Runs dd_shrink_conflict.py multiple times with the same --seed-json and varying numeric --seed to try to produce a shrink certificate.
Writes a summary to checks/dd_repro_targeted_50_51_summary_<ts>.json and preserves CPSAT JSONs.
"""
import glob
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

# Parameters
BIJ = "committed_artifacts/PART_CVII_e8_bijection_intermediate_1770491863.json"
SEED_JSON = "committed_artifacts/PART_CVII_dd_seed_initial_1770586555.json"
CONF = "checks/PART_CVII_dd_shrink_input_pair_1770577580.json"
SEEDS = list(range(212, 237))  # 212..236 inclusive
TIME_LIMIT = 300
MAX_CHECKS = 5000
K = 40
OUT_SUM = Path("checks") / f"dd_repro_targeted_50_51_summary_{int(time.time())}.json"
summary = []

for seed in SEEDS:
    stamp = int(time.time())
    cmd = [
        "py",
        "-3",
        "-X",
        "utf8",
        "scripts/dd_shrink_conflict.py",
        "--bij",
        BIJ,
        "--conf",
        CONF,
        "--index",
        "0",
        "--max-checks",
        str(MAX_CHECKS),
        "--k",
        str(K),
        "--time-limit",
        str(TIME_LIMIT),
        "--seed",
        str(seed),
        "--seed-json",
        SEED_JSON,
        "--workers",
        "1",
        "--reps",
        "5",
        "--repro-threshold",
        "1.0",
    ]
    print("\n=== Running:", " ".join(cmd))
    start = time.time()
    proc = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    end = time.time()
    print(proc.stdout)
    if proc.stderr:
        print("STDERR:\n", proc.stderr)

    # find most recent dd_shrink_result created in checks (timestamp after start)
    results = sorted(glob.glob("checks/PART_CVII_dd_shrink_result_*.json"))
    latest = None
    for r in reversed(results):
        try:
            j = json.loads(open(r, encoding="utf-8").read())
        except Exception:
            continue
        if j.get("timestamp", 0) >= int(start - 2):
            latest = r
            break

    cpsat = Path("checks") / "PART_CVII_e8_embedding_cpsat.json"
    cpsat_copy = None
    if cpsat.exists():
        cpsat_copy = Path("checks") / f"dd_targeted_50_51_seed{seed}_{stamp}_cpsat.json"
        shutil.copyfile(str(cpsat), str(cpsat_copy))

    rec = {
        "seed": seed,
        "dd_shrink_result": latest,
        "cpsat_json": str(cpsat_copy) if cpsat_copy else None,
        "stdout": proc.stdout[:4000],
        "stderr": proc.stderr[:4000],
        "elapsed_seconds": end - start,
        "timestamp": stamp,
    }

    if latest:
        try:
            rj = json.loads(open(latest, encoding="utf-8").read())
            rec["initial_reproducible"] = rj.get("initial_reproducible")
            rec["shrink_status"] = rj.get("shrink_status")
            rec["result_size"] = rj.get("result_size")
            rec["result"] = rj.get("result")
        except Exception:
            pass

    summary.append(rec)
    # small delay to avoid race conditions
    time.sleep(1)

OUT_SUM.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("Wrote summary to", OUT_SUM)
print("Done")
