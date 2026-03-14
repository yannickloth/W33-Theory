from __future__ import annotations

import json
from pathlib import Path

import pytest

from w33_refinement_bridge_synthesis import (
    build_refinement_bridge_synthesis,
    write_summary,
)


def test_synthesis_keeps_the_dimension_firewall_explicit() -> None:
    summary = build_refinement_bridge_synthesis()
    assert summary["status"] == "ok"
    assert summary["bridge_firewall"]["finite_spectrum_alone_is_insufficient"] is True
    assert summary["bridge_firewall"]["explicit_cover_family_exists"] is True
    assert summary["bridge_firewall"]["tomotope_native_dimension"] == 3.0
    assert summary["bridge_firewall"]["external_refinement_dimension"] == 4.0
    assert summary["bridge_firewall"]["flat_external_scalar_curvature_term"] == 0.0


def test_synthesis_records_curved_external_candidates() -> None:
    summary = build_refinement_bridge_synthesis()
    curved = summary["curved_external_candidates"]
    assert curved["cp2_vertices"] == 9
    assert curved["cp2_euler_characteristic"] == 3
    assert curved["cp2_signature"] == 1
    assert curved["k3_vertices"] == 16
    assert curved["k3_euler_characteristic"] == 24
    assert curved["k3_signature"] == -16
    assert curved["cp2_weyl_l2_floor"] > 0.0
    assert curved["k3_weyl_l2_floor"] > curved["cp2_weyl_l2_floor"]
    assert curved["flat_metric_forbidden_for_cp2"] is True
    assert curved["flat_metric_forbidden_for_k3"] is True
    assert curved["barycentric_top_simplex_multiplier"] == 120


def test_synthesis_records_refinement_invariant_curvature_budget() -> None:
    summary = build_refinement_bridge_synthesis()
    budget = summary["curvature_budget_bridge"]
    assert budget["comparison_seed"] == "T4"
    assert budget["torus_weyl_l2_floor"] == 0.0
    assert budget["cp2_nonconformally_flat_topologically_forced"] is True
    assert budget["k3_nonconformally_flat_topologically_forced"] is True
    assert budget["cp2_hitchin_thorpe_plus"] == 9
    assert budget["cp2_hitchin_thorpe_minus"] == 3
    assert sorted((budget["k3_hitchin_thorpe_plus"], budget["k3_hitchin_thorpe_minus"])) == [0, 96]
    assert budget["refinement_preserves_cp2_chi"] == [3, 3, 3]
    assert budget["refinement_preserves_k3_chi"] == [24, 24, 24]


def test_synthesis_records_explicit_curved_external_complexes() -> None:
    summary = build_refinement_bridge_synthesis()
    complexes = summary["explicit_curved_complexes"]
    assert complexes["cp2_facets"] == 36
    assert complexes["cp2_betti_numbers"] == (1, 0, 1, 0, 1)
    assert complexes["cp2_harmonic_form_total"] == 3
    assert complexes["k3_facets"] == 288
    assert complexes["k3_betti_numbers"] == (1, 0, 22, 0, 1)
    assert complexes["k3_harmonic_form_total"] == 24
    assert complexes["k3_orbit_group_order"] == 240


def test_synthesis_records_explicit_curved_external_operator_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    operators = summary["curved_external_operator_bridge"]
    assert operators["cp2_total_chain_dim"] == 255
    assert operators["cp2_zero_modes_by_degree"] == (1, 0, 1, 0, 1)
    assert operators["cp2_total_spectral_gap"] > 1.9
    assert operators["cp2_trace_dk_squared"] == pytest.approx(1728.0)
    assert operators["k3_total_chain_dim"] == 1704
    assert operators["k3_zero_modes_by_degree"] == (1, 0, 22, 0, 1)
    assert operators["k3_total_spectral_gap"] > 0.68
    assert operators["k3_trace_dk_squared"] == pytest.approx(12480.0)
    assert operators["product_heat_factorizes_on_explicit_spectra"] is True


def test_synthesis_records_curved_refinement_density_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    density = summary["curved_refinement_density_bridge"]
    assert density["vanishing_barycentric_modes"] == [2, 24]
    assert density["external_chain_density_limit"] == "120/19"
    assert density["external_trace_density_limit"] == "860/19"
    assert density["product_chain_density_limit"] == "19440/19"
    assert density["product_trace_density_limit"] == "7512120/19"
    assert density["cp2_six_mode"] == "156/19"
    assert density["k3_six_mode"] == "-880/19"
    assert density["cp2_step4_chain_density"] == pytest.approx(120.0 / 19.0)
    assert density["k3_step4_chain_density"] == pytest.approx(120.0 / 19.0)
    assert density["product_zero_modes_vanish_exactly"] is True


def test_synthesis_records_adjacency_dirac_closure_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["adjacency_dirac_closure_bridge"]
    assert bridge["vertex_laplacian_formula"] == "L0 = 12 I - A"
    assert bridge["vertex_laplacian_matches_formula_exactly"] is True
    assert bridge["vertex_laplacian_spectrum"] == {0: 1, 10: 24, 16: 15}
    assert bridge["edge_harmonic_dimension"] == 81
    assert bridge["edge_exact_dimension"] == 39
    assert bridge["edge_coexact_dimension"] == 120
    assert bridge["exact_one_form_spectrum_is_vertex_nonzero_spectrum"] is True
    assert bridge["triangle_laplacian_is_scalar_4"] is True
    assert bridge["tetrahedron_laplacian_is_scalar_4"] is True
    assert bridge["df2_spectrum"] == {0: 82, 4: 320, 10: 48, 16: 30}
    assert bridge["a0_f"] == 480
    assert bridge["a2_f"] == 2240
    assert bridge["a4_f"] == 17600
    assert bridge["mu_squared"] == "14/3"
    assert bridge["lambda"] == "110/3"
    assert bridge["higgs_ratio_square"] == "14/55"
    assert bridge["full_finite_spectrum_forced_from_adjacency_plus_clique_regularities"] is True


def test_synthesis_records_three_channel_and_dual_bose_mesner_bridges() -> None:
    summary = build_refinement_bridge_synthesis()
    three_channel = summary["three_channel_operator_bridge"]
    dual = summary["dual_bose_mesner_bridge"]
    assert three_channel["basis"] == ["I", "A", "J"]
    assert three_channel["three_entry_classes"] == ["diagonal", "edge", "nonedge"]
    assert three_channel["positive_projector_entry_values"] == {
        "diagonal": "5/8",
        "edge": "1/8",
        "nonedge": "-1/24",
    }
    assert three_channel["laplacian_pseudoinverse_entry_values"] == {
        "diagonal": "267/3200",
        "edge": "7/3200",
        "nonedge": "-13/3200",
    }
    assert three_channel["effective_resistance_adjacent"] == "13/80"
    assert three_channel["effective_resistance_nonadjacent"] == "7/40"
    assert three_channel["kemeny_constant"] == "801/20"
    assert three_channel["exact_mixing_rate"] == "1/3"
    assert dual["w33_constant_projector_matches_exactly"] is True
    assert dual["transport_constant_projector_matches_exactly"] is True
    assert dual["shared_nontrivial_polynomial"] == "x^2 + 2x - 8"
    assert dual["kills_mean_zero_on_w33"] is True
    assert dual["kills_mean_zero_on_transport"] is True
    assert dual["positive_channel_coefficients"] == {"alpha": "2/3", "beta": "1/6"}
    assert dual["negative_channel_coefficients"] == {"alpha": "1/3", "beta": "-1/6"}


def test_synthesis_records_curved_eh_mode_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_eh_mode_bridge"]
    assert "860 a0 + 120 a2" in bridge["master_density_formula"]
    assert "12 a0 + 3 a2" in bridge["master_density_formula"]
    assert "6^r" in bridge["master_integrated_formula"]
    assert bridge["exact_scale_separation"] == "120 / 6 = 20"
    assert bridge["finite_df2_cosmological_limit"] == "681600/19"
    assert bridge["finite_df2_eh_6_mode_coefficient"] == "12480"
    assert bridge["finite_df2_topological_1_mode_coefficient"] == "2240"
    assert bridge["a2_transport_cosmological_limit"] == "423000/19"
    assert bridge["transport_dirac_cosmological_limit"] == "19370040/19"
    assert bridge["matter_transport_dirac_cosmological_limit"] == "1568973240/19"
    assert bridge["cp2_finite_df2_curvature_mode_density"] == "54080/19"
    assert bridge["k3_finite_df2_curvature_mode_density"] == "-114400/57"
    assert bridge["cp2_curvature_sign_matches_signature"] is True
    assert bridge["k3_curvature_sign_matches_signature"] is True


