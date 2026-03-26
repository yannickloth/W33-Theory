from __future__ import annotations

from w33_k3_three_u_decomposition_bridge import (
    build_k3_three_u_decomposition_bridge_summary,
)


def test_k3_three_u_decomposition_bridge_realizes_primitive_orthogonal_hyperbolic_core() -> None:
    summary = build_k3_three_u_decomposition_bridge_summary()
    assert summary["status"] == "ok"

    block = summary["three_u_block_profile"]
    assert block["rank"] == 6
    assert block["determinant"] == -1
    assert block["positive_directions"] == 3
    assert block["negative_directions"] == 3
    assert block["unit_maximal_minor_rows"] == [0, 1, 3, 7, 19, 21]
    assert block["unit_maximal_minor_determinant"] == 1

    assert summary["three_u_block_gram_matrix"] == [
        [0, 1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1, 0],
    ]

    theorem = summary["three_u_decomposition_theorem"]
    assert theorem["explicit_vectors_realize_orthogonal_three_u_block"] is True
    assert theorem["three_u_block_has_signature_3_3"] is True
    assert theorem["three_u_block_is_primitive_in_the_ambient_lattice"] is True
    assert theorem["ambient_k3_lattice_is_even_unimodular_signature_3_19"] is True
    assert theorem["orthogonal_complement_has_rank_16"] is True
    assert theorem["orthogonal_complement_is_even_negative_definite_unimodular"] is True
    assert theorem["explicit_k3_seed_contains_primitive_orthogonal_3U_core"] is True


def test_k3_three_u_decomposition_bridge_forces_rank16_negative_definite_complement() -> None:
    summary = build_k3_three_u_decomposition_bridge_summary()
    complement = summary["orthogonal_complement_profile"]

    assert complement["rank"] == 16
    assert complement["positive_directions"] == 0
    assert complement["negative_directions"] == 16
    assert complement["determinant"] == 1
    assert complement["diagonal_even"] is True
    assert complement["unimodular"] is True
