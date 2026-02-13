#!/usr/bin/env python3
"""
Coordinate-descent over a chosen subset of the 9 fiber triads.
Default subset: indices [0,1,4,7] (implicated + current nonzero triads).
Writes: artifacts/linfty_coord_search_subset_results.json
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
OUT = ROOT / "artifacts" / "linfty_coord_search_subset_results.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    data = json.loads(IN.read_text(encoding="utf-8"))
    coeffs = list(
        data.get("rationalized_coeffs_float") or data.get("original", {}).get("coeffs")
    )
    if coeffs is None:
        raise RuntimeError("No base coefficients found")

    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    tune = _load_module(
        ROOT / "tools" / "tune_l3_coeffs_coordinate_search.py", "tune_l3"
    )

    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()

    bad9 = (
        set(tuple(sorted(t)) for t in data["original"]["fiber_triads"])
        if "original" in data
        else set()
    )
    br_l2 = toe.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )
    fiber_triads = [t for t in all_triads if tuple(sorted(t[:3])) in bad9]
    br_fibers = [
        toe.E8Z3Bracket(
            e6_projector=proj,
            cubic_triads=[T],
            scale_g1g1=1.0,
            scale_g2g2=-1.0 / 6.0,
            scale_e6=1.0,
            scale_sl3=1.0 / 6.0,
        )
        for T in fiber_triads
    ]

    rng = np.random.default_rng(20260212)

    subset = [0, 1, 4, 7]
    candidates = [
        0.0,
        -1.0,
        -0.5,
        -1.0 / 3.0,
        -1.0 / 4.0,
        -1.0 / 6.0,
        -1.0 / 8.0,
        -1.0 / 12.0,
        -2.0 / 15.0,
        -3.0 / 22.0,
        -0.134583,
    ]

    history = []
    passes = 6
    best_profile = {"max": float("inf"), "coeffs": list(coeffs)}

    for p in range(passes):
        changed = False
        for i in subset:
            cur = coeffs[i]
            best_val = None
            best_c = cur
            for cand in candidates:
                test = list(coeffs)
                test[i] = float(cand)
                max_h, mean_h = tune.homotopy_residual_for_coeffs(
                    test, br_l2, br_fibers, toe, e6_basis, rng, trials=40
                )
                if best_val is None or max_h < best_val:
                    best_val = max_h
                    best_c = float(cand)
            if best_c != coeffs[i]:
                history.append(
                    {
                        "pass": p + 1,
                        "triad_index": i,
                        "old": cur,
                        "new": best_c,
                        "max": best_val,
                    }
                )
                coeffs[i] = best_c
                changed = True
                if best_val < best_profile["max"]:
                    best_profile = {"max": float(best_val), "coeffs": list(coeffs)}
        if not changed:
            break

    final_max, final_mean = tune.homotopy_residual_for_coeffs(
        coeffs, br_l2, br_fibers, toe, e6_basis, rng, trials=120
    )

    out = {
        "start_coeffs": data.get("rationalized_coeffs_float"),
        "subset": subset,
        "final_coeffs": coeffs,
        "history": history,
        "final_max_sampled": float(final_max),
        "final_mean_sampled": float(final_mean),
        "best_profile": best_profile,
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
