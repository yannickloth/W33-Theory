#!/usr/bin/env python3
"""Inspect bracket(y, V) for each CE2 entry with the same (a,c) as the
recorded failing triple. Prints g1(6,1) contribution per CE2 entry.
"""
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# load toe/tool
spec = importlib.util.spec_from_file_location(
    "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toe)

spec2 = importlib.util.spec_from_file_location(
    "build", ROOT / "tools" / "build_linfty_firewall_extension.py"
)
build = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(build)

# failing triple
ft = {"a": [0, 0], "b": [17, 1], "c": [3, 0]}
a_idx = tuple(ft["a"])
c_idx = tuple(ft["c"])
y_idx = tuple(ft["b"])

# load CE2 artifact
ce2 = json.loads((ROOT / "artifacts" / "ce2_rational_local_solutions.json").read_text())

# prepare bracket tool
tool = build._load_bracket_tool()
br = tool.E8Z3Bracket(
    e6_projector=tool.E6Projector(
        np.load(
            ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
        ).astype(np.complex128)
    ),
    cubic_triads=tool._load_signed_cubic_triads(),
    scale_g1g1=1.0,
    scale_g2g2=-1.0 / 6.0,
    scale_e6=1.0,
    scale_sl3=1.0 / 6.0,
)

from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

y = basis_elem_g1(tool, y_idx)

print("CE2 entries with a==", a_idx, "and c==", c_idx)
for k, e in ce2.items():
    if tuple(e["a"]) == a_idx and tuple(e["c"]) == c_idx:
        V_rats = [Fraction(s) if s != "0" else None for s in e.get("V_rats", [])]
        V_num = np.array(
            [float(fr) if fr is not None else 0.0 for fr in V_rats], dtype=np.complex128
        )
        N = 27 * 27
        e6 = V_num[:N].reshape((27, 27)).astype(np.complex128)
        off = N
        sl3 = V_num[off : off + 9].reshape((3, 3)).astype(np.complex128)
        off += 9
        g1 = V_num[off : off + 81].reshape((27, 3)).astype(np.complex128)
        off += 81
        g2 = V_num[off : off + 81].reshape((27, 3)).astype(np.complex128)
        V_e8 = tool.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)
        out = br.bracket(y, V_e8)
        print(
            k,
            "b=",
            e["b"],
            "V nonzero e6 sample=",
            [(i, j, float(e6[i, j])) for i, j in np.argwhere(np.abs(e6) > 1e-12)[:6]],
            "bracket(y,V).g1[6,1]=",
            float(out.g1[6, 1]),
        )
print("done")
