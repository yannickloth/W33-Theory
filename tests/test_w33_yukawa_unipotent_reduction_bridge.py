from __future__ import annotations

from w33_yukawa_unipotent_reduction_bridge import (
    build_yukawa_unipotent_reduction_summary,
)


def test_active_v4_sectors_reduce_to_two_template_block_spans() -> None:
    summary = build_yukawa_unipotent_reduction_summary()
    h2 = summary["slot_profiles"]["H_2"]
    hbar2 = summary["slot_profiles"]["Hbar_2"]

    assert h2["+-"]["support_labels"] == ["u_c_2", "nu_c"]
    assert h2["-+"]["support_labels"] == ["u_c_1", "u_c_3"]
    assert hbar2["+-"]["support_labels"] == ["d_c_2", "d_c_3", "e_c"]
    assert hbar2["-+"]["support_labels"] == ["d_c_1"]

    assert h2["+-"]["compressed_rank"] == 6
    assert h2["-+"]["compressed_rank"] == 6
    assert hbar2["+-"]["compressed_rank"] == 9
    assert hbar2["-+"]["compressed_rank"] == 3

    for slot in (h2, hbar2):
        for sector in ("+-", "-+"):
            assert slot[sector]["compressed_rank_saturates_three_generation_support"] is True
            assert slot[sector]["block_span_rank"] == 2
            assert slot[sector]["template_pairs"] == [[0, 0], [0, 1]]
            assert slot[sector]["template0_coefficients"] == [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
            ]
            assert slot[sector]["reconstructs_exactly_from_two_templates"] is True


def test_generation_algebra_is_universal_commuting_and_unipotent() -> None:
    summary = build_yukawa_unipotent_reduction_summary()
    algebra = summary["universal_generation_algebra"]

    assert algebra["slot_independent_plus_minus_matrix"] is True
    assert algebra["slot_independent_minus_plus_matrix"] is True
    assert algebra["template0_coefficients_are_identity_for_both_active_sectors"] is True
    assert algebra["plus_minus_generation_matrix"] == [
        [0, 1, 1],
        [-1, 2, 1],
        [1, -1, 1],
    ]
    assert algebra["minus_plus_generation_matrix"] == [
        [0, 1, -1],
        [-1, 2, -1],
        [-1, 1, 1],
    ]
    assert algebra["plus_minus_charpoly"] == "(lambda - 1)**3"
    assert algebra["minus_plus_charpoly"] == "(lambda - 1)**3"
    assert algebra["plus_minus_is_unipotent_jordan_type"] is True
    assert algebra["minus_plus_is_unipotent_jordan_type"] is True
    assert algebra["nilpotent_squares_match_exactly"] is True
    assert algebra["common_nilpotent_square"] == [
        [1, -1, 0],
        [1, -1, 0],
        [0, 0, 0],
    ]
    assert algebra["generation_matrices_commute_exactly"] is True
