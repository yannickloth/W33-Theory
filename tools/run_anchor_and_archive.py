#!/usr/bin/env python3
"""Wrapper: run `anchor_core_and_maximize_cpsat.py` with a given forbid, then archive results.

Usage: python tools/run_anchor_and_archive.py --forbid 0-18-25 --time 300

It will:
 - run tools/anchor_core_and_maximize_cpsat.py with the provided forbid and time
 - copy artifacts/anchor_core_cpsat_summary.json to artifacts/anchor_core_cpsat_summary_forbid_<forbid>.json
 - write reports/anchor_forbid_<forbid>.md and .json summarizing per-W status
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
REPORTS = ROOT / "reports"

parser = argparse.ArgumentParser()
parser.add_argument("--forbid", type=str, required=True)
parser.add_argument("--time", type=int, default=300)
parser.add_argument("--w-list", type=str, default="0,4,5,6,7,8,9,10,11,12,13,14,15")
parser.add_argument("--workers", type=int, default=4)
args = parser.parse_args()

forbid = args.forbid
# run anchored script
cmd = [
    "python",
    str(ROOT / "tools" / "anchor_core_and_maximize_cpsat.py"),
    "--forbid",
    forbid,
    "--time",
    str(args.time),
    "--w-list",
    args.w_list,
    "--workers",
    str(args.workers),
]
print("Running:", " ".join(cmd))
proc = subprocess.run(cmd)
if proc.returncode != 0:
    print("Anchor run failed with returncode", proc.returncode)

# archive summary
src = ART / "anchor_core_cpsat_summary.json"
dst = ART / f"anchor_core_cpsat_summary_forbid_{forbid.replace(',','_')}.json"
shutil.copyfile(src, dst)
print("Copied summary to", dst)

# read summary and write reports
data = json.loads(src.read_text(encoding="utf-8"))
REPORTS.mkdir(parents=True, exist_ok=True)
md = REPORTS / f"anchor_forbid_{forbid.replace(',','_')}.md"
js = REPORTS / f"anchor_forbid_{forbid.replace(',','_')}.json"
lines = [f"# Anchor CP-SAT summary (forbid: {forbid})", ""]
for e in data:
    lines.append(
        f"- W={e.get('W_idx')}: status={e.get('status')}, matched={e.get('matched')}"
    )
md.write_text("\n".join(lines), encoding="utf-8")
js.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("Wrote reports:", md, js)
