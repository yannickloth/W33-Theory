#!/usr/bin/env python3
"""Commit a trial artifact (bijection) to committed_artifacts and push to auto-keep branch.

Usage: py -3 scripts/commit_trial_best.py checks/PART_CVII_e8_bijection_trial_20260207T201739Z_s804.json
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

spec_ga = importlib.util.spec_from_file_location(
    "git_auto_keep", "scripts/git_auto_keep.py"
)
git_auto_keep = importlib.util.module_from_spec(spec_ga)
spec_ga.loader.exec_module(git_auto_keep)


def main():
    if len(sys.argv) < 2:
        print("Usage: commit_trial_best.py <trial_json>")
        sys.exit(2)
    infile = Path(sys.argv[1])
    if not infile.exists():
        print("File not found:", infile)
        sys.exit(1)
    j = json.loads(infile.read_text(encoding="utf-8"))
    trial = j.get("trial", {})
    outname = Path("committed_artifacts") / ("committed_" + infile.stem + ".json")
    artifact = {
        "trial": trial,
        "bijection": j.get("bijection"),
        "verification": trial.get("verification"),
    }
    outname.parent.mkdir(parents=True, exist_ok=True)
    outname.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print("Wrote", outname)
    ok, msg = git_auto_keep.git_add_commit(
        [str(outname)],
        f'Add trial artifact: {infile.name} best_exact={trial.get("best_exact")}',
        branch="auto-keep",
        push=True,
    )
    print("git_auto_keep:", ok, msg)


if __name__ == "__main__":
    main()
