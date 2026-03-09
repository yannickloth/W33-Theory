import pytest

from w33_l6_chiral_gauge_bridge import build_l6_chiral_gauge_bridge_certificate


def test_l6_chiral_family_has_rank_9_response_and_rank_10_no_go():
    certificate = build_l6_chiral_gauge_bridge_certificate()

    assert certificate.mode_indices == (
        8,
        9,
        127,
        128,
        246,
        247,
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
    )
    assert certificate.a2_mode_indices == (8, 9, 127, 128, 246, 247)
    assert certificate.cartan_mode_indices == (0, 1, 2, 3, 4, 5, 6, 7)
    assert certificate.zero_response_mode_indices == (127, 128, 7)
    assert certificate.response_rank == 9
    assert certificate.effective_mode_count == 9
    assert certificate.augmented_rank == 10
    assert certificate.a2_coefficients_all_zero is True
    assert certificate.active_a2_mode_indices == ()
    assert certificate.active_cartan_mode_indices == (0, 1, 2, 3, 4, 5, 6)


def test_l6_chiral_bridge_improves_residual_and_lifts_quark_rank():
    certificate = build_l6_chiral_gauge_bridge_certificate()

    assert certificate.original_total_residual_norm == pytest.approx(
        3.5237290853109955
    )
    assert certificate.bridged_total_residual_norm == pytest.approx(
        0.8266952645059752
    )
    assert certificate.residual_improvement_factor == pytest.approx(
        4.262428051304662
    )
    assert certificate.residual_reduction_fraction == pytest.approx(
        0.7653922951949498
    )
    assert certificate.up_block.original_residual_norm == pytest.approx(
        1.9287301521985925
    )
    assert certificate.up_block.bridged_residual_norm == pytest.approx(
        0.6938204805517192
    )
    assert certificate.down_block.original_residual_norm == pytest.approx(
        2.9490111336966254
    )
    assert certificate.down_block.bridged_residual_norm == pytest.approx(
        0.44948659726802254
    )
    assert certificate.up_block.original_full_rank == 9
    assert certificate.up_block.bridged_full_rank == 12
    assert certificate.down_block.original_full_rank == 9
    assert certificate.down_block.bridged_full_rank == 12
    assert certificate.up_block.original_quark_rank == 6
    assert certificate.up_block.bridged_quark_rank == 9
    assert certificate.down_block.original_quark_rank == 6
    assert certificate.down_block.bridged_quark_rank == 9
    assert certificate.up_block.support_count == 51
    assert certificate.down_block.support_count == 57
    assert certificate.support_preserved is True
    assert "Cartan slice" in certificate.route_interpretation
    assert "rank 6 to rank 9" in certificate.route_interpretation
