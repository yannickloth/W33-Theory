#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toe)
sys.path.insert(0, str(ROOT))
from tools.build_linfty_firewall_extension import LInftyE8Extension

_e6 = np.load(ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy").astype(
    np.complex128
)
proj = toe.E6Projector(_e6)
all_triads = toe._load_signed_cubic_triads()
rat = json.loads(
    (ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json").read_text()
)
bad9 = set(tuple(sorted(t)) for t in rat["original"]["fiber_triads"])
linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)


def basis_elem_g1(idx):
    i, j = idx
    e = toe.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe.E8Z3(e6=e.e6, sl3=e.sl3, g1=arr, g2=e.g2)


# triple to persist
A = (0, 0)
B = (1, 1)
C = (21, 2)
x = basis_elem_g1(A)
y = basis_elem_g1(B)
z = basis_elem_g1(C)
res = linfty.compute_local_ce2_alpha_for_triple(
    x, y, z, return_uv=True, rationalize_uv=True, max_den=240
)
if res is None:
    print("No rational CE2 found; abort")
    raise SystemExit(1)
alpha, U_flat, V_flat, U_rats, V_rats = res
key = f"{A[0]},{A[1]}:{B[0]},{B[1]}:{C[0]},{C[1]}"
ce2p = ROOT / "artifacts" / "ce2_rational_local_solutions.json"
ce2 = json.loads(ce2p.read_text(encoding="utf-8")) if ce2p.exists() else {}
ce2[key] = {
    "a": A,
    "b": B,
    "c": C,
    "U_norm": float(np.linalg.norm(U_flat)),
    "V_norm": float(np.linalg.norm(V_flat)),
    "U_rats": [str(r) if r is not None else "0" for r in U_rats],
    "V_rats": [str(r) if r is not None else "0" for r in V_rats],
}
ce2p.write_text(json.dumps(ce2, indent=2), encoding="utf-8")
print("Persisted CE2 entry for", key)
