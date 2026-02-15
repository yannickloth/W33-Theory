#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
# load modules
spec = importlib.util.spec_from_file_location(
    "build", "tools/build_linfty_firewall_extension.py"
)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
toe_spec = importlib.util.spec_from_file_location(
    "toe", "tools/toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(toe_spec)
toe_spec.loader.exec_module(toe)
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

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
linfty = b.LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)
linfty.attach_l4_from_symbolic_constants(
    ROOT / "artifacts" / "l4_symbolic_constants.json"
)
print(
    "_l4_coboundary_on_triple present?",
    hasattr(linfty, "_l4_coboundary_on_triple")
    and linfty._l4_coboundary_on_triple is not None,
)
exh = json.loads(
    (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text()
)
ft = exh["sectors"]["g1_g1_g2"]["first_fail"]
print("failing-triple from exhaustive artifact:", ft)
x = basis_elem_g1(toe, tuple(ft["a"]))
y = basis_elem_g1(toe, tuple(ft["b"]))
z = basis_elem_g2(toe, tuple(ft["c"]))
J = toe._jacobi(linfty.br_l2, x, y, z)
print("Jacobi(l2).g1 norm =", np.max(np.abs(J.g1)))
print("l3(x,y,z).g1 norm =", np.max(np.abs(linfty.l3(x, y, z).g1)))
print(
    "d_alpha_on_triple.g1 norm =", np.max(np.abs(linfty.d_alpha_on_triple(x, y, z).g1))
)
if hasattr(linfty, "_l4_coboundary_on_triple") and linfty._l4_coboundary_on_triple:
    print(
        "_l4_coboundary_on_triple.g1 norm =",
        np.max(np.abs(linfty._l4_coboundary_on_triple(x, y, z).g1)),
    )
print("homotopy_jacobi.g1 norm =", np.max(np.abs(linfty.homotopy_jacobi(x, y, z).g1)))
# inspect CE2 artifact entry for this triple
ce2 = json.loads((ROOT / "artifacts" / "ce2_rational_local_solutions.json").read_text())
for k, v in ce2.items():
    if v["a"] == ft["a"] and v["b"] == ft["b"] and v["c"] == ft["c"]:
        print(
            "CE2 key=",
            k,
            "U_nonzero=",
            sum(1 for s in v["U_rats"] if s != "0"),
            "V_nonzero=",
            sum(1 for s in v["V_rats"] if s != "0"),
        )

print("Done")