def test_synthesis_records_eh_continuum_lock_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["eh_continuum_lock_bridge"]
    assert bridge["continuum_eh_coefficient"] == "320"
    assert bridge["discrete_eh_6_mode_coefficient"] == "12480"
    assert bridge["rank_factor"] == "39"
    assert bridge["discrete_equals_rank_factor_times_continuum"] is True
    assert bridge["rank_d1"] == 39
    assert bridge["rank_mod_3_adjacency"] == 39
    assert bridge["nontrivial_adjacency_multiplicity_sum"] == 39
    assert bridge["all_rank_39_identifications_agree"] is True
    assert bridge["topological_1_mode_coefficient"] == "2240"
    assert bridge["absolute_euler_characteristic"] == 80
    assert bridge["q_cubic_plus_1"] == 28
    assert bridge["topological_equals_q_cubic_plus_1_times_abs_chi"] is True


def test_synthesis_records_exceptional_channel_continuum_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["exceptional_channel_continuum_bridge"]
    assert bridge["continuum_eh_coefficient"] == 320
    assert bridge["continuum_equals_spinor_e6_times_cartan"] is True
    assert bridge["shared_six_l6_a2_root_support"] == 6
    assert bridge["shared_six_transport_weyl_a2_order"] == 6
    assert bridge["shared_six_firewall_triplet_fibers"] == 6
    assert bridge["shared_six_tomotope_triality_factor"] == 6
    assert bridge["all_shared_six_channels_agree"] is True
    assert bridge["discrete_6_mode_coefficient"] == 12480
    assert bridge["discrete_equals_edges_times_f4"] is True
    assert bridge["discrete_equals_spinor_e6_times_shared_six_times_f4"] is True
    assert bridge["cartan_rank_times_rank39_equals_shared_six_times_f4"] is True
    assert bridge["topological_equals_spinor_e6_times_e7_fund"] is True
    assert bridge["topological_equals_continuum_times_phi6"] is True
    assert bridge["tomotope_automorphism_equals_16_times_shared_six"] is True
    assert bridge["firewall_full_clean_quark_block_exists"] is False


def test_synthesis_records_exceptional_operator_projector_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["exceptional_operator_projector_bridge"]
    assert bridge["spinor_operator_dimension"] == 2304
    assert bridge["channel_ranks"] == {"e6": 40, "a2": 6, "cartan": 8}
    assert bridge["frobenius_channels_are_pairwise_orthogonal_exactly"] is True
    assert bridge["projector_traces_equal_ranks"] is True
    assert bridge["combined_gauge_package_rank"] == 54
    assert bridge["combined_rank_matches_spinor_total_rank"] is True
    assert bridge["e6_generation_preserving"] is True
    assert bridge["a2_generation_mixing_only"] is True
    assert bridge["cartan_generation_preserving"] is True
    assert bridge["continuum_from_projector_ranks"] == 320
    assert bridge["discrete_from_projector_ranks_and_f4"] == 12480
    assert bridge["topological_from_projector_rank_and_e7_fund"] == 2240
    assert bridge["tomotope_from_a2_projector_rank"] == 96
    assert bridge["firewall_triplet_fibers_from_a2_projector_rank"] == 6
    assert bridge["continuum_matches_live_bridge"] is True
    assert bridge["discrete_matches_live_bridge"] is True
    assert bridge["topological_matches_live_bridge"] is True
    assert bridge["tomotope_matches_live_bridge"] is True
    assert bridge["firewall_matches_live_bridge"] is True
    assert bridge["firewall_full_clean_quark_block_exists"] is False


def test_synthesis_records_exceptional_tensor_rank_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["exceptional_tensor_rank_bridge"]
    assert bridge["e6_projector_rank"] == 40
    assert bridge["a2_projector_rank"] == 6
    assert bridge["cartan_projector_rank"] == 8
    assert bridge["a2_transfer_block_rank"] == 16
    assert bridge["all_a2_transfer_blocks_have_rank_16"] is True
    assert bridge["w33_edge_or_e8_root_count"] == 240
    assert bridge["continuum_eh_coefficient"] == 320
    assert bridge["tomotope_automorphism_order"] == 96
    assert bridge["discrete_curvature_coefficient"] == 12480
    assert bridge["topological_coefficient"] == 2240
    assert bridge["edge_count_equals_e6_rank_times_a2_rank"] is True
    assert bridge["continuum_equals_e6_rank_times_cartan_rank"] is True
    assert bridge["tomotope_equals_a2_rank_times_a2_block_rank"] is True
    assert bridge["discrete_equals_edge_count_times_f4"] is True
    assert bridge["topological_equals_e6_rank_times_e7_fund"] is True
    assert bridge["all_promoted_exceptional_counts_match"] is True


def test_synthesis_records_exceptional_residue_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["exceptional_residue_bridge"]
    assert bridge["e6_projector_rank"] == 40
    assert bridge["a2_projector_rank"] == 6
    assert bridge["cartan_projector_rank"] == 8
    assert bridge["edge_or_e8_root_count"] == 240
    assert bridge["discrete_curvature_from_6_pole"] == 12480
    assert bridge["continuum_eh_from_rank39_normalized_6_pole"] == 320
    assert bridge["topological_from_1_pole"] == 2240
    assert bridge["discrete_equals_e6_times_a2_times_f4"] is True
    assert bridge["discrete_equals_edges_times_f4"] is True
    assert bridge["continuum_equals_e6_times_cartan"] is True
    assert bridge["topological_equals_e6_times_e7_fund"] is True
    assert bridge["all_seed_checks_pass"] is True


def test_synthesis_records_curved_inverse_rosetta_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_inverse_rosetta_bridge"]
    assert bridge["w33_vertex_count"] == 40
    assert bridge["w33_edge_or_e8_root_count"] == 240
    assert bridge["spinor_cartan_rank"] == 8
    assert bridge["shared_six_channel"] == 6
    assert bridge["tomotope_automorphism_order"] == 96
    assert bridge["vertex_count_matches"] is True
    assert bridge["edge_count_matches"] is True
    assert bridge["cartan_rank_matches"] is True
    assert bridge["shared_six_matches"] is True
    assert bridge["tomotope_aut_matches"] is True
    assert bridge["all_samples_constant"] is True


def test_synthesis_records_curved_weinberg_lock_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_weinberg_lock_bridge"]
    assert bridge["master_variable"] == "3/13"
    assert bridge["curved_reconstruction_formula"] == "x = 9 * c_EH,cont / c_6"
    assert bridge["cp2_step0_reconstructed_x"] == "3/13"
    assert bridge["cp2_step1_reconstructed_x"] == "3/13"
    assert bridge["k3_step0_reconstructed_x"] == "3/13"
    assert bridge["k3_step1_reconstructed_x"] == "3/13"
    assert bridge["all_curved_samples_match_master_variable"] is True
    assert bridge["exceptional_formula"] == "x = 9 * (40*8) / (40*6*52)"
    assert bridge["exceptional_reconstructed_x"] == "3/13"
    assert bridge["exceptional_matches_master_variable"] is True
    assert bridge["tan_theta_c"] == "3/13"
    assert bridge["sin2_theta_12"] == "4/13"
    assert bridge["sin2_theta_23"] == "7/13"
    assert bridge["sin2_theta_13"] == "2/91"
    assert bridge["omega_lambda"] == "9/13"
    assert bridge["higgs_ratio_square"] == "14/55"
    assert bridge["a2_over_a0"] == "14/3"
    assert bridge["a4_over_a0"] == "110/3"
    assert bridge["discrete_to_continuum_ratio"] == "39"
    assert bridge["all_promoted_observables_match_public_generator_values"] is True


