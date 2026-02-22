#!/usr/bin/env python3
"""
Targeted local search: vary a small subset of the 9 fiber triads (defaults to indices [0,1])
and search for small/rational coefficients that reduce the sampled homotopy residual.

Writes: artifacts/local_targeted_l3_search_results.json
"""
from __future__ import annotations

import importlib.util
import json
from itertools import product
from pathlib import Path
from typing import List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
OUT = ROOT / "artifacts" / "local_targeted_l3_search_results.json"


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
    base_coeffs = data.get("rationalized_coeffs_float") or data.get("original", {}).get(
        "coeffs"
    )
    if base_coeffs is None:
        raise RuntimeError("No base coefficients found")

    # modules
    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    tune = _load_module(
        ROOT / "tools" / "tune_l3_coeffs_coordinate_search.py", "tune_l3"
    )

    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()

    # firewall-filtered l2 and fiber brackets
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

    # triad indices to vary (target the triads implicated by the failing triple)
    vary_indices = [0, 1]  # corresponds to fiber triads [0,21,22] and [1,15,23]

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

    best = {"max": float("inf"), "coeffs": None, "stats": None}
    records = []

    # grid search over small candidate set for the chosen triads
    total = len(candidates) ** len(vary_indices)
    print(f"Searching {total} combinations over triad indices {vary_indices} ...")

    # failing triple to target (g1 basis indices)
    failing_triple = ((0, 0), (1, 1), (21, 2))

    # Stage 1: cheap check — evaluate homotopy residual only on the failing triple
    print("Stage 1: focused check on the failing triple", failing_triple)
    for comb in product(candidates, repeat=len(vary_indices)):
        test_coeffs = list(base_coeffs)
        for idx, val in zip(vary_indices, comb):
            test_coeffs[idx] = float(val)

        # build g1 basis elements for the failing triple
        a_idx, b_idx, c_idx = failing_triple
        x = toe.E8Z3.zero()
        x.g1[a_idx[0], a_idx[1]] = 1.0
        y = toe.E8Z3.zero()
        y.g1[b_idx[0], b_idx[1]] = 1.0
        z = toe.E8Z3.zero()
        z.g1[c_idx[0], c_idx[1]] = 1.0

        # Jacobi for l2 (affine-only bracket)
        j_l2 = toe._jacobi(br_l2, x, y, z)
        mag_j = float(
            max(
                np.max(np.abs(j_l2.e6)),
                np.max(np.abs(j_l2.sl3)),
                np.max(np.abs(j_l2.g1)),
                np.max(np.abs(j_l2.g2)),
            )
        )

        # assemble l3 for this triple using test_coeffs (cheap: per-fiber bracket contributions)
        l3_total = toe.E8Z3.zero()
        for c_val, brf in zip(test_coeffs, br_fibers):
            j1 = brf.bracket(x, br_l2.bracket(y, z))
            j2 = brf.bracket(y, br_l2.bracket(z, x))
            j3 = brf.bracket(z, br_l2.bracket(x, y))
            f1 = br_l2.bracket(brf.bracket(x, y), z)
            f2 = br_l2.bracket(brf.bracket(y, z), x)
            f3 = br_l2.bracket(brf.bracket(z, x), y)
            ff1 = brf.bracket(x, brf.bracket(y, z))
            ff2 = brf.bracket(y, brf.bracket(z, x))
            ff3 = brf.bracket(z, brf.bracket(x, y))
            S = j1 + j2 + j3 + f1 + f2 + f3 + ff1 + ff2 + ff3
            l3_total = l3_total + S.scale(-float(c_val))

        total = toe.E8Z3(
            e6=j_l2.e6 + l3_total.e6,
            sl3=j_l2.sl3 + l3_total.sl3,
            g1=j_l2.g1 + l3_total.g1,
            g2=j_l2.g2 + l3_total.g2,
        )
        mag_tot = float(
            max(
                np.max(np.abs(total.e6)),
                np.max(np.abs(total.sl3)),
                np.max(np.abs(total.g1)),
                np.max(np.abs(total.g2)),
            )
        )

        rec = {
            "trial": comb,
            "fail_mag_j": mag_j,
            "fail_mag_total": mag_tot,
            "coeffs": test_coeffs,
        }
        records.append(rec)
        if mag_tot < best["max"]:
            best = {"max": float(mag_tot), "coeffs": list(test_coeffs), "stats": rec}

    # Stage 2: verify top candidates (by failing-triple residual) with sampled check
    top_candidates = sorted(records, key=lambda r: r["fail_mag_total"])[:8]
    print("Stage 2: sampled verification of top candidates (", len(top_candidates), ")")
    for rc in top_candidates:
        test_coeffs = rc["coeffs"]
        max_h, mean_h = tune.homotopy_residual_for_coeffs(
            test_coeffs, br_l2, br_fibers, toe, e6_basis, rng, trials=40
        )
        rc["sampled_max"] = float(max_h)
        rc["sampled_mean"] = float(mean_h)
        if max_h < best["max"]:
            best = {"max": float(max_h), "coeffs": list(test_coeffs), "stats": rc}

    # sort top candidates
    records_sorted = sorted(
        records,
        key=lambda r: r.get("sampled_max", r.get("fail_mag_total", float("inf"))),
    )[:10]

    out = {
        "base_coeffs": base_coeffs,
        "vary_indices": vary_indices,
        "candidates": candidates,
        "best": best,
        "top10": records_sorted,
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
