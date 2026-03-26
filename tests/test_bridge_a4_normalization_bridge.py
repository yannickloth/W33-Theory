from exploration.w33_bridge_a4_normalization_bridge import (
    build_bridge_a4_normalization_summary,
)


def test_bridge_a4_normalization_summary():
    summary = build_bridge_a4_normalization_summary()

    gamma = summary["gamma_bivector_checks"]
    assert gamma["euclidean_anticommutator_checks_pass"] is True
    assert gamma["diagonal_basis_traces"] == [-4, -4, -4, -4, -4, -4]
    assert gamma["off_diagonal_basis_traces_vanish"] is True
    assert gamma["spin_trace_of_each_bivector_vanishes"] is True

    coeff = summary["local_a4_gauge_coefficient"]
    assert coeff["tr_spin_EF_squared_in_units_of_F_sq"] == "-1/2"
    assert coeff["from_half_E_squared"] == "-1/4"
    assert coeff["from_omega_squared"] == "1/3"
    assert coeff["total_in_front_of_Tr_F_sq"] == "1/12"
    assert coeff["selfdual_4form_prefactor_per_curved_copy"] == "1/(96 pi^2)"

    finite = summary["finite_multiplier"]
    assert finite["trace_0"] == 81
    assert finite["delta_A4"] == "1209/9194 a0"
    assert finite["delta_A4_equals_81_epsilon_squared_a0"] is True
    assert finite["first_family_entry_is_A4_only"] is True

    density = summary["refined_density_channel"]
    assert density["delta_A4_density_formula"] == "epsilon^2 * A0_density(n)"
    assert density["epsilon_squared"] == "403/248238"
    assert density["first_family_sensitive_density_stays_on_A0_channel"] is True

    prefactor = summary["reduced_local_bridge_prefactor"]
    assert prefactor["before_universal_rank2_factor_2"] == "27/(32 pi^2)"
    assert prefactor["after_universal_rank2_factor_2"] == "27/(16 pi^2)"

    theorem = summary["bridge_theorem"]
    assert theorem["local_gauge_packet_is_pure_A4"] is True
    assert theorem["exact_finite_multiplier_is_repo_native_81"] is True
    assert theorem["reduced_local_prefactor_is_27_over_16_pi_squared"] is True
    assert theorem["global_orientation_and_integration_remain_open"] is True