def test_synthesis_records_curved_rosetta_reconstruction_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_rosetta_reconstruction_bridge"]
    assert bridge["master_variable"] == "3/13"
    assert bridge["discrete_to_continuum_ratio"] == "39"
    assert bridge["phi6_from_topological_over_continuum"] == "7"
    assert bridge["vertex_count_from_topological_over_e7_fund"] == 40
    assert bridge["edge_count_from_discrete_over_f4"] == 240
    assert bridge["k_from_two_edges_over_vertices"] == "12"
    assert bridge["q"] == 3
    assert bridge["phi3"] == "13"
    assert bridge["phi6"] == "7"
    assert bridge["srg_data"] == {"v": 40, "k": 12, "lambda": 2, "mu": 4}
    assert bridge["spectral_data"] == {"k": 12, "r": 2, "s": -4}
    assert bridge["all_promoted_observables_match"] is True
    assert bridge["all_samples_constant"] is True


def test_synthesis_records_curved_finite_spectral_reconstruction_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_finite_spectral_reconstruction_bridge"]
    assert bridge["q"] == 3
    assert bridge["line_count"] == 40
    assert bridge["edge_count"] == 240
    assert bridge["triangle_count"] == 160
    assert bridge["tetrahedron_count"] == 40
    assert bridge["betti_numbers"] == {"b0": 1, "b1": 81, "b2": 0, "b3": 0}
    assert bridge["boundary_ranks"] == {"rank_d1": 39, "rank_d2": 120, "rank_d3": 40}
    assert bridge["vertex_laplacian_spectrum"] == {0: 1, 10: 24, 16: 15}
    assert bridge["df2_spectrum"] == {0: 82, 4: 320, 10: 48, 16: 30}
    assert bridge["a0_f"] == 480
    assert bridge["a2_f"] == 2240
    assert bridge["a4_f"] == 17600
    assert bridge["mu_squared"] == "14/3"
    assert bridge["lambda"] == "110/3"
    assert bridge["higgs_ratio_square"] == "14/55"
    assert bridge["df2_spectrum_match"] is True
    assert bridge["moments_match"] is True
    assert bridge["all_samples_constant"] is True


def test_synthesis_records_curved_roundtrip_closure_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_roundtrip_closure_bridge"]
    assert bridge["a0_f"] == 480
    assert bridge["a2_f"] == 2240
    assert bridge["a4_f"] == 17600
    assert bridge["df2_spectrum"] == {0: 82, 4: 320, 10: 48, 16: 30}
    assert bridge["continuum_eh_from_finite"] == "320"
    assert bridge["discrete_eh_from_finite"] == "12480"
    assert bridge["topological_from_finite"] == "2240"
    assert bridge["master_variable_from_roundtrip"] == "3/13"
    assert bridge["continuum_matches"] is True
    assert bridge["discrete_matches"] is True
    assert bridge["topological_matches"] is True
    assert bridge["master_variable_matches"] is True
    assert bridge["all_samples_close_exactly"] is True


def test_synthesis_records_three_sample_master_closure_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["three_sample_master_closure_bridge"]
    assert bridge["minimal_seed"] == "CP2"
    assert bridge["steps"] == [0, 1, 2]
    assert bridge["discrete_eh"] == "12480"
    assert bridge["continuum_eh"] == "320"
    assert bridge["topological_a2"] == "2240"
    assert bridge["master_variable"] == "3/13"
    assert bridge["q"] == 3
    assert bridge["phi3"] == "13"
    assert bridge["phi6"] == "7"
    assert bridge["srg_data"] == {"v": 40, "k": 12, "lambda": 2, "mu": 4}
    assert bridge["spectral_data"] == {"k": 12, "r": 2, "s": -4}
    assert bridge["df2_spectrum"] == {0: 82, 4: 320, 10: 48, 16: 30}
    assert bridge["a0_f"] == 480
    assert bridge["a2_f"] == 2240
    assert bridge["a4_f"] == 17600
    assert bridge["exceptional_data"] == {
        "w33_vertex_count": 40,
        "w33_edge_or_e8_root_count": 240,
        "spinor_cartan_rank": 8,
        "shared_six_channel": 6,
        "tomotope_automorphism_order": 96,
    }
    assert bridge["full_master_closure"] is True


def test_synthesis_records_curvature_cyclotomic_lock_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curvature_cyclotomic_lock_bridge"]
    assert bridge["phi3"] == 13
    assert bridge["phi6"] == 7
    assert bridge["q_phi3"] == 39
    assert bridge["q_plus_1_phi6"] == 28
    assert bridge["gravity_is_q_phi3_times_continuum"] is True
    assert bridge["topology_is_q_plus_1_phi6_times_abs_chi"] is True
    assert bridge["topology_is_q_cubic_plus_1_times_abs_chi"] is True


def test_synthesis_records_q3_curved_selection_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["q3_curved_selection_bridge"]
    assert bridge["gravity_polynomial"] == "q^3 - 2q^2 - 2q - 3"
    assert bridge["gravity_factorization"] == "(q - 3)(q^2 + q + 1)"
    assert bridge["gravity_unique_positive_integer_solution"] == 3
    assert bridge["topology_polynomial"] == "q^2 + q - 12"
    assert bridge["topology_factorization"] == "(q - 3)(q + 4)"
    assert bridge["topology_unique_positive_integer_solution"] == 3


def test_synthesis_records_spectral_action_cyclotomic_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["spectral_action_cyclotomic_bridge"]
    assert bridge["phi3"] == 13
    assert bridge["phi6"] == 7
    assert bridge["four_phi3_plus_q"] == 55
    assert bridge["a2_over_a0"] == "14/3"
    assert bridge["a4_over_a0"] == "110/3"
    assert bridge["higgs_ratio_square"] == "14/55"
    assert bridge["a2_over_a0_matches_formula"] is True
    assert bridge["a4_over_a0_matches_formula"] is True
    assert bridge["higgs_ratio_square_matches_formula"] is True
    assert bridge["continuum_eh_over_a0"] == "2/3"
    assert bridge["discrete_6_mode_over_a0"] == "26"
    assert bridge["discrete_to_continuum_ratio"] == "39"
    assert bridge["continuum_eh_over_a0_matches_formula"] is True
    assert bridge["discrete_6_mode_over_a0_matches_formula"] is True
    assert bridge["discrete_to_continuum_matches_formula"] is True


def test_synthesis_records_spectral_action_q3_selection_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["spectral_action_q3_selection_bridge"]
    assert bridge["internal_polynomial"] == "3q^2 - 10q + 3"
    assert bridge["internal_factorization"] == "(q - 3)(3q - 1)"
    assert bridge["internal_unique_positive_integer_solution"] == 3
    assert bridge["a4_uses_same_polynomial"] is True
    assert bridge["higgs_uses_same_polynomial"] is True
    assert bridge["gravity_polynomial"] == "q^2 + q - 12"
    assert bridge["gravity_factorization"] == "(q - 3)(q + 4)"
    assert bridge["gravity_unique_positive_integer_solution"] == 3


def test_synthesis_records_standard_model_cyclotomic_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["standard_model_cyclotomic_bridge"]
    assert bridge["sin2_theta_w_ew"] == "3/13"
    assert bridge["tan_theta_c"] == "3/13"
    assert bridge["sin2_theta_12"] == "4/13"
    assert bridge["sin2_theta_23"] == "7/13"
    assert bridge["sin2_theta_13"] == "2/91"
    assert bridge["higgs_ratio_square"] == "14/55"
    assert bridge["omega_lambda"] == "9/13"
    assert bridge["tan_cabibbo_equals_ew_weinberg"] is True
    assert bridge["pmns_23_equals_weinberg_plus_pmns_12"] is True
    assert bridge["omega_lambda_equals_q_times_weinberg"] is True
    assert bridge["reactor_has_phi3_phi6_denominator"] is True
    assert bridge["higgs_uses_four_phi3_plus_q_denominator"] is True


