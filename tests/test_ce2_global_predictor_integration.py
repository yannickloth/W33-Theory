from __future__ import annotations

import numpy as np

from tools.build_linfty_firewall_extension import (
    LInftyE8Extension,
    _load_bad9,
    _load_bracket_tool,
)
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2


def max_abs(e) -> float:
    return float(
        max(
            0.0 if e.e6.size == 0 else np.max(np.abs(e.e6)),
            0.0 if e.sl3.size == 0 else np.max(np.abs(e.sl3)),
            0.0 if e.g1.size == 0 else np.max(np.abs(e.g1)),
            0.0 if e.g2.size == 0 else np.max(np.abs(e.g2)),
        )
    )


def test_global_ce2_predictor_cancels_known_mixed_basis_triple() -> None:
    """Integration check: the CE2 global predictor cancels a recorded g1,g1,g2 obstruction.

    This threads the metaplectic/Weil CE2 phase law through the L∞ firewall:
    `homotopy_jacobi` should reduce to ~0 on this triple without attaching a
    per-triple CE2 artifact or running an LSQ solve.
    """
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    # Known failing mixed triple (regression key used elsewhere in the suite).
    x = basis_elem_g1(toe, (0, 0))
    y = basis_elem_g1(toe, (17, 1))
    z = basis_elem_g2(toe, (3, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10
