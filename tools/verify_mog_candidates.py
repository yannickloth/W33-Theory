#!/usr/bin/env python3
"""Verify CP‑SAT candidates produced by `tools/seed_hybrid_from_mog_hexads.py`.
Prints which candidates pass `verify_candidate_numeric`.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RES_FILE = ROOT / "artifacts" / "mog_hexads_seeded_hybrid_results.json"
if not RES_FILE.exists():
    raise SystemExit("No mog_hexads_seeded_hybrid_results.json artifact found")

parser = argparse.ArgumentParser()
parser.add_argument("--samples", type=int, default=160)
args = parser.parse_args()

data = json.loads(RES_FILE.read_text(encoding="utf-8"))

# import hybrid helpers
spec = importlib.util.spec_from_file_location(
    "hybrid_linfty_search", ROOT / "tools" / "hybrid_linfty_search.py"
)
hybrid = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(hybrid)

# import toe and build br_l2/br_fibers (same as hybrid/seed helpers)
toe_spec = importlib.util.spec_from_file_location(
    "toe_e8_mod", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(toe_spec)
assert toe_spec and toe_spec.loader
toe_spec.loader.exec_module(toe)

from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

# prepare br_l2 and br_fibers (copied from hybrid.main)
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

# pick failing triple from exhaustive artifact
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

passed = []
for rec in data.get("results", []):
    if not rec.get("cp_found"):
        continue
    nums = rec.get("nums") or []
    D = rec.get("D")
    if all(int(n) == 0 for n in nums):
        continue
    support = rec["support"]
    cand = [1.0 / 9.0] * 9
    for j, idx in enumerate(support):
        cand[idx] = 1.0 / 9.0 + float(nums[j]) / float(D)
    ok, mag = hybrid.verify_candidate_numeric(
        toe, br_l2, br_fibers, x, y, z, cand, samples=args.samples
    )
    print(f"Support={support} D={D} nums={nums} -> verified={ok} residual={mag:.3e}")
    if ok:
        passed.append({"support": support, "D": D, "nums": nums, "residual": mag})

print("\nVerified candidates:", passed)
