#!/usr/bin/env python3
"""Annotate registered z3 candidate artifacts with conjugacy data.

Finds the latest checks/PART_CVII_z3_conjugacy_*.json (or a specified file) and updates
committed_artifacts/PART_CVII_z3_candidate_*.json to include
  - "centralizer_size"
  - "conj_class_size"

Usage: python scripts/annotate_z3_candidates_with_conjugacy.py [--commit]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict

# safe json dump
try:
    from utils.json_safe import dump_json
except Exception:
    import sys as _sys
    from pathlib import Path as _Path

    _sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
    from utils.json_safe import dump_json


def find_latest_conjugacy(checks_dir: Path) -> Path | None:
    files = sorted(
        glob.glob(str(checks_dir / "PART_CVII_z3_conjugacy_*.json")),
        key=os.path.getmtime,
    )
    return Path(files[-1]) if files else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--conjugacy-file",
        help="Path to PART_CVII_z3_conjugacy_*.json (default: latest in checks)",
    )
    parser.add_argument(
        "--artifacts-dir",
        default="committed_artifacts",
        help="Directory containing candidate artifact JSONs",
    )
    parser.add_argument("--commit", action="store_true", help="Commit changes to git")
    args = parser.parse_args()

    checks = Path("checks")
    conj_path = (
        Path(args.conjugacy_file)
        if args.conjugacy_file
        else find_latest_conjugacy(checks)
    )
    if not conj_path or not conj_path.exists():
        raise FileNotFoundError(
            "No conjugacy file found in checks/; run w33_z3_conjugacy_classes.py first"
        )

    conj = json.loads(conj_path.read_text(encoding="utf-8"))
    index_map: Dict[int, Dict[str, Any]] = {}
    for r in conj.get("results", []):
        idx = int(r["index"])
        index_map[idx] = {
            "centralizer_size": r.get("centralizer_size"),
            "conj_class_size": r.get("conj_class_size"),
        }

    art_dir = Path(args.artifacts_dir)
    json_files = sorted(
        glob.glob(str(art_dir / "PART_CVII_z3_candidate_*.json")), key=os.path.getmtime
    )
    if not json_files:
        print(
            "No candidate metadata JSONs found in committed_artifacts/; nothing to do"
        )
        return

    modified = []
    for jf in json_files:
        p = Path(jf)
        data = json.loads(p.read_text(encoding="utf-8"))
        idx = data.get("index")
        if not idx:
            continue
        conj_info = index_map.get(int(idx))
        if not conj_info:
            print(f"No conjugacy info for index {idx}; skipping {p.name}")
            continue
        changed = False
        for k, v in conj_info.items():
            if data.get(k) != v:
                data[k] = v
                changed = True
        if changed:
            dump_json(data, p, indent=2)
            modified.append(str(p))
            print(f"Annotated {p.name} with conjugacy info: {conj_info}")

    if not modified:
        print("No files required annotation; done")
        return

    if args.commit:
        # Stage and commit modified files
        add_proc = subprocess.run(
            ["git", "add"] + modified,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if add_proc.returncode != 0:
            print("git add failed:", add_proc.stderr)
            return
        commit_msg = "Annotate z3 candidate artifacts with conjugacy info"
        cp = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if cp.returncode != 0:
            print("git commit failed:", cp.stderr)
            print(
                "If pre-commit hooks modified files, re-run this script to commit changes after staging."
            )
            return
        print("Committed annotation changes:", cp.stdout)
    else:
        print("Dry run complete. Use --commit to stage + commit annotated files.")


if __name__ == "__main__":
    main()
