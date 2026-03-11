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
    assert data["focused_test_stack_size"] == 294
