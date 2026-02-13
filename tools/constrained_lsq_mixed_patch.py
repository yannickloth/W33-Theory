#!/usr/bin/env python3
"""Bounded least-squares for mixed triple correction.
Minimize ||A_sub · delta + r_uniform|| with box bounds on delta to keep
corrections small, then rationalize and test.
"""
from __future__ import annotations

import importlib.util
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import lsq_linear

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


def main(max_delta=0.02, max_den=120):
    toe = _load_toe()
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)

    all_triads = toe._load_signed_cubic_triads()
    import json

    rat = json.loads(
        (
            ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
        ).read_text()
    )
    bad9 = set(tuple(sorted(t)) for t in rat["original"]["fiber_triads"])

    br_l2 = toe.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )
    br_fibers = [
        toe.E8Z3Bracket(
            e6_projector=proj,
            cubic_triads=[T],
            scale_g1g1=1.0,
            scale_g2g2=-1.0 / 6.0,
            scale_e6=1.0,
            scale_sl3=1.0 / 6.0,
        )
        for T in [t for t in all_triads if tuple(sorted(t[:3])) in bad9]
    ]

    from tools.exhaustive_homotopy_check_rationalized_l3 import (
        basis_elem_g1,
        basis_elem_g2,
    )

    a_idx = (0, 0)
    b_idx = (17, 1)
    c_idx = (3, 0)
    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g2(toe, c_idx)

    J = toe._jacobi(br_l2, x, y, z)
    Jf = flatten(J)
    nz = np.where(np.abs(Jf) > 1e-12)[0]

    Scols = []
    for brf in br_fibers:
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
        Scols.append(flatten(S))
    A = np.array(Scols).T
    A_sub = A[nz, :]
    # residual after uniform
    uniform = np.array([1.0 / 9.0] * A_sub.shape[1])
    r_uniform = (A_sub @ uniform) + Jf[nz]

    # bounded LSQ: minimize ||A_sub · delta + r_uniform|| with -max_delta <= delta <= max_delta
    lb = -np.ones(A_sub.shape[1]) * max_delta
    ub = np.ones(A_sub.shape[1]) * max_delta
    sol = lsq_linear(
        A_sub, -r_uniform, bounds=(lb, ub), lsmr_tol="auto", max_iter=10000
    )
    delta = sol.x
    print("LSQ bounded status:", sol.message)
    print("delta (float):", [float(round(d, 12)) for d in delta])

    # rationalize delta
    rats = [Fraction(float(d)).limit_denominator(max_den) for d in delta]
    delta_rat = np.array([float(r) for r in rats])
    cand = uniform + delta_rat
    print("\nCandidate (uniform + delta_rat):")
    print([str(r) for r in rats])
    print([float(round(c, 12)) for c in cand])

    # evaluate failing triple residual under candidate
    l3 = toe.E8Z3.zero()
    for cval, brf in zip(cand, br_fibers):
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
    res = toe.E8Z3(
        e6=J.e6 + l3.e6, sl3=J.sl3 + l3.sl3, g1=J.g1 + l3.g1, g2=J.g2 + l3.g2
    )
    res_max = float(
        max(
            np.max(np.abs(res.e6)),
            np.max(np.abs(res.sl3)),
            np.max(np.abs(res.g1)),
            np.max(np.abs(res.g2)),
        )
    )
    print("\nFailing triple residual after candidate:", res_max)

    # quick sampled check for pure sectors (40 samples)
    rng = np.random.default_rng(20260212)
    from tools.build_linfty_firewall_extension import LInftyE8Extension

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    def assemble_l3_for_triple(xa, ya, za, coeffs):
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
        return l3s

    ok = True
    for _ in range(40):
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
        l3s = assemble_l3_for_triple(xa, ya, za, cand)
        total = toe.E8Z3(
            e6=j_l2.e6 + l3s.e6,
            sl3=j_l2.sl3 + l3s.sl3,
            g1=j_l2.g1 + l3s.g1,
            g2=j_l2.g2 + l3s.g2,
        )
        if (
            max(
                np.max(np.abs(total.e6)),
                np.max(np.abs(total.sl3)),
                np.max(np.abs(total.g1)),
                np.max(np.abs(total.g2)),
            )
            > 1e-8
        ):
            ok = False
            break
    print("\nSampled pure-sector check pass?:", ok)

    # If ok and res_max small, print rational candidate
    if ok and res_max < 1e-10:
        print("\nAcceptable bounded-LSQ candidate found (rationalized deltas):")
        print([str(r) for r in rats])
    else:
        print("\nNo acceptable bounded-LSQ candidate found with max_delta=", max_delta)


if __name__ == "__main__":
    main()
