#!/usr/bin/env python3
"""Debug a single CP‑SAT support with verbose logging.

This script rebuilds the S/J matrices for the canonical failing triple
and runs `cp_sat_try_for_support(..., verbose=True)` on the supplied support.

Usage examples:
  python tools/debug_cp_sat_support.py --support 6 --time 30
  python tools/debug_cp_sat_support.py --support 6,7,8 --time 60
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# import hybrid helpers
spec = importlib.util.spec_from_file_location(
    "hybrid_linfty_search", ROOT / "tools" / "hybrid_linfty_search.py"
)
hybrid = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(hybrid)

# import toe module
toe_spec = importlib.util.spec_from_file_location(
    "toe_e8_mod", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(toe_spec)
assert toe_spec and toe_spec.loader
toe_spec.loader.exec_module(toe)

parser = argparse.ArgumentParser(description="Debug CP-SAT on one seeded support")
parser.add_argument(
    "--support", required=False, help="Support indices (comma-separated), default: 6"
)
parser.add_argument(
    "--time", type=float, default=30.0, help="CP-SAT time limit (seconds)"
)
args = parser.parse_args()

support_str = args.support or "6"
support_idx = [int(s.strip()) for s in support_str.split(",") if s.strip()]

# load canonical data (same sources as seed_hybrid_from_pg32)
bad9 = json.loads((ROOT / "artifacts" / "firewall_bad_triads_mapping.json").read_text())

# prepare br_l2 and br_fibers (copied from hybrid.main / seed helper)
e6_basis = np.load(
    ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
).astype(np.complex128)
proj = toe.E6Projector(e6_basis)
all_triads = toe._load_signed_cubic_triads()

# determine "bad9" set from canonical rationalized search artifact (matches hybrid.main)
data = json.loads(
    (ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json").read_text()
)
bad9_set = set(tuple(sorted(t)) for t in data["original"]["fiber_triads"])

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

# pick failing triple from exhaustive artifact
exh = json.loads(
    (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text()
)
sector = exh.get("sectors", {}).get("g1_g1_g2", {})
fails = sector.get("failing_examples") or (
    [sector.get("first_fail")] if sector.get("first_fail") else []
)
if not fails:
    raise SystemExit("No failing triple recorded to target.")
ft = fails[0]
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

x = basis_elem_g1(toe, tuple(ft["a"]))
y = basis_elem_g1(toe, tuple(ft["b"]))
z = basis_elem_g2(toe, tuple(ft["c"]))

# build S matrix and reduced rows
A, Jflat = hybrid.make_S_matrix_and_J(toe, br_l2, br_fibers, x, y, z)
nz_rows = np.where(np.abs(Jflat) > 1e-12)[0]
A_subrows = A[nz_rows][:, support_idx]
rhs_sub = -Jflat[nz_rows]

print("Running verbose CP‑SAT on support:", support_idx)
D, scale, nums = hybrid.cp_sat_try_for_support(
    A_subrows,
    rhs_sub,
    support_idx,
    hybrid.D_LIST,
    hybrid.SCALE_CHOICES,
    args.time,
    verbose=True,
    baseline=np.ones(len(support_idx)) * (1.0 / 9.0),
)
print("Result -> D:", D, "scale:", scale, "nums:", nums)

if D is not None:
    # numeric verification
    cand = [1.0 / 9.0] * A.shape[1]
    for j, idx in enumerate(support_idx):
        cand[idx] = 1.0 / 9.0 + float(nums[j]) / float(D)
    ok, mag = hybrid.verify_candidate_numeric(toe, br_l2, br_fibers, x, y, z, cand)
    print("Verified numeric:", ok, "residual magnitude:", mag)
else:
    print("No CP‑SAT solution found for this support in the given time.")
