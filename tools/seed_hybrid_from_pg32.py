#!/usr/bin/env python3
"""Seed the hybrid LSQ→CP‑SAT search with supports derived from PG(3,2)/MOG.

- Builds candidate supports (indices into the 9 fiber triads) from PG(3,2)
  lines that hit the canonical 9 'bad' triads.
- Calls the CP‑SAT attempt routine from `tools/hybrid_linfty_search.py`
  on each seeded support (short time budget).
- Writes `artifacts/pg32_seeded_hybrid_results.json`.

This is conservative: it only *tests* candidate supports, it doesn't
overwrite canonical artifacts.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "pg32_seeded_hybrid_results.json"

# CLI
parser = argparse.ArgumentParser(
    description="Seed hybrid LSQ→CP‑SAT from PG(3,2) supports"
)
parser.add_argument(
    "--time", type=float, default=300.0, help="CP‑SAT time limit per support (seconds)"
)
args = parser.parse_args()

# import hybrid module (we reuse its helpers)
spec = importlib.util.spec_from_file_location(
    "hybrid_linfty_search", ROOT / "tools" / "hybrid_linfty_search.py"
)
hybrid = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(hybrid)

# load canonical data
pg32 = json.loads((ROOT / "artifacts" / "pg32_lines_from_remaining15.json").read_text())
bad9 = json.loads((ROOT / "artifacts" / "firewall_bad_triads_mapping.json").read_text())

# map Schläfli vertex -> bad9 index (0..8) when present
schlafli_to_bad9 = {}
for bi, tri in enumerate(bad9["bad_triangles_Schlafli_orbit_index"]):
    for v in tri:
        schlafli_to_bad9[v] = bi

# build supports: for each PG(3,2) line (3 Schläfli vertices) collect any
# corresponding bad9 indices — keep supports size 1..4
candidate_supports = set()
for L in pg32["lines"]:
    pts = L["points"]  # these are Schläfli vertex ids in repo convention
    support = sorted({schlafli_to_bad9[v] for v in pts if v in schlafli_to_bad9})
    if 1 <= len(support) <= 4:
        candidate_supports.add(tuple(support))

candidate_supports = sorted(candidate_supports)
print(f"Generated {len(candidate_supports)} seed supports (size<=4)")

# prepare failing triple (use first failing triple from exhaustive artifact)
exh = json.loads(
    (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text()
)
sector = exh.get("sectors", {}).get("g1_g1_g2", {})
fails = sector.get("failing_examples") or (
    [sector.get("first_fail")] if sector.get("first_fail") else []
)
if not fails or fails[0] is None:
    raise SystemExit("No failing triple recorded to target.")
ft = fails[0]
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

# import toe module (use canonical tool implementation)
toe_spec = importlib.util.spec_from_file_location(
    "toe_e8_mod", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(toe_spec)
assert toe_spec and toe_spec.loader
toe_spec.loader.exec_module(toe)

# build toe helpers (copied from hybrid.main)
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

# basis elements for failing triple (pass `toe` module)
x = basis_elem_g1(toe, tuple(ft["a"]))
y = basis_elem_g1(toe, tuple(ft["b"]))
z = basis_elem_g2(toe, tuple(ft["c"]))

# build S-matrix and J (local reimplementation, matching hybrid logic)


def flatten(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


Scols = []
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
    Scols.append(flatten(S))

A_full = np.array(Scols).T
Jflat = flatten(toe._jacobi(br_l2, x, y, z))

# reduced rows where |Jflat| > tol
nz_rows = np.where(np.abs(Jflat) > 1e-12)[0]
A_sub_full = A_full[nz_rows]
rhs_full = -Jflat[nz_rows]

# try CP-SAT on candidate supports
from tools.hybrid_linfty_search import cp_sat_try_for_support

results = []
for support in candidate_supports:
    support_idx = list(support)
    A_use = A_sub_full[:, support_idx]
    D, scale, nums = cp_sat_try_for_support(
        A_use, rhs_full, support_idx, hybrid.D_LIST, hybrid.SCALE_CHOICES, args.time
    )
    rec = {
        "support": support_idx,
        "cp_found": D is not None,
        "D": D,
        "scale": scale,
        "nums": nums,
    }
    results.append(rec)

OUT.write_text(
    json.dumps(
        {"candidate_supports": candidate_supports, "results": results}, indent=2
    ),
    encoding="utf-8",
)
print("Wrote:", OUT)
