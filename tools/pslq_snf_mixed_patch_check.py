#!/usr/bin/env python3
"""Quick PSLQ/SNF probe for the mixed failing triple.

- loads the failing triple from artifacts/mixed_triple_lsq_correction.json
- computes per-triad S_T flats and the Jacobi vector J
- tries rationalizations (Fraction.limit_denominator) of S·J overlaps
- runs Smith Normal Form membership tests for denominators in D_LIST
- writes artifacts/pslq_snf_mixed_patch_check.json
"""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import List

import numpy as np
from sympy import Matrix, N
from sympy.matrices.normalforms import smith_normal_form

# pslq import is optional; try sympy first, fall back to mpmath
try:
    from sympy.ntheory import pslq
except Exception:
    try:
        from sympy.ntheory.modular import pslq
    except Exception:
        try:
            import mpmath as _mp

            def pslq(vec):
                mp_vec = [_mp.mpf(str(float(x))) for x in vec]
                return _mp.pslq(mp_vec)

        except Exception:
            pslq = None

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "pslq_snf_mixed_patch_check.json"

# extended denominator sweep (added 960, 1920)
D_LIST = [9, 72, 240, 480, 960, 1920]
MAX_DEN = 1920


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def flatten(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def main():
    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    exh = _load_module(
        ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py", "exhaustive_hj"
    )
    basis_elem_g1 = exh.basis_elem_g1
    basis_elem_g2 = exh.basis_elem_g2

    data = json.loads(
        (ROOT / "artifacts" / "mixed_triple_lsq_correction.json").read_text()
    )
    ft = data.get("failed_triple", {})
    a_idx = tuple(ft.get("a", [0, 0]))
    b_idx = tuple(ft.get("b", [0, 0]))
    c_idx = tuple(ft.get("c", [0, 0]))

    # load triads & build helper brackets
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    # try to read known bad9 mapping from artifact
    bad9 = set()
    fb = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"
    if fb.exists():
        try:
            bad9_list = json.loads(fb.read_text(encoding="utf-8")).get(
                "bad_triangles_Schlafli_e6id", []
            )
            bad9 = set(tuple(sorted(t)) for t in bad9_list)
        except Exception:
            bad9 = set()
    # fallback: use linfty helper to get bad9 if artifact missing or malformed
    try:
        linfty_mod = _load_module(
            ROOT / "tools" / "build_linfty_firewall_extension.py", "linfty_mod"
        )
        bad9 = linfty_mod._load_bad9()
    except Exception:
        pass

    fiber_triads = [t for t in all_triads if tuple(sorted(t[:3])) in bad9]

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
        for T in fiber_triads
    ]

    # basis elements and Jacobi
    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g2(toe, c_idx)

    J = toe._jacobi(br_l2, x, y, z)
    Jflat = flatten(J)

    # S_T flats
    S_flats = []
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
        S_flats.append(flatten(S))

    A_real = np.vstack([np.real(np.array(S_flats)).T, np.imag(np.array(S_flats)).T])
    b_real = -np.concatenate([np.real(Jflat), np.imag(Jflat)])

    # dot-products S^T J (complex inner product), rationalize with Fraction.limit_denominator
    overlaps = []
    for S in S_flats:
        dot = float(np.vdot(S, Jflat))
        rat = Fraction(dot).limit_denominator(MAX_DEN)
        overlaps.append(
            {
                "dot_float": dot,
                "dot_rational_guess": f"{rat.numerator}/{rat.denominator}",
            }
        )

    # PSLQ attempt on the dot-products (as high-precision reals)
    dp_vec = [o["dot_float"] for o in overlaps]
    try:
        # convert to high-precision sympy numbers
        sp_vec = [N(v, 80) for v in dp_vec]
        pslq_relation = pslq(sp_vec)
    except Exception:
        pslq_relation = None

    # SNF membership tests for multiple denominators
    snf_results = {}
    for D in D_LIST:
        M_int = np.rint(A_real * D).astype(int)
        b_int = np.rint(b_real * D).astype(int)
        Mm = Matrix(M_int.tolist())
        try:
            snf_res = smith_normal_form(Mm)
            if isinstance(snf_res, (tuple, list)):
                Smat, U, V = snf_res
            else:
                Smat = snf_res
                U = None
                V = None
            diag = [
                int(Smat[i, i])
                for i in range(min(Smat.rows, Smat.cols))
                if Smat[i, i] != 0
            ]
            rankM = np.linalg.matrix_rank(M_int)
            rankAug = np.linalg.matrix_rank(np.column_stack([M_int, b_int]))

            solvable = False
            divisibility_checks = None
            Ub_list = None
            if U is not None:
                # test U * b_int divisibility conditions
                Ub = U * Matrix(b_int.tolist())
                Ub_list = [int(x) for x in Ub]
                # find r = rank (# nonzero diag)
                r = len(diag)
                ok = True
                checks = []
                for i in range(r):
                    si = int(Smat[i, i])
                    yi = int(Ub[i, 0])
                    checks.append(
                        {"row": i, "si": si, "yi": yi, "divisible": (yi % si == 0)}
                    )
                    if yi % si != 0:
                        ok = False
                # remaining rows must be zero
                for j in range(r, Ub.rows):
                    if int(Ub[j, 0]) != 0:
                        ok = False
                divisibility_checks = checks
                solvable = bool(ok)

            snf_results[str(D)] = {
                "rank_M": int(rankM),
                "rank_augmented": int(rankAug),
                "snf_diag": diag,
                "snf_solvable_integer_combination_with_denominator": bool(solvable),
                "U_times_b": Ub_list,
                "divisibility_checks": divisibility_checks,
            }
        except Exception as e:
            snf_results[str(D)] = {"error": str(e)}

    out = {
        "failed_triple": {"a": a_idx, "b": b_idx, "c": c_idx},
        "overlaps": overlaps,
        "pslq_on_overlaps": pslq_relation,
        "snf_results": snf_results,
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote:", OUT)


if __name__ == "__main__":
    main()
