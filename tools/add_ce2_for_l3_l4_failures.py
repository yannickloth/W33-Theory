#!/usr/bin/env python3
"""Compute and append CE2 local solutions for triples reported by
`artifacts/exhaustive_homotopy_l3_l4.json` (quick verifier output).

For each sector with a `first_fail`, compute a rationalized U/V via
`LInftyE8Extension.compute_local_ce2_alpha_for_triple` and append an entry
to `artifacts/ce2_rational_local_solutions.json` (skipping duplicates).

This avoids running the expensive full assembler when only a handful of
mixed-sector triples remain.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXH = ROOT / "artifacts" / "exhaustive_homotopy_l3_l4.json"
CE2 = ROOT / "artifacts" / "ce2_rational_local_solutions.json"

if not EXH.exists():
    raise SystemExit("Run tools/run_quick_exhaustive_l3_l4.py first")

exh = json.loads(EXH.read_text(encoding="utf-8"))

# collect failing triples from sectors
fails = []
for sec in ("g1_g1_g2", "g1_g2_g2"):
    f = exh.get("sectors", {}).get(sec, {}).get("first_fail")
    if f:
        fails.append((sec, tuple(f["a"]), tuple(f["b"]), tuple(f["c"])))

if not fails:
    print("No failing triples recorded in exhaustive_homotopy_l3_l4.json")
    raise SystemExit(0)

# load toe and linfty
spec = importlib.util.spec_from_file_location(
    "toe_e8", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toe)  # type: ignore

sys.path.insert(0, str(ROOT))
from tools.build_linfty_firewall_extension import LInftyE8Extension

proj = toe.E6Projector(
    np.load(ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy").astype(
        np.complex128
    )
)
all_triads = toe._load_signed_cubic_triads()
rat = json.loads(
    (ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json").read_text()
)
bad9 = set(tuple(sorted(t)) for t in rat["original"]["fiber_triads"])
linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

# helper constructors


def basis_elem_g1(idx: Tuple[int, int]):
    i, j = idx
    e = toe.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe.E8Z3(e6=e.e6, sl3=e.sl3, g1=arr, g2=e.g2)


def basis_elem_g2(idx: Tuple[int, int]):
    i, j = idx
    e = toe.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe.E8Z3(e6=e.e6, sl3=e.sl3, g1=e.g1, g2=arr)


# load existing CE2 artifact (or start new)
if CE2.exists():
    ce2_data: Dict[str, Any] = json.loads(CE2.read_text(encoding="utf-8"))
else:
    ce2_data = {}

added = []
for sec, a_idx, b_idx, c_idx in fails:
    print("Processing failing triple for sector", sec, a_idx, b_idx, c_idx)
    x = basis_elem_g1(a_idx)
    y = basis_elem_g1(b_idx)
    z = basis_elem_g2(c_idx)

    # skip if already present in artifact (match by indices)
    key = f"{a_idx[0]},{a_idx[1]}:{b_idx[0]},{b_idx[1]}:{c_idx[0]},{c_idx[1]}"
    if key in ce2_data:
        print("  -> already present in CE2 artifact; skipping")
        continue

    res = linfty.compute_local_ce2_alpha_for_triple(
        x, y, z, return_uv=True, rationalize_uv=True, max_den=720
    )
    if res is None:
        print("  -> local CE2 solver failed on triple", (a_idx, b_idx, c_idx))
        continue
    alpha_fn, U_flat, V_flat, U_rats, V_rats = res

    ce2_data[key] = {
        "a": a_idx,
        "b": b_idx,
        "c": c_idx,
        "U_norm": float(np.linalg.norm(U_flat)),
        "V_norm": float(np.linalg.norm(V_flat)),
        "U_rats": [str(r) if r is not None else "0" for r in U_rats],
        "V_rats": [str(r) if r is not None else "0" for r in V_rats],
    }
    added.append(key)

# persist updated artifact (merge)
if added:
    CE2.write_text(json.dumps(ce2_data, indent=2), encoding="utf-8")
    print("Appended CE2 entries for:")
    for k in added:
        print("  -", k)
else:
    print("No new CE2 entries added")

print("Done")