def test_synthesis_records_monster_landauer_ternary_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["monster_landauer_ternary_bridge"]
    assert bridge["monster_class"] == "3B"
    assert bridge["shell_states"] == 3**13
    assert bridge["shell_trits"] == 13
    assert bridge["shell_landauer_over_kT"] == "13 ln(3)"
    assert bridge["heisenberg_irrep_states"] == 3**6
    assert bridge["heisenberg_irrep_trits"] == 6
    assert bridge["complement_states"] == 3**7
    assert bridge["complement_trits"] == 7
    assert bridge["logical_qutrits"] == 81
    assert bridge["logical_trits"] == 4
    assert bridge["phi3_equals_shell_trits"] is True
    assert bridge["shared_six_equals_irrep_trits"] is True
    assert bridge["phi6_equals_complement_trits"] is True
    assert bridge["phi6_equals_shell_minus_irrep"] is True
    assert bridge["heisenberg_irrep_equals_q_squared_times_logical_qutrits"] is True
    assert bridge["weinberg_from_generation_over_shell"] == "3/13"
    assert bridge["theta12_from_logical_over_shell"] == "4/13"
    assert bridge["theta23_from_complement_over_shell"] == "7/13"
    assert bridge["weinberg_matches_promoted_value"] is True
    assert bridge["theta12_matches_promoted_value"] is True
    assert bridge["theta23_matches_promoted_value"] is True
    assert bridge["discrete_to_continuum_ratio"] == "39"
    assert bridge["discrete_to_continuum_equals_shell_times_generation_trits"] is True
    assert bridge["topological_over_continuum"] == "7"
    assert bridge["topological_over_continuum_equals_complement_trits"] is True


def test_synthesis_records_monster_shell_factorization_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["monster_shell_factorization_bridge"]
    assert bridge["shell_states"] == 3**13
    assert bridge["heisenberg_states"] == 3**6
    assert bridge["logical_states"] == 3**4
    assert bridge["generation_states"] == 3**3
    assert bridge["complement_states"] == 3**7
    assert bridge["shell_equals_heisenberg_times_logical_times_generation"] is True
    assert bridge["complement_equals_logical_times_generation"] is True
    assert bridge["shell_trits_split"] == [6, 4, 3]
    assert bridge["shell_trits_factorization_exact"] is True
    assert bridge["complement_trits_split"] == [4, 3]
    assert bridge["complement_trits_factorization_exact"] is True
    assert bridge["weinberg_from_generation_over_shell"] == "3/13"
    assert bridge["theta12_from_logical_over_shell"] == "4/13"
    assert bridge["active_heisenberg_share"] == "6/13"
    assert bridge["theta23_from_complement_over_shell"] == "7/13"
    assert bridge["theta23_equals_theta12_plus_weinberg"] is True
    assert bridge["theta23_plus_active_heisenberg_share_equals_one"] is True
    assert bridge["discrete_to_continuum_ratio"] == "39"
    assert bridge["topological_over_continuum"] == "7"
    assert bridge["discrete_to_continuum_equals_shell_times_generation"] is True
    assert bridge["topological_over_continuum_equals_logical_plus_generation"] is True


def test_synthesis_records_monster_3adic_closure_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["monster_3adic_closure_bridge"]
    assert bridge["three_primary_states"] == 3**20
    assert bridge["three_primary_trits"] == 20
    assert bridge["full_landauer_over_kT"] == "20 ln(3)"
    assert bridge["shell_states"] == 3**13
    assert bridge["complement_states"] == 3**7
    assert bridge["full_three_primary_equals_shell_times_complement"] is True
    assert bridge["full_three_primary_equals_heisenberg_times_logical_squared_times_generation_squared"] is True
    assert bridge["full_three_primary_trits_equal_phi3_plus_phi6"] is True
    assert bridge["landauer_additivity_exact"] is True
    assert bridge["shell_share_of_full_monster_three_primary"] == "13/20"
    assert bridge["complement_share_of_full_monster_three_primary"] == "7/20"
    assert bridge["gravity_over_q"] == "13"
    assert bridge["topological_over_continuum"] == "7"
    assert bridge["shell_from_curved_gravity_exact"] is True
    assert bridge["complement_from_curved_topology_exact"] is True
    assert bridge["full_monster_three_primary_from_curved_coefficients_exact"] is True
    assert bridge["monster_three_trits_equal_phi3_plus_phi6"] is True


def test_synthesis_records_monster_3b_centralizer_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["monster_3b_centralizer_bridge"]
    assert bridge["centralizer_label"] == "3^(1+12).2Suz"
    assert bridge["monster_three_primary_states"] == 3**20
    assert bridge["centralizer_three_primary_states"] == 3**20
    assert bridge["centralizer_three_primary_matches_monster"] is True
    assert bridge["shell_states"] == 3**13
    assert bridge["two_suz_three_primary_states"] == 3**7
    assert bridge["two_suz_three_primary_trits"] == 7
    assert bridge["two_suz_three_primary_equals_logical_times_generation"] is True
    assert bridge["landauer_additivity_exact"] is True
    assert bridge["gravity_over_q"] == "13"
    assert bridge["topology_over_continuum"] == "7"
    assert bridge["shell_from_curved_gravity_exact"] is True
    assert bridge["two_suz_from_curved_topology_exact"] is True
    assert bridge["centralizer_three_primary_from_curved_coefficients_exact"] is True


def test_synthesis_records_weinberg_generator_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["weinberg_generator_bridge"]
    assert bridge["generator"] == "3/13"
    assert bridge["tan_theta_c"] == "3/13"
    assert bridge["sin2_theta_12"] == "4/13"
    assert bridge["sin2_theta_23"] == "7/13"
    assert bridge["sin2_theta_13"] == "2/91"
    assert bridge["omega_lambda"] == "9/13"
    assert bridge["higgs_ratio_square"] == "14/55"
    assert bridge["a2_over_a0"] == "14/3"
    assert bridge["a4_over_a0"] == "110/3"
    assert bridge["discrete_6_mode_over_a0"] == "26"
    assert bridge["discrete_to_continuum_ratio"] == "39"
    assert bridge["sin2_theta_23_plus_2weinberg_equals_1"] is True
    assert bridge["sin2_theta_12_equals_four_thirds_weinberg"] is True
    assert bridge["omega_lambda_equals_3weinberg"] is True
    assert bridge["cabibbo_equals_weinberg"] is True
    assert bridge["gravity_ratio_equals_9_over_weinberg"] is True


def test_synthesis_records_weinberg_reconstruction_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["weinberg_reconstruction_bridge"]
    assert bridge["master_variable"] == "3/13"
    assert bridge["from_cabibbo"] == "3/13"
    assert bridge["from_pmns_12"] == "3/13"
    assert bridge["from_pmns_23"] == "3/13"
    assert bridge["from_omega_lambda"] == "3/13"
    assert bridge["from_higgs_ratio"] == "3/13"
    assert bridge["from_a2_over_a0"] == "3/13"
    assert bridge["from_a4_over_a0"] == "3/13"
    assert bridge["from_discrete_6_mode_over_a0"] == "3/13"
    assert bridge["from_discrete_to_continuum_ratio"] == "3/13"
    assert bridge["all_channels_match_master_variable"] is True


def test_synthesis_records_srg_rosetta_lock_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["srg_rosetta_lock_bridge"]
    assert bridge["q_from_lambda_plus_one"] == 3
    assert bridge["phi3_from_k_plus_one"] == 13
    assert bridge["phi6_from_k_minus_lambda_minus_mu_plus_one"] == 7
    assert bridge["sin2_theta_w_ew"] == "3/13"
    assert bridge["sin2_theta_12"] == "4/13"
    assert bridge["sin2_theta_23"] == "7/13"
    assert bridge["sin2_theta_13"] == "2/91"
    assert bridge["omega_lambda"] == "9/13"
    assert bridge["higgs_ratio_square"] == "14/55"
    assert bridge["a2_over_a0"] == "14/3"
    assert bridge["a4_over_a0"] == "110/3"
    assert bridge["discrete_6_mode_over_a0"] == "26"
    assert bridge["discrete_to_continuum_ratio"] == "39"
    assert bridge["all_matches_formula"] is True


def test_synthesis_records_spectral_rosetta_lock_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["spectral_rosetta_lock_bridge"]
    assert bridge["q_from_r_plus_one"] == 3
    assert bridge["phi3_from_k_plus_one"] == 13
    assert bridge["phi6_from_one_plus_r_minus_s"] == 7
    assert bridge["sin2_theta_w_ew"] == "3/13"
    assert bridge["sin2_theta_12"] == "4/13"
    assert bridge["sin2_theta_23"] == "7/13"
    assert bridge["sin2_theta_13"] == "2/91"
    assert bridge["omega_lambda"] == "9/13"
    assert bridge["higgs_ratio_square"] == "14/55"
    assert bridge["a2_over_a0"] == "14/3"
    assert bridge["a4_over_a0"] == "110/3"
    assert bridge["discrete_6_mode_over_a0"] == "26"
    assert bridge["discrete_to_continuum_ratio"] == "39"
    assert bridge["all_matches_formula"] is True


