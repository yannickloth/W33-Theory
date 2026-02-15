#!/usr/bin/env python3
"""Check runtime CE2 alpha attached by attach_l4_from_symbolic_constants.
Prints d_alpha_on_triple, l4_coboundary_on_triple, and bracket checks for the
recorded failing triple.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

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

# setup
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

# ensure repo root is on sys.path so attach_l4_from_symbolic_constants can import helpers
import sys

sys.path.insert(0, str(ROOT))
# attach symbolic l4 (loader should also attach CE2 alpha)
linfty.attach_l4_from_symbolic_constants(
    ROOT / "artifacts" / "l4_symbolic_constants.json"
)
print(
    "linfty has _ce2_alpha?",
    hasattr(linfty, "_ce2_alpha") and linfty._ce2_alpha is not None,
)
print(
    "linfty has _l4_coboundary_on_triple?",
    hasattr(linfty, "_l4_coboundary_on_triple")
    and linfty._l4_coboundary_on_triple is not None,
)

exh = json.loads(
    (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text()
)
ft = exh["sectors"]["g1_g1_g2"]["first_fail"]

# load helpers module for basis elements
spec_exh = importlib.util.spec_from_file_location(
    "exh", ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py"
)
exh_mod = importlib.util.module_from_spec(spec_exh)
spec_exh.loader.exec_module(exh_mod)

x = exh_mod.basis_elem_g1(toe, tuple(ft["a"]))
y = exh_mod.basis_elem_g1(toe, tuple(ft["b"]))
z = exh_mod.basis_elem_g2(toe, tuple(ft["c"]))

J = toe._jacobi(linfty.br_l2, x, y, z)
l3v = linfty.l3(x, y, z)
print("\nJacobi(l2).g1 max=", float(np.max(np.abs(J.g1))))
print("l3.g1 max=", float(np.max(np.abs(l3v.g1))))

# compute d_alpha and l4_coboundary if available
if hasattr(linfty, "_ce2_alpha") and linfty._ce2_alpha is not None:
    # check direct alpha on pairs
    alpha_fn = linfty._ce2_alpha
    U_e = alpha_fn(y, z)
    V_e = alpha_fn(x, z)
    print("\n_direct _ce2_alpha outputs:")
    print(
        " alpha(y,z) nonzero g1 indices=",
        [
            (i, j, float(U_e.g1[i, j]))
            for i, j in __import__("numpy").argwhere(np.abs(U_e.g1) > 1e-12)
        ],
    )
    print(
        " alpha(x,z) nonzero e6 indices sample=",
        [
            (i, j, float(V_e.e6[i, j]))
            for i, j in __import__("numpy").argwhere(np.abs(V_e.e6) > 1e-12)[:5]
        ],
    )
    d_alpha_val = linfty.d_alpha_on_triple(x, y, z)
    # detailed d_alpha g1 entries
    nz_da = __import__("numpy").argwhere(np.abs(d_alpha_val.g1) > 1e-12)
    print(
        "\nd_alpha_on_triple.g1 nonzero indices and values=",
        [(int(i), int(j), float(d_alpha_val.g1[int(i), int(j)])) for i, j in nz_da],
    )
else:
    print("\n_no _ce2_alpha attached")

if (
    hasattr(linfty, "_l4_coboundary_on_triple")
    and linfty._l4_coboundary_on_triple is not None
):
    l4_cb_val = linfty._l4_coboundary_on_triple(x, y, z)
    nz_cb = __import__("numpy").argwhere(np.abs(l4_cb_val.g1) > 1e-12)
    print(
        "l4_coboundary_on_triple.g1 nonzero indices and values=",
        [(int(i), int(j), float(l4_cb_val.g1[int(i), int(j)])) for i, j in nz_cb],
    )
else:
    print("\n_no _l4_coboundary_on_triple attached")

# compute homotopy total
tot = linfty.homotopy_jacobi(x, y, z)
nz_tot = __import__("numpy").argwhere(np.abs(tot.g1) > 1e-12)
print(
    "\nhomotopy_jacobi.g1 nonzero indices and values=",
    [(int(i), int(j), float(tot.g1[int(i), int(j)])) for i, j in nz_tot],
)
print("homotopy_jacobi.g1 max=", float(np.max(np.abs(tot.g1))))

# if CE2 alpha attached, show U/V nonzero flattened indices for this triple from artifact
ce2 = json.loads((ROOT / "artifacts" / "ce2_rational_local_solutions.json").read_text())
key = f"{ft['a'][0]},{ft['a'][1]}:{ft['b'][0]},{ft['b'][1]}:{ft['c'][0]},{ft['c'][1]}"
entry = ce2.get(key)
if entry:
    print("\nCE2 artifact entry for key=", key)
    nonzero_V = [i for i, s in enumerate(entry.get("V_rats", [])) if s != "0"]
    print(" V_nonzero_count=", len(nonzero_V))
    print(
        " V_nonzero sample (first 6) idx/val=",
        [(i, entry["V_rats"][i]) for i in nonzero_V[:6]],
    )

# compute manual sum of V_e8 for all CE2 entries with same (a_idx,c_idx)
manual_sum = toe.E8Z3.zero()
manual_sub = toe.E8Z3.zero()
for k, e in ce2.items():
    if tuple(e["a"]) == tuple(ft["a"]) and tuple(e["c"]) == tuple(ft["c"]):
        from fractions import Fraction

        V_rats = [Fraction(s) if s != "0" else None for s in e.get("V_rats", [])]
        V_num = np.array(
            [float(fr) if fr is not None else 0.0 for fr in V_rats], dtype=np.complex128
        )
        Nn = 27 * 27
        e6 = V_num[:Nn].reshape((27, 27)).astype(np.complex128)
        off = Nn
        sl3 = V_num[off : off + 9].reshape((3, 3)).astype(np.complex128)
        off += 9
        g1 = V_num[off : off + 81].reshape((27, 3)).astype(np.complex128)
        off += 81
        g2 = V_num[off : off + 81].reshape((27, 3)).astype(np.complex128)
        manual_sum = manual_sum + toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)
    if tuple(e["a"]) == tuple(ft["c"]) and tuple(e["c"]) == tuple(ft["a"]):
        # subtracting CE2 entries where (a,c) are swapped
        from fractions import Fraction

        V_rats = [Fraction(s) if s != "0" else None for s in e.get("V_rats", [])]
        V_num = np.array(
            [float(fr) if fr is not None else 0.0 for fr in V_rats], dtype=np.complex128
        )
        Nn = 27 * 27
        e6 = V_num[:Nn].reshape((27, 27)).astype(np.complex128)
        off = Nn
        sl3 = V_num[off : off + 9].reshape((3, 3)).astype(np.complex128)
        off += 9
        g1 = V_num[off : off + 81].reshape((27, 3)).astype(np.complex128)
        off += 81
        g2 = V_num[off : off + 81].reshape((27, 3)).astype(np.complex128)
        manual_sub = manual_sub + toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)

print(
    "\nmanual_sum alpha(x,z) nonzero e6 indices sample:",
    [
        (int(i), int(j), float(manual_sum.e6[int(i), int(j)]))
        for i, j in __import__("numpy").argwhere(np.abs(manual_sum.e6) > 1e-12)[:10]
    ],
)
print(
    "manual_sub (entries with swapped a/c) nonzero e6 indices sample:",
    [
        (int(i), int(j), float(manual_sub.e6[int(i), int(j)]))
        for i, j in __import__("numpy").argwhere(np.abs(manual_sub.e6) > 1e-12)[:10]
    ],
)
print(
    "\n(manual_sum - manual_sub) sample indices:",
    [
        (int(i), int(j), float((manual_sum - manual_sub).e6[int(i), int(j)]))
        for i, j in __import__("numpy").argwhere(
            np.abs((manual_sum - manual_sub).e6) > 1e-12
        )[:20]
    ],
)
print(
    "linfty._ce2_alpha(x,z) nonzero e6 indices sample:",
    [
        (int(i), int(j), float(linfty._ce2_alpha(x, z).e6[int(i), int(j)]))
        for i, j in __import__("numpy").argwhere(
            np.abs(linfty._ce2_alpha(x, z).e6) > 1e-12
        )[:20]
    ],
)

print("\nDone")
