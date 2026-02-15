#!/usr/bin/env python3
"""Retry CP‑SAT for Klein-derived candidates using exact-scale + larger numerator bounds.

- Loads `artifacts/klein_seeded_hybrid_results.json` and re-runs
  `cp_sat_try_for_support` for entries with `cp_found=True` and nonzero numerators.
- Tries the computed exact scale first (if available), with an increased
  `MAX_NUM_FACTOR` to expand numerator bounds, then falls back to previous
  `SCALE_CHOICES` if needed.
- Uses full-row system (A, -Jflat) so returned candidates satisfy the same
  linear system used by `verify_candidate_numeric`.
- If a candidate verifies numerically, persists `artifacts/hybrid_linfty_candidate.json`.

Run: python tools/retest_failed_klein_candidates.py
"""
from __future__ import annotations

import importlib.util
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "artifacts" / "klein_seeded_hybrid_results.json"
OUT_CAND = ROOT / "artifacts" / "hybrid_linfty_candidate_from_klein.json"

if not RES.exists():
    raise SystemExit(
        "No klein_seeded_hybrid_results.json found — run tools/seed_from_klein.py first"
    )

data = json.loads(RES.read_text(encoding="utf-8"))

# import hybrid helpers
spec = importlib.util.spec_from_file_location(
    "hybrid_linfty_search", ROOT / "tools" / "hybrid_linfty_search.py"
)
hybrid = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(hybrid)

# load toe and build br_L2/br_fibers
toe_spec = importlib.util.spec_from_file_location(
    "toe_e8_mod", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(toe_spec)
assert toe_spec and toe_spec.loader
toe_spec.loader.exec_module(toe)

from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

# prepare br_l2 and br_fibers (same as hybrid main)
e6_basis = np.load(
    ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
).astype(np.complex128)
proj = toe.E6Projector(e6_basis)
all_triads = toe._load_signed_cubic_triads()
bad9_set = set(
    tuple(sorted(t[:3]))
    for t in json.loads(
        (
            ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
        ).read_text(encoding="utf-8")
    )["original"]["fiber_triads"]
)

br_l2 = toe.E8Z3Bracket(
    e6_projector=proj,
    cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9_set],
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
    for T in [t for t in all_triads if tuple(sorted(t[:3])) in bad9_set]
]

# failing triple (canonical)
exh = json.loads(
    (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text(
        encoding="utf-8"
    )
)
sector = exh.get("sectors", {}).get("g1_g1_g2", {})
fails = sector.get("failing_examples") or (
    [sector.get("first_fail")] if sector.get("first_fail") else []
)
if not fails or not fails[0]:
    raise SystemExit("No failing triple recorded to target.")
ft = fails[0]
x = basis_elem_g1(toe, tuple(ft["a"]))
y = basis_elem_g1(toe, tuple(ft["b"]))
z = basis_elem_g2(toe, tuple(ft["c"]))

# build full S/J
A_full, Jflat = hybrid.make_S_matrix_and_J(toe, br_l2, br_fibers, x, y, z)
# we'll pass full rhs (no row restriction) — cp_sat will ignore zero rows
rhs_full = -Jflat

# helper: compute exact scale used by hybrid


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
            denom_A = (denom_A * f.denominator) // math.gcd(denom_A, f.denominator)
        denom_rhs = 1
        for f in r_fracs:
            denom_rhs = (denom_rhs * f.denominator) // math.gcd(
                denom_rhs, f.denominator
            )
        rhs_div = 1
        if denom_rhs != 0:
            rhs_div = denom_rhs // math.gcd(denom_rhs, D)
        if denom_A == 0:
            exact_scale = rhs_div
        elif rhs_div == 0:
            exact_scale = denom_A
        else:
            exact_scale = (denom_A * rhs_div) // math.gcd(denom_A, rhs_div)
        if exact_scale > 0 and exact_scale < 10**9:
            return int(exact_scale)
    except Exception:
        return None
    return None


# collect candidates to retest
failed_recs = []
for rec in data.get("results", []):
    if not rec.get("cp_found"):
        continue
    nums = rec.get("nums") or []
    if all(int(n) == 0 for n in nums):
        continue
    failed_recs.append(rec)

print(
    f"Retrying {len(failed_recs)} Klein-derived CP candidates with exact-scale tests..."
)

verified = []
for rec in failed_recs:
    support = rec["support"]
    D_found = rec.get("D")
    print(
        "\nRetesting support",
        support,
        "D_found=",
        D_found,
        "original nums=",
        rec.get("nums"),
    )

    # compute exact scale for the given D (if possible)
    A_sub = A_full[:, support]
    rhs_eff = rhs_full - A_sub.dot(np.ones(len(support)) * (1.0 / 9.0))
    exact_scale = compute_exact_scale(A_sub, rhs_eff, D_found if D_found else 1)
    print("  computed exact_scale =", exact_scale)

    # try exact_scale first (if available), then fallback scales
    trial_scales = []
    if exact_scale:
        trial_scales.append(exact_scale)
    trial_scales += [s for s in hybrid.SCALE_CHOICES if s not in trial_scales]

    # temporarily raise numerator bound while retesting
    old_max = hybrid.MAX_NUM_FACTOR
    hybrid.MAX_NUM_FACTOR = max(old_max, 6.0)

    found_any = False
    A_sub = A_full[:, support]
    for sc in trial_scales:
        # try both baseline (delta) and full-coeff
        for baseline_mode in (True, False):
            baseline_vec = (
                (np.ones(len(support)) * (1.0 / 9.0)) if baseline_mode else None
            )
            print(
                f"   trying scale={sc}, baseline={'delta' if baseline_mode else 'full-coeff'}"
            )
            D_try, scale_try, nums_try = hybrid.cp_sat_try_for_support(
                A_sub,
                rhs_full,
                support,
                [D_found] if D_found else hybrid.D_LIST,
                [sc],
                120.0,
                verbose=False,
                baseline=baseline_vec,
            )
            if D_try is None:
                print("    no solution at this scale/mode")
                continue

            print("    cp_sat returned D,scale,nums =", (D_try, scale_try, nums_try))
            # build full candidate and verify numerically
            cand = [1.0 / 9.0] * A_full.shape[1]
            for j, idx in enumerate(support):
                cand[idx] = 1.0 / 9.0 + float(nums_try[j]) / float(D_try)
            ok, mag = hybrid.verify_candidate_numeric(
                toe, br_l2, br_fibers, x, y, z, cand, samples=160
            )
            print(f"    numeric verify -> {ok}, residual={mag:.3e}")
            if ok:
                print("    -> VERIFIED candidate from Klein-derived support", support)
                verified.append(
                    {
                        "support": support,
                        "D": D_try,
                        "scale": scale_try,
                        "nums": nums_try,
                        "residual": mag,
                    }
                )
                # persist artifact
                cand_record = {
                    "rationalized_coeffs": [
                        str(Fraction(c).limit_denominator(720)) for c in cand
                    ],
                    "rationalized_coeffs_float": [float(c) for c in cand],
                    "origin": "klein_seeder_retest",
                }
                OUT_CAND.write_text(json.dumps(cand_record, indent=2), encoding="utf-8")
                found_any = True
                break
        if found_any:
            break

    hybrid.MAX_NUM_FACTOR = old_max
    if not found_any:
        print("  no verified candidate found for this support")

print("\nRetest complete. Verified candidates:", verified)
