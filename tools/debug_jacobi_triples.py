import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

toe_spec = importlib.util.spec_from_file_location(
    "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(toe_spec)
import sys

sys.modules[toe_spec.name] = toe
toe_spec.loader.exec_module(toe)

# setup projector and br_l2
e6_basis = np.load(
    ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
).astype(np.complex128)
proj = toe.E6Projector(e6_basis)
all_triads = toe._load_signed_cubic_triads()
bad9 = set(
    tuple(sorted(t[:3]))
    for t in json.loads(
        (
            ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
        ).read_text()
    )["original"]["fiber_triads"]
)
br_l2 = toe.E8Z3Bracket(
    e6_projector=proj,
    cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
    scale_g1g1=1.0,
    scale_g2g2=-1.0 / 6.0,
    scale_e6=1.0,
    scale_sl3=1.0 / 6.0,
)

from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

x = basis_elem_g1(toe, (0, 0))
y = basis_elem_g1(toe, (17, 1))
z0 = basis_elem_g2(toe, (3, 0))
z1 = basis_elem_g2(toe, (3, 1))
J0 = toe._jacobi(br_l2, x, y, z0)
J1 = toe._jacobi(br_l2, x, y, z1)


def mag(J):
    return max(
        np.max(np.abs(J.e6)) if J.e6.size else 0.0,
        np.max(np.abs(J.sl3)) if J.sl3.size else 0.0,
        np.max(np.abs(J.g1)) if J.g1.size else 0.0,
        np.max(np.abs(J.g2)) if J.g2.size else 0.0,
    )


print("mag_j (3,0)=", mag(J0))
print("mag_j (3,1)=", mag(J1))
