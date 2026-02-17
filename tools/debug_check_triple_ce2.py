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

# load symbolic l4 (if present) to force _ce2_local_uv_map population
symp = ROOT / "artifacts" / "l4_symbolic_constants.json"
ce2p = ROOT / "artifacts" / "ce2_rational_local_solutions.json"
if symp.exists():
    linfty.attach_l4_from_symbolic_constants(symp)
else:
    print("No symbolic l4 present")

if ce2p.exists():
    print("CE2 artifact exists; will attach CE2 alpha via attach_ce2_alpha")
    ce2 = json.loads(ce2p.read_text(encoding="utf-8"))
    # build alpha_global (same as other scripts)
    from fractions import Fraction

    def flat_to_e8(vec_flat):
        N = 27 * 27
        e6 = vec_flat[:N].reshape((27, 27)).astype(np.complex128)
        off = N
        sl3 = vec_flat[off : off + 9].reshape((3, 3)).astype(np.complex128)
        off += 9
        g1 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
        off += 81
        g2 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
        return toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)

    def alpha_global(a, b):
        acc = toe.E8Z3.zero()
        for k, e in ce2.items():
            a_idx = tuple(e["a"])
            b_idx = tuple(e["b"])
            c_idx = tuple(e["c"])
            U_rats = [Fraction(s) if s != "0" else None for s in e.get("U_rats", [])]
            V_rats = [Fraction(s) if s != "0" else None for s in e.get("V_rats", [])]
            U_num = np.array(
                [float(fr) if fr is not None else 0.0 for fr in U_rats],
                dtype=np.complex128,
            )
            V_num = np.array(
                [float(fr) if fr is not None else 0.0 for fr in V_rats],
                dtype=np.complex128,
            )
            U_e8 = flat_to_e8(U_num)
            V_e8 = flat_to_e8(V_num)
            # matching logic (conservative)
            if np.allclose(a.g1, toe.E8Z3.zero().g1) and np.allclose(
                b.g2, toe.E8Z3.zero().g2
            ):
                pass
            # match by identity
            if np.allclose(a.g1, toe.E8Z3.zero().g1) and np.allclose(
                b.g2, toe.E8Z3.zero().g2
            ):
                continue
            if np.allclose(a.g1, toe.E8Z3.zero().g1) and np.allclose(
                b.g2, toe.E8Z3.zero().g2
            ):
                continue
            # consistent with assemble logic
            if np.allclose(a.g1, toe.E8Z3.zero().g1) and np.allclose(
                b.g2, toe.E8Z3.zero().g2
            ):
                continue
        return acc

    # attach CE2 alpha (so d_alpha_on_triple can prefer per-triple map if set)
    linfty.attach_ce2_alpha(lambda a, b: toe.E8Z3.zero())
else:
    print("No CE2 artifact present")

# examine whether LInfty instance has _ce2_local_uv_map
has_map = hasattr(linfty, "_ce2_local_uv_map") and linfty._ce2_local_uv_map is not None
print("linfty has _ce2_local_uv_map =", has_map)
if has_map:
    print("Number of per-triple entries:", len(linfty._ce2_local_uv_map))

# inspect specific triple
A = (0, 0)
B = (1, 1)
C = (21, 2)
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1

x = basis_elem_g1(toe, A)
y = basis_elem_g1(toe, B)
z = basis_elem_g1(toe, C)
# raw Jacobi
j = toe._jacobi(linfty.br_l2, x, y, z)
mag_j = max(
    [float(np.max(np.abs(getattr(j, attr)))) for attr in ("e6", "sl3", "g1", "g2")]
)
print("mag_j =", mag_j)
# l3 contribution
l3c = linfty.l3(x, y, z)
mag_l3 = max(
    [float(np.max(np.abs(getattr(l3c, attr)))) for attr in ("e6", "sl3", "g1", "g2")]
)
print("mag_l3 =", mag_l3)
# d_alpha_on_triple
dalpha = linfty.d_alpha_on_triple(x, y, z)
mag_dalpha = max(
    [float(np.max(np.abs(getattr(dalpha, attr)))) for attr in ("e6", "sl3", "g1", "g2")]
)
print("mag_dalpha =", mag_dalpha)
# homotopy jacobi
hj = linfty.homotopy_jacobi(x, y, z)
mag_hj = max(
    [float(np.max(np.abs(getattr(hj, attr)))) for attr in ("e6", "sl3", "g1", "g2")]
)
print("mag_hj =", mag_hj)

# check whether triple present in CE2 artifact
if ce2p.exists():
    ce2 = json.loads(ce2p.read_text(encoding="utf-8"))
    key = f"{A[0]},{A[1]}:{B[0]},{B[1]}:{C[0]},{C[1]}"
    print("artifact contains key?", key in ce2)
    if key in ce2:
        e = ce2[key]
        print("U_norm,V_norm =", e.get("U_norm"), e.get("V_norm"))
        print("U_rats (first 10) =", e.get("U_rats", [])[:10])

print("\nDone")
