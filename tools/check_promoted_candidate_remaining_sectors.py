#!/usr/bin/env python3
"""Run exhaustive checks for remaining sectors (g2_g2_g2 and g1_g2_g2)
for the promoted rationalized l3 candidate and write a verification report.
"""
from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

# make project root importable so `from tools...` works when run as a script
sys.path.insert(0, str(ROOT))
IN = ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
OUT = ROOT / "artifacts" / "hybrid_linfty_candidate_verification.json"

data = json.loads(IN.read_text(encoding="utf-8"))
coeffs = data.get("rationalized_coeffs_float") or data.get("original", {}).get("coeffs")
if coeffs is None:
    raise SystemExit("No rationalized candidate found in canonical artifact")

# import toe and the sector check helpers
spec = importlib.util.spec_from_file_location(
    "toe_e8", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(toe)

# prepare br_l2/br_fibers (same construction as other helpers)
import numpy as np

from tools.exhaustive_homotopy_check_rationalized_l3 import (
    check_sector_g1g1g2,
    check_sector_g1g2g2,
    check_sector_g2g2g2,
    make_g1_basis,
    make_g2_basis,
)

proj = toe.E6Projector(
    np.load(ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy").astype(
        np.complex128
    )
)
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
g1_idx = make_g1_basis(toe)
g2_idx = make_g2_basis(toe)

report = {"candidate": coeffs, "sectors": {}}
start = time.time()
print("Running g2_g2_g2 sector (exhaustive)...")
res_g2 = check_sector_g2g2g2(g2_idx, coeffs, br_l2, br_fibers, toe)
report["sectors"]["g2_g2_g2"] = res_g2
print("  ->", res_g2)

print("Running g1_g1_g2 sector (exhaustive)...")
res_g1g1g2 = check_sector_g1g1g2(g1_idx, g2_idx, coeffs, br_l2, br_fibers, toe)
report["sectors"]["g1_g1_g2"] = res_g1g1g2
print("  ->", res_g1g1g2)

print("Running g1_g2_g2 sector (exhaustive)...")
res_g1g2g2 = check_sector_g1g2g2(g1_idx, g2_idx, coeffs, br_l2, br_fibers, toe)
report["sectors"]["g1_g2_g2"] = res_g1g2g2
print("  ->", res_g1g2g2)

report["elapsed_sec"] = time.time() - start
OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print("Wrote", OUT)
