#!/usr/bin/env python3
"""Seed hybrid LSQ→CP‑SAT from Klein/PG(3,2) plane supports.

Strategy:
- Reconstruct the 15 PG(3,2) points and 35 lines from
  `artifacts/pg32_lines_from_remaining15.json`.
- Enumerate the 7‑point Fano planes (all 7‑subsets that contain exactly
  7 lines from the PG(3,2) line set).
- Map Schläfli vertex ids -> `bad9` indices using
  `artifacts/firewall_bad_triads_mapping.json` (same mapping as
  `tools/seed_hybrid_from_pg32.py`).
- For each plane, collect the set of mapped `bad9` indices appearing in
  that plane — these are Klein‑derived candidate supports.
- Optionally try CP‑SAT on the generated supports (short budget by default)
  using `tools/hybrid_linfty_search.cp_sat_try_for_support`.

Writes: `artifacts/klein_seeded_supports.json` and (if run)
`artifacts/klein_seeded_hybrid_results.json`.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
from pathlib import Path
from typing import List, Set, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "klein_seeded_supports.json"
OUT_RESULTS = ROOT / "artifacts" / "klein_seeded_hybrid_results.json"

parser = argparse.ArgumentParser(
    description="Seed hybrid search from Klein/PG(3,2) planes"
)
parser.add_argument(
    "--time", type=float, default=60.0, help="CP‑SAT time limit per support (seconds)"
)
parser.add_argument(
    "--max-support-size",
    type=int,
    default=4,
    help="Maximum support size to keep from plane intersections",
)
parser.add_argument(
    "--try-cp",
    action="store_true",
    help="Run CP‑SAT on generated supports (short budget)",
)
args = parser.parse_args()

# load PG(3,2) lines (Schläfli vertex ids are used in points[] fields)
pg32 = json.loads(
    (ROOT / "artifacts" / "pg32_lines_from_remaining15.json").read_text(
        encoding="utf-8"
    )
)
lines = pg32["lines"]
all_points = sorted({p for L in lines for p in L["points"]})
# sanity check: expect 15 distinct points
if len(all_points) != 15:
    print("Warning: expected 15 PG(3,2) points, found", len(all_points))

# build quick lookup of which lines are contained in a given 7-subset
line_point_sets = [set(L["points"]) for L in lines]

# enumerate candidate 7-point planes (Fano planes)
planes: List[Set[int]] = []
for subset in itertools.combinations(all_points, 7):
    subset_set = set(subset)
    # count how many PG lines lie entirely inside this subset
    contained_lines = sum(1 for lp in line_point_sets if lp.issubset(subset_set))
    if contained_lines == 7:
        planes.append(subset_set)

planes = sorted(planes, key=lambda s: sorted(s))
print(f"Found {len(planes)} PG(3,2) planes (7-point Fano planes)")

# map Schläfli vertex -> bad9 index using canonical mapping in firewall_bad_triads_mapping.json
bad9 = json.loads(
    (ROOT / "artifacts" / "firewall_bad_triads_mapping.json").read_text(
        encoding="utf-8"
    )
)
schlafli_to_bad9 = {}
for bi, tri in enumerate(bad9["bad_triangles_Schlafli_orbit_index"]):
    for v in tri:
        schlafli_to_bad9[v] = bi

# build supports: for each plane, map member points -> bad9 indices (when present)
supports: Set[Tuple[int, ...]] = set()
for pl in planes:
    mapped = sorted({schlafli_to_bad9[p] for p in pl if p in schlafli_to_bad9})
    if 1 <= len(mapped) <= args.max_support_size:
        supports.add(tuple(mapped))

# dedupe and sort
candidate_supports = sorted(supports)
print(
    f"Generated {len(candidate_supports)} Klein-derived candidate supports (size<= {args.max_support_size})"
)
OUT.write_text(
    json.dumps(
        {"klein_planes_count": len(planes), "candidate_supports": candidate_supports},
        indent=2,
    ),
    encoding="utf-8",
)
print("Wrote:", OUT)

# optional CP‑SAT checks on each support (reuse hybrid.cp_sat_try_for_support)
if args.try_cp and candidate_supports:
    spec = importlib.util.spec_from_file_location(
        "hybrid_linfty_search", ROOT / "tools" / "hybrid_linfty_search.py"
    )
    hybrid = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(hybrid)

    # reconstruct the S/J matrices for the canonical failing triple
    from tools.exhaustive_homotopy_check_rationalized_l3 import (
        basis_elem_g1,
        basis_elem_g2,
    )

    toe_spec = importlib.util.spec_from_file_location(
        "toe_e8_mod", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
    )
    toe = importlib.util.module_from_spec(toe_spec)
    assert toe_spec and toe_spec.loader
    toe_spec.loader.exec_module(toe)

    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9_set = (
        set(tuple(sorted(t[:3])) for t in bad9["bad_triangles_Schlafli_e6id"])
        if "bad_triangles_Schlafli_e6id" in bad9
        else set()
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

    # build S/J matrix (reuse hybrid helper)
    A_full, Jflat = hybrid.make_S_matrix_and_J(toe, br_l2, br_fibers, x, y, z)
    nz_rows = np.where(np.abs(Jflat) > 1e-12)[0]
    A_sub_full = A_full[nz_rows]
    rhs_full = -Jflat[nz_rows]

    results = []
    for support in candidate_supports:
        support_idx = list(support)
        A_use = A_sub_full[:, support_idx]
        baseline_sub = np.ones(len(support_idx)) * (1.0 / 9.0)
        D, scale, nums = hybrid.cp_sat_try_for_support(
            A_use,
            rhs_full,
            support_idx,
            hybrid.D_LIST,
            hybrid.SCALE_CHOICES,
            args.time,
            verbose=False,
            baseline=baseline_sub,
        )
        rec = {
            "support": support_idx,
            "cp_found": D is not None,
            "D": D,
            "scale": scale,
            "nums": nums,
        }
        results.append(rec)

    OUT_RESULTS.write_text(
        json.dumps(
            {"candidate_supports": candidate_supports, "results": results}, indent=2
        ),
        encoding="utf-8",
    )
    print("Wrote:", OUT_RESULTS)

print("Done.")
