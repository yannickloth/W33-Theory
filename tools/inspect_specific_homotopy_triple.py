"""Inspect a specific homotopy triple (print J, l3, d_alpha, l4 coboundary, homotopy residual).

Usage: run this script from the repo root; it prints g1 norms and nonzero indices.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# load helpers
spec_build = importlib.util.spec_from_file_location(
    "build_linfty", ROOT / "tools" / "build_linfty_firewall_extension.py"
)
build = importlib.util.module_from_spec(spec_build)
spec_build.loader.exec_module(build)

spec_toe = importlib.util.spec_from_file_location(
    "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec_toe)
spec_toe.loader.exec_module(toe)

# projector + linfty
_e6 = np.load(ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy").astype(
    np.complex128
)
proj = toe.E6Projector(_e6)
all_triads = toe._load_signed_cubic_triads()
rat = json.loads(
    (ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json").read_text()
)
bad9 = set(tuple(sorted(t)) for t in rat["original"]["fiber_triads"])
linfty = build.LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

# attach symbolic l4 + CE2 if present
symp = ROOT / "artifacts" / "l4_symbolic_constants.json"
if symp.exists():
    linfty.attach_l4_from_symbolic_constants(symp)

# helpers from exhaustive module
spec_exh = importlib.util.spec_from_file_location(
    "exh", ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py"
)
exh = importlib.util.module_from_spec(spec_exh)
spec_exh.loader.exec_module(exh)


# inspect triple
def flat_g1_indices(arr):
    res = []
    g1 = arr.g1
    nz = np.argwhere(np.abs(g1) > 1e-12)
    for r in nz:
        i, j = int(r[0]), int(r[1])
        res.append((i, j, float(g1[i, j])))
    return res


# failing triple (modify as needed)
TRIPLE_A = (0, 0)
TRIPLE_B = (17, 1)
TRIPLE_C = (3, 1)

x = exh.basis_elem_g1(toe, TRIPLE_A)
y = exh.basis_elem_g1(toe, TRIPLE_B)
z = exh.basis_elem_g2(toe, TRIPLE_C)

J = toe._jacobi(linfty.br_l2, x, y, z)
print("Jacobi(l2).g1 nonzero entries:", flat_g1_indices(J))
print("||Jacobi(l2).g1|| =", float(np.max(np.abs(J.g1))))

l3v = linfty.l3(x, y, z)
print("l3(x,y,z).g1 nonzero entries:", flat_g1_indices(l3v))
print("||l3.g1|| =", float(np.max(np.abs(l3v.g1))))

# alpha/d_alpha
if hasattr(linfty, "_ce2_alpha") and linfty._ce2_alpha is not None:
    U = linfty._ce2_alpha(y, z)
    V = linfty._ce2_alpha(x, z)
else:
    U = linfty.d_alpha_on_triple(y, z, x)  # fallback (not expected)
    V = linfty.d_alpha_on_triple(x, z, y)

print("alpha(y,z)=U nonzero g1 entries:", flat_g1_indices(U))
print("alpha(x,z)=V nonzero g1 entries:", flat_g1_indices(V))
print(
    "||U||, ||V|| =",
    float(np.max(np.abs(U.g1))) if U.g1.size else 0.0,
    float(np.max(np.abs(V.g1))) if V.g1.size else 0.0,
)

# coboundary terms and homotopy
term1 = linfty.br_l2.bracket(x, U)
term2 = linfty.br_l2.bracket(y, V).scale(-1.0)
term3 = linfty.br_l2.bracket(
    z, linfty._ce2_alpha(x, y) if hasattr(linfty, "_ce2_alpha") else toe.E8Z3.zero()
)
print("term1 g1 nonzero:", flat_g1_indices(term1))
print("term2 g1 nonzero:", flat_g1_indices(term2))
print("term3 g1 nonzero:", flat_g1_indices(term3))

# total
tot = linfty.homotopy_jacobi(x, y, z)
print("homotopy_jacobi.g1 nonzero indices:", flat_g1_indices(tot))
print("||homotopy_jacobi.g1|| =", float(np.max(np.abs(tot.g1))))
