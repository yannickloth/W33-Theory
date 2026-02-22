#!/usr/bin/env python3
"""Reconstruct alpha_global by summing per-entry local alpha functions
from `artifacts/ce2_rational_local_solutions.json` (same logic as
`assemble_exact_l4_from_local_ce2.py`) and verify homotopy_jacobi for the
recorded failing triple.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def flat_rats_to_E8Z3(toe_mod, flat_rats):
    N = 27 * 27
    vec = np.zeros(len(flat_rats), dtype=np.complex128)
    for i, r in enumerate(flat_rats):
        if r is None or r == 0:
            vec[i] = 0.0
        else:
            vec[i] = float(r)
    e6 = vec[:N].reshape((27, 27))
    off = N
    sl3 = vec[off : off + 9].reshape((3, 3))
    off += 9
    g1 = vec[off : off + 81].reshape((27, 3))
    off += 81
    g2 = vec[off : off + 81].reshape((27, 3))
    return toe_mod.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)


# load modules
import sys

sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location(
    "build", ROOT / "tools" / "build_linfty_firewall_extension.py"
)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
spec2 = importlib.util.spec_from_file_location(
    "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(toe)

# setup linfty
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

# load CE2 artifact
ce2p = ROOT / "artifacts" / "ce2_rational_local_solutions.json"
ce2 = json.loads(ce2p.read_text())

# rebuild local alpha functions exactly as assemble_exact_l4_from_local_ce2
local_alphas = []
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

for k, e in ce2.items():
    a_idx = tuple(e["a"])
    b_idx = tuple(e["b"])
    c_idx = tuple(e["c"])
    U_rats = [
        None if s == "0" else float(__import__("fractions").Fraction(s))
        for s in e.get("U_rats", [])
    ]
    V_rats = [
        None if s == "0" else float(__import__("fractions").Fraction(s))
        for s in e.get("V_rats", [])
    ]
    U_e8 = flat_rats_to_E8Z3(toe, U_rats)
    V_e8 = flat_rats_to_E8Z3(toe, V_rats)

    def make_alpha_from_rats(
        U_e8=U_e8, V_e8=V_e8, a_idx=a_idx, b_idx=b_idx, c_idx=c_idx
    ):
        def alpha(a, b):
            if np.allclose(a.g1, basis_elem_g1(toe, b_idx).g1) and np.allclose(
                b.g2, basis_elem_g2(toe, c_idx).g2
            ):
                return U_e8
            if np.allclose(a.g1, basis_elem_g1(toe, c_idx).g1) and np.allclose(
                b.g2, basis_elem_g2(toe, b_idx).g2
            ):
                return U_e8.scale(-1.0)
            if np.allclose(a.g1, basis_elem_g1(toe, a_idx).g1) and np.allclose(
                b.g2, basis_elem_g2(toe, c_idx).g2
            ):
                return V_e8
            if np.allclose(a.g1, basis_elem_g1(toe, c_idx).g1) and np.allclose(
                b.g2, basis_elem_g2(toe, a_idx).g2
            ):
                return V_e8.scale(-1.0)
            return toe.E8Z3.zero()

        return alpha

    local_alphas.append(make_alpha_from_rats())


# assemble alpha_global by summing local alphas
def alpha_global_local(a, b):
    acc = toe.E8Z3.zero()
    for alpha in local_alphas:
        acc = acc + alpha(a, b)
    return acc


linfty.attach_l4_from_ce2(alpha_global_local)

# verify failing triple
exh = json.loads(
    (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text()
)
ft = exh["sectors"]["g1_g1_g2"]["first_fail"]

# quick checks
print("local_alphas count=", len(local_alphas))
print(
    "alpha_global_local(x,z) e6 nonzero=",
    [
        (
            int(i),
            int(j),
            float(
                alpha_global_local(
                    basis_elem_g1(toe, tuple(ft["a"])),
                    basis_elem_g2(toe, tuple(ft["c"])),
                ).e6[int(i), int(j)]
            ),
        )
        for i, j in __import__("numpy").argwhere(
            np.abs(
                alpha_global_local(
                    basis_elem_g1(toe, tuple(ft["a"])),
                    basis_elem_g2(toe, tuple(ft["c"])),
                ).e6
            )
            > 1e-12
        )[:10]
    ],
)

x = basis_elem_g1(toe, tuple(ft["a"]))
y = basis_elem_g1(toe, tuple(ft["b"]))
z = basis_elem_g2(toe, tuple(ft["c"]))

print(
    "alpha_global_local(x,z) g1 nonzero=",
    [
        (int(i), int(j), float(alpha_global_local(x, z).g1[int(i), int(j)]))
        for i, j in __import__("numpy").argwhere(
            np.abs(alpha_global_local(x, z).g1) > 1e-12
        )[:10]
    ],
)
print(
    "alpha_global_local(x,z) e6 nonzero=",
    [
        (int(i), int(j), float(alpha_global_local(x, z).e6[int(i), int(j)]))
        for i, j in __import__("numpy").argwhere(
            np.abs(alpha_global_local(x, z).e6) > 1e-12
        )[:10]
    ],
)
print(
    "alpha_global_local(y,z) g1 nonzero=",
    [
        (int(i), int(j), float(alpha_global_local(y, z).g1[int(i), int(j)]))
        for i, j in __import__("numpy").argwhere(
            np.abs(alpha_global_local(y, z).g1) > 1e-12
        )[:10]
    ],
)

# compute d(alpha_global_local) manually (not using linfty._ce2_alpha)
term1 = linfty.br_l2.bracket(x, alpha_global_local(y, z))
term2 = linfty.br_l2.bracket(y, alpha_global_local(x, z)).scale(-1.0)
term3 = linfty.br_l2.bracket(z, alpha_global_local(x, y))
term4 = alpha_global_local(linfty.br_l2.bracket(x, y), z).scale(-1.0)
term5 = alpha_global_local(linfty.br_l2.bracket(x, z), y)
term6 = alpha_global_local(linfty.br_l2.bracket(y, z), x).scale(-1.0)
manual_dalpha = term1 + term2 + term3 + term4 + term5 + term6
print(
    "manual d_alpha.g1 nonzero=",
    [
        (int(i), int(j), float(manual_dalpha.g1[int(i), int(j)]))
        for i, j in __import__("numpy").argwhere(np.abs(manual_dalpha.g1) > 1e-12)[:20]
    ],
)
print("manual d_alpha.g1 max=", float(np.max(np.abs(manual_dalpha.g1))))

print(
    "linfty.d_alpha_on_triple (uses _ce2_alpha?) g1 max=",
    float(np.max(np.abs(linfty.d_alpha_on_triple(x, y, z).g1))),
)
print(
    "linfty._ce2_alpha(x,z) e6 nonzero=",
    [
        (int(i), int(j), float(linfty._ce2_alpha(x, z).e6[int(i), int(j)]))
        for i, j in __import__("numpy").argwhere(
            np.abs(linfty._ce2_alpha(x, z).e6) > 1e-12
        )[:20]
    ],
)

print(
    "homotopy_jacobi.g1 max=", float(np.max(np.abs(linfty.homotopy_jacobi(x, y, z).g1)))
)
print("Done")
