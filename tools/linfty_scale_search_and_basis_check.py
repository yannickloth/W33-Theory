#!/usr/bin/env python3
"""
Grid-search l_3 scale and run exhaustive g1-basis homotopy Jacobi check.

Produces:
  - artifacts/linfty_scale_search_results.json
  - artifacts/linfty_basis_homotopy_check.json

This is a lightweight diagnostic (deterministic RNG) intended to find an
l_3 scaling that reduces the *mixed* homotopy residual and to report the
max residual over the canonical g1 basis triples for the best scale.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
from pathlib import Path
from typing import List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_SCALE_JSON = ROOT / "artifacts" / "linfty_scale_search_results.json"
OUT_BASIS_JSON = ROOT / "artifacts" / "linfty_basis_homotopy_check.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _triad_key(i: int, j: int, k: int) -> Tuple[int, int, int]:
    return tuple(sorted((int(i), int(j), int(k))))


def main():
    toe_path = ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
    linfty_path = ROOT / "tools" / "build_linfty_firewall_extension.py"

    toe = _load_module(toe_path, "toe_e8_z3graded_bracket_jacobi")
    linfty_mod = _load_module(linfty_path, "build_linfty_firewall_extension")

    basis_path = ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    e6_basis = np.load(basis_path).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)

    all_triads = toe._load_signed_cubic_triads()
    # load the firewall "bad9" set used by the LInfty builder
    bad9 = linfty_mod._load_bad9()

    rng = np.random.default_rng(123)

    # grid search for l3_scale
    scales = np.linspace(-1.0, 2.0, 31)
    results = []
    for s in scales:
        L = linfty_mod.LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=float(s))
        stats = linfty_mod.verify_homotopy_jacobi(L, toe, e6_basis, rng, trials=30)
        mixed = stats["mixed"]["homotopy_residual_max"]
        results.append({"l3_scale": float(s), "mixed_homotopy_residual": float(mixed)})

    # pick best scale (min mixed residual)
    best = min(results, key=lambda r: r["mixed_homotopy_residual"])

    # Exhaustive g1-basis triple check for best scale
    best_scale = best["l3_scale"]
    Lbest = linfty_mod.LInftyE8Extension(
        toe, proj, all_triads, bad9, l3_scale=best_scale
    )

    # build canonical g1 basis (27 x 3 = 81)
    g1_basis: List[toe.E8Z3] = []
    for i in range(27):
        for j in range(3):
            e = toe.E8Z3.zero()
            g1 = np.zeros((27, 3), dtype=np.complex128)
            g1[i, j] = 1.0
            g1_basis.append(
                toe.E8Z3(
                    e6=np.zeros((27, 27), dtype=np.complex128),
                    sl3=np.zeros((3, 3), dtype=np.complex128),
                    g1=g1,
                    g2=np.zeros((27, 3), dtype=np.complex128),
                )
            )

    max_l2_anom = 0.0
    max_homotopy = 0.0
    count_nonzero_homotopy = 0

    # iterate combinations (unordered) of 3 basis vectors
    total = 0
    from math import comb

    total = comb(len(g1_basis), 3)
    print(f"Running exhaustive g1-basis triples: {total} checks")

    thresh = 1e-12
    idx = 0
    for a_idx, b_idx, c_idx in itertools.combinations(range(len(g1_basis)), 3):
        a = g1_basis[a_idx]
        b = g1_basis[b_idx]
        c = g1_basis[c_idx]

        j_l2 = toe._jacobi(Lbest.br_l2, a, b, c)
        hj = Lbest.homotopy_jacobi(a, b, c)

        l2_mag = max(
            float(np.max(np.abs(j_l2.e6))) if j_l2.e6.size else 0.0,
            float(np.max(np.abs(j_l2.sl3))) if j_l2.sl3.size else 0.0,
            float(np.max(np.abs(j_l2.g1))) if j_l2.g1.size else 0.0,
            float(np.max(np.abs(j_l2.g2))) if j_l2.g2.size else 0.0,
        )
        hj_mag = max(
            float(np.max(np.abs(hj.e6))) if hj.e6.size else 0.0,
            float(np.max(np.abs(hj.sl3))) if hj.sl3.size else 0.0,
            float(np.max(np.abs(hj.g1))) if hj.g1.size else 0.0,
            float(np.max(np.abs(hj.g2))) if hj.g2.size else 0.0,
        )

        max_l2_anom = max(max_l2_anom, l2_mag)
        max_homotopy = max(max_homotopy, hj_mag)
        if hj_mag > thresh:
            count_nonzero_homotopy += 1

        idx += 1
        if idx % 5000 == 0:
            print(
                f"  checked {idx}/{total} triples — current max homotopy {max_homotopy:.3e}"
            )

    out_scale = {
        "grid": results,
        "best": best,
    }
    OUT_SCALE_JSON.write_text(json.dumps(out_scale, indent=2), encoding="utf-8")

    out_basis = {
        "best_scale": best_scale,
        "g1_basis_triples_checked": total,
        "max_l2_anomaly_on_basis_triples": max_l2_anom,
        "max_homotopy_residual_on_basis_triples": max_homotopy,
        "count_triples_with_homotopy_gt_1e-12": count_nonzero_homotopy,
    }
    OUT_BASIS_JSON.write_text(json.dumps(out_basis, indent=2), encoding="utf-8")

    print("\nSummary:")
    print(
        f"  best l3_scale = {best_scale} → mixed homotopy residual = {best['mixed_homotopy_residual']:.3e}"
    )
    print(f"  exhaustive g1-basis triples: max l2 anomaly = {max_l2_anom:.3e}")
    print(f"  exhaustive g1-basis triples: max homotopy residual = {max_homotopy:.3e}")
    print(f"  triples with homotopy > 1e-12: {count_nonzero_homotopy}")


if __name__ == "__main__":
    main()
