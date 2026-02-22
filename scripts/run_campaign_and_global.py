#!/usr/bin/env python3
"""Run an adaptive local-patch campaign, then run a global CP‑SAT solve using the final seed.

Usage:
  python scripts/run_campaign_and_global.py  --bij <bij.json> --campaign-iter 6 --campaign-edge-sizes 24,48 --campaign-time 60 --campaign-k 40 --campaign-seed 212 --campaign-seed-reward 10000 --cp-k 40 --cp-time 600 --cp-seed 212 --cp-seed-reward 20000 --auto-commit --check-collaborator

The script runs the campaign (blocking), finds the latest campaign seed, and launches the CP‑SAT solve with that seed.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import time
from pathlib import Path


def find_latest_seed(
    pattern="checks/PART_CVII_e8_bijection_seed_campaign_*.json",
) -> Path | None:
    files = glob.glob(pattern)
    if not files:
        return None
    files = sorted(files, key=os.path.getmtime, reverse=True)
    return Path(files[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bij", default="checks/PART_CVII_e8_bijection.json")
    parser.add_argument("--campaign-iter", type=int, default=6)
    parser.add_argument("--campaign-edge-sizes", type=str, default="24,48")
    parser.add_argument("--campaign-k", type=int, default=40)
    parser.add_argument("--campaign-time", type=float, default=60.0)
    parser.add_argument("--campaign-seed", type=int, default=212)
    parser.add_argument("--campaign-seed-reward", type=float, default=10000.0)

    parser.add_argument("--cp-k", type=int, default=40)
    parser.add_argument("--cp-time", type=float, default=600.0)
    parser.add_argument("--cp-seed", type=int, default=212)
    parser.add_argument("--cp-seed-reward", type=float, default=20000.0)

    parser.add_argument("--auto-commit", action="store_true")
    parser.add_argument("--commit-branch", type=str, default=None)
    parser.add_argument("--push-commits", action="store_true")
    parser.add_argument("--check-collaborator", action="store_true")

    args = parser.parse_args()

    # Run campaign
    cmd = [
        "py",
        "-3",
        "-X",
        "utf8",
        "-u",
        "scripts/run_local_patch_campaign.py",
        "--bij",
        args.bij,
        "--edge-sizes",
        args.campaign_edge_sizes,
        "--k",
        str(args.campaign_k),
        "--time-limit",
        str(args.campaign_time),
        "--seed",
        str(args.campaign_seed),
        "--seed-reward",
        str(args.campaign_seed_reward),
        "--max-iter",
        str(args.campaign_iter),
    ]
    if args.auto_commit:
        cmd += ["--auto-commit"]
    if args.commit_branch:
        cmd += ["--commit-branch", args.commit_branch]
    if args.push_commits:
        cmd += ["--push-commits"]
    if args.check_collaborator:
        cmd += ["--check-collaborator"]

    print("Running local patch campaign:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    # find latest seed and run CP-SAT
    latest_seed = find_latest_seed()
    if not latest_seed:
        print("No campaign seed found, aborting global CP-SAT run")
        return

    print("Found seed:", latest_seed)

    cp_cmd = [
        "py",
        "-3",
        "-X",
        "utf8",
        "scripts/solve_e8_embedding_cpsat.py",
        "--seed-json",
        str(latest_seed),
        "--k",
        str(args.cp_k),
        "--time-limit",
        str(args.cp_time),
        "--seed",
        str(args.cp_seed),
        "--seed-reward",
        str(args.cp_seed_reward),
        "--log",
    ]
    print("Running global CP-SAT:", " ".join(cp_cmd))
    subprocess.run(cp_cmd, check=True)

    # optionally, mirror the solver result into committed_artifacts and commit it
    res_path = Path.cwd() / "checks" / "PART_CVII_e8_embedding_cpsat.json"
    if res_path.exists() and args.auto_commit:
        artifact = Path.cwd() / "committed_artifacts" / res_path.name
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(res_path.read_text(encoding="utf-8"), encoding="utf-8")
        try:
            from scripts import git_auto_keep

            ok, msg = git_auto_keep.git_add_commit(
                [str(artifact)],
                f"Global CP-SAT result: {artifact.name}",
                branch=args.commit_branch,
                push=args.push_commits,
            )
            print("Global CP-SAT auto-commit:", ok, msg)
        except Exception as e:
            print("Failed to auto-commit CP-SAT result:", e)


if __name__ == "__main__":
    main()
