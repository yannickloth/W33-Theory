#!/usr/bin/env python3
"""Verify the promoted rationalized l3 candidate for the g1_g1_g2 sector only.
Writes result to `artifacts/hybrid_linfty_candidate_verification.json`.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
OUT = ROOT / "artifacts" / "hybrid_linfty_candidate_verification.json"

# load canonical candidate
data = json.loads(IN.read_text(encoding="utf-8"))
coeffs = data.get("rationalized_coeffs_float") or data.get("original", {}).get("coeffs")
if coeffs is None:
    raise SystemExit("No rationalized candidate found in canonical artifact")

# import toe module
spec = importlib.util.spec_from_file_location(
    "toe_e8", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(toe)

# prepare projector / brackets (same as exhaustive script)
e6_basis = np.load(
    ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
).astype(np.complex128)
proj = toe.E6Projector(e6_basis)
all_triads = toe._load_signed_cubic_triads()
bad9 = set(tuple(sorted(t)) for t in data.get("original", {}).get("fiber_triads", []))

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

# basis indices
from tools.exhaustive_homotopy_check_rationalized_l3 import (
    check_sector_g1g1g2,
    make_g1_basis,
    make_g2_basis,
)

g1_idx = make_g1_basis(toe)
g2_idx = make_g2_basis(toe)

print("Running focused exhaustive check for sector g1_g1_g2...")
res = check_sector_g1g1g2(g1_idx, g2_idx, coeffs, br_l2, br_fibers, toe)
print("Result:", res)

OUT.write_text(
    json.dumps({"sector": "g1_g1_g2", "result": res}, indent=2), encoding="utf-8"
)
print("Wrote", OUT)
