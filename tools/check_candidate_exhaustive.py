#!/usr/bin/env python3
"""Run exhaustive sector checks for a candidate coefficient vector (9 entries)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    "exh_mod", ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py"
)
exh = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(exh)

# helper to build br_l2/br_fibers from project artifacts
spec_toe = importlib.util.spec_from_file_location(
    "toe_e8", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec_toe)
assert spec_toe and spec_toe.loader
spec_toe.loader.exec_module(toe)

from tools.exhaustive_homotopy_check_rationalized_l3 import make_g1_basis, make_g2_basis

# prepare br_l2/br_fibers
proj = toe.E6Projector(
    np.load(ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy").astype(
        np.complex128
    )
)
all_triads = toe._load_signed_cubic_triads()
bad9 = set(
    tuple(sorted(t))
    for t in json.loads(
        (
            ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
        ).read_text(encoding="utf-8")
    )["original"]["fiber_triads"]
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

# candidates to test (list of 9-entry coefficient vectors)
candidates = {
    "triad_0_1.0": [1.0] + [0.0] * 8,
    "triad_3_1.0": [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "triad_8_1.0": [0.0] * 8 + [1.0],
}

out = {}
for name, coeffs in candidates.items():
    print("Checking candidate:", name)
    g1_idx = make_g1_basis(toe)
    g2_idx = make_g2_basis(toe)
    res = {}
    # run the mixed sectors first (they're the known failure points)
    res["g1_g1_g2"] = exh.check_sector_g1g1g2(
        g1_idx, g2_idx, coeffs, br_l2, br_fibers, toe
    )
    print(" g1_g1_g2 ->", res["g1_g1_g2"])
    if not res["g1_g1_g2"]["passed"]:
        out[name] = res
        continue

    res["g1_g2_g2"] = exh.check_sector_g1g2g2(
        g1_idx, g2_idx, coeffs, br_l2, br_fibers, toe
    )
    print(" g1_g2_g2 ->", res["g1_g2_g2"])
    if not res["g1_g2_g2"]["passed"]:
        out[name] = res
        continue

    # mixed sectors pass — run the remaining exhaustive sectors
    res["g1_g1_g1"] = exh.check_sector_g1g1g1(g1_idx, coeffs, br_l2, br_fibers, toe)
    print(" g1_g1_g1 ->", res["g1_g1_g1"])
    if not res["g1_g1_g1"]["passed"]:
        out[name] = res
        continue

    res["g2_g2_g2"] = exh.check_sector_g2g2g2(g2_idx, coeffs, br_l2, br_fibers, toe)
    print(" g2_g2_g2 ->", res["g2_g2_g2"])

    out[name] = res

OUT = ROOT / "artifacts" / "exhaustive_candidate_checks.json"
OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
print("Wrote", OUT)
