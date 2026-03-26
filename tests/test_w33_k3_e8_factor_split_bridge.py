from __future__ import annotations

from w33_k3_e8_factor_split_bridge import build_k3_e8_factor_split_bridge_summary


def test_k3_e8_factor_split_bridge_constructs_two_explicit_e8_factors() -> None:
    summary = build_k3_e8_factor_split_bridge_summary()
    theorem = summary["e8_factor_split_theorem"]

    assert summary["status"] == "ok"
    assert summary["representative_root_component_sizes"] == [120, 120]
    assert summary["full_root_component_sizes"] == [240, 240]
    assert summary["combined_simple_root_change_of_basis_determinant"] in {-1, 1}
    assert theorem["representative_root_graph_splits_into_two_120_packets"] is True
    assert theorem["full_root_graph_splits_into_two_240_packets"] is True
    assert theorem["each_root_packet_has_rank8_simple_system"] is True
    assert theorem["factor_one_has_exact_negative_e8_cartan"] is True
    assert theorem["factor_two_has_exact_negative_e8_cartan"] is True
    assert theorem["the_two_e8_factor_bases_are_exactly_orthogonal"] is True
    assert theorem["combined_simple_root_basis_is_unimodular_in_the_explicit_complement"] is True
    assert theorem["explicit_n16_is_constructively_split_as_e8_plus_e8"] is True


def test_k3_e8_factor_split_bridge_records_exact_cartan_blocks() -> None:
    summary = build_k3_e8_factor_split_bridge_summary()

    assert summary["e8_factor_one_gram_matrix"] == [
        [-2, 1, 0, 0, 0, 0, 0, 0],
        [1, -2, 1, 0, 0, 0, 0, 0],
        [0, 1, -2, 1, 0, 0, 0, 1],
        [0, 0, 1, -2, 1, 0, 0, 0],
        [0, 0, 0, 1, -2, 1, 0, 0],
        [0, 0, 0, 0, 1, -2, 1, 0],
        [0, 0, 0, 0, 0, 1, -2, 0],
        [0, 0, 1, 0, 0, 0, 0, -2],
    ]
    assert summary["e8_factor_two_gram_matrix"] == summary["e8_factor_one_gram_matrix"]
    assert summary["cross_gram_matrix"] == [[0] * 8 for _ in range(8)]
