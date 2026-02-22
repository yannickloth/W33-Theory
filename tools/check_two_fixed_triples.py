"""Quick check: compute homotopy_jacobi magnitude for the two repaired triples."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

spec_toe = importlib.util.spec_from_file_location(
    "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec_toe)
spec_toe.loader.exec_module(toe)

spec_build = importlib.util.spec_from_file_location(
    "build", ROOT / "tools" / "build_linfty_firewall_extension.py"
)
build = importlib.util.module_from_spec(spec_build)
spec_build.loader.exec_module(build)

spec_exh = importlib.util.spec_from_file_location(
    "exh", ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py"
)
exh = importlib.util.module_from_spec(spec_exh)
spec_exh.loader.exec_module(exh)

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

# attach symbolic l4 (we created a minimal JSON earlier) which will also attach CE2 alpha
symp = ROOT / "artifacts" / "l4_symbolic_constants.json"
if symp.exists():
    linfty.attach_l4_from_symbolic_constants(symp)

# helper to eval triple


def mag_for_triple(a_idx, b_idx, c_idx, sector="g1_g1_g2"):
    if sector == "g1_g2_g2":
        x = exh.basis_elem_g1(toe, a_idx)
        y = exh.basis_elem_g2(toe, b_idx)
        z = exh.basis_elem_g2(toe, c_idx)
    elif sector == "g1_g1_g2":
        x = exh.basis_elem_g1(toe, a_idx)
        y = exh.basis_elem_g1(toe, b_idx)
        z = exh.basis_elem_g2(toe, c_idx)
    else:
        raise ValueError("unknown sector")
    hj = linfty.homotopy_jacobi(x, y, z)
    return float(
        max(
            np.max(np.abs(hj.e6)) if hj.e6.size else 0.0,
            np.max(np.abs(hj.sl3)) if hj.sl3.size else 0.0,
            np.max(np.abs(hj.g1)) if hj.g1.size else 0.0,
            np.max(np.abs(hj.g2)) if hj.g2.size else 0.0,
        )
    )


# triples to check (the recorded failing ones)
triples = [
    ("g1_g2_g2", (0, 0), (0, 0), (21, 1)),
    ("g1_g1_g2", (0, 0), (17, 1), (3, 0)),
]

for sector, a, b, c in triples:
    mag = mag_for_triple(a, b, c, sector=sector)
    print(f"{sector} {a} {b} {c} -> homotopy_jacobi magnitude = {mag}")
