from fractions import Fraction
import math

import numpy as np

from w33_induced_quark_yukawa import (
    BACKGROUND_SLOT_NAMES,
    DEFAULT_BACKGROUND_COEFFS,
    best_heavy_background_search,
    build_induced_quark_yukawa_candidate,
    hypercharge_projected_induced_yukawa_8x8,
)


def test_bounded_search_selects_max_rank_heavy_background_representative():
    search = best_heavy_background_search()

    assert search.background_slots == BACKGROUND_SLOT_NAMES
    assert search.background_coeffs == DEFAULT_BACKGROUND_COEFFS
    assert search.search_bound == 3
    assert search.heavy_background_rank == 4
    assert search.total_quark_support == 32
    assert search.total_lepton_support == 4
    assert math.isclose(search.total_quark_residual, 1.0290319770177434)
    assert math.isclose(search.total_projected_residual, search.total_quark_residual)


def test_induced_candidate_has_expected_channel_support_and_heavy_basis():
    candidate = build_induced_quark_yukawa_candidate()

    assert candidate.background_coeffs == DEFAULT_BACKGROUND_COEFFS
    assert candidate.heavy_basis_slots == (
        "S",
        "T_1",
        "T_2",
        "T_3",
        "H_1",
        "H_2",
        "Tbar_1",
        "Tbar_2",
        "Tbar_3",
        "Hbar_1",
        "Hbar_2",
    )
    assert candidate.heavy_background_rank == 4
    assert candidate.total_quark_support == 32
    assert candidate.total_lepton_support == 4
    assert candidate.up_channel.supported_sm_pairs == (("L", "nu_c"), ("Q", "u_c"))
    assert candidate.down_channel.supported_sm_pairs == (("L", "e_c"), ("Q", "d_c"))


def test_projected_induced_yukawas_have_expected_exact_rational_entries():
    up = hypercharge_projected_induced_yukawa_8x8("H_2", DEFAULT_BACKGROUND_COEFFS)
    down = hypercharge_projected_induced_yukawa_8x8("Hbar_2", DEFAULT_BACKGROUND_COEFFS)

    assert up[0][0] == Fraction(1, 20)
    assert up[0][1] == Fraction(1, 24)
    assert up[4][0] == Fraction(1, 120)
    assert up[6][7] == Fraction(1, 48)
    assert up[7][7] == Fraction(1, 20)

    assert down[0][3] == Fraction(1, 48)
    assert down[1][5] == Fraction(-11, 120)
    assert down[3][3] == Fraction(-1, 20)
    assert down[6][6] == Fraction(1, 20)
    assert down[7][6] == Fraction(-1, 48)


def test_remaining_induced_residual_sits_on_quark_blocks_not_leptons():
    candidate = build_induced_quark_yukawa_candidate()

    assert candidate.up_channel.quark_rank == 2
    assert candidate.down_channel.quark_rank == 2
    assert candidate.up_channel.lepton_rank == 1
    assert candidate.down_channel.lepton_rank == 1

    assert np.allclose(
        candidate.up_channel.quark_singular_values,
        (0.10675419420266109, 0.05279744120616351, 0.0),
        atol=1e-12,
    )
    assert np.allclose(
        candidate.down_channel.quark_singular_values,
        (0.13446544401435329, 0.06764092227359728, 0.0),
        atol=1e-12,
    )

    assert candidate.up_channel.lepton_residual_norm == 0.0
    assert candidate.down_channel.lepton_residual_norm == 0.0
    assert math.isclose(candidate.up_channel.total_residual_norm, 0.4346134936801766)
    assert math.isclose(candidate.down_channel.total_residual_norm, 0.594418483337567)
    assert math.isclose(candidate.up_channel.quark_residual_norm, candidate.up_channel.total_residual_norm)
    assert math.isclose(candidate.down_channel.quark_residual_norm, candidate.down_channel.total_residual_norm)
