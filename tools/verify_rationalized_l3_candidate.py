#!/usr/bin/env python3
"""
Rationalize the coordinate-descent l3 candidate (PSLQ/limit_denominator) and
verify homotopy‑Jacobi numerically using the rationalized coefficients.

Writes: artifacts/linfty_coord_search_results_rationalized.json
"""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "artifacts" / "linfty_coord_search_results.json"
OUT = ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def rationalize_coeffs(xs: List[float], max_den=240) -> List[Fraction]:
    return [Fraction(x).limit_denominator(max_den) for x in xs]


def assemble_l3_total_from_coeffs(
    coeffs: List[float], br_l2, br_fibers, toe_mod, x, y, z
):
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
    return l3_total


def max_mag(e):
    return max(
        np.max(np.abs(e.e6)),
        np.max(np.abs(e.sl3)),
        np.max(np.abs(e.g1)),
        np.max(np.abs(e.g2)),
    )


def case_residuals(
    coeffs: List[float], br_l2, br_fibers, toe_mod, e6_basis, rng, trials=200
) -> dict:
    cases = {
        "g1_g1_g1": lambda: toe_mod._random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=2,
            scale2=0,
            include_g0=False,
            include_g2=False,
        ),
        "g2_g2_g2": lambda: toe_mod._random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=0,
            scale2=2,
            include_g0=False,
            include_g1=False,
        ),
        "mixed": lambda: toe_mod._random_element(
            rng, e6_basis, scale0=2, scale1=2, scale2=2
        ),
    }

    out = {}
    for name, gen in cases.items():
        max_r = 0.0
        sum_r = 0.0
        for _ in range(trials):
            x, y, z = gen(), gen(), gen()
            j_l2 = toe_mod._jacobi(br_l2, x, y, z)
            l3_total = assemble_l3_total_from_coeffs(
                coeffs, br_l2, br_fibers, toe_mod, x, y, z
            )
            total = toe_mod.E8Z3(
                e6=j_l2.e6 + l3_total.e6,
                sl3=j_l2.sl3 + l3_total.sl3,
                g1=j_l2.g1 + l3_total.g1,
                g2=j_l2.g2 + l3_total.g2,
            )
            mag = float(max_mag(total))
            max_r = max(max_r, mag)
            sum_r += mag
        out[name] = {"max": max_r, "mean": sum_r / trials}
    return out


def main():
    data = json.loads(IN.read_text(encoding="utf-8"))
    coeffs_num = data.get("coeffs", [])

    # rationalize
    rat = rationalize_coeffs(coeffs_num, max_den=240)
    rat_str = [
        f"{f.numerator}/{f.denominator}" if f.denominator != 1 else str(f.numerator)
        for f in rat
    ]
    rat_as_float = [float(f) for f in rat]

    # load modules and bracket objects (reuse tune setup)
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
        set(tuple(sorted(t)) for t in data["fiber_triads"])
        if "fiber_triads" in data
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

    # verify numeric candidate vs rationalized candidate
    trials = 240
    print("Numeric coeffs:", coeffs_num)
    num_max, num_mean = tune.homotopy_residual_for_coeffs(
        coeffs_num, br_l2, br_fibers, toe, e6_basis, rng, trials=trials
    )
    print(f"Numeric -> max {num_max:.6e}, mean {num_mean:.6e}")

    print("Rationalized coeffs:", rat_str)
    rat_max, rat_mean = tune.homotopy_residual_for_coeffs(
        rat_as_float, br_l2, br_fibers, toe, e6_basis, rng, trials=trials
    )
    print(f"Rationalized -> max {rat_max:.6e}, mean {rat_mean:.6e}")

    # case-by-case residuals (g1/g2/mixed) for rationalized candidate
    case_stats = case_residuals(
        rat_as_float, br_l2, br_fibers, toe, e6_basis, rng, trials=40
    )
    for k, v in case_stats.items():
        print(f"  {k}: max={v['max']:.6e}, mean={v['mean']:.6e}")

    out = {
        "original": data,
        "rationalized_coeffs": rat_str,
        "rationalized_coeffs_float": rat_as_float,
        "numeric_stats": {"max": float(num_max), "mean": float(num_mean)},
        "rationalized_stats": {"max": float(rat_max), "mean": float(rat_mean)},
        "case_stats": case_stats,
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
