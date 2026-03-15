from __future__ import annotations

from w33_yukawa_kronecker_reduction_bridge import (
    build_yukawa_kronecker_reduction_summary,
)


def test_generation_matrices_are_conjugate_unipotent_jordan_operators() -> None:
    summary = build_yukawa_kronecker_reduction_summary()
    algebra = summary["generation_algebra"]

    assert algebra["plus_minus_matrix"] == [
        [0, 1, 1],
        [-1, 2, 1],
        [1, -1, 1],
    ]
    assert algebra["minus_plus_matrix"] == [
        [0, 1, -1],
        [-1, 2, -1],
        [-1, 1, 1],
    ]
    assert algebra["conjugating_matrix"] == [
        [-2, 1, 0],
        [-1, 0, 0],
        [0, 0, 1],
    ]
    assert algebra["conjugating_matrix_determinant"] == 1
    assert algebra["exact_integer_conjugacy_between_generation_matrices"] is True
    assert algebra["plus_minus_charpoly"] == "(lambda - 1)**3"
    assert algebra["minus_plus_charpoly"] == "(lambda - 1)**3"
    assert algebra["common_jordan_form"] == [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 1],
    ]


def test_all_active_sectors_have_exact_kronecker_and_reduced_gram_forms() -> None:
    summary = build_yukawa_kronecker_reduction_summary()
    theorem = summary["kronecker_reduction_theorem"]
    assert theorem["all_active_sectors_have_exact_kronecker_form"] is True
    assert theorem["all_active_sectors_have_exact_reduced_gram_formula"] is True
    assert theorem["all_active_sector_singular_spectra_match_reduced_gram_exactly"] is True
    assert theorem["template_ranks_match_active_sector_widths"] is True

    h2 = summary["slot_profiles"]["H_2"]
    hbar2 = summary["slot_profiles"]["Hbar_2"]
    assert h2["+-"]["sector_width"] == 2
    assert h2["-+"]["sector_width"] == 2
    assert hbar2["+-"]["sector_width"] == 3
    assert hbar2["-+"]["sector_width"] == 1
    assert h2["+-"]["compressed_rank"] == 6
    assert h2["-+"]["compressed_rank"] == 6
    assert hbar2["+-"]["compressed_rank"] == 9
    assert hbar2["-+"]["compressed_rank"] == 3