def test_synthesis_records_curved_mode_projector_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_mode_projector_bridge"]
    assert bridge["tower_characteristic_polynomial"] == "x^3 - 127x^2 + 846x - 720"
    assert bridge["p120"] == "((E-6)(E-1))/13566"
    assert bridge["p6"] == "-((E-120)(E-1))/570"
    assert bridge["p1"] == "((E-120)(E-6))/595"
    assert bridge["finite_einstein_hilbert_coefficient"] == "12480"
    assert bridge["cp2_eh_extracted"] == "12480"
    assert bridge["k3_eh_extracted"] == "12480"
    assert bridge["cp2_continuum_eh"] == "320"
    assert bridge["k3_continuum_eh"] == "320"
    assert bridge["all_projector_samples_match"] is True


def test_synthesis_records_curved_mode_residue_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_mode_residue_bridge"]
    assert bridge["generating_function_formula"] == "A/(1 - 120 z) + B/(1 - 6 z) + C/(1 - z)"
    assert bridge["residue_definition"] == "R_alpha(G) = -alpha * Res_{z = 1/alpha} G(z)"
    assert bridge["expected_eh"] == "12480"
    assert bridge["cp2_eh_from_residue"] == "12480"
    assert bridge["k3_eh_from_residue"] == "12480"
    assert bridge["cp2_continuum_from_residue"] == "320"
    assert bridge["k3_continuum_from_residue"] == "320"
    assert bridge["all_seed_residues_match_expected"] is True


def test_synthesis_records_curved_continuum_extractor_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_continuum_extractor_bridge"]
    assert bridge["discrete_eh_formula"] == "-(M_{r+2} - 121 M_{r+1} + 120 M_r) / (570 * six * 6^r)"
    assert bridge["continuum_eh_formula"] == "-(M_{r+2} - 121 M_{r+1} + 120 M_r) / (570 * six * 39 * 6^r)"
    assert bridge["topological_a2_formula"] == "(M_{r+2} - 126 M_{r+1} + 720 M_r) / (595 * chi)"
    assert bridge["expected_discrete_eh"] == "12480"
    assert bridge["expected_continuum_eh"] == "320"
    assert bridge["cp2_step0_continuum_eh"] == "320"
    assert bridge["k3_step0_continuum_eh"] == "320"
    assert bridge["all_samples_match_expected"] is True


def test_synthesis_records_center_quad_exceptional_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["center_quad_exceptional_bridge"]
    assert bridge["center_quads"] == 90
    assert bridge["quotient_points"] == 45
    assert bridge["quotient_lines"] == 27
    assert bridge["incidences"] == 135
    assert bridge["line_graph_vertices"] == 27
    assert bridge["line_graph_degree"] == 10
    assert bridge["line_graph_lambda"] == 1
    assert bridge["line_graph_mu"] == 5
    assert bridge["line_graph_triangles"] == 45
    assert bridge["point_graph_edges"] == 270
    assert bridge["line_lifts_partition_w33"] is True


def test_synthesis_records_center_quad_transport_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["center_quad_transport_bridge"]
    assert bridge["cover_vertices"] == 90
    assert bridge["cover_degree"] == 32
    assert bridge["transport_quotient_vertices"] == 45
    assert bridge["transport_quotient_edges"] == 720
    assert bridge["transport_quotient_degree"] == 32
    assert bridge["raw_z2_distribution"] == {0: 414, 1: 306}
    assert bridge["canonical_z2_distribution"] == {0: 414, 1: 306}
    assert bridge["triangle_count"] == 5280
    assert bridge["triangle_parity0"] == 3120
    assert bridge["triangle_parity1"] == 2160
    assert bridge["v14_triangle_stats_match_exactly"] is True
    assert bridge["transport_edges_270"] == 270
    assert bridge["s3_sheet_pockets"] == 54
    assert bridge["s3_sheet_transport_exact"] is True
    assert bridge["nonzero_sheet_generator"] == ["g3"]
    assert bridge["z2_trivial_but_s3_odd"] is True


def test_synthesis_records_transport_complement_theorem() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["center_quad_transport_complement_bridge"]
    assert bridge["point_graph_degree"] == 12
    assert bridge["point_graph_lambda"] == 3
    assert bridge["point_graph_mu"] == 3
    assert bridge["transport_graph_degree"] == 32
    assert bridge["transport_graph_lambda"] == 22
    assert bridge["transport_graph_mu"] == 24
    assert bridge["transport_is_complement_of_point_graph"] is True
    assert bridge["transport_is_triangle_disjointness_graph"] is True
    assert bridge["all_six_local_s3_matchings"] is True
    assert bridge["raw_z2_not_determined_by_matching_permutation"] is True
    assert bridge["raw_z2_not_determined_by_matching_parity"] is True


def test_synthesis_records_transport_holonomy_theorem() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["center_quad_transport_holonomy_bridge"]
    assert bridge["transport_triangles"] == 5280
    assert bridge["triangle_parity0"] == 3120
    assert bridge["triangle_parity1"] == 2160
    assert bridge["holonomy_cycle_types"] == {
        "identity": 240,
        "three_cycle": 2880,
        "transposition": 2160,
    }
    assert bridge["z2_parity_equals_holonomy_sign_exactly"] is True


def test_synthesis_records_uor_transport_shadow_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["uor_transport_shadow_bridge"]
    assert bridge["shadow_ring"] == "Z/2Z"
    assert bridge["transport_group"] == "Weyl(A2) ~= S3 ~= D3"
    assert bridge["shadow_is_holonomy_sign_not_raw_voltage"] is True
    assert bridge["weyl_group_order"] == 6
    assert bridge["sign_kernel_order"] == 3
    assert bridge["sign_coset_order"] == 3
    assert bridge["edge_sign_shadow_surjective"] is True
    assert bridge["triangle_shadow_forgets_identity_vs_three_cycle"] is True


def test_synthesis_records_transport_path_groupoid_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["transport_path_groupoid_bridge"]
    assert bridge["objects"] == 45
    assert bridge["directed_generators"] == 1440
    assert bridge["tree_edges"] == 44
    assert bridge["fundamental_cycles"] == 676
    assert bridge["tree_edges_gauge_trivialized"] is True
    assert bridge["fundamental_cycle_holonomy_group_order"] == 6
    assert bridge["real_flat_section_dimension"] == 0
    assert bridge["ternary_flat_section_dimension"] == 1
    assert bridge["ternary_invariant_line"] == [1, 2]
    assert bridge["ternary_quotient_character_values"] == [1, 2]


def test_synthesis_records_transport_operator_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["center_quad_transport_operator_bridge"]
    assert bridge["bundle_dimension"] == 135
    assert bridge["bundle_spectrum"] == {
        -16: 6,
        -4: 20,
        -1: 64,
        2: 24,
        8: 20,
        32: 1,
    }
    assert bridge["bundle_laplacian_spectrum"] == {
        0: 1,
        24: 20,
        30: 24,
        33: 64,
        36: 20,
        48: 6,
    }
    assert bridge["trivial_dimension"] == 45
    assert bridge["standard_dimension"] == 90
    assert bridge["trivial_block_equals_transport_adjacency"] is True
    assert bridge["standard_block_spectrum"] == {-16: 6, -1: 64, 8: 20}
    assert bridge["signed_holonomy_spectrum"] == {-4: 30, 8: 15}
    assert bridge["signed_operator_quadratic_identity"] is True
    assert bridge["signed_trace_matches_triangle_excess"] is True


def test_synthesis_records_native_a2_transport_sector() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["center_quad_transport_a2_bridge"]
    assert bridge["fiber_rank"] == 2
    assert bridge["cartan_matrix"] == [[2, -1], [-1, 2]]
    assert bridge["all_six_weyl_matrices_realized"] is True
    assert bridge["determinant_character_equals_permutation_parity"] is True
    assert bridge["a2_operator_dimension"] == 90
    assert bridge["a2_operator_spectrum"] == {-16: 6, -1: 64, 8: 20}
    assert bridge["a2_operator_cubic_relation"] is True
    assert bridge["matches_standard_sector_up_to_local_basis_change"] is True
    assert bridge["triangle_character_sum"] == -2400
    assert bridge["trace_cube_matches_character_sum"] is True


