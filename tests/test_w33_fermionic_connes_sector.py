from collections import Counter

import numpy as np

from w33_fermionic_connes_sector import (
    DOWNLIKE_HIGGS_SLOT_NAMES,
    FERMION_MATTER_DIM,
    FERMION_TOTAL_DIM,
    HIGGS_SLOT_NAMES,
    UPLIKE_HIGGS_SLOT_NAMES,
    build_fermionic_connes_sector_candidate,
    canonical_spinor_basis,
    chiral_grading_16,
    clean_higgs_slots,
    color_generator_names,
    fermionic_dirac_for_higgs_slot_16,
    higgs_yukawa_slices_8x8,
    left_spinor_basis,
    right_spinor_basis,
    sample_order_one_residual_map,
    sample_order_one_residual_norm,
    sample_order_one_residuals_for_slot,
    sample_order_zero_residuals,
    weak_generator_names,
)


def test_spinor_basis_matches_expected_16_plet_counts():
    basis = canonical_spinor_basis()
    assert len(basis) * 3 == FERMION_MATTER_DIM
    assert 2 * FERMION_MATTER_DIM == FERMION_TOTAL_DIM

    counts = Counter(state.sm for state in basis)
    assert counts == Counter(
        {
            "Q": 6,
            "u_c": 3,
            "d_c": 3,
            "L": 2,
            "e_c": 1,
            "nu_c": 1,
        }
    )


def test_spinor_basis_has_left_right_8_plus_8_split():
    left = left_spinor_basis()
    right = right_spinor_basis()

    assert len(left) == 8
    assert len(right) == 8
    assert [state.slot for state in left] == [
        "Q_1_1",
        "Q_1_2",
        "Q_2_1",
        "Q_2_2",
        "Q_3_1",
        "Q_3_2",
        "L_1",
        "L_2",
    ]
    assert [state.slot for state in right] == [
        "u_c_1",
        "u_c_2",
        "u_c_3",
        "d_c_1",
        "d_c_2",
        "d_c_3",
        "e_c",
        "nu_c",
    ]


def test_each_exact_higgs_slice_has_rank_two_on_left_right_fermion_split():
    slices = higgs_yukawa_slices_8x8()
    assert set(slices) == set(HIGGS_SLOT_NAMES)
    for slot in HIGGS_SLOT_NAMES:
        matrix = slices[slot]
        assert matrix.shape == (8, 8)
        assert np.linalg.matrix_rank(matrix.astype(float)) == 2


def test_fermionic_dirac_slices_are_odd_for_chiral_grading():
    grading = chiral_grading_16()
    for slot in HIGGS_SLOT_NAMES:
        dirac = fermionic_dirac_for_higgs_slot_16(slot)
        assert dirac.shape == (16, 16)
        assert np.array_equal(dirac, dirac.T)
        assert np.allclose(grading @ dirac, -dirac @ grading)


def test_sample_order_zero_screen_is_exact():
    residuals = sample_order_zero_residuals()
    assert set(name for name, _ in residuals) == set(weak_generator_names())
    assert set(name for _, name in residuals) == set(color_generator_names())
    for residual in residuals.values():
        assert np.allclose(residual, 0.0)


def test_clean_higgs_directions_are_selected_exactly():
    assert clean_higgs_slots() == ("H_2", "Hbar_2")
    assert sample_order_one_residual_norm("H_2") == 0.0
    assert sample_order_one_residual_norm("Hbar_2") == 0.0
    assert sample_order_one_residual_norm("H_1") > 0.0
    assert sample_order_one_residual_norm("Hbar_1") > 0.0


def test_clean_higgs_slots_have_zero_sample_order_one_residuals():
    for slot in ("H_2", "Hbar_2"):
        for residual in sample_order_one_residuals_for_slot(slot).values():
            assert np.allclose(residual, 0.0)


def test_each_higgs_pair_has_one_dimensional_clean_subspace_under_screen():
    up_map = sample_order_one_residual_map(UPLIKE_HIGGS_SLOT_NAMES)
    down_map = sample_order_one_residual_map(DOWNLIKE_HIGGS_SLOT_NAMES)
    assert up_map.shape[1] == 2
    assert down_map.shape[1] == 2
    assert np.linalg.matrix_rank(up_map) == 1
    assert np.linalg.matrix_rank(down_map) == 1


def test_candidate_summary_reports_clean_higgs_slots():
    candidate = build_fermionic_connes_sector_candidate()
    assert candidate.clean_higgs_slots == ("H_2", "Hbar_2")
    assert candidate.weak_generator_names == weak_generator_names()
    assert candidate.color_generator_names == color_generator_names()
