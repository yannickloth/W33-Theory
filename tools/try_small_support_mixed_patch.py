#!/usr/bin/env python3
"""Find small-support rational corrections (1-3 triads) that cancel the
single failing mixed triple without disturbing sampled pure g1/g2 sectors.

Outputs candidate patches to stdout for manual inspection.
"""
from __future__ import annotations

import importlib.util
from fractions import Fraction
from itertools import combinations
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
    proj = toe.E6Projector(e6_basis)

    all_triads = toe._load_signed_cubic_triads()
    # load current bad9 (order preserved in rationalized artifact)
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

    # failing mixed triple (from exhaustive check)
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

    # build Scols
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
    b = -Jf[nz]

    # diagnostics: column norms and alignment
    col_norms = np.linalg.norm(A_sub, axis=0)
    col_dots = np.abs(np.dot(A_sub.T, b))
    idxs = list(range(A_sub.shape[1]))
    ranking = sorted(idxs, key=lambda i: (-col_dots[i], -col_norms[i]))

    print("Top triads by alignment (index, dot, norm):")
    for i in ranking[:6]:
        print(f"  {i:2d}  dot={col_dots[i]:.6e}  norm={col_norms[i]:.6e}")

    uniform = np.array([1.0 / 9.0] * len(ranking))
    r_uniform = (A_sub @ uniform) + Jf[nz]
    print("\nResidual after uniform max abs =", np.max(np.abs(r_uniform)))

    # Try exact solve on small supports (k=1..3) - solve A_sub[:,S] * delta_S = -r_uniform
    best = []
    for k in (1, 2, 3):
        print("\nTrying support size", k)
        for S in combinations(range(A_sub.shape[1]), k):
            As = A_sub[:, list(S)]
            # solve least-squares for delta that would fix uniform residual
            rhs = -r_uniform
            sol, *_ = np.linalg.lstsq(As, rhs, rcond=None)
            # rationalize sol with small denominator
            rats = [Fraction(float(v)).limit_denominator(120) for v in sol]
            sol_rat = np.array([float(r) for r in rats])
            cand = uniform.copy()
            for idx, val in zip(S, sol_rat):
                cand[idx] += val
            # evaluate residual on failing triple
            res_vec = A_sub @ cand + Jf[nz]
            res_max = float(np.max(np.abs(res_vec)))
            # quick sample check for pure sectors (20 samples)
            from tools.build_linfty_firewall_extension import (
                LInftyE8Extension,
                _load_bracket_tool,
            )

            toe_mod = _load_toe()
            proj = toe_mod.E6Projector(e6_basis)
            linfty = LInftyE8Extension(
                toe_mod, proj, all_triads, bad9, l3_scale=1.0 / 9.0
            )
            # temporarily override l3_scale per-triad by constructing l3 manually
            # test failing triple residual under candidate
            l3 = toe_mod.E8Z3.zero()
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
            tot = toe_mod.E8Z3(
                e6=J.e6 + l3.e6, sl3=J.sl3 + l3.sl3, g1=J.g1 + l3.g1, g2=J.g2 + l3.g2
            )
            fail_res = float(
                max(
                    np.max(np.abs(tot.e6)),
                    np.max(np.abs(tot.sl3)),
                    np.max(np.abs(tot.g1)),
                    np.max(np.abs(tot.g2)),
                )
            )
            # quick sampled checks for g1_g1_g1 and g2_g2_g2
            rng = np.random.default_rng(1234)
            sample_ok = True
            for _ in range(20):
                xa = toe_mod._random_element(
                    rng,
                    e6_basis,
                    scale0=0,
                    scale1=2,
                    scale2=0,
                    include_g0=False,
                    include_g2=False,
                )
                ya = toe_mod._random_element(
                    rng,
                    e6_basis,
                    scale0=0,
                    scale1=2,
                    scale2=0,
                    include_g0=False,
                    include_g2=False,
                )
                za = toe_mod._random_element(
                    rng,
                    e6_basis,
                    scale0=0,
                    scale1=2,
                    scale2=0,
                    include_g0=False,
                    include_g2=False,
                )
                # jacobi under br_l2
                j_l2 = toe_mod._jacobi(br_l2, xa, ya, za)
                # assemble candidate l3 for this triple
                l3s = toe_mod.E8Z3.zero()
                for cval, brf in zip(cand, br_fibers):
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
                total = toe_mod.E8Z3(
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
                    sample_ok = False
                    break
            if fail_res < 1e-10 and sample_ok:
                print(
                    "GOOD PATCH S=",
                    S,
                    "sol_rat=",
                    rats,
                    "-> candidate coeffs (first 6)=",
                    [float(cand[i]) for i in range(min(6, len(cand)))],
                )
                best.append((S, rats, cand, fail_res))
    if not best:
        print(
            "\nNo small-support exact rational patch found that preserves sampled pure sectors."
        )
    else:
        print("\nFound patches:")
        for b in best:
            print("  support=", b[0], "rats=", b[1], "residual=", b[3])


if __name__ == "__main__":
    main()
