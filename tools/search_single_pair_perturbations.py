#!/usr/bin/env python3
"""Brute-force search over single- and two-triad coefficient substitutions.

Try replacing 1/9 on one or two fiber triads with values from a small candidate set
and check the failing mixed triple plus sampled pure-sector checks.
"""
from __future__ import annotations

import importlib.util
import json
from itertools import combinations, product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_toe():
    spec = importlib.util.spec_from_file_location(
        "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def flatten(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def main():
    toe = _load_toe()
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)

    # load canonical candidate
    data = json.load(
        (ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json").open()
    )
    canon = [float(Fraction) for Fraction in data["rationalized_coeffs_float"]]

    # candidate replacement pool (try a mix of small denominators & LSQ hints)
    candidate_vals = [
        0.0,
        1.0 / 9.0,
        1.0 / 6.0,
        1.0 / 7.0,
        1.0 / 3.0,
        -1.0 / 8.0,
        -17.0 / 72.0,
    ]

    all_triads = toe._load_signed_cubic_triads()
    bad9 = set(tuple(sorted(t)) for t in data["original"]["fiber_triads"])

    br_l2 = toe.E8Z3Bracket(
        e6_projector=toe.E6Projector(e6_basis),
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )
    br_fibers = [
        toe.E8Z3Bracket(
            e6_projector=toe.E6Projector(e6_basis),
            cubic_triads=[T],
            scale_g1g1=1.0,
            scale_g2g2=-1.0 / 6.0,
            scale_e6=1.0,
            scale_sl3=1.0 / 6.0,
        )
        for T in [t for t in all_triads if tuple(sorted(t[:3])) in bad9]
    ]

    # failing mixed triple (use values from exhaustive artifact)
    exh = json.load(
        (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").open()
    )
    ff = exh["sectors"]["g1_g1_g2"]["first_fail"]
    a_idx, b_idx, c_idx = tuple(ff["a"]), tuple(ff["b"]), tuple(ff["c"])

    # create basis elems
    exh_mod = importlib.util.spec_from_file_location(
        "exh", "tools/exhaustive_homotopy_check_rationalized_l3.py"
    )
    mod = importlib.util.module_from_spec(exh_mod)
    exh_mod.loader = mod

    spec = importlib.util.spec_from_file_location(
        "exhaustive_hj", ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py"
    )
    exhmod = importlib.util.module_from_spec(spec)
    import sys as _sys

    _sys.modules[spec.name] = exhmod
    spec.loader.exec_module(exhmod)
    basis_elem_g1 = exhmod.basis_elem_g1
    basis_elem_g2 = exhmod.basis_elem_g2

    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g2(toe, c_idx)
    J = toe._jacobi(br_l2, x, y, z)

    # helper: test candidate coefficients list
    def test_candidate(coeffs):
        l3 = toe.E8Z3.zero()
        for cval, brf in zip(coeffs, br_fibers):
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
            l3 = l3 + S.scale(-float(cval))
        tot = toe.E8Z3(
            e6=J.e6 + l3.e6, sl3=J.sl3 + l3.sl3, g1=J.g1 + l3.g1, g2=J.g2 + l3.g2
        )
        res = max(
            np.max(np.abs(tot.e6)),
            np.max(np.abs(tot.sl3)),
            np.max(np.abs(tot.g1)),
            np.max(np.abs(tot.g2)),
        )
        if res > 1e-10:
            return False, res
        # sampled pure check (quick)
        rng = np.random.default_rng(123)
        for _ in range(60):
            xa = toe._random_element(
                rng,
                e6_basis,
                scale0=0,
                scale1=2,
                scale2=0,
                include_g0=False,
                include_g2=False,
            )
            ya = toe._random_element(
                rng,
                e6_basis,
                scale0=0,
                scale1=2,
                scale2=0,
                include_g0=False,
                include_g2=False,
            )
            za = toe._random_element(
                rng,
                e6_basis,
                scale0=0,
                scale1=2,
                scale2=0,
                include_g0=False,
                include_g2=False,
            )
            j_l2 = toe._jacobi(br_l2, xa, ya, za)
            l3s = toe.E8Z3.zero()
            for cval, brf in zip(coeffs, br_fibers):
                j1 = brf.bracket(xa, br_l2.bracket(ya, za))
                j2 = brf.bracket(ya, br_l2.bracket(za, xa))
                j3 = brf.bracket(za, br_l2.bracket(xa, ya))
                f1 = br_l2.bracket(brf.bracket(xa, ya), za)
                f2 = br_l2.bracket(brf.bracket(ya, za), xa)
                f3 = br_l2.bracket(brf.bracket(za, xa), ya)
                ff1 = brf.bracket(xa, brf.bracket(ya, za))
                ff2 = brf.bracket(ya, brf.bracket(za, xa))
                ff3 = brf.bracket(za, brf.bracket(xa, ya))
                S = j1 + j2 + j3 + f1 + f2 + f3 + ff1 + ff2 + ff3
                l3s = l3s + S.scale(-float(cval))
            tot2 = toe.E8Z3(
                e6=j_l2.e6 + l3s.e6,
                sl3=j_l2.sl3 + l3s.sl3,
                g1=j_l2.g1 + l3s.g1,
                g2=j_l2.g2 + l3s.g2,
            )
            if (
                max(
                    np.max(np.abs(tot2.e6)),
                    np.max(np.abs(tot2.sl3)),
                    np.max(np.abs(tot2.g1)),
                    np.max(np.abs(tot2.g2)),
                )
                > 1e-8
            ):
                return False, 1e-6
        return True, res

    n = len(canon)
    # single-triad perturbations
    print("Searching single-triad perturbations...")
    for i in range(n):
        for v in candidate_vals:
            if abs(v - canon[i]) < 1e-12:
                continue
            cand = canon.copy()
            cand[i] = v
            ok, r = test_candidate(cand)
            if ok:
                print("FOUND single-triad patch: index=", i, "value=", v, "res=", r)
                return

    # two-triad perturbations
    print("Searching two-triad perturbations (pairwise)...")
    for i, j in combinations(range(n), 2):
        for v1, v2 in product(candidate_vals, candidate_vals):
            if abs(v1 - canon[i]) < 1e-12 and abs(v2 - canon[j]) < 1e-12:
                continue
            cand = canon.copy()
            cand[i] = v1
            cand[j] = v2
            ok, r = test_candidate(cand)
            if ok:
                print(
                    "FOUND pair patch: indices=", (i, j), "values=", (v1, v2), "res=", r
                )
                return

    print(
        "No single- or pairwise substitution from the candidate set produced an acceptable patch."
    )


if __name__ == "__main__":
    main()
