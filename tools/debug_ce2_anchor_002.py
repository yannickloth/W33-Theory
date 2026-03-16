import sys

sys.path.insert(0, r"c:\Repos\Theory of Everything")

import numpy as np
from tools.build_linfty_firewall_extension import LInftyE8Extension, _load_bad9, _load_bracket_tool
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2


def max_abs(e):
    return float(
        max(
            0.0 if e.e6.size == 0 else np.max(np.abs(e.e6)),
            0.0 if e.sl3.size == 0 else np.max(np.abs(e.sl3)),
            0.0 if e.g1.size == 0 else np.max(np.abs(e.g1)),
            0.0 if e.g2.size == 0 else np.max(np.abs(e.g2)),
        )
    )


toe = _load_bracket_tool()
e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(np.complex128)
proj = toe.E6Projector(e6_basis)
all_triads = toe._load_signed_cubic_triads()
bad9 = _load_bad9()

linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

x = basis_elem_g1(toe, (22, 0))
y = basis_elem_g1(toe, (0, 1))
z = basis_elem_g2(toe, (0, 0))

baseline = linfty.homotopy_jacobi(x, y, z)
print('baseline max_abs', max_abs(baseline))

linfty.enable_ce2_global_predictor()
repaired = linfty.homotopy_jacobi(x, y, z)
print('repaired max_abs', max_abs(repaired))

from scripts.ce2_global_cocycle import predict_ce2_uv
print('predict_ce2_uv', predict_ce2_uv((22,0),(0,1),(0,0)))
