#!/usr/bin/env python3
"""Run SNF/PSLQ membership tests for failing triples reported by exhaustive check.

Writes: artifacts/verify_exhaustive_failures_snf_pslq.json
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import List

import numpy as np
from sympy import Matrix, N
from sympy.matrices.normalforms import smith_normal_form

ROOT = Path(__file__).resolve().parents[1]
EXH = ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json"
OUT = ROOT / "artifacts" / "verify_exhaustive_failures_snf_pslq.json"

# denominators grid to test (expand if needed)
D_LIST = [9, 18, 36, 72, 120, 240, 360, 480]
MAX_DEN = max(D_LIST)


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


def analyze_triple(toe, br_l2, br_fibers, a_idx, b_idx, c_idx) -> dict:
    # import basis element factories without package import (use dynamic loader)
    exh_spec = importlib.util.spec_from_file_location(
        "exhaustive_hj", ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py"
    )
    exh_mod = importlib.util.module_from_spec(exh_spec)
    import sys as _sys

    _sys.modules[exh_spec.name] = exh_mod
    exh_spec.loader.exec_module(exh_mod)
    basis_elem_g1 = exh_mod.basis_elem_g1
    basis_elem_g2 = exh_mod.basis_elem_g2

    # build x,y,z depending on types (we assume g1_g1_g2 triple by convention)
    x = basis_elem_g1(toe, tuple(a_idx))
    y = basis_elem_g1(toe, tuple(b_idx))
    z = basis_elem_g2(toe, tuple(c_idx))

    J = toe._jacobi(br_l2, x, y, z)
    Jflat = flatten(J)

    # build S_flats (per fiber triad)
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

    # assemble real block matrix (handle degenerate S/J sizes)
    S_mat = np.array(S_flats)
    if S_mat.size == 0:
        # no S contributions (degenerate): return diagnosis
        return {
            "J_norm_max": float(np.max(np.abs(Jflat))) if Jflat.size else 0.0,
            "degenerate": True,
            "note": "S_flats empty or zero; nothing to solve on this support",
            "overlaps": [0.0 for _ in S_flats],
            "snf_map": {},
        }

    A_real = np.vstack([np.real(S_mat).T, np.imag(S_mat).T])
    b_real = -np.concatenate([np.real(Jflat), np.imag(Jflat)])

    # quick linear-algebra facts (guard against zero-dim arrays)
    rank_A = int(np.linalg.matrix_rank(A_real)) if A_real.size else 0
    rank_aug = (
        int(np.linalg.matrix_rank(np.column_stack([A_real, b_real])))
        if A_real.size
        else 0
    )

    overlaps = [float(np.vdot(S, Jflat)) for S in S_flats]

    # SNF checks for denominators
    snf_map = {}
    for D in D_LIST:
        M_int = np.rint(A_real * D).astype(int)
        b_int = np.rint(b_real * D).astype(int)
        try:
            snf_res = smith_normal_form(Matrix(M_int.tolist()))
            if isinstance(snf_res, (tuple, list)):
                S_mat, U, V = snf_res
            else:
                S_mat = snf_res
                U = None
                V = None
            diag = [
                int(S_mat[i, i])
                for i in range(min(S_mat.rows, S_mat.cols))
                if S_mat[i, i] != 0
            ]
            rankM = np.linalg.matrix_rank(M_int)
            rankAug = np.linalg.matrix_rank(np.column_stack([M_int, b_int]))

            solvable = False
            divisibility = None
            U_times_b = None
            if U is not None:
                Ub = U * Matrix(b_int.tolist())
                U_times_b = [int(x) for x in Ub]
                r = len(diag)
                ok = True
                checks = []
                for i in range(r):
                    si = int(S_mat[i, i])
                    yi = int(Ub[i, 0])
                    checks.append(
                        {"row": i, "si": si, "yi": yi, "divisible": (yi % si == 0)}
                    )
                    if yi % si != 0:
                        ok = False
                for j in range(r, Ub.rows):
                    if int(Ub[j, 0]) != 0:
                        ok = False
                divisibility = checks
                solvable = bool(ok)

            snf_map[str(D)] = {
                "rank_M": int(rankM),
                "rank_augmented": int(rankAug),
                "snf_diag": diag,
                "snf_solvable_integer_combination_with_denominator": solvable,
                "U_times_b": U_times_b,
                "divisibility_checks": divisibility,
            }
        except Exception as e:
            snf_map[str(D)] = {"error": str(e)}

    return {
        "J_norm_max": float(np.max(np.abs(Jflat))),
        "rank_A_real": rank_A,
        "rank_augmented_real": rank_aug,
        "overlaps": overlaps,
        "snf_map": snf_map,
    }


def main():
    if not EXH.exists():
        raise RuntimeError(
            "Exhaustive result artifact missing; run tools/exhaustive_homotopy_check_rationalized_l3.py first"
        )
    data = json.loads(EXH.read_text(encoding="utf-8"))

    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)

    all_triads = toe._load_signed_cubic_triads()
    bad9 = set(
        tuple(sorted(t[:3])) for t in data.get("original", {}).get("fiber_triads", [])
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

    out = {"exhaustive_artifact": str(EXH), "failures": {}}

    sectors = data.get("sectors", {})
    for sector_name, info in sectors.items():
        if not info.get("passed", True):
            first = info.get("first_fail")
            if not first:
                continue
            a = first["a"]
            b = first["b"]
            c = first["c"]
            print(f"Analyzing failure {sector_name} triple {a},{b},{c}...")
            res = analyze_triple(toe, br_l2, br_fibers, a, b, c)
            out["failures"][sector_name] = {
                "triple": {"a": a, "b": b, "c": c},
                "analysis": res,
            }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