def test_synthesis_records_ternary_homological_code_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["ternary_homological_code_bridge"]
    assert bridge["field"] == "F3"
    assert bridge["physical_qutrits"] == 240
    assert bridge["x_check_rank"] == 39
    assert bridge["z_check_rank"] == 120
    assert bridge["logical_qutrits"] == 81
    assert bridge["stabilizer_rank_total"] == 159
    assert bridge["primal_logical_distance"] == 4
    assert bridge["weight_four_witness_cycle"] == [0, 4, 1, 13]


def test_synthesis_records_transport_ternary_line_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["transport_ternary_line_bridge"]
    assert bridge["real_flat_section_dimension"] == 0
    assert bridge["ternary_flat_section_dimension"] == 1
    assert bridge["invariant_line"] == [1, 2]
    assert bridge["logical_qutrits"] == 81
    assert bridge["canonical_transport_stable_sector_dimension"] == 81
    assert bridge["matter_flavour_dimension"] == 162
    assert bridge["matches_flat_internal_dimension_exactly"] is True


def test_synthesis_records_transport_ternary_extension_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["transport_ternary_extension_bridge"]
    assert bridge["field"] == "F3"
    assert bridge["holonomy_group_order"] == 6
    assert bridge["unique_invariant_line"] == [1, 2]
    assert bridge["invariant_complement_count"] == 0
    assert bridge["top_character_values"] == [1]
    assert bridge["quotient_character_values"] == [1, 2]
    assert bridge["nonsplit_extension_witness_count"] == 4
    assert bridge["is_nonsplit_extension_of_sign_by_trivial"] is True
    assert bridge["base_logical_qutrits"] == 81
    assert bridge["short_exact_sequence_dimensions"] == [81, 162, 81]
    assert bridge["matches_flat_internal_dimension_exactly"] is True


def test_synthesis_records_transport_ternary_cocycle_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["transport_ternary_cocycle_bridge"]
    assert bridge["field"] == "F3"
    assert bridge["adapted_group_order"] == 6
    assert bridge["twisted_cocycle_identity_exact"] is True
    assert bridge["cocycle_values_on_sign_trivial_subgroup"] == [0, 1, 2]
    assert bridge["cocycle_is_not_a_coboundary"] is True
    assert bridge["fiber_shift_rank"] == 1
    assert bridge["fiber_shift_square_zero"] is True
    assert bridge["matter_operator_dimension"] == 162
    assert bridge["matter_operator_rank"] == 81
    assert bridge["matter_operator_square_zero"] is True
    assert bridge["matter_operator_image_equals_kernel"] is True


def test_synthesis_records_transport_curvature_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["transport_curvature_bridge"]
    assert bridge["triangles"] == 5280
    assert bridge["all_six_reduced_holonomy_classes_realized"] is True
    assert bridge["curvature_rank_counts"] == {0: 528, 1: 4752}
    assert bridge["curvature_vanishes_exactly_on_identity_holonomy_triangles"] is True
    assert bridge["global_curvature_operator_rank"] == 42
    assert bridge["global_curvature_operator_nullity"] == 48


def test_synthesis_records_transport_borel_factor_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["transport_borel_factor_bridge"]
    assert bridge["group_order"] == 6
    assert bridge["parity0_total"] == 3120
    assert bridge["parity1_total"] == 2160
    assert bridge["flat_total"] == 528
    assert bridge["pure_nilpotent_total"] == 2592
    assert bridge["semisimple_curved_total"] == 2160
    assert bridge["parity0_splits_as_flat_plus_pure_nilpotent"] is True


def test_synthesis_records_transport_twisted_precomplex_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["transport_twisted_precomplex_bridge"]
    assert bridge["c0_dimension"] == 90
    assert bridge["c1_dimension"] == 1440
    assert bridge["c2_dimension"] == 10560
    assert bridge["d0_rank"] == 89
    assert bridge["d1_rank"] == 1393
    assert bridge["d0_lower_left_block_vanishes"] is True
    assert bridge["d1_lower_left_block_vanishes"] is True
    assert bridge["trivial_h0_dimension"] == 1
    assert bridge["trivial_h1_dimension"] == 0
    assert bridge["sign_h0_flat_dimension"] == 0
    assert bridge["semisimple_curvature_rank"] == 42
    assert bridge["semisimple_curvature_support_triangles"] == 2160
    assert bridge["semisimple_curvature_support_equals_parity1_triangles"] is True
    assert bridge["full_curvature_rank"] == 42
    assert bridge["off_diagonal_curvature_rank"] == 36
    assert bridge["curvature_factors_through_sign_quotient"] is True
    assert bridge["upper_right_curvature_identity_exact"] is True


def test_synthesis_records_transport_matter_curved_harmonic_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["transport_matter_curved_harmonic_bridge"]
    assert bridge["logical_qutrits"] == 81
    assert bridge["matter_extension_dimension"] == 162
    assert bridge["coupled_c0_dimension"] == 7290
    assert bridge["coupled_c1_dimension"] == 116640
    assert bridge["coupled_c2_dimension"] == 855360
    assert bridge["protected_flat_h0_dimension"] == 81
    assert bridge["full_curvature_rank"] == 3402
    assert bridge["off_diagonal_curvature_rank"] == 2916
    assert bridge["cp2_protected_flat_matter_zero_modes"] == 243
    assert bridge["k3_protected_flat_matter_zero_modes"] == 1944
    assert bridge["cp2_curvature_rank_on_harmonics"] == 10206
    assert bridge["k3_curvature_rank_on_harmonics"] == 81648
    assert bridge["protected_flat_sector_is_exactly_one_81_copy"] is True


def test_synthesis_records_transport_spectral_selector_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["transport_spectral_selector_bridge"]
    assert bridge["w33_rank_mod_3"] == 39
    assert bridge["w33_kernel_dimension_mod_3"] == 1
    assert bridge["w33_all_ones_spans_mod_3_kernel"] is True
    assert bridge["transport_projector_rank"] == 1
    assert bridge["transport_walk_gap_exact"] == "7/8"
    assert bridge["transport_kemeny_exact"] == "1952/45"
    assert bridge["a2_positive_laplacian_gap"] == 24
    assert bridge["protected_flat_selector_rank_after_tensoring"] == 81
    assert bridge["matches_protected_flat_matter_dimension"] is True
    assert bridge["protected_flat_curved_harmonic_lifts"] == {
        "CP2_9": 243,
        "K3_16": 1944,
    }


def test_synthesis_records_transport_curved_dirac_refinement_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["transport_curved_dirac_refinement_bridge"]
    assert bridge["transport_dirac_dimension"] == 12090
    assert bridge["transport_trace_d_squared"] == 74772
    assert bridge["transport_curvature_corner_rank"] == 42
    assert bridge["matter_dirac_dimension"] == 979290
    assert bridge["matter_trace_d_squared"] == 6056532
    assert bridge["protected_flat_subsector_dimension"] == 81
    assert bridge["transport_constant_limit"] == "1450800/19"
    assert bridge["transport_linear_limit"] == "19370040/19"
    assert bridge["matter_constant_limit"] == "117514800/19"
    assert bridge["matter_linear_limit"] == "1568973240/19"
    assert bridge["cp2_transport_step0_constant"] == "171275/2"
    assert bridge["k3_matter_step0_linear"] == "78270381"


def test_synthesis_records_transport_curved_dirac_quadratic_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["transport_curved_dirac_quadratic_bridge"]
    assert bridge["transport_trace_d_fourth"] == 2116184
    assert bridge["matter_trace_d_fourth"] == 171410904
    assert bridge["cp2_transport_seed_quadratic"] == "39997843/3"
    assert bridge["k3_transport_seed_quadratic"] == "36601793/3"
    assert bridge["cp2_transport_sd1_quadratic"] == "4701453583/360"
    assert bridge["k3_transport_sd1_quadratic"] == "5052856873/360"
    assert bridge["cp2_matter_seed_quadratic"] == "1079941761"
    assert bridge["k3_matter_sd1_quadratic"] == "45475711857/40"
    assert bridge["transport_first_refinement_contracts_gap"] is True
    assert bridge["matter_first_refinement_contracts_gap"] is True


