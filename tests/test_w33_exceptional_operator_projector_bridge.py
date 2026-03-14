from __future__ import annotations

import numpy as np

from w33_exceptional_operator_projector_bridge import (
    build_exceptional_operator_projector_summary,
    channel_operator_columns,
    channel_projector_basis,
)


def test_channel_column_spaces_are_exactly_frobenius_orthogonal_with_ranks_40_6_8() -> None:
    e6 = channel_operator_columns("e6")
    a2 = channel_operator_columns("a2")
    cartan = channel_operator_columns("cartan")

    assert np.linalg.matrix_rank(e6) == 40
    assert np.linalg.matrix_rank(a2) == 6
    assert np.linalg.matrix_rank(cartan) == 8
    assert np.array_equal(e6.T @ a2, np.zeros((72, 6), dtype=int))
    assert np.array_equal(e6.T @ cartan, np.zeros((72, 8), dtype=int))
    assert np.array_equal(a2.T @ cartan, np.zeros((6, 8), dtype=int))


def test_projector_bases_are_orthonormal_pairwise_orthogonal_and_sum_to_rank_54() -> None:
    e6 = channel_projector_basis("e6")
    a2 = channel_projector_basis("a2")
    cartan = channel_projector_basis("cartan")

    assert np.allclose(e6.T @ e6, np.eye(40), atol=1e-10)
    assert np.allclose(a2.T @ a2, np.eye(6), atol=1e-10)
    assert np.allclose(cartan.T @ cartan, np.eye(8), atol=1e-10)
    assert np.allclose(e6.T @ a2, 0.0, atol=1e-10)
    assert np.allclose(e6.T @ cartan, 0.0, atol=1e-10)
    assert np.allclose(a2.T @ cartan, 0.0, atol=1e-10)
    combined = np.concatenate([e6, a2, cartan], axis=1)
    assert np.linalg.matrix_rank(combined) == 54


def test_projector_rank_dressing_matches_curved_continuum_discrete_and_tomotope_data() -> None:
    summary = build_exceptional_operator_projector_summary()
    operator_space = summary["operator_space"]
    projectors = summary["orthogonal_projectors"]
    dressing = summary["curved_rank_dressing"]
    alignment = summary["generation_channel_alignment"]

    assert operator_space["spinor_operator_dimension"] == 2304
    assert operator_space["channel_ranks"] == {"e6": 40, "a2": 6, "cartan": 8}
    assert operator_space["frobenius_channels_are_pairwise_orthogonal_exactly"] is True
    assert projectors["projector_traces_equal_ranks"] is True
    assert projectors["combined_gauge_package_rank"] == 54
    assert projectors["combined_rank_matches_spinor_total_rank"] is True
    assert alignment["spinor_action_ranks"] == (40, 6, 8)
    assert alignment["e6_generation_preserving"] is True
    assert alignment["a2_generation_mixing_only"] is True
    assert alignment["cartan_generation_preserving"] is True
    assert dressing["continuum_from_projector_ranks"] == 320
    assert dressing["discrete_from_projector_ranks_and_f4"] == 12480
    assert dressing["topological_from_projector_rank_and_e7_fund"] == 2240
    assert dressing["tomotope_from_a2_projector_rank"] == 96
    assert dressing["firewall_triplet_fibers_from_a2_projector_rank"] == 6
    assert dressing["continuum_matches_live_bridge"] is True
    assert dressing["discrete_matches_live_bridge"] is True
    assert dressing["topological_matches_live_bridge"] is True
    assert dressing["tomotope_matches_live_bridge"] is True
    assert dressing["firewall_matches_live_bridge"] is True
    assert dressing["firewall_full_clean_quark_block_exists"] is False
