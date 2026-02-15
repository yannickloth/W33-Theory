#!/usr/bin/env python3
"""
Coordinate-descent search for small/rational l_3 coefficients on the 9 fiber triads.

Strategy:
 - start from baseline (uniform scale = candidate or 0)
 - for each fiber triad, try a small set of rational coefficients and accept the
   change if it reduces the sampled mixed homotopy residual
 - repeat for a few passes

Writes: artifacts/linfty_coord_search_results.json
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "linfty_coord_search_results.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _flatten_e8z3(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def homotopy_residual_for_coeffs(
    coeffs: List[float],
    br_l2,
    br_fibers,
    toe_mod,
    e6_basis,
    rng,
    trials=40,
):
    max_h = 0.0
    sum_h = 0.0
    for _ in range(trials):
        x = toe_mod._random_element(rng, e6_basis, scale0=2, scale1=2, scale2=2)
        y = toe_mod._random_element(rng, e6_basis, scale0=2, scale1=2, scale2=2)
        z = toe_mod._random_element(rng, e6_basis, scale0=2, scale1=2, scale2=2)

        j_l2 = toe_mod._jacobi(br_l2, x, y, z)

        # assemble l3 from coeffs
        l3_total = toe_mod.E8Z3.zero()
        for c, brf in zip(coeffs, br_fibers):
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
            l3_total = l3_total + S.scale(-float(c))

        total = toe_mod.E8Z3(
            e6=j_l2.e6 + l3_total.e6,
            sl3=j_l2.sl3 + l3_total.sl3,
            g1=j_l2.g1 + l3_total.g1,
            g2=j_l2.g2 + l3_total.g2,
        )

        mag = max(
            np.max(np.abs(total.e6)),
            np.max(np.abs(total.sl3)),
            np.max(np.abs(total.g1)),
            np.max(np.abs(total.g2)),
        )
        max_h = max(max_h, float(mag))
        sum_h += float(mag)
    return max_h, sum_h / trials


def main():
    # keep a defensive wrapper so partial progress is saved on error
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

    # firewall-filtered l2 bracket
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

    # baseline: uniform global scale from previous quick fit
    baseline_scale = -0.134583
    coeffs = [baseline_scale for _ in fiber_triads]

    try:
        print("Baseline uniform scale", baseline_scale)
        base_max, base_mean = homotopy_residual_for_coeffs(
            coeffs, br_l2, br_fibers, toe, e6_basis, rng, trials=120
        )
        print("  baseline max,mean:", base_max, base_mean)

        # candidate rationals to try (small, interpretable)
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
            baseline_scale,
        ]

        improved = True
        passes = 5
        history = []

        for p in range(passes):
            changed = False
            for i in range(len(coeffs)):
                best_coeff = coeffs[i]
                best_val = None
                for cand in candidates:
                    test = list(coeffs)
                    test[i] = float(cand)
                    max_h, mean_h = homotopy_residual_for_coeffs(
                        test, br_l2, br_fibers, toe, e6_basis, rng, trials=120
                    )
                    if best_val is None or max_h < best_val:
                        best_val = max_h
                        best_coeff = float(cand)
                if best_coeff != coeffs[i]:
                    print(
                        f"Pass {p+1}: triad {i} coeff {coeffs[i]:.6f} -> {best_coeff:.6f} (max {best_val:.3e})"
                    )
                    coeffs[i] = best_coeff
                    changed = True
                    history.append(
                        {"triad_index": i, "new_coeff": best_coeff, "max_h": best_val}
                    )
            if not changed:
                break

        final_max, final_mean = homotopy_residual_for_coeffs(
            coeffs, br_l2, br_fibers, toe, e6_basis, rng, trials=120
        )

        out = {
            "fiber_triads": [list(t[:3]) for t in fiber_triads],
            "baseline_scale": baseline_scale,
            "initial_baseline_max": float(base_max),
            "coeffs": coeffs,
            "history": history,
            "final_max_sampled": float(final_max),
            "final_mean_sampled": float(final_mean),
        }
        OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print("Wrote", OUT)
        print("Final max,mean:", final_max, final_mean)

    except Exception as exc:
        # attempt to persist partial progress
        partial = {
            "fiber_triads": (
                [list(t[:3]) for t in fiber_triads]
                if "fiber_triads" in locals()
                else []
            ),
            "coeffs": coeffs if "coeffs" in locals() else [],
            "history": history if "history" in locals() else [],
            "error": repr(exc),
        }
        try:
            OUT.write_text(json.dumps(partial, indent=2), encoding="utf-8")
            print("Wrote partial results to", OUT)
        except Exception:
            print("Failed to write partial results")
        raise


if __name__ == "__main__":
    main()
