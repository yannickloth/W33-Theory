import numpy as np

from w33_almost_commutative_candidate import (
    DOWNLIKE_FAMILY,
    UPLIKE_FAMILY,
    all_channel_charge_sums_vanish,
    build_almost_commutative_candidate,
    family_component_residual_norms,
    family_exact_decomposition,
    left_module_action_16,
    right_complex_charge_signs,
    right_module_action_16,
    u1_complex_generator_16,
)


def test_candidate_reports_standard_right_complex_split():
    candidate = build_almost_commutative_candidate()
    assert candidate.right_complex_charge_signs == (1, 1, 1, -1, -1, -1, -1, 1)
    assert right_complex_charge_signs() == candidate.right_complex_charge_signs
    assert candidate.weak_clean_slots == ("H_2", "Hbar_2")


def test_left_and_right_module_actions_commute_for_sample_elements():
    left = left_module_action_16(
        0.25 + 0.75j,
        -0.5 + 0.125j,
        np.array(
            [
                [1, 2j, 0],
                [-2j, 3, 0.5],
                [1.5, 0, -1],
            ],
            dtype=complex,
        ),
    )
    right = right_module_action_16(
        1j,
        np.array(
            [
                [0, 1, 0],
                [1, 0, 0],
                [0, 0, 1],
            ],
            dtype=complex,
        ),
    )
    assert left.shape == (16, 16)
    assert right.shape == (16, 16)
    assert np.allclose(left @ right, right @ left)


def test_u1_complex_generator_has_expected_right_block_signs():
    generator = u1_complex_generator_16()
    diag = np.diag(generator)
    assert np.allclose(diag[:8], 1.0)
    assert tuple(int(x.real) for x in diag[8:]) == (1, 1, 1, -1, -1, -1, -1, 1)


def test_up_family_decomposes_into_exact_leptonic_swap_and_leptoquark_parts():
    decomposition = family_exact_decomposition(UPLIKE_FAMILY)
    for slot in UPLIKE_FAMILY:
        rebuilt = (
            decomposition["sm_leptonic"][slot]
            + decomposition["singlet_swap"][slot]
            + decomposition["leptoquark"][slot]
        )
        assert np.array_equal(rebuilt, decomposition["exact"][slot])

    assert np.count_nonzero(decomposition["leptoquark"]["H_1"]) > 0
    assert np.count_nonzero(decomposition["leptoquark"]["H_2"]) == 0


def test_down_family_decomposes_into_exact_leptonic_swap_and_leptoquark_parts():
    decomposition = family_exact_decomposition(DOWNLIKE_FAMILY)
    for slot in DOWNLIKE_FAMILY:
        rebuilt = (
            decomposition["sm_leptonic"][slot]
            + decomposition["singlet_swap"][slot]
            + decomposition["leptoquark"][slot]
        )
        assert np.array_equal(rebuilt, decomposition["exact"][slot])

    assert np.count_nonzero(decomposition["leptoquark"]["Hbar_1"]) > 0
    assert np.count_nonzero(decomposition["leptoquark"]["Hbar_2"]) == 0


def test_sm_leptonic_projections_are_exactly_hypercharge_compatible():
    up = family_exact_decomposition(UPLIKE_FAMILY)["sm_leptonic"]
    down = family_exact_decomposition(DOWNLIKE_FAMILY)["sm_leptonic"]
    for slot, matrix in {**up, **down}.items():
        assert all_channel_charge_sums_vanish(slot, matrix)


def test_singlet_swap_is_weak_color_clean_but_hypercharge_wrong():
    up = family_exact_decomposition(UPLIKE_FAMILY)["singlet_swap"]
    down = family_exact_decomposition(DOWNLIKE_FAMILY)["singlet_swap"]
    up_residuals = family_component_residual_norms(UPLIKE_FAMILY)["singlet_swap"]
    down_residuals = family_component_residual_norms(DOWNLIKE_FAMILY)["singlet_swap"]
    for slot, matrix in {**up, **down}.items():
        assert not all_channel_charge_sums_vanish(slot, matrix)
    assert up_residuals["H_1"] == 0.0
    assert up_residuals["H_2"] == 0.0
    assert down_residuals["Hbar_1"] == 0.0
    assert down_residuals["Hbar_2"] == 0.0


def test_leptoquark_projection_exactly_sources_weak_color_residual():
    up_residuals = family_component_residual_norms(UPLIKE_FAMILY)
    down_residuals = family_component_residual_norms(DOWNLIKE_FAMILY)

    assert up_residuals["sm_leptonic"]["H_1"] == 0.0
    assert up_residuals["sm_leptonic"]["H_2"] == 0.0
    assert up_residuals["singlet_swap"]["H_1"] == 0.0
    assert up_residuals["singlet_swap"]["H_2"] == 0.0
    assert up_residuals["exact"]["H_1"] == up_residuals["leptoquark"]["H_1"]
    assert up_residuals["exact"]["H_2"] == 0.0
    assert up_residuals["leptoquark"]["H_2"] == 0.0

    assert down_residuals["sm_leptonic"]["Hbar_1"] == 0.0
    assert down_residuals["sm_leptonic"]["Hbar_2"] == 0.0
    assert down_residuals["singlet_swap"]["Hbar_1"] == 0.0
    assert down_residuals["singlet_swap"]["Hbar_2"] == 0.0
    assert down_residuals["exact"]["Hbar_1"] == down_residuals["leptoquark"]["Hbar_1"]
    assert down_residuals["exact"]["Hbar_2"] == 0.0
    assert down_residuals["leptoquark"]["Hbar_2"] == 0.0
