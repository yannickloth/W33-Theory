#!/usr/bin/env python3
"""
Evaluate single‑triad augmentations to the l_3 (bad9) support.

For each affine triad T not in bad9:
  - treat bad9' = bad9 ∪ {T}
  - build L∞ using bad9'
  - compute mixed homotopy residual (quick sampling)

Write results to artifacts/l3_candidate_evaluation.json
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "l3_candidate_evaluation.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def triad_key(t):
    return tuple(sorted((int(t[0]), int(t[1]), int(t[2]))))


def main():
    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    linfty_mod = _load_module(
        ROOT / "tools" / "build_linfty_firewall_extension.py", "linfty_mod"
    )

    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = linfty_mod._load_bad9()

    rng = np.random.default_rng(20260212)

    # Use the single-triad deletion contribution (faster) to rank candidates
    cf_path = ROOT / "tools" / "compute_firewall_jacobiator_tensor.py"
    cf_mod = _load_module(cf_path, "cf_mod")

    candidates = []
    for t in all_triads:
        tk = triad_key(t[:3])
        if tk in bad9:
            continue
        contrib = cf_mod.compute_single_triad_jacobi_contribution(
            toe, proj, all_triads, t, rng, e6_basis, trials=24
        )
        # focus on mixed-sector components (g1 + g2)
        mixed_mag = max(contrib.get("g1", 0.0), contrib.get("g2", 0.0))
        candidates.append(
            {
                "triad": t[:3],
                "triad_key": tk,
                "single_triad_mixed_mag": float(mixed_mag),
            }
        )

    candidates.sort(key=lambda x: -x["single_triad_mixed_mag"])

    out = {
        "top_candidates": candidates[:8],
        "all_candidates_count": len(candidates),
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Top candidates (triad -> single-triad mixed magnitude):")
    for c in out["top_candidates"]:
        print(f"  {c['triad']} -> {c['single_triad_mixed_mag']:.3e}")


if __name__ == "__main__":
    main()
