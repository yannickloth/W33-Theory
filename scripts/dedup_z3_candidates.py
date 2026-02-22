#!/usr/bin/env python3
"""Deduplicate z3 candidates by conjugacy group and annotate committed artifacts.

This script groups candidates by (centralizer_size, conj_class_size) from the
latest checks/PART_CVII_z3_conjugacy_*.json and marks a representative for each
group (lowest R3_norm). It updates the JSON metadata in committed_artifacts to
include: "conj_group": <id>, "conj_group_rep": true/false, "conj_group_size": n

Usage: python scripts/dedup_z3_candidates.py --commit
"""
from __future__ import annotations

import glob
import json
import subprocess
from pathlib import Path

try:
    from utils.json_safe import dump_json
except Exception:
    import sys as _sys
    from pathlib import Path as _Path

    _sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
    from utils.json_safe import dump_json


def find_latest_conjugacy():
    files = sorted(
        glob.glob("checks/PART_CVII_z3_conjugacy_*.json"),
        key=lambda p: Path(p).stat().st_mtime,
    )
    return Path(files[-1]) if files else None


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--conjugacy-file", help="Optional conjugacy file path")
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()

    conj_file = (
        Path(args.conjugacy_file) if args.conjugacy_file else find_latest_conjugacy()
    )
    if not conj_file or not conj_file.exists():
        raise FileNotFoundError(
            "No conjugacy file found; run w33_z3_conjugacy_classes.py first"
        )

    conj = json.loads(open(conj_file, encoding="utf-8").read())
    groups = {}
    for r in conj.get("results", []):
        idx = int(r["index"])
        key = (r.get("centralizer_size"), r.get("conj_class_size"))
        groups.setdefault(key, []).append(idx)

    # For each group pick rep as candidate with lowest R3_norm
    reps = {}
    for gid, (key, idxs) in enumerate(groups.items(), start=1):
        best = None
        best_r3 = None
        for idx in idxs:
            # find committed artifact with index
            matches = glob.glob(
                f"committed_artifacts/PART_CVII_z3_candidate_*_{idx:02d}.json"
            )
            if matches:
                # choose the most recent one
                path = sorted(matches, key=lambda p: Path(p).stat().st_mtime)[-1]
                data = json.loads(open(path, encoding="utf-8").read())
                r3 = data.get("R3_norm", float("inf"))
                if best is None or r3 < best_r3:
                    best = path
                    best_r3 = r3
        reps[gid] = {
            "group_key": key,
            "indices": idxs,
            "rep": best and Path(best).name,
        }

    # annotate artifacts
    modified = []
    for gid, info in reps.items():
        for idx in info["indices"]:
            matches = glob.glob(
                f"committed_artifacts/PART_CVII_z3_candidate_*_{idx:02d}.json"
            )
            if not matches:
                continue
            path = sorted(matches, key=lambda p: Path(p).stat().st_mtime)[-1]
            data = json.loads(open(path, encoding="utf-8").read())
            changed = False
            if data.get("conj_group") != gid:
                data["conj_group"] = gid
                changed = True
            if data.get("conj_group_size") != len(info["indices"]):
                data["conj_group_size"] = len(info["indices"])
                changed = True
            is_rep = Path(path).name == info.get("rep")
            if data.get("conj_group_rep") != is_rep:
                data["conj_group_rep"] = is_rep
                changed = True
            if changed:
                dump_json(data, Path(path), indent=2)
                modified.append(str(path))
                print(f"Annotated {path} -> group {gid} rep={is_rep}")

    if args.commit and modified:
        subprocess.run(["git", "add"] + modified)
        cp = subprocess.run(
            ["git", "commit", "-m", "Annotate z3 candidates with conjugacy group ids"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if cp.returncode != 0:
            print("git commit failed:", cp.stderr)
        else:
            print("Committed conjugacy group annotations")
    else:
        print("Done. Use --commit to stage and commit changes.")


if __name__ == "__main__":
    main()
