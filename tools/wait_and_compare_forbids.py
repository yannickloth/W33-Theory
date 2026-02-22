#!/usr/bin/env python3
"""Monitor anchored CP-SAT summary and, when the current sweep completes, run a comparison sweep forbidding alt triad.

Behavior:
 - Polls `artifacts/anchor_core_cpsat_summary.json` until all expected W indices are present.
 - Backups the existing summary to `artifacts/anchor_core_cpsat_summary_backup_{ts}.json`.
 - Runs `tools/anchor_core_and_maximize_cpsat.py` with the same W-list and params but with `--forbid` set to the comparison triad (defaults to '0-20-23').
 - After run completes, saves the comparison summary to `artifacts/anchor_core_cpsat_summary_forbid_{triad}.json` and writes a short `artifacts/anchor_compare_{triad}_report.json` summarizing per-W status.

Run with the same Python interpreter to ensure the same virtualenv is used.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--expected-w-list", type=str, default="0,4,5,6,7,8,9,10,11,12,13,14,15"
)
parser.add_argument("--poll-interval", type=int, default=30, help="seconds")
parser.add_argument("--compare-forbid", type=str, default="0-20-23")
parser.add_argument("--anchor-time", type=int, default=3600)
parser.add_argument("--anchor-workers", type=int, default=8)
parser.add_argument("--enforce-signs", action="store_true")
args = parser.parse_args()

expected_w = set(int(x) for x in args.expected_w_list.split(","))
summary_path = ART / "anchor_core_cpsat_summary.json"

print("Waiting for anchored sweep summary at", summary_path)
# wait loop
while True:
    if summary_path.exists():
        try:
            data = json.loads(summary_path.read_text(encoding="utf-8"))
            present_w = set(int(item["W_idx"]) for item in data if "W_idx" in item)
            print("Found", len(present_w), "W entries:", sorted(present_w))
            if expected_w.issubset(present_w):
                print("All expected W present; proceeding to comparison run.")
                break
        except Exception as e:
            print("Error reading summary:", e)
    else:
        print("No summary file yet; sleeping...")
    time.sleep(args.poll_interval)

# backup current summary
ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
backup = ART / f"anchor_core_cpsat_summary_backup_{ts}.json"
shutil.copy(summary_path, backup)
print("Backed up current summary to", backup)

# run comparison anchor script
cmd = [
    sys.executable,
    str(ROOT / "tools" / "anchor_core_and_maximize_cpsat.py"),
    "--w-list",
    args.expected_w_list,
    "--time",
    str(args.anchor_time),
    "--workers",
    str(args.anchor_workers),
    "--forbid",
    args.compare_forbid,
]
if args.enforce_signs:
    cmd.append("--enforce-signs")

print("Running comparison anchor script:", " ".join(cmd))
proc = subprocess.run(cmd, capture_output=True, text=True)
print("Comparison run exit code", proc.returncode)
print(proc.stdout)
print(proc.stderr)

# save comparison summary
comp_dest = (
    ART
    / f'anchor_core_cpsat_summary_forbid_{args.compare_forbid.replace("-","_")}.json'
)
if summary_path.exists():
    shutil.copy(summary_path, comp_dest)
    print("Saved comparison summary to", comp_dest)
else:
    print("No summary produced by comparison run")

# produce short report
report = {
    "compare_forbid": args.compare_forbid,
    "backup": str(backup),
    "comparison_summary": str(comp_dest),
    "exit_code": proc.returncode,
}
if comp_dest.exists():
    comp = json.loads(comp_dest.read_text(encoding="utf-8"))
    report["per_W"] = {
        str(item["W_idx"]): {
            "status": item.get("status"),
            "matched": item.get("matched"),
        }
        for item in comp
    }

report_path = ART / f'anchor_compare_{args.compare_forbid.replace("-","_")}_report.json'
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
print("Wrote report to", report_path)
print("Done.")
