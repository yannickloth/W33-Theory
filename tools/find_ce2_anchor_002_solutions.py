"""Search for local CE2 solutions (U,V) for anchor a=(0,0,2) and record them.

This tool finds triples where `a` is the g1 index corresponding to the
Heisenberg vector (0,0,2) and where the local CE2 solver finds a nontrivial
solution. It writes the discovered solutions to a JSON file.

This is intended to fill the missing anchor in the CE2 sparse solution table.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# Load E8 tools and LInfty extension (same setup as other tools)
spec = importlib.util.spec_from_file_location(
    "toe_e8", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toe)  # type: ignore

sys.path.insert(0, str(ROOT))
from tools.build_linfty_firewall_extension import LInftyE8Extension

# Load data required for the LInfty extension
proj = toe.E6Projector(
    np.load(
        ROOT
        / "artifacts"
        / "e6_27rep_basis_export"
        / "E6_basis_78.npy"
    ).astype(np.complex128)
)
all_triads = toe._load_signed_cubic_triads()
rat = json.loads((ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json").read_text())
bad9 = set(tuple(sorted(t)) for t in rat["original"]["fiber_triads"])
linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

# Helpers --------------------------------------------------------------------

def basis_elem_g1(idx: int):
    """Construct a g1 basis element from a flat index 0..80."""
    i = idx // 3
    j = idx % 3
    e = toe.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe.E8Z3(e6=e.e6, sl3=e.sl3, g1=arr, g2=e.g2)


def basis_elem_g2(idx: int):
    """Construct a g2 basis element from a flat index 0..80."""
    i = idx // 3
    j = idx % 3
    e = toe.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe.E8Z3(e6=e.e6, sl3=e.sl3, g1=e.g1, g2=arr)


def main():
    # Determine the g1 index for a=(0,0,2)
    from scripts.ce2_global_cocycle import _heisenberg_vec_maps

    e6id_to_vec, _ = _heisenberg_vec_maps()
    a_idx_candidates = [i for i, v in e6id_to_vec.items() if tuple(int(x) for x in v) == (0, 0, 2)]
    if not a_idx_candidates:
        raise SystemExit("No E6 index found for anchor (0,0,2)")
    a_idx = a_idx_candidates[0]
    print("Using a_idx", a_idx, "for anchor (0,0,2)")

    results: dict[str, Any] = {}
    count = 0
    max_records = 20

    for b_idx in range(81):
        if count >= max_records:
            break
        for c_idx in range(81):
            if count >= max_records:
                break

            x = basis_elem_g1(a_idx)
            y = basis_elem_g1(b_idx)
            z = basis_elem_g2(c_idx)

            res = linfty.compute_local_ce2_alpha_for_triple(
                x, y, z, return_uv=True, rationalize_uv=True, max_den=720
            )
            if res is None:
                continue
            alpha_fn, U_flat, V_flat, U_rats, V_rats = res
            # skip trivial solutions
            if np.linalg.norm(U_flat) < 1e-12 and np.linalg.norm(V_flat) < 1e-12:
                continue

            key = f"{a_idx},0:{b_idx},0:{c_idx},0"
            results[key] = {
                "a": [a_idx, 0],
                "b": [b_idx, 0],
                "c": [c_idx, 0],
                "U_norm": float(np.linalg.norm(U_flat)),
                "V_norm": float(np.linalg.norm(V_flat)),
                "U_rats": [str(r) for r in U_rats],
                "V_rats": [str(r) for r in V_rats],
            }
            count += 1

    out_path = ROOT / "committed_artifacts" / "ce2_anchor_002_candidates.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} candidate entries to {out_path}")


if __name__ == "__main__":
    main()
