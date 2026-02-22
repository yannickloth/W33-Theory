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


# target triple
A = (0, 0)
B = (1, 1)
C = (21, 2)
x = basis_elem_g1(A)
y = basis_elem_g1(B)
z = basis_elem_g1(C)
print("Trying compute_local_ce2_alpha_for_triple on", A, B, C)
for max_den in (240, 720, 5040, 10000):
    print("\nmax_den=", max_den)
    try:
        res = linfty.compute_local_ce2_alpha_for_triple(
            x, y, z, return_uv=True, rationalize_uv=True, max_den=max_den
        )
    except Exception as e:
        print("  Exception during solve:", e)
        res = None
    if res is None:
        print("  -> no rationalized CE2 found (max_den=", max_den, ")")
        # try numeric
        res2 = linfty.compute_local_ce2_alpha_for_triple(
            x, y, z, return_uv=True, rationalize_uv=False, max_den=max_den
        )
        if res2 is None:
            print("   numeric solve also failed")
        else:
            alpha, U_flat, V_flat = res2
            print(
                "   numeric solve succeeded; norms U,V =",
                float(np.linalg.norm(U_flat)),
                float(np.linalg.norm(V_flat)),
            )
            # attach numeric alpha in-memory and test residual
            linfty.attach_ce2_alpha(alpha)
            linfty.attach_l4_from_ce2(alpha)
            hj = linfty.homotopy_jacobi(x, y, z)
            mag = max(
                [
                    float(np.max(np.abs(getattr(hj, attr))))
                    for attr in ("e6", "sl3", "g1", "g2")
                ]
            )
            print("   homotopy_jacobi residual after attach =", mag)
            break
    else:
        alpha, U_flat, V_flat, U_rats, V_rats = res
        print(
            "  -> rationalized CE2 found; U_norm,V_norm =",
            float(np.linalg.norm(U_flat)),
            float(np.linalg.norm(V_flat)),
        )
        # attach and test
        linfty.attach_ce2_alpha(alpha)
        linfty.attach_l4_from_ce2(alpha)
        hj = linfty.homotopy_jacobi(x, y, z)
        mag = max(
            [
                float(np.max(np.abs(getattr(hj, attr))))
                for attr in ("e6", "sl3", "g1", "g2")
            ]
        )
        print("  -> homotopy_jacobi residual after attach =", mag)
        break
print("\nDone")