def test_synthesis_records_curved_a2_transport_product_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_a2_transport_product_bridge"]
    assert bridge["internal_dimension"] == 90
    assert bridge["internal_laplacian_spectrum"] == {24: 20, 33: 64, 48: 6}
    assert bridge["internal_gap"] == 24
    assert bridge["cp2_product_dimension"] == 22950
    assert bridge["cp2_product_trace"] == 889920
    assert bridge["k3_product_dimension"] == 153360
    assert bridge["k3_product_trace"] == 6030720
    assert bridge["product_heat_factorizes_exactly"] is True
    assert bridge["product_chain_density_limit"] == "10800/19"
    assert bridge["product_trace_density_limit"] == "423000/19"


def test_synthesis_records_curved_a2_heat_density_asymptotics() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_a2_heat_density_asymptotics"]
    assert bridge["persistent_gap"] == 24
    assert bridge["constant_limit"] == "10800/19"
    assert bridge["linear_limit"] == "423000/19"
    assert bridge["cp2_constant_corr_20"] == "1170/19"
    assert bridge["cp2_linear_corr_20"] == "42120/19"
    assert bridge["k3_constant_corr_20"] == "-825/19"
    assert bridge["k3_linear_corr_20"] == "-29700/19"
    assert bridge["step_zero_small_t_checks_improve"] is True


def test_synthesis_records_curved_a2_quadratic_seed_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_a2_quadratic_seed_bridge"]
    assert bridge["cp2_external_second_moment"] == 13392
    assert bridge["k3_external_second_moment"] == 128640
    assert bridge["cp2_triangle_tetra_degree_distribution"] == {3: 21, 4: 27, 5: 27, 6: 9}
    assert bridge["k3_triangle_tetra_degree_distribution"] == {3: 80, 4: 240, 7: 240}
    assert bridge["cp2_quadratic_density_coefficient"] == "491580"
    assert bridge["k3_quadratic_density_coefficient"] == "426060"
    assert bridge["second_order_step_zero_prediction_improves_first_order"] is True


def test_synthesis_records_curved_a2_refined_quadratic_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["curved_a2_refined_quadratic_bridge"]
    assert bridge["cp2_sd1_f_vector"] == (255, 2916, 9144, 10800, 4320)
    assert bridge["k3_sd1_f_vector"] == (1704, 22320, 72480, 86400, 34560)
    assert bridge["cp2_sd1_external_second_moment"] == 2104848
    assert bridge["k3_sd1_external_second_moment"] == 22872000
    assert bridge["cp2_sd1_product_quadratic_density_coefficient"] == "908925/2"
    assert bridge["k3_sd1_product_quadratic_density_coefficient"] == "1835497/4"
    assert bridge["seed_quadratic_gap"] == "65520"
    assert bridge["sd1_quadratic_gap"] == "17647/4"
    assert bridge["sd1_f_vectors_match_exact_barycentric_transform_for_both_seeds"] is True
    assert bridge["first_refinement_contracts_cp2_k3_product_quadratic_gap"] is True


def test_synthesis_records_uor_gluing_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["uor_gluing_bridge"]
    assert bridge["all_pairwise_overlaps_are_compatible"] is True
    assert bridge["all_cells_are_covered"] is True
    assert bridge["forward_route_glues_to_canonical_section"] is True
    assert bridge["reverse_route_glues_to_canonical_section"] is True
    assert bridge["full_cover_has_unique_global_section"] is True
    assert bridge["canonical_global_section_is_slot_independent"] is True


def test_synthesis_records_transport_lie_tower_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["transport_lie_tower_bridge"]
    assert bridge["transport_identity_edge_count"] == 192
    assert bridge["transport_reflection_edge_count"] == 396
    assert bridge["transport_three_cycle_edge_count"] == 132
    assert bridge["l6_e6_root_support_size"] == 72
    assert bridge["l6_a2_root_support_size"] == 6
    assert bridge["l6_cartan_support_size"] == 8
    assert bridge["l6_spinor_action_ranks"] == (40, 6, 8)
    assert bridge["complete_oriented_three_generation_graph"] is True
    assert bridge["a2_channels_are_signed_permutation_blocks"] is True
    assert bridge["cartan_modes_are_generation_diagonal"] is True
    assert bridge["current_l6_bridge_activates_only_cartan_modes"] is True


def test_synthesis_records_structural_l6_a2_selection_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["l6_a2_selection_bridge"]
    assert bridge["seed_block_unions_h2"] == [[0, 0], [1, 1], [2, 2]]
    assert bridge["seed_block_unions_hbar2"] == [[0, 0], [1, 1], [2, 2]]
    assert bridge["seed_residual_unions_h2"] == [[0, 0], [1, 1], [2, 2]]
    assert bridge["seed_residual_unions_hbar2"] == [[0, 0], [1, 1], [2, 2]]
    assert bridge["seed_yukawas_are_generation_diagonal"] is True
    assert bridge["seed_residuals_are_generation_diagonal"] is True
    assert bridge["a2_zero_response_mode_indices"] == [127, 128]
    assert bridge["a2_nonzero_mode_indices"] == [8, 9, 246, 247]
    assert bridge["a2_nonzero_channels_are_single_off_diagonal_blocks"] is True
    assert bridge["a2_response_channels_stay_single_off_diagonal_blocks"] is True
    assert bridge["replicated_seed_only_realizes_generation_2_star"] is True
    assert bridge["a2_rhs_is_exactly_zero"] is True
    assert bridge["a2_cartan_cross_gram_is_zero"] is True
    assert bridge["current_l6_solution_has_no_active_a2_modes"] is True
    assert bridge["cartan_only_selection_is_structurally_forced"] is True


def test_synthesis_records_exact_l6_a2_mixed_seed_activation_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["l6_a2_mixed_seed_bridge"]
    assert bridge["base_response_rank"] == 9
    assert bridge["base_augmented_rank"] == 10
    assert bridge["minimal_full_activation_seed_size"] == 2
    assert sorted(bridge["minimal_full_activation_seed_modes"]) == [[8, 9], [246, 247]]
    assert bridge["minimal_full_activation_profiles_are_exactly_fans"] is True
    assert bridge["minimal_rank_lift_seed_size"] == 2
    assert sorted(bridge["minimal_rank_lift_seed_modes"]) == [
        [8, 246],
        [8, 247],
        [9, 246],
        [9, 247],
    ]
    assert bridge["minimal_rank_lift_profiles_are_paths_or_bidirected_edges"] is True
    assert bridge["max_response_rank"] == 11
    assert bridge["max_augmented_rank"] == 12
    assert bridge["fan_closure_seeds_have_full_3x3_support"] is True
    assert bridge["fan_closure_seeds_have_slotwise_isotropic_off_diagonal_shell"] is True
    assert bridge["fan_closure_seeds_keep_all_six_a2_modes_active"] is True
    assert bridge["single_edge_seed_activates_exact_unordered_edge_pair"] is True
    assert bridge["no_exact_closure_within_unit_a2_seed_family"] is True


def test_synthesis_records_l6_a2_v4_mode_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["l6_a2_v4_mode_bridge"]
    assert bridge["all_mode_blocks_are_pure_right_character_twists"] is True
    assert bridge["pure_a_modes_are_exactly_8_and_128"] is True
    assert bridge["pure_b_modes_are_exactly_9_and_127"] is True
    assert bridge["mixed_i_a_ab_modes_are_exactly_246_and_247"] is True
    assert bridge["all_four_v4_characters_already_realized_on_fan_seed"] is True
    assert bridge["dormant_modes_127_128_awaken_as_single_block_channels"] is True


def test_synthesis_records_delta27_envelope_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["l6_delta27_texture_bridge"]
    assert bridge["fan_closures_match_for_both_slots"] is True
    assert bridge["canonical_closure_is_not_cycle_invariant"] is True
    assert bridge["canonical_closure_has_delta27_envelope_shape"] is True
    assert bridge["cycle_orbit_has_three_distinguished_generations"] is True
    assert bridge["h2_distinguished_generation"] == 0
    assert bridge["hbar2_distinguished_generation"] == 0


