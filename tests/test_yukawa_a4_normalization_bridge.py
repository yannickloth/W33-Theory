from exploration.w33_yukawa_a4_normalization_bridge import (
    build_yukawa_a4_normalization_summary,
)


def test_yukawa_a4_normalization_summary():
    summary = build_yukawa_a4_normalization_summary()
    theorem = summary["a4_normalization_theorem"]

    assert theorem["bridge_packet_is_purely_a4"] is True
    assert theorem["bridge_packet_does_not_shift_A2_or_EH_channel"] is True
    assert theorem["finite_multiplicity_is_81_not_162"] is True
    assert theorem["rank_two_external_activation_is_required"] is True
    assert theorem["exact_reduced_prefactor_is_27_over_16_pi_sq"] is True
    assert theorem["remaining_open_step_is_global_branch_counting_and_orientation"] is True

    product = summary["product_heat_bridge"]
    assert product["a4_convolution"] == "a0*b4 + a2*b2 + a4*b0"
    assert product["pure_external_curvature_packet_is_weighted_by_finite_a0_only"] is True

    gauge = summary["twisted_dirac_gauge"]
    assert gauge["spin_trace_EF"] == "0"
    assert gauge["spin_trace_EF_vanishes"] is True
    assert gauge["a4_gauge_coefficient_in_front_of_TrF2"] == "1/12"
    assert gauge["selfdual_prefactor_per_curved_copy"] == "1/(96*pi**2)"
    assert gauge["bridge_packet_has_no_a2_contamination"] is True

    split = summary["transport_split"]
    assert split["exact_split"] == "81_flat + 81_curved inside the 162-sector"
    assert split["curved_block_trace_multiplier"] == 81
    assert split["only_curved_half_contributes"] is True

    activation = summary["external_activation"]
    assert activation["rank_one_branch_kills_packet"] is True
    assert activation["rank_two_branch_scales_quartically"] is True
    assert activation["C_to_tC_scaling"] == "t**4"

    density = summary["bridge_density"]
    assert density["reduced_density_prefactor"] == "27/(16*pi**2)"
