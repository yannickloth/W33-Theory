#!/usr/bin/env python3
"""Wrapper to prepare analysis/w33_bundle_temp and write analysis artifacts.

Runs, in order:
 - tools/export_w33_heisenberg_bundle.py
 - tools/build_qutrit_clifford_lift.py
 - tools/compare_sp23_clifford_and_bargmann.py
 - tools/build_agl23_permutation_lifts.py
 - tools/phase_correct_mubs.py

Usage:
  python tools/prepare_w33_analysis_bundle.py --bundle-dir artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1 --out-dir analysis/w33_bundle_temp --v0 0

Options:
  --dry-run    : Print steps without executing them
  --verbose    : Print command stdout/stderr as they run
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd, verbose=False):
    print("Running:", " ".join(str(x) for x in cmd))
    if args.dry_run:
        return 0
    result = subprocess.run(
        [str(x) for x in cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if verbose:
        print("--- stdout ---")
        print(result.stdout)
        print("--- stderr ---")
        print(result.stderr)
    if result.returncode != 0:
        print(f"Command failed (exit {result.returncode}): {' '.join(cmd)}")
        print(result.stdout)
        print(result.stderr)
        raise SystemExit(result.returncode)
    return result.returncode


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--bundle-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--v0", type=int, default=0)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    bundle_dir = args.bundle_dir
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir = out_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    steps = [
        (
            [
                sys.executable,
                "tools/export_w33_heisenberg_bundle.py",
                "--out-dir",
                str(out_dir),
                "--v0",
                str(args.v0),
            ],
            "Export H27/N12/MUB CSVs",
        ),
        (
            [
                sys.executable,
                "tools/build_qutrit_clifford_lift.py",
                "--bundle-dir",
                str(bundle_dir),
                "--out-dir",
                str(analysis_dir),
            ],
            "Build qutrit clifford lift",
        ),
        (
            [
                sys.executable,
                "tools/compare_sp23_clifford_and_bargmann.py",
                "--bundle-dir",
                str(bundle_dir),
                "--out-dir",
                str(analysis_dir),
                "--mub-csv",
                str(bundle_dir / "qutrit_MUB_state_vectors_for_N12_vertices.csv"),
            ],
            "Compute sp23 action and raw parallelogram comparison",
        ),
        (
            [
                sys.executable,
                "tools/build_agl23_permutation_lifts.py",
                "--bundle-dir",
                str(out_dir),
                "--out-dir",
                str(analysis_dir),
            ],
            "Build AGL23 lifts",
        ),
        (
            [
                sys.executable,
                "tools/phase_correct_mubs.py",
                "--bundle-dir",
                str(bundle_dir),
                "--out-dir",
                str(analysis_dir),
                "--write-holonomy-gauge",
            ],
            "Phase-correct MUBs and recompute parallelogram comparison",
        ),
    ]

    for cmd, desc in steps:
        print(f"\n=== Step: {desc} ===")
        run(cmd, verbose=args.verbose)

    # Sanity checks
    expected = [
        analysis_dir / "clifford_lift_on_H27_and_N12.json",
        analysis_dir / "W33_Heisenberg_generators_Tx_Ty_Z.json",
        analysis_dir / "AGL23_lifts.json",
        analysis_dir / "parallelogram_holonomy_vs_bargmann.json",
        analysis_dir / "qutrit_MUB_state_vectors_for_N12_vertices_phase_corrected.csv",
    ]
    missing = [p for p in expected if not p.exists()]
    if missing:
        print("Missing expected outputs:")
        for m in missing:
            print(" -", m)
        raise SystemExit(2)

    print("All expected analysis bundle outputs present in:", analysis_dir)
    print("Done.")
