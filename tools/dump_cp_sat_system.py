#!/usr/bin/env python3
"""Dump integer CP‑SAT linear system for a given support + D/scale/baseline.

Useful for manual inspection when CP‑SAT presolve reports infeasible.

Examples
--------
python tools/dump_cp_sat_system.py --support 0,1,2,4,6,7 --D 6 --baseline --show-cand 1/6,1/6,1/6,1/6,1/6,1/6
python tools/dump_cp_sat_system.py --support 0,1,2,4,6,7 --D 6 --scale 6 --no-baseline
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# import helpers from existing tools
import importlib.util

spec = importlib.util.spec_from_file_location(
    "hybrid", ROOT / "tools" / "hybrid_linfty_search.py"
)
hybrid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hybrid)

toe_spec = importlib.util.spec_from_file_location(
    "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(toe_spec)
toe_spec.loader.exec_module(toe)
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2


def parse_rat_list(s: str) -> List[float]:
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b) if a and b else max(a, b)


parser = argparse.ArgumentParser(
    description="Dump CP‑SAT integer linear system for a support"
)
parser.add_argument(
    "--support", required=True, help="Support indices (comma-separated), e.g. 0,1,2"
)
parser.add_argument(
    "--D",
    type=int,
    default=None,
    help="Denominator D to inspect (if omitted, iterate hybrid.D_LIST)",
)
parser.add_argument(
    "--scale",
    type=int,
    default=None,
    help="Force integer scale (otherwise script will show computed exact-scale)",
)
parser.add_argument(
    "--baseline",
    dest="baseline",
    action="store_true",
    help="Use baseline = 1/9 (search for delta)",
)
parser.add_argument(
    "--no-baseline",
    dest="baseline",
    action="store_false",
    help="Do full-coeff search (no baseline)",
)
parser.add_argument(
    "--show-cand",
    type=str,
    default=None,
    help="Comma-separated candidate coeffs for support (floats) to test against the integer system",
)
parser.add_argument(
    "--max-num-test",
    type=int,
    default=None,
    help="Test reachability with this max_num (overrides MAX_NUM_FACTOR for capacity check)",
)
parser.set_defaults(baseline=True)
args = parser.parse_args()

support = [int(x) for x in args.support.split(",") if x.strip()]

# load canonical failing triple and build A_sub/rhs_sub (same ordering as hybrid)
exh = json.loads(
    (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text()
)
sector = exh.get("sectors", {}).get("g1_g1_g2", {})
ft = sector.get("first_fail") or (sector.get("failing_examples") or [None])[0]
if not ft:
    raise SystemExit("No failing triple recorded")

x = basis_elem_g1(toe, tuple(ft["a"]))
y = basis_elem_g1(toe, tuple(ft["b"]))
z = basis_elem_g2(toe, tuple(ft["c"]))

A, Jflat = hybrid.make_S_matrix_and_J(
    toe,
    toe.E8Z3Bracket(
        e6_projector=toe.E6Projector(
            np.load(
                ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
            ).astype(np.complex128)
        ),
        cubic_triads=[
            t
            for t in toe._load_signed_cubic_triads()
            if tuple(sorted(t[:3]))
            not in set(
                tuple(sorted(t))
                for t in json.loads(
                    (
                        ROOT
                        / "artifacts"
                        / "linfty_coord_search_results_rationalized.json"
                    ).read_text(encoding="utf-8")
                )["original"]["fiber_triads"]
            )
        ],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    ),
    [
        toe.E8Z3Bracket(
            e6_projector=toe.E6Projector(
                np.load(
                    ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
                ).astype(np.complex128)
            ),
            cubic_triads=[T],
            scale_g1g1=1.0,
            scale_g2g2=-1.0 / 6.0,
            scale_e6=1.0,
            scale_sl3=1.0 / 6.0,
        )
        for T in [
            t
            for t in toe._load_signed_cubic_triads()
            if tuple(sorted(t[:3]))
            in set(
                tuple(sorted(t))
                for t in json.loads(
                    (
                        ROOT
                        / "artifacts"
                        / "linfty_coord_search_results_rationalized.json"
                    ).read_text(encoding="utf-8")
                )["original"]["fiber_triads"]
            )
        ]
    ],
    x,
    y,
    z,
)

nz = np.where(np.abs(Jflat) > 1e-12)[0]
A_sub = A[nz][:, support]
rhs_sub = -Jflat[nz]

print("\nSupport:", support)
print("Rows used (nz):", nz.tolist())
print("A_sub shape:", A_sub.shape, "rhs_sub len:", len(rhs_sub))

# candidate coeffs passed by user (for support entries only)
user_cand = None
if args.show_cand:
    user_cand = parse_rat_list(args.show_cand)
    if len(user_cand) != len(support):
        raise SystemExit("--show-cand must have same length as support")

# helper to compute exact integer scale for given D (copied from hybrid)


def compute_exact_scale(
    A_mat: np.ndarray, rhs_vec: np.ndarray, D: int
) -> Optional[int]:
    try:
        max_den = 720
        a_fracs = [
            Fraction(float(v)).limit_denominator(max_den)
            for v in A_mat.flatten()
            if abs(v) > 1e-15
        ]
        r_fracs = [
            Fraction(float(v)).limit_denominator(max_den)
            for v in rhs_vec.flatten()
            if abs(v) > 1e-15
        ]
        denom_A = 1
        for f in a_fracs:
            denom_A = lcm(denom_A, f.denominator)
        denom_rhs = 1
        for f in r_fracs:
            denom_rhs = lcm(denom_rhs, f.denominator)
        rhs_div = 1
        if denom_rhs != 0:
            rhs_div = denom_rhs // math.gcd(denom_rhs, D)
        if denom_A == 0:
            exact_scale = rhs_div
        elif rhs_div == 0:
            exact_scale = denom_A
        else:
            exact_scale = lcm(denom_A, rhs_div)
        if exact_scale > 0 and exact_scale < 10**9:
            return int(exact_scale)
    except Exception:
        return None
    return None


# choose D set to inspect
D_list = [args.D] if args.D else hybrid.D_LIST

for D in D_list:
    print("\n--- D =", D, "---")
    exact_scale = compute_exact_scale(
        A_sub,
        (
            rhs_sub
            if not args.baseline
            else (rhs_sub - A_sub.dot(np.ones(len(support)) * (1.0 / 9.0)))
        ),
        D,
    )
    print("Computed exact_scale (from rationals):", exact_scale)
    scales_to_try = (
        [args.scale] if args.scale else ([exact_scale] if exact_scale else [])
    ) + hybrid.SCALE_CHOICES

    for scale in scales_to_try:
        if scale is None:
            continue
        A_use_real = np.real(A_sub)
        rhs_eff = (
            rhs_sub
            if not args.baseline
            else (rhs_sub - A_use_real.dot(np.ones(len(support)) * (1.0 / 9.0)))
        )
        C = np.rint(scale * A_use_real).astype(np.int64)
        RHS_int = np.rint(-scale * D * rhs_eff).astype(np.int64)
        print(f"\nscale={scale}:")
        print("  #nonzero rows:", int(np.sum(np.any(C != 0, axis=1))))
        # print first few rows
        for i in range(min(6, C.shape[0])):
            print(f"   row {i:3d}: coeffs={C[i].tolist()} RHS={int(RHS_int[i])}")

        # detect rows with zero coeffs but nonzero RHS
        zero_rows = [
            i for i in range(C.shape[0]) if np.all(C[i] == 0) and RHS_int[i] != 0
        ]
        if zero_rows:
            print("  >>> rows with all-zero coeffs but nonzero RHS:", zero_rows)

        # row capacity checks (for small set of max_num values)
        max_num_list = [
            1,
            math.floor(hybrid.MAX_NUM_FACTOR * D),
            D,
            (math.floor(hybrid.MAX_NUM_FACTOR * D) * 2),
        ]
        if args.max_num_test is not None:
            max_num_list = [args.max_num_test]
        for mnum in sorted(set(max_num_list)):
            row_capacity = np.sum(np.abs(C) * mnum, axis=1)
            rhs_abs = np.abs(RHS_int)
            feasible_rows = np.where(rhs_abs <= row_capacity)[0]
            infeasible_rows = np.where(rhs_abs > row_capacity)[0]
            print(
                f"   max_num={mnum}: infeasible rows count={len(infeasible_rows)} (max rhs={int(rhs_abs.max())}, max cap={int(row_capacity.max())})"
            )
            if len(infeasible_rows) and len(infeasible_rows) < 8:
                print("    infeasible row indices sample:", infeasible_rows.tolist())

        # gcd diagnostics per row
        gcds = []
        for i in range(C.shape[0]):
            row_coeffs = [int(abs(int(v))) for v in C[i] if int(abs(int(v))) != 0]
            if not row_coeffs:
                gcds.append(None)
                continue
            g = row_coeffs[0]
            for a in row_coeffs[1:]:
                g = math.gcd(g, a)
            gcds.append(g)
        print("  sample row gcds (first 8):", gcds[:8])

        # if user supplied candidate, test it
        if user_cand is not None:
            # build full-length candidate for support
            nums_from_cand = [int(round((float(c) * D))) for c in user_cand]
            lhs = C.dot(np.array(nums_from_cand, dtype=np.int64))
            diff = lhs - RHS_int
            print("  Testing user candidate (nums from cand * D):", nums_from_cand)
            print("   max abs(lhs-RHS):", int(np.max(np.abs(diff))))
            if np.all(diff == 0):
                print("   -> candidate satisfies integer system for this scale")
            else:
                print(
                    "   -> candidate DOES NOT satisfy system (first diffs):",
                    diff[:6].tolist(),
                )

        # write JSON artifact for manual inspection
        outp = {
            "support": support,
            "D": D,
            "scale": scale,
            "C": C.tolist(),
            "RHS_int": RHS_int.tolist(),
            "rows_with_zero_coeff_but_RHS": zero_rows,
        }
        outpath = (
            ROOT
            / "artifacts"
            / f'cp_sat_system_support_{"_".join(map(str,support))}_D{D}_s{scale}.json'
        )
        outpath.write_text(json.dumps(outp, indent=2), encoding="utf-8")
        print("  wrote artifact ->", outpath)

print("\nDone.")
