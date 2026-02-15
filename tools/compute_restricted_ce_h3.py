#!/usr/bin/env python3
"""Compute restricted Chevalley--Eilenberg H^3 for a given failing triple support.

- Loads the failing triple from `artifacts/exhaustive_homotopy_rationalized_l3.json`
  (or accepts a triple via CLI).
- Builds the per-fiber S_flats and the Jacobiator J.
- Returns linear-algebra diagnostics and exact SNF membership checks for
  denominators in D_LIST.
- Writes artifact: artifacts/restricted_ce_h3_<sector>.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Tuple

import numpy as np
from sympy import Matrix
from sympy.matrices.normalforms import smith_normal_form

ROOT = Path(__file__).resolve().parents[1]
EXH = ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json"
OUT_DIR = ROOT / "artifacts"
D_LIST = [9, 18, 36, 72, 120, 240, 360, 480, 960]


def flatten(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    import sys as _sys

    _sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def analyze_triple(
    toe, a_idx: Tuple[int, int], b_idx: Tuple[int, int], c_idx: Tuple[int, int]
):
    # load helpers from exhaustive_homotopy_check_rationalized_l3
    exh_spec = importlib.util.spec_from_file_location(
        "exh_mod", ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py"
    )
    exh_mod = importlib.util.module_from_spec(exh_spec)
    import sys as _sys

    _sys.modules[exh_spec.name] = exh_mod
    exh_spec.loader.exec_module(exh_mod)
    basis_elem_g1 = exh_mod.basis_elem_g1
    basis_elem_g2 = exh_mod.basis_elem_g2

    # build br_l2 and br_fibers using the same bad9 mapping as other tools
    toe_mod = toe
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe_mod.E6Projector(e6_basis)
    all_triads = toe_mod._load_signed_cubic_triads()

    # detect bad9 via known artifact or linfty helper
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
    if not bad9:
        try:
            linfty_mod = _load_module(
                ROOT / "tools" / "build_linfty_firewall_extension.py", "linfty_mod"
            )
            bad9 = linfty_mod._load_bad9()
        except Exception:
            pass

    br_l2 = toe_mod.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )

    fiber_triads = [t for t in all_triads if tuple(sorted(t[:3])) in bad9]
    br_fibers = [
        toe_mod.E8Z3Bracket(
            e6_projector=proj,
            cubic_triads=[T],
            scale_g1g1=1.0,
            scale_g2g2=-1.0 / 6.0,
            scale_e6=1.0,
            scale_sl3=1.0 / 6.0,
        )
        for T in fiber_triads
    ]

    # basis elements
    x = basis_elem_g1(toe_mod, tuple(a_idx))
    y = basis_elem_g1(toe_mod, tuple(b_idx))
    z = basis_elem_g2(toe_mod, tuple(c_idx))

    J = toe_mod._jacobi(br_l2, x, y, z)
    Jflat = flatten(J)

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

    if len(S_flats) == 0:
        return {
            "J_norm_max": float(np.max(np.abs(Jflat))) if Jflat.size else 0.0,
            "degenerate": True,
            "note": "S_flats empty or zero; H^3 restricted nontrivial (obstruction)",
            "overlaps": [],
            "rank_A_real": 0,
            "rank_augmented_real": 0,
            "snf_map": {},
        }

    A_real = np.vstack([np.real(np.array(S_flats)).T, np.imag(np.array(S_flats)).T])
    b_real = -np.concatenate([np.real(Jflat), np.imag(Jflat)])

    rank_A = int(np.linalg.matrix_rank(A_real)) if A_real.size else 0
    rank_aug = (
        int(np.linalg.matrix_rank(np.column_stack([A_real, b_real])))
        if A_real.size
        else 0
    )
    overlaps = [float(np.vdot(S, Jflat)) for S in S_flats]

    # SNF rational-denominator membership checks
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
            rankM = int(np.linalg.matrix_rank(M_int))
            rankAug = int(np.linalg.matrix_rank(np.column_stack([M_int, b_int])))

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
                "snf_solvable_integer_combination_with_denominator": bool(solvable),
                "U_times_b": U_times_b,
                "divisibility_checks": divisibility,
            }
        except Exception as e:
            snf_map[str(D)] = {"error": str(e)}

    # cohomology dimension estimate (restricted)
    dim_RHS = len(b_real)
    dim_image = rank_A
    dim_H3_restricted = max(0, dim_RHS - dim_image)

    return {
        "J_norm_max": float(np.max(np.abs(Jflat))),
        "degenerate": False,
        "note": "Computed restricted CE H^3 diagnostics",
        "overlaps": overlaps,
        "rank_A_real": rank_A,
        "rank_augmented_real": rank_aug,
        "dim_H3_restricted": int(dim_H3_restricted),
        "snf_map": snf_map,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sector",
        default=None,
        help="Sector name from exhaustive artifact (e.g. g1_g1_g2)",
    )
    args = parser.parse_args()

    if not EXH.exists():
        raise RuntimeError(
            "exhaustive_homotopy_rationalized_l3.json missing; run tools/exhaustive_homotopy_check_rationalized_l3.py first"
        )

    data = json.loads(EXH.read_text(encoding="utf-8"))
    sectors = data.get("sectors", {})

    # find target sectors to analyze
    targets = []
    if args.sector:
        if args.sector not in sectors:
            raise RuntimeError(f"Sector {args.sector} not found in exhaustive artifact")
        if not sectors[args.sector].get("passed", True):
            first = sectors[args.sector].get("first_fail")
            targets.append((args.sector, first))
    else:
        for sname, info in sectors.items():
            if not info.get("passed", True):
                first = info.get("first_fail")
                targets.append((sname, first))

    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")

    out = {"exhaustive_artifact": str(EXH), "results": {}}
    for sector_name, first in targets:
        if not first:
            continue
        a = tuple(first["a"])
        b = tuple(first["b"])
        c = tuple(first["c"])
        print(f"Analyzing sector {sector_name} triple {a},{b},{c}...")
        res = analyze_triple(toe, a, b, c)
        out["results"][sector_name] = {
            "triple": {"a": a, "b": b, "c": c},
            "analysis": res,
        }

    outpath = OUT_DIR / "restricted_ce_h3_results.json"
    outpath.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote:", outpath)


if __name__ == "__main__":
    main()
