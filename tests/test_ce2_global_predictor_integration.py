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


def _build_linfty():
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()
    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)
    return toe, linfty


def _assert_predictor_cancels_triples(triples) -> None:
    for triple in triples:
        toe, linfty = _build_linfty()
        x = basis_elem_g1(toe, triple[0])
        y = basis_elem_g2(toe, triple[1])
        z = basis_elem_g2(toe, triple[2])

        baseline = linfty.homotopy_jacobi(x, y, z)
        assert max_abs(baseline) > 1e-10, triple

        linfty.enable_ce2_global_predictor()
        repaired = linfty.homotopy_jacobi(x, y, z)
        assert max_abs(repaired) < 1e-10, triple


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


def test_global_ce2_predictor_cancels_dual_diagonal_fiber_triple() -> None:
    """Integration check for the first closed-form g1,g2,g2 W-family."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (4, 1))
    y = basis_elem_g2(toe, (4, 1))
    z = basis_elem_g2(toe, (25, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_artifact_loader_does_not_smear_dual_w_family() -> None:
    """Artifact aggregation must not block the dual predictor on unseen c-legs."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)
    linfty.attach_l4_from_symbolic_constants(
        "artifacts/l4_symbolic_constants.json", load_ce2_artifact=True
    )
    linfty.enable_ce2_global_predictor()

    x = basis_elem_g1(toe, (0, 0))
    y = basis_elem_g2(toe, (0, 0))
    z = basis_elem_g2(toe, (21, 2))

    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_dual_same_e6id_fiber_triple() -> None:
    """Integration check for the second closed-form g1,g2,g2 family."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (4, 1))
    y = basis_elem_g2(toe, (4, 2))
    z = basis_elem_g2(toe, (25, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_dual_missing_focus_u_triple() -> None:
    """Integration check for the focus-section U-family."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (0, 0))
    y = basis_elem_g2(toe, (1, 0))
    z = basis_elem_g2(toe, (15, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_second_focus_section_u_orbit() -> None:
    """A second orbit checks the section rule is not a one-off fit."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (0, 2))
    y = basis_elem_g2(toe, (9, 2))
    z = basis_elem_g2(toe, (4, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_origin_line_w_family() -> None:
    """Integration check for the first off-fiber W-only frontier family."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (0, 0))
    y = basis_elem_g2(toe, (1, 0))
    z = basis_elem_g2(toe, (16, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_origin_line_w_family_second_lambda() -> None:
    """A second affine-line placement checks the lookup table orientation."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (0, 1))
    y = basis_elem_g2(toe, (2, 1))
    z = basis_elem_g2(toe, (15, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_origin_line_w_family_mirror_z_order() -> None:
    """Mirror z-order should be covered by the same origin-line law."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (0, 0))
    y = basis_elem_g2(toe, (4, 0))
    z = basis_elem_g2(toe, (13, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_origin_line_v_family() -> None:
    """Color-swapped dual of the origin-line W-family."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (0, 0))
    y = basis_elem_g2(toe, (1, 1))
    z = basis_elem_g2(toe, (16, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_origin_line_v_family_mirror_z_order() -> None:
    """Mirror z-order should be covered for the dual V family too."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (0, 0))
    y = basis_elem_g2(toe, (4, 1))
    z = basis_elem_g2(toe, (13, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_origin_line_v_family_second_line() -> None:
    """A second line direction checks the dual V table."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (0, 0))
    y = basis_elem_g2(toe, (2, 2))
    z = basis_elem_g2(toe, (15, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_origin_same_fiber_uv_family_mirror_z_order() -> None:
    """The 1/108 overlap family should also cover the mirrored z-order."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (0, 0))
    y = basis_elem_g2(toe, (4, 1))
    z = basis_elem_g2(toe, (9, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_origin_same_fiber_uv_family_x_axis() -> None:
    """The explicit V-sign table should cover the x-axis line too."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (0, 0))
    y = basis_elem_g2(toe, (11, 1))
    z = basis_elem_g2(toe, (14, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_translated_2v_line_w_family() -> None:
    """Translated branch with `a` at the 2v,z=2 point."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 0))
    y = basis_elem_g2(toe, (0, 0))
    z = basis_elem_g2(toe, (20, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_translated_2v_line_v_family() -> None:
    """Translated V dual on the same branch."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 0))
    y = basis_elem_g2(toe, (0, 1))
    z = basis_elem_g2(toe, (20, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_translated_2v_overlap_uv_family() -> None:
    """Translated half-strength overlap branch."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 0))
    y = basis_elem_g2(toe, (0, 1))
    z = basis_elem_g2(toe, (22, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_vertical_z2_line_w_family() -> None:
    """Gauge-fixed same-z vertical branch with pure W support."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 1))
    y = basis_elem_g2(toe, (2, 1))
    z = basis_elem_g2(toe, (22, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_vertical_z2_line_v_family() -> None:
    """Color-swapped vertical same-z dual."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 2))
    y = basis_elem_g2(toe, (2, 0))
    z = basis_elem_g2(toe, (22, 2))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_vertical_z2_overlap_uv_family() -> None:
    """Half-strength vertical overlap with U on the z=1 fiber point."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 1))
    y = basis_elem_g2(toe, (2, 0))
    z = basis_elem_g2(toe, (20, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchored_nonvertical_z2_line_w_family() -> None:
    """Nonvertical z=2 affine-line W-family through the a=(0,2,2) anchor."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 0))
    y = basis_elem_g2(toe, (3, 0))
    z = basis_elem_g2(toe, (13, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchored_nonvertical_z2_line_v_family() -> None:
    """Color-swapped dual on the same nonvertical z=2 affine line."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 0))
    y = basis_elem_g2(toe, (3, 1))
    z = basis_elem_g2(toe, (13, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchored_nonvertical_z2_overlap_uv_family() -> None:
    """Half-strength overlap on the active nonvertical z=2 branch."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 0))
    y = basis_elem_g2(toe, (3, 1))
    z = basis_elem_g2(toe, (6, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchored_z1_to_z0_line_w_family() -> None:
    """Anchored branch with the first g2 leg in z=1 and the second in z=0."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 0))
    y = basis_elem_g2(toe, (4, 0))
    z = basis_elem_g2(toe, (19, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchored_z1_to_z0_line_v_family() -> None:
    """Color-swapped dual on the anchored z=1 -> z=0 branch."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 0))
    y = basis_elem_g2(toe, (4, 1))
    z = basis_elem_g2(toe, (19, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchored_z1_to_z0_overlap_uv_family() -> None:
    """Half-strength overlap on the anchored z=1 -> z=0 branch."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 0))
    y = basis_elem_g2(toe, (4, 1))
    z = basis_elem_g2(toe, (9, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchored_nonvertical_z2_complement_uv_family() -> None:
    """Complementary overlap on the u1=1 half of the anchored z=2 pencil."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 0))
    y = basis_elem_g2(toe, (7, 1))
    z = basis_elem_g2(toe, (19, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchored_nonvertical_z2_complement_uv_family_negative_v_sign() -> None:
    """A second direction checks the complementary V-sign table."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (1, 0))
    y = basis_elem_g2(toe, (11, 1))
    z = basis_elem_g2(toe, (17, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_01_origin_line_w_family() -> None:
    """Origin-line branch for the new a=(0,1,2) anchor."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (2, 0))
    y = basis_elem_g2(toe, (0, 0))
    z = basis_elem_g2(toe, (23, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_01_origin_overlap_uv_family() -> None:
    """Half-strength origin overlap for the new a=(0,1,2) anchor."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (2, 0))
    y = basis_elem_g2(toe, (0, 1))
    z = basis_elem_g2(toe, (21, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_01_samefiber_z2_line_w_family() -> None:
    """Same-fiber z=2 branch for the new a=(0,1,2) anchor."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (2, 1))
    y = basis_elem_g2(toe, (1, 1))
    z = basis_elem_g2(toe, (21, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_01_samefiber_z2_overlap_uv_family() -> None:
    """Half-strength same-fiber overlap for the new a=(0,1,2) anchor."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (2, 0))
    y = basis_elem_g2(toe, (1, 2))
    z = basis_elem_g2(toe, (23, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_01_affine_z2_line_w_family() -> None:
    """Representative nonvertical z=2 affine-line branch for a=(0,1,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (2, 0))
    y = basis_elem_g2(toe, (5, 0))
    z = basis_elem_g2(toe, (18, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_01_affine_z2_overlap_uv_family() -> None:
    """Representative nonvertical z=2 overlap for a=(0,1,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (2, 0))
    y = basis_elem_g2(toe, (3, 1))
    z = basis_elem_g2(toe, (6, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_01_affine_z1_overlap_uv_family() -> None:
    """Representative z=1 affine overlap for a=(0,1,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (2, 0))
    y = basis_elem_g2(toe, (6, 1))
    z = basis_elem_g2(toe, (3, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_01_affine_z1_complement_uv_family() -> None:
    """Complementary z=1 overlap on the u1=1 half of the a=(0,1,2) pencil."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (2, 0))
    y = basis_elem_g2(toe, (8, 1))
    z = basis_elem_g2(toe, (18, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_01_affine_z1_complement_uv_family_second_direction() -> None:
    """A second direction checks the complementary z=1 U-sign character."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (2, 0))
    y = basis_elem_g2(toe, (12, 1))
    z = basis_elem_g2(toe, (19, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_origin_overlap_uv_family() -> None:
    """Origin overlap branch for the anchored a=(2,0,2) orbit."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (0, 1))
    z = basis_elem_g2(toe, (21, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_samefiber_z2_line_w_family() -> None:
    """Same-fiber z=2 line branch for the anchored a=(2,0,2) orbit."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (11, 0))
    z = basis_elem_g2(toe, (21, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_samefiber_z2_overlap_uv_family() -> None:
    """Half-strength same-fiber overlap for the anchored a=(2,0,2) orbit."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (11, 1))
    z = basis_elem_g2(toe, (17, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_zero2_z2_line_w_family() -> None:
    """Affine z=2 branch through b=(0,2,2) for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (1, 0))
    z = basis_elem_g2(toe, (8, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_zero2_z2_overlap_uv_family() -> None:
    """Half-strength overlap on the b=(0,2,2) affine branch for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (1, 1))
    z = basis_elem_g2(toe, (15, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_zero1_z2_line_w_family() -> None:
    """Affine z=2 branch through b=(0,1,2) for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (2, 0))
    z = basis_elem_g2(toe, (7, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_zero1_z2_overlap_uv_family() -> None:
    """Half-strength overlap on the b=(0,1,2) affine branch for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (2, 1))
    z = basis_elem_g2(toe, (20, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_two2_z1_line_w_family() -> None:
    """z=1 affine branch through b=(2,2,1) for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (4, 0))
    z = basis_elem_g2(toe, (5, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_two2_z1_overlap_uv_family() -> None:
    """Half-strength overlap on the b=(2,2,1) branch for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (4, 1))
    z = basis_elem_g2(toe, (9, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_two1_z2_complement_uv_family() -> None:
    """Complementary z=2 overlap through b=(2,1,2) for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (5, 1))
    z = basis_elem_g2(toe, (24, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_one2_z2_complement_uv_family() -> None:
    """Complementary z=2 overlap through b=(1,2,2) for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (7, 1))
    z = basis_elem_g2(toe, (12, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_one1_z1_complement_uv_family() -> None:
    """Complementary z=1 overlap through b=(1,1,1) for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (8, 1))
    z = basis_elem_g2(toe, (18, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_two2_z2_line_w_family() -> None:
    """z=2 line branch through b=(2,2,2) for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (9, 0))
    z = basis_elem_g2(toe, (24, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_one2_z1_line_w_family() -> None:
    """z=1 line branch through b=(1,2,1) for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (12, 0))
    z = basis_elem_g2(toe, (20, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_one2_z1_overlap_uv_family() -> None:
    """Half-strength overlap on the b=(1,2,1) branch for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (12, 1))
    z = basis_elem_g2(toe, (7, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_zero2_z1_line_w_family() -> None:
    """z=1 line branch through b=(0,2,1) for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (15, 0))
    z = basis_elem_g2(toe, (18, 1))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_20_zero2_z1_overlap_uv_family() -> None:
    """Half-strength overlap on the b=(0,2,1) branch for a=(2,0,2)."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (3, 0))
    y = basis_elem_g2(toe, (15, 1))
    z = basis_elem_g2(toe, (1, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_anchor_22_line_families() -> None:
    """Table-driven line families on the anchored a=(2,2,1) orbit."""
    triples = [
        ((4, 0), (0, 0), (18, 1)),
        ((4, 0), (1, 1), (12, 0)),
        ((4, 0), (2, 0), (11, 1)),
        ((4, 0), (3, 1), (10, 0)),
        ((4, 0), (6, 0), (24, 1)),
        ((4, 0), (7, 1), (23, 0)),
        ((4, 0), (8, 0), (22, 1)),
        ((4, 0), (16, 1), (17, 0)),
    ]
    _assert_predictor_cancels_triples(triples)


def test_global_ce2_predictor_cancels_anchor_22_overlap_families() -> None:
    """Half-strength overlap families on the anchored a=(2,2,1) orbit."""
    triples = [
        ((4, 0), (0, 1), (22, 0)),
        ((4, 0), (0, 2), (22, 0)),
        ((4, 0), (1, 1), (23, 0)),
        ((4, 0), (2, 1), (16, 0)),
        ((4, 0), (3, 1), (6, 0)),
        ((4, 0), (7, 1), (12, 0)),
        ((4, 0), (7, 2), (12, 0)),
        ((4, 0), (8, 1), (18, 0)),
        ((4, 0), (10, 1), (24, 0)),
        ((4, 0), (11, 1), (17, 0)),
    ]
    _assert_predictor_cancels_triples(triples)


def test_global_ce2_predictor_cancels_anchor_21_line_families() -> None:
    """Table-driven line families on the anchored a=(2,1,2) orbit."""
    triples = [
        ((5, 0), (1, 0), (14, 1)),
        ((5, 0), (2, 1), (13, 0)),
        ((5, 0), (3, 0), (25, 1)),
        ((5, 0), (6, 1), (9, 0)),
        ((5, 0), (7, 0), (21, 1)),
        ((5, 0), (8, 1), (20, 0)),
        ((5, 0), (15, 0), (17, 1)),
    ]
    _assert_predictor_cancels_triples(triples)


def test_global_ce2_predictor_cancels_anchor_21_overlap_families() -> None:
    """Half-strength overlap families on the anchored a=(2,1,2) orbit."""
    triples = [
        ((5, 0), (0, 1), (21, 0)),
        ((5, 0), (0, 2), (21, 0)),
        ((5, 0), (1, 1), (15, 0)),
        ((5, 0), (2, 1), (20, 0)),
        ((5, 0), (3, 1), (6, 0)),
        ((5, 0), (7, 1), (19, 0)),
        ((5, 0), (7, 2), (19, 0)),
        ((5, 0), (8, 1), (13, 0)),
        ((5, 0), (9, 1), (25, 0)),
        ((5, 0), (14, 1), (17, 0)),
    ]
    _assert_predictor_cancels_triples(triples)


def test_global_ce2_predictor_cancels_anchor_201_line_families() -> None:
    """Table-driven line families on the anchored a=(2,0,1) orbit."""
    triples = [
        ((6, 0), (0, 0), (17, 1)),
        ((6, 0), (0, 1), (17, 0)),
        ((6, 0), (1, 0), (8, 1)),
        ((6, 0), (1, 1), (8, 0)),
        ((6, 0), (2, 0), (7, 1)),
        ((6, 0), (2, 1), (7, 0)),
        ((6, 0), (4, 0), (5, 1)),
        ((6, 0), (4, 1), (5, 0)),
    ]
    _assert_predictor_cancels_triples(triples)


def test_global_ce2_predictor_cancels_anchor_201_overlap_families() -> None:
    """Half-strength overlap families on the anchored a=(2,0,1) orbit."""
    triples = [
        ((6, 0), (0, 1), (22, 0)),
        ((6, 0), (0, 2), (22, 0)),
        ((6, 0), (1, 1), (23, 0)),
        ((6, 0), (1, 2), (23, 0)),
        ((6, 0), (2, 1), (16, 0)),
        ((6, 0), (2, 2), (16, 0)),
        ((6, 0), (4, 1), (25, 0)),
        ((6, 0), (4, 2), (25, 0)),
    ]
    _assert_predictor_cancels_triples(triples)


def test_global_ce2_predictor_cancels_anchor_201_samefiber_v_families() -> None:
    """Same-fiber sl3/e6 families on the anchored a=(2,0,1) orbit."""
    triples = [
        ((6, 0), (3, 0), (6, 1)),
        ((6, 0), (3, 0), (6, 2)),
        ((6, 0), (3, 1), (6, 0)),
        ((6, 0), (3, 2), (6, 0)),
    ]
    _assert_predictor_cancels_triples(triples)


def test_global_ce2_predictor_cancels_origin_same_fiber_uv_family() -> None:
    """Half-strength U/V overlap on a same-fiber origin line."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (0, 0))
    y = basis_elem_g2(toe, (1, 1))
    z = basis_elem_g2(toe, (15, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10


def test_global_ce2_predictor_cancels_origin_same_fiber_uv_family_diagonal() -> None:
    """A diagonal same-fiber case checks the sign tables beyond the axis lines."""
    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    x = basis_elem_g1(toe, (0, 0))
    y = basis_elem_g2(toe, (9, 1))
    z = basis_elem_g2(toe, (4, 0))

    baseline = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(baseline) > 1e-10

    linfty.enable_ce2_global_predictor()
    repaired = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(repaired) < 1e-10
