#!/usr/bin/env python3
"""Select next N INFEASIBLE candidate pairs from existing seed files and write a temporary feasibility JSON for verification.

Usage: py -3 scripts/select_next_candidates.py --out checks/_tmp_verify_next20_48_49.json --n 20
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--out", type=str, required=True)
parser.add_argument("--n", type=int, default=20)
parser.add_argument("--forbid-json", type=str, default="checks/PART_CVII_forbids.json")
parser.add_argument(
    "--feasibility",
    type=str,
    default=None,
    help="Glob or file path for local_hotspot_feasibility json outputs (optional)",
)
args = parser.parse_args()

forb_sets = []
if os.path.exists(args.forbid_json):
    try:
        forb = json.load(open(args.forbid_json, encoding="utf-8")).get(
            "obstruction_sets", []
        )
        forb_sets = [tuple(sorted(entry.get("set", []))) for entry in forb]
    except Exception:
        forb_sets = []

# gather candidate entries either from feasibility outputs or from existing seed files
candidate_entries = []
if args.feasibility:
    files = (
        sorted(glob.glob(args.feasibility))
        if ("*" in args.feasibility or "?" in args.feasibility)
        else [args.feasibility]
    )
    for f in files:
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        tests = j.get("tests", [])
        for t in tests:
            if t.get("status") == "INFEASIBLE" and t.get("pair"):
                p = t["pair"]
                if len(p) == 4:
                    candidate_entries.append(
                        {
                            "src": f,
                            "pair": [int(p[0]), int(p[1]), int(p[2]), int(p[3])],
                            "status": "INFEASIBLE",
                        }
                    )
else:
    seed_files = sorted(
        glob.glob("checks/_tmp_seed_pair_verify_*.json"),
        key=lambda p: os.path.getmtime(p),
    )
    for sf in seed_files:
        try:
            j = json.load(open(sf, encoding="utf-8"))
        except Exception:
            continue
        se = j.get("seed_edges", [])
        if len(se) != 2:
            continue
        e1 = int(se[0]["edge_index"])
        r1 = int(se[0]["root_index"])
        e2 = int(se[1]["edge_index"])
        r2 = int(se[1]["root_index"])
        candidate_entries.append(
            {"src": sf, "pair": [e1, r1, e2, r2], "status": "INFEASIBLE"}
        )

selected = []
seen_pairs = set()
for entry in candidate_entries:
    pair = entry["pair"]
    e1 = int(pair[0])
    e2 = int(pair[2])
    s = tuple(sorted((e1, e2)))
    if s in forb_sets:
        continue
    tpair = tuple(pair)
    if tpair in seen_pairs:
        continue
    selected.append({"pair": pair, "status": entry.get("status", "INFEASIBLE")})
    seen_pairs.add(tpair)
    if len(selected) >= args.n:
        break

if not selected:
    print("No candidates selected")
    raise SystemExit(0)

out = {
    "edges": [selected[0]["pair"][0], selected[0]["pair"][2]],
    "k": 40,
    "radius": 1,
    "time_limit": 30,
    "tests": selected,
}

open(args.out, "w", encoding="utf-8").write(json.dumps(out, indent=2))
print("Wrote", args.out, "selected", len(selected))
