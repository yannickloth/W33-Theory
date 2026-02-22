#!/usr/bin/env python3
"""Try to rationalize LSQ solutions for top supports (baseline & full‑coeff).

- Enumerates supports up to `MAX_SUPPORT` (reads `tools/hybrid_linfty_search.py`)
- For each support with small LSQ residual, tries denominators from `D_LIST`
  to see if `c_i` can be written exactly as `baseline + num/D` (or `num/D` when
  doing full-coeff search).
- Runs `verify_candidate_numeric` for any rational candidate found and
  persists any verified candidate to `artifacts/hybrid_linfty_candidate_rationalized.json`.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "hybrid_linfty_candidate_rationalized.json"

# import hybrid utilities
spec = importlib.util.spec_from_file_location(
    "hybrid_linfty_search", ROOT / "tools" / "hybrid_linfty_search.py"
)
hybrid = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(hybrid)

# load toe & helpers
toe_spec = importlib.util.spec_from_file_location(
    "toe_e8_mod", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(toe_spec)
assert toe_spec and toe_spec.loader
toe_spec.loader.exec_module(toe)
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

# prepare br_l2/br_fibers
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

# failing triple
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

# build S/J
A, Jflat = hybrid.make_S_matrix_and_J(toe, br_l2, br_fibers, x, y, z)
# reduced rows where |Jflat| > tol
nz = np.where(np.abs(Jflat) > 1e-12)[0]
A_subrows = A[nz]
rhs_sub = -Jflat[nz]

# enumerate supports (up to hybrid.MAX_SUPPORT)
idxs = list(range(A.shape[1]))
supports = []
for k in range(1, hybrid.MAX_SUPPORT + 1):
    for comb in itertools.combinations(idxs, k):
        full_coeffs, res = hybrid.lsq_on_support(A, Jflat, list(comb))
        supports.append(
            {"support": list(comb), "lsq_coeffs": full_coeffs, "residual": res}
        )

# sort by residual
supports.sort(key=lambda s: s["residual"])

# try to rationalize top supports (both baseline and full-coeff)
results = []
for s in supports[: hybrid.TOP_K]:
    support = s["support"]
    sol_full = s["lsq_coeffs"]
    res = s["residual"]
    entry = {"support": support, "lsq_residual": res, "rationalizations": []}

    # try baseline-mode rationalization first (search for nums such that c = 1/9 + num/D)
    for mode in ("baseline", "full"):
        if mode == "baseline":
            baseline = 1.0 / 9.0
            vals = [sol_full[idx] - baseline for idx in support]
        else:
            baseline = 0.0
            vals = [sol_full[idx] for idx in support]

        for D in hybrid.D_LIST:
            nums = [int(round(v * D)) for v in vals]
            # quick capacity check
            max_num = int(math.floor(hybrid.MAX_NUM_FACTOR * D)) if D >= 5 else D
            if any(abs(n) > max_num for n in nums):
                continue
            # build candidate coeffs
            cand = [1.0 / 9.0] * A.shape[1]
            for j, idx in enumerate(support):
                cand[idx] = baseline + float(nums[j]) / float(D)
            # quick linear residual check on the restricted rows
            A_check = A_subrows[:, support]
            rhs_check = -Jflat[nz] - (
                A_subrows.dot(np.ones(A.shape[1]) * (1.0 / 9.0))
                if mode == "baseline"
                else 0.0
            )
            delta = np.array(
                [
                    cand[idx] - (1.0 / 9.0 if mode == "baseline" else 0.0)
                    for idx in support
                ]
            )
            lin_res = float(np.linalg.norm(A_check.dot(delta) + rhs_check))
            if lin_res > 1e-9:
                continue
            # numeric verify (full check)
            ok, mag = hybrid.verify_candidate_numeric(
                toe, br_l2, br_fibers, x, y, z, cand, samples=160
            )
            entry["rationalizations"].append(
                {
                    "mode": mode,
                    "D": D,
                    "nums": nums,
                    "lin_res": lin_res,
                    "verified": bool(ok),
                    "residual_after": float(mag),
                }
            )
            if ok:
                OUT.write_text(
                    json.dumps(
                        {
                            "support": support,
                            "mode": mode,
                            "D": D,
                            "nums": nums,
                            "coeffs": cand,
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                print(
                    "Verified rationalized candidate for support",
                    support,
                    "mode=",
                    mode,
                    "D=",
                    D,
                )
                results.append(entry)
                break
        if any(r["verified"] for r in entry["rationalizations"]):
            break

print("Rationalization attempts complete — results for top supports:")
print(json.dumps(results, indent=2))
