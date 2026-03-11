"""Synthesis of the March 2026 refinement / tomotope bridge program.

This module consolidates the bridge work developed across the recent
explorations:

- tomotope infinite-cover tower;
- exact almost-commutative product with a 4D external factor;
- flat spectral-action coefficients from the exact W33 finite Dirac operator;
- curved 4D seed geometries from minimal triangulations of CP2 and K3;
- surface/Fano/tetrahedron/tomotope flag bridges;
- exact order identities for U_{t,ho} -> T -> R2;
- the Klitzing tomotope operation ladder.

The point is to state one defensible combined verdict:

1. A finite seed can generate infinite towers, so the bridge is not blocked by
   finiteness alone.
2. The explicit tomotope tower is still natively cubic, so it does not by itself
   produce the missing 4D Weyl-law theorem.
3. The mathematically coherent route is now visible: exact finite internal data
   plus a genuine curved 4D refinement family.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    for candidate in (ROOT, ROOT / "tools"):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
else:
    ROOT = Path(__file__).resolve().parents[1]

from tomotope_cover_bridge import build_cover_bridge_summary
from w33_center_quad_transport_a2_bridge import build_center_quad_transport_a2_summary
from w33_curved_a2_heat_density_asymptotics import build_curved_a2_heat_density_asymptotics_summary
from w33_curved_a2_quadratic_seed_bridge import build_curved_a2_quadratic_seed_bridge_summary
from w33_curved_a2_refined_quadratic_bridge import build_curved_a2_refined_quadratic_bridge_summary
from w33_curved_a2_transport_product import build_curved_a2_transport_product_summary
from w33_center_quad_gq42_e6_bridge import build_center_quad_gq42_e6_bridge_summary
from w33_center_quad_transport_bridge import build_center_quad_transport_bridge_summary
from w33_center_quad_transport_complement_bridge import build_center_quad_transport_complement_summary
from w33_center_quad_transport_holonomy_bridge import build_center_quad_transport_holonomy_summary
from w33_center_quad_transport_operator_bridge import build_center_quad_transport_operator_summary
from w33_exceptional_triad_bridge import build_exceptional_triad_summary
from w33_curved_barycentric_density_bridge import build_curved_barycentric_density_bridge_summary
from w33_curved_4d_curvature_budget import build_curved_4d_curvature_budget_summary
from w33_curved_external_hodge_product import build_curved_external_hodge_product_summary
from w33_explicit_curved_4d_complexes import build_explicit_curved_4d_complexes_summary
from w33_fano_group_bridge import build_fano_group_summary
from w33_fano_square_tomotope_bridge import build_fano_square_tomotope_summary
from w33_flat_ac_spectral_action import build_flat_product_summary
from w33_minimal_triangulation_bridge import build_minimal_triangulation_summary
from w33_mobius_fano_bridge import build_mobius_fano_summary
from w33_mobius_szilassi_dual import build_mobius_szilassi_dual_summary
from w33_realization_orbit_bridge import build_realization_orbit_summary
from w33_surface_neighborly_bridge import build_surface_neighborly_summary
from w33_witting_srg_bridge import build_witting_srg_bridge_summary
from w33_tomotope_ac_bridge import build_bridge_summary
from w33_tomotope_klitzing_ladder import build_klitzing_ladder_summary
from w33_tomotope_order_bridge import build_tomotope_order_summary
from w33_torus_refinement_bridge import build_refinement_summary
from w33_lie_tower_cycle_bridge import build_lie_tower_cycle_bridge_summary
from w33_lie_tower_s12_bridge import build_lie_tower_s12_bridge_summary
from w33_l6_a2_selection_bridge import build_l6_a2_selection_bridge_summary
from w33_l6_a2_mixed_seed_bridge import build_l6_a2_mixed_seed_bridge_summary
from w33_l6_a2_v4_mode_bridge import build_l6_a2_v4_mode_bridge_summary
from w33_l6_delta27_texture_bridge import build_l6_delta27_texture_bridge_summary
from w33_l6_delta27_v4_bridge import build_l6_delta27_v4_bridge_summary
from w33_l6_v4_projector_bridge import build_l6_v4_projector_bridge_summary
from w33_l6_v4_closure_selection_bridge import build_l6_v4_closure_selection_bridge_summary
from w33_l6_v4_seed_reconstruction_bridge import build_l6_v4_seed_reconstruction_bridge_summary
from w33_transport_lie_tower_bridge import build_transport_lie_tower_bridge_summary
from w33_uor_gluing_bridge import build_w33_uor_gluing_summary
from w33_uor_transport_shadow_bridge import build_w33_uor_transport_shadow_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_refinement_bridge_synthesis_summary.json"


@lru_cache(maxsize=1)
def build_refinement_bridge_synthesis() -> dict[str, Any]:
    cover = build_cover_bridge_summary()
    ac_bridge = build_bridge_summary()
    torus = build_refinement_summary()
    flat = build_flat_product_summary()
    center_quad_transport_a2 = build_center_quad_transport_a2_summary()
    curved_a2_asymptotics = build_curved_a2_heat_density_asymptotics_summary()
    curved_a2_quadratic = build_curved_a2_quadratic_seed_bridge_summary()
    curved_a2_refined_quadratic = build_curved_a2_refined_quadratic_bridge_summary()
    curved_a2_product = build_curved_a2_transport_product_summary()
    center_quad = build_center_quad_gq42_e6_bridge_summary()
    center_quad_transport = build_center_quad_transport_bridge_summary()
    center_quad_transport_complement = build_center_quad_transport_complement_summary()
    center_quad_transport_holonomy = build_center_quad_transport_holonomy_summary()
    center_quad_transport_operator = build_center_quad_transport_operator_summary()
    barycentric_density = build_curved_barycentric_density_bridge_summary()
    curvature_budget = build_curved_4d_curvature_budget_summary()
    curved_operator = build_curved_external_hodge_product_summary()
    explicit_complexes = build_explicit_curved_4d_complexes_summary()
    triangulations = build_minimal_triangulation_summary()
    surface = build_surface_neighborly_summary()
    mobius = build_mobius_fano_summary()
    mobius_dual = build_mobius_szilassi_dual_summary()
    realization = build_realization_orbit_summary()
    witting = build_witting_srg_bridge_summary()
    lie_tower_cycle = build_lie_tower_cycle_bridge_summary()
    lie_tower_s12 = build_lie_tower_s12_bridge_summary()
    l6_a2_selection = build_l6_a2_selection_bridge_summary()
    l6_a2_mixed_seed = build_l6_a2_mixed_seed_bridge_summary()
    l6_a2_v4_modes = build_l6_a2_v4_mode_bridge_summary()
    l6_delta27_texture = build_l6_delta27_texture_bridge_summary()
    l6_delta27_v4 = build_l6_delta27_v4_bridge_summary()
    l6_v4_projectors = build_l6_v4_projector_bridge_summary()
    l6_v4_closure_selection = build_l6_v4_closure_selection_bridge_summary()
    l6_v4_seed_reconstruction = build_l6_v4_seed_reconstruction_bridge_summary()
    transport_lie = build_transport_lie_tower_bridge_summary()
    uor_gluing = build_w33_uor_gluing_summary()
    uor_transport_shadow = build_w33_uor_transport_shadow_summary()
    fano_group = build_fano_group_summary()
    fano_square = build_fano_square_tomotope_summary()
    order = build_tomotope_order_summary()
    klitzing = build_klitzing_ladder_summary()
    exceptional = build_exceptional_triad_summary()

    cp2 = triangulations["seeds"][0]
    k3 = triangulations["seeds"][1]
    cp2_budget = curvature_budget["curved_seeds"][0]
    k3_budget = curvature_budget["curved_seeds"][1]
    cp2_density = barycentric_density["seed_decompositions"][0]
    k3_density = barycentric_density["seed_decompositions"][1]
    cp2_operator = curved_operator["external_profiles"][0]
    k3_operator = curved_operator["external_profiles"][1]
    cp2_complex = explicit_complexes["profiles"][0]
    k3_complex = explicit_complexes["profiles"][1]
    local_square = fano_group["local_square_bridge"]
    flat_coeffs = flat["coefficients"]
    torus_t005 = [entry for entry in torus["comparisons"] if entry["t"] == 0.05]

    return {
        "status": "ok",
        "bridge_firewall": {
            "finite_spectrum_alone_is_insufficient": True,
            "explicit_cover_family_exists": True,
            "tomotope_native_dimension": cover["native_scaling"]["carrier_growth_degree"],
            "external_refinement_dimension": ac_bridge["bridge_level"]["external_growth_degree"],
            "flat_external_scalar_curvature_term": flat_coeffs["external_scalar_curvature_term"],
            "external_refinement_error_at_t_0_05_for_n_24": torus_t005[-1]["external_abs_error"],
        },
        "exact_internal_bridge": {
            "w33_internal_dimension": flat_coeffs["internal_dimension"],
            "trace_d2": flat_coeffs["trace_d2"],
            "trace_d4": flat_coeffs["trace_d4"],
            "witting_srg_vertices": witting["orthogonality_graph"]["vertices"],
            "witting_srg_degree": witting["orthogonality_graph"]["degree"],
            "witting_tetrads": witting["paper_system"]["orthogonal_tetrads"],
            "tomotope_flag_count": order["tomotope"]["flags"],
            "minimal_regular_cover_order": order["minimal_regular_cover"]["automorphism_group_order"],
        },
        "center_quad_exceptional_bridge": {
            "center_quads": center_quad["w33_seed"]["center_quads"],
            "quotient_points": center_quad["dual_gq42_incidence"]["points"],
            "quotient_lines": center_quad["dual_gq42_incidence"]["lines"],
            "incidences": center_quad["dual_gq42_incidence"]["incidences"],
            "line_graph_vertices": center_quad["exceptional_graphs"]["line_graph_srg"]["vertices"],
            "line_graph_degree": center_quad["exceptional_graphs"]["line_graph_srg"]["degree"],
            "line_graph_lambda": center_quad["exceptional_graphs"]["line_graph_srg"]["lambda"],
            "line_graph_mu": center_quad["exceptional_graphs"]["line_graph_srg"]["mu"],
            "line_graph_triangles": center_quad["exceptional_graphs"]["line_graph_triangles"],
            "point_graph_edges": center_quad["exceptional_graphs"]["point_graph_srg"]["edge_count"],
            "line_lifts_partition_w33": center_quad["quotient_cover"]["line_lift_partitions_all_40_w33_vertices"],
        },
        "center_quad_transport_bridge": {
            "cover_vertices": center_quad_transport["cover_graph"]["vertices"],
            "cover_degree": next(iter(center_quad_transport["cover_graph"]["degree_distribution"])),
            "transport_quotient_vertices": center_quad_transport["quotient_graph"]["vertices"],
            "transport_quotient_edges": center_quad_transport["quotient_graph"]["edges"],
            "transport_quotient_degree": next(iter(center_quad_transport["quotient_graph"]["degree_distribution"])),
            "raw_z2_distribution": center_quad_transport["quotient_graph"]["raw_z2_distribution"],
            "canonical_z2_distribution": center_quad_transport["quotient_graph"]["canonical_z2_distribution"],
            "triangle_count": center_quad_transport["triangle_parity"]["reconstructed"]["num_triangles"],
            "triangle_parity0": center_quad_transport["triangle_parity"]["reconstructed"]["parity0"],
            "triangle_parity1": center_quad_transport["triangle_parity"]["reconstructed"]["parity1"],
            "v14_triangle_stats_match_exactly": all(
                center_quad_transport["triangle_parity"]["matches_archived_exactly"].values()
            ),
            "transport_edges_270": center_quad_transport["transport_refinement"]["transport_edges_270"],
            "s3_sheet_pockets": center_quad_transport["transport_refinement"]["s3_sheet_pockets"],
            "s3_sheet_transport_exact": center_quad_transport["transport_refinement"]["s3_sheet_transport_exact"],
            "nonzero_sheet_generator": center_quad_transport["transport_refinement"]["nonzero_sheet_generator"],
            "z2_trivial_but_s3_odd": center_quad_transport["v16_edge_lift"]["z2_trivial_but_s3_odd"],
        },
        "center_quad_transport_complement_bridge": {
            "point_graph_degree": center_quad_transport_complement["point_graph_srg"]["degree"],
            "point_graph_lambda": center_quad_transport_complement["point_graph_srg"]["lambda"],
            "point_graph_mu": center_quad_transport_complement["point_graph_srg"]["mu"],
            "transport_graph_degree": center_quad_transport_complement["transport_graph_srg"]["degree"],
            "transport_graph_lambda": center_quad_transport_complement["transport_graph_srg"]["lambda"],
            "transport_graph_mu": center_quad_transport_complement["transport_graph_srg"]["mu"],
            "transport_is_complement_of_point_graph": center_quad_transport_complement["complement_theorem"]["transport_is_complement_of_point_graph"],
            "transport_is_triangle_disjointness_graph": center_quad_transport_complement["complement_theorem"]["transport_edges_are_exactly_disjoint_triangle_pairs"],
            "all_six_local_s3_matchings": center_quad_transport_complement["local_s3_matching"]["all_six_permutations_realized_under_sorted_labels"],
            "raw_z2_not_determined_by_matching_permutation": center_quad_transport_complement["local_s3_matching"]["raw_z2_not_determined_by_permutation"],
            "raw_z2_not_determined_by_matching_parity": center_quad_transport_complement["local_s3_matching"]["raw_z2_not_determined_by_permutation_parity"],
        },
        "center_quad_transport_holonomy_bridge": {
            "transport_triangles": center_quad_transport_holonomy["transport_triangles"],
            "triangle_parity0": center_quad_transport_holonomy["archived_v14_triangle_parity"]["parity0"],
            "triangle_parity1": center_quad_transport_holonomy["archived_v14_triangle_parity"]["parity1"],
            "holonomy_cycle_types": center_quad_transport_holonomy["triangle_holonomy"]["cycle_type_counts"],
            "z2_parity_equals_holonomy_sign_exactly": center_quad_transport_holonomy["triangle_holonomy"]["z2_parity_equals_holonomy_sign_exactly"],
        },
        "uor_transport_shadow_bridge": {
            "shadow_ring": uor_transport_shadow["uor_alignment"]["coefficient_shadow_ring"],
            "transport_group": uor_transport_shadow["uor_alignment"]["nonabelian_transport_group"],
            "shadow_is_holonomy_sign_not_raw_voltage": uor_transport_shadow["uor_alignment"]["right_binary_shadow_is_holonomy_sign_not_raw_edge_voltage"],
            "weyl_group_order": uor_transport_shadow["weyl_group_shadow"]["group_closure_order"],
            "sign_kernel_order": uor_transport_shadow["weyl_group_shadow"]["sign_kernel_order"],
            "sign_coset_order": uor_transport_shadow["weyl_group_shadow"]["sign_nontrivial_coset_order"],
            "edge_sign_shadow_surjective": uor_transport_shadow["weyl_group_shadow"]["edge_sign_character_is_surjective"],
            "triangle_shadow_forgets_identity_vs_three_cycle": uor_transport_shadow["triangle_shadow"]["z2_shadow_forgets_identity_vs_three_cycle"],
        },
        "center_quad_transport_operator_bridge": {
            "bundle_dimension": center_quad_transport_operator["connection_bundle"]["total_dimension"],
            "bundle_spectrum": center_quad_transport_operator["connection_bundle"]["adjacency_spectrum"],
            "bundle_laplacian_spectrum": center_quad_transport_operator["connection_bundle"]["laplacian_spectrum"],
            "trivial_dimension": center_quad_transport_operator["trivial_standard_split"]["trivial_dimension"],
            "standard_dimension": center_quad_transport_operator["trivial_standard_split"]["standard_dimension"],
            "trivial_block_equals_transport_adjacency": center_quad_transport_operator["trivial_standard_split"]["trivial_block_equals_transport_adjacency"],
            "standard_block_spectrum": center_quad_transport_operator["trivial_standard_split"]["standard_block_spectrum"],
            "signed_holonomy_spectrum": center_quad_transport_operator["signed_holonomy_operator"]["spectrum"],
            "signed_operator_quadratic_identity": center_quad_transport_operator["signed_holonomy_operator"]["quadratic_identity_s_squared_equals_4s_plus_32i"],
            "signed_trace_matches_triangle_excess": center_quad_transport_operator["signed_holonomy_operator"]["trace_s_cubed_equals_six_times_signed_triangle_excess"],
        },
        "center_quad_transport_a2_bridge": {
            "fiber_rank": center_quad_transport_a2["local_a2_fiber"]["rank"],
            "cartan_matrix": center_quad_transport_a2["local_a2_fiber"]["cartan_matrix"],
            "all_six_weyl_matrices_realized": center_quad_transport_a2["local_a2_fiber"]["all_six_weyl_matrices_realized"],
            "determinant_character_equals_permutation_parity": center_quad_transport_a2["local_a2_fiber"]["determinant_character_equals_permutation_parity"],
            "a2_operator_dimension": center_quad_transport_a2["a2_transport_operator"]["dimension"],
            "a2_operator_spectrum": center_quad_transport_a2["a2_transport_operator"]["spectrum"],
            "a2_operator_cubic_relation": center_quad_transport_a2["a2_transport_operator"]["cubic_relation_h3_plus_9h2_minus_120h_minus_128i"],
            "matches_standard_sector_up_to_local_basis_change": center_quad_transport_a2["a2_transport_operator"]["matches_standard_sector_up_to_fixed_local_basis_change"],
            "triangle_character_sum": center_quad_transport_a2["triangle_character_formula"]["character_sum_over_triangle_holonomies"],
            "trace_cube_matches_character_sum": center_quad_transport_a2["triangle_character_formula"]["trace_h_cubed_equals_six_character_sum"],
        },
        "curved_a2_transport_product_bridge": {
            "internal_dimension": curved_a2_product["a2_internal_profile"]["total_dimension"],
            "internal_laplacian_spectrum": curved_a2_product["a2_internal_profile"]["laplacian_spectrum"],
            "internal_gap": curved_a2_product["a2_internal_profile"]["spectral_gap"],
            "cp2_product_dimension": curved_a2_product["curved_product_profiles"][0]["total_dimension"],
            "cp2_product_trace": curved_a2_product["curved_product_profiles"][0]["trace_product"],
            "k3_product_dimension": curved_a2_product["curved_product_profiles"][1]["total_dimension"],
            "k3_product_trace": curved_a2_product["curved_product_profiles"][1]["trace_product"],
            "product_heat_factorizes_exactly": all(
                row["abs_error"] < 1e-9 for row in curved_a2_product["product_heat_checks"]
            ),
            "product_chain_density_limit": curved_a2_product["density_limits"]["a2_product_chain_density_per_top_simplex"]["exact"],
            "product_trace_density_limit": curved_a2_product["density_limits"]["a2_product_trace_per_top_simplex"]["exact"],
        },
        "curved_a2_heat_density_asymptotics": {
            "persistent_gap": curved_a2_asymptotics["persistent_gap_theorem"]["product_gap_for_all_refinement_steps"],
            "constant_limit": curved_a2_asymptotics["universal_limits"]["constant_term_per_top_simplex"]["exact"],
            "linear_limit": curved_a2_asymptotics["universal_limits"]["linear_term_per_top_simplex"]["exact"],
            "cp2_constant_corr_20": curved_a2_asymptotics["seed_closed_forms"][0]["constant_term_formula"]["corr_20_power_r"]["exact"],
            "cp2_linear_corr_20": curved_a2_asymptotics["seed_closed_forms"][0]["linear_term_formula"]["corr_20_power_r"]["exact"],
            "k3_constant_corr_20": curved_a2_asymptotics["seed_closed_forms"][1]["constant_term_formula"]["corr_20_power_r"]["exact"],
            "k3_linear_corr_20": curved_a2_asymptotics["seed_closed_forms"][1]["linear_term_formula"]["corr_20_power_r"]["exact"],
            "step_zero_small_t_checks_improve": all(
                curved_a2_asymptotics["step_zero_heat_checks"][index]["abs_error"]
                < curved_a2_asymptotics["step_zero_heat_checks"][index + 2]["abs_error"]
                for index in (0, 3)
            ),
        },
        "curved_a2_quadratic_seed_bridge": {
            "cp2_external_second_moment": curved_a2_quadratic["external_second_moment_profiles"][0]["external_second_moment"],
            "k3_external_second_moment": curved_a2_quadratic["external_second_moment_profiles"][1]["external_second_moment"],
            "cp2_triangle_tetra_degree_distribution": curved_a2_quadratic["external_second_moment_profiles"][0]["boundary_square_layers"][2]["degree_distribution"],
            "k3_triangle_tetra_degree_distribution": curved_a2_quadratic["external_second_moment_profiles"][1]["boundary_square_layers"][2]["degree_distribution"],
            "cp2_quadratic_density_coefficient": curved_a2_quadratic["product_quadratic_seed_profiles"][0]["quadratic_density_coefficient"]["exact"],
            "k3_quadratic_density_coefficient": curved_a2_quadratic["product_quadratic_seed_profiles"][1]["quadratic_density_coefficient"]["exact"],
            "second_order_step_zero_prediction_improves_first_order": all(
                row["second_order_abs_error"] < row["first_order_abs_error"]
                for row in curved_a2_quadratic["step_zero_second_order_heat_checks"]
            ),
        },
        "curved_a2_refined_quadratic_bridge": {
            "cp2_sd1_f_vector": tuple(curved_a2_refined_quadratic["refined_external_profiles"][0]["refined_f_vector"]),
            "k3_sd1_f_vector": tuple(curved_a2_refined_quadratic["refined_external_profiles"][1]["refined_f_vector"]),
            "cp2_sd1_external_second_moment": curved_a2_refined_quadratic["refined_quadratic_theorem"]["cp2_sd1_external_second_moment"],
            "k3_sd1_external_second_moment": curved_a2_refined_quadratic["refined_quadratic_theorem"]["k3_sd1_external_second_moment"],
            "cp2_sd1_product_quadratic_density_coefficient": curved_a2_refined_quadratic["refined_quadratic_theorem"]["cp2_sd1_product_quadratic_density_coefficient"],
            "k3_sd1_product_quadratic_density_coefficient": curved_a2_refined_quadratic["refined_quadratic_theorem"]["k3_sd1_product_quadratic_density_coefficient"],
            "seed_quadratic_gap": curved_a2_refined_quadratic["refined_quadratic_theorem"]["seed_quadratic_gap"],
            "sd1_quadratic_gap": curved_a2_refined_quadratic["refined_quadratic_theorem"]["sd1_quadratic_gap"],
            "sd1_f_vectors_match_exact_barycentric_transform_for_both_seeds": curved_a2_refined_quadratic["refined_quadratic_theorem"]["sd1_f_vectors_match_exact_barycentric_transform_for_both_seeds"],
            "first_refinement_contracts_cp2_k3_product_quadratic_gap": curved_a2_refined_quadratic["refined_quadratic_theorem"]["first_refinement_contracts_cp2_k3_product_quadratic_gap"],
        },
        "transport_lie_tower_bridge": {
            "transport_identity_edge_count": transport_lie["transport_weyl_classes"][2]["edge_count"],
            "transport_reflection_edge_count": transport_lie["transport_weyl_classes"][1]["edge_count"],
            "transport_three_cycle_edge_count": transport_lie["transport_weyl_classes"][0]["edge_count"],
            "l6_e6_root_support_size": transport_lie["l6_exceptional_split"]["e6_root_support_size"],
            "l6_a2_root_support_size": transport_lie["l6_exceptional_split"]["a2_root_support_size"],
            "l6_cartan_support_size": transport_lie["l6_exceptional_split"]["cartan_support_size"],
            "l6_spinor_action_ranks": transport_lie["l6_exceptional_split"]["spinor_action_ranks"],
            "complete_oriented_three_generation_graph": transport_lie["generation_channel_theorem"]["complete_oriented_three_generation_graph"],
            "a2_channels_are_signed_permutation_blocks": transport_lie["generation_channel_theorem"]["all_a2_channels_are_signed_permutation_blocks"],
            "cartan_modes_are_generation_diagonal": transport_lie["generation_channel_theorem"]["all_cartan_modes_are_generation_diagonal"],
            "current_l6_bridge_activates_only_cartan_modes": transport_lie["generation_channel_theorem"]["current_l6_bridge_activates_only_cartan_modes"],
        },
        "l6_a2_selection_bridge": {
            "seed_block_unions_h2": l6_a2_selection["seed_generation_structure"]["seed_block_unions"]["H_2"],
            "seed_block_unions_hbar2": l6_a2_selection["seed_generation_structure"]["seed_block_unions"]["Hbar_2"],
            "seed_residual_unions_h2": l6_a2_selection["seed_generation_structure"]["seed_residual_block_unions"]["H_2"],
            "seed_residual_unions_hbar2": l6_a2_selection["seed_generation_structure"]["seed_residual_block_unions"]["Hbar_2"],
            "seed_yukawas_are_generation_diagonal": l6_a2_selection["seed_generation_structure"]["seed_yukawas_are_generation_diagonal"],
            "seed_residuals_are_generation_diagonal": l6_a2_selection["seed_generation_structure"]["seed_residuals_are_generation_diagonal"],
            "a2_zero_response_mode_indices": l6_a2_selection["selection_theorem"]["a2_zero_response_mode_indices"],
            "a2_nonzero_mode_indices": l6_a2_selection["selection_theorem"]["a2_nonzero_mode_indices"],
            "a2_nonzero_channels_are_single_off_diagonal_blocks": l6_a2_selection["selection_theorem"]["all_nonzero_a2_seed_blocks_are_single_off_diagonal_channels"],
            "a2_response_channels_stay_single_off_diagonal_blocks": l6_a2_selection["selection_theorem"]["all_nonzero_a2_response_blocks_stay_single_off_diagonal_channels"],
            "replicated_seed_only_realizes_generation_2_star": l6_a2_selection["selection_theorem"]["replicated_seed_only_realizes_generation_2_star_in_a2_slice"],
            "a2_rhs_is_exactly_zero": l6_a2_selection["selection_theorem"]["a2_rhs_is_exactly_zero"],
            "a2_cartan_cross_gram_is_zero": l6_a2_selection["selection_theorem"]["a2_cartan_cross_gram_is_zero"],
            "current_l6_solution_has_no_active_a2_modes": l6_a2_selection["selection_theorem"]["current_l6_solution_has_no_active_a2_modes"],
            "cartan_only_selection_is_structurally_forced": l6_a2_selection["selection_theorem"]["cartan_only_selection_is_structurally_forced"],
        },
        "l6_a2_mixed_seed_bridge": {
            "base_response_rank": l6_a2_mixed_seed["base_profile"]["response_rank"],
            "base_augmented_rank": l6_a2_mixed_seed["base_profile"]["augmented_rank"],
            "minimal_full_activation_seed_size": l6_a2_mixed_seed["activation_theorems"]["minimal_full_a2_activation_seed_size"],
            "minimal_full_activation_seed_modes": l6_a2_mixed_seed["activation_theorems"]["minimal_full_a2_activation_seed_modes"],
            "minimal_full_activation_profiles_are_exactly_fans": l6_a2_mixed_seed["activation_theorems"]["minimal_full_activation_profiles_are_exactly_fans"],
            "minimal_rank_lift_seed_size": l6_a2_mixed_seed["activation_theorems"]["minimal_rank_lift_seed_size"],
            "minimal_rank_lift_seed_modes": l6_a2_mixed_seed["activation_theorems"]["minimal_rank_lift_seed_modes"],
            "minimal_rank_lift_profiles_are_paths_or_bidirected_edges": l6_a2_mixed_seed["activation_theorems"]["minimal_rank_lift_profiles_are_paths_or_bidirected_edges"],
            "max_response_rank": l6_a2_mixed_seed["activation_theorems"]["max_response_rank_within_unit_a2_seed_family"],
            "max_augmented_rank": l6_a2_mixed_seed["activation_theorems"]["max_augmented_rank_within_unit_a2_seed_family"],
            "fan_closure_seeds_have_full_3x3_support": l6_a2_mixed_seed["activation_theorems"]["fan_closure_seeds_have_full_3x3_support"],
            "fan_closure_seeds_have_slotwise_isotropic_off_diagonal_shell": l6_a2_mixed_seed["activation_theorems"]["fan_closure_seeds_have_slotwise_isotropic_off_diagonal_shell"],
            "fan_closure_seeds_keep_all_six_a2_modes_active": l6_a2_mixed_seed["activation_theorems"]["fan_closure_seeds_keep_all_six_a2_modes_active"],
            "single_edge_seed_activates_exact_unordered_edge_pair": l6_a2_mixed_seed["activation_theorems"]["single_edge_seeds_activate_exact_unordered_edge_pair"],
            "no_exact_closure_within_unit_a2_seed_family": l6_a2_mixed_seed["activation_theorems"]["no_exact_closure_within_unit_a2_seed_family"],
        },
        "l6_a2_v4_mode_bridge": {
            "all_mode_blocks_are_pure_right_character_twists": l6_a2_v4_modes["a2_v4_mode_theorem"]["all_mode_blocks_are_pure_right_character_twists"],
            "pure_a_modes_are_exactly_8_and_128": l6_a2_v4_modes["a2_v4_mode_theorem"]["pure_a_modes_are_exactly_8_and_128"],
            "pure_b_modes_are_exactly_9_and_127": l6_a2_v4_modes["a2_v4_mode_theorem"]["pure_b_modes_are_exactly_9_and_127"],
            "mixed_i_a_ab_modes_are_exactly_246_and_247": l6_a2_v4_modes["a2_v4_mode_theorem"]["mixed_i_a_ab_modes_are_exactly_246_and_247"],
            "all_four_v4_characters_already_realized_on_fan_seed": l6_a2_v4_modes["a2_v4_mode_theorem"]["all_four_v4_characters_already_realized_on_fan_seed"],
            "dormant_modes_127_128_awaken_as_single_block_channels": l6_a2_v4_modes["a2_v4_mode_theorem"]["dormant_modes_127_128_awaken_as_single_block_channels"],
        },
        "l6_delta27_texture_bridge": {
            "fan_closures_match_for_both_slots": l6_delta27_texture["delta27_envelope_theorem"]["fan_closures_match_for_both_slots"],
            "canonical_closure_is_not_cycle_invariant": l6_delta27_texture["delta27_envelope_theorem"]["canonical_closure_is_not_cycle_invariant"],
            "canonical_closure_has_delta27_envelope_shape": l6_delta27_texture["delta27_envelope_theorem"]["canonical_closure_has_delta27_envelope_shape"],
            "cycle_orbit_has_three_distinguished_generations": l6_delta27_texture["delta27_envelope_theorem"]["cycle_orbit_has_three_distinguished_generations"],
            "h2_distinguished_generation": l6_delta27_texture["slot_profiles"]["H_2"]["canonical_texture"]["distinguished_generation"],
            "hbar2_distinguished_generation": l6_delta27_texture["slot_profiles"]["Hbar_2"]["canonical_texture"]["distinguished_generation"],
        },
        "l6_delta27_v4_bridge": {
            "all_off_diagonal_blocks_share_exact_support_for_both_slots": l6_delta27_v4["matrix_level_v4_theorem"]["all_off_diagonal_blocks_share_exact_support_for_both_slots"],
            "all_relative_row_signs_are_trivial_for_both_slots": l6_delta27_v4["matrix_level_v4_theorem"]["all_relative_row_signs_are_trivial_for_both_slots"],
            "all_off_diagonal_blocks_are_exact_right_sign_twists_for_both_slots": l6_delta27_v4["matrix_level_v4_theorem"]["all_off_diagonal_blocks_are_exact_right_sign_twists_for_both_slots"],
            "four_v4_characters_realized_for_both_slots": l6_delta27_v4["matrix_level_v4_theorem"]["four_v4_characters_realized_for_both_slots"],
            "generators_are_commuting_involutions_for_both_slots": l6_delta27_v4["matrix_level_v4_theorem"]["generators_are_commuting_involutions_for_both_slots"],
            "pair_character_pattern_is_slot_independent": l6_delta27_v4["matrix_level_v4_theorem"]["pair_character_pattern_is_slot_independent"],
            "cycle_orbit_preserves_v4_structure_for_both_slots": l6_delta27_v4["matrix_level_v4_theorem"]["cycle_orbit_preserves_v4_structure_for_both_slots"],
            "h2_active_right_support_labels": l6_delta27_v4["slot_profiles"]["H_2"]["active_right_support_labels"],
            "hbar2_active_right_support_labels": l6_delta27_v4["slot_profiles"]["Hbar_2"]["active_right_support_labels"],
            "h2_generator_a_flipped_labels": l6_delta27_v4["slot_profiles"]["H_2"]["generator_a_flipped_labels"],
            "h2_generator_b_flipped_labels": l6_delta27_v4["slot_profiles"]["H_2"]["generator_b_flipped_labels"],
            "hbar2_generator_a_flipped_labels": l6_delta27_v4["slot_profiles"]["Hbar_2"]["generator_a_flipped_labels"],
            "hbar2_generator_b_flipped_labels": l6_delta27_v4["slot_profiles"]["Hbar_2"]["generator_b_flipped_labels"],
            "pair_character_labels": l6_delta27_v4["slot_profiles"]["H_2"]["pair_character_labels"],
        },
        "l6_v4_projector_bridge": {
            "minus_minus_projector_vanishes_for_both_slots": l6_v4_projectors["projector_theorem"]["minus_minus_projector_vanishes_for_both_slots"],
            "plus_plus_projector_is_exact_inactive_support_for_both_slots": l6_v4_projectors["projector_theorem"]["plus_plus_projector_is_exact_inactive_support_for_both_slots"],
            "h2_active_support_splits_as_2_plus_2": l6_v4_projectors["projector_theorem"]["h2_active_support_splits_as_2_plus_2"],
            "hbar2_active_support_splits_as_1_plus_3": l6_v4_projectors["projector_theorem"]["hbar2_active_support_splits_as_1_plus_3"],
            "h2_plus_minus_support": l6_v4_projectors["slot_profiles"]["H_2"]["projectors"]["+-"]["support_labels"],
            "h2_minus_plus_support": l6_v4_projectors["slot_profiles"]["H_2"]["projectors"]["-+"]["support_labels"],
            "hbar2_plus_minus_support": l6_v4_projectors["slot_profiles"]["Hbar_2"]["projectors"]["+-"]["support_labels"],
            "hbar2_minus_plus_support": l6_v4_projectors["slot_profiles"]["Hbar_2"]["projectors"]["-+"]["support_labels"],
        },
        "l6_v4_closure_selection_bridge": {
            "forward_fan_is_exact_generation_2_row_for_both_slots": l6_v4_closure_selection["closure_selection_theorem"]["forward_fan_is_exact_generation_2_row_for_both_slots"],
            "reverse_completion_adds_exact_double_ab_i_a_row_for_both_slots": l6_v4_closure_selection["closure_selection_theorem"]["reverse_completion_adds_exact_double_ab_i_a_row_for_both_slots"],
            "reverse_fan_is_exact_two_row_a_column_shell_for_both_slots": l6_v4_closure_selection["closure_selection_theorem"]["reverse_fan_is_exact_two_row_a_column_shell_for_both_slots"],
            "forward_completion_supplies_exact_missing_ab_i_and_a_b_entries_for_both_slots": l6_v4_closure_selection["closure_selection_theorem"]["forward_completion_supplies_exact_missing_ab_i_and_a_b_entries_for_both_slots"],
            "forward_route_assembles_canonical_label_matrix_for_both_slots": l6_v4_closure_selection["closure_selection_theorem"]["forward_route_assembles_canonical_label_matrix_for_both_slots"],
            "reverse_route_assembles_canonical_label_matrix_for_both_slots": l6_v4_closure_selection["closure_selection_theorem"]["reverse_route_assembles_canonical_label_matrix_for_both_slots"],
            "canonical_label_matrix_is_slot_independent": l6_v4_closure_selection["closure_selection_theorem"]["canonical_label_matrix_is_slot_independent"],
        },
        "l6_v4_seed_reconstruction_bridge": {
            "label_matrix_is_slot_independent": l6_v4_seed_reconstruction["seed_reconstruction_theorem"]["label_matrix_is_slot_independent"],
            "expected_label_matrix": l6_v4_seed_reconstruction["seed_reconstruction_theorem"]["expected_label_matrix"],
            "reconstructs_canonical_closure_exactly_for_both_slots": l6_v4_seed_reconstruction["seed_reconstruction_theorem"]["reconstructs_canonical_closure_exactly_for_both_slots"],
            "generation_0_diagonal_delta_equals_offdiag_1_to_0_for_both_slots": l6_v4_seed_reconstruction["seed_reconstruction_theorem"]["generation_0_diagonal_delta_equals_offdiag_1_to_0_for_both_slots"],
            "generation_1_diagonal_delta_equals_offdiag_0_to_1_for_both_slots": l6_v4_seed_reconstruction["seed_reconstruction_theorem"]["generation_1_diagonal_delta_equals_offdiag_0_to_1_for_both_slots"],
            "generation_2_diagonal_block_is_unchanged_for_both_slots": l6_v4_seed_reconstruction["seed_reconstruction_theorem"]["generation_2_diagonal_block_is_unchanged_for_both_slots"],
            "reference_projector_rank_split_matches_h2_2_plus_2_and_hbar2_3_plus_1": l6_v4_seed_reconstruction["seed_reconstruction_theorem"]["reference_projector_rank_split_matches_h2_2_plus_2_and_hbar2_3_plus_1"],
        },
        "uor_gluing_bridge": {
            "all_pairwise_overlaps_are_compatible": uor_gluing["gluing_theorem"]["all_pairwise_overlaps_are_compatible_for_both_slots"],
            "all_cells_are_covered": uor_gluing["gluing_theorem"]["all_cells_are_covered_for_both_slots"],
            "forward_route_glues_to_canonical_section": uor_gluing["gluing_theorem"]["forward_route_glues_to_canonical_section_for_both_slots"],
            "reverse_route_glues_to_canonical_section": uor_gluing["gluing_theorem"]["reverse_route_glues_to_canonical_section_for_both_slots"],
            "full_cover_has_unique_global_section": uor_gluing["gluing_theorem"]["full_cover_has_unique_global_section_for_both_slots"],
            "canonical_global_section_is_slot_independent": uor_gluing["gluing_theorem"]["canonical_global_section_is_slot_independent"],
        },
        "lie_tower_cycle_bridge": {
            "l3_support_size": lie_tower_cycle["raw_tower_profiles"][0]["support_size"],
            "l3_uniform_output_term_count": lie_tower_cycle["raw_tower_profiles"][0]["uniform_output_term_count"],
            "l4_support_size": lie_tower_cycle["raw_tower_profiles"][1]["support_size"],
            "l4_uniform_output_term_count": lie_tower_cycle["raw_tower_profiles"][1]["uniform_output_term_count"],
            "l5_support_size": lie_tower_cycle["raw_tower_profiles"][2]["support_size"],
            "l5_uniform_output_term_count": lie_tower_cycle["raw_tower_profiles"][2]["uniform_output_term_count"],
            "l6_support_size": lie_tower_cycle["raw_tower_profiles"][3]["support_size"],
            "l6_multi_entry_count": lie_tower_cycle["raw_tower_profiles"][3]["multi_entry_count"],
            "pure_single_term_layers_before_l6": lie_tower_cycle["z3_grade_cycle_theorem"]["pure_single_term_layers_before_l6"],
            "l6_first_full_gauge_return": lie_tower_cycle["z3_grade_cycle_theorem"]["l6_first_full_gauge_return"],
            "l6_multi_terms_only_cartan_only_democratic": lie_tower_cycle["pattern_progression_theorem"]["l6_multi_terms_only_cartan_only_democratic"],
            "l4_effective_mode_count": lie_tower_cycle["l4_to_l6_quark_bridge_escalation"]["l4_effective_mode_count"],
            "l6_total_chiral_mode_count": lie_tower_cycle["l4_to_l6_quark_bridge_escalation"]["l6_total_chiral_mode_count"],
            "l6_currently_activates_only_cartan": lie_tower_cycle["l4_to_l6_quark_bridge_escalation"]["l6_currently_activates_only_cartan"],
        },
        "lie_tower_s12_bridge": {
            "s12_total_nonzero_dimension": lie_tower_s12["s12_grade_only_model"]["total_nonzero_dimension"],
            "s12_grade_split": lie_tower_s12["s12_grade_only_model"]["grade_split"],
            "s12_jacobi_failure_count": lie_tower_s12["s12_grade_only_model"]["jacobi_failure_count"],
            "sl27_partition": lie_tower_s12["sl27_z3_bridge"]["unique_partition"],
            "sl27_a_family_rank": lie_tower_s12["sl27_z3_bridge"]["a_family_rank"],
            "exact_channel_set_matches_across_layers": lie_tower_s12["shared_channel_dictionary"]["exact_channel_set_matches_across_layers"],
            "monster_heisenberg_irrep_dimension": lie_tower_s12["monster_heisenberg_closure"]["heisenberg_irrep_dimension"],
            "phase_resolution_mechanism_exact": lie_tower_s12["monster_heisenberg_closure"]["phase_resolution_mechanism_exact"],
            "current_linearized_l6_bridge_activates_only_cartan_modes": lie_tower_s12["l6_asymmetric_a2_bridge"]["current_linearized_l6_bridge_activates_only_cartan_modes"],
        },
        "curved_external_candidates": {
            "cp2_vertices": cp2["vertices"],
            "cp2_euler_characteristic": cp2["euler_characteristic"],
            "cp2_signature": cp2_budget["signature"],
            "cp2_weyl_l2_floor": cp2_budget["weyl_l2_floor"],
            "k3_vertices": k3["vertices"],
            "k3_euler_characteristic": k3["euler_characteristic"],
            "k3_signature": k3_budget["signature"],
            "k3_weyl_l2_floor": k3_budget["weyl_l2_floor"],
            "flat_metric_forbidden_for_cp2": cp2["flat_metric_topologically_forbidden"],
            "flat_metric_forbidden_for_k3": k3["flat_metric_topologically_forbidden"],
            "barycentric_top_simplex_multiplier": triangulations["barycentric_subdivision"]["top_simplex_multiplier_per_step"],
        },
        "curvature_budget_bridge": {
            "comparison_seed": curvature_budget["comparison_seed"]["name"],
            "torus_weyl_l2_floor": curvature_budget["comparison_seed"]["weyl_l2_floor"],
            "cp2_nonconformally_flat_topologically_forced": cp2_budget["nonconformally_flat_topologically_forced"],
            "k3_nonconformally_flat_topologically_forced": k3_budget["nonconformally_flat_topologically_forced"],
            "cp2_hitchin_thorpe_plus": cp2_budget["hitchin_thorpe_plus"],
            "cp2_hitchin_thorpe_minus": cp2_budget["hitchin_thorpe_minus"],
            "k3_hitchin_thorpe_plus": k3_budget["hitchin_thorpe_plus"],
            "k3_hitchin_thorpe_minus": k3_budget["hitchin_thorpe_minus"],
            "refinement_preserves_cp2_chi": curvature_budget["refinement_invariance"]["cp2_euler_characteristics"],
            "refinement_preserves_k3_chi": curvature_budget["refinement_invariance"]["k3_euler_characteristics"],
        },
        "explicit_curved_complexes": {
            "cp2_facets": cp2_complex["facets"],
            "cp2_betti_numbers": cp2_complex["betti_numbers"],
            "cp2_harmonic_form_total": cp2_complex["harmonic_form_total"],
            "k3_facets": k3_complex["facets"],
            "k3_betti_numbers": k3_complex["betti_numbers"],
            "k3_harmonic_form_total": k3_complex["harmonic_form_total"],
            "k3_orbit_group_order": explicit_complexes["construction_notes"]["k3_orbit_group_order"],
        },
        "curved_external_operator_bridge": {
            "cp2_total_chain_dim": cp2_operator["total_chain_dim"],
            "cp2_zero_modes_by_degree": cp2_operator["zero_modes_by_degree"],
            "cp2_total_spectral_gap": cp2_operator["total_spectral_gap"],
            "cp2_trace_dk_squared": cp2_operator["trace_dk_squared"],
            "k3_total_chain_dim": k3_operator["total_chain_dim"],
            "k3_zero_modes_by_degree": k3_operator["zero_modes_by_degree"],
            "k3_total_spectral_gap": k3_operator["total_spectral_gap"],
            "k3_trace_dk_squared": k3_operator["trace_dk_squared"],
            "product_heat_factorizes_on_explicit_spectra": all(
                row["abs_error"] < 1e-9 for row in curved_operator["product_heat_checks"]
            ),
        },
        "curved_refinement_density_bridge": {
            "vanishing_barycentric_modes": barycentric_density["neighborly_mode_formulas"]["vanishing_modes"],
            "external_chain_density_limit": barycentric_density["universal_local_limits"]["external_chain_density_per_top_simplex"]["exact"],
            "external_trace_density_limit": barycentric_density["universal_local_limits"]["external_trace_dk_squared_per_top_simplex"]["exact"],
            "product_chain_density_limit": barycentric_density["universal_local_limits"]["product_chain_density_per_top_simplex"]["exact"],
            "product_trace_density_limit": barycentric_density["universal_local_limits"]["product_trace_per_top_simplex"]["exact"],
            "cp2_six_mode": cp2_density["six_mode"]["exact"],
            "k3_six_mode": k3_density["six_mode"]["exact"],
            "cp2_step4_chain_density": cp2_density["density_samples"][-1]["chain_density_per_top_simplex"]["float"],
            "k3_step4_chain_density": k3_density["density_samples"][-1]["chain_density_per_top_simplex"]["float"],
            "product_zero_modes_vanish_exactly": barycentric_density["universal_local_limits"]["product_zero_modes_vanish_exactly"],
        },
        "fano_tomotope_local_model": {
            "fano_flags": surface["fano_bridge"]["fano_plane"]["flags"],
            "dual_toroidal_pair_flags": surface["fano_bridge"]["dual_pair_total_flags"],
            "tetrahedron_midpoint_flags": surface["tetrahedral_midpoint_bridge"]["tetrahedron"]["flags"],
            "fano_point_stabilizer_order": fano_group["summary"]["point_stabilizer_order"],
            "fano_flag_stabilizer_order": fano_group["summary"]["flag_stabilizer_order"],
            "flag_stabilizer_is_d8": local_square["flag_stabilizer_is_dihedral_square"],
            "local_tomotope_flags_per_edge": fano_square["tomotope_local_bridge"]["flags_around_edge"],
        },
        "mobius_fano_surface_bridge": {
            "standard_heptad_size": mobius["summary"]["standard_heptad_size"],
            "complementary_heptad_size": mobius["summary"]["complementary_heptad_size"],
            "torus_face_count": mobius["summary"]["union_face_count"],
            "torus_euler_characteristic": mobius["summary"]["euler_characteristic"],
            "each_edge_seen_once_per_heptad": mobius["mobius_torus_checks"]["each_edge_seen_once_per_heptad"],
            "triangle_vertex_incidences": mobius["summary"]["triangle_vertex_incidences"],
            "triangle_vertex_incidences_equals_two_fano_flag_sets": mobius["incidence_lift"]["equals_two_fano_flag_sets"],
        },
        "mobius_szilassi_dual_bridge": {
            "dual_vertex_count": mobius_dual["summary"]["dual_vertex_count"],
            "dual_edge_count": mobius_dual["summary"]["dual_edge_count"],
            "dual_face_count": mobius_dual["summary"]["dual_face_count"],
            "dual_face_size": mobius_dual["summary"]["dual_face_size"],
            "dual_is_heawood_skeleton": mobius_dual["heawood_checks"]["matches_shifted_fano_lines"],
            "dual_face_adjacency_is_k7": mobius_dual["szilassi_checks"]["complete_face_adjacency_k7"],
        },
        "realization_orbit_bridge": {
            "catalog_total": realization["catalog_counts"]["total"],
            "common_symmetry_group": realization["common_symmetry"]["group"],
            "csaszar_vertex_orbits": realization["dual_orbit_package"]["csaszar_vertex_orbits"],
            "csaszar_face_orbits": realization["dual_orbit_package"]["csaszar_face_orbits"],
            "szilassi_vertex_orbits": realization["dual_orbit_package"]["szilassi_vertex_orbits"],
            "szilassi_face_orbits": realization["dual_orbit_package"]["szilassi_face_orbits"],
            "orbit_package_is_dual": realization["dual_orbit_package"]["is_dual_swap"],
        },
        "witting_srg_bridge": {
            "states": witting["paper_system"]["witting_rays"],
            "orthogonal_tetrads": witting["paper_system"]["orthogonal_tetrads"],
            "degree": witting["orthogonality_graph"]["degree"],
            "lambda_parameter": witting["orthogonality_graph"]["lambda_parameter"],
            "mu_parameter": witting["orthogonality_graph"]["mu_parameter"],
            "graph_isomorphic_to_standard_w33": witting["symplectic_model"]["graph_isomorphic_to_standard_w33"],
            "tetrads_match_symplectic_lines": witting["symplectic_model"]["mapped_lines_equal_symplectic_lines"],
        },
        "cover_and_operation_tower": {
            "aut_universal_equals_tomotope_flags": order["exact_identities"]["aut_universal_equals_flags_tomotope"],
            "regular_cover_equals_flags_squared": order["exact_identities"]["regular_cover_equals_flags_t_squared"],
            "klitzing_ladder": list(klitzing["leading_count_ladder"]),
            "klitzing_doublings": list(klitzing["successive_doublings"]),
        },
        "exceptional_triad_note": exceptional["global_verdict"],
        "combined_verdict": (
            "The missing theorem is no longer a vague 'continuum limit' placeholder. "
            "The finite internal side is exact: the Witting 40-state system is now "
            "identified explicitly with W(3,3) via SRG(40,12,2,4) and 40 orthogonal "
            "tetrads, the W33 center-quad quotient reconstructs an exact 45-point / "
            "27-line dual GQ(4,2) whose line graph is SRG(27,10,1,5) with 45 "
            "triangles, giving a direct exact bridge to the 27-line / 45-tritangent "
            "E6 layer. On those same 45 quotient points the old transport layer "
            "can now be rebuilt exactly as a degree-32 quotient transport graph with "
            "reconstructed Z2 voltage matching the archived v14 parity counts and an "
            "explicit v16 edge where Z2 is trivial but the S3 port transport is odd, "
            "so the transport refinement is genuinely non-abelian rather than an "
            "embedding artifact. Better, that transport graph is itself exact: it is "
            "the complement SRG(45,32,22,24) of the 45-point SRG(45,12,3,3) "
            "incidence graph, equivalently the disjointness graph on the 45 "
            "triangles of SRG(27,10,1,5), and every transport edge carries a unique "
            "local S3 line-matching even though the raw Z2 sheet data is finer than "
            "that matching permutation. More sharply, the old v14 triangle parity "
            "is now identified exactly with the sign of local S3 holonomy around "
            "transport triangles, and the new UOR bridge sharpens that point: the "
            "right binary coefficient shadow is this holonomy sign rather than the "
            "raw edge voltage, because the full local transport group is already "
            "Weyl(A2) ~= S3 ~= D3 and parity-0 already conflates identity holonomy "
            "with 3-cycles. So the transport side now has the exact pattern of a "
            "Z2 shadow sitting above a genuinely non-abelian local system. "
            "Those same edge matchings define a canonical "
            "135-dimensional connection operator on the local-line bundle over the "
            "transport graph. That operator splits exactly as 45 + 90, with the "
            "45-dimensional trivial sector equal to the transport adjacency itself, "
            "the 90-dimensional standard sector carrying exact spectrum 8, -1, -16, "
            "and the associated signed holonomy operator satisfying S^2 = 4S + 32I. "
            "Better still, that 90-dimensional standard sector is itself native: "
            "it is the A2 root-lattice local system over the 45 quotient points, "
            "with the local S3 line-matchings acting by exact Weyl(A2) matrices "
            "preserving the Cartan form and satisfying the cubic relation "
            "H^3 + 9H^2 - 120H - 128I = 0. That native A2 transport sector also "
            "now pairs directly with the explicit curved CP2_9 and K3_16 operator "
            "packages through its positive Laplacian spectrum 24, 33, 48, giving "
            "exact product heat-trace factorization, exact curved-product traces, "
            "and exact refined density limits 10800/19 and 423000/19 per top simplex. "
            "More sharply still, the whole curved A2 tower now has exact first-order "
            "heat-density asymptotics per top simplex: constant term 10800/19, "
            "linear term 423000/19, persistent product gap 24, and explicit "
            "20^{-r} and 120^{-r} correction coefficients for both CP2 and K3. "
            "At the explicit curved seeds, the bridge now also has exact "
            "second-order data: the external second moments are 13392 for CP2_9 "
            "and 128640 for K3_16, recovered combinatorially from coface "
            "degree-square sums, and the native A2 product heat density has exact "
            "step-zero quadratic coefficients 491580 and 426060. Better still, "
            "the first barycentric refinement step is now exact too: sd^1(CP2_9) "
            "and sd^1(K3_16) have refined f-vectors (255,2916,9144,10800,4320) "
            "and (1704,22320,72480,86400,34560), external second moments 2104848 "
            "and 22872000, and native A2 product quadratic coefficients 908925/2 "
            "and 1835497/4. The CP2/K3 product-gap therefore contracts from 65520 "
            "at step 0 to 17647/4 at step 1. "
            "The raw tower itself now has an exact progression theorem: l3, l4, and "
            "l5 are pure single-term layers cycling exactly through g0(E6), g1, "
            "and g2 with uniform output multiplicities 36, 320, and 3520, while "
            "l6 is the first multi-term layer and the first full gauge return. Its "
            "only multi-term interference is the democratic 2-2-2 sextuple sector "
            "feeding Cartan, while the six asymmetric 3-2-1 sextuple sectors "
            "isolate the six A2 channels. "
            "The Lie tower is sharper too: the corrected l6 return really does "
            "split as 72 E6 roots + 6 A2 roots + 8 Cartan directions, and those "
            "six A2 modes are exactly the six ordered generation-transfer "
            "channels on the 48-spinor space, each a single signed permutation "
            "block of rank 16, while the current linear l6 bridge still activates "
            "only Cartan modes. Better, that Cartan-only selection is now explained "
            "structurally on the first honest three-generation seed: the replicated "
            "H_2/Hbar_2 Yukawas and their strict SU(3)xSU(2) residuals are exactly "
            "generation-diagonal, every Cartan l6 response stays generation-diagonal, "
            "and every nonzero A2 response occupies one off-diagonal generation block. "
            "Two A2 modes vanish exactly on that replicated seed, the remaining four "
            "realize only the generation-2 star, and the full A2 response slice is "
            "orthogonal both to the seed residual and to the Cartan response sector. "
            "So the current l6 least-squares bridge solves in the Cartan slice for a "
            "structural reason, not because the optimizer missed an A2 channel. "
            "Better, exact A2 activation beyond that seed is now mapped too. "
            "Inside the repo-native unit mixed-seed family generated by the four "
            "nonzero dormant A2 deltas, a single directed seed activates exactly "
            "its unordered edge pair, a two-edge fan through generation 2 is the "
            "minimal exact seed that activates all six A2 modes, and two-edge "
            "directed paths or bidirected edges are the minimal exact seeds that "
            "raise the response rank from 9 to 11 and the augmented rank from "
            "10 to 12. One exact nonlinear closure step then turns each minimal "
            "fan into a full 3x3-support mixed seed whose six off-diagonal 8x8 "
            "blocks have identical singular spectra within each external slot, "
            "i.e. a circulant-style off-diagonal shell. Better still, on the "
            "canonical fan seed the six exact A2 modes already refine into V4 "
            "flavour characters: 8 and 128 are pure A channels, 9 and 127 are "
            "pure B channels, and the reverse-fan modes 246 and 247 are the "
            "first mixed character modes with exact blockwise content {I, A, AB}. "
            "So the full V4 flavour torsor is already present before the final "
            "nonlinear closure and is carried directly by the exact A2 Lie channels. "
            "Better still, the commuting V4 generators admit an exact simultaneous "
            "projector decomposition of the right-handed sector: the (-- ) character "
            "is absent, the (+,+) sector is exactly the inactive support, and the "
            "active support splits rigidly as 2+2 for H_2 and 1+3 for Hbar_2. "
            "Better again, the canonical mixed seed is now reconstructible "
            "exactly from native internal data: replicated base Yukawa, one "
            "reference off-diagonal block, and one slot-independent V4-labelled "
            "generation matrix [[AB,I,A],[AB,I,A],[A,B,0]]. The generation-0 "
            "and generation-1 diagonal corrections are exact off-diagonal blocks, "
            "while the generation-2 diagonal block stays unchanged. Better "
            "still, that label matrix is now selected dynamically by the exact "
            "two-step A2 closure itself: the minimal forward fan contributes the "
            "bottom row [A,B,0], the reverse completion adds exactly two identical "
            "rows [AB,I,A], and the reverse route assembles the same canonical "
            "matrix in a complementary way for both H_2 and Hbar_2. "
            "The external UOR sheaf clue now lands exactly here too: those local "
            "closure patches overlap compatibly and glue to one unique global "
            "section on the 3x3 generation grid, so the flavour problem is no "
            "longer whether the exact V4 data glues but what deeper operator "
            "principle selects those local sections. "
            "The two fan closures then coincide to one canonical mixed seed, and its 3x3 generation "
            "envelope is already of Delta(27) circulant-plus-diagonal type: one "
            "distinguished diagonal generation, a degenerate diagonal pair, and a "
            "uniform off-diagonal shell, with a full 3-element orbit under cyclic "
            "generation permutation. Better still, this Delta(27)-type texture now "
            "lifts to matrix level: in each external slot every off-diagonal 8x8 "
            "block is exactly one reference block multiplied on the right by one of "
            "four diagonal sign characters forming a V4 subgroup, and the ordered "
            "generation-pair to character-label map is the same for H_2 and Hbar_2. "
            "So the generation pattern is slot-independent while the slot dependence "
            "sits only in which active right-handed states carry the two commuting "
            "involution generators. But none of those exact unit A2 seeds closes the "
            "linearized residual. "
            "The old s12 scripts now land on the same six-channel "
            "structure: the grade-only Golay model has exactly six Jacobi-failure "
            "triples, the corrected l6 exceptional return has exactly six asymmetric "
            "A2 sextuple sectors, and those two six-sets canonically identify with "
            "the same complete oriented three-generation graph. The sl_27 block-cyclic "
            "9+9+9 bridge and the Monster 3B / Heisenberg / Golay closure then show "
            "what resolves the old six-channel obstruction: an honest phase/cocycle "
            "mechanism rather than more grade-only counting. "
            "The tomotope gives a genuine infinite cover family, the "
            "Fano/tetrahedron bridge gives a concrete D8 local model for tomotope "
            "edge stars, the M\"obius/Csaszar torus seed splits exactly as two Fano "
            "heptads on the same 7 vertices, that seed has an explicit abstract "
            "Szilassi dual with Heawood 1-skeleton and K7 face adjacency, the seven "
            "cataloged Euclidean realizations all share the same Z2 half-turn with "
            "dual orbit package (Csaszar: 4V/7F, Szilassi: 7V/4F), and minimal "
            "triangulations of CP2 and K3 supply curved 4D simplicial seed geometries "
            "with true refinement towers, a signature-forced nonzero Weyl-curvature "
            "budget, explicit external chain complexes with exact Betti profiles, and "
            "explicit external Hodge/Dirac-Kahler spectra whose almost-commutative "
            "product heat traces with the W33 finite triple factorize exactly on the "
            "full explicit spectra. Better, the barycentric refinement family now has "
            "an exact mode split: for neighborly curved 4-manifold seeds the 2- and "
            "24-modes vanish, Euler characteristic is the pure eigenvalue-1 mode, and "
            "the local densities converge exactly to the universal 120-mode limits "
            "120/19 and 860/19 per top simplex. What remains open is the curved 4D "
            "spectral-action theorem for an almost-commutative product built from "
            "that exact internal data and a genuine curved 4D refinement family."
        ),
        "next_theorem_target": (
            "Lift the exact second-order curved A2 data from steps 0 and 1 to the "
            "full curved barycentric refinement tower, move beyond the replicated "
            "generation-diagonal three-generation seed that structurally forces "
            "Cartan-only l6 selection, push the new exact V4 closure-selection "
            "theorem past minimal fan dynamics to a deeper internal operator or "
            "variational principle that explains why the exact generation label "
            "matrix [[AB,I,A],[AB,I,A],[A,B,0]] is selected now that the "
            "local-to-global gluing step is exact, "
            "and push that seed into the rank-lift regime or the full six-mode regime, "
            "extend the exact l3/l4/l5/l6 tower-cycle theorem "
            "to the next gauge-return rung beyond l6, then prove the small-time / cutoff "
            "asymptotics that generate the Einstein-Hilbert term."
        ),
        "residual_risk": (
            "Tomotope itself remains natively cubic in its explicit Q_k tower. The 4D "
            "geometry must therefore come from an external factor or from a different "
            "genuinely 4D refinement family."
        ),
        "focused_test_stack_size": 334,
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_refinement_bridge_synthesis(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
