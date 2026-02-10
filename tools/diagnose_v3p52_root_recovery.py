#!/usr/bin/env python3
"""Diagnose toe_root_operator_dictionary seed sensitivity for v3p52.

Runs toe_root_operator_dictionary for a set of seeds, recomputes the v3p52
backbone/coset map, and records mean rel_resid.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
V3P52 = (
    ART
    / "more_new_work_extracted"
    / "NewestWork2_2_2026_delta_v3p52"
    / "toe_coupling_strengths_v3.json"
)


def run_cmd(cmd):
    print("Running:", " ".join(cmd))
    proc = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    print(proc.stdout)
    if proc.stderr:
        print("STDERR:", proc.stderr)
    return proc.returncode


def measure_mean_rel(out_json_path: Path):
    j = json.loads(out_json_path.read_text(encoding="utf-8"))
    vals = [
        c.get("backbone_coset", {}).get("rel_resid")
        for c in j.get("couplings", [])
        if c.get("backbone_coset")
    ]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    p.add_argument(
        "--export-dir",
        type=str,
        default=None,
        help="Optional export-dir to pass to toe_root_operator_dictionary.py (use a bundle e6_basis_export)",
    )
    p.add_argument(
        "--restore", action="store_true", help="Restore original root dict after run"
    )
    args = p.parse_args()

    if not V3P52.exists():
        raise FileNotFoundError(V3P52)

    # backup existing root dict if present
    root_npy = ART / "toe_root_operator_dictionary.npy"
    backup = ART / "toe_root_operator_dictionary.npy.bak"
    if root_npy.exists():
        backup.write_bytes(root_npy.read_bytes())
        print("Backed up root dict to", backup)

    results = []
    for s in args.seeds:
        t0 = time.time()
        # build root dict with given seed
        cmd1 = [
            "py",
            "-3",
            "tools/toe_root_operator_dictionary.py",
            "--seed",
            str(int(s)),
            "--out-npy",
            str(root_npy),
        ]
        if args.export_dir:
            cmd1 += ["--export-dir", args.export_dir]
        rc = run_cmd(cmd1)
        if rc != 0:
            results.append({"seed": s, "error": "root dict build failed"})
            continue
        # compute decomposition
        out_json = ART / f"toe_backbone_coset_coupling_map_v3p52_exact_seed{s}.json"
        out_md = ART / f"toe_backbone_coset_coupling_map_v3p52_exact_seed{s}.md"
        cmd2 = [
            "py",
            "-3",
            "tools/toe_backbone_coset_coupling_map.py",
            "--in-json",
            str(V3P52),
            "--out-json",
            str(out_json),
            "--out-md",
            str(out_md),
        ]
        rc2 = run_cmd(cmd2)
        if rc2 != 0:
            results.append({"seed": s, "error": "decomposition failed"})
            continue
        # measure mean rel_resid
        mean_rel = measure_mean_rel(out_json)
        elapsed = time.time() - t0
        results.append(
            {
                "seed": s,
                "mean_rel_resid": mean_rel,
                "elapsed_s": elapsed,
                "out_json": str(out_json),
            }
        )
        print(f"Seed {s}: mean_rel_resid={mean_rel} (elapsed {elapsed:.1f}s)")

    # write results
    outp = ART / "toe_root_operator_diagnostics_v3p52.json"
    outp.write_text(json.dumps({"results": results}, indent=2), encoding="utf-8")
    print("Wrote", outp)

    if args.restore and backup.exists():
        root_npy.write_bytes(backup.read_bytes())
        print("Restored original root dict from", backup)


if __name__ == "__main__":
    main()
