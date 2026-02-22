#!/usr/bin/env python3
"""Run extract_e8_rootword_cocycle across all A2 solutions for the det1 orbit and summarize stats."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

A2_JSON = Path("artifacts/a2_4_decomposition.json")
CYCLES_JSON = Path("analysis/minimal_commutator_cycles/det1_orbit_cycles.json")
OUT_ROOT = Path("analysis/minimal_commutator_cycles")


def main():
    data = json.loads(A2_JSON.read_text(encoding="utf-8"))
    sol = data.get("a2_4_solution", [])
    summary = []
    for idx in range(len(sol)):
        outdir = OUT_ROOT / f"e8_det1_a2_{idx}"
        outdir.mkdir(parents=True, exist_ok=True)
        cmd = [
            "py",
            "-3",
            "tools/extract_e8_rootword_cocycle.py",
            "--cycles-json",
            str(CYCLES_JSON),
            "--a2-index",
            str(idx),
            "--out-dir",
            str(outdir),
        ]
        print("Running", " ".join(cmd))
        subprocess.run(cmd, check=True)
        jpath = outdir / "e8_rootword_cocycle.json"
        if not jpath.exists():
            print("Missing output for idx", idx)
            continue
        j = json.loads(jpath.read_text(encoding="utf-8"))
        stats = j.get("stats", {})
        summary.append(
            {
                "a2_index": idx,
                "a2_indices": j.get("a2_indices"),
                "ai_idx": j.get("ai_idx"),
                "bi_idx": j.get("bi_idx"),
                "stats": stats,
            }
        )

    summary_path = OUT_ROOT / "e8_det1_a2_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Wrote", summary_path)


if __name__ == "__main__":
    main()