def test_synthesis_records_delta27_v4_matrix_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["l6_delta27_v4_bridge"]
    assert bridge["all_off_diagonal_blocks_share_exact_support_for_both_slots"] is True
    assert bridge["all_relative_row_signs_are_trivial_for_both_slots"] is True
    assert bridge["all_off_diagonal_blocks_are_exact_right_sign_twists_for_both_slots"] is True
    assert bridge["four_v4_characters_realized_for_both_slots"] is True
    assert bridge["generators_are_commuting_involutions_for_both_slots"] is True
    assert bridge["pair_character_pattern_is_slot_independent"] is True
    assert bridge["cycle_orbit_preserves_v4_structure_for_both_slots"] is True
    assert bridge["h2_active_right_support_labels"] == ["u_c_1", "u_c_2", "u_c_3", "nu_c"]
    assert bridge["hbar2_active_right_support_labels"] == ["d_c_1", "d_c_2", "d_c_3", "e_c"]
    assert bridge["h2_generator_a_flipped_labels"] == ["u_c_1", "u_c_3"]
    assert bridge["h2_generator_b_flipped_labels"] == ["u_c_2", "nu_c"]
    assert bridge["hbar2_generator_a_flipped_labels"] == ["d_c_1"]
    assert bridge["hbar2_generator_b_flipped_labels"] == ["d_c_2", "d_c_3", "e_c"]
    assert bridge["pair_character_labels"] == {
        "0->1": "I",
        "0->2": "A",
        "1->0": "AB",
        "1->2": "A",
        "2->0": "A",
        "2->1": "B",
    }


def test_synthesis_records_v4_projector_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["l6_v4_projector_bridge"]
    assert bridge["minus_minus_projector_vanishes_for_both_slots"] is True
    assert bridge["plus_plus_projector_is_exact_inactive_support_for_both_slots"] is True
    assert bridge["h2_active_support_splits_as_2_plus_2"] is True
    assert bridge["hbar2_active_support_splits_as_1_plus_3"] is True
    assert bridge["h2_plus_minus_support"] == ["u_c_2", "nu_c"]
    assert bridge["h2_minus_plus_support"] == ["u_c_1", "u_c_3"]
    assert bridge["hbar2_plus_minus_support"] == ["d_c_2", "d_c_3", "e_c"]
    assert bridge["hbar2_minus_plus_support"] == ["d_c_1"]


def test_synthesis_records_v4_seed_reconstruction_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["l6_v4_seed_reconstruction_bridge"]
    assert bridge["label_matrix_is_slot_independent"] is True
    assert bridge["expected_label_matrix"] == [
        ["AB", "I", "A"],
        ["AB", "I", "A"],
        ["A", "B", "0"],
    ]
    assert bridge["reconstructs_canonical_closure_exactly_for_both_slots"] is True
    assert bridge["generation_0_diagonal_delta_equals_offdiag_1_to_0_for_both_slots"] is True
    assert bridge["generation_1_diagonal_delta_equals_offdiag_0_to_1_for_both_slots"] is True
    assert bridge["generation_2_diagonal_block_is_unchanged_for_both_slots"] is True
    assert bridge["reference_projector_rank_split_matches_h2_2_plus_2_and_hbar2_3_plus_1"] is True


def test_synthesis_records_v4_closure_selection_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["l6_v4_closure_selection_bridge"]
    assert bridge["forward_fan_is_exact_generation_2_row_for_both_slots"] is True
    assert bridge["reverse_completion_adds_exact_double_ab_i_a_row_for_both_slots"] is True
    assert bridge["reverse_fan_is_exact_two_row_a_column_shell_for_both_slots"] is True
    assert bridge["forward_completion_supplies_exact_missing_ab_i_and_a_b_entries_for_both_slots"] is True
    assert bridge["forward_route_assembles_canonical_label_matrix_for_both_slots"] is True
    assert bridge["reverse_route_assembles_canonical_label_matrix_for_both_slots"] is True
    assert bridge["canonical_label_matrix_is_slot_independent"] is True


def test_synthesis_records_lie_tower_cycle_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["lie_tower_cycle_bridge"]
    assert bridge["l3_support_size"] == 72
    assert bridge["l3_uniform_output_term_count"] == 36
    assert bridge["l4_support_size"] == 81
    assert bridge["l4_uniform_output_term_count"] == 320
    assert bridge["l5_support_size"] == 81
    assert bridge["l5_uniform_output_term_count"] == 3520
    assert bridge["l6_support_size"] == 86
    assert bridge["l6_multi_entry_count"] == 68040
    assert bridge["pure_single_term_layers_before_l6"] is True
    assert bridge["l6_first_full_gauge_return"] is True
    assert bridge["l6_multi_terms_only_cartan_only_democratic"] is True
    assert bridge["l4_effective_mode_count"] == 6
    assert bridge["l6_total_chiral_mode_count"] == 14
    assert bridge["l6_currently_activates_only_cartan"] is True


def test_synthesis_records_lie_tower_s12_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    bridge = summary["lie_tower_s12_bridge"]
    assert bridge["s12_total_nonzero_dimension"] == 728
    assert bridge["s12_grade_split"] == [242, 243, 243]
    assert bridge["s12_jacobi_failure_count"] == 6
    assert bridge["sl27_partition"] == [9, 9, 9]
    assert bridge["sl27_a_family_rank"] == 26
    assert bridge["exact_channel_set_matches_across_layers"] is True
    assert bridge["monster_heisenberg_irrep_dimension"] == 729
    assert bridge["phase_resolution_mechanism_exact"] is True
    assert bridge["current_linearized_l6_bridge_activates_only_cartan_modes"] is True


def test_synthesis_records_local_fano_tomotope_model() -> None:
    summary = build_refinement_bridge_synthesis()
    local = summary["fano_tomotope_local_model"]
    assert local["fano_flags"] == 21
    assert local["dual_toroidal_pair_flags"] == 168
    assert local["tetrahedron_midpoint_flags"] == 24
    assert local["fano_point_stabilizer_order"] == 24
    assert local["fano_flag_stabilizer_order"] == 8
    assert local["flag_stabilizer_is_d8"] is True
    assert local["local_tomotope_flags_per_edge"] == 16


def test_synthesis_records_explicit_mobius_fano_surface_split() -> None:
    summary = build_refinement_bridge_synthesis()
    surface = summary["mobius_fano_surface_bridge"]
    assert surface["standard_heptad_size"] == 7
    assert surface["complementary_heptad_size"] == 7
    assert surface["torus_face_count"] == 14
    assert surface["torus_euler_characteristic"] == 0
    assert surface["each_edge_seen_once_per_heptad"] is True
    assert surface["triangle_vertex_incidences"] == 42
    assert surface["triangle_vertex_incidences_equals_two_fano_flag_sets"] is True


def test_synthesis_records_explicit_abstract_szilassi_dual() -> None:
    summary = build_refinement_bridge_synthesis()
    dual = summary["mobius_szilassi_dual_bridge"]
    assert dual["dual_vertex_count"] == 14
    assert dual["dual_edge_count"] == 21
    assert dual["dual_face_count"] == 7
    assert dual["dual_face_size"] == 6
    assert dual["dual_is_heawood_skeleton"] is True
    assert dual["dual_face_adjacency_is_k7"] is True


def test_synthesis_records_realization_orbit_package() -> None:
    summary = build_refinement_bridge_synthesis()
    realization = summary["realization_orbit_bridge"]
    assert realization["catalog_total"] == 7
    assert realization["common_symmetry_group"] == "Z2"
    assert realization["csaszar_vertex_orbits"] == 4
    assert realization["csaszar_face_orbits"] == 7
    assert realization["szilassi_vertex_orbits"] == 7
    assert realization["szilassi_face_orbits"] == 4
    assert realization["orbit_package_is_dual"] is True


def test_synthesis_records_witting_srg_bridge() -> None:
    summary = build_refinement_bridge_synthesis()
    witting = summary["witting_srg_bridge"]
    assert witting["states"] == 40
    assert witting["orthogonal_tetrads"] == 40
    assert witting["degree"] == 12
    assert witting["lambda_parameter"] == 2
    assert witting["mu_parameter"] == 4
    assert witting["graph_isomorphic_to_standard_w33"] is True
    assert witting["tetrads_match_symplectic_lines"] is True


def test_synthesis_records_cover_and_klitzing_towers() -> None:
    summary = build_refinement_bridge_synthesis()
    tower = summary["cover_and_operation_tower"]
    assert tower["aut_universal_equals_tomotope_flags"] is True
    assert tower["regular_cover_equals_flags_squared"] is True
    assert tower["klitzing_ladder"] == [12, 24, 48, 96]
    assert tower["klitzing_doublings"] == [2, 2, 2]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_refinement_bridge_synthesis_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["focused_test_stack_size"] >= 372
