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
from w33_curved_h2_host_bridge import build_curved_h2_host_bridge_summary
from w33_curved_h2_qutrit_bridge import build_curved_h2_qutrit_bridge_summary
from w33_curved_harmonic_qutrit_split_bridge import build_curved_harmonic_qutrit_split_bridge_summary
from w33_curved_h2_cup_plane_bridge import build_curved_h2_cup_plane_bridge_summary
from w33_k3_rank2_qutrit_plane_bridge import build_k3_rank2_qutrit_plane_bridge_summary
from w33_transport_mixed_plane_obstruction_bridge import (
    build_transport_mixed_plane_obstruction_summary,
)
from w33_k3_mixed_plane_a4_projection_bridge import (
    build_k3_mixed_plane_a4_projection_summary,
)
from w33_k3_refined_plane_persistence_bridge import (
    build_k3_refined_plane_persistence_bridge_summary,
)
from w33_k3_integral_h2_lattice_bridge import (
    build_k3_integral_h2_lattice_bridge_summary,
)
from w33_k3_primitive_plane_global_a4_bridge import (
    build_k3_primitive_plane_global_a4_bridge_summary,
)
from w33_k3_three_u_decomposition_bridge import (
    build_k3_three_u_decomposition_bridge_summary,
)
from w33_k3_three_u_refinement_bridge import (
    build_k3_three_u_refinement_bridge_summary,
)
from w33_k3_three_u_complement_refinement_bridge import (
    build_k3_three_u_complement_refinement_bridge_summary,
)
from w33_k3_n16_e8e8_bridge import (
    build_k3_n16_e8e8_bridge_summary,
)
from w33_k3_e8_factor_split_bridge import (
    build_k3_e8_factor_split_bridge_summary,
)
from w33_k3_e8_factor_refinement_bridge import (
    build_k3_e8_factor_refinement_bridge_summary,
)
from w33_k3_primitive_plane_three_u_alignment_bridge import (
    build_k3_primitive_plane_three_u_alignment_bridge_summary,
)
from w33_k3_selector_three_u_shadow_bridge import (
    build_k3_selector_three_u_shadow_bridge_summary,
)
from w33_k3_selector_e8_shadow_bridge import (
    build_k3_selector_e8_shadow_bridge_summary,
)
from w33_k3_selector_shadow_refinement_bridge import (
    build_k3_selector_shadow_refinement_bridge_summary,
)
from w33_k3_selector_a4_lattice_split_bridge import (
    build_k3_selector_a4_lattice_split_bridge_summary,
)
from w33_k3_selector_a4_five_factor_bridge import (
    build_k3_selector_a4_five_factor_bridge_summary,
)
from w33_k3_selector_a4_five_factor_refinement_bridge import (
    build_k3_selector_a4_five_factor_refinement_bridge_summary,
)
from w33_u1_family_a4_carrier_bridge import (
    build_u1_family_a4_carrier_bridge_summary,
)
from w33_u1_isotropic_line_obstruction_bridge import (
    build_u1_isotropic_line_obstruction_bridge_summary,
)
from w33_selector_a4_weight_hierarchy_bridge import (
    build_selector_a4_weight_hierarchy_bridge_summary,
)
from w33_transport_semisimplification_shadow_bridge import (
    build_transport_semisimplification_shadow_bridge_summary,
)
from w33_global_local_carrier_split_bridge import (
    build_global_local_carrier_split_bridge_summary,
)
from w33_family_flag_visibility_obstruction_bridge import (
    build_family_flag_visibility_obstruction_bridge_summary,
)
from w33_e13_visibility_obstruction_bridge import (
    build_e13_visibility_obstruction_bridge_summary,
)
from w33_u1_selector_line_selection_bridge import (
    build_u1_selector_line_selection_bridge_summary,
)
from w33_explicit_curved_4d_complexes import build_explicit_curved_4d_complexes_summary
from w33_fano_group_bridge import build_fano_group_summary
from w33_fano_square_tomotope_bridge import build_fano_square_tomotope_summary
from w33_flat_ac_spectral_action import build_flat_product_summary
from w33_minimal_triangulation_bridge import build_minimal_triangulation_summary
from w33_mobius_fano_bridge import build_mobius_fano_summary
from w33_mod7_fano_duality_bridge import build_mod7_fano_duality_summary
from w33_heawood_harmonic_bridge import build_heawood_harmonic_summary
from w33_heawood_tetra_radical_bridge import build_heawood_tetra_radical_summary
from w33_heawood_klein_symmetry_bridge import build_heawood_klein_symmetry_summary
from w33_heawood_shell_ladder_bridge import build_heawood_shell_ladder_summary
from w33_klein_quartic_gf3_tetra_bridge import build_klein_quartic_gf3_tetra_summary
from w33_mobius_szilassi_dual import build_mobius_szilassi_dual_summary
from w33_realization_orbit_bridge import build_realization_orbit_summary
from w33_surface_neighborly_bridge import build_surface_neighborly_summary
from w33_surface_congruence_selector_bridge import build_surface_congruence_selector_summary
from w33_surface_hurwitz_flag_bridge import build_surface_hurwitz_flag_summary
from w33_mod12_selector_closure_bridge import build_mod12_selector_closure_summary
from w33_decimal_surface_flag_bridge import build_decimal_surface_flag_summary
from w33_fano_toroidal_complement_bridge import build_fano_toroidal_complement_summary
from w33_surface_physics_shell_bridge import build_surface_physics_shell_summary
from w33_toroidal_k7_spectral_bridge import build_toroidal_k7_spectral_summary
from w33_klein_hurwitz_extremal_bridge import build_klein_hurwitz_extremal_summary
from w33_hurwitz_237_selector_bridge import build_hurwitz_237_selector_summary
from w33_affine_middle_shell_bridge import build_affine_middle_shell_summary
from w33_witting_srg_bridge import build_witting_srg_bridge_summary
from w33_tomotope_ac_bridge import build_bridge_summary
from w33_tomotope_klitzing_ladder import build_klitzing_ladder_summary
from w33_tomotope_order_bridge import build_tomotope_order_summary
from w33_tomotope_partial_sheet_bridge import build_tomotope_partial_sheet_summary
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
from w33_transport_path_groupoid_bridge import build_transport_path_groupoid_summary
from w33_ternary_homological_code_bridge import build_ternary_homological_code_summary
from w33_transport_ternary_line_bridge import build_transport_ternary_line_summary
from w33_transport_ternary_extension_bridge import build_transport_ternary_extension_summary
from w33_transport_ternary_cocycle_bridge import build_transport_ternary_cocycle_summary
from w33_transport_curvature_bridge import build_transport_curvature_summary
from w33_transport_borel_factor_bridge import build_transport_borel_factor_summary
from w33_transport_twisted_precomplex_bridge import build_transport_twisted_precomplex_summary
from w33_transport_matter_curved_harmonic_bridge import build_transport_matter_curved_harmonic_summary
from w33_transport_spectral_selector_bridge import build_transport_spectral_selector_summary
from w33_transport_curved_dirac_refinement_bridge import (
    build_transport_curved_dirac_refinement_summary,
)
from w33_transport_curved_dirac_quadratic_bridge import (
    build_transport_curved_dirac_quadratic_bridge_summary,
)
from w33_adjacency_dirac_closure_bridge import build_adjacency_dirac_closure_summary
from w33_three_channel_operator_bridge import build_three_channel_operator_summary
from w33_dual_bose_mesner_bridge import build_dual_bose_mesner_bridge_summary
from w33_curved_eh_mode_bridge import build_curved_eh_mode_bridge_summary
from w33_eh_continuum_lock_bridge import build_eh_continuum_lock_summary
from w33_curvature_cyclotomic_lock_bridge import build_curvature_cyclotomic_lock_summary
from w33_q3_curved_selection_bridge import build_q3_curved_selection_summary
from w33_spectral_action_cyclotomic_bridge import build_spectral_action_cyclotomic_summary
from w33_spectral_action_q3_selection_bridge import build_spectral_action_q3_selection_summary
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary
from w33_monster_landauer_ternary_bridge import build_monster_landauer_ternary_bridge_summary
from w33_monster_shell_factorization_bridge import build_monster_shell_factorization_summary
from w33_monster_3adic_closure_bridge import build_monster_3adic_closure_summary
from w33_monster_3b_centralizer_bridge import build_monster_3b_centralizer_summary
from w33_monster_lagrangian_complement_bridge import (
    build_monster_lagrangian_complement_summary,
)
from w33_monster_selector_completion_bridge import (
    build_monster_selector_completion_summary,
)
from w33_monster_q5_completion_bridge import build_monster_q5_completion_summary
from w33_monster_transport_shell_bridge import build_monster_transport_shell_summary
from w33_monster_supertrace_bridge import build_monster_supertrace_summary
from w33_monster_moonshine_lift_bridge import build_monster_moonshine_lift_summary
from w33_monster_transport_moonshine_bridge import build_monster_transport_moonshine_summary
from w33_monster_gap_duality_bridge import build_monster_gap_duality_summary
from w33_monster_triangle_landauer_bridge import build_monster_triangle_landauer_summary
from w33_triality_moonshine_spine_bridge import build_triality_moonshine_spine_summary
from w33_vacuum_unity_bridge import build_vacuum_unity_summary
from w33_quantum_vacuum_standards_bridge import build_quantum_vacuum_standards_summary
from w33_natural_units_meaning_bridge import build_natural_units_meaning_summary
from w33_natural_units_topological_bridge import build_natural_units_topological_summary
from w33_natural_units_electroweak_split_bridge import (
    build_natural_units_electroweak_split_summary,
)
from w33_heawood_weinberg_denominator_bridge import (
    build_heawood_weinberg_denominator_summary,
)
from w33_heawood_q_center_bridge import build_heawood_q_center_summary
from w33_heawood_involution_bridge import build_heawood_involution_summary
from w33_heawood_clifford_bridge import build_heawood_clifford_summary
from w33_natural_units_projective_denominator_bridge import (
    build_natural_units_projective_denominator_summary,
)
from w33_natural_units_custodial_bridge import (
    build_natural_units_custodial_summary,
)
from w33_natural_units_sigma_shell_bridge import (
    build_natural_units_sigma_shell_summary,
)
from w33_natural_units_neutral_shell_bridge import (
    build_natural_units_neutral_shell_summary,
)
from w33_natural_units_root_gap_bridge import (
    build_natural_units_root_gap_summary,
)
from w33_heawood_electroweak_polarization_bridge import (
    build_heawood_electroweak_polarization_summary,
)
from w33_natural_units_cosmological_complement_bridge import (
    build_natural_units_cosmological_complement_summary,
)
from w33_natural_units_unit_balance_bridge import (
    build_natural_units_unit_balance_summary,
)
from w33_electroweak_lagrangian_bridge import build_electroweak_lagrangian_summary
from w33_one_scale_bosonic_bridge import build_one_scale_bosonic_summary
from w33_bosonic_action_completion_bridge import build_bosonic_action_completion_summary
from w33_standard_model_action_backbone_bridge import build_standard_model_action_backbone_summary
from w33_q3_fermion_hierarchy_bridge import build_q3_fermion_hierarchy_summary
from w33_alpha_hierarchy_gaussian_bridge import build_alpha_hierarchy_gaussian_summary
from w33_qcd_beta_phi6_bridge import build_qcd_beta_phi6_summary
from w33_jones_mu4_selector_bridge import build_jones_mu4_selector_summary
from w33_f4_neutrino_scale_bridge import build_f4_neutrino_scale_summary
from w33_one_input_fermion_spectrum_bridge import build_one_input_fermion_spectrum_summary
from w33_l3_pfaffian_packet_bridge import build_l3_pfaffian_packet_summary
from w33_selector_firewall_bridge import build_selector_firewall_summary
from w33_theta_hierarchy_bridge import build_theta_hierarchy_summary
from w33_truncated_dirac_shell_bridge import build_truncated_dirac_shell_summary
from w33_yukawa_scaffold_bridge import build_yukawa_scaffold_summary
from w33_yukawa_unipotent_reduction_bridge import (
    build_yukawa_unipotent_reduction_summary,
)
from w33_yukawa_kronecker_reduction_bridge import (
    build_yukawa_kronecker_reduction_summary,
)
from w33_yukawa_gram_shell_bridge import build_yukawa_gram_shell_summary
from w33_yukawa_base_spectrum_bridge import build_yukawa_base_spectrum_summary
from w33_yukawa_active_spectrum_bridge import build_yukawa_active_spectrum_summary
from w33_s12_klein_projective_bridge import build_s12_klein_projective_summary
from w33_klein_quartic_ag21_bridge import build_klein_quartic_ag21_summary
from w33_klein_harmonic_vogel_bridge import build_klein_harmonic_vogel_summary
from w33_klein_clifford_topological_bridge import (
    build_klein_clifford_topological_summary,
)
from w33_klein_bitangent_shell_bridge import build_klein_bitangent_shell_summary
from w33_s12_vogel_spine_bridge import build_s12_vogel_spine_summary
from w33_weinberg_generator_bridge import build_weinberg_generator_summary
from w33_weinberg_reconstruction_bridge import build_weinberg_reconstruction_summary
from w33_srg_rosetta_lock_bridge import build_srg_rosetta_lock_summary
from w33_spectral_rosetta_lock_bridge import build_spectral_rosetta_lock_summary
from w33_curved_mode_projector_bridge import build_curved_mode_projector_bridge_summary
from w33_curved_mode_residue_bridge import build_curved_mode_residue_bridge_summary
from w33_curved_continuum_extractor_bridge import build_curved_continuum_extractor_summary
from w33_curved_weinberg_lock_bridge import build_curved_weinberg_lock_bridge_summary
from w33_curved_rosetta_reconstruction_bridge import build_curved_rosetta_reconstruction_summary
from w33_curved_finite_spectral_reconstruction_bridge import (
    build_curved_finite_spectral_reconstruction_summary,
)
from w33_curved_roundtrip_closure_bridge import build_curved_roundtrip_closure_summary
from w33_three_sample_master_closure_bridge import build_three_sample_master_closure_summary
from w33_exceptional_channel_continuum_bridge import (
    build_exceptional_channel_continuum_bridge_summary,
)
from w33_exceptional_operator_projector_bridge import (
    build_exceptional_operator_projector_summary,
)
from w33_exceptional_tensor_rank_bridge import (
    build_exceptional_tensor_rank_summary,
)
from w33_exceptional_residue_bridge import build_exceptional_residue_bridge_summary
from w33_d4_f4_tomotope_reye_bridge import build_d4_f4_tomotope_reye_summary
from w33_triality_ladder_algebra_bridge import build_triality_ladder_algebra_summary
from w33_curved_inverse_rosetta_bridge import build_curved_inverse_rosetta_summary


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
    curved_h2_host = build_curved_h2_host_bridge_summary()
    curved_h2_qutrit = build_curved_h2_qutrit_bridge_summary()
    curved_harmonic_qutrit_split = build_curved_harmonic_qutrit_split_bridge_summary()
    curved_h2_cup_plane = build_curved_h2_cup_plane_bridge_summary()
    k3_rank2_qutrit_plane = build_k3_rank2_qutrit_plane_bridge_summary()
    transport_mixed_plane_obstruction = build_transport_mixed_plane_obstruction_summary()
    k3_mixed_plane_a4_projection = build_k3_mixed_plane_a4_projection_summary()
    k3_refined_plane_persistence = build_k3_refined_plane_persistence_bridge_summary()
    k3_integral_h2_lattice = build_k3_integral_h2_lattice_bridge_summary()
    k3_primitive_plane_global_a4 = build_k3_primitive_plane_global_a4_bridge_summary()
    k3_three_u_decomposition = build_k3_three_u_decomposition_bridge_summary()
    k3_three_u_refinement = build_k3_three_u_refinement_bridge_summary()
    k3_three_u_complement_refinement = (
        build_k3_three_u_complement_refinement_bridge_summary()
    )
    k3_n16_e8e8 = build_k3_n16_e8e8_bridge_summary()
    k3_e8_factor_split = build_k3_e8_factor_split_bridge_summary()
    k3_e8_factor_refinement = build_k3_e8_factor_refinement_bridge_summary()
    k3_primitive_plane_three_u_alignment = (
        build_k3_primitive_plane_three_u_alignment_bridge_summary()
    )
    k3_selector_three_u_shadow = build_k3_selector_three_u_shadow_bridge_summary()
    k3_selector_e8_shadow = build_k3_selector_e8_shadow_bridge_summary()
    k3_selector_shadow_refinement = build_k3_selector_shadow_refinement_bridge_summary()
    k3_selector_a4_lattice_split = build_k3_selector_a4_lattice_split_bridge_summary()
    k3_selector_a4_five_factor = build_k3_selector_a4_five_factor_bridge_summary()
    k3_selector_a4_five_factor_refinement = (
        build_k3_selector_a4_five_factor_refinement_bridge_summary()
    )
    u1_family_a4_carrier = build_u1_family_a4_carrier_bridge_summary()
    u1_isotropic_line_obstruction = build_u1_isotropic_line_obstruction_bridge_summary()
    selector_a4_weight_hierarchy = build_selector_a4_weight_hierarchy_bridge_summary()
    transport_semisimplification_shadow = (
        build_transport_semisimplification_shadow_bridge_summary()
    )
    global_local_carrier_split = build_global_local_carrier_split_bridge_summary()
    u1_selector_line_selection = build_u1_selector_line_selection_bridge_summary()
    family_flag_visibility_obstruction = (
        build_family_flag_visibility_obstruction_bridge_summary()
    )
    e13_visibility_obstruction = build_e13_visibility_obstruction_bridge_summary()
    explicit_complexes = build_explicit_curved_4d_complexes_summary()
    triangulations = build_minimal_triangulation_summary()
    surface = build_surface_neighborly_summary()
    mobius = build_mobius_fano_summary()
    mod7_fano_duality = build_mod7_fano_duality_summary()
    heawood_harmonic = build_heawood_harmonic_summary()
    heawood_tetra_radical = build_heawood_tetra_radical_summary()
    heawood_klein_symmetry = build_heawood_klein_symmetry_summary()
    heawood_shell_ladder = build_heawood_shell_ladder_summary()
    klein_quartic_gf3_tetra = build_klein_quartic_gf3_tetra_summary()
    mobius_dual = build_mobius_szilassi_dual_summary()
    realization = build_realization_orbit_summary()
    surface_congruence_selector = build_surface_congruence_selector_summary()
    surface_hurwitz_flag = build_surface_hurwitz_flag_summary()
    mod12_selector_closure = build_mod12_selector_closure_summary()
    decimal_surface_flag = build_decimal_surface_flag_summary()
    fano_toroidal_complement = build_fano_toroidal_complement_summary()
    surface_physics_shell = build_surface_physics_shell_summary()
    toroidal_k7_spectral = build_toroidal_k7_spectral_summary()
    klein_hurwitz_extremal = build_klein_hurwitz_extremal_summary()
    hurwitz_237_selector = build_hurwitz_237_selector_summary()
    affine_middle_shell = build_affine_middle_shell_summary()
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
    transport_path_groupoid = build_transport_path_groupoid_summary()
    ternary_homological_code = build_ternary_homological_code_summary()
    transport_ternary_line = build_transport_ternary_line_summary()
    transport_ternary_extension = build_transport_ternary_extension_summary()
    transport_ternary_cocycle = build_transport_ternary_cocycle_summary()
    transport_curvature = build_transport_curvature_summary()
    transport_borel = build_transport_borel_factor_summary()
    transport_twisted_precomplex = build_transport_twisted_precomplex_summary()
    transport_matter_curved = build_transport_matter_curved_harmonic_summary()
    transport_spectral_selector = build_transport_spectral_selector_summary()
    transport_curved_dirac_refinement = build_transport_curved_dirac_refinement_summary()
    transport_curved_dirac_quadratic = build_transport_curved_dirac_quadratic_bridge_summary()
    adjacency_dirac_closure = build_adjacency_dirac_closure_summary()
    three_channel_operator = build_three_channel_operator_summary()
    dual_bose_mesner = build_dual_bose_mesner_bridge_summary()
    curved_eh_mode = build_curved_eh_mode_bridge_summary()
    eh_continuum_lock = build_eh_continuum_lock_summary()
    curvature_cyclotomic_lock = build_curvature_cyclotomic_lock_summary()
    q3_curved_selection = build_q3_curved_selection_summary()
    spectral_action_cyclotomic = build_spectral_action_cyclotomic_summary()
    spectral_action_q3_selection = build_spectral_action_q3_selection_summary()
    standard_model_cyclotomic = build_standard_model_cyclotomic_summary()
    monster_landauer_ternary = build_monster_landauer_ternary_bridge_summary()
    monster_shell_factorization = build_monster_shell_factorization_summary()
    monster_3adic_closure = build_monster_3adic_closure_summary()
    monster_3b_centralizer = build_monster_3b_centralizer_summary()
    monster_lagrangian_complement = build_monster_lagrangian_complement_summary()
    monster_selector_completion = build_monster_selector_completion_summary()
    monster_q5_completion = build_monster_q5_completion_summary()
    monster_transport_shell = build_monster_transport_shell_summary()
    monster_supertrace = build_monster_supertrace_summary()
    monster_moonshine_lift = build_monster_moonshine_lift_summary()
    monster_transport_moonshine = build_monster_transport_moonshine_summary()
    monster_gap_duality = build_monster_gap_duality_summary()
    monster_triangle_landauer = build_monster_triangle_landauer_summary()
    triality_moonshine_spine = build_triality_moonshine_spine_summary()
    vacuum_unity = build_vacuum_unity_summary()
    quantum_vacuum_standards = build_quantum_vacuum_standards_summary()
    natural_units_meaning = build_natural_units_meaning_summary()
    natural_units_topological = build_natural_units_topological_summary()
    natural_units_electroweak_split = build_natural_units_electroweak_split_summary()
    heawood_weinberg_denominator = build_heawood_weinberg_denominator_summary()
    heawood_q_center = build_heawood_q_center_summary()
    heawood_involution = build_heawood_involution_summary()
    heawood_clifford = build_heawood_clifford_summary()
    natural_units_projective_denominator = build_natural_units_projective_denominator_summary()
    natural_units_custodial = build_natural_units_custodial_summary()
    natural_units_sigma_shell = build_natural_units_sigma_shell_summary()
    natural_units_neutral_shell = build_natural_units_neutral_shell_summary()
    natural_units_root_gap = build_natural_units_root_gap_summary()
    heawood_electroweak_polarization = build_heawood_electroweak_polarization_summary()
    natural_units_cosmological_complement = build_natural_units_cosmological_complement_summary()
    natural_units_unit_balance = build_natural_units_unit_balance_summary()
    electroweak_lagrangian = build_electroweak_lagrangian_summary()
    one_scale_bosonic = build_one_scale_bosonic_summary()
    bosonic_action_completion = build_bosonic_action_completion_summary()
    standard_model_action_backbone = build_standard_model_action_backbone_summary()
    q3_fermion_hierarchy = build_q3_fermion_hierarchy_summary()
    alpha_hierarchy_gaussian = build_alpha_hierarchy_gaussian_summary()
    qcd_beta_phi6 = build_qcd_beta_phi6_summary()
    jones_mu4_selector = build_jones_mu4_selector_summary()
    f4_neutrino_scale = build_f4_neutrino_scale_summary()
    one_input_fermion_spectrum = build_one_input_fermion_spectrum_summary()
    l3_pfaffian_packet = build_l3_pfaffian_packet_summary()
    selector_firewall = build_selector_firewall_summary()
    theta_hierarchy = build_theta_hierarchy_summary()
    truncated_dirac_shell = build_truncated_dirac_shell_summary()
    yukawa_scaffold = build_yukawa_scaffold_summary()
    yukawa_unipotent_reduction = build_yukawa_unipotent_reduction_summary()
    yukawa_kronecker_reduction = build_yukawa_kronecker_reduction_summary()
    yukawa_gram_shell = build_yukawa_gram_shell_summary()
    yukawa_base_spectrum = build_yukawa_base_spectrum_summary()
    yukawa_active_spectrum = build_yukawa_active_spectrum_summary()
    s12_klein_projective = build_s12_klein_projective_summary()
    klein_quartic_ag21 = build_klein_quartic_ag21_summary()
    klein_harmonic_vogel = build_klein_harmonic_vogel_summary()
    klein_clifford_topological = build_klein_clifford_topological_summary()
    klein_bitangent_shell = build_klein_bitangent_shell_summary()
    s12_vogel_spine = build_s12_vogel_spine_summary()
    weinberg_generator = build_weinberg_generator_summary()
    weinberg_reconstruction = build_weinberg_reconstruction_summary()
    srg_rosetta_lock = build_srg_rosetta_lock_summary()
    spectral_rosetta_lock = build_spectral_rosetta_lock_summary()
    curved_mode_projector = build_curved_mode_projector_bridge_summary()
    curved_mode_residue = build_curved_mode_residue_bridge_summary()
    curved_continuum_extractor = build_curved_continuum_extractor_summary()
    curved_weinberg_lock = build_curved_weinberg_lock_bridge_summary()
    curved_rosetta_reconstruction = build_curved_rosetta_reconstruction_summary()
    curved_finite_spectral_reconstruction = build_curved_finite_spectral_reconstruction_summary()
    curved_roundtrip_closure = build_curved_roundtrip_closure_summary()
    three_sample_master_closure = build_three_sample_master_closure_summary()
    exceptional_channel_continuum = build_exceptional_channel_continuum_bridge_summary()
    exceptional_operator_projector = build_exceptional_operator_projector_summary()
    exceptional_tensor_rank = build_exceptional_tensor_rank_summary()
    exceptional_residue = build_exceptional_residue_bridge_summary()
    d4_f4_tomotope_reye = build_d4_f4_tomotope_reye_summary()
    triality_ladder_algebra = build_triality_ladder_algebra_summary()
    curved_inverse_rosetta = build_curved_inverse_rosetta_summary()
    fano_group = build_fano_group_summary()
    fano_square = build_fano_square_tomotope_summary()
    order = build_tomotope_order_summary()
    klitzing = build_klitzing_ladder_summary()
    partial_sheet = build_tomotope_partial_sheet_summary()
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
        "adjacency_dirac_closure_bridge": {
            "vertex_laplacian_formula": adjacency_dirac_closure["adjacency_side"]["vertex_laplacian_formula"],
            "vertex_laplacian_matches_formula_exactly": adjacency_dirac_closure["adjacency_side"]["vertex_laplacian_matches_formula_exactly"],
            "vertex_laplacian_spectrum": adjacency_dirac_closure["adjacency_side"]["vertex_laplacian_spectrum"],
            "edge_harmonic_dimension": adjacency_dirac_closure["hodge_lift_theorem"]["edge_harmonic_dimension"],
            "edge_exact_dimension": adjacency_dirac_closure["hodge_lift_theorem"]["exact_one_form_dimension"],
            "edge_coexact_dimension": adjacency_dirac_closure["hodge_lift_theorem"]["coexact_one_form_dimension"],
            "exact_one_form_spectrum_is_vertex_nonzero_spectrum": adjacency_dirac_closure["hodge_lift_theorem"]["exact_one_form_spectrum_is_vertex_nonzero_spectrum"],
            "triangle_laplacian_is_scalar_4": adjacency_dirac_closure["high_degree_regularities"]["triangle_laplacian_is_scalar_4"],
            "tetrahedron_laplacian_is_scalar_4": adjacency_dirac_closure["high_degree_regularities"]["tetrahedron_laplacian_is_scalar_4"],
            "df2_spectrum": adjacency_dirac_closure["finite_dirac_closure"]["df2_spectrum"],
            "a0_f": adjacency_dirac_closure["finite_dirac_closure"]["seeley_dewitt_moments"]["a0_f"],
            "a2_f": adjacency_dirac_closure["finite_dirac_closure"]["seeley_dewitt_moments"]["a2_f"],
            "a4_f": adjacency_dirac_closure["finite_dirac_closure"]["seeley_dewitt_moments"]["a4_f"],
            "mu_squared": adjacency_dirac_closure["finite_dirac_closure"]["spectral_action_ratios"]["mu_squared"],
            "lambda": adjacency_dirac_closure["finite_dirac_closure"]["spectral_action_ratios"]["lambda"],
            "higgs_ratio_square": adjacency_dirac_closure["finite_dirac_closure"]["spectral_action_ratios"]["higgs_ratio_square"],
            "full_finite_spectrum_forced_from_adjacency_plus_clique_regularities": adjacency_dirac_closure["finite_dirac_closure"]["full_finite_spectrum_forced_from_adjacency_plus_clique_regularities"],
        },
        "three_channel_operator_bridge": {
            "basis": three_channel_operator["operator_calculus"]["basis"],
            "three_entry_classes": three_channel_operator["operator_calculus"]["three_entry_classes"],
            "positive_projector_entry_values": three_channel_operator["spectral_projectors"]["positive_projector_entry_values"],
            "laplacian_pseudoinverse_entry_values": three_channel_operator["resistance_bridge"]["laplacian_pseudoinverse_entry_values"],
            "effective_resistance_adjacent": three_channel_operator["resistance_bridge"]["effective_resistance_adjacent"],
            "effective_resistance_nonadjacent": three_channel_operator["resistance_bridge"]["effective_resistance_nonadjacent"],
            "kemeny_constant": three_channel_operator["resistance_bridge"]["kemeny_constant"],
            "exact_mixing_rate": three_channel_operator["mixing_bridge"]["exact_mixing_rate"],
        },
        "dual_bose_mesner_bridge": {
            "w33_constant_projector_matches_exactly": dual_bose_mesner["w33"]["constant_projector_matches_exactly"],
            "transport_constant_projector_matches_exactly": dual_bose_mesner["transport"]["constant_projector_matches_exactly"],
            "shared_nontrivial_polynomial": dual_bose_mesner["shared_nontrivial_polynomial"]["polynomial"],
            "kills_mean_zero_on_w33": dual_bose_mesner["shared_nontrivial_polynomial"]["kills_mean_zero_on_w33"],
            "kills_mean_zero_on_transport": dual_bose_mesner["shared_nontrivial_polynomial"]["kills_mean_zero_on_transport"],
            "positive_channel_coefficients": dual_bose_mesner["shared_mean_zero_calculus"]["positive_channel_coefficients"],
            "negative_channel_coefficients": dual_bose_mesner["shared_mean_zero_calculus"]["negative_channel_coefficients"],
        },
        "curved_eh_mode_bridge": {
            "master_density_formula": curved_eh_mode["master_formula"]["density"],
            "master_integrated_formula": curved_eh_mode["master_formula"]["integrated"],
            "exact_scale_separation": curved_eh_mode["master_formula"]["exact_scale_separation"],
            "finite_df2_cosmological_limit": curved_eh_mode["profiles"][2]["global_coefficients"]["cosmological_density_limit"]["exact"],
            "finite_df2_eh_6_mode_coefficient": curved_eh_mode["profiles"][2]["global_coefficients"]["einstein_hilbert_6_mode_coefficient"]["exact"],
            "finite_df2_topological_1_mode_coefficient": curved_eh_mode["profiles"][2]["global_coefficients"]["topological_1_mode_coefficient"]["exact"],
            "a2_transport_cosmological_limit": curved_eh_mode["profiles"][3]["global_coefficients"]["cosmological_density_limit"]["exact"],
            "transport_dirac_cosmological_limit": curved_eh_mode["profiles"][4]["global_coefficients"]["cosmological_density_limit"]["exact"],
            "matter_transport_dirac_cosmological_limit": curved_eh_mode["profiles"][5]["global_coefficients"]["cosmological_density_limit"]["exact"],
            "cp2_finite_df2_curvature_mode_density": curved_eh_mode["profiles"][2]["seeds"][0]["density_formula"]["einstein_hilbert_density_coefficient"]["exact"],
            "k3_finite_df2_curvature_mode_density": curved_eh_mode["profiles"][2]["seeds"][1]["density_formula"]["einstein_hilbert_density_coefficient"]["exact"],
            "cp2_curvature_sign_matches_signature": curved_eh_mode["profiles"][2]["seeds"][0]["sign_matches_signature_for_curvature_mode"],
            "k3_curvature_sign_matches_signature": curved_eh_mode["profiles"][2]["seeds"][1]["sign_matches_signature_for_curvature_mode"],
        },
        "eh_continuum_lock_bridge": {
            "continuum_eh_coefficient": eh_continuum_lock["continuum_lock"]["continuum_eh_coefficient"]["exact"],
            "discrete_eh_6_mode_coefficient": eh_continuum_lock["continuum_lock"]["discrete_eh_6_mode_coefficient"]["exact"],
            "rank_factor": eh_continuum_lock["continuum_lock"]["rank_factor"]["exact"],
            "discrete_equals_rank_factor_times_continuum": eh_continuum_lock["continuum_lock"]["discrete_equals_rank_factor_times_continuum"],
            "rank_d1": eh_continuum_lock["rank_39_identifications"]["rank_d1"],
            "rank_mod_3_adjacency": eh_continuum_lock["rank_39_identifications"]["rank_mod_3_adjacency"],
            "nontrivial_adjacency_multiplicity_sum": eh_continuum_lock["rank_39_identifications"]["nontrivial_adjacency_multiplicity_sum"],
            "all_rank_39_identifications_agree": eh_continuum_lock["rank_39_identifications"]["all_equal_39"],
            "topological_1_mode_coefficient": eh_continuum_lock["topological_lock"]["topological_1_mode_coefficient"]["exact"],
            "absolute_euler_characteristic": eh_continuum_lock["topological_lock"]["absolute_euler_characteristic"],
            "q_cubic_plus_1": eh_continuum_lock["topological_lock"]["q_cubic_plus_1"],
            "topological_equals_q_cubic_plus_1_times_abs_chi": eh_continuum_lock["topological_lock"]["topological_equals_q_cubic_plus_1_times_abs_chi"],
        },
        "curvature_cyclotomic_lock_bridge": {
            "phi3": curvature_cyclotomic_lock["cyclotomic_factors"]["phi3"],
            "phi6": curvature_cyclotomic_lock["cyclotomic_factors"]["phi6"],
            "q_phi3": curvature_cyclotomic_lock["cyclotomic_factors"]["q_phi3"],
            "q_plus_1_phi6": curvature_cyclotomic_lock["cyclotomic_factors"]["q_plus_1_phi6"],
            "gravity_is_q_phi3_times_continuum": curvature_cyclotomic_lock["gravity_lock"]["discrete_equals_q_phi3_times_continuum"],
            "topology_is_q_plus_1_phi6_times_abs_chi": curvature_cyclotomic_lock["topology_lock"]["topological_equals_q_plus_1_phi6_times_abs_chi"],
            "topology_is_q_cubic_plus_1_times_abs_chi": curvature_cyclotomic_lock["topology_lock"]["equals_q_cubic_plus_1_times_abs_chi"],
        },
        "q3_curved_selection_bridge": {
            "gravity_polynomial": q3_curved_selection["curved_selection_equations"]["gravity_compression"]["polynomial"],
            "gravity_factorization": q3_curved_selection["curved_selection_equations"]["gravity_compression"]["factorization"],
            "gravity_unique_positive_integer_solution": q3_curved_selection["curved_selection_equations"]["gravity_compression"]["unique_positive_integer_solution"],
            "topology_polynomial": q3_curved_selection["curved_selection_equations"]["topology_compression"]["polynomial"],
            "topology_factorization": q3_curved_selection["curved_selection_equations"]["topology_compression"]["factorization"],
            "topology_unique_positive_integer_solution": q3_curved_selection["curved_selection_equations"]["topology_compression"]["unique_positive_integer_solution"],
        },
        "spectral_action_cyclotomic_bridge": {
            "phi3": spectral_action_cyclotomic["cyclotomic_data"]["phi3"],
            "phi6": spectral_action_cyclotomic["cyclotomic_data"]["phi6"],
            "four_phi3_plus_q": spectral_action_cyclotomic["cyclotomic_data"]["four_phi3_plus_q"],
            "a2_over_a0": spectral_action_cyclotomic["internal_spectral_action"]["a2_over_a0"]["exact"],
            "a4_over_a0": spectral_action_cyclotomic["internal_spectral_action"]["a4_over_a0"]["exact"],
            "higgs_ratio_square": spectral_action_cyclotomic["internal_spectral_action"]["higgs_ratio_square"]["exact"],
            "a2_over_a0_matches_formula": spectral_action_cyclotomic["internal_spectral_action"]["a2_over_a0_matches_formula"],
            "a4_over_a0_matches_formula": spectral_action_cyclotomic["internal_spectral_action"]["a4_over_a0_matches_formula"],
            "higgs_ratio_square_matches_formula": spectral_action_cyclotomic["internal_spectral_action"]["higgs_ratio_square_matches_formula"],
            "continuum_eh_over_a0": spectral_action_cyclotomic["gravity_lock"]["continuum_eh_over_a0"]["exact"],
            "discrete_6_mode_over_a0": spectral_action_cyclotomic["gravity_lock"]["discrete_6_mode_over_a0"]["exact"],
            "discrete_to_continuum_ratio": spectral_action_cyclotomic["gravity_lock"]["discrete_to_continuum_ratio"]["exact"],
            "continuum_eh_over_a0_matches_formula": spectral_action_cyclotomic["gravity_lock"]["continuum_eh_over_a0_matches_formula"],
            "discrete_6_mode_over_a0_matches_formula": spectral_action_cyclotomic["gravity_lock"]["discrete_6_mode_over_a0_matches_formula"],
            "discrete_to_continuum_matches_formula": spectral_action_cyclotomic["gravity_lock"]["discrete_to_continuum_matches_formula"],
        },
        "spectral_action_q3_selection_bridge": {
            "internal_polynomial": spectral_action_q3_selection["selection_equations"]["internal_a2_ratio"]["polynomial"],
            "internal_factorization": spectral_action_q3_selection["selection_equations"]["internal_a2_ratio"]["factorization"],
            "internal_unique_positive_integer_solution": spectral_action_q3_selection["selection_equations"]["internal_a2_ratio"]["unique_positive_integer_solution"],
            "a4_uses_same_polynomial": spectral_action_q3_selection["selection_equations"]["internal_a4_ratio"]["polynomial"]
            == spectral_action_q3_selection["selection_equations"]["internal_a2_ratio"]["polynomial"],
            "higgs_uses_same_polynomial": spectral_action_q3_selection["selection_equations"]["higgs_ratio"]["polynomial"]
            == spectral_action_q3_selection["selection_equations"]["internal_a2_ratio"]["polynomial"],
            "gravity_polynomial": spectral_action_q3_selection["selection_equations"]["gravity_normalization"]["polynomial"],
            "gravity_factorization": spectral_action_q3_selection["selection_equations"]["gravity_normalization"]["factorization"],
            "gravity_unique_positive_integer_solution": spectral_action_q3_selection["selection_equations"]["gravity_normalization"]["unique_positive_integer_solution"],
        },
        "standard_model_cyclotomic_bridge": {
            "sin2_theta_w_ew": standard_model_cyclotomic["promoted_observables"]["sin2_theta_w_ew"]["exact"],
            "tan_theta_c": standard_model_cyclotomic["promoted_observables"]["tan_theta_c"]["exact"],
            "sin2_theta_12": standard_model_cyclotomic["promoted_observables"]["sin2_theta_12"]["exact"],
            "sin2_theta_23": standard_model_cyclotomic["promoted_observables"]["sin2_theta_23"]["exact"],
            "sin2_theta_13": standard_model_cyclotomic["promoted_observables"]["sin2_theta_13"]["exact"],
            "higgs_ratio_square": standard_model_cyclotomic["promoted_observables"]["higgs_ratio_square"]["exact"],
            "omega_lambda": standard_model_cyclotomic["promoted_observables"]["omega_lambda"]["exact"],
            "tan_cabibbo_equals_ew_weinberg": standard_model_cyclotomic["closure_relations"]["tan_cabibbo_equals_ew_weinberg"],
            "pmns_23_equals_weinberg_plus_pmns_12": standard_model_cyclotomic["closure_relations"]["pmns_23_equals_weinberg_plus_pmns_12"],
            "omega_lambda_equals_q_times_weinberg": standard_model_cyclotomic["closure_relations"]["omega_lambda_equals_q_times_weinberg"],
            "reactor_has_phi3_phi6_denominator": standard_model_cyclotomic["closure_relations"]["reactor_has_phi3_phi6_denominator"],
            "higgs_uses_four_phi3_plus_q_denominator": standard_model_cyclotomic["closure_relations"]["higgs_uses_four_phi3_plus_q_denominator"],
        },
        "vacuum_unity_bridge": {
            "alpha_inverse": vacuum_unity["w33_alpha_input"]["alpha_inverse"]["exact"],
            "alpha": vacuum_unity["w33_alpha_input"]["alpha"]["exact"],
            "unity_relation": vacuum_unity["vacuum_unity_relations"]["c_squared_mu0_epsilon0"]["exact"],
            "impedance_admittance_unity": vacuum_unity["vacuum_unity_relations"]["z0_times_y0"]["exact"],
            "z0_equals_mu0_c": vacuum_unity["vacuum_unity_relations"]["z0_equals_mu0_c"],
            "z0_equals_one_over_epsilon0_c": vacuum_unity["vacuum_unity_relations"]["z0_equals_one_over_epsilon0_c"],
            "mu0_formula": vacuum_unity["vacuum_unity_relations"]["mu0_formula"],
            "epsilon0_formula": vacuum_unity["vacuum_unity_relations"]["epsilon0_formula"],
            "z0_formula": vacuum_unity["vacuum_unity_relations"]["z0_formula"],
            "mu0_prediction": vacuum_unity["predicted_vacuum_constants"]["mu0_si"]["scientific"],
            "epsilon0_prediction": vacuum_unity["predicted_vacuum_constants"]["epsilon0_si"]["scientific"],
            "z0_prediction": vacuum_unity["predicted_vacuum_constants"]["z0_si"]["scientific"],
            "mu0_error_tracks_alpha": vacuum_unity["codata_2022_comparison"]["mu0_error_tracks_alpha"],
            "epsilon0_error_tracks_negative_alpha": vacuum_unity["codata_2022_comparison"]["epsilon0_error_tracks_negative_alpha"],
            "z0_error_tracks_alpha": vacuum_unity["codata_2022_comparison"]["z0_error_tracks_alpha"],
            "selector_line_dimension": vacuum_unity["selector_cross_bridge"]["selector_line_dimension"],
            "vacuum_unity_matches_selector_rank": vacuum_unity["selector_cross_bridge"]["vacuum_unity_matches_selector_rank"],
        },
        "quantum_vacuum_standards_bridge": {
            "rk_formula": quantum_vacuum_standards["exact_quantum_standards"]["von_klitzing_constant"]["formula"],
            "kj_formula": quantum_vacuum_standards["exact_quantum_standards"]["josephson_constant"]["formula"],
            "g0_formula": quantum_vacuum_standards["exact_quantum_standards"]["conductance_quantum"]["formula"],
            "phi0_formula": quantum_vacuum_standards["exact_quantum_standards"]["flux_quantum"]["formula"],
            "rk_prediction": quantum_vacuum_standards["exact_quantum_standards"]["von_klitzing_constant"]["scientific"],
            "kj_prediction": quantum_vacuum_standards["exact_quantum_standards"]["josephson_constant"]["scientific"],
            "g0_prediction": quantum_vacuum_standards["exact_quantum_standards"]["conductance_quantum"]["scientific"],
            "phi0_prediction": quantum_vacuum_standards["exact_quantum_standards"]["flux_quantum"]["scientific"],
            "phi0_times_kj": quantum_vacuum_standards["exact_quantum_standards"]["phi0_times_kj"]["exact"],
            "rk_times_g0": quantum_vacuum_standards["exact_quantum_standards"]["rk_times_g0"]["exact"],
            "kj_squared_rk_h": quantum_vacuum_standards["exact_quantum_standards"]["kj_squared_rk_h"]["exact"],
            "z0_equals_2_alpha_rk": quantum_vacuum_standards["vacuum_transport_dictionary"]["z0_equals_2_alpha_rk"],
            "mu0_equals_2_alpha_rk_over_c": quantum_vacuum_standards["vacuum_transport_dictionary"]["mu0_equals_2_alpha_rk_over_c"],
            "epsilon0_equals_one_over_2_alpha_rk_c": quantum_vacuum_standards["vacuum_transport_dictionary"]["epsilon0_equals_one_over_2_alpha_rk_c"],
            "y0_equals_g0_over_4alpha": quantum_vacuum_standards["vacuum_transport_dictionary"]["y0_equals_g0_over_4alpha"],
            "alpha_from_z0_over_2rk": quantum_vacuum_standards["vacuum_transport_dictionary"]["alpha_from_z0_over_2rk"]["exact"],
            "alpha_from_z0_g0_over_4": quantum_vacuum_standards["vacuum_transport_dictionary"]["alpha_from_z0_g0_over_4"]["exact"],
            "z0_times_g0": quantum_vacuum_standards["vacuum_transport_dictionary"]["z0_times_g0"]["exact"],
            "rk_over_z0": quantum_vacuum_standards["vacuum_transport_dictionary"]["rk_over_z0"]["exact"],
        },
        "natural_units_meaning_bridge": {
            "convention": natural_units_meaning["heaviside_lorentz_natural_units"]["convention"],
            "alpha_formula": natural_units_meaning["heaviside_lorentz_natural_units"]["alpha_formula"],
            "e_hl_squared_symbolic": natural_units_meaning["heaviside_lorentz_natural_units"]["electric_charge_squared_symbolic"],
            "e_hl_squared": natural_units_meaning["heaviside_lorentz_natural_units"]["electric_charge_squared"],
            "e_hl": natural_units_meaning["heaviside_lorentz_natural_units"]["electric_charge"],
            "rk_natural_symbolic": natural_units_meaning["heaviside_lorentz_natural_units"]["von_klitzing_symbolic"],
            "rk_natural": natural_units_meaning["heaviside_lorentz_natural_units"]["von_klitzing_constant"],
            "g0_natural_symbolic": natural_units_meaning["heaviside_lorentz_natural_units"]["conductance_quantum_symbolic"],
            "g0_natural": natural_units_meaning["heaviside_lorentz_natural_units"]["conductance_quantum"],
            "kj_natural": natural_units_meaning["heaviside_lorentz_natural_units"]["josephson_constant"],
            "phi0_natural": natural_units_meaning["heaviside_lorentz_natural_units"]["flux_quantum"],
            "vacuum_unity_becomes_unit_element": natural_units_meaning["heaviside_lorentz_natural_units"]["vacuum_unity_becomes_unit_element"],
            "z0_equals_2alpha_rk_becomes_unit_identity": natural_units_meaning["heaviside_lorentz_natural_units"]["z0_equals_2alpha_rk_becomes_unit_identity"],
            "alpha_equals_g0_over_4": natural_units_meaning["heaviside_lorentz_natural_units"]["alpha_equals_g0_over_4"],
            "rk_times_g0_equals_2": natural_units_meaning["heaviside_lorentz_natural_units"]["rk_times_g0_equals_2"],
            "phi0_times_kj_equals_1": natural_units_meaning["heaviside_lorentz_natural_units"]["phi0_times_kj_equals_1"],
            "gaussian_alpha_formula": natural_units_meaning["gaussian_crosscheck"]["alpha_formula"],
            "heaviside_equals_4pi_gaussian": natural_units_meaning["gaussian_crosscheck"]["heaviside_equals_4pi_gaussian"],
            "weinberg_x": natural_units_meaning["dimensionless_graph_observables"]["weinberg_x"],
            "higgs_ratio_square": natural_units_meaning["dimensionless_graph_observables"]["higgs_ratio_square"],
            "omega_lambda": natural_units_meaning["dimensionless_graph_observables"]["omega_lambda"],
            "a2_over_a0": natural_units_meaning["dimensionless_graph_observables"]["a2_over_a0"],
            "a4_over_a0": natural_units_meaning["dimensionless_graph_observables"]["a4_over_a0"],
            "discrete_to_continuum_ratio": natural_units_meaning["dimensionless_graph_observables"]["discrete_to_continuum_ratio"],
            "topological_over_continuum": natural_units_meaning["dimensionless_graph_observables"]["topological_over_continuum"],
            "graphs_mean_couplings_and_mode_weights_in_natural_units": natural_units_meaning["dimensionless_graph_observables"]["graphs_mean_couplings_and_mode_weights_in_natural_units"],
            "si_vacuum_is_reexpression_of_dimensionless_package": natural_units_meaning["dimensionless_graph_observables"]["si_vacuum_is_reexpression_of_dimensionless_package"],
        },
        "natural_units_topological_bridge": {
            "q": natural_units_topological["local_shell_dictionary"]["q"],
            "lambda": natural_units_topological["local_shell_dictionary"]["lambda"],
            "mu": natural_units_topological["local_shell_dictionary"]["mu"],
            "phi6": natural_units_topological["local_shell_dictionary"]["phi6"],
            "q_squared": natural_units_topological["local_shell_dictionary"]["q_squared"],
            "lambda_plus_phi6": natural_units_topological["local_shell_dictionary"]["lambda_plus_phi6"],
            "rk_formula": natural_units_topological["natural_unit_transport_dictionary"]["rk_formula"],
            "g0_formula": natural_units_topological["natural_unit_transport_dictionary"]["g0_formula"],
            "z0_unit_formula": natural_units_topological["natural_unit_transport_dictionary"]["z0_unit_formula"],
            "y0_unit_formula": natural_units_topological["natural_unit_transport_dictionary"]["y0_unit_formula"],
            "flux_josephson_unit_formula": natural_units_topological["natural_unit_transport_dictionary"]["flux_josephson_unit_formula"],
            "rk": natural_units_topological["natural_unit_transport_dictionary"]["rk"]["exact"],
            "g0": natural_units_topological["natural_unit_transport_dictionary"]["g0"]["exact"],
            "rk_times_g0": natural_units_topological["natural_unit_transport_dictionary"]["rk_times_g0"]["exact"],
            "mu_over_lambda": natural_units_topological["natural_unit_transport_dictionary"]["mu_over_lambda"]["exact"],
            "packet_dimension": natural_units_topological["topological_unit_dictionary"]["packet_dimension"],
            "fano_selector_formula": natural_units_topological["topological_unit_dictionary"]["fano_selector_formula"],
            "toroidal_shell_formula": natural_units_topological["topological_unit_dictionary"]["toroidal_shell_formula"],
            "normalized_unit_formula": natural_units_topological["topological_unit_dictionary"]["normalized_unit_formula"],
            "vacuum_unit_from_local_shell": natural_units_topological["topological_unit_dictionary"]["vacuum_unit_from_local_shell"]["exact"],
            "fano_nontrivial_trace": natural_units_topological["topological_unit_dictionary"]["fano_nontrivial_trace"],
            "toroidal_nontrivial_trace": natural_units_topological["topological_unit_dictionary"]["toroidal_nontrivial_trace"],
            "combined_nontrivial_trace": natural_units_topological["topological_unit_dictionary"]["combined_nontrivial_trace"],
            "rk_equals_one_over_lambda_alpha": natural_units_topological["exact_factorizations"]["rk_equals_one_over_lambda_alpha"],
            "g0_equals_mu_alpha": natural_units_topological["exact_factorizations"]["g0_equals_mu_alpha"],
            "z0_unit_matches_lambda_alpha_rk": natural_units_topological["exact_factorizations"]["z0_unit_matches_lambda_alpha_rk"],
            "y0_unit_matches_g0_over_mu_alpha": natural_units_topological["exact_factorizations"]["y0_unit_matches_g0_over_mu_alpha"],
            "rk_times_g0_equals_mu_over_lambda": natural_units_topological["exact_factorizations"]["rk_times_g0_equals_mu_over_lambda"],
            "lambda_plus_phi6_equals_q_squared": natural_units_topological["exact_factorizations"]["lambda_plus_phi6_equals_q_squared"],
            "vacuum_unit_equals_lambda_plus_phi6_over_q_squared": natural_units_topological["exact_factorizations"]["vacuum_unit_equals_lambda_plus_phi6_over_q_squared"],
            "normalized_complement_is_identity": natural_units_topological["exact_factorizations"]["normalized_complement_is_identity"],
            "flux_josephson_unit_matches_selector_line": natural_units_topological["exact_factorizations"]["flux_josephson_unit_matches_selector_line"],
            "unit_operator_matches_natural_vacuum": natural_units_topological["exact_factorizations"]["unit_operator_matches_natural_vacuum"],
            "transport_standards_live_on_same_local_shell": natural_units_topological["exact_factorizations"]["transport_standards_live_on_same_local_shell"],
        },
        "natural_units_electroweak_split_bridge": {
            "q": natural_units_electroweak_split["nested_complement_dictionary"]["q"],
            "lambda": natural_units_electroweak_split["nested_complement_dictionary"]["lambda"],
            "phi6": natural_units_electroweak_split["nested_complement_dictionary"]["phi6"],
            "q_squared": natural_units_electroweak_split["nested_complement_dictionary"]["q_squared"],
            "theta_w33": natural_units_electroweak_split["nested_complement_dictionary"]["theta_w33"],
            "phi3": natural_units_electroweak_split["nested_complement_dictionary"]["phi3"],
            "local_unit_formula": natural_units_electroweak_split["nested_complement_dictionary"]["local_unit_formula"],
            "electroweak_unit_formula": natural_units_electroweak_split["nested_complement_dictionary"]["electroweak_unit_formula"],
            "local_unit_value": natural_units_electroweak_split["nested_complement_dictionary"]["local_unit_value"]["exact"],
            "electroweak_unit_value": natural_units_electroweak_split["nested_complement_dictionary"]["electroweak_unit_value"]["exact"],
            "weinberg_formula": natural_units_electroweak_split["electroweak_split_dictionary"]["weinberg_formula"],
            "cosine_formula": natural_units_electroweak_split["electroweak_split_dictionary"]["cosine_formula"],
            "electric_reciprocal_formula": natural_units_electroweak_split["electroweak_split_dictionary"]["electric_reciprocal_formula"],
            "weak_reciprocal_formula": natural_units_electroweak_split["electroweak_split_dictionary"]["weak_reciprocal_formula"],
            "hypercharge_reciprocal_formula": natural_units_electroweak_split["electroweak_split_dictionary"]["hypercharge_reciprocal_formula"],
            "neutral_reciprocal_formula": natural_units_electroweak_split["electroweak_split_dictionary"]["neutral_reciprocal_formula"],
            "sin2_theta_w": natural_units_electroweak_split["electroweak_split_dictionary"]["sin2_theta_w"]["exact"],
            "cos2_theta_w": natural_units_electroweak_split["electroweak_split_dictionary"]["cos2_theta_w"]["exact"],
            "q_over_phi3": natural_units_electroweak_split["electroweak_split_dictionary"]["q_over_phi3"]["exact"],
            "theta_over_phi3": natural_units_electroweak_split["electroweak_split_dictionary"]["theta_over_phi3"]["exact"],
            "reciprocal_g": natural_units_electroweak_split["electroweak_split_dictionary"]["reciprocal_g"]["exact"],
            "reciprocal_gprime": natural_units_electroweak_split["electroweak_split_dictionary"]["reciprocal_gprime"]["exact"],
            "reciprocal_gz": natural_units_electroweak_split["electroweak_split_dictionary"]["reciprocal_gz"]["exact"],
            "tan2_theta_w": natural_units_electroweak_split["electroweak_split_dictionary"]["tan2_theta_w"]["exact"],
            "theta_over_q": natural_units_electroweak_split["electroweak_split_dictionary"]["theta_over_q"]["exact"],
            "lambda_plus_phi6_equals_q_squared": natural_units_electroweak_split["exact_factorizations"]["lambda_plus_phi6_equals_q_squared"],
            "theta_equals_q_plus_phi6": natural_units_electroweak_split["exact_factorizations"]["theta_equals_q_plus_phi6"],
            "q_plus_theta_equals_phi3": natural_units_electroweak_split["exact_factorizations"]["q_plus_theta_equals_phi3"],
            "phi3_equals_2q_plus_phi6": natural_units_electroweak_split["exact_factorizations"]["phi3_equals_2q_plus_phi6"],
            "weinberg_equals_q_over_phi3": natural_units_electroweak_split["exact_factorizations"]["weinberg_equals_q_over_phi3"],
            "cosine_equals_theta_over_phi3": natural_units_electroweak_split["exact_factorizations"]["cosine_equals_theta_over_phi3"],
            "sin2_plus_cos2_equals_unity": natural_units_electroweak_split["exact_factorizations"]["sin2_plus_cos2_equals_unity"],
            "weak_reciprocal_matches_weinberg": natural_units_electroweak_split["exact_factorizations"]["weak_reciprocal_matches_weinberg"],
            "hypercharge_reciprocal_matches_cosine": natural_units_electroweak_split["exact_factorizations"]["hypercharge_reciprocal_matches_cosine"],
            "electric_reciprocal_harmonic_sum_closes": natural_units_electroweak_split["exact_factorizations"]["electric_reciprocal_harmonic_sum_closes"],
            "g_squared_over_gprime_squared_equals_theta_over_q": natural_units_electroweak_split["exact_factorizations"]["g_squared_over_gprime_squared_equals_theta_over_q"],
            "neutral_reciprocal_equals_q_theta_over_phi3_squared": natural_units_electroweak_split["exact_factorizations"]["neutral_reciprocal_equals_q_theta_over_phi3_squared"],
            "local_and_electroweak_are_nested_unit_laws": natural_units_electroweak_split["exact_factorizations"]["local_and_electroweak_are_nested_unit_laws"],
        },
        "heawood_weinberg_denominator_bridge": {
            "middle_quadratic_polynomial": heawood_weinberg_denominator["heawood_shell_dictionary"]["middle_quadratic_polynomial"],
            "shared_six_channel": heawood_weinberg_denominator["heawood_shell_dictionary"]["shared_six_channel"],
            "phi6": heawood_weinberg_denominator["heawood_shell_dictionary"]["phi6"],
            "phi3": heawood_weinberg_denominator["heawood_shell_dictionary"]["phi3"],
            "theta_w33": heawood_weinberg_denominator["heawood_shell_dictionary"]["theta_w33"],
            "denominator_formula": heawood_weinberg_denominator["heawood_shell_dictionary"]["denominator_formula"],
            "theta_formula": heawood_weinberg_denominator["heawood_shell_dictionary"]["theta_formula"],
            "weinberg_from_heawood_formula": heawood_weinberg_denominator["electroweak_from_heawood_dictionary"]["weinberg_from_heawood_formula"],
            "cosine_from_heawood_formula": heawood_weinberg_denominator["electroweak_from_heawood_dictionary"]["cosine_from_heawood_formula"],
            "pmns23_from_heawood_formula": heawood_weinberg_denominator["electroweak_from_heawood_dictionary"]["pmns23_from_heawood_formula"],
            "sin2_theta_w": heawood_weinberg_denominator["electroweak_from_heawood_dictionary"]["sin2_theta_w"]["exact"],
            "cos2_theta_w": heawood_weinberg_denominator["electroweak_from_heawood_dictionary"]["cos2_theta_w"]["exact"],
            "sin2_theta_23": heawood_weinberg_denominator["electroweak_from_heawood_dictionary"]["sin2_theta_23"]["exact"],
            "q_over_heawood_denominator": heawood_weinberg_denominator["electroweak_from_heawood_dictionary"]["q_over_heawood_denominator"]["exact"],
            "theta_over_heawood_denominator": heawood_weinberg_denominator["electroweak_from_heawood_dictionary"]["theta_over_heawood_denominator"]["exact"],
            "phi6_over_heawood_denominator": heawood_weinberg_denominator["electroweak_from_heawood_dictionary"]["phi6_over_heawood_denominator"]["exact"],
            "phi3_equals_shared_six_plus_phi6": heawood_weinberg_denominator["exact_factorizations"]["phi3_equals_shared_six_plus_phi6"],
            "theta_equals_q_plus_phi6": heawood_weinberg_denominator["exact_factorizations"]["theta_equals_q_plus_phi6"],
            "weinberg_equals_q_over_heawood_denominator": heawood_weinberg_denominator["exact_factorizations"]["weinberg_equals_q_over_heawood_denominator"],
            "cosine_equals_theta_over_heawood_denominator": heawood_weinberg_denominator["exact_factorizations"]["cosine_equals_theta_over_heawood_denominator"],
            "pmns23_equals_phi6_over_heawood_denominator": heawood_weinberg_denominator["exact_factorizations"]["pmns23_equals_phi6_over_heawood_denominator"],
        },
        "heawood_q_center_bridge": {
            "middle_quadratic_polynomial": heawood_q_center["heawood_q_center_dictionary"]["middle_quadratic_polynomial"],
            "q_centered_formula": heawood_q_center["heawood_q_center_dictionary"]["q_centered_formula"],
            "root_formula": heawood_q_center["heawood_q_center_dictionary"]["root_formula"],
            "q": heawood_q_center["heawood_q_center_dictionary"]["q"],
            "lambda": heawood_q_center["heawood_q_center_dictionary"]["lambda"],
            "phi6": heawood_q_center["heawood_q_center_dictionary"]["phi6"],
            "phi3": heawood_q_center["heawood_q_center_dictionary"]["phi3"],
            "middle_branch_minus": heawood_q_center["heawood_q_center_dictionary"]["middle_branch_minus"],
            "middle_branch_plus": heawood_q_center["heawood_q_center_dictionary"]["middle_branch_plus"],
            "middle_shell_trace_exact": heawood_q_center["heawood_q_center_dictionary"]["middle_shell_trace_exact"],
            "middle_shell_pseudodeterminant_exact": heawood_q_center["heawood_q_center_dictionary"]["middle_shell_pseudodeterminant_exact"],
            "linear_term_equals_2q": heawood_q_center["exact_factorizations"]["linear_term_equals_2q"],
            "constant_term_equals_phi6": heawood_q_center["exact_factorizations"]["constant_term_equals_phi6"],
            "q_squared_minus_phi6_equals_lambda": heawood_q_center["exact_factorizations"]["q_squared_minus_phi6_equals_lambda"],
            "roots_equal_q_plus_minus_sqrt_lambda": heawood_q_center["exact_factorizations"]["roots_equal_q_plus_minus_sqrt_lambda"],
            "phi3_equals_2q_plus_phi6": heawood_q_center["exact_factorizations"]["phi3_equals_2q_plus_phi6"],
            "middle_trace_equals_q_times_gauge_dimension": heawood_q_center["exact_factorizations"]["middle_trace_equals_q_times_gauge_dimension"],
            "middle_pseudodeterminant_equals_phi6_to_6": heawood_q_center["exact_factorizations"]["middle_pseudodeterminant_equals_phi6_to_6"],
        },
        "heawood_involution_bridge": {
            "middle_quadratic_polynomial": heawood_involution["centered_shell_dictionary"]["middle_quadratic_polynomial"],
            "centered_quadratic_formula": heawood_involution["centered_shell_dictionary"]["centered_quadratic_formula"],
            "operator_formula": heawood_involution["centered_shell_dictionary"]["operator_formula"],
            "normalized_involution_formula": heawood_involution["centered_shell_dictionary"]["normalized_involution_formula"],
            "q": heawood_involution["centered_shell_dictionary"]["q"],
            "lambda": heawood_involution["centered_shell_dictionary"]["lambda"],
            "phi6": heawood_involution["centered_shell_dictionary"]["phi6"],
            "adjacency_quartic_polynomial": heawood_involution["centered_shell_dictionary"]["adjacency_quartic_polynomial"],
            "middle_projector_rank": heawood_involution["centered_shell_dictionary"]["middle_projector_rank"],
            "q_squared_minus_phi6_equals_lambda": heawood_involution["exact_factorizations"]["q_squared_minus_phi6_equals_lambda"],
            "centered_shell_relation_holds": heawood_involution["exact_factorizations"]["centered_shell_relation_holds"],
            "normalized_operator_is_involution": heawood_involution["exact_factorizations"]["normalized_operator_is_involution"],
            "middle_projector_is_idempotent": heawood_involution["exact_factorizations"]["middle_projector_is_idempotent"],
            "middle_shell_rank_is_12": heawood_involution["exact_factorizations"]["middle_shell_rank_is_12"],
        },
        "heawood_clifford_bridge": {
            "gamma_formula": heawood_clifford["clifford_dictionary"]["gamma_formula"],
            "gamma_mid_formula": heawood_clifford["clifford_dictionary"]["gamma_mid_formula"],
            "j_mid_formula": heawood_clifford["clifford_dictionary"]["j_mid_formula"],
            "k_mid_formula": heawood_clifford["clifford_dictionary"]["k_mid_formula"],
            "pi_plus_formula": heawood_clifford["clifford_dictionary"]["pi_plus_formula"],
            "pi_minus_formula": heawood_clifford["clifford_dictionary"]["pi_minus_formula"],
            "middle_shell_rank": heawood_clifford["clifford_dictionary"]["middle_shell_rank"],
            "complex_rank": heawood_clifford["clifford_dictionary"]["complex_rank"],
            "gamma_mid_squared_equals_middle_projector": heawood_clifford["exact_factorizations"]["gamma_mid_squared_equals_middle_projector"],
            "j_mid_squared_equals_middle_projector": heawood_clifford["exact_factorizations"]["j_mid_squared_equals_middle_projector"],
            "gamma_and_j_anticommute": heawood_clifford["exact_factorizations"]["gamma_and_j_anticommute"],
            "k_mid_squared_equals_minus_middle_projector": heawood_clifford["exact_factorizations"]["k_mid_squared_equals_minus_middle_projector"],
            "pi_plus_is_projector": heawood_clifford["exact_factorizations"]["pi_plus_is_projector"],
            "pi_minus_is_projector": heawood_clifford["exact_factorizations"]["pi_minus_is_projector"],
            "pi_plus_pi_minus_zero": heawood_clifford["exact_factorizations"]["pi_plus_pi_minus_zero"],
            "pi_plus_rank_is_6": heawood_clifford["exact_factorizations"]["pi_plus_rank_is_6"],
            "pi_minus_rank_is_6": heawood_clifford["exact_factorizations"]["pi_minus_rank_is_6"],
            "middle_shell_is_12_equals_6_plus_6": heawood_clifford["exact_factorizations"]["middle_shell_is_12_equals_6_plus_6"],
        },
        "natural_units_projective_denominator_bridge": {
            "fano_selector_formula": natural_units_projective_denominator["metrology_shell_dictionary"]["fano_selector_formula"],
            "metrology_selector_formula": natural_units_projective_denominator["metrology_shell_dictionary"]["metrology_selector_formula"],
            "toroidal_shell_formula": natural_units_projective_denominator["metrology_shell_dictionary"]["toroidal_shell_formula"],
            "local_sum_formula": natural_units_projective_denominator["metrology_shell_dictionary"]["local_sum_formula"],
            "q_from_selector_and_metrology_formula": natural_units_projective_denominator["metrology_shell_dictionary"]["q_from_selector_and_metrology_formula"],
            "shared_six_formula": natural_units_projective_denominator["metrology_shell_dictionary"]["shared_six_formula"],
            "selector_line": natural_units_projective_denominator["metrology_shell_dictionary"]["selector_line"],
            "q": natural_units_projective_denominator["metrology_shell_dictionary"]["q"],
            "rk_times_g0": natural_units_projective_denominator["metrology_shell_dictionary"]["rk_times_g0"]["exact"],
            "phi6": natural_units_projective_denominator["metrology_shell_dictionary"]["phi6"],
            "q_squared": natural_units_projective_denominator["metrology_shell_dictionary"]["q_squared"],
            "phi3_formula": natural_units_projective_denominator["projective_denominator_dictionary"]["phi3_formula"],
            "theta_formula": natural_units_projective_denominator["projective_denominator_dictionary"]["theta_formula"],
            "phi3": natural_units_projective_denominator["projective_denominator_dictionary"]["phi3"],
            "theta_w33": natural_units_projective_denominator["projective_denominator_dictionary"]["theta_w33"],
            "selector_plus_projective_plus_shells": natural_units_projective_denominator["projective_denominator_dictionary"]["selector_plus_projective_plus_shells"]["exact"],
            "theta_from_selector_and_shells": natural_units_projective_denominator["projective_denominator_dictionary"]["theta_from_selector_and_shells"]["exact"],
            "sin2_theta_w_formula": natural_units_projective_denominator["projective_denominator_dictionary"]["sin2_theta_w_formula"],
            "cos2_theta_w_formula": natural_units_projective_denominator["projective_denominator_dictionary"]["cos2_theta_w_formula"],
            "sin2_theta_w": natural_units_projective_denominator["projective_denominator_dictionary"]["sin2_theta_w"]["exact"],
            "cos2_theta_w": natural_units_projective_denominator["projective_denominator_dictionary"]["cos2_theta_w"]["exact"],
            "q_over_projective_denominator": natural_units_projective_denominator["projective_denominator_dictionary"]["q_over_projective_denominator"]["exact"],
            "theta_over_projective_denominator": natural_units_projective_denominator["projective_denominator_dictionary"]["theta_over_projective_denominator"]["exact"],
            "selector_coefficient_equals_metrology_coefficient": natural_units_projective_denominator["exact_factorizations"]["selector_coefficient_equals_metrology_coefficient"],
            "q_equals_selector_line_plus_metrology_shell": natural_units_projective_denominator["exact_factorizations"]["q_equals_selector_line_plus_metrology_shell"],
            "shared_six_equals_selector_plus_projective_plus_metrology_shell": natural_units_projective_denominator["exact_factorizations"]["shared_six_equals_selector_plus_projective_plus_metrology_shell"],
            "metrology_plus_qcd_shell_equals_q_squared": natural_units_projective_denominator["exact_factorizations"]["metrology_plus_qcd_shell_equals_q_squared"],
            "phi3_equals_selector_plus_projective_plus_shells": natural_units_projective_denominator["exact_factorizations"]["phi3_equals_selector_plus_projective_plus_shells"],
            "theta_equals_selector_plus_shells": natural_units_projective_denominator["exact_factorizations"]["theta_equals_selector_plus_shells"],
            "weinberg_equals_q_over_projective_denominator": natural_units_projective_denominator["exact_factorizations"]["weinberg_equals_q_over_projective_denominator"],
            "cosine_equals_theta_over_projective_denominator": natural_units_projective_denominator["exact_factorizations"]["cosine_equals_theta_over_projective_denominator"],
            "projective_denominator_rebuilds_from_natural_units_shells": natural_units_projective_denominator["exact_factorizations"]["projective_denominator_rebuilds_from_natural_units_shells"],
        },
        "natural_units_custodial_bridge": {
            "phi3": natural_units_custodial["custodial_shell_dictionary"]["phi3"],
            "theta_w33": natural_units_custodial["custodial_shell_dictionary"]["theta_w33"],
            "selector_line": natural_units_custodial["custodial_shell_dictionary"]["selector_line"],
            "q": natural_units_custodial["custodial_shell_dictionary"]["q"],
            "rk_times_g0": natural_units_custodial["custodial_shell_dictionary"]["rk_times_g0"]["exact"],
            "phi6": natural_units_custodial["custodial_shell_dictionary"]["phi6"],
            "custodial_numerator_formula": natural_units_custodial["custodial_shell_dictionary"]["custodial_numerator_formula"],
            "denominator_formula": natural_units_custodial["custodial_shell_dictionary"]["denominator_formula"],
            "mass_ratio_formula": natural_units_custodial["custodial_shell_dictionary"]["mass_ratio_formula"],
            "gap_formula": natural_units_custodial["custodial_shell_dictionary"]["gap_formula"],
            "mw_squared_over_mz_squared": natural_units_custodial["weak_mass_dictionary"]["mw_squared_over_mz_squared"]["exact"],
            "z_gap_over_z_squared": natural_units_custodial["weak_mass_dictionary"]["z_gap_over_z_squared"]["exact"],
            "sin2_theta_w": natural_units_custodial["weak_mass_dictionary"]["sin2_theta_w"]["exact"],
            "cos2_theta_w": natural_units_custodial["weak_mass_dictionary"]["cos2_theta_w"]["exact"],
            "theta_over_phi3": natural_units_custodial["weak_mass_dictionary"]["theta_over_phi3"]["exact"],
            "q_over_phi3": natural_units_custodial["weak_mass_dictionary"]["q_over_phi3"]["exact"],
            "rho_parameter": natural_units_custodial["weak_mass_dictionary"]["rho_parameter"]["exact"],
            "theta_equals_selector_plus_metrology_plus_qcd": natural_units_custodial["exact_factorizations"]["theta_equals_selector_plus_metrology_plus_qcd"],
            "phi3_equals_selector_plus_projective_plus_metrology_plus_qcd": natural_units_custodial["exact_factorizations"]["phi3_equals_selector_plus_projective_plus_metrology_plus_qcd"],
            "mw_over_mz_squared_equals_cos2_theta_w": natural_units_custodial["exact_factorizations"]["mw_over_mz_squared_equals_cos2_theta_w"],
            "z_gap_over_z_squared_equals_sin2_theta_w": natural_units_custodial["exact_factorizations"]["z_gap_over_z_squared_equals_sin2_theta_w"],
            "cos2_equals_theta_over_phi3": natural_units_custodial["exact_factorizations"]["cos2_equals_theta_over_phi3"],
            "sin2_equals_q_over_phi3": natural_units_custodial["exact_factorizations"]["sin2_equals_q_over_phi3"],
            "custodial_split_sums_to_unity": natural_units_custodial["exact_factorizations"]["custodial_split_sums_to_unity"],
            "rho_equals_one": natural_units_custodial["exact_factorizations"]["rho_equals_one"],
        },
        "natural_units_sigma_shell_bridge": {
            "sigma_formula": natural_units_sigma_shell["sigma_shell_dictionary"]["sigma_formula"],
            "sigma": natural_units_sigma_shell["sigma_shell_dictionary"]["sigma"],
            "metrology_eigenvalue": natural_units_sigma_shell["sigma_shell_dictionary"]["metrology_eigenvalue"],
            "toroidal_eigenvalue": natural_units_sigma_shell["sigma_shell_dictionary"]["toroidal_eigenvalue"],
            "complement_eigenvalue": natural_units_sigma_shell["sigma_shell_dictionary"]["complement_eigenvalue"],
            "phi3_formula": natural_units_sigma_shell["sigma_shell_dictionary"]["phi3_formula"],
            "heawood_middle_rank_formula": natural_units_sigma_shell["sigma_shell_dictionary"]["heawood_middle_rank_formula"],
            "heawood_middle_trace_formula": natural_units_sigma_shell["sigma_shell_dictionary"]["heawood_middle_trace_formula"],
            "metrology_trace": natural_units_sigma_shell["trace_ladder_dictionary"]["metrology_trace"],
            "toroidal_trace": natural_units_sigma_shell["trace_ladder_dictionary"]["toroidal_trace"],
            "complement_trace": natural_units_sigma_shell["trace_ladder_dictionary"]["complement_trace"],
            "heawood_middle_rank": natural_units_sigma_shell["trace_ladder_dictionary"]["heawood_middle_rank"],
            "heawood_middle_trace": natural_units_sigma_shell["trace_ladder_dictionary"]["heawood_middle_trace"],
            "single_surface_flags": natural_units_sigma_shell["trace_ladder_dictionary"]["single_surface_flags"],
            "dual_pair_flags": natural_units_sigma_shell["trace_ladder_dictionary"]["dual_pair_flags"],
            "full_heawood_order": natural_units_sigma_shell["trace_ladder_dictionary"]["full_heawood_order"],
            "sigma_equals_selector_plus_projective_plus_metrology": natural_units_sigma_shell["exact_factorizations"]["sigma_equals_selector_plus_projective_plus_metrology"],
            "phi3_equals_sigma_plus_phi6": natural_units_sigma_shell["exact_factorizations"]["phi3_equals_sigma_plus_phi6"],
            "metrology_trace_equals_sigma_times_rk_times_g0": natural_units_sigma_shell["exact_factorizations"]["metrology_trace_equals_sigma_times_rk_times_g0"],
            "toroidal_trace_equals_sigma_times_phi6": natural_units_sigma_shell["exact_factorizations"]["toroidal_trace_equals_sigma_times_phi6"],
            "complement_trace_equals_sigma_times_q_squared": natural_units_sigma_shell["exact_factorizations"]["complement_trace_equals_sigma_times_q_squared"],
            "complement_trace_equals_metrology_plus_toroidal_trace": natural_units_sigma_shell["exact_factorizations"]["complement_trace_equals_metrology_plus_toroidal_trace"],
            "heawood_middle_rank_equals_two_sigma": natural_units_sigma_shell["exact_factorizations"]["heawood_middle_rank_equals_two_sigma"],
            "heawood_middle_trace_equals_two_q_sigma": natural_units_sigma_shell["exact_factorizations"]["heawood_middle_trace_equals_two_q_sigma"],
            "single_surface_flags_equals_two_toroidal_traces": natural_units_sigma_shell["exact_factorizations"]["single_surface_flags_equals_two_toroidal_traces"],
            "dual_pair_flags_equals_four_toroidal_traces": natural_units_sigma_shell["exact_factorizations"]["dual_pair_flags_equals_four_toroidal_traces"],
            "full_heawood_order_equals_eight_toroidal_traces": natural_units_sigma_shell["exact_factorizations"]["full_heawood_order_equals_eight_toroidal_traces"],
        },
        "natural_units_neutral_shell_bridge": {
            "neutral_numerator_formula": natural_units_neutral_shell["neutral_shell_dictionary"]["neutral_numerator_formula"],
            "neutral_reciprocal_formula": natural_units_neutral_shell["neutral_shell_dictionary"]["neutral_reciprocal_formula"],
            "q": natural_units_neutral_shell["neutral_shell_dictionary"]["q"],
            "theta_w33": natural_units_neutral_shell["neutral_shell_dictionary"]["theta_w33"],
            "phi3": natural_units_neutral_shell["neutral_shell_dictionary"]["phi3"],
            "sigma": natural_units_neutral_shell["neutral_shell_dictionary"]["sigma"],
            "q_squared": natural_units_neutral_shell["neutral_shell_dictionary"]["q_squared"],
            "rk_times_g0": natural_units_neutral_shell["neutral_shell_dictionary"]["rk_times_g0"],
            "phi6": natural_units_neutral_shell["neutral_shell_dictionary"]["phi6"],
            "ag21_length": natural_units_neutral_shell["neutral_shell_dictionary"]["ag21_length"],
            "neutral_numerator": natural_units_neutral_shell["neutral_shell_dictionary"]["neutral_numerator"],
            "neutral_reciprocal": natural_units_neutral_shell["neutral_shell_dictionary"]["neutral_reciprocal"]["exact"],
            "single_surface_flags": natural_units_neutral_shell["neutral_shell_dictionary"]["single_surface_flags"],
            "complement_trace": natural_units_neutral_shell["neutral_shell_dictionary"]["complement_trace"],
            "neutral_numerator_equals_q_times_theta": natural_units_neutral_shell["exact_factorizations"]["neutral_numerator_equals_q_times_theta"],
            "neutral_reciprocal_equals_q_theta_over_phi3_squared": natural_units_neutral_shell["exact_factorizations"]["neutral_reciprocal_equals_q_theta_over_phi3_squared"],
            "q_times_rk_times_g0_equals_sigma": natural_units_neutral_shell["exact_factorizations"]["q_times_rk_times_g0_equals_sigma"],
            "q_times_phi6_equals_ag21": natural_units_neutral_shell["exact_factorizations"]["q_times_phi6_equals_ag21"],
            "neutral_numerator_equals_q_plus_sigma_plus_ag21": natural_units_neutral_shell["exact_factorizations"]["neutral_numerator_equals_q_plus_sigma_plus_ag21"],
            "complement_trace_equals_sigma_times_q_squared": natural_units_neutral_shell["exact_factorizations"]["complement_trace_equals_sigma_times_q_squared"],
            "surface_flags_equals_complement_trace_plus_neutral_numerator": natural_units_neutral_shell["exact_factorizations"]["surface_flags_equals_complement_trace_plus_neutral_numerator"],
        },
        "natural_units_root_gap_bridge": {
            "quadratic_formula": natural_units_root_gap["root_gap_dictionary"]["quadratic_formula"],
            "sum_formula": natural_units_root_gap["root_gap_dictionary"]["sum_formula"],
            "product_formula": natural_units_root_gap["root_gap_dictionary"]["product_formula"],
            "discriminant_formula": natural_units_root_gap["root_gap_dictionary"]["discriminant_formula"],
            "gap_formula": natural_units_root_gap["root_gap_dictionary"]["gap_formula"],
            "weak_root_formula": natural_units_root_gap["root_gap_dictionary"]["weak_root_formula"],
            "hypercharge_root_formula": natural_units_root_gap["root_gap_dictionary"]["hypercharge_root_formula"],
            "q": natural_units_root_gap["root_gap_dictionary"]["q"],
            "theta_w33": natural_units_root_gap["root_gap_dictionary"]["theta_w33"],
            "phi3": natural_units_root_gap["root_gap_dictionary"]["phi3"],
            "phi6": natural_units_root_gap["root_gap_dictionary"]["phi6"],
            "weak_share": natural_units_root_gap["root_gap_dictionary"]["weak_share"]["exact"],
            "hypercharge_share": natural_units_root_gap["root_gap_dictionary"]["hypercharge_share"]["exact"],
            "neutral_product": natural_units_root_gap["root_gap_dictionary"]["neutral_product"]["exact"],
            "discriminant": natural_units_root_gap["root_gap_dictionary"]["discriminant"]["exact"],
            "root_gap": natural_units_root_gap["root_gap_dictionary"]["root_gap"]["exact"],
            "atmospheric_share": natural_units_root_gap["root_gap_dictionary"]["atmospheric_share"]["exact"],
            "weak_plus_hypercharge_equals_unity": natural_units_root_gap["exact_factorizations"]["weak_plus_hypercharge_equals_unity"],
            "weak_times_hypercharge_equals_neutral_product": natural_units_root_gap["exact_factorizations"]["weak_times_hypercharge_equals_neutral_product"],
            "discriminant_equals_phi6_squared_over_phi3_squared": natural_units_root_gap["exact_factorizations"]["discriminant_equals_phi6_squared_over_phi3_squared"],
            "root_gap_equals_phi6_over_phi3": natural_units_root_gap["exact_factorizations"]["root_gap_equals_phi6_over_phi3"],
            "root_gap_equals_atmospheric_share": natural_units_root_gap["exact_factorizations"]["root_gap_equals_atmospheric_share"],
            "weak_root_reconstructs_from_gap": natural_units_root_gap["exact_factorizations"]["weak_root_reconstructs_from_gap"],
            "hypercharge_root_reconstructs_from_gap": natural_units_root_gap["exact_factorizations"]["hypercharge_root_reconstructs_from_gap"],
            "weak_root_equals_q_over_phi3": natural_units_root_gap["exact_factorizations"]["weak_root_equals_q_over_phi3"],
            "hypercharge_root_equals_theta_over_phi3": natural_units_root_gap["exact_factorizations"]["hypercharge_root_equals_theta_over_phi3"],
            "heawood_denominator_matches_root_gap": natural_units_root_gap["exact_factorizations"]["heawood_denominator_matches_root_gap"],
        },
        "heawood_electroweak_polarization_bridge": {
            "operator_formula": heawood_electroweak_polarization["polarization_dictionary"]["operator_formula"],
            "projector_form_formula": heawood_electroweak_polarization["polarization_dictionary"]["projector_form_formula"],
            "centered_gap_formula": heawood_electroweak_polarization["polarization_dictionary"]["centered_gap_formula"],
            "quadratic_formula": heawood_electroweak_polarization["polarization_dictionary"]["quadratic_formula"],
            "reduced_packet_formula": heawood_electroweak_polarization["polarization_dictionary"]["reduced_packet_formula"],
            "q": heawood_electroweak_polarization["polarization_dictionary"]["q"],
            "theta_w33": heawood_electroweak_polarization["polarization_dictionary"]["theta_w33"],
            "phi3": heawood_electroweak_polarization["polarization_dictionary"]["phi3"],
            "phi6": heawood_electroweak_polarization["polarization_dictionary"]["phi6"],
            "middle_rank": heawood_electroweak_polarization["polarization_dictionary"]["middle_rank"],
            "complex_rank": heawood_electroweak_polarization["polarization_dictionary"]["complex_rank"],
            "weak_share": heawood_electroweak_polarization["polarization_dictionary"]["weak_share"]["exact"],
            "hypercharge_share": heawood_electroweak_polarization["polarization_dictionary"]["hypercharge_share"]["exact"],
            "neutral_product": heawood_electroweak_polarization["polarization_dictionary"]["neutral_product"]["exact"],
            "root_gap": heawood_electroweak_polarization["polarization_dictionary"]["root_gap"]["exact"],
            "polarization_amplitude": heawood_electroweak_polarization["polarization_dictionary"]["polarization_amplitude"]["exact"],
            "middle_trace": heawood_electroweak_polarization["polarization_dictionary"]["middle_trace"],
            "reduced_trace": heawood_electroweak_polarization["reduced_packet_dictionary"]["trace"]["exact"],
            "reduced_determinant": heawood_electroweak_polarization["reduced_packet_dictionary"]["determinant"]["exact"],
            "reduced_eigenvalue_minus": heawood_electroweak_polarization["reduced_packet_dictionary"]["eigenvalue_minus"]["exact"],
            "reduced_eigenvalue_plus": heawood_electroweak_polarization["reduced_packet_dictionary"]["eigenvalue_plus"]["exact"],
            "pi_plus_rank_is_6": heawood_electroweak_polarization["exact_factorizations"]["pi_plus_rank_is_6"],
            "pi_minus_rank_is_6": heawood_electroweak_polarization["exact_factorizations"]["pi_minus_rank_is_6"],
            "polarization_operator_has_expected_trace": heawood_electroweak_polarization["exact_factorizations"]["polarization_operator_has_expected_trace"],
            "average_trace_on_middle_shell_equals_half": heawood_electroweak_polarization["exact_factorizations"]["average_trace_on_middle_shell_equals_half"],
            "operator_equals_projector_plus_polarization_form": heawood_electroweak_polarization["exact_factorizations"]["operator_equals_projector_plus_polarization_form"],
            "centered_gap_is_atmospheric_selector": heawood_electroweak_polarization["exact_factorizations"]["centered_gap_is_atmospheric_selector"],
            "operator_satisfies_neutral_shell_quadratic": heawood_electroweak_polarization["exact_factorizations"]["operator_satisfies_neutral_shell_quadratic"],
            "reduced_packet_trace_is_one": heawood_electroweak_polarization["exact_factorizations"]["reduced_packet_trace_is_one"],
            "reduced_packet_determinant_is_neutral_product": heawood_electroweak_polarization["exact_factorizations"]["reduced_packet_determinant_is_neutral_product"],
            "reduced_packet_eigenvalues_match_weak_and_hypercharge": heawood_electroweak_polarization["exact_factorizations"]["reduced_packet_eigenvalues_match_weak_and_hypercharge"],
            "neutral_numerator_is_heawood_trace_minus_clifford_rank": heawood_electroweak_polarization["exact_factorizations"]["neutral_numerator_is_heawood_trace_minus_clifford_rank"],
            "clifford_packet_is_available": heawood_electroweak_polarization["exact_factorizations"]["clifford_packet_is_available"],
        },
        "natural_units_cosmological_complement_bridge": {
            "reduced_complement_formula": natural_units_cosmological_complement["cosmological_complement_dictionary"]["reduced_complement_formula"],
            "lifted_complement_formula": natural_units_cosmological_complement["cosmological_complement_dictionary"]["lifted_complement_formula"],
            "numerator_formula": natural_units_cosmological_complement["cosmological_complement_dictionary"]["numerator_formula"],
            "surface_formula": natural_units_cosmological_complement["cosmological_complement_dictionary"]["surface_formula"],
            "q": natural_units_cosmological_complement["cosmological_complement_dictionary"]["q"],
            "theta_w33": natural_units_cosmological_complement["cosmological_complement_dictionary"]["theta_w33"],
            "phi3": natural_units_cosmological_complement["cosmological_complement_dictionary"]["phi3"],
            "phi6": natural_units_cosmological_complement["cosmological_complement_dictionary"]["phi6"],
            "root_gap": natural_units_cosmological_complement["cosmological_complement_dictionary"]["root_gap"]["exact"],
            "cosmological_fraction": natural_units_cosmological_complement["cosmological_complement_dictionary"]["cosmological_fraction"]["exact"],
            "cosmological_numerator": natural_units_cosmological_complement["cosmological_complement_dictionary"]["cosmological_numerator"],
            "single_surface_flags": natural_units_cosmological_complement["cosmological_complement_dictionary"]["single_surface_flags"],
            "heawood_middle_trace": natural_units_cosmological_complement["cosmological_complement_dictionary"]["heawood_middle_trace"],
            "middle_rank": natural_units_cosmological_complement["cosmological_complement_dictionary"]["middle_rank"],
            "external_chain_density_limit": natural_units_cosmological_complement["cosmological_complement_dictionary"]["external_chain_density_limit"],
            "cosmological_numerator_equals_phi3_squared_minus_phi6_squared": natural_units_cosmological_complement["exact_factorizations"]["cosmological_numerator_equals_phi3_squared_minus_phi6_squared"],
            "cosmological_numerator_equals_4_q_theta": natural_units_cosmological_complement["exact_factorizations"]["cosmological_numerator_equals_4_q_theta"],
            "cosmological_fraction_equals_one_minus_gap_squared": natural_units_cosmological_complement["exact_factorizations"]["cosmological_fraction_equals_one_minus_gap_squared"],
            "reduced_complement_is_120_over_169_identity": natural_units_cosmological_complement["exact_factorizations"]["reduced_complement_is_120_over_169_identity"],
            "four_det_equals_cosmological_fraction": natural_units_cosmological_complement["exact_factorizations"]["four_det_equals_cosmological_fraction"],
            "surface_plus_middle_trace_equals_120": natural_units_cosmological_complement["exact_factorizations"]["surface_plus_middle_trace_equals_120"],
            "lifted_coefficient_matches_cosmological_fraction": natural_units_cosmological_complement["exact_factorizations"]["lifted_coefficient_matches_cosmological_fraction"],
            "lifted_average_trace_matches_cosmological_fraction": natural_units_cosmological_complement["exact_factorizations"]["lifted_average_trace_matches_cosmological_fraction"],
            "curved_bridge_uses_universal_120_mode": natural_units_cosmological_complement["exact_factorizations"]["curved_bridge_uses_universal_120_mode"],
        },
        "natural_units_unit_balance_bridge": {
            "reduced_balance_formula": natural_units_unit_balance["unit_balance_dictionary"]["reduced_balance_formula"],
            "lifted_balance_formula": natural_units_unit_balance["unit_balance_dictionary"]["lifted_balance_formula"],
            "mixed_product_formula": natural_units_unit_balance["unit_balance_dictionary"]["mixed_product_formula"],
            "fraction_formula": natural_units_unit_balance["unit_balance_dictionary"]["fraction_formula"],
            "numerator_formula": natural_units_unit_balance["unit_balance_dictionary"]["numerator_formula"],
            "shell_balance_formula": natural_units_unit_balance["unit_balance_dictionary"]["shell_balance_formula"],
            "shell_formula": natural_units_unit_balance["unit_balance_dictionary"]["shell_formula"],
            "phi3": natural_units_unit_balance["unit_balance_dictionary"]["phi3"],
            "phi6": natural_units_unit_balance["unit_balance_dictionary"]["phi6"],
            "denominator_square": natural_units_unit_balance["unit_balance_dictionary"]["denominator_square"],
            "polarization_fraction": natural_units_unit_balance["unit_balance_dictionary"]["polarization_fraction"]["exact"],
            "cosmological_fraction": natural_units_unit_balance["unit_balance_dictionary"]["cosmological_fraction"]["exact"],
            "polarization_numerator": natural_units_unit_balance["unit_balance_dictionary"]["polarization_numerator"],
            "cosmological_numerator": natural_units_unit_balance["unit_balance_dictionary"]["cosmological_numerator"],
            "single_surface_flags": natural_units_unit_balance["unit_balance_dictionary"]["single_surface_flags"],
            "heawood_middle_trace": natural_units_unit_balance["unit_balance_dictionary"]["heawood_middle_trace"],
            "toroidal_trace": natural_units_unit_balance["unit_balance_dictionary"]["toroidal_trace"],
            "qcd_selector": natural_units_unit_balance["unit_balance_dictionary"]["qcd_selector"],
            "reduced_balance_is_identity": natural_units_unit_balance["exact_factorizations"]["reduced_balance_is_identity"],
            "polarization_fraction_equals_gap_squared": natural_units_unit_balance["exact_factorizations"]["polarization_fraction_equals_gap_squared"],
            "cosmological_fraction_equals_four_det": natural_units_unit_balance["exact_factorizations"]["cosmological_fraction_equals_four_det"],
            "unit_splits_into_polarization_plus_complement": natural_units_unit_balance["exact_factorizations"]["unit_splits_into_polarization_plus_complement"],
            "denominator_square_equals_two_numerators": natural_units_unit_balance["exact_factorizations"]["denominator_square_equals_two_numerators"],
            "polarization_numerator_equals_toroidal_trace_plus_qcd_selector": natural_units_unit_balance["exact_factorizations"]["polarization_numerator_equals_toroidal_trace_plus_qcd_selector"],
            "cosmological_numerator_equals_surface_plus_heawood_trace": natural_units_unit_balance["exact_factorizations"]["cosmological_numerator_equals_surface_plus_heawood_trace"],
            "denominator_square_equals_surface_heawood_plus_polarization": natural_units_unit_balance["exact_factorizations"]["denominator_square_equals_surface_heawood_plus_polarization"],
            "denominator_square_equals_surface_heawood_toroidal_qcd_shells": natural_units_unit_balance["exact_factorizations"]["denominator_square_equals_surface_heawood_toroidal_qcd_shells"],
        },
        "electroweak_lagrangian_bridge": {
            "vev_ew_gev": electroweak_lagrangian["graph_inputs"]["vev_ew_gev"],
            "weinberg_x": electroweak_lagrangian["graph_inputs"]["weinberg_x"]["exact"],
            "cos2_theta_w": electroweak_lagrangian["graph_inputs"]["cos2_theta_w"]["exact"],
            "higgs_ratio_square": electroweak_lagrangian["graph_inputs"]["higgs_ratio_square"]["exact"],
            "lambda_h": electroweak_lagrangian["graph_inputs"]["lambda_h"]["exact"],
            "g_squared_over_4pi_alpha": electroweak_lagrangian["dimensionless_lagrangian_dictionary"]["g_squared_over_4pi_alpha"]["exact"],
            "gprime_squared_over_4pi_alpha": electroweak_lagrangian["dimensionless_lagrangian_dictionary"]["gprime_squared_over_4pi_alpha"]["exact"],
            "gz_squared_over_4pi_alpha": electroweak_lagrangian["dimensionless_lagrangian_dictionary"]["gz_squared_over_4pi_alpha"]["exact"],
            "one_over_e_squared_equals_sum": electroweak_lagrangian["dimensionless_lagrangian_dictionary"]["one_over_e_squared_equals_sum"],
            "g_squared_over_gprime_squared": electroweak_lagrangian["dimensionless_lagrangian_dictionary"]["g_squared_over_gprime_squared"]["exact"],
            "rho_parameter": electroweak_lagrangian["dimensionless_lagrangian_dictionary"]["rho_parameter"]["exact"],
            "mw_squared_over_mz_squared": electroweak_lagrangian["dimensionless_lagrangian_dictionary"]["mw_squared_over_mz_squared"]["exact"],
            "e": electroweak_lagrangian["natural_unit_couplings"]["e"]["scientific"],
            "g": electroweak_lagrangian["natural_unit_couplings"]["g"]["scientific"],
            "gprime": electroweak_lagrangian["natural_unit_couplings"]["gprime"]["scientific"],
            "gZ": electroweak_lagrangian["natural_unit_couplings"]["gZ"]["scientific"],
            "mw_tree_gev": electroweak_lagrangian["natural_unit_couplings"]["mw_tree_gev"]["scientific"],
            "mz_tree_gev": electroweak_lagrangian["natural_unit_couplings"]["mz_tree_gev"]["scientific"],
            "mh_tree_gev": electroweak_lagrangian["natural_unit_couplings"]["mh_tree_gev"]["scientific"],
            "fermi_constant_tree": electroweak_lagrangian["natural_unit_couplings"]["fermi_constant_tree"]["scientific"],
            "e_equals_g_sin_theta": electroweak_lagrangian["exact_tree_level_relations"]["e_equals_g_sin_theta"],
            "e_equals_gprime_cos_theta": electroweak_lagrangian["exact_tree_level_relations"]["e_equals_gprime_cos_theta"],
            "mz_equals_mw_over_cos_theta": electroweak_lagrangian["exact_tree_level_relations"]["mz_equals_mw_over_cos_theta"],
            "mh_equals_v_sqrt_2lambda": electroweak_lagrangian["exact_tree_level_relations"]["mh_equals_v_sqrt_2lambda"],
            "gf_equals_one_over_sqrt2_v2": electroweak_lagrangian["exact_tree_level_relations"]["gf_equals_one_over_sqrt2_v2"],
        },
        "one_scale_bosonic_bridge": {
            "vev_ew_gev": one_scale_bosonic["graph_fixed_inputs"]["vev_ew_gev"],
            "weinberg_x": one_scale_bosonic["graph_fixed_inputs"]["weinberg_x"]["exact"],
            "cos2_theta_w": one_scale_bosonic["graph_fixed_inputs"]["cos2_theta_w"]["exact"],
            "lambda_h": one_scale_bosonic["graph_fixed_inputs"]["lambda_h"]["exact"],
            "higgs_ratio_square": one_scale_bosonic["graph_fixed_inputs"]["higgs_ratio_square"]["exact"],
            "mu_h_squared_over_v_squared": one_scale_bosonic["higgs_potential_dictionary"]["mu_h_squared_over_v_squared"]["exact"],
            "mh_squared_over_v_squared": one_scale_bosonic["higgs_potential_dictionary"]["mh_squared_over_v_squared"]["exact"],
            "vacuum_energy_over_v_fourth": one_scale_bosonic["higgs_potential_dictionary"]["vacuum_energy_over_v_fourth"]["exact"],
            "mu_equals_lambda_v_squared": one_scale_bosonic["higgs_potential_dictionary"]["mu_equals_lambda_v_squared"],
            "mh_squared_equals_2lambda_v_squared": one_scale_bosonic["higgs_potential_dictionary"]["mh_squared_equals_2lambda_v_squared"],
            "vacuum_energy_equals_minus_lambda_v_fourth_over_4": one_scale_bosonic["higgs_potential_dictionary"]["vacuum_energy_equals_minus_lambda_v_fourth_over_4"],
            "mw_squared_over_mz_squared": one_scale_bosonic["normalized_tree_mass_dictionary"]["mw_squared_over_mz_squared"]["exact"],
            "z_minus_w_split_over_z": one_scale_bosonic["normalized_tree_mass_dictionary"]["z_minus_w_split_over_z"]["exact"],
            "rho_parameter": one_scale_bosonic["normalized_tree_mass_dictionary"]["rho_parameter"]["exact"],
            "mw_over_v": one_scale_bosonic["normalized_tree_mass_dictionary"]["mw_over_v"]["scientific"],
            "mz_over_v": one_scale_bosonic["normalized_tree_mass_dictionary"]["mz_over_v"]["scientific"],
            "mh_over_v": one_scale_bosonic["normalized_tree_mass_dictionary"]["mh_over_v"]["scientific"],
            "mw_over_mz_equals_sqrt_cos2": one_scale_bosonic["normalized_tree_mass_dictionary"]["mw_over_mz_equals_sqrt_cos2"],
            "mh_over_v_equals_sqrt_higgs_ratio": one_scale_bosonic["normalized_tree_mass_dictionary"]["mh_over_v_equals_sqrt_higgs_ratio"],
            "all_dimensionless_bosonic_data_fixed": one_scale_bosonic["one_scale_closure"]["all_dimensionless_bosonic_data_fixed"],
            "only_overall_scale_is_v": one_scale_bosonic["one_scale_closure"]["only_overall_scale_is_v"],
            "vev_is_graph_fixed_as_q5_plus_q": one_scale_bosonic["one_scale_closure"]["vev_is_graph_fixed_as_q5_plus_q"],
            "vev_is_graph_fixed_as_edges_plus_2q": one_scale_bosonic["one_scale_closure"]["vev_is_graph_fixed_as_edges_plus_2q"],
            "zero_extra_parameter_bosonic_closure_if_promoted_vev_accepted": one_scale_bosonic["one_scale_closure"]["zero_extra_parameter_bosonic_closure_if_promoted_vev_accepted"],
        },
        "bosonic_action_completion_bridge": {
            "lagrangian_formula": bosonic_action_completion["canonical_bosonic_action"]["lagrangian_formula"],
            "covariant_derivative_formula": bosonic_action_completion["canonical_bosonic_action"]["covariant_derivative_formula"],
            "potential_formula": bosonic_action_completion["canonical_bosonic_action"]["potential_formula"],
            "alpha": bosonic_action_completion["graph_fixed_inputs"]["alpha"]["exact"],
            "weinberg_x": bosonic_action_completion["graph_fixed_inputs"]["weinberg_x"]["exact"],
            "lambda_h": bosonic_action_completion["graph_fixed_inputs"]["lambda_h"]["exact"],
            "vev_ew_gev": bosonic_action_completion["graph_fixed_inputs"]["vev_ew_gev"],
            "g_squared_over_4pi_alpha": bosonic_action_completion["gauge_ratio_dictionary"]["g_squared_over_4pi_alpha"]["exact"],
            "gprime_squared_over_4pi_alpha": bosonic_action_completion["gauge_ratio_dictionary"]["gprime_squared_over_4pi_alpha"]["exact"],
            "gz_squared_over_4pi_alpha": bosonic_action_completion["gauge_ratio_dictionary"]["gz_squared_over_4pi_alpha"]["exact"],
            "g_squared_over_gprime_squared": bosonic_action_completion["gauge_ratio_dictionary"]["g_squared_over_gprime_squared"]["exact"],
            "mw_squared_over_mz_squared": bosonic_action_completion["gauge_ratio_dictionary"]["mw_squared_over_mz_squared"]["exact"],
            "rho_parameter": bosonic_action_completion["gauge_ratio_dictionary"]["rho_parameter"]["exact"],
            "mu_h_squared_over_v_squared": bosonic_action_completion["higgs_dictionary"]["mu_h_squared_over_v_squared"]["exact"],
            "mh_squared_over_v_squared": bosonic_action_completion["higgs_dictionary"]["mh_squared_over_v_squared"]["exact"],
            "vacuum_energy_over_v_fourth": bosonic_action_completion["higgs_dictionary"]["vacuum_energy_over_v_fourth"]["exact"],
            "canonical_gauge_kinetics_fixed": bosonic_action_completion["completion_claim"]["canonical_gauge_kinetics_fixed"],
            "covariant_derivative_fixed_by_alpha_and_x": bosonic_action_completion["completion_claim"]["covariant_derivative_fixed_by_alpha_and_x"],
            "higgs_potential_fixed_by_x_and_v": bosonic_action_completion["completion_claim"]["higgs_potential_fixed_by_x_and_v"],
            "no_free_bosonic_parameter_beyond_graph_fixed_alpha_x_v": bosonic_action_completion["completion_claim"]["no_free_bosonic_parameter_beyond_graph_fixed_alpha_x_v"],
            "graph_fixes_full_tree_level_bosonic_electroweak_action": bosonic_action_completion["completion_claim"]["graph_fixes_full_tree_level_bosonic_electroweak_action"],
        },
        "standard_model_action_backbone_bridge": {
            "alpha": standard_model_action_backbone["bosonic_action_backbone"]["alpha"]["exact"],
            "weinberg_x": standard_model_action_backbone["bosonic_action_backbone"]["weinberg_x"]["exact"],
            "lambda_h": standard_model_action_backbone["bosonic_action_backbone"]["lambda_h"]["exact"],
            "vev_ew_gev": standard_model_action_backbone["bosonic_action_backbone"]["vev_ew_gev"],
            "mw_squared_over_mz_squared": standard_model_action_backbone["bosonic_action_backbone"]["mw_squared_over_mz_squared"]["exact"],
            "rho_parameter": standard_model_action_backbone["bosonic_action_backbone"]["rho_parameter"]["exact"],
            "one_generation_spinor_dimension": standard_model_action_backbone["fermion_representation_backbone"]["one_generation_spinor_dimension"],
            "three_generation_matter_dimension": standard_model_action_backbone["fermion_representation_backbone"]["three_generation_matter_dimension"],
            "left_right_split": standard_model_action_backbone["fermion_representation_backbone"]["left_right_split"],
            "one_generation_counts": standard_model_action_backbone["fermion_representation_backbone"]["one_generation_counts"],
            "clean_higgs_slots": standard_model_action_backbone["fermion_representation_backbone"]["clean_higgs_slots"],
            "tan_theta_c": standard_model_action_backbone["mixing_backbone"]["tan_theta_c"]["exact"],
            "sin2_theta_12": standard_model_action_backbone["mixing_backbone"]["sin2_theta_12"]["exact"],
            "sin2_theta_23": standard_model_action_backbone["mixing_backbone"]["sin2_theta_23"]["exact"],
            "sin2_theta_13": standard_model_action_backbone["mixing_backbone"]["sin2_theta_13"]["exact"],
            "all_anomalies_cancel": standard_model_action_backbone["anomaly_backbone"]["all_anomalies_cancel"],
            "full_bosonic_action_fixed": standard_model_action_backbone["bosonic_action_backbone"]["full_bosonic_action_fixed"],
            "decomposition_16_equals_6_3_3_2_1_1": standard_model_action_backbone["fermion_representation_backbone"]["decomposition_16_equals_6_3_3_2_1_1"],
            "clean_higgs_pair_is_h2_hbar2": standard_model_action_backbone["fermion_representation_backbone"]["clean_higgs_pair_is_h2_hbar2"],
            "bosonic_action_complete": standard_model_action_backbone["frontier_boundary"]["bosonic_action_complete"],
            "fermion_representations_complete": standard_model_action_backbone["frontier_boundary"]["fermion_representations_complete"],
            "mixing_backbone_complete": standard_model_action_backbone["frontier_boundary"]["mixing_backbone_complete"],
            "anomaly_backbone_complete": standard_model_action_backbone["frontier_boundary"]["anomaly_backbone_complete"],
            "full_yukawa_eigenvalue_spectrum_still_open": standard_model_action_backbone["frontier_boundary"]["full_yukawa_eigenvalue_spectrum_still_open"],
        },
        "q3_fermion_hierarchy_bridge": {
            "alpha_inverse_exact": q3_fermion_hierarchy["electromagnetic_to_flavour_lock"]["alpha_inverse_exact"]["exact"],
            "alpha_tree_inverse": q3_fermion_hierarchy["electromagnetic_to_flavour_lock"]["alpha_tree_inverse"]["exact"],
            "gaussian_norm_mu_plus_i": q3_fermion_hierarchy["electromagnetic_to_flavour_lock"]["gaussian_norm_mu_plus_i"]["exact"],
            "up_sector_suppressor": q3_fermion_hierarchy["electromagnetic_to_flavour_lock"]["up_sector_suppressor"]["exact"],
            "alpha_tree_minus_one_equals_up_sector_suppressor": q3_fermion_hierarchy["electromagnetic_to_flavour_lock"]["alpha_tree_minus_one_equals_up_sector_suppressor"],
            "vertex_correction_term": q3_fermion_hierarchy["electromagnetic_to_flavour_lock"]["vertex_correction_term"]["exact"],
            "mc_over_mt": q3_fermion_hierarchy["dimensionless_hierarchy_ratios"]["mc_over_mt"]["exact"],
            "mu_over_mc": q3_fermion_hierarchy["dimensionless_hierarchy_ratios"]["mu_over_mc"]["exact"],
            "mb_over_mc": q3_fermion_hierarchy["dimensionless_hierarchy_ratios"]["mb_over_mc"]["exact"],
            "ms_over_mb": q3_fermion_hierarchy["dimensionless_hierarchy_ratios"]["ms_over_mb"]["exact"],
            "md_over_ms": q3_fermion_hierarchy["dimensionless_hierarchy_ratios"]["md_over_ms"]["exact"],
            "mmu_over_me": q3_fermion_hierarchy["dimensionless_hierarchy_ratios"]["mmu_over_me"]["exact"],
            "charm_suppressor_is_alpha_tree_minus_one": q3_fermion_hierarchy["fermion_hierarchy_theorem"]["charm_suppressor_is_alpha_tree_minus_one"],
            "bottom_ratio_is_projective_plane_over_line": q3_fermion_hierarchy["fermion_hierarchy_theorem"]["bottom_ratio_is_projective_plane_over_line"],
            "strange_ratio_is_inverse_nonbacktracking_degree_times_mu": q3_fermion_hierarchy["fermion_hierarchy_theorem"]["strange_ratio_is_inverse_nonbacktracking_degree_times_mu"],
            "down_ratio_is_lambda_over_v": q3_fermion_hierarchy["fermion_hierarchy_theorem"]["down_ratio_is_lambda_over_v"],
            "muon_ratio_is_phi3_mu_squared": q3_fermion_hierarchy["fermion_hierarchy_theorem"]["muon_ratio_is_phi3_mu_squared"],
        },
        "alpha_hierarchy_gaussian_bridge": {
            "outer_alpha_formula": alpha_hierarchy_gaussian["nested_gaussian_shells"]["outer_alpha_formula"],
            "outer_alpha_vector": alpha_hierarchy_gaussian["nested_gaussian_shells"]["outer_alpha_vector"],
            "outer_alpha_norm": alpha_hierarchy_gaussian["nested_gaussian_shells"]["outer_alpha_norm"]["exact"],
            "inner_hierarchy_formula": alpha_hierarchy_gaussian["nested_gaussian_shells"]["inner_hierarchy_formula"],
            "inner_hierarchy_vector": alpha_hierarchy_gaussian["nested_gaussian_shells"]["inner_hierarchy_vector"],
            "inner_hierarchy_norm": alpha_hierarchy_gaussian["nested_gaussian_shells"]["inner_hierarchy_norm"]["exact"],
            "transport_prefactor": alpha_hierarchy_gaussian["nested_gaussian_shells"]["transport_prefactor"]["exact"],
            "up_sector_suppressor": alpha_hierarchy_gaussian["nested_gaussian_shells"]["up_sector_suppressor"]["exact"],
            "selector_line_dimension": alpha_hierarchy_gaussian["selector_split"]["selector_line_dimension"]["exact"],
            "alpha_tree_equals_up_sector_plus_selector": alpha_hierarchy_gaussian["selector_split"]["alpha_tree_equals_up_sector_plus_selector"],
            "vertex_correction_term": alpha_hierarchy_gaussian["selector_split"]["vertex_correction_term"]["exact"],
            "alpha_full_equals_nested_shell_plus_vertex_correction": alpha_hierarchy_gaussian["selector_split"]["alpha_full_equals_nested_shell_plus_vertex_correction"],
            "mc_over_mt": alpha_hierarchy_gaussian["hierarchy_lock"]["mc_over_mt"]["exact"],
            "mu_over_mc": alpha_hierarchy_gaussian["hierarchy_lock"]["mu_over_mc"]["exact"],
            "charm_ratio_is_inverse_selector_reduced_tree_alpha": alpha_hierarchy_gaussian["hierarchy_lock"]["charm_ratio_is_inverse_selector_reduced_tree_alpha"],
            "second_up_step_is_extra_mu_factor": alpha_hierarchy_gaussian["hierarchy_lock"]["second_up_step_is_extra_mu_factor"],
        },
        "qcd_beta_phi6_bridge": {
            "beta0_formula": qcd_beta_phi6["qcd_beta_dictionary"]["beta0_formula"],
            "beta0_su3": qcd_beta_phi6["qcd_beta_dictionary"]["beta0_su3"]["exact"],
            "phi6_formula": qcd_beta_phi6["qcd_beta_dictionary"]["phi6_formula"],
            "phi6_q3": qcd_beta_phi6["qcd_beta_dictionary"]["phi6_q3"]["exact"],
            "pmns_atmospheric_ratio": qcd_beta_phi6["qcd_beta_dictionary"]["pmns_atmospheric_ratio"]["exact"],
            "higgs_quartic": qcd_beta_phi6["qcd_beta_dictionary"]["higgs_quartic"]["exact"],
            "topological_over_continuum_ratio": qcd_beta_phi6["qcd_beta_dictionary"]["topological_over_continuum_ratio"]["exact"],
            "beta0_equals_phi6": qcd_beta_phi6["selector_bridge"]["beta0_equals_phi6"],
            "positive_integer_solution_of_phi6_equals_7": qcd_beta_phi6["selector_bridge"]["positive_integer_solution_of_phi6_equals_7"],
        },
        "jones_mu4_selector_bridge": {
            "jones_value_set": jones_mu4_selector["jones_dictionary"]["jones_value_set"],
            "critical_boundary": jones_mu4_selector["jones_dictionary"]["critical_boundary"]["exact"],
            "mu": jones_mu4_selector["jones_dictionary"]["mu"]["exact"],
            "spectral_gap": jones_mu4_selector["jones_dictionary"]["spectral_gap"]["exact"],
            "external_dimension": jones_mu4_selector["jones_dictionary"]["external_dimension"]["exact"],
            "mu_equals_q_plus_one": jones_mu4_selector["selector_bridge"]["mu_equals_q_plus_one"],
            "mu_hits_jones_boundary": jones_mu4_selector["selector_bridge"]["mu_hits_jones_boundary"],
            "mu_equals_spectral_gap": jones_mu4_selector["selector_bridge"]["mu_equals_spectral_gap"],
            "mu_equals_external_dimension": jones_mu4_selector["selector_bridge"]["mu_equals_external_dimension"],
            "positive_integer_solution_of_q_plus_one_equals_4": jones_mu4_selector["selector_bridge"]["positive_integer_solution_of_q_plus_one_equals_4"],
        },
        "f4_neutrino_scale_bridge": {
            "f4_dimension": f4_neutrino_scale["exceptional_scale_dictionary"]["f4_dimension"],
            "vev_ew_gev": f4_neutrino_scale["exceptional_scale_dictionary"]["vev_ew_gev"],
            "mr_over_vew": f4_neutrino_scale["exceptional_scale_dictionary"]["mr_over_vew"]["exact"],
            "mnu_over_me_squared_if_dirac_seed_is_electron": f4_neutrino_scale["exceptional_scale_dictionary"]["mnu_over_me_squared_if_dirac_seed_is_electron"]["exact"],
            "f4_dimension_equals_phi3_times_mu": f4_neutrino_scale["exceptional_scale_theorem"]["f4_dimension_equals_phi3_times_mu"],
            "f4_dimension_equals_v_plus_k": f4_neutrino_scale["exceptional_scale_theorem"]["f4_dimension_equals_v_plus_k"],
            "majorana_scale_is_inverse_f4_dimension": f4_neutrino_scale["exceptional_scale_theorem"]["majorana_scale_is_inverse_f4_dimension"],
            "seesaw_coefficient_is_exact_f4_over_vew": f4_neutrino_scale["exceptional_scale_theorem"]["seesaw_coefficient_is_exact_f4_over_vew"],
            "seesaw_coefficient_reduces_to_26_over_123": f4_neutrino_scale["exceptional_scale_theorem"]["seesaw_coefficient_reduces_to_26_over_123"],
        },
        "one_input_fermion_spectrum_bridge": {
            "vev_ew_gev": one_input_fermion_spectrum["graph_fixed_seed"]["vev_ew_gev"],
            "mt_over_vew": one_input_fermion_spectrum["graph_fixed_seed"]["mt_over_vew"]["exact"],
            "mc_over_vew": one_input_fermion_spectrum["graph_fixed_seed"]["mc_over_vew"]["exact"],
            "mu_over_vew": one_input_fermion_spectrum["graph_fixed_seed"]["mu_over_vew"]["exact"],
            "mb_over_vew": one_input_fermion_spectrum["graph_fixed_seed"]["mb_over_vew"]["exact"],
            "ms_over_vew": one_input_fermion_spectrum["graph_fixed_seed"]["ms_over_vew"]["exact"],
            "md_over_vew": one_input_fermion_spectrum["graph_fixed_seed"]["md_over_vew"]["exact"],
            "mu_over_mt": one_input_fermion_spectrum["dimensionless_fermion_ladder"]["mu_over_mt"]["exact"],
            "residual_seed": one_input_fermion_spectrum["charged_lepton_one_seed_closure"]["residual_seed"],
            "mmu_over_me": one_input_fermion_spectrum["charged_lepton_one_seed_closure"]["mmu_over_me"]["exact"],
            "koide_q": one_input_fermion_spectrum["charged_lepton_one_seed_closure"]["koide_q"]["exact"],
            "sqrt_mtau_over_me": one_input_fermion_spectrum["charged_lepton_one_seed_closure"]["sqrt_mtau_over_me"]["exact"],
            "mtau_over_me_minpoly": one_input_fermion_spectrum["charged_lepton_one_seed_closure"]["mtau_over_me_minpoly"],
            "mnu_over_me_squared_if_dirac_seed_is_electron": one_input_fermion_spectrum["exceptional_neutrino_closure"]["mnu_over_me_squared_if_dirac_seed_is_electron"]["exact"],
            "quark_ladder_fixed_by_graph_scale_and_q3_ratios": one_input_fermion_spectrum["fermion_spectrum_theorem"]["quark_ladder_fixed_by_graph_scale_and_q3_ratios"],
            "charged_lepton_ladder_reduced_to_one_electron_seed": one_input_fermion_spectrum["fermion_spectrum_theorem"]["charged_lepton_ladder_reduced_to_one_electron_seed"],
            "koide_packet_closes_tau_over_e_algebraically": one_input_fermion_spectrum["fermion_spectrum_theorem"]["koide_packet_closes_tau_over_e_algebraically"],
            "neutrino_scale_reduced_to_same_electron_seed_plus_f4_coefficient": one_input_fermion_spectrum["fermion_spectrum_theorem"]["neutrino_scale_reduced_to_same_electron_seed_plus_f4_coefficient"],
            "remaining_fermion_frontier_is_one_seed_plus_final_internal_spectral_packet": one_input_fermion_spectrum["fermion_spectrum_theorem"]["remaining_fermion_frontier_is_one_seed_plus_final_internal_spectral_packet"],
        },
        "l3_pfaffian_packet_bridge": {
            "support_count": l3_pfaffian_packet["l3_tensor_dictionary"]["support_count"],
            "plus_count": l3_pfaffian_packet["l3_tensor_dictionary"]["plus_count"],
            "minus_count": l3_pfaffian_packet["l3_tensor_dictionary"]["minus_count"],
            "balanced_signs": l3_pfaffian_packet["l3_tensor_dictionary"]["balanced_signs"],
            "all_supported_entries_are_antisymmetric": l3_pfaffian_packet["l3_tensor_dictionary"]["all_supported_entries_are_antisymmetric"],
            "vector_vev_count": l3_pfaffian_packet["l3_tensor_dictionary"]["vector_vev_count"],
            "all_vector_packets_have_determinant_plus_one": l3_pfaffian_packet["skew_packet_dictionary"]["all_vector_packets_have_determinant_plus_one"],
            "all_vector_packets_have_full_skew_rank": l3_pfaffian_packet["skew_packet_dictionary"]["all_vector_packets_have_full_skew_rank"],
            "type_a_directions": l3_pfaffian_packet["spectral_archetypes"]["type_a"]["i27_directions"],
            "type_a_charpoly": l3_pfaffian_packet["spectral_archetypes"]["type_a"]["characteristic_polynomial"],
            "type_b_directions": l3_pfaffian_packet["spectral_archetypes"]["type_b"]["i27_directions"],
            "type_b_charpoly": l3_pfaffian_packet["spectral_archetypes"]["type_b"]["characteristic_polynomial"],
            "democratic_directions": l3_pfaffian_packet["higgs_packet_bridge"]["democratic_directions"],
            "democratic_labels": l3_pfaffian_packet["higgs_packet_bridge"]["democratic_labels"],
            "democratic_characteristic_polynomial": l3_pfaffian_packet["higgs_packet_bridge"]["democratic_characteristic_polynomial"],
            "democratic_packet_is_exactly_higgs_higgsbar": l3_pfaffian_packet["higgs_packet_bridge"]["democratic_packet_is_exactly_higgs_higgsbar"],
            "remaining_direction_labels": l3_pfaffian_packet["higgs_packet_bridge"]["remaining_direction_labels"],
        },
        "selector_firewall_bridge": {
            "identity": selector_firewall["master_equation"]["identity"],
            "srg_parameters": selector_firewall["master_equation"]["srg_parameters"],
            "identity_holds_for_canonical_w33": selector_firewall["master_equation"]["identity_holds_for_canonical_w33"],
            "classification_count_for_srg_40_12_2_4": selector_firewall["master_equation"]["classification_count_for_srg_40_12_2_4"],
            "master_equation_alone_does_not_force_unique_graph": selector_firewall["master_equation"]["master_equation_alone_does_not_force_unique_graph"],
            "canonical_realization": selector_firewall["selector_package"]["canonical_realization"],
            "gf3_rank_of_adjacency": selector_firewall["selector_package"]["gf3_rank_of_adjacency"],
            "gf3_rank_selector_matches_v_minus_1": selector_firewall["selector_package"]["gf3_rank_selector_matches_v_minus_1"],
            "all_neighborhoods_decompose_as_4K3": selector_firewall["selector_package"]["all_neighborhoods_decompose_as_4K3"],
            "neighborhood_component_sizes": selector_firewall["selector_package"]["neighborhood_component_sizes"],
            "symplectic_group_order": selector_firewall["selector_package"]["symplectic_group_order"],
        },
        "theta_hierarchy_bridge": {
            "lovasz_theta": theta_hierarchy["theta_dictionary"]["lovasz_theta"],
            "theta_complement": theta_hierarchy["theta_dictionary"]["theta_complement"],
            "theta_times_theta_complement": theta_hierarchy["theta_dictionary"]["theta_times_theta_complement"],
            "theta_times_theta_complement_equals_v": theta_hierarchy["theta_dictionary"]["theta_times_theta_complement_equals_v"],
            "small_selector_formula": theta_hierarchy["hierarchy_selector"]["small_selector_formula"],
            "small_selector": theta_hierarchy["hierarchy_selector"]["small_selector"],
            "mu_over_v": theta_hierarchy["hierarchy_selector"]["mu_over_v"],
            "selector_matches_mu_over_v": theta_hierarchy["hierarchy_selector"]["selector_matches_mu_over_v"],
            "selector_times_theta_is_unity": theta_hierarchy["hierarchy_selector"]["selector_times_theta_is_unity"],
            "betti_numbers": theta_hierarchy["truncated_shell_lock"]["betti_numbers"],
            "zero_mode_count": theta_hierarchy["truncated_shell_lock"]["zero_mode_count"],
            "zero_mode_formula": theta_hierarchy["truncated_shell_lock"]["zero_mode_formula"],
            "zero_mode_formula_value": theta_hierarchy["truncated_shell_lock"]["zero_mode_formula_value"],
            "betti_sum_equals_formula": theta_hierarchy["truncated_shell_lock"]["betti_sum_equals_formula"],
        },
        "truncated_dirac_shell_bridge": {
            "chain_dimensions": truncated_dirac_shell["truncated_sector"]["chain_dimensions"],
            "total_dimension": truncated_dirac_shell["truncated_sector"]["total_dimension"],
            "boundary_ranks": truncated_dirac_shell["truncated_sector"]["boundary_ranks"],
            "betti_numbers": truncated_dirac_shell["truncated_sector"]["betti_numbers"],
            "zero_mode_count": truncated_dirac_shell["truncated_sector"]["zero_mode_count"],
            "lovasz_theta": truncated_dirac_shell["truncated_sector"]["lovasz_theta"],
            "zero_mode_formula": truncated_dirac_shell["truncated_sector"]["zero_mode_formula"],
            "zero_mode_formula_value": truncated_dirac_shell["truncated_sector"]["zero_mode_formula_value"],
            "zero_modes_equal_graph_formula": truncated_dirac_shell["truncated_sector"]["zero_modes_equal_graph_formula"],
            "d2_spectrum": truncated_dirac_shell["spectral_shell"]["d2_spectrum"],
            "f0": truncated_dirac_shell["spectral_shell"]["f0"],
            "f2": truncated_dirac_shell["spectral_shell"]["f2"],
            "f4": truncated_dirac_shell["spectral_shell"]["f4"],
            "f6": truncated_dirac_shell["spectral_shell"]["f6"],
            "f2_over_f0": truncated_dirac_shell["spectral_shell"]["f2_over_f0"],
            "f4_over_f2": truncated_dirac_shell["spectral_shell"]["f4_over_f2"],
            "f6_over_f4": truncated_dirac_shell["spectral_shell"]["f6_over_f4"],
            "f2_over_f0_formula": truncated_dirac_shell["spectral_shell"]["f2_over_f0_formula"],
            "f4_over_f2_formula": truncated_dirac_shell["spectral_shell"]["f4_over_f2_formula"],
            "f2_over_f0_matches_formula": truncated_dirac_shell["spectral_shell"]["f2_over_f0_matches_formula"],
            "f4_over_f2_matches_formula": truncated_dirac_shell["spectral_shell"]["f4_over_f2_matches_formula"],
            "f2_equals_k_times_triangle_count": truncated_dirac_shell["spectral_shell"]["f2_equals_k_times_triangle_count"],
        },
        "yukawa_scaffold_bridge": {
            "clean_higgs_slots": yukawa_scaffold["sm_backbone_anchor"]["clean_higgs_slots"],
            "clean_higgs_pair_is_h2_hbar2": yukawa_scaffold["sm_backbone_anchor"]["clean_higgs_pair_is_h2_hbar2"],
            "one_generation_spinor_dimension": yukawa_scaffold["sm_backbone_anchor"]["one_generation_spinor_dimension"],
            "three_generation_matter_dimension": yukawa_scaffold["sm_backbone_anchor"]["three_generation_matter_dimension"],
            "label_matrix": yukawa_scaffold["canonical_texture"]["label_matrix"],
            "label_matrix_is_slot_independent": yukawa_scaffold["canonical_texture"]["label_matrix_is_slot_independent"],
            "reconstructs_exactly_for_both_slots": yukawa_scaffold["canonical_texture"]["reconstructs_exactly_for_both_slots"],
            "generation_0_diagonal_delta_equals_offdiag_1_to_0": yukawa_scaffold["canonical_texture"]["generation_0_diagonal_delta_equals_offdiag_1_to_0"],
            "generation_1_diagonal_delta_equals_offdiag_0_to_1": yukawa_scaffold["canonical_texture"]["generation_1_diagonal_delta_equals_offdiag_0_to_1"],
            "generation_2_diagonal_block_unchanged": yukawa_scaffold["canonical_texture"]["generation_2_diagonal_block_unchanged"],
            "h2_split": yukawa_scaffold["v4_projector_scaffold"]["h2_split"],
            "hbar2_split": yukawa_scaffold["v4_projector_scaffold"]["hbar2_split"],
            "minimal_full_a2_activation_seed_modes": yukawa_scaffold["a2_activation_scaffold"]["minimal_full_a2_activation_seed_modes"],
            "minimal_rank_lift_seed_modes": yukawa_scaffold["a2_activation_scaffold"]["minimal_rank_lift_seed_modes"],
            "max_response_rank_within_unit_seed_family": yukawa_scaffold["a2_activation_scaffold"]["max_response_rank_within_unit_seed_family"],
            "max_augmented_rank_within_unit_seed_family": yukawa_scaffold["a2_activation_scaffold"]["max_augmented_rank_within_unit_seed_family"],
            "generated_source_unit_count": yukawa_scaffold["ce2_boundary"]["generated_source_unit_count"],
            "projected_mode_count": yukawa_scaffold["ce2_boundary"]["projected_mode_count"],
            "response_rank": yukawa_scaffold["ce2_boundary"]["response_rank"],
            "augmented_rank": yukawa_scaffold["ce2_boundary"]["augmented_rank"],
            "arbitrary_quark_screen_rank": yukawa_scaffold["ce2_boundary"]["arbitrary_quark_screen_rank"],
            "arbitrary_quark_screen_nullity": yukawa_scaffold["ce2_boundary"]["arbitrary_quark_screen_nullity"],
            "trivial_closure_total_residual_norm": yukawa_scaffold["ce2_boundary"]["trivial_closure_total_residual_norm"],
            "zero_is_unique_clean_point": yukawa_scaffold["ce2_boundary"]["zero_is_unique_clean_point"],
            "l4_response_contained_in_ce2": yukawa_scaffold["ce2_boundary"]["l4_response_contained_in_ce2"],
            "yukawa_scaffold_is_exact": yukawa_scaffold["frontier_boundary"]["yukawa_scaffold_is_exact"],
            "nonzero_yukawa_eigenvalues_still_open": yukawa_scaffold["frontier_boundary"]["nonzero_yukawa_eigenvalues_still_open"],
            "exact_open_problem_is_spectrum_not_support_or_symmetry": yukawa_scaffold["frontier_boundary"]["exact_open_problem_is_spectrum_not_support_or_symmetry"],
        },
        "yukawa_unipotent_reduction_bridge": {
            "h2_plus_minus_support": yukawa_unipotent_reduction["slot_profiles"]["H_2"]["+-"]["support_labels"],
            "h2_minus_plus_support": yukawa_unipotent_reduction["slot_profiles"]["H_2"]["-+"]["support_labels"],
            "hbar2_plus_minus_support": yukawa_unipotent_reduction["slot_profiles"]["Hbar_2"]["+-"]["support_labels"],
            "hbar2_minus_plus_support": yukawa_unipotent_reduction["slot_profiles"]["Hbar_2"]["-+"]["support_labels"],
            "h2_plus_minus_compressed_rank": yukawa_unipotent_reduction["slot_profiles"]["H_2"]["+-"]["compressed_rank"],
            "h2_minus_plus_compressed_rank": yukawa_unipotent_reduction["slot_profiles"]["H_2"]["-+"]["compressed_rank"],
            "hbar2_plus_minus_compressed_rank": yukawa_unipotent_reduction["slot_profiles"]["Hbar_2"]["+-"]["compressed_rank"],
            "hbar2_minus_plus_compressed_rank": yukawa_unipotent_reduction["slot_profiles"]["Hbar_2"]["-+"]["compressed_rank"],
            "all_active_sector_block_spans_have_rank_2": all(
                yukawa_unipotent_reduction["slot_profiles"][slot][sector]["block_span_rank"] == 2
                for slot in ("H_2", "Hbar_2")
                for sector in ("+-", "-+")
            ),
            "all_active_sector_ranks_saturate_three_generation_support": all(
                yukawa_unipotent_reduction["slot_profiles"][slot][sector]["compressed_rank_saturates_three_generation_support"]
                for slot in ("H_2", "Hbar_2")
                for sector in ("+-", "-+")
            ),
            "plus_minus_generation_matrix": yukawa_unipotent_reduction["universal_generation_algebra"]["plus_minus_generation_matrix"],
            "minus_plus_generation_matrix": yukawa_unipotent_reduction["universal_generation_algebra"]["minus_plus_generation_matrix"],
            "plus_minus_charpoly": yukawa_unipotent_reduction["universal_generation_algebra"]["plus_minus_charpoly"],
            "minus_plus_charpoly": yukawa_unipotent_reduction["universal_generation_algebra"]["minus_plus_charpoly"],
            "plus_minus_is_unipotent_jordan_type": yukawa_unipotent_reduction["universal_generation_algebra"]["plus_minus_is_unipotent_jordan_type"],
            "minus_plus_is_unipotent_jordan_type": yukawa_unipotent_reduction["universal_generation_algebra"]["minus_plus_is_unipotent_jordan_type"],
            "nilpotent_squares_match_exactly": yukawa_unipotent_reduction["universal_generation_algebra"]["nilpotent_squares_match_exactly"],
            "common_nilpotent_square": yukawa_unipotent_reduction["universal_generation_algebra"]["common_nilpotent_square"],
            "generation_matrices_commute_exactly": yukawa_unipotent_reduction["universal_generation_algebra"]["generation_matrices_commute_exactly"],
            "slot_independent_plus_minus_matrix": yukawa_unipotent_reduction["universal_generation_algebra"]["slot_independent_plus_minus_matrix"],
            "slot_independent_minus_plus_matrix": yukawa_unipotent_reduction["universal_generation_algebra"]["slot_independent_minus_plus_matrix"],
        },
        "yukawa_kronecker_reduction_bridge": {
            "plus_minus_matrix": yukawa_kronecker_reduction["generation_algebra"]["plus_minus_matrix"],
            "minus_plus_matrix": yukawa_kronecker_reduction["generation_algebra"]["minus_plus_matrix"],
            "conjugating_matrix": yukawa_kronecker_reduction["generation_algebra"]["conjugating_matrix"],
            "conjugating_matrix_determinant": yukawa_kronecker_reduction["generation_algebra"]["conjugating_matrix_determinant"],
            "exact_integer_conjugacy_between_generation_matrices": yukawa_kronecker_reduction["generation_algebra"]["exact_integer_conjugacy_between_generation_matrices"],
            "plus_minus_charpoly": yukawa_kronecker_reduction["generation_algebra"]["plus_minus_charpoly"],
            "minus_plus_charpoly": yukawa_kronecker_reduction["generation_algebra"]["minus_plus_charpoly"],
            "common_jordan_form": yukawa_kronecker_reduction["generation_algebra"]["common_jordan_form"],
            "all_active_sectors_have_exact_kronecker_form": yukawa_kronecker_reduction["kronecker_reduction_theorem"]["all_active_sectors_have_exact_kronecker_form"],
            "all_active_sectors_have_exact_reduced_gram_formula": yukawa_kronecker_reduction["kronecker_reduction_theorem"]["all_active_sectors_have_exact_reduced_gram_formula"],
            "all_active_sector_singular_spectra_match_reduced_gram_exactly": yukawa_kronecker_reduction["kronecker_reduction_theorem"]["all_active_sector_singular_spectra_match_reduced_gram_exactly"],
            "template_ranks_match_active_sector_widths": yukawa_kronecker_reduction["kronecker_reduction_theorem"]["template_ranks_match_active_sector_widths"],
            "h2_plus_minus_sector_width": yukawa_kronecker_reduction["slot_profiles"]["H_2"]["+-"]["sector_width"],
            "h2_minus_plus_sector_width": yukawa_kronecker_reduction["slot_profiles"]["H_2"]["-+"]["sector_width"],
            "hbar2_plus_minus_sector_width": yukawa_kronecker_reduction["slot_profiles"]["Hbar_2"]["+-"]["sector_width"],
            "hbar2_minus_plus_sector_width": yukawa_kronecker_reduction["slot_profiles"]["Hbar_2"]["-+"]["sector_width"],
        },
        "yukawa_gram_shell_bridge": {
            "root_denominator": yukawa_gram_shell["root_denominator"],
            "gram_denominator": yukawa_gram_shell["gram_denominator"],
            "all_template_grams_scale_exactly_to_integer_shell": yukawa_gram_shell["gram_shell_theorem"]["all_template_grams_scale_exactly_to_integer_shell"],
            "plus_minus_slots_share_exact_phi3_mode_13_over_240": yukawa_gram_shell["gram_shell_theorem"]["plus_minus_slots_share_exact_phi3_mode_13_over_240"],
            "h2_plus_minus_base_gram_numerator": yukawa_gram_shell["gram_shell_theorem"]["h2_plus_minus_base_gram_numerator"],
            "h2_minus_plus_base_gram_numerator": yukawa_gram_shell["gram_shell_theorem"]["h2_minus_plus_base_gram_numerator"],
            "hbar2_plus_minus_base_gram_numerator": yukawa_gram_shell["gram_shell_theorem"]["hbar2_plus_minus_base_gram_numerator"],
            "hbar2_minus_plus_base_gram_numerator": yukawa_gram_shell["gram_shell_theorem"]["hbar2_minus_plus_base_gram_numerator"],
            "residual_frontier_is_two_integer_2x2_blocks_plus_exact_scalar_channels": yukawa_gram_shell["gram_shell_theorem"]["residual_frontier_is_two_integer_2x2_blocks_plus_exact_scalar_channels"],
            "h2_minus_plus_residual_block_numerator": yukawa_gram_shell["gram_shell_theorem"]["h2_minus_plus_residual_block_numerator"],
            "hbar2_plus_minus_residual_block_numerator": yukawa_gram_shell["gram_shell_theorem"]["hbar2_plus_minus_residual_block_numerator"],
            "exact_scalar_channel_numerators": yukawa_gram_shell["gram_shell_theorem"]["exact_scalar_channel_numerators"],
            "h2_plus_minus_contains_exact_phi3_mode": yukawa_gram_shell["slot_profiles"]["H_2"]["+-"]["contains_exact_phi3_mode_13_over_240"],
            "h2_minus_plus_contains_exact_phi3_mode": yukawa_gram_shell["slot_profiles"]["H_2"]["-+"]["contains_exact_phi3_mode_13_over_240"],
            "hbar2_plus_minus_contains_exact_phi3_mode": yukawa_gram_shell["slot_profiles"]["Hbar_2"]["+-"]["contains_exact_phi3_mode_13_over_240"],
            "hbar2_minus_plus_contains_exact_phi3_mode": yukawa_gram_shell["slot_profiles"]["Hbar_2"]["-+"]["contains_exact_phi3_mode_13_over_240"],
        },
        "yukawa_base_spectrum_bridge": {
            "gram_denominator": yukawa_base_spectrum["gram_denominator"],
            "h2_plus_minus_squared_spectrum": yukawa_base_spectrum["base_squared_spectra"]["h2_plus_minus"],
            "h2_minus_plus_squared_spectrum": yukawa_base_spectrum["base_squared_spectra"]["h2_minus_plus"],
            "hbar2_plus_minus_squared_spectrum": yukawa_base_spectrum["base_squared_spectra"]["hbar2_plus_minus"],
            "hbar2_minus_plus_squared_spectrum": yukawa_base_spectrum["base_squared_spectra"]["hbar2_minus_plus"],
            "shared_phi3_scalar_channel": yukawa_base_spectrum["radical_packet_dictionary"]["shared_phi3_scalar_channel"],
            "h2_plus_minus_companion_scalar_channel": yukawa_base_spectrum["radical_packet_dictionary"]["h2_plus_minus_companion_scalar_channel"],
            "hbar2_minus_plus_scalar_channel": yukawa_base_spectrum["radical_packet_dictionary"]["hbar2_minus_plus_scalar_channel"],
            "h2_minus_plus_radical_pair": yukawa_base_spectrum["radical_packet_dictionary"]["h2_minus_plus_radical_pair"],
            "hbar2_plus_minus_radical_pair": yukawa_base_spectrum["radical_packet_dictionary"]["hbar2_plus_minus_radical_pair"],
            "all_base_squared_spectra_are_exact_algebraic_numbers_on_240_shell": yukawa_base_spectrum["base_spectrum_theorem"]["all_base_squared_spectra_are_exact_algebraic_numbers_on_240_shell"],
            "residual_base_frontier_is_two_radical_pairs_plus_exact_scalar_channels": yukawa_base_spectrum["base_spectrum_theorem"]["residual_base_frontier_is_two_radical_pairs_plus_exact_scalar_channels"],
            "h2_minus_plus_block_trace": yukawa_base_spectrum["base_spectrum_theorem"]["h2_minus_plus_block_trace"],
            "h2_minus_plus_block_determinant": yukawa_base_spectrum["base_spectrum_theorem"]["h2_minus_plus_block_determinant"],
            "hbar2_plus_minus_block_trace": yukawa_base_spectrum["base_spectrum_theorem"]["hbar2_plus_minus_block_trace"],
            "hbar2_plus_minus_block_determinant": yukawa_base_spectrum["base_spectrum_theorem"]["hbar2_plus_minus_block_determinant"],
        },
        "yukawa_active_spectrum_bridge": {
            "gram_denominator": yukawa_active_spectrum["gram_denominator"],
            "scaled_variable": yukawa_active_spectrum["scaled_variable"],
            "h2_plus_minus_factors": yukawa_active_spectrum["slot_factorizations"]["H_2"]["+-"],
            "h2_minus_plus_factors": yukawa_active_spectrum["slot_factorizations"]["H_2"]["-+"],
            "hbar2_plus_minus_factors": yukawa_active_spectrum["slot_factorizations"]["Hbar_2"]["+-"],
            "hbar2_minus_plus_factors": yukawa_active_spectrum["slot_factorizations"]["Hbar_2"]["-+"],
            "all_active_sector_scaled_spectra_factor_over_z": yukawa_active_spectrum["active_spectrum_theorem"]["all_active_sector_scaled_spectra_factor_over_z"],
            "max_factor_degree": yukawa_active_spectrum["active_spectrum_theorem"]["max_factor_degree"],
            "h2_plus_minus_contains_exact_base_scalar_packet": yukawa_active_spectrum["active_spectrum_theorem"]["h2_plus_minus_contains_exact_base_scalar_packet"],
            "h2_minus_plus_contains_exact_base_quadratic_packet": yukawa_active_spectrum["active_spectrum_theorem"]["h2_minus_plus_contains_exact_base_quadratic_packet"],
            "hbar2_plus_minus_contains_exact_base_packet": yukawa_active_spectrum["active_spectrum_theorem"]["hbar2_plus_minus_contains_exact_base_packet"],
            "hbar2_minus_plus_contains_exact_base_scalar_packet": yukawa_active_spectrum["active_spectrum_theorem"]["hbar2_minus_plus_contains_exact_base_scalar_packet"],
            "remaining_full_active_frontier_is_finite_algebraic_packet": yukawa_active_spectrum["active_spectrum_theorem"]["remaining_full_active_frontier_is_finite_algebraic_packet"],
        },
        "monster_landauer_ternary_bridge": {
            "monster_class": monster_landauer_ternary["monster_local_shell"]["monster_class"],
            "shell_states": monster_landauer_ternary["monster_local_shell"]["extraspecial_shell"]["states"],
            "shell_trits": monster_landauer_ternary["monster_local_shell"]["extraspecial_shell"]["trits"],
            "shell_landauer_over_kT": monster_landauer_ternary["monster_local_shell"]["extraspecial_shell"]["landauer_over_kT"]["exact"],
            "heisenberg_irrep_states": monster_landauer_ternary["monster_local_shell"]["heisenberg_irrep"]["states"],
            "heisenberg_irrep_trits": monster_landauer_ternary["monster_local_shell"]["heisenberg_irrep"]["trits"],
            "complement_states": monster_landauer_ternary["monster_local_shell"]["shell_complement"]["states"],
            "complement_trits": monster_landauer_ternary["monster_local_shell"]["shell_complement"]["trits"],
            "logical_qutrits": monster_landauer_ternary["ternary_lock_dictionary"]["logical_qutrits"],
            "logical_trits": monster_landauer_ternary["ternary_lock_dictionary"]["logical_trits"],
            "phi3_equals_shell_trits": monster_landauer_ternary["ternary_lock_dictionary"]["phi3_equals_shell_trits"],
            "shared_six_equals_irrep_trits": monster_landauer_ternary["ternary_lock_dictionary"]["shared_six_equals_irrep_trits"],
            "phi6_equals_complement_trits": monster_landauer_ternary["ternary_lock_dictionary"]["phi6_equals_complement_trits"],
            "phi6_equals_shell_minus_irrep": monster_landauer_ternary["ternary_lock_dictionary"]["phi6_equals_shell_minus_irrep"],
            "heisenberg_irrep_equals_q_squared_times_logical_qutrits": monster_landauer_ternary["ternary_lock_dictionary"]["heisenberg_irrep_equals_q_squared_times_logical_qutrits"],
            "weinberg_from_generation_over_shell": monster_landauer_ternary["landauer_ratio_dictionary"]["weinberg_from_generation_over_shell"]["exact"],
            "theta12_from_logical_over_shell": monster_landauer_ternary["landauer_ratio_dictionary"]["theta12_from_logical_over_shell"]["exact"],
            "theta23_from_complement_over_shell": monster_landauer_ternary["landauer_ratio_dictionary"]["theta23_from_complement_over_shell"]["exact"],
            "weinberg_matches_promoted_value": monster_landauer_ternary["landauer_ratio_dictionary"]["weinberg_matches_promoted_value"],
            "theta12_matches_promoted_value": monster_landauer_ternary["landauer_ratio_dictionary"]["theta12_matches_promoted_value"],
            "theta23_matches_promoted_value": monster_landauer_ternary["landauer_ratio_dictionary"]["theta23_matches_promoted_value"],
            "discrete_to_continuum_ratio": monster_landauer_ternary["landauer_ratio_dictionary"]["discrete_to_continuum_ratio"]["exact"],
            "discrete_to_continuum_equals_shell_times_generation_trits": monster_landauer_ternary["landauer_ratio_dictionary"]["discrete_to_continuum_equals_shell_times_generation_trits"],
            "topological_over_continuum": monster_landauer_ternary["landauer_ratio_dictionary"]["topological_over_continuum"]["exact"],
            "topological_over_continuum_equals_complement_trits": monster_landauer_ternary["landauer_ratio_dictionary"]["topological_over_continuum_equals_complement_trits"],
        },
        "monster_shell_factorization_bridge": {
            "shell_states": monster_shell_factorization["shell_factorization"]["shell_states"],
            "heisenberg_states": monster_shell_factorization["shell_factorization"]["heisenberg_states"],
            "logical_states": monster_shell_factorization["shell_factorization"]["logical_states"],
            "generation_states": monster_shell_factorization["shell_factorization"]["generation_states"],
            "complement_states": monster_shell_factorization["shell_factorization"]["complement_states"],
            "shell_equals_heisenberg_times_logical_times_generation": monster_shell_factorization["shell_factorization"]["shell_equals_heisenberg_times_logical_times_generation"],
            "complement_equals_logical_times_generation": monster_shell_factorization["shell_factorization"]["complement_equals_logical_times_generation"],
            "shell_trits_split": monster_shell_factorization["shell_factorization"]["shell_trits_split"],
            "shell_trits_factorization_exact": monster_shell_factorization["shell_factorization"]["shell_trits_factorization_exact"],
            "complement_trits_split": monster_shell_factorization["shell_factorization"]["complement_trits_split"],
            "complement_trits_factorization_exact": monster_shell_factorization["shell_factorization"]["complement_trits_factorization_exact"],
            "weinberg_from_generation_over_shell": monster_shell_factorization["promoted_ratio_factorization"]["weinberg_from_generation_over_shell"]["exact"],
            "theta12_from_logical_over_shell": monster_shell_factorization["promoted_ratio_factorization"]["theta12_from_logical_over_shell"]["exact"],
            "active_heisenberg_share": monster_shell_factorization["promoted_ratio_factorization"]["active_heisenberg_share"]["exact"],
            "theta23_from_complement_over_shell": monster_shell_factorization["promoted_ratio_factorization"]["theta23_from_complement_over_shell"]["exact"],
            "theta23_equals_theta12_plus_weinberg": monster_shell_factorization["promoted_ratio_factorization"]["theta23_equals_theta12_plus_weinberg"],
            "theta23_plus_active_heisenberg_share_equals_one": monster_shell_factorization["promoted_ratio_factorization"]["theta23_plus_active_heisenberg_share_equals_one"],
            "discrete_to_continuum_ratio": monster_shell_factorization["curved_ratio_factorization"]["discrete_to_continuum_ratio"]["exact"],
            "topological_over_continuum": monster_shell_factorization["curved_ratio_factorization"]["topological_over_continuum"]["exact"],
            "discrete_to_continuum_equals_shell_times_generation": monster_shell_factorization["curved_ratio_factorization"]["discrete_to_continuum_equals_shell_times_generation"],
            "topological_over_continuum_equals_logical_plus_generation": monster_shell_factorization["curved_ratio_factorization"]["topological_over_continuum_equals_logical_plus_generation"],
        },
        "monster_3adic_closure_bridge": {
            "three_primary_states": monster_3adic_closure["monster_3_primary_order"]["three_primary_part"]["states"],
            "three_primary_trits": monster_3adic_closure["monster_3_primary_order"]["three_primary_part"]["trits"],
            "full_landauer_over_kT": monster_3adic_closure["monster_3_primary_order"]["three_primary_part"]["landauer_over_kT"]["exact"],
            "shell_states": monster_3adic_closure["local_global_ternary_closure"]["shell_states"],
            "complement_states": monster_3adic_closure["local_global_ternary_closure"]["complement_states"],
            "full_three_primary_equals_shell_times_complement": monster_3adic_closure["local_global_ternary_closure"]["full_three_primary_equals_shell_times_complement"],
            "full_three_primary_equals_heisenberg_times_logical_squared_times_generation_squared": monster_3adic_closure["local_global_ternary_closure"]["full_three_primary_equals_heisenberg_times_logical_squared_times_generation_squared"],
            "full_three_primary_trits_equal_phi3_plus_phi6": monster_3adic_closure["local_global_ternary_closure"]["full_three_primary_trits_equal_phi3_plus_phi6"],
            "landauer_additivity_exact": monster_3adic_closure["landauer_budget"]["landauer_additivity_exact"],
            "shell_share_of_full_monster_three_primary": monster_3adic_closure["landauer_budget"]["shell_share_of_full_monster_three_primary"]["exact"],
            "complement_share_of_full_monster_three_primary": monster_3adic_closure["landauer_budget"]["complement_share_of_full_monster_three_primary"]["exact"],
            "gravity_over_q": monster_3adic_closure["curved_thermodynamic_dictionary"]["gravity_over_q"]["exact"],
            "topological_over_continuum": monster_3adic_closure["curved_thermodynamic_dictionary"]["topological_over_continuum"]["exact"],
            "shell_from_curved_gravity_exact": monster_3adic_closure["curved_thermodynamic_dictionary"]["shell_from_curved_gravity_exact"],
            "complement_from_curved_topology_exact": monster_3adic_closure["curved_thermodynamic_dictionary"]["complement_from_curved_topology_exact"],
            "full_monster_three_primary_from_curved_coefficients_exact": monster_3adic_closure["curved_thermodynamic_dictionary"]["full_monster_three_primary_from_curved_coefficients_exact"],
            "monster_three_trits_equal_phi3_plus_phi6": monster_3adic_closure["curved_thermodynamic_dictionary"]["monster_three_trits_equal_phi3_plus_phi6"],
        },
        "monster_3b_centralizer_bridge": {
            "centralizer_label": monster_3b_centralizer["three_b_centralizer"]["centralizer_label"],
            "monster_three_primary_states": monster_3b_centralizer["three_b_centralizer"]["monster_three_primary_part"]["states"],
            "centralizer_three_primary_states": monster_3b_centralizer["three_b_centralizer"]["centralizer_three_primary_part"]["states"],
            "centralizer_three_primary_matches_monster": monster_3b_centralizer["three_b_centralizer"]["centralizer_three_primary_matches_monster"],
            "shell_states": monster_3b_centralizer["centralizer_factorization"]["shell_states"],
            "two_suz_three_primary_states": monster_3b_centralizer["centralizer_factorization"]["two_suz_three_primary_states"],
            "two_suz_three_primary_trits": monster_3b_centralizer["centralizer_factorization"]["two_suz_three_primary_trits"],
            "two_suz_three_primary_equals_logical_times_generation": monster_3b_centralizer["centralizer_factorization"]["two_suz_three_primary_equals_logical_times_generation"],
            "landauer_additivity_exact": monster_3b_centralizer["landauer_budget"]["landauer_additivity_exact"],
            "gravity_over_q": monster_3b_centralizer["curved_dictionary"]["gravity_over_q"]["exact"],
            "topology_over_continuum": monster_3b_centralizer["curved_dictionary"]["topology_over_continuum"]["exact"],
            "shell_from_curved_gravity_exact": monster_3b_centralizer["curved_dictionary"]["shell_from_curved_gravity_exact"],
            "two_suz_from_curved_topology_exact": monster_3b_centralizer["curved_dictionary"]["two_suz_from_curved_topology_exact"],
            "centralizer_three_primary_from_curved_coefficients_exact": monster_3b_centralizer["curved_dictionary"]["centralizer_three_primary_from_curved_coefficients_exact"],
        },
        "monster_lagrangian_complement_bridge": {
            "max_abelian_subgroup_order": monster_lagrangian_complement["lagrangian_realization"]["max_abelian_subgroup_order"],
            "complement_states": monster_lagrangian_complement["lagrangian_realization"]["complement_states"],
            "lagrangian_quotient_states": monster_lagrangian_complement["lagrangian_realization"]["lagrangian_quotient_states"],
            "complement_equals_lifted_max_abelian_exactly": monster_lagrangian_complement["lagrangian_realization"]["complement_equals_lifted_max_abelian_exactly"],
            "lagrangian_quotient_equals_heisenberg_irrep": monster_lagrangian_complement["lagrangian_realization"]["lagrangian_quotient_equals_heisenberg_irrep"],
            "lagrangian_quotient_equals_golay_codewords": monster_lagrangian_complement["lagrangian_realization"]["lagrangian_quotient_equals_golay_codewords"],
            "lagrangian_quotient_equals_sl27_operator_basis": monster_lagrangian_complement["lagrangian_realization"]["lagrangian_quotient_equals_sl27_operator_basis"],
            "center_times_lagrangian_quotient_equals_complement": monster_lagrangian_complement["lagrangian_realization"]["center_times_lagrangian_quotient_equals_complement"],
            "complement_equals_logical_times_generation": monster_lagrangian_complement["dual_factorization"]["complement_equals_logical_times_generation"],
            "logical_plus_generation_trits": monster_lagrangian_complement["dual_factorization"]["logical_plus_generation_trits"],
            "center_plus_heisenberg_trits": monster_lagrangian_complement["dual_factorization"]["center_plus_heisenberg_trits"],
            "complement_trits_equal_logical_plus_generation": monster_lagrangian_complement["dual_factorization"]["complement_trits_equal_logical_plus_generation"],
            "complement_trits_equal_center_plus_heisenberg": monster_lagrangian_complement["dual_factorization"]["complement_trits_equal_center_plus_heisenberg"],
            "dual_trit_splits_agree_exactly": monster_lagrangian_complement["dual_factorization"]["dual_trit_splits_agree_exactly"],
            "topological_over_continuum": monster_lagrangian_complement["curved_dictionary"]["topological_over_continuum"]["exact"],
            "topological_equals_complement_trits": monster_lagrangian_complement["curved_dictionary"]["topological_equals_complement_trits"],
            "topological_equals_logical_plus_generation": monster_lagrangian_complement["curved_dictionary"]["topological_equals_logical_plus_generation"],
            "topological_equals_center_plus_heisenberg": monster_lagrangian_complement["curved_dictionary"]["topological_equals_center_plus_heisenberg"],
        },
        "monster_selector_completion_bridge": {
            "complement_states": monster_selector_completion["selector_completion"]["complement_states"],
            "center_states": monster_selector_completion["selector_completion"]["center_states"],
            "heisenberg_completion_states": monster_selector_completion["selector_completion"]["heisenberg_completion_states"],
            "sl27_traceless_dimension": monster_selector_completion["selector_completion"]["sl27_traceless_dimension"],
            "nonzero_golay_codewords": monster_selector_completion["selector_completion"]["nonzero_golay_codewords"],
            "full_golay_codewords": monster_selector_completion["selector_completion"]["full_golay_codewords"],
            "selector_line_dimension": monster_selector_completion["selector_completion"]["selector_line_dimension"],
            "projective_selector_line": monster_selector_completion["selector_completion"]["projective_selector_line"],
            "w33_kernel_dimension_mod_3": monster_selector_completion["selector_completion"]["w33_kernel_dimension_mod_3"],
            "full_codewords_equal_sl27_plus_selector": monster_selector_completion["selector_completion"]["full_codewords_equal_sl27_plus_selector"],
            "nonzero_codewords_equal_sl27_traceless": monster_selector_completion["selector_completion"]["nonzero_codewords_equal_sl27_traceless"],
            "complement_equals_center_times_selector_completion": monster_selector_completion["selector_completion"]["complement_equals_center_times_selector_completion"],
            "selector_completion_decomposition_exact": monster_selector_completion["selector_completion"]["selector_completion_decomposition_exact"],
            "sl27_z3_total_dimension": monster_selector_completion["cross_bridge_dictionary"]["sl27_z3_total_dimension"],
            "sl27_bridge_claim_holds": monster_selector_completion["cross_bridge_dictionary"]["sl27_bridge_claim_holds"],
            "golay_nonzero_equals_sl27_total": monster_selector_completion["cross_bridge_dictionary"]["golay_nonzero_equals_sl27_total"],
            "transport_selector_is_unique": monster_selector_completion["cross_bridge_dictionary"]["transport_selector_is_unique"],
            "w33_all_ones_spans_mod_3_kernel": monster_selector_completion["cross_bridge_dictionary"]["w33_all_ones_spans_mod_3_kernel"],
            "transport_projective_selector_line_is_unique": monster_selector_completion["cross_bridge_dictionary"]["transport_projective_selector_line_is_unique"],
            "path_groupoid_has_unique_invariant_line": monster_selector_completion["cross_bridge_dictionary"]["path_groupoid_has_unique_invariant_line"],
        },
        "monster_q5_completion_bridge": {
            "q": monster_q5_completion["q5_restoration"]["q"],
            "q5": monster_q5_completion["q5_restoration"]["q5"],
            "q7": monster_q5_completion["q5_restoration"]["q7"],
            "grade_split": monster_q5_completion["q5_restoration"]["grade_split"],
            "selector_line_dimension": monster_q5_completion["q5_restoration"]["selector_line_dimension"],
            "restored_blocks": monster_q5_completion["q5_restoration"]["restored_blocks"],
            "restored_blocks_are_three_q5_blocks": monster_q5_completion["q5_restoration"]["restored_blocks_are_three_q5_blocks"],
            "full_codewords": monster_q5_completion["q5_restoration"]["full_codewords"],
            "full_codewords_equal_3q5": monster_q5_completion["q5_restoration"]["full_codewords_equal_3q5"],
            "complement_states": monster_q5_completion["monster_completion_dictionary"]["complement_states"],
            "complement_equals_q7": monster_q5_completion["monster_completion_dictionary"]["complement_equals_q7"],
            "edge_count": monster_q5_completion["w33_q5_dictionary"]["edge_count"],
            "edge_count_equals_q5_minus_q": monster_q5_completion["w33_q5_dictionary"]["edge_count_equals_q5_minus_q"],
            "semisimple_curved_states": monster_q5_completion["transport_curvature_dictionary"]["semisimple_curved_states"],
            "generation_states": monster_q5_completion["transport_curvature_dictionary"]["generation_states"],
            "semisimple_curved_equals_q_squared_times_edges": monster_q5_completion["transport_curvature_dictionary"]["semisimple_curved_equals_q_squared_times_edges"],
            "semisimple_curved_equals_q7_minus_q3": monster_q5_completion["transport_curvature_dictionary"]["semisimple_curved_equals_q7_minus_q3"],
            "complement_equals_semisimple_curved_plus_generation": monster_q5_completion["transport_curvature_dictionary"]["complement_equals_semisimple_curved_plus_generation"],
            "complement_equals_q_squared_edges_plus_q_cubed": monster_q5_completion["transport_curvature_dictionary"]["complement_equals_q_squared_edges_plus_q_cubed"],
        },
        "monster_transport_shell_bridge": {
            "q": monster_transport_shell["transport_shell_dictionary"]["q"],
            "w33_edge_count": monster_transport_shell["transport_shell_dictionary"]["w33_edge_count"],
            "transport_edge_count": monster_transport_shell["transport_shell_dictionary"]["transport_edge_count"],
            "local_line_bundle_dimension": monster_transport_shell["transport_shell_dictionary"]["local_line_bundle_dimension"],
            "a2_transfer_block_rank": monster_transport_shell["transport_shell_dictionary"]["a2_transfer_block_rank"],
            "semisimple_transport_shell": monster_transport_shell["transport_shell_dictionary"]["semisimple_transport_shell"],
            "generation_states": monster_transport_shell["transport_shell_dictionary"]["generation_states"],
            "monster_complement_states": monster_transport_shell["transport_shell_dictionary"]["monster_complement_states"],
            "semisimple_equals_q_squared_times_w33_edges": monster_transport_shell["transport_shell_dictionary"]["semisimple_equals_q_squared_times_w33_edges"],
            "semisimple_equals_q_times_transport_edges": monster_transport_shell["transport_shell_dictionary"]["semisimple_equals_q_times_transport_edges"],
            "semisimple_equals_a2_block_rank_times_bundle_dimension": monster_transport_shell["transport_shell_dictionary"]["semisimple_equals_a2_block_rank_times_bundle_dimension"],
            "complement_equals_semisimple_plus_generation": monster_transport_shell["monster_transport_completion"]["complement_equals_semisimple_plus_generation"],
            "complement_equals_q_squared_edges_plus_q_cubed": monster_transport_shell["monster_transport_completion"]["complement_equals_q_squared_edges_plus_q_cubed"],
            "complement_equals_q_transport_edges_plus_q_cubed": monster_transport_shell["monster_transport_completion"]["complement_equals_q_transport_edges_plus_q_cubed"],
            "complement_equals_block_bundle_plus_generation": monster_transport_shell["monster_transport_completion"]["complement_equals_block_bundle_plus_generation"],
        },
        "monster_supertrace_bridge": {
            "euler_characteristic": monster_supertrace["spectral_dictionary"]["euler_characteristic"],
            "supertrace": monster_supertrace["spectral_dictionary"]["supertrace"],
            "supertrace_magnitude": monster_supertrace["spectral_dictionary"]["supertrace_magnitude"],
            "selector_line_dimension": monster_supertrace["spectral_dictionary"]["selector_line_dimension"],
            "logical_qutrits": monster_supertrace["spectral_dictionary"]["logical_qutrits"],
            "generation_states": monster_supertrace["spectral_dictionary"]["generation_states"],
            "e8_second_shell": monster_supertrace["spectral_dictionary"]["e8_second_shell"],
            "semisimple_transport_shell": monster_supertrace["spectral_dictionary"]["semisimple_transport_shell"],
            "monster_complement_states": monster_supertrace["spectral_dictionary"]["monster_complement_states"],
            "euler_matches_supertrace_exactly": monster_supertrace["spectral_dictionary"]["euler_matches_supertrace_exactly"],
            "semisimple_equals_e8_second_shell": monster_supertrace["spectral_dictionary"]["semisimple_equals_e8_second_shell"],
            "semisimple_equals_generation_times_supertrace_magnitude": monster_supertrace["spectral_dictionary"]["semisimple_equals_generation_times_supertrace_magnitude"],
            "logical_equals_supertrace_magnitude_plus_selector": monster_supertrace["spectral_dictionary"]["logical_equals_supertrace_magnitude_plus_selector"],
            "monster_complement_equals_generation_times_logical": monster_supertrace["spectral_dictionary"]["monster_complement_equals_generation_times_logical"],
            "monster_complement_equals_e8_second_shell_plus_generation": monster_supertrace["spectral_dictionary"]["monster_complement_equals_e8_second_shell_plus_generation"],
        },
        "monster_moonshine_lift_bridge": {
            "q": monster_moonshine_lift["moonshine_lift_dictionary"]["q"],
            "phi3": monster_moonshine_lift["moonshine_lift_dictionary"]["phi3"],
            "phi6": monster_moonshine_lift["moonshine_lift_dictionary"]["phi6"],
            "cyclotomic_lift_factor": monster_moonshine_lift["moonshine_lift_dictionary"]["cyclotomic_lift_factor"],
            "local_second_shell": monster_moonshine_lift["moonshine_lift_dictionary"]["local_second_shell"],
            "leech_kissing_number": monster_moonshine_lift["moonshine_lift_dictionary"]["leech_kissing_number"],
            "logical_qutrits": monster_moonshine_lift["moonshine_lift_dictionary"]["logical_qutrits"],
            "spacetime_factor": monster_moonshine_lift["moonshine_lift_dictionary"]["spacetime_factor"],
            "moonshine_gap": monster_moonshine_lift["moonshine_lift_dictionary"]["moonshine_gap"],
            "first_moonshine_coefficient": monster_moonshine_lift["moonshine_lift_dictionary"]["first_moonshine_coefficient"],
            "smallest_monster_irrep": monster_moonshine_lift["moonshine_lift_dictionary"]["smallest_monster_irrep"],
            "selector_line_dimension": monster_moonshine_lift["moonshine_lift_dictionary"]["selector_line_dimension"],
            "local_second_shell_matches_theta_e8_second_shell": monster_moonshine_lift["moonshine_lift_dictionary"]["local_second_shell_matches_theta_e8_second_shell"],
            "leech_equals_local_second_shell_times_phi3_phi6": monster_moonshine_lift["moonshine_lift_dictionary"]["leech_equals_local_second_shell_times_phi3_phi6"],
            "moonshine_gap_equals_q_plus_1_times_logical_qutrits": monster_moonshine_lift["moonshine_lift_dictionary"]["moonshine_gap_equals_q_plus_1_times_logical_qutrits"],
            "moonshine_gap_equals_q_plus_1_times_q_to_four": monster_moonshine_lift["moonshine_lift_dictionary"]["moonshine_gap_equals_q_plus_1_times_q_to_four"],
            "first_moonshine_equals_leech_plus_gap": monster_moonshine_lift["moonshine_lift_dictionary"]["first_moonshine_equals_leech_plus_gap"],
            "first_moonshine_equals_selector_plus_smallest_monster_irrep": monster_moonshine_lift["moonshine_lift_dictionary"]["first_moonshine_equals_selector_plus_smallest_monster_irrep"],
            "first_moonshine_equals_cyclotomic_lifted_shell_plus_spacetime_matter": monster_moonshine_lift["moonshine_lift_dictionary"]["first_moonshine_equals_cyclotomic_lifted_shell_plus_spacetime_matter"],
        },
        "monster_transport_moonshine_bridge": {
            "sl27_traceless_dimension": monster_transport_moonshine["transport_moonshine_dictionary"]["sl27_traceless_dimension"],
            "sl27_completed_dimension": monster_transport_moonshine["transport_moonshine_dictionary"]["sl27_completed_dimension"],
            "directed_transport_edges": monster_transport_moonshine["transport_moonshine_dictionary"]["directed_transport_edges"],
            "gauge_package_rank": monster_transport_moonshine["transport_moonshine_dictionary"]["gauge_package_rank"],
            "leech_kissing_number": monster_transport_moonshine["transport_moonshine_dictionary"]["leech_kissing_number"],
            "moonshine_gap": monster_transport_moonshine["transport_moonshine_dictionary"]["moonshine_gap"],
            "first_moonshine_coefficient": monster_transport_moonshine["transport_moonshine_dictionary"]["first_moonshine_coefficient"],
            "leech_equals_sl27_traceless_times_transport_edges": monster_transport_moonshine["transport_moonshine_dictionary"]["leech_equals_sl27_traceless_times_transport_edges"],
            "first_moonshine_equals_completed_sl27_times_transport_plus_gauge_rank": monster_transport_moonshine["transport_moonshine_dictionary"]["first_moonshine_equals_completed_sl27_times_transport_plus_gauge_rank"],
            "moonshine_gap_equals_transport_plus_gauge_rank": monster_transport_moonshine["transport_moonshine_dictionary"]["moonshine_gap_equals_transport_plus_gauge_rank"],
            "gauge_package_rank_equals_e6_plus_a2_plus_cartan": monster_transport_moonshine["transport_moonshine_dictionary"]["gauge_package_rank_equals_e6_plus_a2_plus_cartan"],
        },
        "monster_gap_duality_bridge": {
            "leech_kissing_number": monster_gap_duality["moonshine_gap_dictionary"]["leech_kissing_number"],
            "first_moonshine_coefficient": monster_gap_duality["moonshine_gap_dictionary"]["first_moonshine_coefficient"],
            "moonshine_gap": monster_gap_duality["moonshine_gap_dictionary"]["moonshine_gap"],
            "gauge_package_rank": monster_gap_duality["moonshine_gap_dictionary"]["gauge_package_rank"],
            "shared_six_channel_rank": monster_gap_duality["moonshine_gap_dictionary"]["shared_six_channel_rank"],
            "spacetime_factor": monster_gap_duality["moonshine_gap_dictionary"]["spacetime_factor"],
            "logical_qutrits": monster_gap_duality["moonshine_gap_dictionary"]["logical_qutrits"],
            "gap_equals_exceptional_gauge_rank_times_shared_six": monster_gap_duality["moonshine_gap_dictionary"]["gap_equals_exceptional_gauge_rank_times_shared_six"],
            "gap_equals_spacetime_factor_times_logical_qutrits": monster_gap_duality["moonshine_gap_dictionary"]["gap_equals_spacetime_factor_times_logical_qutrits"],
            "exceptional_gap_matches_spacetime_matter_gap": monster_gap_duality["moonshine_gap_dictionary"]["exceptional_gap_matches_spacetime_matter_gap"],
            "first_moonshine_equals_traceless_transport_plus_exceptional_gap": monster_gap_duality["moonshine_gap_dictionary"]["first_moonshine_equals_traceless_transport_plus_exceptional_gap"],
            "first_moonshine_equals_completed_transport_plus_gauge_rank": monster_gap_duality["moonshine_gap_dictionary"]["first_moonshine_equals_completed_transport_plus_gauge_rank"],
            "gauge_rank_equals_e6_plus_a2_plus_cartan": monster_gap_duality["moonshine_gap_dictionary"]["gauge_rank_equals_e6_plus_a2_plus_cartan"],
            "shared_six_is_live_a2_rank": monster_gap_duality["moonshine_gap_dictionary"]["shared_six_is_live_a2_rank"],
        },
        "monster_triangle_landauer_bridge": {
            "q": monster_triangle_landauer["triangle_landauer_dictionary"]["q"],
            "vertices": monster_triangle_landauer["triangle_landauer_dictionary"]["vertices"],
            "degree": monster_triangle_landauer["triangle_landauer_dictionary"]["degree"],
            "lambda": monster_triangle_landauer["triangle_landauer_dictionary"]["lambda"],
            "triangle_count": monster_triangle_landauer["triangle_landauer_dictionary"]["triangle_count"],
            "automorphism_order": monster_triangle_landauer["triangle_landauer_dictionary"]["automorphism_order"],
            "triangle_stabilizer": monster_triangle_landauer["triangle_landauer_dictionary"]["triangle_stabilizer"],
            "moonshine_gap": monster_triangle_landauer["triangle_landauer_dictionary"]["moonshine_gap"],
            "triangle_stabilizer_matches_general_formula": monster_triangle_landauer["triangle_landauer_dictionary"]["triangle_stabilizer_matches_general_formula"],
            "triangle_stabilizer_equals_moonshine_gap": monster_triangle_landauer["triangle_landauer_dictionary"]["triangle_stabilizer_equals_moonshine_gap"],
            "triangle_stabilizer_equals_exceptional_times_shared_six": monster_triangle_landauer["triangle_landauer_dictionary"]["triangle_stabilizer_equals_exceptional_times_shared_six"],
            "triangle_stabilizer_equals_spacetime_times_logical_qutrits": monster_triangle_landauer["triangle_landauer_dictionary"]["triangle_stabilizer_equals_spacetime_times_logical_qutrits"],
            "triangle_stabilizer_equals_degree_times_generation": monster_triangle_landauer["triangle_landauer_dictionary"]["triangle_stabilizer_equals_degree_times_generation"],
            "first_moonshine_equals_transport_traceless_plus_triangle_stabilizer": monster_triangle_landauer["triangle_landauer_dictionary"]["first_moonshine_equals_transport_traceless_plus_triangle_stabilizer"],
            "landauer_gap_over_kT": monster_triangle_landauer["triangle_landauer_dictionary"]["landauer_gap_over_kT"]["exact"],
            "landauer_exceptional_split": monster_triangle_landauer["triangle_landauer_dictionary"]["landauer_exceptional_split"],
            "landauer_matter_split": monster_triangle_landauer["triangle_landauer_dictionary"]["landauer_matter_split"],
            "landauer_exceptional_split_matches": monster_triangle_landauer["triangle_landauer_dictionary"]["landauer_exceptional_split_matches"],
            "landauer_matter_split_matches": monster_triangle_landauer["triangle_landauer_dictionary"]["landauer_matter_split_matches"],
        },
        "triality_moonshine_spine_bridge": {
            "q8_vertex_block": triality_moonshine_spine["compressed_spine_dictionary"]["q8_vertex_block"],
            "weyl_e6_order": triality_moonshine_spine["compressed_spine_dictionary"]["weyl_e6_order"],
            "monster_semisimple_shell": triality_moonshine_spine["compressed_spine_dictionary"]["monster_semisimple_shell"],
            "monster_local_complement": triality_moonshine_spine["compressed_spine_dictionary"]["monster_local_complement"],
            "leech_kissing_number": triality_moonshine_spine["compressed_spine_dictionary"]["leech_kissing_number"],
            "first_moonshine_coefficient": triality_moonshine_spine["compressed_spine_dictionary"]["first_moonshine_coefficient"],
            "moonshine_gap": triality_moonshine_spine["compressed_spine_dictionary"]["moonshine_gap"],
            "weyl_e6_quotiented_by_q8_vertex_block_equals_shell": triality_moonshine_spine["compressed_spine_dictionary"]["weyl_e6_quotiented_by_q8_vertex_block_equals_shell"],
            "shell_equals_tritangents_times_spinor_dimension": triality_moonshine_spine["compressed_spine_dictionary"]["shell_equals_tritangents_times_spinor_dimension"],
            "shell_equals_directed_transport_edges_times_cartan_rank": triality_moonshine_spine["compressed_spine_dictionary"]["shell_equals_directed_transport_edges_times_cartan_rank"],
            "shell_equals_transport_edges_times_q": triality_moonshine_spine["compressed_spine_dictionary"]["shell_equals_transport_edges_times_q"],
            "shell_equals_w33_edges_times_q_squared": triality_moonshine_spine["compressed_spine_dictionary"]["shell_equals_w33_edges_times_q_squared"],
            "local_complement_equals_shell_plus_generation": triality_moonshine_spine["compressed_spine_dictionary"]["local_complement_equals_shell_plus_generation"],
            "leech_equals_shell_times_phi3_phi6": triality_moonshine_spine["compressed_spine_dictionary"]["leech_equals_shell_times_phi3_phi6"],
            "first_moonshine_equals_leech_plus_gap": triality_moonshine_spine["compressed_spine_dictionary"]["first_moonshine_equals_leech_plus_gap"],
            "gap_equals_gauge_rank_times_shared_six": triality_moonshine_spine["compressed_spine_dictionary"]["gap_equals_gauge_rank_times_shared_six"],
            "gap_equals_spacetime_factor_times_logical_qutrits": triality_moonshine_spine["compressed_spine_dictionary"]["gap_equals_spacetime_factor_times_logical_qutrits"],
        },
        "s12_klein_projective_bridge": {
            "harmonic_cube_order": s12_klein_projective["harmonic_cube_square_dictionary"]["harmonic_cube_order"],
            "ternary_golay_code_size": s12_klein_projective["harmonic_cube_square_dictionary"]["ternary_golay_code_size"],
            "sl27_shell_dimension": s12_klein_projective["harmonic_cube_square_dictionary"]["sl27_shell_dimension"],
            "projectivized_shell_size": s12_klein_projective["harmonic_cube_square_dictionary"]["projectivized_shell_size"],
            "ambient_pg53_points": s12_klein_projective["harmonic_cube_square_dictionary"]["ambient_pg53_points"],
            "w33_klein_slice_points": s12_klein_projective["harmonic_cube_square_dictionary"]["w33_klein_slice_points"],
            "moonshine_gap": s12_klein_projective["harmonic_cube_square_dictionary"]["moonshine_gap"],
            "harmonic_cube_square_equals_golay_size": s12_klein_projective["harmonic_cube_square_dictionary"]["harmonic_cube_square_equals_golay_size"],
            "nonzero_golay_equals_sl27_dimension": s12_klein_projective["harmonic_cube_square_dictionary"]["nonzero_golay_equals_sl27_dimension"],
            "projectivized_nonzero_shell_equals_pg53_points": s12_klein_projective["harmonic_cube_square_dictionary"]["projectivized_nonzero_shell_equals_pg53_points"],
            "projective_shell_minus_w33_klein_slice_equals_gap": s12_klein_projective["harmonic_cube_square_dictionary"]["projective_shell_minus_w33_klein_slice_equals_gap"],
            "projective_shell_splits_as_w33_slice_plus_gap": s12_klein_projective["harmonic_cube_square_dictionary"]["projective_shell_splits_as_w33_slice_plus_gap"],
            "projective_weight_distribution": s12_klein_projective["weight_projectivization"]["projective_weight_distribution"],
            "external_plane_points": s12_klein_projective["quartic_parallelism_guide_rail"]["clifford_parallelism_external_plane_points"],
            "plane_quartic_bitangent_count": s12_klein_projective["quartic_parallelism_guide_rail"]["plane_quartic_bitangent_count"],
            "ambient_equals_bitangents_times_external_plane_points": s12_klein_projective["quartic_parallelism_guide_rail"]["ambient_pg53_equals_bitangents_times_external_plane_points"],
        },
        "klein_quartic_ag21_bridge": {
            "klein_quartic_ag_code_length": klein_quartic_ag21["ag21_coding_shadow"]["klein_quartic_ag_code_length"],
            "fano_flags": klein_quartic_ag21["ag21_coding_shadow"]["fano_flags"],
            "heawood_edges": klein_quartic_ag21["ag21_coding_shadow"]["heawood_edges"],
            "csaszar_edges": klein_quartic_ag21["ag21_coding_shadow"]["csaszar_edges"],
            "szilassi_edges": klein_quartic_ag21["ag21_coding_shadow"]["szilassi_edges"],
            "ag21_equals_q_times_phi6": klein_quartic_ag21["ag21_coding_shadow"]["ag21_equals_q_times_phi6"],
            "all_promoted_21_counts_agree": klein_quartic_ag21["ag21_coding_shadow"]["all_promoted_21_counts_agree"],
        },
        "klein_harmonic_vogel_bridge": {
            "harmonic_packet_total": klein_harmonic_vogel["harmonic_quartic_dictionary"]["harmonic_packet_total"],
            "klein_quartic_vertices": klein_harmonic_vogel["harmonic_quartic_dictionary"]["klein_quartic_vertices"],
            "klein_quartic_triangles": klein_harmonic_vogel["harmonic_quartic_dictionary"]["klein_quartic_triangles"],
            "klein_quartic_edges": klein_harmonic_vogel["harmonic_quartic_dictionary"]["klein_quartic_edges"],
            "klein_quartic_automorphism_order": klein_harmonic_vogel["harmonic_quartic_dictionary"]["klein_quartic_automorphism_order"],
            "bitangent_count": klein_harmonic_vogel["harmonic_quartic_dictionary"]["bitangent_count"],
            "ag21_length": klein_harmonic_vogel["harmonic_quartic_dictionary"]["ag21_length"],
            "phi3": klein_harmonic_vogel["harmonic_quartic_dictionary"]["phi3"],
            "g2_dimension": klein_harmonic_vogel["harmonic_quartic_dictionary"]["g2_dimension"],
            "a26_rank": klein_harmonic_vogel["harmonic_quartic_dictionary"]["a26_rank"],
            "ambient_pg53_points": klein_harmonic_vogel["harmonic_quartic_dictionary"]["ambient_pg53_points"],
            "w33_klein_slice_points": klein_harmonic_vogel["harmonic_quartic_dictionary"]["w33_klein_slice_points"],
            "moonshine_gap": klein_harmonic_vogel["harmonic_quartic_dictionary"]["moonshine_gap"],
            "sl27_shell_dimension": klein_harmonic_vogel["harmonic_quartic_dictionary"]["sl27_shell_dimension"],
            "harmonic_packet_total_equals_g2_dimension": klein_harmonic_vogel["harmonic_quartic_dictionary"]["harmonic_packet_total_equals_g2_dimension"],
            "triangles_equals_packets_times_spacetime": klein_harmonic_vogel["harmonic_quartic_dictionary"]["triangles_equals_packets_times_spacetime"],
            "triangles_equals_two_times_bitangents": klein_harmonic_vogel["harmonic_quartic_dictionary"]["triangles_equals_two_times_bitangents"],
            "triangles_equals_cartan_times_phi6": klein_harmonic_vogel["harmonic_quartic_dictionary"]["triangles_equals_cartan_times_phi6"],
            "edges_equals_packets_times_shared_six": klein_harmonic_vogel["promoted_factorizations"]["edges_equals_packets_times_shared_six"],
            "edges_equals_four_times_ag21": klein_harmonic_vogel["promoted_factorizations"]["edges_equals_four_times_ag21"],
            "edges_equals_gauge_closure_times_phi6": klein_harmonic_vogel["promoted_factorizations"]["edges_equals_gauge_closure_times_phi6"],
            "automorphisms_equals_two_times_edges": klein_harmonic_vogel["promoted_factorizations"]["automorphisms_equals_two_times_edges"],
            "automorphisms_equals_eight_times_ag21": klein_harmonic_vogel["promoted_factorizations"]["automorphisms_equals_eight_times_ag21"],
            "automorphisms_equals_vertex_seed_times_phi6": klein_harmonic_vogel["promoted_factorizations"]["automorphisms_equals_vertex_seed_times_phi6"],
            "ambient_equals_g2_times_a26": klein_harmonic_vogel["promoted_factorizations"]["ambient_equals_g2_times_a26"],
            "ambient_equals_bitangents_times_phi3": klein_harmonic_vogel["promoted_factorizations"]["ambient_equals_bitangents_times_phi3"],
            "ambient_equals_w33_slice_plus_gap": klein_harmonic_vogel["promoted_factorizations"]["ambient_equals_w33_slice_plus_gap"],
            "sl27_equals_two_times_ambient": klein_harmonic_vogel["promoted_factorizations"]["sl27_equals_two_times_ambient"],
            "sl27_equals_bitangents_times_a26": klein_harmonic_vogel["promoted_factorizations"]["sl27_equals_bitangents_times_a26"],
            "sl27_equals_triangles_times_phi3": klein_harmonic_vogel["promoted_factorizations"]["sl27_equals_triangles_times_phi3"],
            "gap_equals_spacetime_times_logical_qutrits": klein_harmonic_vogel["promoted_factorizations"]["gap_equals_spacetime_times_logical_qutrits"],
        },
        "klein_clifford_topological_bridge": {
            "external_plane_points": klein_clifford_topological["clifford_quartic_lift"]["clifford_parallelism_external_plane_points"],
            "bitangent_count": klein_clifford_topological["clifford_quartic_lift"]["plane_quartic_bitangent_count"],
            "quartic_triangle_count": klein_clifford_topological["clifford_quartic_lift"]["klein_quartic_triangle_count"],
            "e7_fundamental_dimension": klein_clifford_topological["clifford_quartic_lift"]["e7_fundamental_dimension"],
            "w33_klein_slice_points": klein_clifford_topological["clifford_quartic_lift"]["w33_klein_slice_points"],
            "topological_1_mode_coefficient": klein_clifford_topological["clifford_quartic_lift"]["topological_1_mode_coefficient"],
            "quartic_triangles_equal_e7_fund": klein_clifford_topological["clifford_quartic_lift"]["quartic_triangles_equal_e7_fund"],
            "quartic_triangles_equal_two_times_bitangents": klein_clifford_topological["clifford_quartic_lift"]["quartic_triangles_equal_two_times_bitangents"],
            "quartic_triangles_equal_cartan_times_phi6": klein_clifford_topological["clifford_quartic_lift"]["quartic_triangles_equal_cartan_times_phi6"],
            "bitangents_equal_q_cubic_plus_1": klein_clifford_topological["clifford_quartic_lift"]["bitangents_equal_q_cubic_plus_1"],
            "topological_equals_w33_slice_times_quartic_triangles": klein_clifford_topological["clifford_quartic_lift"]["topological_equals_w33_slice_times_quartic_triangles"],
            "ambient_pg53_points": klein_clifford_topological["ambient_shell_lift"]["ambient_pg53_points"],
            "sl27_shell_dimension": klein_clifford_topological["ambient_shell_lift"]["sl27_shell_dimension"],
            "ambient_equals_bitangents_times_phi3": klein_clifford_topological["ambient_shell_lift"]["ambient_equals_bitangents_times_phi3"],
            "sl27_equals_quartic_triangles_times_phi3": klein_clifford_topological["ambient_shell_lift"]["sl27_equals_quartic_triangles_times_phi3"],
            "sl27_equals_two_times_ambient": klein_clifford_topological["ambient_shell_lift"]["sl27_equals_two_times_ambient"],
        },
        "klein_bitangent_shell_bridge": {
            "bitangent_shell": klein_bitangent_shell["bitangent_shell_dictionary"]["bitangent_shell"],
            "phi3": klein_bitangent_shell["bitangent_shell_dictionary"]["phi3"],
            "a26_rank": klein_bitangent_shell["bitangent_shell_dictionary"]["a26_rank"],
            "quartic_triangle_shell": klein_bitangent_shell["bitangent_shell_dictionary"]["quartic_triangle_shell"],
            "w33_slice": klein_bitangent_shell["bitangent_shell_dictionary"]["w33_slice"],
            "supertrace_magnitude": klein_bitangent_shell["bitangent_shell_dictionary"]["supertrace_magnitude"],
            "euler_magnitude": klein_bitangent_shell["bitangent_shell_dictionary"]["euler_magnitude"],
            "ambient_pg53_points": klein_bitangent_shell["bitangent_shell_dictionary"]["ambient_pg53_points"],
            "sl27_shell_dimension": klein_bitangent_shell["bitangent_shell_dictionary"]["sl27_shell_dimension"],
            "topological_1_mode_coefficient": klein_bitangent_shell["bitangent_shell_dictionary"]["topological_1_mode_coefficient"],
            "ambient_equals_bitangents_times_phi3": klein_bitangent_shell["bitangent_shell_dictionary"]["ambient_equals_bitangents_times_phi3"],
            "sl27_equals_bitangents_times_a26_rank": klein_bitangent_shell["bitangent_shell_dictionary"]["sl27_equals_bitangents_times_a26_rank"],
            "topological_equals_bitangents_times_supertrace_magnitude": klein_bitangent_shell["bitangent_shell_dictionary"]["topological_equals_bitangents_times_supertrace_magnitude"],
            "topological_equals_bitangents_times_euler_magnitude": klein_bitangent_shell["bitangent_shell_dictionary"]["topological_equals_bitangents_times_euler_magnitude"],
            "quartic_triangles_equals_two_times_bitangents": klein_bitangent_shell["bitangent_shell_dictionary"]["quartic_triangles_equals_two_times_bitangents"],
            "quartic_triangles_equals_cartan_times_phi6": klein_bitangent_shell["bitangent_shell_dictionary"]["quartic_triangles_equals_cartan_times_phi6"],
            "topological_equals_w33_slice_times_quartic_triangles": klein_bitangent_shell["bitangent_shell_dictionary"]["topological_equals_w33_slice_times_quartic_triangles"],
            "a26_rank_equals_two_times_phi3": klein_bitangent_shell["bitangent_shell_dictionary"]["a26_rank_equals_two_times_phi3"],
            "dressings": klein_bitangent_shell["bitangent_shell_dictionary"]["dressings"],
            "shell_ladder": klein_bitangent_shell["bitangent_shell_dictionary"]["shell_ladder"],
            "topological_over_ambient": klein_bitangent_shell["bitangent_shell_dictionary"]["topological_over_ambient"],
            "topological_over_sl27": klein_bitangent_shell["bitangent_shell_dictionary"]["topological_over_sl27"],
        },
        "s12_vogel_spine_bridge": {
            "sl27_dimension": s12_vogel_spine["vogel_a_line_dictionary"]["sl27_dimension"],
            "a_family_rank": s12_vogel_spine["vogel_a_line_dictionary"]["a_family_rank"],
            "projective_shell_dimension": s12_vogel_spine["vogel_a_line_dictionary"]["projective_shell_dimension"],
            "g2_dimension": s12_vogel_spine["vogel_a_line_dictionary"]["g2_dimension"],
            "d4_dimension": s12_vogel_spine["vogel_a_line_dictionary"]["d4_dimension"],
            "f4_dimension": s12_vogel_spine["vogel_a_line_dictionary"]["f4_dimension"],
            "e8_dimension": s12_vogel_spine["vogel_a_line_dictionary"]["e8_dimension"],
            "finite_w33_dimension": s12_vogel_spine["vogel_a_line_dictionary"]["finite_w33_dimension"],
            "sl27_is_exactly_a26": s12_vogel_spine["vogel_a_line_dictionary"]["sl27_is_exactly_a26"],
            "projective_shell_equals_g2_times_a26_rank": s12_vogel_spine["vogel_a_line_dictionary"]["projective_shell_equals_g2_times_a26_rank"],
            "sl27_equals_d4_dimension_times_a26_rank": s12_vogel_spine["vogel_a_line_dictionary"]["sl27_equals_d4_dimension_times_a26_rank"],
            "sl27_equals_g2_times_f4": s12_vogel_spine["vogel_a_line_dictionary"]["sl27_equals_g2_times_f4"],
            "sl27_equals_finite_w33_plus_e8": s12_vogel_spine["vogel_a_line_dictionary"]["sl27_equals_finite_w33_plus_e8"],
            "dim_242_in_positive_exceptional_hit_set": s12_vogel_spine["exceptional_line_firewall"]["dim_242_in_positive_exceptional_hit_set"],
            "dim_486_in_positive_exceptional_hit_set": s12_vogel_spine["exceptional_line_firewall"]["dim_486_in_positive_exceptional_hit_set"],
            "dim_728_in_positive_exceptional_hit_set": s12_vogel_spine["exceptional_line_firewall"]["dim_728_in_positive_exceptional_hit_set"],
            "nearest_positive_exceptional_hits_to_728": s12_vogel_spine["exceptional_line_firewall"]["nearest_positive_exceptional_hits_to_728"],
            "distance_from_728_to_nearest_positive_exceptional_hit": s12_vogel_spine["exceptional_line_firewall"]["distance_from_728_to_nearest_positive_exceptional_hit"],
        },
        "weinberg_generator_bridge": {
            "generator": weinberg_generator["generator"]["exact"]["exact"],
            "tan_theta_c": weinberg_generator["generated_observables"]["tan_theta_c"]["exact"]["exact"],
            "sin2_theta_12": weinberg_generator["generated_observables"]["sin2_theta_12"]["exact"]["exact"],
            "sin2_theta_23": weinberg_generator["generated_observables"]["sin2_theta_23"]["exact"]["exact"],
            "sin2_theta_13": weinberg_generator["generated_observables"]["sin2_theta_13"]["exact"]["exact"],
            "omega_lambda": weinberg_generator["generated_observables"]["omega_lambda"]["exact"]["exact"],
            "higgs_ratio_square": weinberg_generator["generated_observables"]["higgs_ratio_square"]["exact"]["exact"],
            "a2_over_a0": weinberg_generator["generated_observables"]["a2_over_a0"]["exact"]["exact"],
            "a4_over_a0": weinberg_generator["generated_observables"]["a4_over_a0"]["exact"]["exact"],
            "discrete_6_mode_over_a0": weinberg_generator["generated_observables"]["discrete_6_mode_over_a0"]["exact"]["exact"],
            "discrete_to_continuum_ratio": weinberg_generator["generated_observables"]["discrete_to_continuum_ratio"]["exact"]["exact"],
            "sin2_theta_23_plus_2weinberg_equals_1": weinberg_generator["derived_relations"]["sin2_theta_23_plus_2weinberg_equals_1"],
            "sin2_theta_12_equals_four_thirds_weinberg": weinberg_generator["derived_relations"]["sin2_theta_12_equals_four_thirds_weinberg"],
            "omega_lambda_equals_3weinberg": weinberg_generator["derived_relations"]["omega_lambda_equals_3weinberg"],
            "cabibbo_equals_weinberg": weinberg_generator["derived_relations"]["cabibbo_equals_weinberg"],
            "gravity_ratio_equals_9_over_weinberg": weinberg_generator["derived_relations"]["gravity_ratio_equals_9_over_weinberg"],
        },
        "weinberg_reconstruction_bridge": {
            "master_variable": weinberg_reconstruction["master_variable"]["exact"]["exact"],
            "from_cabibbo": weinberg_reconstruction["independent_reconstructions"]["from_cabibbo"]["exact"]["exact"],
            "from_pmns_12": weinberg_reconstruction["independent_reconstructions"]["from_pmns_12"]["exact"]["exact"],
            "from_pmns_23": weinberg_reconstruction["independent_reconstructions"]["from_pmns_23"]["exact"]["exact"],
            "from_omega_lambda": weinberg_reconstruction["independent_reconstructions"]["from_omega_lambda"]["exact"]["exact"],
            "from_higgs_ratio": weinberg_reconstruction["independent_reconstructions"]["from_higgs_ratio"]["exact"]["exact"],
            "from_a2_over_a0": weinberg_reconstruction["independent_reconstructions"]["from_a2_over_a0"]["exact"]["exact"],
            "from_a4_over_a0": weinberg_reconstruction["independent_reconstructions"]["from_a4_over_a0"]["exact"]["exact"],
            "from_discrete_6_mode_over_a0": weinberg_reconstruction["independent_reconstructions"]["from_discrete_6_mode_over_a0"]["exact"]["exact"],
            "from_discrete_to_continuum_ratio": weinberg_reconstruction["independent_reconstructions"]["from_discrete_to_continuum_ratio"]["exact"]["exact"],
            "all_channels_match_master_variable": all(
                channel["matches_master_variable"]
                for channel in weinberg_reconstruction["independent_reconstructions"].values()
            ),
        },
        "srg_rosetta_lock_bridge": {
            "q_from_lambda_plus_one": srg_rosetta_lock["srg_data"]["q_from_lambda_plus_one"],
            "phi3_from_k_plus_one": srg_rosetta_lock["srg_data"]["phi3_from_k_plus_one"],
            "phi6_from_k_minus_lambda_minus_mu_plus_one": srg_rosetta_lock["srg_data"]["phi6_from_k_minus_lambda_minus_mu_plus_one"],
            "sin2_theta_w_ew": srg_rosetta_lock["promoted_observables"]["sin2_theta_w_ew"]["exact"]["exact"],
            "sin2_theta_12": srg_rosetta_lock["promoted_observables"]["sin2_theta_12"]["exact"]["exact"],
            "sin2_theta_23": srg_rosetta_lock["promoted_observables"]["sin2_theta_23"]["exact"]["exact"],
            "sin2_theta_13": srg_rosetta_lock["promoted_observables"]["sin2_theta_13"]["exact"]["exact"],
            "omega_lambda": srg_rosetta_lock["promoted_observables"]["omega_lambda"]["exact"]["exact"],
            "higgs_ratio_square": srg_rosetta_lock["promoted_observables"]["higgs_ratio_square"]["exact"]["exact"],
            "a2_over_a0": srg_rosetta_lock["promoted_observables"]["a2_over_a0"]["exact"]["exact"],
            "a4_over_a0": srg_rosetta_lock["promoted_observables"]["a4_over_a0"]["exact"]["exact"],
            "discrete_6_mode_over_a0": srg_rosetta_lock["promoted_observables"]["discrete_6_mode_over_a0"]["exact"]["exact"],
            "discrete_to_continuum_ratio": srg_rosetta_lock["promoted_observables"]["discrete_to_continuum_ratio"]["exact"]["exact"],
            "all_matches_formula": all(
                entry["matches_formula"] for entry in srg_rosetta_lock["promoted_observables"].values()
            ),
        },
        "spectral_rosetta_lock_bridge": {
            "q_from_r_plus_one": spectral_rosetta_lock["spectral_data"]["q_from_r_plus_one"],
            "phi3_from_k_plus_one": spectral_rosetta_lock["spectral_data"]["phi3_from_k_plus_one"],
            "phi6_from_one_plus_r_minus_s": spectral_rosetta_lock["spectral_data"]["phi6_from_one_plus_r_minus_s"],
            "sin2_theta_w_ew": spectral_rosetta_lock["promoted_observables"]["sin2_theta_w_ew"]["exact"]["exact"],
            "sin2_theta_12": spectral_rosetta_lock["promoted_observables"]["sin2_theta_12"]["exact"]["exact"],
            "sin2_theta_23": spectral_rosetta_lock["promoted_observables"]["sin2_theta_23"]["exact"]["exact"],
            "sin2_theta_13": spectral_rosetta_lock["promoted_observables"]["sin2_theta_13"]["exact"]["exact"],
            "omega_lambda": spectral_rosetta_lock["promoted_observables"]["omega_lambda"]["exact"]["exact"],
            "higgs_ratio_square": spectral_rosetta_lock["promoted_observables"]["higgs_ratio_square"]["exact"]["exact"],
            "a2_over_a0": spectral_rosetta_lock["promoted_observables"]["a2_over_a0"]["exact"]["exact"],
            "a4_over_a0": spectral_rosetta_lock["promoted_observables"]["a4_over_a0"]["exact"]["exact"],
            "discrete_6_mode_over_a0": spectral_rosetta_lock["promoted_observables"]["discrete_6_mode_over_a0"]["exact"]["exact"],
            "discrete_to_continuum_ratio": spectral_rosetta_lock["promoted_observables"]["discrete_to_continuum_ratio"]["exact"]["exact"],
            "all_matches_formula": all(
                entry["matches_formula"] for entry in spectral_rosetta_lock["promoted_observables"].values()
            ),
        },
        "curved_mode_projector_bridge": {
            "tower_characteristic_polynomial": curved_mode_projector["tower_characteristic_polynomial"],
            "p120": curved_mode_projector["shift_projectors"]["P_120"],
            "p6": curved_mode_projector["shift_projectors"]["P_6"],
            "p1": curved_mode_projector["shift_projectors"]["P_1"],
            "finite_einstein_hilbert_coefficient": curved_mode_projector["finite_profile"]["einstein_hilbert_coefficient"]["exact"],
            "cp2_eh_extracted": curved_mode_projector["seeds"][0]["eh_extracted_coefficient"]["exact"],
            "k3_eh_extracted": curved_mode_projector["seeds"][1]["eh_extracted_coefficient"]["exact"],
            "cp2_continuum_eh": curved_mode_projector["seeds"][0]["continuum_eh_from_rank_39_lock"]["exact"],
            "k3_continuum_eh": curved_mode_projector["seeds"][1]["continuum_eh_from_rank_39_lock"]["exact"],
            "all_projector_samples_match": all(
                sample["projected_120"]["exact"] == sample["expected_120"]["exact"]
                and sample["projected_6"]["exact"] == sample["expected_6"]["exact"]
                and sample["projected_1"]["exact"] == sample["expected_1"]["exact"]
                for seed in curved_mode_projector["seeds"]
                for sample in seed["projector_samples"]
            ),
        },
        "curved_mode_residue_bridge": {
            "generating_function_formula": curved_mode_residue["generating_function"]["formula"],
            "residue_definition": curved_mode_residue["generating_function"]["normalized_residue_definition"],
            "expected_eh": curved_mode_residue["finite_profile"]["einstein_hilbert_coefficient"]["exact"],
            "cp2_eh_from_residue": curved_mode_residue["seed_residue_data"][0]["eh_from_residue_over_six_mode"]["exact"],
            "k3_eh_from_residue": curved_mode_residue["seed_residue_data"][1]["eh_from_residue_over_six_mode"]["exact"],
            "cp2_continuum_from_residue": curved_mode_residue["seed_residue_data"][0]["continuum_eh_after_rank39_normalization"]["exact"],
            "k3_continuum_from_residue": curved_mode_residue["seed_residue_data"][1]["continuum_eh_after_rank39_normalization"]["exact"],
            "all_seed_residues_match_expected": all(
                seed["eh_from_residue_over_six_mode"]["exact"]
                == curved_mode_residue["finite_profile"]["einstein_hilbert_coefficient"]["exact"]
                and seed["continuum_eh_after_rank39_normalization"]["exact"] == "320"
                for seed in curved_mode_residue["seed_residue_data"]
            ),
        },
        "curved_continuum_extractor_bridge": {
            "discrete_eh_formula": curved_continuum_extractor["extractor_formulas"]["discrete_eh"],
            "continuum_eh_formula": curved_continuum_extractor["extractor_formulas"]["continuum_eh"],
            "topological_a2_formula": curved_continuum_extractor["extractor_formulas"]["topological_a2"],
            "expected_discrete_eh": curved_continuum_extractor["finite_profile"]["expected_discrete_eh"]["exact"],
            "expected_continuum_eh": curved_continuum_extractor["finite_profile"]["expected_continuum_eh"]["exact"],
            "cp2_step0_continuum_eh": curved_continuum_extractor["seeds"][0]["samples"][0]["continuum_eh"]["exact"],
            "k3_step0_continuum_eh": curved_continuum_extractor["seeds"][1]["samples"][0]["continuum_eh"]["exact"],
            "all_samples_match_expected": all(
                sample["discrete_eh"]["exact"] == curved_continuum_extractor["finite_profile"]["expected_discrete_eh"]["exact"]
                and sample["continuum_eh"]["exact"] == curved_continuum_extractor["finite_profile"]["expected_continuum_eh"]["exact"]
                and sample["topological_a2"]["exact"] == curved_continuum_extractor["finite_profile"]["a2"]["exact"]
                for seed in curved_continuum_extractor["seeds"]
                for sample in seed["samples"]
            ),
        },
        "curved_weinberg_lock_bridge": {
            "master_variable": curved_weinberg_lock["master_variable"]["exact"]["exact"],
            "curved_reconstruction_formula": curved_weinberg_lock["curved_reconstruction_formula"],
            "cp2_step0_reconstructed_x": curved_weinberg_lock["curved_samples"][0]["reconstructed_x"]["exact"],
            "cp2_step1_reconstructed_x": curved_weinberg_lock["curved_samples"][1]["reconstructed_x"]["exact"],
            "k3_step0_reconstructed_x": curved_weinberg_lock["curved_samples"][2]["reconstructed_x"]["exact"],
            "k3_step1_reconstructed_x": curved_weinberg_lock["curved_samples"][3]["reconstructed_x"]["exact"],
            "all_curved_samples_match_master_variable": all(
                sample["matches_master_variable"] for sample in curved_weinberg_lock["curved_samples"]
            ),
            "exceptional_formula": curved_weinberg_lock["exceptional_reconstruction"]["formula"],
            "exceptional_reconstructed_x": curved_weinberg_lock["exceptional_reconstruction"]["reconstructed_x"]["exact"],
            "exceptional_matches_master_variable": curved_weinberg_lock["exceptional_reconstruction"]["matches_master_variable"],
            "tan_theta_c": curved_weinberg_lock["promoted_observables_from_curved_x"]["tan_theta_c"]["exact"]["exact"],
            "sin2_theta_12": curved_weinberg_lock["promoted_observables_from_curved_x"]["sin2_theta_12"]["exact"]["exact"],
            "sin2_theta_23": curved_weinberg_lock["promoted_observables_from_curved_x"]["sin2_theta_23"]["exact"]["exact"],
            "sin2_theta_13": curved_weinberg_lock["promoted_observables_from_curved_x"]["sin2_theta_13"]["exact"]["exact"],
            "omega_lambda": curved_weinberg_lock["promoted_observables_from_curved_x"]["omega_lambda"]["exact"]["exact"],
            "higgs_ratio_square": curved_weinberg_lock["promoted_observables_from_curved_x"]["higgs_ratio_square"]["exact"]["exact"],
            "a2_over_a0": curved_weinberg_lock["promoted_observables_from_curved_x"]["a2_over_a0"]["exact"]["exact"],
            "a4_over_a0": curved_weinberg_lock["promoted_observables_from_curved_x"]["a4_over_a0"]["exact"]["exact"],
            "discrete_to_continuum_ratio": curved_weinberg_lock["promoted_observables_from_curved_x"]["discrete_to_continuum_ratio"]["exact"]["exact"],
            "all_promoted_observables_match_public_generator_values": all(
                entry["matches_public_generator_value"]
                for entry in curved_weinberg_lock["promoted_observables_from_curved_x"].values()
            ),
        },
        "curved_rosetta_reconstruction_bridge": {
            "master_variable": curved_rosetta_reconstruction["curved_inputs"]["master_variable"]["exact"],
            "discrete_to_continuum_ratio": curved_rosetta_reconstruction["curved_inputs"]["discrete_to_continuum_ratio"]["exact"],
            "phi6_from_topological_over_continuum": curved_rosetta_reconstruction["curved_inputs"]["phi6_from_topological_over_continuum"]["exact"],
            "vertex_count_from_topological_over_e7_fund": curved_rosetta_reconstruction["curved_inputs"]["vertex_count_from_topological_over_e7_fund"],
            "edge_count_from_discrete_over_f4": curved_rosetta_reconstruction["curved_inputs"]["edge_count_from_discrete_over_f4"],
            "k_from_two_edges_over_vertices": curved_rosetta_reconstruction["curved_inputs"]["k_from_two_edges_over_vertices"]["exact"],
            "q": curved_rosetta_reconstruction["reconstructed_cyclotomic_data"]["q"],
            "phi3": curved_rosetta_reconstruction["reconstructed_cyclotomic_data"]["phi3"]["exact"],
            "phi6": curved_rosetta_reconstruction["reconstructed_cyclotomic_data"]["phi6"]["exact"],
            "srg_data": curved_rosetta_reconstruction["reconstructed_srg_data"],
            "spectral_data": curved_rosetta_reconstruction["reconstructed_spectral_data"],
            "all_promoted_observables_match": curved_rosetta_reconstruction["matches_live_rosetta_data"]["all_promoted_observables_match"],
            "all_samples_constant": curved_rosetta_reconstruction["all_samples_constant"],
        },
        "curved_finite_spectral_reconstruction_bridge": {
            "q": curved_finite_spectral_reconstruction["reconstructed_graph_geometry"]["q"],
            "line_count": curved_finite_spectral_reconstruction["reconstructed_graph_geometry"]["line_count"],
            "edge_count": curved_finite_spectral_reconstruction["reconstructed_graph_geometry"]["edge_count"],
            "triangle_count": curved_finite_spectral_reconstruction["reconstructed_graph_geometry"]["triangle_count"],
            "tetrahedron_count": curved_finite_spectral_reconstruction["reconstructed_graph_geometry"]["tetrahedron_count"],
            "betti_numbers": curved_finite_spectral_reconstruction["reconstructed_hodge_data"]["betti_numbers"],
            "boundary_ranks": curved_finite_spectral_reconstruction["reconstructed_hodge_data"]["boundary_ranks"],
            "vertex_laplacian_spectrum": curved_finite_spectral_reconstruction["reconstructed_vertex_channels"]["vertex_laplacian_spectrum"],
            "df2_spectrum": curved_finite_spectral_reconstruction["reconstructed_finite_dirac_package"]["df2_spectrum"],
            "a0_f": curved_finite_spectral_reconstruction["reconstructed_finite_dirac_package"]["seeley_dewitt_moments"]["a0_f"],
            "a2_f": curved_finite_spectral_reconstruction["reconstructed_finite_dirac_package"]["seeley_dewitt_moments"]["a2_f"],
            "a4_f": curved_finite_spectral_reconstruction["reconstructed_finite_dirac_package"]["seeley_dewitt_moments"]["a4_f"],
            "mu_squared": curved_finite_spectral_reconstruction["reconstructed_finite_dirac_package"]["spectral_action_ratios"]["mu_squared"]["exact"],
            "lambda": curved_finite_spectral_reconstruction["reconstructed_finite_dirac_package"]["spectral_action_ratios"]["lambda"]["exact"],
            "higgs_ratio_square": curved_finite_spectral_reconstruction["reconstructed_finite_dirac_package"]["spectral_action_ratios"]["higgs_ratio_square"]["exact"],
            "df2_spectrum_match": curved_finite_spectral_reconstruction["matches_live_internal_package"]["df2_spectrum_match"],
            "moments_match": curved_finite_spectral_reconstruction["matches_live_internal_package"]["moments_match"],
            "all_samples_constant": curved_finite_spectral_reconstruction["all_samples_constant"],
        },
        "curved_roundtrip_closure_bridge": {
            "a0_f": curved_roundtrip_closure["reconstructed_finite_package"]["a0_f"],
            "a2_f": curved_roundtrip_closure["reconstructed_finite_package"]["a2_f"],
            "a4_f": curved_roundtrip_closure["reconstructed_finite_package"]["a4_f"],
            "df2_spectrum": curved_roundtrip_closure["reconstructed_finite_package"]["df2_spectrum"],
            "continuum_eh_from_finite": curved_roundtrip_closure["roundtrip_curved_coefficients"]["continuum_eh_from_finite"]["exact"],
            "discrete_eh_from_finite": curved_roundtrip_closure["roundtrip_curved_coefficients"]["discrete_eh_from_finite"]["exact"],
            "topological_from_finite": curved_roundtrip_closure["roundtrip_curved_coefficients"]["topological_from_finite"]["exact"],
            "master_variable_from_roundtrip": curved_roundtrip_closure["roundtrip_curved_coefficients"]["master_variable_from_roundtrip"]["exact"],
            "continuum_matches": curved_roundtrip_closure["matches_curved_extractor_profile"]["continuum_matches"],
            "discrete_matches": curved_roundtrip_closure["matches_curved_extractor_profile"]["discrete_matches"],
            "topological_matches": curved_roundtrip_closure["matches_curved_extractor_profile"]["topological_matches"],
            "master_variable_matches": curved_roundtrip_closure["matches_curved_extractor_profile"]["master_variable_matches"],
            "all_samples_close_exactly": curved_roundtrip_closure["all_samples_close_exactly"],
        },
        "three_sample_master_closure_bridge": {
            "minimal_seed": three_sample_master_closure["minimal_curved_data"]["seed_name"],
            "steps": three_sample_master_closure["minimal_curved_data"]["steps"],
            "discrete_eh": three_sample_master_closure["minimal_curved_data"]["discrete_eh"],
            "continuum_eh": three_sample_master_closure["minimal_curved_data"]["continuum_eh"],
            "topological_a2": three_sample_master_closure["minimal_curved_data"]["topological_a2"],
            "master_variable": three_sample_master_closure["public_generator_layer"]["master_variable"],
            "q": three_sample_master_closure["rosetta_layer"]["q"],
            "phi3": three_sample_master_closure["rosetta_layer"]["phi3"],
            "phi6": three_sample_master_closure["rosetta_layer"]["phi6"],
            "srg_data": three_sample_master_closure["rosetta_layer"]["srg_data"],
            "spectral_data": three_sample_master_closure["rosetta_layer"]["spectral_data"],
            "df2_spectrum": three_sample_master_closure["finite_spectral_layer"]["df2_spectrum"],
            "a0_f": three_sample_master_closure["finite_spectral_layer"]["a0_f"],
            "a2_f": three_sample_master_closure["finite_spectral_layer"]["a2_f"],
            "a4_f": three_sample_master_closure["finite_spectral_layer"]["a4_f"],
            "exceptional_data": three_sample_master_closure["exceptional_layer"],
            "full_master_closure": three_sample_master_closure["closure_checks"]["full_master_closure"],
        },
        "exceptional_channel_continuum_bridge": {
            "continuum_eh_coefficient": exceptional_channel_continuum["base_continuum_channel"]["continuum_eh_coefficient"],
            "continuum_equals_spinor_e6_times_cartan": exceptional_channel_continuum["base_continuum_channel"]["continuum_equals_spinor_e6_times_cartan"],
            "shared_six_l6_a2_root_support": exceptional_channel_continuum["shared_six_channel"]["l6_a2_root_support"],
            "shared_six_transport_weyl_a2_order": exceptional_channel_continuum["shared_six_channel"]["transport_weyl_a2_order"],
            "shared_six_firewall_triplet_fibers": exceptional_channel_continuum["shared_six_channel"]["firewall_triplet_fibers"],
            "shared_six_tomotope_triality_factor": exceptional_channel_continuum["shared_six_channel"]["tomotope_triality_factor"],
            "all_shared_six_channels_agree": exceptional_channel_continuum["shared_six_channel"]["all_equal_to_6"],
            "discrete_6_mode_coefficient": exceptional_channel_continuum["discrete_curvature_channel"]["discrete_6_mode_coefficient"],
            "discrete_equals_edges_times_f4": exceptional_channel_continuum["discrete_curvature_channel"]["discrete_equals_edges_times_f4"],
            "discrete_equals_spinor_e6_times_shared_six_times_f4": exceptional_channel_continuum["discrete_curvature_channel"]["discrete_equals_spinor_e6_times_shared_six_times_f4"],
            "cartan_rank_times_rank39_equals_shared_six_times_f4": exceptional_channel_continuum["discrete_curvature_channel"]["cartan_rank_times_rank39_equals_shared_six_times_f4"],
            "topological_equals_spinor_e6_times_e7_fund": exceptional_channel_continuum["topological_channel"]["topological_equals_spinor_e6_times_e7_fund"],
            "topological_equals_continuum_times_phi6": exceptional_channel_continuum["topological_channel"]["topological_equals_continuum_times_phi6"],
            "tomotope_automorphism_equals_16_times_shared_six": exceptional_channel_continuum["tomotope_triality_bridge"]["tomotope_automorphism_equals_16_times_shared_six"],
            "firewall_full_clean_quark_block_exists": exceptional_channel_continuum["transport_lie_crosscheck"]["firewall_full_clean_quark_block_exists"],
        },
        "exceptional_operator_projector_bridge": {
            "spinor_operator_dimension": exceptional_operator_projector["operator_space"]["spinor_operator_dimension"],
            "channel_ranks": exceptional_operator_projector["operator_space"]["channel_ranks"],
            "frobenius_channels_are_pairwise_orthogonal_exactly": exceptional_operator_projector["operator_space"]["frobenius_channels_are_pairwise_orthogonal_exactly"],
            "projector_traces_equal_ranks": exceptional_operator_projector["orthogonal_projectors"]["projector_traces_equal_ranks"],
            "combined_gauge_package_rank": exceptional_operator_projector["orthogonal_projectors"]["combined_gauge_package_rank"],
            "combined_rank_matches_spinor_total_rank": exceptional_operator_projector["orthogonal_projectors"]["combined_rank_matches_spinor_total_rank"],
            "e6_generation_preserving": exceptional_operator_projector["generation_channel_alignment"]["e6_generation_preserving"],
            "a2_generation_mixing_only": exceptional_operator_projector["generation_channel_alignment"]["a2_generation_mixing_only"],
            "cartan_generation_preserving": exceptional_operator_projector["generation_channel_alignment"]["cartan_generation_preserving"],
            "continuum_from_projector_ranks": exceptional_operator_projector["curved_rank_dressing"]["continuum_from_projector_ranks"],
            "discrete_from_projector_ranks_and_f4": exceptional_operator_projector["curved_rank_dressing"]["discrete_from_projector_ranks_and_f4"],
            "topological_from_projector_rank_and_e7_fund": exceptional_operator_projector["curved_rank_dressing"]["topological_from_projector_rank_and_e7_fund"],
            "tomotope_from_a2_projector_rank": exceptional_operator_projector["curved_rank_dressing"]["tomotope_from_a2_projector_rank"],
            "firewall_triplet_fibers_from_a2_projector_rank": exceptional_operator_projector["curved_rank_dressing"]["firewall_triplet_fibers_from_a2_projector_rank"],
            "continuum_matches_live_bridge": exceptional_operator_projector["curved_rank_dressing"]["continuum_matches_live_bridge"],
            "discrete_matches_live_bridge": exceptional_operator_projector["curved_rank_dressing"]["discrete_matches_live_bridge"],
            "topological_matches_live_bridge": exceptional_operator_projector["curved_rank_dressing"]["topological_matches_live_bridge"],
            "tomotope_matches_live_bridge": exceptional_operator_projector["curved_rank_dressing"]["tomotope_matches_live_bridge"],
            "firewall_matches_live_bridge": exceptional_operator_projector["curved_rank_dressing"]["firewall_matches_live_bridge"],
            "firewall_full_clean_quark_block_exists": exceptional_operator_projector["curved_rank_dressing"]["firewall_full_clean_quark_block_exists"],
        },
        "exceptional_tensor_rank_bridge": {
            "e6_projector_rank": exceptional_tensor_rank["base_ranks"]["e6_projector_rank"],
            "a2_projector_rank": exceptional_tensor_rank["base_ranks"]["a2_projector_rank"],
            "cartan_projector_rank": exceptional_tensor_rank["base_ranks"]["cartan_projector_rank"],
            "a2_transfer_block_rank": exceptional_tensor_rank["base_ranks"]["a2_transfer_block_rank"],
            "all_a2_transfer_blocks_have_rank_16": exceptional_tensor_rank["base_ranks"]["all_a2_transfer_blocks_have_rank_16"],
            "w33_edge_or_e8_root_count": exceptional_tensor_rank["tensor_rank_dictionary"]["w33_edge_or_e8_root_count"],
            "continuum_eh_coefficient": exceptional_tensor_rank["tensor_rank_dictionary"]["continuum_eh_coefficient"],
            "tomotope_automorphism_order": exceptional_tensor_rank["tensor_rank_dictionary"]["tomotope_automorphism_order"],
            "discrete_curvature_coefficient": exceptional_tensor_rank["tensor_rank_dictionary"]["discrete_curvature_coefficient"],
            "topological_coefficient": exceptional_tensor_rank["tensor_rank_dictionary"]["topological_coefficient"],
            "edge_count_equals_e6_rank_times_a2_rank": exceptional_tensor_rank["tensor_rank_dictionary"]["edge_count_equals_e6_rank_times_a2_rank"],
            "continuum_equals_e6_rank_times_cartan_rank": exceptional_tensor_rank["tensor_rank_dictionary"]["continuum_equals_e6_rank_times_cartan_rank"],
            "tomotope_equals_a2_rank_times_a2_block_rank": exceptional_tensor_rank["tensor_rank_dictionary"]["tomotope_equals_a2_rank_times_a2_block_rank"],
            "discrete_equals_edge_count_times_f4": exceptional_tensor_rank["tensor_rank_dictionary"]["discrete_equals_edge_count_times_f4"],
            "topological_equals_e6_rank_times_e7_fund": exceptional_tensor_rank["tensor_rank_dictionary"]["topological_equals_e6_rank_times_e7_fund"],
            "all_promoted_exceptional_counts_match": all(
                exceptional_tensor_rank["promoted_exceptional_lock"].values()
            ),
        },
        "exceptional_residue_bridge": {
            "e6_projector_rank": exceptional_residue["internal_exceptional_data"]["e6_projector_rank"],
            "a2_projector_rank": exceptional_residue["internal_exceptional_data"]["a2_projector_rank"],
            "cartan_projector_rank": exceptional_residue["internal_exceptional_data"]["cartan_projector_rank"],
            "edge_or_e8_root_count": exceptional_residue["internal_exceptional_data"]["edge_or_e8_root_count"],
            "discrete_curvature_from_6_pole": exceptional_residue["pole_dictionary"]["discrete_curvature_from_6_pole"],
            "continuum_eh_from_rank39_normalized_6_pole": exceptional_residue["pole_dictionary"]["continuum_eh_from_rank39_normalized_6_pole"],
            "topological_from_1_pole": exceptional_residue["pole_dictionary"]["topological_from_1_pole"],
            "discrete_equals_e6_times_a2_times_f4": exceptional_residue["pole_dictionary"]["discrete_equals_e6_times_a2_times_f4"],
            "discrete_equals_edges_times_f4": exceptional_residue["pole_dictionary"]["discrete_equals_edges_times_f4"],
            "continuum_equals_e6_times_cartan": exceptional_residue["pole_dictionary"]["continuum_equals_e6_times_cartan"],
            "topological_equals_e6_times_e7_fund": exceptional_residue["pole_dictionary"]["topological_equals_e6_times_e7_fund"],
            "all_seed_checks_pass": exceptional_residue["all_seed_checks_pass"],
        },
        "d4_f4_tomotope_reye_bridge": {
            "weyl_d4_order": d4_f4_tomotope_reye["d4_lock"]["weyl_d4_order"],
            "tomotope_flag_count": d4_f4_tomotope_reye["d4_lock"]["tomotope_flag_count"],
            "tomotope_automorphism_order": d4_f4_tomotope_reye["d4_lock"]["tomotope_automorphism_order"],
            "weyl_d4_equals_tomotope_flags": d4_f4_tomotope_reye["d4_lock"]["weyl_d4_equals_tomotope_flags"],
            "weyl_d4_equals_2_times_tomotope_automorphism": d4_f4_tomotope_reye["d4_lock"]["weyl_d4_equals_2_times_tomotope_automorphism"],
            "aut_q8_order": d4_f4_tomotope_reye["q8_to_24cell_bridge"]["aut_q8_order"],
            "d4_root_count": d4_f4_tomotope_reye["q8_to_24cell_bridge"]["d4_root_count"],
            "twenty_four_cell_vertex_count": d4_f4_tomotope_reye["q8_to_24cell_bridge"]["twenty_four_cell_vertex_count"],
            "aut_q8_equals_d4_root_count": d4_f4_tomotope_reye["q8_to_24cell_bridge"]["aut_q8_equals_d4_root_count"],
            "d4_root_count_equals_24cell_vertices": d4_f4_tomotope_reye["q8_to_24cell_bridge"]["d4_root_count_equals_24cell_vertices"],
            "reye_points": d4_f4_tomotope_reye["reye_shadow"]["reye_points"],
            "reye_lines": d4_f4_tomotope_reye["reye_shadow"]["reye_lines"],
            "twenty_four_cell_axes": d4_f4_tomotope_reye["reye_shadow"]["twenty_four_cell_axes"],
            "twenty_four_cell_hexagon_shadow_count": d4_f4_tomotope_reye["reye_shadow"]["twenty_four_cell_hexagon_shadow_count"],
            "all_twelve_counts_agree": d4_f4_tomotope_reye["reye_shadow"]["all_twelve_counts_agree"],
            "all_sixteen_counts_agree": d4_f4_tomotope_reye["reye_shadow"]["all_sixteen_counts_agree"],
            "outer_d4_order": d4_f4_tomotope_reye["f4_triality_lift"]["outer_d4_order"],
            "weyl_f4_order": d4_f4_tomotope_reye["f4_triality_lift"]["weyl_f4_order"],
            "twenty_four_cell_rotational_symmetry_order": d4_f4_tomotope_reye["f4_triality_lift"]["twenty_four_cell_rotational_symmetry_order"],
            "weyl_f4_equals_triality_times_weyl_d4": d4_f4_tomotope_reye["f4_triality_lift"]["weyl_f4_equals_triality_times_weyl_d4"],
            "weyl_f4_equals_triality_times_tomotope_flags": d4_f4_tomotope_reye["f4_triality_lift"]["weyl_f4_equals_triality_times_tomotope_flags"],
            "weyl_f4_equals_twelve_times_tomotope_automorphism": d4_f4_tomotope_reye["f4_triality_lift"]["weyl_f4_equals_twelve_times_tomotope_automorphism"],
            "rotational_24_equals_triality_times_tomotope_automorphism": d4_f4_tomotope_reye["f4_triality_lift"]["rotational_24_equals_triality_times_tomotope_automorphism"],
            "weyl_f4_equals_2_times_rotational_24": d4_f4_tomotope_reye["f4_triality_lift"]["weyl_f4_equals_2_times_rotational_24"],
        },
        "triality_ladder_algebra_bridge": {
            "q8_vertex_block": triality_ladder_algebra["triality_ladder"]["q8_d4_24cell_vertex_block"]["value"],
            "tomotope_aut_block": triality_ladder_algebra["triality_ladder"]["tomotope_aut_block"]["value"],
            "d4_weyl_flag_block": triality_ladder_algebra["triality_ladder"]["d4_weyl_flag_block"]["value"],
            "rotational_24cell_block": triality_ladder_algebra["triality_ladder"]["rotational_24cell_block"]["value"],
            "f4_weyl_block": triality_ladder_algebra["triality_ladder"]["f4_weyl_block"]["value"],
            "e6_weyl_closure": triality_ladder_algebra["triality_ladder"]["e6_weyl_closure"]["value"],
            "tomotope_equals_a2_rank_times_block_rank": triality_ladder_algebra["triality_ladder"]["tomotope_aut_block"]["equals_a2_rank_times_a2_block_rank"],
            "d4_equals_d4_roots_times_cartan_rank": triality_ladder_algebra["triality_ladder"]["d4_weyl_flag_block"]["equals_d4_roots_times_cartan_rank"],
            "rotational_24_equals_e6_root_support_times_cartan_rank": triality_ladder_algebra["triality_ladder"]["rotational_24cell_block"]["equals_e6_root_support_times_cartan_rank"],
            "f4_equals_e6_root_support_times_block_rank": triality_ladder_algebra["triality_ladder"]["f4_weyl_block"]["equals_e6_root_support_times_a2_block_rank"],
            "we6_equals_tritangents_times_wf4": triality_ladder_algebra["triality_ladder"]["e6_weyl_closure"]["equals_tritangents_times_wf4"],
            "we6_equals_directed_transport_edges_times_wd4": triality_ladder_algebra["triality_ladder"]["e6_weyl_closure"]["equals_directed_transport_edges_times_wd4"],
            "we6_equals_e6_root_support_times_transport_edges": triality_ladder_algebra["triality_ladder"]["e6_weyl_closure"]["equals_e6_root_support_times_transport_edges"],
            "tritangents": triality_ladder_algebra["triality_ladder"]["e6_weyl_closure"]["tritangents"],
            "directed_transport_edges": triality_ladder_algebra["triality_ladder"]["e6_weyl_closure"]["directed_transport_edges"],
            "transport_edges": triality_ladder_algebra["triality_ladder"]["e6_weyl_closure"]["transport_edges"],
        },
        "curved_inverse_rosetta_bridge": {
            "w33_vertex_count": curved_inverse_rosetta["reconstructed_internal_data"]["w33_vertex_count"],
            "w33_edge_or_e8_root_count": curved_inverse_rosetta["reconstructed_internal_data"]["w33_edge_or_e8_root_count"],
            "spinor_cartan_rank": curved_inverse_rosetta["reconstructed_internal_data"]["spinor_cartan_rank"],
            "shared_six_channel": curved_inverse_rosetta["reconstructed_internal_data"]["shared_six_channel"],
            "tomotope_automorphism_order": curved_inverse_rosetta["reconstructed_internal_data"]["tomotope_automorphism_order"],
            "vertex_count_matches": curved_inverse_rosetta["matches_live_internal_data"]["vertex_count_matches"],
            "edge_count_matches": curved_inverse_rosetta["matches_live_internal_data"]["edge_count_matches"],
            "cartan_rank_matches": curved_inverse_rosetta["matches_live_internal_data"]["cartan_rank_matches"],
            "shared_six_matches": curved_inverse_rosetta["matches_live_internal_data"]["shared_six_matches"],
            "tomotope_aut_matches": curved_inverse_rosetta["matches_live_internal_data"]["tomotope_aut_matches"],
            "all_samples_constant": curved_inverse_rosetta["all_samples_constant"],
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
        "transport_path_groupoid_bridge": {
            "objects": transport_path_groupoid["path_groupoid"]["objects"],
            "directed_generators": transport_path_groupoid["path_groupoid"]["directed_generating_morphisms"],
            "tree_edges": transport_path_groupoid["spanning_tree_gauge"]["tree_edges"],
            "fundamental_cycles": transport_path_groupoid["spanning_tree_gauge"]["fundamental_cycles"],
            "tree_edges_gauge_trivialized": transport_path_groupoid["spanning_tree_gauge"]["all_tree_edges_gauge_trivialized"],
            "fundamental_cycle_holonomy_group_order": transport_path_groupoid["spanning_tree_gauge"]["fundamental_cycle_holonomy_group_order"],
            "real_flat_section_dimension": transport_path_groupoid["real_local_system"]["common_fixed_subspace_dimension"],
            "ternary_flat_section_dimension": transport_path_groupoid["ternary_reduction"]["common_fixed_subspace_dimension"],
            "ternary_invariant_line": transport_path_groupoid["ternary_reduction"]["unique_invariant_projective_line"],
            "ternary_quotient_character_values": transport_path_groupoid["ternary_reduction"]["quotient_character_values"],
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
        "ternary_homological_code_bridge": {
            "field": ternary_homological_code["ternary_css_code"]["field"],
            "physical_qutrits": ternary_homological_code["ternary_css_code"]["physical_qutrits"],
            "x_check_rank": ternary_homological_code["ternary_css_code"]["x_check_rank"],
            "z_check_rank": ternary_homological_code["ternary_css_code"]["z_check_rank"],
            "logical_qutrits": ternary_homological_code["ternary_css_code"]["logical_qutrits"],
            "stabilizer_rank_total": ternary_homological_code["ternary_css_code"]["stabilizer_rank_total"],
            "primal_logical_distance": ternary_homological_code["homological_distance"]["primal_logical_distance"],
            "weight_four_witness_cycle": ternary_homological_code["homological_distance"]["witness_cycle_vertices"],
        },
        "transport_ternary_line_bridge": {
            "real_flat_section_dimension": transport_ternary_line["transport_side"]["real_flat_section_dimension"],
            "ternary_flat_section_dimension": transport_ternary_line["transport_side"]["ternary_flat_section_dimension"],
            "invariant_line": transport_ternary_line["transport_side"]["invariant_line"],
            "logical_qutrits": transport_ternary_line["matter_side"]["logical_qutrits"],
            "canonical_transport_stable_sector_dimension": transport_ternary_line["matter_side"]["canonical_transport_stable_sector_dimension"],
            "matter_flavour_dimension": transport_ternary_line["combined_sector"]["matter_flavour_dimension"],
            "matches_flat_internal_dimension_exactly": transport_ternary_line["combined_sector"]["matches_flat_internal_dimension_exactly"],
        },
        "transport_ternary_extension_bridge": {
            "field": transport_ternary_extension["reduced_transport_module"]["field"],
            "holonomy_group_order": transport_ternary_extension["reduced_transport_module"]["holonomy_group_order"],
            "unique_invariant_line": transport_ternary_extension["reduced_transport_module"]["unique_invariant_line"],
            "invariant_complement_count": transport_ternary_extension["reduced_transport_module"]["invariant_complement_count"],
            "top_character_values": transport_ternary_extension["reduced_transport_module"]["top_character_values"],
            "quotient_character_values": transport_ternary_extension["reduced_transport_module"]["quotient_character_values"],
            "nonsplit_extension_witness_count": transport_ternary_extension["reduced_transport_module"]["nonsplit_extension_witness_count"],
            "is_nonsplit_extension_of_sign_by_trivial": transport_ternary_extension["reduced_transport_module"]["is_nonsplit_extension_of_sign_by_trivial"],
            "base_logical_qutrits": transport_ternary_extension["matter_flavour_extension"]["base_logical_qutrits"],
            "short_exact_sequence_dimensions": transport_ternary_extension["matter_flavour_extension"]["short_exact_sequence_dimensions"],
            "matches_flat_internal_dimension_exactly": transport_ternary_extension["matter_flavour_extension"]["matches_flat_internal_dimension_exactly"],
        },
        "transport_ternary_cocycle_bridge": {
            "field": transport_ternary_cocycle["extension_cocycle"]["field"],
            "adapted_group_order": transport_ternary_cocycle["extension_cocycle"]["adapted_group_order"],
            "twisted_cocycle_identity_exact": transport_ternary_cocycle["extension_cocycle"]["twisted_cocycle_identity_exact"],
            "cocycle_values_on_sign_trivial_subgroup": transport_ternary_cocycle["extension_cocycle"]["cocycle_values_on_sign_trivial_subgroup"],
            "cocycle_is_not_a_coboundary": transport_ternary_cocycle["extension_cocycle"]["cocycle_is_not_a_coboundary"],
            "fiber_shift_rank": transport_ternary_cocycle["fiber_nilpotent_operator"]["rank"],
            "fiber_shift_square_zero": transport_ternary_cocycle["fiber_nilpotent_operator"]["square_zero"],
            "matter_operator_dimension": transport_ternary_cocycle["matter_extension_operator"]["dimension"],
            "matter_operator_rank": transport_ternary_cocycle["matter_extension_operator"]["rank"],
            "matter_operator_square_zero": transport_ternary_cocycle["matter_extension_operator"]["square_zero"],
            "matter_operator_image_equals_kernel": transport_ternary_cocycle["matter_extension_operator"]["image_equals_kernel"],
        },
        "transport_curvature_bridge": {
            "triangles": transport_curvature["transport_triangle_curvature"]["triangles"],
            "all_six_reduced_holonomy_classes_realized": transport_curvature["transport_triangle_curvature"]["all_six_reduced_holonomy_classes_realized"],
            "curvature_rank_counts": transport_curvature["transport_triangle_curvature"]["curvature_rank_counts"],
            "curvature_vanishes_exactly_on_identity_holonomy_triangles": transport_curvature["transport_triangle_curvature"]["curvature_vanishes_exactly_on_identity_holonomy_triangles"],
            "global_curvature_operator_rank": transport_curvature["global_curvature_operator"]["rank"],
            "global_curvature_operator_nullity": transport_curvature["global_curvature_operator"]["nullity"],
        },
        "transport_borel_factor_bridge": {
            "group_order": transport_borel["reduced_borel_group"]["group_order"],
            "parity0_total": transport_borel["triangle_channel_split"]["parity0_total"],
            "parity1_total": transport_borel["triangle_channel_split"]["parity1_total"],
            "flat_total": transport_borel["triangle_channel_split"]["flat_total"],
            "pure_nilpotent_total": transport_borel["triangle_channel_split"]["pure_nilpotent_total"],
            "semisimple_curved_total": transport_borel["triangle_channel_split"]["semisimple_curved_total"],
            "parity0_splits_as_flat_plus_pure_nilpotent": transport_borel["triangle_channel_split"]["parity0_splits_as_flat_plus_pure_nilpotent"],
        },
        "transport_twisted_precomplex_bridge": {
            "c0_dimension": transport_twisted_precomplex["cochain_dimensions"]["c0_dimension"],
            "c1_dimension": transport_twisted_precomplex["cochain_dimensions"]["c1_dimension"],
            "c2_dimension": transport_twisted_precomplex["cochain_dimensions"]["c2_dimension"],
            "d0_rank": transport_twisted_precomplex["adapted_block_decomposition"]["full_d0_rank"],
            "d1_rank": transport_twisted_precomplex["adapted_block_decomposition"]["full_d1_rank"],
            "d0_lower_left_block_vanishes": transport_twisted_precomplex["adapted_block_decomposition"]["d0_lower_left_block_vanishes"],
            "d1_lower_left_block_vanishes": transport_twisted_precomplex["adapted_block_decomposition"]["d1_lower_left_block_vanishes"],
            "trivial_h0_dimension": transport_twisted_precomplex["invariant_line_subcomplex"]["h0_dimension"],
            "trivial_h1_dimension": transport_twisted_precomplex["invariant_line_subcomplex"]["h1_dimension"],
            "sign_h0_flat_dimension": transport_twisted_precomplex["sign_shadow_precomplex"]["h0_flat_dimension"],
            "semisimple_curvature_rank": transport_twisted_precomplex["sign_shadow_precomplex"]["semisimple_curvature_rank"],
            "semisimple_curvature_support_triangles": transport_twisted_precomplex["sign_shadow_precomplex"]["semisimple_curvature_support_triangles"],
            "semisimple_curvature_support_equals_parity1_triangles": transport_twisted_precomplex["sign_shadow_precomplex"]["semisimple_curvature_support_equals_parity1_triangles"],
            "full_curvature_rank": transport_twisted_precomplex["curved_extension_package"]["full_curvature_rank"],
            "off_diagonal_curvature_rank": transport_twisted_precomplex["curved_extension_package"]["off_diagonal_curvature_rank"],
            "curvature_factors_through_sign_quotient": transport_twisted_precomplex["curved_extension_package"]["curvature_factors_through_sign_quotient"],
            "upper_right_curvature_identity_exact": transport_twisted_precomplex["curved_extension_package"]["upper_right_curvature_identity_exact"],
        },
        "transport_matter_curved_harmonic_bridge": {
            "logical_qutrits": transport_matter_curved["matter_coupled_precomplex"]["logical_qutrits"],
            "matter_extension_dimension": transport_matter_curved["matter_coupled_precomplex"]["matter_extension_dimension"],
            "coupled_c0_dimension": transport_matter_curved["matter_coupled_precomplex"]["coupled_c0_dimension"],
            "coupled_c1_dimension": transport_matter_curved["matter_coupled_precomplex"]["coupled_c1_dimension"],
            "coupled_c2_dimension": transport_matter_curved["matter_coupled_precomplex"]["coupled_c2_dimension"],
            "protected_flat_h0_dimension": transport_matter_curved["matter_coupled_precomplex"]["protected_flat_h0_dimension"],
            "full_curvature_rank": transport_matter_curved["matter_coupled_precomplex"]["full_curvature_rank"],
            "off_diagonal_curvature_rank": transport_matter_curved["matter_coupled_precomplex"]["off_diagonal_curvature_rank"],
            "cp2_protected_flat_matter_zero_modes": transport_matter_curved["curved_external_harmonic_channels"][0]["protected_flat_matter_zero_modes"],
            "k3_protected_flat_matter_zero_modes": transport_matter_curved["curved_external_harmonic_channels"][1]["protected_flat_matter_zero_modes"],
            "cp2_curvature_rank_on_harmonics": transport_matter_curved["curved_external_harmonic_channels"][0]["matter_curvature_rank_on_external_harmonics"],
            "k3_curvature_rank_on_harmonics": transport_matter_curved["curved_external_harmonic_channels"][1]["matter_curvature_rank_on_external_harmonics"],
            "protected_flat_sector_is_exactly_one_81_copy": transport_matter_curved["matter_coupled_precomplex"]["protected_flat_sector_is_exactly_one_81_copy"],
        },
        "transport_spectral_selector_bridge": {
            "w33_rank_mod_3": transport_spectral_selector["w33_base_selector"]["rank_mod_3"],
            "w33_kernel_dimension_mod_3": transport_spectral_selector["w33_base_selector"]["kernel_dimension_mod_3"],
            "w33_all_ones_spans_mod_3_kernel": transport_spectral_selector["w33_base_selector"]["all_ones_spans_mod_3_kernel"],
            "transport_projector_rank": transport_spectral_selector["transport_selector"]["projector_rank"],
            "transport_walk_gap_exact": transport_spectral_selector["transport_selector"]["spectral_gap"]["exact"],
            "transport_kemeny_exact": transport_spectral_selector["transport_selector"]["kemeny_constant"]["exact"],
            "a2_positive_laplacian_gap": transport_spectral_selector["dynamic_selection_bridge"]["a2_positive_laplacian_gap"],
            "protected_flat_selector_rank_after_tensoring": transport_spectral_selector["dynamic_selection_bridge"]["protected_flat_selector_rank_after_tensoring"],
            "matches_protected_flat_matter_dimension": transport_spectral_selector["dynamic_selection_bridge"]["matches_protected_flat_matter_dimension"],
            "protected_flat_curved_harmonic_lifts": transport_spectral_selector["dynamic_selection_bridge"]["protected_flat_curved_harmonic_lifts"],
        },
        "transport_curved_dirac_refinement_bridge": {
            "transport_dirac_dimension": transport_curved_dirac_refinement["transport_curved_dirac"]["total_dimension"],
            "transport_trace_d_squared": transport_curved_dirac_refinement["transport_curved_dirac"]["trace_d_squared"],
            "transport_curvature_corner_rank": transport_curved_dirac_refinement["transport_curved_dirac"]["curvature_corner_rank"],
            "matter_dirac_dimension": transport_curved_dirac_refinement["matter_coupled_curved_dirac"]["total_dimension"],
            "matter_trace_d_squared": transport_curved_dirac_refinement["matter_coupled_curved_dirac"]["trace_d_squared"],
            "protected_flat_subsector_dimension": transport_curved_dirac_refinement["matter_coupled_curved_dirac"]["protected_flat_subsector_dimension"],
            "transport_constant_limit": transport_curved_dirac_refinement["curved_refinement_first_order_bridge"]["transport"][0]["constant_term_formula"]["limit"]["exact"],
            "transport_linear_limit": transport_curved_dirac_refinement["curved_refinement_first_order_bridge"]["transport"][0]["linear_term_formula"]["limit"]["exact"],
            "matter_constant_limit": transport_curved_dirac_refinement["curved_refinement_first_order_bridge"]["matter_coupled"][0]["constant_term_formula"]["limit"]["exact"],
            "matter_linear_limit": transport_curved_dirac_refinement["curved_refinement_first_order_bridge"]["matter_coupled"][0]["linear_term_formula"]["limit"]["exact"],
            "cp2_transport_step0_constant": transport_curved_dirac_refinement["curved_refinement_first_order_bridge"]["transport"][0]["samples"][0]["constant_term"]["exact"],
            "k3_matter_step0_linear": transport_curved_dirac_refinement["curved_refinement_first_order_bridge"]["matter_coupled"][1]["samples"][0]["linear_term"]["exact"],
        },
        "transport_curved_dirac_quadratic_bridge": {
            "transport_trace_d_fourth": transport_curved_dirac_quadratic["internal_profiles"][0]["trace_d_fourth"],
            "matter_trace_d_fourth": transport_curved_dirac_quadratic["internal_profiles"][1]["trace_d_fourth"],
            "cp2_transport_seed_quadratic": transport_curved_dirac_quadratic["transport_seed_profiles"][0]["quadratic_density_coefficient"]["exact"],
            "k3_transport_seed_quadratic": transport_curved_dirac_quadratic["transport_seed_profiles"][1]["quadratic_density_coefficient"]["exact"],
            "cp2_transport_sd1_quadratic": transport_curved_dirac_quadratic["transport_sd1_profiles"][0]["quadratic_density_coefficient"]["exact"],
            "k3_transport_sd1_quadratic": transport_curved_dirac_quadratic["transport_sd1_profiles"][1]["quadratic_density_coefficient"]["exact"],
            "cp2_matter_seed_quadratic": transport_curved_dirac_quadratic["matter_seed_profiles"][0]["quadratic_density_coefficient"]["exact"],
            "k3_matter_sd1_quadratic": transport_curved_dirac_quadratic["matter_sd1_profiles"][1]["quadratic_density_coefficient"]["exact"],
            "transport_first_refinement_contracts_gap": transport_curved_dirac_quadratic["quadratic_gap_theorem"]["transport_first_refinement_contracts_gap"],
            "matter_first_refinement_contracts_gap": transport_curved_dirac_quadratic["quadratic_gap_theorem"]["matter_first_refinement_contracts_gap"],
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
        "curved_h2_host_bridge": {
            "cp2_h2_dimension": curved_h2_host["seed_profiles"][0]["h2_dimension"],
            "cp2_b2_plus": curved_h2_host["seed_profiles"][0]["b2_plus"],
            "cp2_b2_minus": curved_h2_host["seed_profiles"][0]["b2_minus"],
            "cp2_rank2_h2_branch_available": curved_h2_host["seed_profiles"][0]["rank2_h2_branch_available"],
            "k3_h2_dimension": curved_h2_host["seed_profiles"][1]["h2_dimension"],
            "k3_b2_plus": curved_h2_host["seed_profiles"][1]["b2_plus"],
            "k3_b2_minus": curved_h2_host["seed_profiles"][1]["b2_minus"],
            "k3_rank2_h2_branch_available": curved_h2_host["seed_profiles"][1]["rank2_h2_branch_available"],
            "k3_mixed_sign_h2_plane_available": curved_h2_host["seed_profiles"][1]["mixed_sign_h2_plane_available"],
            "cp2_six_mode": curved_h2_host["seed_profiles"][0]["six_mode"]["exact"],
            "k3_six_mode": curved_h2_host["seed_profiles"][1]["six_mode"]["exact"],
            "six_mode_sign_matches_signature_on_both_explicit_seeds": (
                curved_h2_host["bridge_constraints"]["six_mode_sign_matches_signature_on_both_explicit_seeds"]
            ),
            "first_explicit_rank2_h2_host_is_k3": curved_h2_host["bridge_constraints"]["first_explicit_rank2_h2_host_is_k3"],
        },
        "curved_h2_qutrit_bridge": {
            "logical_qutrits": curved_h2_qutrit["bridge_constraints"]["logical_qutrits"],
            "cp2_middle_degree_qutrit_channel": curved_h2_qutrit["bridge_constraints"]["cp2_middle_degree_qutrit_channel"],
            "k3_middle_degree_qutrit_channel": curved_h2_qutrit["bridge_constraints"]["k3_middle_degree_qutrit_channel"],
            "k3_minus_cp2_middle_degree_gap": curved_h2_qutrit["bridge_constraints"]["k3_minus_cp2_middle_degree_gap"],
            "k3_positive_middle_degree_qutrit_channel": (
                curved_h2_qutrit["seed_profiles"][1]["positive_middle_degree_qutrit_channel"]
            ),
            "k3_negative_middle_degree_qutrit_channel": (
                curved_h2_qutrit["seed_profiles"][1]["negative_middle_degree_qutrit_channel"]
            ),
            "cp2_is_not_rank2_middle_degree_host": (
                curved_h2_qutrit["bridge_constraints"]["cp2_is_not_rank2_middle_degree_host"]
            ),
            "k3_is_rank2_middle_degree_host": curved_h2_qutrit["bridge_constraints"]["k3_is_rank2_middle_degree_host"],
            "k3_has_both_middle_degree_sign_channels": (
                curved_h2_qutrit["bridge_constraints"]["k3_has_both_middle_degree_sign_channels"]
            ),
            "first_exact_middle_degree_qutrit_host_is_k3": (
                curved_h2_qutrit["bridge_constraints"]["first_exact_middle_degree_qutrit_host_is_k3"]
            ),
        },
        "curved_harmonic_qutrit_split_bridge": {
            "logical_qutrits": curved_harmonic_qutrit_split["bridge_constraints"]["logical_qutrits"],
            "universal_endpoint_qutrit_channel": (
                curved_harmonic_qutrit_split["bridge_constraints"]["universal_endpoint_qutrit_channel"]
            ),
            "endpoint_qutrit_channel_matches_on_all_explicit_seeds": (
                curved_harmonic_qutrit_split["bridge_constraints"]["endpoint_qutrit_channel_matches_on_all_explicit_seeds"]
            ),
            "cp2_total_harmonic_qutrit_channel": (
                curved_harmonic_qutrit_split["bridge_constraints"]["cp2_total_harmonic_qutrit_channel"]
            ),
            "k3_total_harmonic_qutrit_channel": (
                curved_harmonic_qutrit_split["bridge_constraints"]["k3_total_harmonic_qutrit_channel"]
            ),
            "cp2_middle_degree_qutrit_channel": (
                curved_harmonic_qutrit_split["bridge_constraints"]["cp2_middle_degree_qutrit_channel"]
            ),
            "k3_middle_degree_qutrit_channel": (
                curved_harmonic_qutrit_split["bridge_constraints"]["k3_middle_degree_qutrit_channel"]
            ),
            "all_seed_dependence_is_middle_degree": (
                curved_harmonic_qutrit_split["bridge_constraints"]["all_seed_dependence_is_middle_degree"]
            ),
            "k3_minus_cp2_total_harmonic_gap": (
                curved_harmonic_qutrit_split["bridge_constraints"]["k3_minus_cp2_total_harmonic_gap"]
            ),
            "k3_minus_cp2_middle_degree_gap": (
                curved_harmonic_qutrit_split["bridge_constraints"]["k3_minus_cp2_middle_degree_gap"]
            ),
        },
        "curved_h2_cup_plane_bridge": {
            "cp2_cup_signature": curved_h2_cup_plane["bridge_constraints"]["cp2_h2_signature_from_cup_form"],
            "k3_cup_signature": curved_h2_cup_plane["bridge_constraints"]["k3_h2_signature_from_cup_form"],
            "k3_positive_h2_directions_from_cup_form": (
                curved_h2_cup_plane["bridge_constraints"]["k3_positive_h2_directions_from_cup_form"]
            ),
            "k3_negative_h2_directions_from_cup_form": (
                curved_h2_cup_plane["bridge_constraints"]["k3_negative_h2_directions_from_cup_form"]
            ),
            "k3_canonical_mixed_plane_selector_triangle": (
                curved_h2_cup_plane["k3_canonical_mixed_plane"]["selector_triangle"]
            ),
            "k3_canonical_mixed_plane_split": (
                curved_h2_cup_plane["k3_canonical_mixed_plane"]["qutrit_lift_split"]
            ),
            "k3_canonical_mixed_plane_is_split": (
                curved_h2_cup_plane["k3_canonical_mixed_plane"]["split_qutrit_package"]
            ),
            "canonical_k3_mixed_plane_has_nonzero_intersection_determinant": (
                curved_h2_cup_plane["bridge_constraints"][
                    "canonical_k3_mixed_plane_has_nonzero_intersection_determinant"
                ]
            ),
        },
        "k3_rank2_qutrit_plane_bridge": {
            "minimal_rank2_qutrit_branch_dimension": (
                k3_rank2_qutrit_plane["bridge_constraints"]["minimal_rank2_qutrit_branch_dimension"]
            ),
            "mixed_rank2_qutrit_split": (
                k3_rank2_qutrit_plane["bridge_constraints"]["mixed_rank2_qutrit_split"]
            ),
            "k3_supports_positive_rank2_plane": (
                k3_rank2_qutrit_plane["bridge_constraints"]["k3_supports_positive_rank2_plane"]
            ),
            "k3_supports_mixed_rank2_plane": (
                k3_rank2_qutrit_plane["bridge_constraints"]["k3_supports_mixed_rank2_plane"]
            ),
            "k3_supports_negative_rank2_plane": (
                k3_rank2_qutrit_plane["bridge_constraints"]["k3_supports_negative_rank2_plane"]
            ),
            "minimal_rank2_branch_matches_transport_extension_size": (
                k3_rank2_qutrit_plane["bridge_constraints"]["minimal_rank2_branch_matches_transport_extension_size"]
            ),
        },
        "transport_mixed_plane_obstruction_bridge": {
            "dimension_pattern_matches_exactly": (
                transport_mixed_plane_obstruction["comparison_theorem"]["dimension_pattern_matches_exactly"]
            ),
            "internal_transport_162_is_nonsplit": (
                transport_mixed_plane_obstruction["comparison_theorem"]["internal_transport_162_is_nonsplit"]
            ),
            "external_mixed_plane_162_is_split": (
                transport_mixed_plane_obstruction["comparison_theorem"]["external_mixed_plane_162_is_split"]
            ),
            "exact_split_vs_nonsplit_obstruction_is_present": (
                transport_mixed_plane_obstruction["comparison_theorem"][
                    "exact_split_vs_nonsplit_obstruction_is_present"
                ]
            ),
            "exact_identification_between_current_structures_is_supported": (
                transport_mixed_plane_obstruction["comparison_theorem"][
                    "exact_identification_between_current_structures_is_supported"
                ]
            ),
        },
        "k3_mixed_plane_a4_projection_bridge": {
            "branch_dimension_is_162": (
                k3_mixed_plane_a4_projection["projection_theorem"]["branch_dimension_is_162"]
            ),
            "finite_trace_multiplier_is_81": (
                k3_mixed_plane_a4_projection["projection_theorem"]["finite_trace_multiplier_is_81"]
            ),
            "branch_dimension_equals_2_times_trace_multiplier": (
                k3_mixed_plane_a4_projection["projection_theorem"][
                    "branch_dimension_equals_2_times_trace_multiplier"
                ]
            ),
            "factor_of_two_is_exact_rank2_external_factor": (
                k3_mixed_plane_a4_projection["projection_theorem"][
                    "factor_of_two_is_exact_rank2_external_factor"
                ]
            ),
            "eightyone_vs_one_sixtytwo_is_dimension_vs_trace_split": (
                k3_mixed_plane_a4_projection["projection_theorem"][
                    "eightyone_vs_one_sixtytwo_is_dimension_vs_trace_split"
                ]
            ),
            "projecting_to_canonical_mixed_plane_does_not_promote_multiplier_to_162": (
                k3_mixed_plane_a4_projection["projection_theorem"][
                    "projecting_to_canonical_mixed_plane_does_not_promote_multiplier_to_162"
                ]
            ),
        },
        "k3_refined_plane_persistence_bridge": {
            "first_refinement_scale_factor": (
                k3_refined_plane_persistence["first_refinement_scale_factor"]
            ),
            "first_barycentric_pullback_scales_restricted_form_by_120": (
                k3_refined_plane_persistence["refinement_theorem"][
                    "first_barycentric_pullback_scales_restricted_form_by_120"
                ]
            ),
            "restricted_determinant_scales_by_120_squared": (
                k3_refined_plane_persistence["refinement_theorem"][
                    "restricted_determinant_scales_by_120_squared"
                ]
            ),
            "normalized_restricted_form_is_refinement_invariant": (
                k3_refined_plane_persistence["refinement_theorem"][
                    "normalized_restricted_form_is_refinement_invariant"
                ]
            ),
            "mixed_signature_survives_first_refinement": (
                k3_refined_plane_persistence["refinement_theorem"][
                    "mixed_signature_survives_first_refinement"
                ]
            ),
        },
        "k3_integral_h2_lattice_bridge": {
            "h2_rank": k3_integral_h2_lattice["integral_lattice_profile"]["h2_rank"],
            "cocycle_rank": k3_integral_h2_lattice["integral_lattice_profile"]["cocycle_rank"],
            "exact_rank": k3_integral_h2_lattice["integral_lattice_profile"]["exact_rank"],
            "determinant": k3_integral_h2_lattice["integral_lattice_profile"]["determinant"],
            "positive_directions": (
                k3_integral_h2_lattice["integral_lattice_profile"]["positive_directions"]
            ),
            "negative_directions": (
                k3_integral_h2_lattice["integral_lattice_profile"]["negative_directions"]
            ),
            "diagonal_even": k3_integral_h2_lattice["integral_lattice_profile"]["diagonal_even"],
            "unimodular": k3_integral_h2_lattice["integral_lattice_profile"]["unimodular"],
            "primitive_plane_gram_matrix": (
                k3_integral_h2_lattice["primitive_hyperbolic_plane"]["gram_matrix"]
            ),
            "primitive_plane_minor_gcd": (
                k3_integral_h2_lattice["primitive_hyperbolic_plane"]["primitive_minor_gcd"]
            ),
            "explicit_k3_seed_realizes_full_even_unimodular_k3_lattice": (
                k3_integral_h2_lattice["integral_h2_lattice_theorem"][
                    "explicit_k3_seed_realizes_full_even_unimodular_k3_lattice"
                ]
            ),
        },
        "k3_primitive_plane_global_a4_bridge": {
            "primitive_plane_seed_form": (
                k3_primitive_plane_global_a4["primitive_plane_seed_form"]
            ),
            "primitive_plane_first_refinement_form": (
                k3_primitive_plane_global_a4["primitive_plane_first_refinement_form"]
            ),
            "Q_curv": k3_primitive_plane_global_a4["curvature_quantum_lock"]["Q_curv"],
            "normalized_global_prefactor": (
                k3_primitive_plane_global_a4["reduced_prefactors"]["normalized_global"]
            ),
            "raw_first_refinement_prefactor": (
                k3_primitive_plane_global_a4["reduced_prefactors"]["raw_first_refinement"]
            ),
            "primitive_plane_first_refinement_quantum_is_plus_120": (
                k3_primitive_plane_global_a4["global_a4_coupling_theorem"][
                    "primitive_plane_first_refinement_quantum_is_plus_120"
                ]
            ),
            "reduced_global_prefactor_is_351_over_4_pi_squared": (
                k3_primitive_plane_global_a4["global_a4_coupling_theorem"][
                    "reduced_global_prefactor_is_351_over_4_pi_squared"
                ]
            ),
            "sign_is_fixed_positive_on_the_canonical_oriented_plane": (
                k3_primitive_plane_global_a4["global_a4_coupling_theorem"][
                    "sign_is_fixed_positive_on_the_canonical_oriented_plane"
                ]
            ),
        },
        "k3_three_u_decomposition_bridge": {
            "three_u_block_gram_matrix": (
                k3_three_u_decomposition["three_u_block_gram_matrix"]
            ),
            "three_u_block_unit_minor_rows": (
                k3_three_u_decomposition["three_u_block_profile"]["unit_maximal_minor_rows"]
            ),
            "three_u_block_unit_minor_determinant": (
                k3_three_u_decomposition["three_u_block_profile"]["unit_maximal_minor_determinant"]
            ),
            "three_u_block_has_signature_3_3": (
                k3_three_u_decomposition["three_u_decomposition_theorem"][
                    "three_u_block_has_signature_3_3"
                ]
            ),
            "three_u_block_is_primitive_in_the_ambient_lattice": (
                k3_three_u_decomposition["three_u_decomposition_theorem"][
                    "three_u_block_is_primitive_in_the_ambient_lattice"
                ]
            ),
            "orthogonal_complement_rank": (
                k3_three_u_decomposition["orthogonal_complement_profile"]["rank"]
            ),
            "orthogonal_complement_signature": (
                [
                    k3_three_u_decomposition["orthogonal_complement_profile"]["positive_directions"],
                    k3_three_u_decomposition["orthogonal_complement_profile"]["negative_directions"],
                ]
            ),
            "orthogonal_complement_is_even_negative_definite_unimodular": (
                k3_three_u_decomposition["three_u_decomposition_theorem"][
                    "orthogonal_complement_is_even_negative_definite_unimodular"
                ]
            ),
            "explicit_k3_seed_contains_primitive_orthogonal_3U_core": (
                k3_three_u_decomposition["three_u_decomposition_theorem"][
                    "explicit_k3_seed_contains_primitive_orthogonal_3U_core"
                ]
            ),
        },
        "k3_three_u_refinement_bridge": {
            "three_u_seed_form": (
                k3_three_u_refinement["three_u_seed_form"]
            ),
            "three_u_first_refinement_form": (
                k3_three_u_refinement["three_u_first_refinement_form"]
            ),
            "three_u_block_scales_by_120": (
                k3_three_u_refinement["three_u_refinement_theorem"][
                    "three_u_block_scales_by_120"
                ]
            ),
            "seed_form_is_exact_3u": (
                k3_three_u_refinement["three_u_refinement_theorem"][
                    "seed_form_is_exact_3u"
                ]
            ),
            "first_refinement_form_is_exact_120_times_3u": (
                k3_three_u_refinement["three_u_refinement_theorem"][
                    "first_refinement_form_is_exact_120_times_3u"
                ]
            ),
            "normalized_three_u_block_is_refinement_invariant": (
                k3_three_u_refinement["three_u_refinement_theorem"][
                    "normalized_three_u_block_is_refinement_invariant"
                ]
            ),
            "three_u_signature_survives_first_refinement": (
                k3_three_u_refinement["three_u_refinement_theorem"][
                    "three_u_signature_survives_first_refinement"
                ]
            ),
            "three_u_determinant_scales_by_120_to_the_6": (
                k3_three_u_refinement["three_u_refinement_theorem"][
                    "three_u_determinant_scales_by_120_to_the_6"
                ]
            ),
        },
        "k3_three_u_complement_refinement_bridge": {
            "three_u_complement_basis_shape": (
                k3_three_u_complement_refinement["three_u_complement_basis_shape"]
            ),
            "three_u_complement_seed_form": (
                k3_three_u_complement_refinement["three_u_complement_seed_form"]
            ),
            "three_u_complement_first_refinement_form": (
                k3_three_u_complement_refinement["three_u_complement_first_refinement_form"]
            ),
            "full_split_seed_form": (
                k3_three_u_complement_refinement["full_split_seed_form"]
            ),
            "full_split_first_refinement_form": (
                k3_three_u_complement_refinement["full_split_first_refinement_form"]
            ),
            "three_u_and_complement_are_exactly_orthogonal": (
                k3_three_u_complement_refinement["three_u_complement_refinement_theorem"][
                    "three_u_and_complement_are_exactly_orthogonal"
                ]
            ),
            "complement_has_signature_0_16": (
                k3_three_u_complement_refinement["three_u_complement_refinement_theorem"][
                    "complement_has_signature_0_16"
                ]
            ),
            "complement_form_scales_by_120": (
                k3_three_u_complement_refinement["three_u_complement_refinement_theorem"][
                    "complement_form_scales_by_120"
                ]
            ),
            "full_split_form_scales_by_120": (
                k3_three_u_complement_refinement["three_u_complement_refinement_theorem"][
                    "full_split_form_scales_by_120"
                ]
            ),
            "full_split_cross_terms_remain_zero": (
                k3_three_u_complement_refinement["three_u_complement_refinement_theorem"][
                    "full_split_cross_terms_remain_zero"
                ]
            ),
            "full_split_signature_survives_first_refinement": (
                k3_three_u_complement_refinement["three_u_complement_refinement_theorem"][
                    "full_split_signature_survives_first_refinement"
                ]
            ),
            "explicit_k3_lattice_split_is_first_refinement_rigid": (
                k3_three_u_complement_refinement["three_u_complement_refinement_theorem"][
                    "explicit_k3_lattice_split_is_first_refinement_rigid"
                ]
            ),
        },
        "k3_n16_e8e8_bridge": {
            "root_representative_count": (
                k3_n16_e8e8["root_representative_count"]
            ),
            "total_root_count": (
                k3_n16_e8e8["total_root_count"]
            ),
            "root_span_smith_diagonal": (
                k3_n16_e8e8["root_span_smith_diagonal"]
            ),
            "root_span_rank": (
                k3_n16_e8e8["root_span_rank"]
            ),
            "root_span_index": (
                k3_n16_e8e8["root_span_index"]
            ),
            "n16_has_480_roots": (
                k3_n16_e8e8["n16_classification_theorem"]["n16_has_480_roots"]
            ),
            "root_span_equals_the_full_lattice": (
                k3_n16_e8e8["n16_classification_theorem"][
                    "root_span_equals_the_full_lattice"
                ]
            ),
            "explicit_n16_is_not_d16_plus": (
                k3_n16_e8e8["n16_classification_theorem"][
                    "explicit_n16_is_not_d16_plus"
                ]
            ),
            "explicit_n16_is_e8_plus_e8_by_rank16_even_unimodular_classification": (
                k3_n16_e8e8["n16_classification_theorem"][
                    "explicit_n16_is_e8_plus_e8_by_rank16_even_unimodular_classification"
                ]
            ),
        },
        "k3_e8_factor_split_bridge": {
            "representative_root_component_sizes": (
                k3_e8_factor_split["representative_root_component_sizes"]
            ),
            "full_root_component_sizes": (
                k3_e8_factor_split["full_root_component_sizes"]
            ),
            "e8_factor_one_gram_matrix": (
                k3_e8_factor_split["e8_factor_one_gram_matrix"]
            ),
            "e8_factor_two_gram_matrix": (
                k3_e8_factor_split["e8_factor_two_gram_matrix"]
            ),
            "cross_gram_matrix": (
                k3_e8_factor_split["cross_gram_matrix"]
            ),
            "combined_simple_root_change_of_basis_determinant": (
                k3_e8_factor_split["combined_simple_root_change_of_basis_determinant"]
            ),
            "representative_root_graph_splits_into_two_120_packets": (
                k3_e8_factor_split["e8_factor_split_theorem"][
                    "representative_root_graph_splits_into_two_120_packets"
                ]
            ),
            "full_root_graph_splits_into_two_240_packets": (
                k3_e8_factor_split["e8_factor_split_theorem"][
                    "full_root_graph_splits_into_two_240_packets"
                ]
            ),
            "factor_one_has_exact_negative_e8_cartan": (
                k3_e8_factor_split["e8_factor_split_theorem"][
                    "factor_one_has_exact_negative_e8_cartan"
                ]
            ),
            "factor_two_has_exact_negative_e8_cartan": (
                k3_e8_factor_split["e8_factor_split_theorem"][
                    "factor_two_has_exact_negative_e8_cartan"
                ]
            ),
            "the_two_e8_factor_bases_are_exactly_orthogonal": (
                k3_e8_factor_split["e8_factor_split_theorem"][
                    "the_two_e8_factor_bases_are_exactly_orthogonal"
                ]
            ),
            "combined_simple_root_basis_is_unimodular_in_the_explicit_complement": (
                k3_e8_factor_split["e8_factor_split_theorem"][
                    "combined_simple_root_basis_is_unimodular_in_the_explicit_complement"
                ]
            ),
            "explicit_n16_is_constructively_split_as_e8_plus_e8": (
                k3_e8_factor_split["e8_factor_split_theorem"][
                    "explicit_n16_is_constructively_split_as_e8_plus_e8"
                ]
            ),
        },
        "k3_e8_factor_refinement_bridge": {
            "e8_factor_one_seed_form": (
                k3_e8_factor_refinement["e8_factor_one_seed_form"]
            ),
            "e8_factor_one_first_refinement_form": (
                k3_e8_factor_refinement["e8_factor_one_first_refinement_form"]
            ),
            "e8_factor_two_seed_form": (
                k3_e8_factor_refinement["e8_factor_two_seed_form"]
            ),
            "e8_factor_two_first_refinement_form": (
                k3_e8_factor_refinement["e8_factor_two_first_refinement_form"]
            ),
            "e8_factor_cross_seed_form": (
                k3_e8_factor_refinement["e8_factor_cross_seed_form"]
            ),
            "full_named_seed_form": (
                k3_e8_factor_refinement["full_named_seed_form"]
            ),
            "full_named_first_refinement_form": (
                k3_e8_factor_refinement["full_named_first_refinement_form"]
            ),
            "factor_one_refined_form_is_exact_120_times_negative_e8_cartan": (
                k3_e8_factor_refinement["e8_factor_refinement_theorem"][
                    "factor_one_refined_form_is_exact_120_times_negative_e8_cartan"
                ]
            ),
            "factor_two_refined_form_is_exact_120_times_negative_e8_cartan": (
                k3_e8_factor_refinement["e8_factor_refinement_theorem"][
                    "factor_two_refined_form_is_exact_120_times_negative_e8_cartan"
                ]
            ),
            "e8_factors_remain_exactly_orthogonal_after_refinement": (
                k3_e8_factor_refinement["e8_factor_refinement_theorem"][
                    "e8_factors_remain_exactly_orthogonal_after_refinement"
                ]
            ),
            "full_named_split_scales_by_120": (
                k3_e8_factor_refinement["e8_factor_refinement_theorem"][
                    "full_named_split_scales_by_120"
                ]
            ),
            "normalized_named_split_is_refinement_invariant": (
                k3_e8_factor_refinement["e8_factor_refinement_theorem"][
                    "normalized_named_split_is_refinement_invariant"
                ]
            ),
            "explicit_named_k3_split_is_first_refinement_rigid": (
                k3_e8_factor_refinement["e8_factor_refinement_theorem"][
                    "explicit_named_k3_split_is_first_refinement_rigid"
                ]
            ),
        },
        "k3_primitive_plane_three_u_alignment_bridge": {
            "primitive_plane_coefficients": (
                k3_primitive_plane_three_u_alignment["primitive_plane_coefficients"]
            ),
            "three_u_factor_one_coefficients": (
                k3_primitive_plane_three_u_alignment["three_u_factor_one_coefficients"]
            ),
            "selector_u_factor_one_form": (
                k3_primitive_plane_three_u_alignment["selector_u_factor_one_form"]
            ),
            "selector_u_factor_two_form": (
                k3_primitive_plane_three_u_alignment["selector_u_factor_two_form"]
            ),
            "selector_u_factor_three_form": (
                k3_primitive_plane_three_u_alignment["selector_u_factor_three_form"]
            ),
            "selector_three_u_shadow_reconstruction_error_linf": (
                k3_primitive_plane_three_u_alignment["selector_three_u_shadow_reconstruction_error_linf"]
            ),
            "primitive_plane_equals_the_first_explicit_u_factor": (
                k3_primitive_plane_three_u_alignment["primitive_plane_three_u_alignment_theorem"][
                    "primitive_plane_equals_the_first_explicit_u_factor"
                ]
            ),
            "selector_three_u_shadow_decomposes_exactly_across_the_three_u_factors": (
                k3_primitive_plane_three_u_alignment["primitive_plane_three_u_alignment_theorem"][
                    "selector_three_u_shadow_decomposes_exactly_across_the_three_u_factors"
                ]
            ),
            "selector_has_nonzero_projection_on_u_factor_one": (
                k3_primitive_plane_three_u_alignment["primitive_plane_three_u_alignment_theorem"][
                    "selector_has_nonzero_projection_on_u_factor_one"
                ]
            ),
            "selector_has_nonzero_projection_on_u_factor_two": (
                k3_primitive_plane_three_u_alignment["primitive_plane_three_u_alignment_theorem"][
                    "selector_has_nonzero_projection_on_u_factor_two"
                ]
            ),
            "selector_has_nonzero_projection_on_u_factor_three": (
                k3_primitive_plane_three_u_alignment["primitive_plane_three_u_alignment_theorem"][
                    "selector_has_nonzero_projection_on_u_factor_three"
                ]
            ),
            "selector_three_u_shadow_is_not_supported_on_the_primitive_plane_alone": (
                k3_primitive_plane_three_u_alignment["primitive_plane_three_u_alignment_theorem"][
                    "selector_three_u_shadow_is_not_supported_on_the_primitive_plane_alone"
                ]
            ),
            "primitive_plane_is_distinguished_but_not_equal_to_the_selector_positive_channel": (
                k3_primitive_plane_three_u_alignment["primitive_plane_three_u_alignment_theorem"][
                    "primitive_plane_is_distinguished_but_not_equal_to_the_selector_positive_channel"
                ]
            ),
        },
        "k3_selector_three_u_shadow_bridge": {
            "selector_plane_form": (
                k3_selector_three_u_shadow["selector_plane_form"]
            ),
            "three_u_shadow_form": (
                k3_selector_three_u_shadow["three_u_shadow_form"]
            ),
            "rank16_residual_form": (
                k3_selector_three_u_shadow["rank16_residual_form"]
            ),
            "principal_cosines_against_three_u_core": (
                k3_selector_three_u_shadow["principal_cosines_against_three_u_core"]
            ),
            "selector_plane_shadow_on_three_u_is_positive_definite": (
                k3_selector_three_u_shadow["selector_three_u_shadow_theorem"][
                    "selector_plane_shadow_on_three_u_is_positive_definite"
                ]
            ),
            "selector_plane_residual_on_rank16_complement_is_negative_definite": (
                k3_selector_three_u_shadow["selector_three_u_shadow_theorem"][
                    "selector_plane_residual_on_rank16_complement_is_negative_definite"
                ]
            ),
            "selector_plane_is_not_contained_in_three_u_core": (
                k3_selector_three_u_shadow["selector_three_u_shadow_theorem"][
                    "selector_plane_is_not_contained_in_three_u_core"
                ]
            ),
            "selector_plane_straddles_both_k3_lattice_pieces": (
                k3_selector_three_u_shadow["selector_three_u_shadow_theorem"][
                    "selector_plane_straddles_both_k3_lattice_pieces"
                ]
            ),
        },
        "k3_selector_e8_shadow_bridge": {
            "selector_plane_form": (
                k3_selector_e8_shadow["selector_plane_form"]
            ),
            "three_u_component_form": (
                k3_selector_e8_shadow["three_u_component_form"]
            ),
            "e8_factor_one_component_form": (
                k3_selector_e8_shadow["e8_factor_one_component_form"]
            ),
            "e8_factor_two_component_form": (
                k3_selector_e8_shadow["e8_factor_two_component_form"]
            ),
            "reconstruction_error_linf": (
                k3_selector_e8_shadow["reconstruction_error_linf"]
            ),
            "selector_projection_on_three_u_is_positive_definite": (
                k3_selector_e8_shadow["selector_e8_shadow_theorem"][
                    "selector_projection_on_three_u_is_positive_definite"
                ]
            ),
            "selector_projection_on_e8_factor_one_is_negative_definite": (
                k3_selector_e8_shadow["selector_e8_shadow_theorem"][
                    "selector_projection_on_e8_factor_one_is_negative_definite"
                ]
            ),
            "selector_projection_on_e8_factor_two_is_negative_definite": (
                k3_selector_e8_shadow["selector_e8_shadow_theorem"][
                    "selector_projection_on_e8_factor_two_is_negative_definite"
                ]
            ),
            "selector_projection_on_e8_factor_one_is_nonzero": (
                k3_selector_e8_shadow["selector_e8_shadow_theorem"][
                    "selector_projection_on_e8_factor_one_is_nonzero"
                ]
            ),
            "selector_projection_on_e8_factor_two_is_nonzero": (
                k3_selector_e8_shadow["selector_e8_shadow_theorem"][
                    "selector_projection_on_e8_factor_two_is_nonzero"
                ]
            ),
            "selector_decomposes_orthogonally_across_three_u_and_both_e8_factors": (
                k3_selector_e8_shadow["selector_e8_shadow_theorem"][
                    "selector_decomposes_orthogonally_across_three_u_and_both_e8_factors"
                ]
            ),
            "selector_is_not_supported_on_single_e8_factor": (
                k3_selector_e8_shadow["selector_e8_shadow_theorem"][
                    "selector_is_not_supported_on_single_e8_factor"
                ]
            ),
            "selector_bridges_three_u_and_both_e8_factors": (
                k3_selector_e8_shadow["selector_e8_shadow_theorem"][
                    "selector_bridges_three_u_and_both_e8_factors"
                ]
            ),
        },
        "k3_selector_shadow_refinement_bridge": {
            "selector_seed_form": (
                k3_selector_shadow_refinement["selector_seed_form"]
            ),
            "selector_first_refinement_form": (
                k3_selector_shadow_refinement["selector_first_refinement_form"]
            ),
            "three_u_shadow_seed_form": (
                k3_selector_shadow_refinement["three_u_shadow_seed_form"]
            ),
            "three_u_shadow_first_refinement_form": (
                k3_selector_shadow_refinement["three_u_shadow_first_refinement_form"]
            ),
            "rank16_residual_seed_form": (
                k3_selector_shadow_refinement["rank16_residual_seed_form"]
            ),
            "rank16_residual_first_refinement_form": (
                k3_selector_shadow_refinement["rank16_residual_first_refinement_form"]
            ),
            "selector_plane_scales_by_120": (
                k3_selector_shadow_refinement["selector_shadow_refinement_theorem"][
                    "selector_plane_scales_by_120"
                ]
            ),
            "three_u_shadow_scales_by_120": (
                k3_selector_shadow_refinement["selector_shadow_refinement_theorem"][
                    "three_u_shadow_scales_by_120"
                ]
            ),
            "rank16_residual_scales_by_120": (
                k3_selector_shadow_refinement["selector_shadow_refinement_theorem"][
                    "rank16_residual_scales_by_120"
                ]
            ),
            "three_u_shadow_stays_positive_definite": (
                k3_selector_shadow_refinement["selector_shadow_refinement_theorem"][
                    "three_u_shadow_stays_positive_definite"
                ]
            ),
            "rank16_residual_stays_negative_definite": (
                k3_selector_shadow_refinement["selector_shadow_refinement_theorem"][
                    "rank16_residual_stays_negative_definite"
                ]
            ),
        },
        "k3_selector_a4_lattice_split_bridge": {
            "common_scalar_prefactor": (
                k3_selector_a4_lattice_split["common_scalar_prefactor"]
            ),
            "selector_packet_form": (
                k3_selector_a4_lattice_split["selector_packet_form"]
            ),
            "three_u_packet_form": (
                k3_selector_a4_lattice_split["three_u_packet_form"]
            ),
            "e8_factor_one_packet_form": (
                k3_selector_a4_lattice_split["e8_factor_one_packet_form"]
            ),
            "e8_factor_two_packet_form": (
                k3_selector_a4_lattice_split["e8_factor_two_packet_form"]
            ),
            "selector_packet_reconstructs_as_three_u_plus_e8_plus_e8": (
                k3_selector_a4_lattice_split["selector_a4_lattice_split_theorem"][
                    "selector_packet_reconstructs_as_three_u_plus_e8_plus_e8"
                ]
            ),
            "three_u_packet_piece_is_positive_definite": (
                k3_selector_a4_lattice_split["selector_a4_lattice_split_theorem"][
                    "three_u_packet_piece_is_positive_definite"
                ]
            ),
            "e8_factor_one_packet_piece_is_negative_definite": (
                k3_selector_a4_lattice_split["selector_a4_lattice_split_theorem"][
                    "e8_factor_one_packet_piece_is_negative_definite"
                ]
            ),
            "e8_factor_two_packet_piece_is_negative_definite": (
                k3_selector_a4_lattice_split["selector_a4_lattice_split_theorem"][
                    "e8_factor_two_packet_piece_is_negative_definite"
                ]
            ),
            "all_three_packet_pieces_are_nonzero": (
                k3_selector_a4_lattice_split["selector_a4_lattice_split_theorem"][
                    "all_three_packet_pieces_are_nonzero"
                ]
            ),
            "reduced_selector_packet_is_tri_supported_across_the_named_k3_split": (
                k3_selector_a4_lattice_split["selector_a4_lattice_split_theorem"][
                    "reduced_selector_packet_is_tri_supported_across_the_named_k3_split"
                ]
            ),
            "scalar_prefactor_remains_exactly_351_over_4_pi_squared": (
                k3_selector_a4_lattice_split["selector_a4_lattice_split_theorem"][
                    "scalar_prefactor_remains_exactly_351_over_4_pi_squared"
                ]
            ),
        },
        "k3_selector_a4_five_factor_bridge": {
            "common_scalar_prefactor": (
                k3_selector_a4_five_factor["common_scalar_prefactor"]
            ),
            "u_factor_one_packet_form": (
                k3_selector_a4_five_factor["u_factor_one_packet_form"]
            ),
            "u_factor_two_packet_form": (
                k3_selector_a4_five_factor["u_factor_two_packet_form"]
            ),
            "u_factor_three_packet_form": (
                k3_selector_a4_five_factor["u_factor_three_packet_form"]
            ),
            "e8_factor_one_packet_form": (
                k3_selector_a4_five_factor["e8_factor_one_packet_form"]
            ),
            "e8_factor_two_packet_form": (
                k3_selector_a4_five_factor["e8_factor_two_packet_form"]
            ),
            "reconstruction_error_linf": (
                k3_selector_a4_five_factor["reconstruction_error_linf"]
            ),
            "three_u_packet_reconstructs_as_u1_plus_u2_plus_u3": (
                k3_selector_a4_five_factor["selector_a4_five_factor_theorem"][
                    "three_u_packet_reconstructs_as_u1_plus_u2_plus_u3"
                ]
            ),
            "selector_packet_reconstructs_as_u1_plus_u2_plus_u3_plus_e8_plus_e8": (
                k3_selector_a4_five_factor["selector_a4_five_factor_theorem"][
                    "selector_packet_reconstructs_as_u1_plus_u2_plus_u3_plus_e8_plus_e8"
                ]
            ),
            "u_factor_one_packet_piece_is_mixed_signature": (
                k3_selector_a4_five_factor["selector_a4_five_factor_theorem"][
                    "u_factor_one_packet_piece_is_mixed_signature"
                ]
            ),
            "u_factor_two_packet_piece_is_mixed_signature": (
                k3_selector_a4_five_factor["selector_a4_five_factor_theorem"][
                    "u_factor_two_packet_piece_is_mixed_signature"
                ]
            ),
            "u_factor_three_packet_piece_is_mixed_signature": (
                k3_selector_a4_five_factor["selector_a4_five_factor_theorem"][
                    "u_factor_three_packet_piece_is_mixed_signature"
                ]
            ),
            "all_five_packet_pieces_are_nonzero": (
                k3_selector_a4_five_factor["selector_a4_five_factor_theorem"][
                    "all_five_packet_pieces_are_nonzero"
                ]
            ),
            "distinguished_u1_plane_has_nonzero_selector_packet_piece": (
                k3_selector_a4_five_factor["selector_a4_five_factor_theorem"][
                    "distinguished_u1_plane_has_nonzero_selector_packet_piece"
                ]
            ),
            "selector_hyperbolic_packet_is_not_supported_on_u1_alone": (
                k3_selector_a4_five_factor["selector_a4_five_factor_theorem"][
                    "selector_hyperbolic_packet_is_not_supported_on_u1_alone"
                ]
            ),
            "reduced_selector_packet_is_five_supported_across_u_u_u_e8_e8": (
                k3_selector_a4_five_factor["selector_a4_five_factor_theorem"][
                    "reduced_selector_packet_is_five_supported_across_u_u_u_e8_e8"
                ]
            ),
        },
        "k3_selector_a4_five_factor_refinement_bridge": {
            "u_factor_one_seed_form": (
                k3_selector_a4_five_factor_refinement["u_factor_one_seed_form"]
            ),
            "u_factor_one_first_refinement_form": (
                k3_selector_a4_five_factor_refinement["u_factor_one_first_refinement_form"]
            ),
            "u_factor_two_seed_form": (
                k3_selector_a4_five_factor_refinement["u_factor_two_seed_form"]
            ),
            "u_factor_two_first_refinement_form": (
                k3_selector_a4_five_factor_refinement["u_factor_two_first_refinement_form"]
            ),
            "u_factor_three_seed_form": (
                k3_selector_a4_five_factor_refinement["u_factor_three_seed_form"]
            ),
            "u_factor_three_first_refinement_form": (
                k3_selector_a4_five_factor_refinement["u_factor_three_first_refinement_form"]
            ),
            "e8_factor_one_seed_form": (
                k3_selector_a4_five_factor_refinement["e8_factor_one_seed_form"]
            ),
            "e8_factor_one_first_refinement_form": (
                k3_selector_a4_five_factor_refinement["e8_factor_one_first_refinement_form"]
            ),
            "e8_factor_two_seed_form": (
                k3_selector_a4_five_factor_refinement["e8_factor_two_seed_form"]
            ),
            "e8_factor_two_first_refinement_form": (
                k3_selector_a4_five_factor_refinement["e8_factor_two_first_refinement_form"]
            ),
            "u_factor_one_packet_piece_scales_by_120": (
                k3_selector_a4_five_factor_refinement["selector_a4_five_factor_refinement_theorem"][
                    "u_factor_one_packet_piece_scales_by_120"
                ]
            ),
            "u_factor_two_packet_piece_scales_by_120": (
                k3_selector_a4_five_factor_refinement["selector_a4_five_factor_refinement_theorem"][
                    "u_factor_two_packet_piece_scales_by_120"
                ]
            ),
            "u_factor_three_packet_piece_scales_by_120": (
                k3_selector_a4_five_factor_refinement["selector_a4_five_factor_refinement_theorem"][
                    "u_factor_three_packet_piece_scales_by_120"
                ]
            ),
            "e8_factor_one_packet_piece_scales_by_120": (
                k3_selector_a4_five_factor_refinement["selector_a4_five_factor_refinement_theorem"][
                    "e8_factor_one_packet_piece_scales_by_120"
                ]
            ),
            "e8_factor_two_packet_piece_scales_by_120": (
                k3_selector_a4_five_factor_refinement["selector_a4_five_factor_refinement_theorem"][
                    "e8_factor_two_packet_piece_scales_by_120"
                ]
            ),
            "all_five_normalized_packet_forms_are_refinement_invariant": (
                k3_selector_a4_five_factor_refinement["selector_a4_five_factor_refinement_theorem"][
                    "all_five_normalized_packet_forms_are_refinement_invariant"
                ]
            ),
            "all_three_u_factor_packet_pieces_stay_mixed_signature": (
                k3_selector_a4_five_factor_refinement["selector_a4_five_factor_refinement_theorem"][
                    "all_three_u_factor_packet_pieces_stay_mixed_signature"
                ]
            ),
            "both_e8_packet_pieces_stay_negative_definite": (
                k3_selector_a4_five_factor_refinement["selector_a4_five_factor_refinement_theorem"][
                    "both_e8_packet_pieces_stay_negative_definite"
                ]
            ),
            "fine_selector_packet_split_is_first_refinement_rigid": (
                k3_selector_a4_five_factor_refinement["selector_a4_five_factor_refinement_theorem"][
                    "fine_selector_packet_split_is_first_refinement_rigid"
                ]
            ),
        },
        "u1_family_a4_carrier_bridge": {
            "delta_A4": (
                u1_family_a4_carrier["internal_family_entry"]["delta_A4"]
            ),
            "canonical_external_carrier": (
                u1_family_a4_carrier["canonical_external_carrier"]["plane_name"]
            ),
            "normalized_global_prefactor": (
                u1_family_a4_carrier["canonical_external_carrier"]["normalized_global_prefactor"]
            ),
            "common_line_generator": (
                u1_family_a4_carrier["internal_family_boundary_condition"]["common_line_generator"]
            ),
            "common_plane_equation": (
                u1_family_a4_carrier["internal_family_boundary_condition"]["common_plane_equation"]
            ),
            "distinguished_generation": (
                u1_family_a4_carrier["internal_family_boundary_condition"]["distinguished_generation"]
            ),
            "first_family_entry_is_a4_only": (
                u1_family_a4_carrier["u1_family_a4_carrier_theorem"][
                    "first_family_entry_is_a4_only"
                ]
            ),
            "canonical_external_carrier_equals_u_factor_one": (
                u1_family_a4_carrier["u1_family_a4_carrier_theorem"][
                    "canonical_external_carrier_equals_u_factor_one"
                ]
            ),
            "canonical_u1_carrier_has_exact_351_over_4_pi_squared_coupling": (
                u1_family_a4_carrier["u1_family_a4_carrier_theorem"][
                    "canonical_u1_carrier_has_exact_351_over_4_pi_squared_coupling"
                ]
            ),
            "u1_is_nonzero_piece_of_full_selector_packet": (
                u1_family_a4_carrier["u1_family_a4_carrier_theorem"][
                    "u1_is_nonzero_piece_of_full_selector_packet"
                ]
            ),
            "full_selector_packet_is_not_supported_on_u1_alone": (
                u1_family_a4_carrier["u1_family_a4_carrier_theorem"][
                    "full_selector_packet_is_not_supported_on_u1_alone"
                ]
            ),
            "internal_family_side_has_exact_one_vs_two_flag_boundary_condition": (
                u1_family_a4_carrier["u1_family_a4_carrier_theorem"][
                    "internal_family_side_has_exact_one_vs_two_flag_boundary_condition"
                ]
            ),
            "exact_identification_of_u1_with_transport_162_extension_is_obstructed": (
                u1_family_a4_carrier["u1_family_a4_carrier_theorem"][
                    "exact_identification_of_u1_with_transport_162_extension_is_obstructed"
                ]
            ),
            "minimal_canonical_family_bridge_carrier_is_delta_a4_on_u1": (
                u1_family_a4_carrier["u1_family_a4_carrier_theorem"][
                    "minimal_canonical_family_bridge_carrier_is_delta_a4_on_u1"
                ]
            ),
        },
        "u1_isotropic_line_obstruction_bridge": {
            "u1_seed_form": (
                u1_isotropic_line_obstruction["u1_seed_form"]
            ),
            "u1_swapped_seed_form": (
                u1_isotropic_line_obstruction["u1_swapped_seed_form"]
            ),
            "u1_line_one_coefficients": (
                u1_isotropic_line_obstruction["u1_line_one_coefficients"]
            ),
            "u1_line_two_coefficients": (
                u1_isotropic_line_obstruction["u1_line_two_coefficients"]
            ),
            "internal_common_line_generator": (
                u1_isotropic_line_obstruction["internal_common_line_generator"]
            ),
            "line_one_is_primitive": (
                u1_isotropic_line_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "line_one_is_primitive"
                ]
            ),
            "line_two_is_primitive": (
                u1_isotropic_line_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "line_two_is_primitive"
                ]
            ),
            "line_one_is_isotropic": (
                u1_isotropic_line_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "line_one_is_isotropic"
                ]
            ),
            "line_two_is_isotropic": (
                u1_isotropic_line_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "line_two_is_isotropic"
                ]
            ),
            "line_pair_has_unit_hyperbolic_pairing": (
                u1_isotropic_line_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "line_pair_has_unit_hyperbolic_pairing"
                ]
            ),
            "swapping_the_two_isotropic_lines_preserves_the_u1_seed_form": (
                u1_isotropic_line_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "swapping_the_two_isotropic_lines_preserves_the_u1_seed_form"
                ]
            ),
            "current_u1_data_do_not_distinguish_one_isotropic_line_from_the_other": (
                u1_isotropic_line_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "current_u1_data_do_not_distinguish_one_isotropic_line_from_the_other"
                ]
            ),
            "exact_identification_of_the_internal_common_line_with_a_canonical_u1_line_is_not_yet_supported": (
                u1_isotropic_line_obstruction["u1_isotropic_line_obstruction_theorem"][
                    "exact_identification_of_the_internal_common_line_with_a_canonical_u1_line_is_not_yet_supported"
                ]
            ),
        },
        "selector_a4_weight_hierarchy_bridge": {
            "factor_frobenius_norms": (
                selector_a4_weight_hierarchy["factor_frobenius_norms"]
            ),
            "hyperbolic_weight_shares": (
                selector_a4_weight_hierarchy["hyperbolic_weight_shares"]
            ),
            "exceptional_weight_shares": (
                selector_a4_weight_hierarchy["exceptional_weight_shares"]
            ),
            "hyperbolic_weight_order_is_u3_gt_u1_gt_u2": (
                selector_a4_weight_hierarchy["selector_a4_weight_hierarchy_theorem"][
                    "hyperbolic_weight_order_is_u3_gt_u1_gt_u2"
                ]
            ),
            "exceptional_weight_order_is_e8_factor_two_gt_e8_factor_one": (
                selector_a4_weight_hierarchy["selector_a4_weight_hierarchy_theorem"][
                    "exceptional_weight_order_is_e8_factor_two_gt_e8_factor_one"
                ]
            ),
            "u3_carries_more_than_four_fifths_of_hyperbolic_packet_weight": (
                selector_a4_weight_hierarchy["selector_a4_weight_hierarchy_theorem"][
                    "u3_carries_more_than_four_fifths_of_hyperbolic_packet_weight"
                ]
            ),
            "e8_factor_two_carries_more_than_eight_ninths_of_exceptional_packet_weight": (
                selector_a4_weight_hierarchy["selector_a4_weight_hierarchy_theorem"][
                    "e8_factor_two_carries_more_than_eight_ninths_of_exceptional_packet_weight"
                ]
            ),
            "fine_weight_hierarchy_is_refinement_invariant": (
                selector_a4_weight_hierarchy["selector_a4_weight_hierarchy_theorem"][
                    "fine_weight_hierarchy_is_refinement_invariant"
                ]
            ),
        },
        "transport_semisimplification_shadow_bridge": {
            "internal_transport_semisimplification": (
                transport_semisimplification_shadow["internal_transport_semisimplification"]
            ),
            "external_split_shadow": (
                transport_semisimplification_shadow["external_split_shadow"]
            ),
            "internal_semisimplification_is_81_plus_81": (
                transport_semisimplification_shadow["transport_semisimplification_shadow_theorem"][
                    "internal_semisimplification_is_81_plus_81"
                ]
            ),
            "external_split_shadow_is_81_plus_81": (
                transport_semisimplification_shadow["transport_semisimplification_shadow_theorem"][
                    "external_split_shadow_is_81_plus_81"
                ]
            ),
            "internal_and_external_objects_match_exactly_at_semisimplified_shadow_level": (
                transport_semisimplification_shadow["transport_semisimplification_shadow_theorem"][
                    "internal_and_external_objects_match_exactly_at_semisimplified_shadow_level"
                ]
            ),
            "internal_extension_class_is_nonzero": (
                transport_semisimplification_shadow["transport_semisimplification_shadow_theorem"][
                    "internal_extension_class_is_nonzero"
                ]
            ),
            "external_extension_class_is_zero": (
                transport_semisimplification_shadow["transport_semisimplification_shadow_theorem"][
                    "external_extension_class_is_zero"
                ]
            ),
            "transport_k3_match_is_semisimplified_shadow_not_extension_identity": (
                transport_semisimplification_shadow["transport_semisimplification_shadow_theorem"][
                    "transport_k3_match_is_semisimplified_shadow_not_extension_identity"
                ]
            ),
        },
        "global_local_carrier_split_bridge": {
            "canonical_global_carrier": (
                global_local_carrier_split["canonical_global_carrier"]
            ),
            "dominant_hyperbolic_packet_piece": (
                global_local_carrier_split["dominant_hyperbolic_packet_piece"]
            ),
            "dominant_exceptional_packet_piece": (
                global_local_carrier_split["dominant_exceptional_packet_piece"]
            ),
            "hyperbolic_dominance_ratio_u3_over_u1": (
                global_local_carrier_split["hyperbolic_dominance_ratio_u3_over_u1"]
            ),
            "exceptional_dominance_ratio_e8_factor_two_over_e8_factor_one": (
                global_local_carrier_split[
                    "exceptional_dominance_ratio_e8_factor_two_over_e8_factor_one"
                ]
            ),
            "canonical_global_carrier_is_u1": (
                global_local_carrier_split["global_local_carrier_split_theorem"][
                    "canonical_global_carrier_is_u1"
                ]
            ),
            "dominant_hyperbolic_packet_piece_is_u3": (
                global_local_carrier_split["global_local_carrier_split_theorem"][
                    "dominant_hyperbolic_packet_piece_is_u3"
                ]
            ),
            "dominant_exceptional_packet_piece_is_e8_factor_two": (
                global_local_carrier_split["global_local_carrier_split_theorem"][
                    "dominant_exceptional_packet_piece_is_e8_factor_two"
                ]
            ),
            "canonical_global_carrier_differs_from_dominant_hyperbolic_packet_piece": (
                global_local_carrier_split["global_local_carrier_split_theorem"][
                    "canonical_global_carrier_differs_from_dominant_hyperbolic_packet_piece"
                ]
            ),
            "first_family_packet_has_canonical_global_support_but_non_u1_local_dominance": (
                global_local_carrier_split["global_local_carrier_split_theorem"][
                    "first_family_packet_has_canonical_global_support_but_non_u1_local_dominance"
                ]
            ),
            "global_local_carrier_split_is_refinement_invariant": (
                global_local_carrier_split["global_local_carrier_split_theorem"][
                    "global_local_carrier_split_is_refinement_invariant"
                ]
            ),
        },
        "u1_selector_line_selection_bridge": {
            "u1_selector_coordinate_matrix": (
                u1_selector_line_selection["u1_selector_coordinate_matrix"]
            ),
            "u1_isotropic_line_weights": (
                u1_selector_line_selection["u1_isotropic_line_weights"]
            ),
            "u1_first_refinement_form": (
                u1_selector_line_selection["u1_first_refinement_form"]
            ),
            "u1_selector_first_refinement_packet_form": (
                u1_selector_line_selection["u1_selector_first_refinement_packet_form"]
            ),
            "dominant_isotropic_line_index": (
                u1_selector_line_selection["dominant_isotropic_line_index"]
            ),
            "recessive_isotropic_line_index": (
                u1_selector_line_selection["recessive_isotropic_line_index"]
            ),
            "dominant_isotropic_line_coefficients": (
                u1_selector_line_selection["dominant_isotropic_line_coefficients"]
            ),
            "recessive_isotropic_line_coefficients": (
                u1_selector_line_selection["recessive_isotropic_line_coefficients"]
            ),
            "dominance_ratio": u1_selector_line_selection["dominance_ratio"],
            "carrier_metric_alone_is_line_blind": (
                u1_selector_line_selection["u1_selector_line_selection_theorem"][
                    "carrier_metric_alone_is_line_blind"
                ]
            ),
            "canonical_selector_u1_component_has_full_rank_2": (
                u1_selector_line_selection["u1_selector_line_selection_theorem"][
                    "canonical_selector_u1_component_has_full_rank_2"
                ]
            ),
            "canonical_selector_u1_component_assigns_unequal_weights_to_the_two_isotropic_lines": (
                u1_selector_line_selection["u1_selector_line_selection_theorem"][
                    "canonical_selector_u1_component_assigns_unequal_weights_to_the_two_isotropic_lines"
                ]
            ),
            "there_is_a_unique_dominant_isotropic_line_inside_u1": (
                u1_selector_line_selection["u1_selector_line_selection_theorem"][
                    "there_is_a_unique_dominant_isotropic_line_inside_u1"
                ]
            ),
            "dominant_isotropic_line_is_the_first_u1_line_in_the_current_canonical_basis": (
                u1_selector_line_selection["u1_selector_line_selection_theorem"][
                    "dominant_isotropic_line_is_the_first_u1_line_in_the_current_canonical_basis"
                ]
            ),
            "selector_line_weights_are_invariant_under_selector_basis_signs_and_swap": (
                u1_selector_line_selection["u1_selector_line_selection_theorem"][
                    "selector_line_weights_are_invariant_under_selector_basis_signs_and_swap"
                ]
            ),
            "u1_carrier_form_scales_by_120_at_first_refinement": (
                u1_selector_line_selection["u1_selector_line_selection_theorem"][
                    "u1_carrier_form_scales_by_120_at_first_refinement"
                ]
            ),
            "u1_selector_packet_form_scales_by_120_at_first_refinement": (
                u1_selector_line_selection["u1_selector_line_selection_theorem"][
                    "u1_selector_packet_form_scales_by_120_at_first_refinement"
                ]
            ),
            "dominant_line_candidate_is_first_refinement_rigid": (
                u1_selector_line_selection["u1_selector_line_selection_theorem"][
                    "dominant_line_candidate_is_first_refinement_rigid"
                ]
            ),
            "full_current_external_packet_selects_a_canonical_isotropic_line_candidate_inside_u1": (
                u1_selector_line_selection["u1_selector_line_selection_theorem"][
                    "full_current_external_packet_selects_a_canonical_isotropic_line_candidate_inside_u1"
                ]
            ),
        },
        "family_flag_visibility_obstruction_bridge": {
            "internal_common_line_generator": (
                family_flag_visibility_obstruction["internal_common_line_generator"]
            ),
            "internal_common_plane_equation": (
                family_flag_visibility_obstruction["internal_common_plane_equation"]
            ),
            "external_canonical_carrier_plane": (
                family_flag_visibility_obstruction["external_canonical_carrier_plane"]
            ),
            "external_canonical_line_candidate": (
                family_flag_visibility_obstruction["external_canonical_line_candidate"]
            ),
            "external_semisimplified_shadow": (
                family_flag_visibility_obstruction["external_semisimplified_shadow"]
            ),
            "internal_family_flag_is_exact_line_in_plane_data": (
                family_flag_visibility_obstruction["family_flag_visibility_obstruction_theorem"][
                    "internal_family_flag_is_exact_line_in_plane_data"
                ]
            ),
            "external_side_fixes_a_canonical_carrier_plane_u1": (
                family_flag_visibility_obstruction["family_flag_visibility_obstruction_theorem"][
                    "external_side_fixes_a_canonical_carrier_plane_u1"
                ]
            ),
            "carrier_metric_alone_is_line_blind_inside_u1": (
                family_flag_visibility_obstruction["family_flag_visibility_obstruction_theorem"][
                    "carrier_metric_alone_is_line_blind_inside_u1"
                ]
            ),
            "full_external_packet_selects_a_canonical_line_candidate_inside_u1": (
                family_flag_visibility_obstruction["family_flag_visibility_obstruction_theorem"][
                    "full_external_packet_selects_a_canonical_line_candidate_inside_u1"
                ]
            ),
            "external_side_matches_only_the_graded_shadow_of_the_transport_162_sector": (
                family_flag_visibility_obstruction["family_flag_visibility_obstruction_theorem"][
                    "external_side_matches_only_the_graded_shadow_of_the_transport_162_sector"
                ]
            ),
            "exact_external_identification_of_the_internal_common_line_is_not_yet_supported": (
                family_flag_visibility_obstruction["family_flag_visibility_obstruction_theorem"][
                    "exact_external_identification_of_the_internal_common_line_is_not_yet_supported"
                ]
            ),
            "exact_external_identification_of_the_internal_transport_extension_is_not_yet_supported": (
                family_flag_visibility_obstruction["family_flag_visibility_obstruction_theorem"][
                    "exact_external_identification_of_the_internal_transport_extension_is_not_yet_supported"
                ]
            ),
            "current_bridge_fixes_plane_line_candidate_and_graded_shadow_but_not_full_extension_object": (
                family_flag_visibility_obstruction["family_flag_visibility_obstruction_theorem"][
                    "current_bridge_fixes_plane_line_candidate_and_graded_shadow_but_not_full_extension_object"
                ]
            ),
        },
        "e13_visibility_obstruction_bridge": {
            "internal_common_square": e13_visibility_obstruction["internal_common_square"],
            "internal_common_line_generator": (
                e13_visibility_obstruction["internal_common_line_generator"]
            ),
            "external_canonical_carrier_plane": (
                e13_visibility_obstruction["external_canonical_carrier_plane"]
            ),
            "external_canonical_line_candidate": (
                e13_visibility_obstruction["external_canonical_line_candidate"]
            ),
            "external_graded_shadow": (
                e13_visibility_obstruction["external_graded_shadow"]
            ),
            "internal_common_square_is_exact_central_2e13_channel": (
                e13_visibility_obstruction["e13_visibility_obstruction_theorem"][
                    "internal_common_square_is_exact_central_2e13_channel"
                ]
            ),
            "image_of_the_common_square_is_the_internal_common_line": (
                e13_visibility_obstruction["e13_visibility_obstruction_theorem"][
                    "image_of_the_common_square_is_the_internal_common_line"
                ]
            ),
            "current_external_bridge_fixes_the_canonical_u1_carrier_plane": (
                e13_visibility_obstruction["e13_visibility_obstruction_theorem"][
                    "current_external_bridge_fixes_the_canonical_u1_carrier_plane"
                ]
            ),
            "current_external_bridge_picks_a_canonical_line_candidate_for_the_e13_image": (
                e13_visibility_obstruction["e13_visibility_obstruction_theorem"][
                    "current_external_bridge_picks_a_canonical_line_candidate_for_the_e13_image"
                ]
            ),
            "exact_external_identification_of_the_e13_image_with_the_internal_common_line_is_not_yet_supported": (
                e13_visibility_obstruction["e13_visibility_obstruction_theorem"][
                    "exact_external_identification_of_the_e13_image_with_the_internal_common_line_is_not_yet_supported"
                ]
            ),
            "current_external_bridge_matches_only_the_graded_shadow_of_the_transport_channel": (
                e13_visibility_obstruction["e13_visibility_obstruction_theorem"][
                    "current_external_bridge_matches_only_the_graded_shadow_of_the_transport_channel"
                ]
            ),
            "current_bridge_captures_carrier_plane_line_candidate_and_graded_shadow_of_the_central_channel": (
                e13_visibility_obstruction["e13_visibility_obstruction_theorem"][
                    "current_bridge_captures_carrier_plane_line_candidate_and_graded_shadow_of_the_central_channel"
                ]
            ),
            "exact_external_realization_of_the_central_2e13_channel_is_not_yet_supported": (
                e13_visibility_obstruction["e13_visibility_obstruction_theorem"][
                    "exact_external_realization_of_the_central_2e13_channel_is_not_yet_supported"
                ]
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
        "mod7_fano_duality_bridge": {
            "quadratic_residues": mod7_fano_duality["mod7_dictionary"]["quadratic_residues"],
            "quadratic_nonresidues": mod7_fano_duality["mod7_dictionary"]["quadratic_nonresidues"],
            "decimal_generator_mod_7": mod7_fano_duality["mod7_dictionary"]["decimal_generator_mod_7"],
            "decimal_square_mod_7": mod7_fano_duality["mod7_dictionary"]["decimal_square_mod_7"],
            "decimal_generator_order": mod7_fano_duality["mod7_dictionary"]["decimal_generator_order"],
            "point_cycle_type": mod7_fano_duality["mod7_dictionary"]["point_cycle_type"],
            "affine_group_order": mod7_fano_duality["affine_group"]["full_affine_group_order"],
            "heptad_preserver_subgroup_order": mod7_fano_duality["affine_group"]["heptad_preserver_subgroup_order"],
            "heptad_duality_coset_order": mod7_fano_duality["affine_group"]["heptad_duality_coset_order"],
            "decimal_and_translation_generate_full_affine_group": mod7_fano_duality["affine_group"]["decimal_and_translation_generate_full_affine_group"],
            "residues_preserve_each_heptad": mod7_fano_duality["heptad_action"]["residues_preserve_each_heptad"],
            "nonresidues_swap_heptads": mod7_fano_duality["heptad_action"]["nonresidues_swap_heptads"],
            "decimal_power_targets_on_A": mod7_fano_duality["decimal_duality_bridge"]["decimal_power_targets_on_A"],
            "odd_decimal_powers_swap_heptads": mod7_fano_duality["decimal_duality_bridge"]["odd_decimal_powers_swap_heptads"],
            "even_decimal_powers_preserve_heptads": mod7_fano_duality["decimal_duality_bridge"]["even_decimal_powers_preserve_heptads"],
            "c6_splits_into_c3_and_z2_shadow": mod7_fano_duality["decimal_duality_bridge"]["c6_splits_into_c3_and_z2_shadow"],
        },
        "mobius_szilassi_dual_bridge": {
            "dual_vertex_count": mobius_dual["summary"]["dual_vertex_count"],
            "dual_edge_count": mobius_dual["summary"]["dual_edge_count"],
            "dual_face_count": mobius_dual["summary"]["dual_face_count"],
            "dual_face_size": mobius_dual["summary"]["dual_face_size"],
            "dual_is_heawood_skeleton": mobius_dual["heawood_checks"]["matches_shifted_fano_lines"],
            "dual_face_adjacency_is_k7": mobius_dual["szilassi_checks"]["complete_face_adjacency_k7"],
        },
        "surface_congruence_selector_bridge": {
            "vertex_integral_residues_mod_12": surface_congruence_selector["surface_selector"]["vertex_integral_residues_mod_12"],
            "face_integral_residues_mod_12": surface_congruence_selector["surface_selector"]["face_integral_residues_mod_12"],
            "admissible_residues_are_0_3_4_7": surface_congruence_selector["surface_selector"]["admissible_residues_are_0_3_4_7"],
            "tetrahedron_fixed_point_value": surface_congruence_selector["fixed_and_first_torus_values"]["tetrahedron_fixed_point_value"],
            "tetrahedron_is_self_dual_fixed_point": surface_congruence_selector["fixed_and_first_torus_values"]["tetrahedron_is_self_dual_fixed_point"],
            "first_toroidal_dual_value": surface_congruence_selector["fixed_and_first_torus_values"]["first_toroidal_dual_value"],
            "csaszar_and_szilassi_share_first_toroidal_value": surface_congruence_selector["fixed_and_first_torus_values"]["csaszar_and_szilassi_share_first_toroidal_value"],
        },
        "heawood_harmonic_bridge": {
            "selector_eigenvalues_exact": heawood_harmonic["incidence_operator"]["selector_eigenvalues_exact"],
            "adjacency_minimal_polynomial": heawood_harmonic["heawood_operator"]["adjacency_minimal_polynomial"],
            "adjacency_quartic_relation_holds": heawood_harmonic["heawood_operator"]["adjacency_quartic_relation_holds"],
            "laplacian_gap_exact": heawood_harmonic["heawood_operator"]["laplacian_gap_exact"],
            "tetra_weight_for_same_gap_exact": heawood_harmonic["local_normalization"]["tetra_weight_for_same_gap_exact"],
            "weighted_tetra_nonzero_laplacian_equals_heawood_gap": heawood_harmonic["local_normalization"]["weighted_tetra_nonzero_laplacian_equals_heawood_gap"],
        },
        "heawood_tetra_radical_bridge": {
            "full_laplacian_minimal_polynomial": heawood_tetra_radical["heawood_middle_shell"]["full_laplacian_minimal_polynomial"],
            "middle_shell_dimension": heawood_tetra_radical["heawood_middle_shell"]["middle_shell_dimension"],
            "middle_quadratic_polynomial": heawood_tetra_radical["heawood_middle_shell"]["middle_quadratic_polynomial"],
            "middle_quadratic_relation_holds": heawood_tetra_radical["heawood_middle_shell"]["middle_quadratic_relation_holds"],
            "middle_branch_eigenvalues_exact": heawood_tetra_radical["heawood_middle_shell"]["middle_branch_eigenvalues_exact"],
            "middle_branch_multiplicity_each": heawood_tetra_radical["heawood_middle_shell"]["middle_branch_multiplicity_each"],
            "middle_shell_trace_exact": heawood_tetra_radical["heawood_middle_shell"]["middle_shell_trace_exact"],
            "middle_shell_pseudodeterminant_exact": heawood_tetra_radical["heawood_middle_shell"]["middle_shell_pseudodeterminant_exact"],
            "projector_three_rank": heawood_tetra_radical["heawood_spectral_projectors"]["projector_three_rank"],
            "projector_sqrt2_rank": heawood_tetra_radical["heawood_spectral_projectors"]["projector_sqrt2_rank"],
            "low_shell_projector_rank": heawood_tetra_radical["heawood_spectral_projectors"]["low_shell_projector_rank"],
            "weighted_tetra_branch_weights_exact": heawood_tetra_radical["klein_tetra_local_packet"]["weighted_tetra_branch_weights_exact"],
            "weighted_tetra_minus_spectrum_exact": heawood_tetra_radical["klein_tetra_local_packet"]["weighted_tetra_minus_spectrum_exact"],
            "weighted_tetra_plus_spectrum_exact": heawood_tetra_radical["klein_tetra_local_packet"]["weighted_tetra_plus_spectrum_exact"],
            "middle_shell_dimension_equals_gauge_dimension": heawood_tetra_radical["exact_factorizations"]["middle_shell_dimension_equals_gauge_dimension"],
            "low_shell_rank_equals_toroidal_seed_order": heawood_tetra_radical["exact_factorizations"]["low_shell_rank_equals_toroidal_seed_order"],
            "middle_branch_product_equals_phi6": heawood_tetra_radical["exact_factorizations"]["middle_branch_product_equals_phi6"],
            "weighted_klein_tetra_minus_realizes_middle_minus_branch": heawood_tetra_radical["exact_factorizations"]["weighted_klein_tetra_minus_realizes_middle_minus_branch"],
            "weighted_klein_tetra_plus_realizes_middle_plus_branch": heawood_tetra_radical["exact_factorizations"]["weighted_klein_tetra_plus_realizes_middle_plus_branch"],
        },
        "heawood_klein_symmetry_bridge": {
            "bipartition_preserving_order": heawood_klein_symmetry["bipartition_preserving_symmetry"]["heawood_bipartition_preserving_order"],
            "full_heawood_order": heawood_klein_symmetry["full_symmetry"]["full_heawood_automorphism_order"],
            "flag_edge_stabilizer_order": heawood_klein_symmetry["bipartition_preserving_symmetry"]["flag_edge_stabilizer_order"],
            "full_edge_stabilizer_order": heawood_klein_symmetry["full_symmetry"]["edge_stabilizer_order"],
            "polarity_formula": heawood_klein_symmetry["point_line_duality"]["polarity_formula"],
            "polarity_permutation": heawood_klein_symmetry["point_line_duality"]["polarity_permutation"],
            "polarity_is_incidence_duality": heawood_klein_symmetry["point_line_duality"]["polarity_is_incidence_duality"],
            "polarity_swap_is_involution": heawood_klein_symmetry["point_line_duality"]["polarity_swap_is_involution"],
            "matches_klein_quartic_orientation_preserving_order": heawood_klein_symmetry["klein_quartic_bridge"]["matches_klein_quartic_orientation_preserving_order"],
            "full_heawood_order_is_double_klein_order": heawood_klein_symmetry["klein_quartic_bridge"]["full_heawood_order_is_double_klein_order"],
            "preserving_order_equals_8_times_21": heawood_klein_symmetry["klein_quartic_bridge"]["preserving_order_equals_8_times_21"],
            "full_order_equals_16_times_21": heawood_klein_symmetry["klein_quartic_bridge"]["full_order_equals_16_times_21"],
        },
        "heawood_shell_ladder_bridge": {
            "heptad_size": heawood_shell_ladder["heawood_shell_dictionary"]["heptad_size"],
            "phi6": heawood_shell_ladder["heawood_shell_dictionary"]["phi6"],
            "heawood_vertices": heawood_shell_ladder["heawood_shell_dictionary"]["heawood_vertices"],
            "g2_dimension": heawood_shell_ladder["heawood_shell_dictionary"]["g2_dimension"],
            "heawood_edges": heawood_shell_ladder["heawood_shell_dictionary"]["heawood_edges"],
            "ag21_length": heawood_shell_ladder["heawood_shell_dictionary"]["ag21_length"],
            "hurwitz_unit_order": heawood_shell_ladder["heawood_shell_dictionary"]["hurwitz_unit_order"],
            "d4_seed_order": heawood_shell_ladder["heawood_shell_dictionary"]["d4_seed_order"],
            "affine_order": heawood_shell_ladder["heawood_shell_dictionary"]["affine_order"],
            "preserving_order": heawood_shell_ladder["heawood_shell_dictionary"]["preserving_order"],
            "full_order": heawood_shell_ladder["heawood_shell_dictionary"]["full_order"],
            "vertices_equal_2_times_phi6": heawood_shell_ladder["exact_factorizations"]["vertices_equal_2_times_phi6"],
            "vertices_equal_g2_dimension": heawood_shell_ladder["exact_factorizations"]["vertices_equal_g2_dimension"],
            "edges_equal_ag21_length": heawood_shell_ladder["exact_factorizations"]["edges_equal_ag21_length"],
            "affine_order_equals_2_times_ag21": heawood_shell_ladder["exact_factorizations"]["affine_order_equals_2_times_ag21"],
            "preserving_order_equals_hurwitz_units_times_phi6": heawood_shell_ladder["exact_factorizations"]["preserving_order_equals_hurwitz_units_times_phi6"],
            "preserving_order_equals_d4_seed_times_phi6": heawood_shell_ladder["exact_factorizations"]["preserving_order_equals_d4_seed_times_phi6"],
            "full_order_equals_hurwitz_units_times_g2_dimension": heawood_shell_ladder["exact_factorizations"]["full_order_equals_hurwitz_units_times_g2_dimension"],
            "full_order_equals_d4_seed_times_g2_dimension": heawood_shell_ladder["exact_factorizations"]["full_order_equals_d4_seed_times_g2_dimension"],
            "full_order_equals_affine_order_times_preserving_edge_stabilizer": heawood_shell_ladder["exact_factorizations"]["full_order_equals_affine_order_times_preserving_edge_stabilizer"],
        },
        "klein_quartic_gf3_tetra_bridge": {
            "field": klein_quartic_gf3_tetra["gf3_klein_quartic_packet"]["field"],
            "point_count": klein_quartic_gf3_tetra["gf3_klein_quartic_packet"]["point_count"],
            "projective_points": klein_quartic_gf3_tetra["gf3_klein_quartic_packet"]["projective_points"],
            "point_count_equals_q_plus_1": klein_quartic_gf3_tetra["gf3_klein_quartic_packet"]["point_count_equals_q_plus_1"],
            "point_count_equals_mu": klein_quartic_gf3_tetra["gf3_klein_quartic_packet"]["point_count_equals_mu"],
            "no_three_points_are_collinear": klein_quartic_gf3_tetra["gf3_klein_quartic_packet"]["no_three_points_are_collinear"],
            "induced_projective_packet_is_k4": klein_quartic_gf3_tetra["gf3_klein_quartic_packet"]["induced_projective_packet_is_k4"],
            "point_count_matches_surface_fixed_point": klein_quartic_gf3_tetra["surface_and_hurwitz_dictionary"]["point_count_matches_surface_fixed_point"],
            "tetra_automorphism_order_matches_hurwitz_units": klein_quartic_gf3_tetra["surface_and_hurwitz_dictionary"]["tetra_automorphism_order_matches_hurwitz_units"],
        },
        "surface_hurwitz_flag_bridge": {
            "q": surface_hurwitz_flag["surface_hurwitz_dictionary"]["q"],
            "q_plus_one": surface_hurwitz_flag["surface_hurwitz_dictionary"]["q_plus_one"],
            "phi6": surface_hurwitz_flag["surface_hurwitz_dictionary"]["phi6"],
            "genus_denominator": surface_hurwitz_flag["surface_hurwitz_dictionary"]["genus_denominator"],
            "tetrahedron_fixed_point": surface_hurwitz_flag["surface_hurwitz_dictionary"]["tetrahedron_fixed_point"],
            "nonzero_surface_residues_mod_12": surface_hurwitz_flag["surface_hurwitz_dictionary"]["nonzero_surface_residues_mod_12"],
            "single_surface_flags": surface_hurwitz_flag["surface_hurwitz_dictionary"]["single_surface_flags"],
            "dual_pair_flags": surface_hurwitz_flag["surface_hurwitz_dictionary"]["dual_pair_flags"],
            "heawood_preserving_order": surface_hurwitz_flag["surface_hurwitz_dictionary"]["heawood_preserving_order"],
            "heawood_full_order": surface_hurwitz_flag["surface_hurwitz_dictionary"]["heawood_full_order"],
            "heawood_vertices": surface_hurwitz_flag["surface_hurwitz_dictionary"]["heawood_vertices"],
            "heawood_edges": surface_hurwitz_flag["surface_hurwitz_dictionary"]["heawood_edges"],
            "shared_six_channel": surface_hurwitz_flag["surface_hurwitz_dictionary"]["shared_six_channel"],
            "nonzero_surface_residues_are_q_q_plus_one_phi6": surface_hurwitz_flag["exact_factorizations"]["nonzero_surface_residues_are_q_q_plus_one_phi6"],
            "nonzero_surface_residues_add_to_phi6": surface_hurwitz_flag["exact_factorizations"]["nonzero_surface_residues_add_to_phi6"],
            "single_surface_flags_equals_product_of_nonzero_surface_residues": surface_hurwitz_flag["exact_factorizations"]["single_surface_flags_equals_product_of_nonzero_surface_residues"],
            "single_surface_flags_equals_genus_denominator_times_phi6": surface_hurwitz_flag["exact_factorizations"]["single_surface_flags_equals_genus_denominator_times_phi6"],
            "single_surface_flags_equals_heawood_vertices_times_shared_six": surface_hurwitz_flag["exact_factorizations"]["single_surface_flags_equals_heawood_vertices_times_shared_six"],
            "single_surface_flags_equals_heawood_edges_times_tetrahedron_fixed_point": surface_hurwitz_flag["exact_factorizations"]["single_surface_flags_equals_heawood_edges_times_tetrahedron_fixed_point"],
            "dual_pair_flags_equals_heawood_preserving_order": surface_hurwitz_flag["exact_factorizations"]["dual_pair_flags_equals_heawood_preserving_order"],
            "full_heawood_order_equals_four_single_surface_flag_packets": surface_hurwitz_flag["exact_factorizations"]["full_heawood_order_equals_four_single_surface_flag_packets"],
            "q3_is_unique_positive_solution": surface_hurwitz_flag["q3_selection"]["q3_is_unique_positive_solution"],
        },
        "mod12_selector_closure_bridge": {
            "modulus": mod12_selector_closure["mod12_selector_dictionary"]["modulus"],
            "nonzero_surface_residues_mod_12": mod12_selector_closure["mod12_selector_dictionary"]["nonzero_surface_residues_mod_12"],
            "q": mod12_selector_closure["mod12_selector_dictionary"]["q"],
            "mu": mod12_selector_closure["mod12_selector_dictionary"]["mu"],
            "phi6": mod12_selector_closure["mod12_selector_dictionary"]["phi6"],
            "theta_w33": mod12_selector_closure["mod12_selector_dictionary"]["theta_w33"],
            "k_minus_one": mod12_selector_closure["mod12_selector_dictionary"]["k_minus_one"],
            "g2_dimension": mod12_selector_closure["mod12_selector_dictionary"]["g2_dimension"],
            "single_surface_flags": mod12_selector_closure["mod12_selector_dictionary"]["single_surface_flags"],
            "residues_equal_q_mu_phi6": mod12_selector_closure["exact_closures"]["residues_equal_q_mu_phi6"],
            "q_plus_mu_equals_phi6": mod12_selector_closure["exact_closures"]["q_plus_mu_equals_phi6"],
            "q_plus_phi6_equals_theta": mod12_selector_closure["exact_closures"]["q_plus_phi6_equals_theta"],
            "mu_plus_phi6_equals_k_minus_one": mod12_selector_closure["exact_closures"]["mu_plus_phi6_equals_k_minus_one"],
            "q_plus_mu_plus_phi6_equals_g2_dimension": mod12_selector_closure["exact_closures"]["q_plus_mu_plus_phi6_equals_g2_dimension"],
            "q_times_mu_times_phi6_equals_single_surface_flags": mod12_selector_closure["exact_closures"]["q_times_mu_times_phi6_equals_single_surface_flags"],
            "modulus_equals_gauge_dimension": mod12_selector_closure["exact_closures"]["modulus_equals_gauge_dimension"],
        },
        "decimal_surface_flag_bridge": {
            "decimal_generator_mod_7": decimal_surface_flag["decimal_surface_dictionary"]["decimal_generator_mod_7"],
            "decimal_generator_order_mod_7": decimal_surface_flag["decimal_surface_dictionary"]["decimal_generator_order_mod_7"],
            "decimal_square_order_mod_7": decimal_surface_flag["decimal_surface_dictionary"]["decimal_square_order_mod_7"],
            "genus_denominator": decimal_surface_flag["decimal_surface_dictionary"]["genus_denominator"],
            "first_toroidal_dual_value": decimal_surface_flag["decimal_surface_dictionary"]["first_toroidal_dual_value"],
            "phi6": decimal_surface_flag["decimal_surface_dictionary"]["phi6"],
            "heawood_vertices": decimal_surface_flag["decimal_surface_dictionary"]["heawood_vertices"],
            "heawood_edges": decimal_surface_flag["decimal_surface_dictionary"]["heawood_edges"],
            "tetrahedral_fixed_point": decimal_surface_flag["decimal_surface_dictionary"]["tetrahedral_fixed_point"],
            "shared_six_channel": decimal_surface_flag["decimal_surface_dictionary"]["shared_six_channel"],
            "single_surface_flags": decimal_surface_flag["decimal_surface_dictionary"]["single_surface_flags"],
            "decimal_order_equals_shared_six_channel": decimal_surface_flag["exact_factorizations"]["decimal_order_equals_shared_six_channel"],
            "single_surface_flags_equals_12_times_7": decimal_surface_flag["exact_factorizations"]["single_surface_flags_equals_12_times_7"],
            "single_surface_flags_equals_14_times_6": decimal_surface_flag["exact_factorizations"]["single_surface_flags_equals_14_times_6"],
            "single_surface_flags_equals_21_times_4": decimal_surface_flag["exact_factorizations"]["single_surface_flags_equals_21_times_4"],
            "decimal_order_plus_one_equals_first_toroidal_value": decimal_surface_flag["exact_factorizations"]["decimal_order_plus_one_equals_first_toroidal_value"],
        },
        "surface_physics_shell_bridge": {
            "gauge_dimension": surface_physics_shell["standard_model_gauge_dictionary"]["gauge_dimension"],
            "gauge_dimension_decomposition": surface_physics_shell["standard_model_gauge_dictionary"]["gauge_dimension_decomposition"],
            "beta0_qcd": surface_physics_shell["standard_model_gauge_dictionary"]["beta0_qcd"],
            "shared_six_channel": surface_physics_shell["standard_model_gauge_dictionary"]["shared_six_channel"],
            "g2_dimension": surface_physics_shell["standard_model_gauge_dictionary"]["g2_dimension"],
            "topological_shell": surface_physics_shell["standard_model_gauge_dictionary"]["topological_shell"],
            "quartic_e7_packet": surface_physics_shell["standard_model_gauge_dictionary"]["quartic_e7_packet"],
            "single_surface_flags": surface_physics_shell["surface_physics_shell_dictionary"]["single_surface_flags"],
            "dual_pair_flags": surface_physics_shell["surface_physics_shell_dictionary"]["dual_pair_flags"],
            "full_heawood_order": surface_physics_shell["surface_physics_shell_dictionary"]["full_heawood_order"],
            "gauge_dimension_equals_8_plus_3_plus_1": surface_physics_shell["exact_factorizations"]["gauge_dimension_equals_8_plus_3_plus_1"],
            "single_surface_flags_equals_gauge_dimension_times_beta0": surface_physics_shell["exact_factorizations"]["single_surface_flags_equals_gauge_dimension_times_beta0"],
            "single_surface_flags_equals_g2_dimension_times_shared_six": surface_physics_shell["exact_factorizations"]["single_surface_flags_equals_g2_dimension_times_shared_six"],
            "dual_pair_flags_equals_gauge_dimension_times_g2_dimension": surface_physics_shell["exact_factorizations"]["dual_pair_flags_equals_gauge_dimension_times_g2_dimension"],
            "dual_pair_flags_equals_shared_six_times_topological_shell": surface_physics_shell["exact_factorizations"]["dual_pair_flags_equals_shared_six_times_topological_shell"],
            "full_heawood_order_equals_gauge_dimension_times_topological_shell": surface_physics_shell["exact_factorizations"]["full_heawood_order_equals_gauge_dimension_times_topological_shell"],
            "full_heawood_order_equals_shared_six_times_quartic_e7_packet": surface_physics_shell["exact_factorizations"]["full_heawood_order_equals_shared_six_times_quartic_e7_packet"],
        },
        "toroidal_k7_spectral_bridge": {
            "toroidal_seed_order": toroidal_k7_spectral["toroidal_k7_dictionary"]["toroidal_seed_order"],
            "csaszar_vertex_graph": toroidal_k7_spectral["toroidal_k7_dictionary"]["csaszar_vertex_graph"],
            "szilassi_face_graph": toroidal_k7_spectral["toroidal_k7_dictionary"]["szilassi_face_graph"],
            "adjacency_spectrum": toroidal_k7_spectral["toroidal_k7_dictionary"]["adjacency_spectrum"],
            "laplacian_spectrum": toroidal_k7_spectral["toroidal_k7_dictionary"]["laplacian_spectrum"],
            "selector_line_dimension": toroidal_k7_spectral["toroidal_k7_dictionary"]["selector_line_dimension"],
            "shared_six_channel": toroidal_k7_spectral["toroidal_k7_dictionary"]["shared_six_channel"],
            "phi6": toroidal_k7_spectral["toroidal_k7_dictionary"]["phi6"],
            "adjacency_square_trace": toroidal_k7_spectral["toroidal_k7_dictionary"]["adjacency_square_trace"],
            "laplacian_trace": toroidal_k7_spectral["toroidal_k7_dictionary"]["laplacian_trace"],
            "csaszar_vertex_graph_is_k7": toroidal_k7_spectral["exact_factorizations"]["csaszar_vertex_graph_is_k7"],
            "szilassi_face_graph_is_k7": toroidal_k7_spectral["exact_factorizations"]["szilassi_face_graph_is_k7"],
            "selector_plus_shared_six_equals_toroidal_seed_order": toroidal_k7_spectral["exact_factorizations"]["selector_plus_shared_six_equals_toroidal_seed_order"],
            "nontrivial_laplacian_mode_equals_phi6": toroidal_k7_spectral["exact_factorizations"]["nontrivial_laplacian_mode_equals_phi6"],
            "nontrivial_adjacency_multiplicity_equals_shared_six": toroidal_k7_spectral["exact_factorizations"]["nontrivial_adjacency_multiplicity_equals_shared_six"],
            "laplacian_trace_equals_shared_six_times_phi6": toroidal_k7_spectral["exact_factorizations"]["laplacian_trace_equals_shared_six_times_phi6"],
            "adjacency_square_trace_equals_shared_six_times_phi6": toroidal_k7_spectral["exact_factorizations"]["adjacency_square_trace_equals_shared_six_times_phi6"],
        },
        "fano_toroidal_complement_bridge": {
            "space_dimension": fano_toroidal_complement["operator_dictionary"]["space_dimension"],
            "fano_selector_formula": fano_toroidal_complement["operator_dictionary"]["fano_selector_formula"],
            "toroidal_laplacian_formula": fano_toroidal_complement["operator_dictionary"]["toroidal_laplacian_formula"],
            "complement_formula": fano_toroidal_complement["operator_dictionary"]["complement_formula"],
            "q_squared": fano_toroidal_complement["operator_dictionary"]["q_squared"],
            "selector_spectrum_exact": fano_toroidal_complement["operator_dictionary"]["selector_spectrum_exact"],
            "toroidal_laplacian_spectrum_exact": fano_toroidal_complement["operator_dictionary"]["toroidal_laplacian_spectrum_exact"],
            "selector_trace": fano_toroidal_complement["operator_dictionary"]["selector_trace"],
            "selector_nontrivial_trace": fano_toroidal_complement["operator_dictionary"]["selector_nontrivial_trace"],
            "toroidal_trace": fano_toroidal_complement["operator_dictionary"]["toroidal_trace"],
            "combined_trace": fano_toroidal_complement["operator_dictionary"]["combined_trace"],
            "combined_nontrivial_trace": fano_toroidal_complement["operator_dictionary"]["combined_nontrivial_trace"],
            "selector_determinant": fano_toroidal_complement["operator_dictionary"]["selector_determinant"],
            "selector_determinant_square_root": fano_toroidal_complement["operator_dictionary"]["selector_determinant_square_root"],
            "selector_minimal_polynomial": fano_toroidal_complement["operator_dictionary"]["selector_minimal_polynomial"],
            "complement_operator_equals_q_squared_identity": fano_toroidal_complement["exact_factorizations"]["complement_operator_equals_q_squared_identity"],
            "selector_trace_equals_ag21_length": fano_toroidal_complement["exact_factorizations"]["selector_trace_equals_ag21_length"],
            "selector_nontrivial_trace_equals_gauge_dimension": fano_toroidal_complement["exact_factorizations"]["selector_nontrivial_trace_equals_gauge_dimension"],
            "toroidal_trace_equals_6_times_phi6": fano_toroidal_complement["exact_factorizations"]["toroidal_trace_equals_6_times_phi6"],
            "combined_nontrivial_trace_equals_exceptional_projector_rank": fano_toroidal_complement["exact_factorizations"]["combined_nontrivial_trace_equals_exceptional_projector_rank"],
            "selector_determinant_square_root_equals_hurwitz_unit_shell": fano_toroidal_complement["exact_factorizations"]["selector_determinant_square_root_equals_hurwitz_unit_shell"],
            "selector_quadratic_matches_heawood_quartic_in_x_squared": fano_toroidal_complement["exact_factorizations"]["selector_quadratic_matches_heawood_quartic_in_x_squared"],
            "gauge_plus_toroidal_equals_exceptional_rank": fano_toroidal_complement["exact_factorizations"]["gauge_plus_toroidal_equals_exceptional_rank"],
        },
        "klein_hurwitz_extremal_bridge": {
            "klein_quartic_genus": klein_hurwitz_extremal["hurwitz_extremal_dictionary"]["klein_quartic_genus"],
            "hurwitz_coefficient": klein_hurwitz_extremal["hurwitz_extremal_dictionary"]["hurwitz_coefficient"],
            "heawood_preserving_order": klein_hurwitz_extremal["hurwitz_extremal_dictionary"]["heawood_preserving_order"],
            "heawood_full_order": klein_hurwitz_extremal["hurwitz_extremal_dictionary"]["heawood_full_order"],
            "standard_model_gauge_dimension": klein_hurwitz_extremal["hurwitz_extremal_dictionary"]["standard_model_gauge_dimension"],
            "phi6": klein_hurwitz_extremal["hurwitz_extremal_dictionary"]["phi6"],
            "g2_dimension": klein_hurwitz_extremal["hurwitz_extremal_dictionary"]["g2_dimension"],
            "preserving_order_equals_hurwitz_bound_at_genus_3": klein_hurwitz_extremal["exact_factorizations"]["preserving_order_equals_hurwitz_bound_at_genus_3"],
            "preserving_order_equals_two_times_hurwitz_coefficient": klein_hurwitz_extremal["exact_factorizations"]["preserving_order_equals_two_times_hurwitz_coefficient"],
            "preserving_order_equals_2_k_phi6": klein_hurwitz_extremal["exact_factorizations"]["preserving_order_equals_2_k_phi6"],
            "preserving_order_equals_k_times_g2_dimension": klein_hurwitz_extremal["exact_factorizations"]["preserving_order_equals_k_times_g2_dimension"],
            "full_order_equals_two_times_preserving_order": klein_hurwitz_extremal["exact_factorizations"]["full_order_equals_two_times_preserving_order"],
            "full_order_equals_four_times_hurwitz_coefficient": klein_hurwitz_extremal["exact_factorizations"]["full_order_equals_four_times_hurwitz_coefficient"],
        },
        "hurwitz_237_selector_bridge": {
            "triangle_signature": hurwitz_237_selector["hurwitz_237_dictionary"]["triangle_signature"],
            "duality_sheet_flip_order": hurwitz_237_selector["hurwitz_237_dictionary"]["duality_sheet_flip_order"],
            "q": hurwitz_237_selector["hurwitz_237_dictionary"]["q"],
            "phi6": hurwitz_237_selector["hurwitz_237_dictionary"]["phi6"],
            "affine_shell_order": hurwitz_237_selector["hurwitz_237_dictionary"]["affine_shell_order"],
            "single_surface_flags": hurwitz_237_selector["hurwitz_237_dictionary"]["single_surface_flags"],
            "heawood_preserving_order": hurwitz_237_selector["hurwitz_237_dictionary"]["heawood_preserving_order"],
            "heawood_full_order": hurwitz_237_selector["hurwitz_237_dictionary"]["heawood_full_order"],
            "affine_shell_equals_2_3_7": hurwitz_237_selector["exact_factorizations"]["affine_shell_equals_2_3_7"],
            "affine_shell_is_agl_1_7": hurwitz_237_selector["exact_factorizations"]["affine_shell_is_agl_1_7"],
            "decimal_c6_splits_into_c3_and_z2": hurwitz_237_selector["exact_factorizations"]["decimal_c6_splits_into_c3_and_z2"],
            "single_surface_flags_equals_2_times_affine_shell": hurwitz_237_selector["exact_factorizations"]["single_surface_flags_equals_2_times_affine_shell"],
            "heawood_preserving_equals_4_times_affine_shell": hurwitz_237_selector["exact_factorizations"]["heawood_preserving_equals_4_times_affine_shell"],
            "heawood_full_equals_8_times_affine_shell": hurwitz_237_selector["exact_factorizations"]["heawood_full_equals_8_times_affine_shell"],
        },
        "affine_middle_shell_bridge": {
            "duality_factor": affine_middle_shell["affine_middle_shell_dictionary"]["duality_factor"],
            "q": affine_middle_shell["affine_middle_shell_dictionary"]["q"],
            "phi6": affine_middle_shell["affine_middle_shell_dictionary"]["phi6"],
            "ag21_length": affine_middle_shell["affine_middle_shell_dictionary"]["ag21_length"],
            "g2_dimension": affine_middle_shell["affine_middle_shell_dictionary"]["g2_dimension"],
            "shared_six_channel": affine_middle_shell["affine_middle_shell_dictionary"]["shared_six_channel"],
            "affine_shell_order": affine_middle_shell["affine_middle_shell_dictionary"]["affine_shell_order"],
            "affine_shell_equals_2_times_ag21": affine_middle_shell["exact_factorizations"]["affine_shell_equals_2_times_ag21"],
            "affine_shell_equals_q_times_g2": affine_middle_shell["exact_factorizations"]["affine_shell_equals_q_times_g2"],
            "affine_shell_equals_shared_six_times_phi6": affine_middle_shell["exact_factorizations"]["affine_shell_equals_shared_six_times_phi6"],
            "ag21_equals_3_times_phi6": affine_middle_shell["exact_factorizations"]["ag21_equals_3_times_phi6"],
            "g2_equals_2_times_phi6": affine_middle_shell["exact_factorizations"]["g2_equals_2_times_phi6"],
            "shared_six_equals_2_times_q": affine_middle_shell["exact_factorizations"]["shared_six_equals_2_times_q"],
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
        "tomotope_partial_sheet_bridge": {
            "partial_a": partial_sheet["principal_packets"]["partial_a"],
            "partial_b": partial_sheet["principal_packets"]["partial_b"],
            "entrywise_ratio": partial_sheet["principal_packets"]["entrywise_ratio"],
            "partial_a_equals_two_times_partial_b": partial_sheet["principal_packets"]["partial_a_equals_two_times_partial_b"],
            "partial_b_matches_tomotope_edge_triangle_cell_counts": partial_sheet["live_count_alignment"]["partial_b_matches_tomotope_edge_triangle_cell_counts"],
            "partial_a_matches_universal_edge_triangle_cell_counts": partial_sheet["live_count_alignment"]["partial_a_matches_universal_edge_triangle_cell_counts"],
            "automorphism_ratio_matches_sheet_doubling": partial_sheet["live_count_alignment"]["automorphism_ratio_matches_sheet_doubling"],
            "flag_ratio_matches_sheet_doubling": partial_sheet["live_count_alignment"]["flag_ratio_matches_sheet_doubling"],
            "monodromy_ratio_is_quadratic_not_linear": partial_sheet["live_count_alignment"]["monodromy_ratio_is_quadratic_not_linear"],
        },
        "exceptional_triad_note": exceptional["global_verdict"],
        "combined_verdict": (
            "The missing theorem is no longer a vague 'continuum limit' placeholder. "
            "The finite internal side is exact: the Witting 40-state system is now "
            "identified explicitly with W(3,3) via SRG(40,12,2,4) and 40 orthogonal "
            "tetrads, and the whole 480-dimensional finite Dirac/Hodge spectrum is "
            "now seen to be forced by the same rank-3 adjacency algebra plus the "
            "clique-complex regularities L0 = 12I - A, L2 = 4I, and L3 = 4I, so "
            "the internal spectral-action moments a0 = 480, a2 = 2240, a4 = 17600 "
            "are not a separate fitted package. More sharply, those moments, the "
            "Higgs ratio 2a2/a4 = 14/55, the continuum Einstein-Hilbert coefficient "
            "per internal degree of freedom 2/q, and the discrete 6-mode curvature "
            "coefficient per internal degree of freedom 2Phi_3 are now one exact "
            "cyclotomic law governed by Phi_3 = 13 and Phi_6 = 7, and the matter/Higgs "
            "side now independently selects q = 3 because a2/a0, a4/a0, and 2a2/a4 all "
            "collapse to the same polynomial 3q^2 - 10q + 3. The promoted Standard Model "
            "observables are sharper in the same language: sin^2(theta_W)=tan(theta_C)=3/13, "
            "sin^2(theta_12)=4/13, sin^2(theta_23)=7/13, sin^2(theta_13)=2/91, and "
            "Omega_Lambda=9/13 form one exact Phi_3/Phi_6 Rosetta layer. More strongly, "
            "once q=3 is fixed that whole promoted Standard Model/cosmology package, together "
            "with the Higgs ratio and the promoted internal gravity normalizations, collapses "
            "to a single generator x = sin^2(theta_W) = 3/13. Better, the same x is then "
            "reconstructed independently from Cabibbo, PMNS, Omega_Lambda, the Higgs ratio, "
            "the internal spectral-action moments, and the promoted gravity ratios. More sharply still, "
            "that same promoted package is already a direct SRG law: q = lambda + 1, Phi_3 = k + 1, "
            "and Phi_6 = k - lambda - mu + 1 for SRG(40,12,2,4). Even more tightly, it is a direct "
            "spectral law on the adjacency eigenvalues (k,r,s) = (12,2,-4), with q = r + 1 and "
            "Phi_6 = 1 + r - s. On the curved side, the first product-moment refinement tower is "
            "now not just decomposed but projector-controlled: its characteristic polynomial is "
            "x^3 - 127x^2 + 846x - 720, and exact shift projectors isolate the 120-, 6-, and 1-mode "
            "channels from three successive refinement levels, extracting the same EH coefficient 12480 "
            "for both CP2_9 and K3_16 and the same continuum value 320 after the rank-39 normalization. "
            "The same tower is now also an exact pole theorem: its generating function has only the "
            "120-, 6-, and 1-poles, and the 6-pole residue divided by the seed six-mode recovers the "
            "same 12480 while the 1-pole residue divided by the Euler mode recovers the same 2240. "
            "More sharply still, that continuum value is now an exact three-sample discrete extractor on "
            "the refinement tower itself, and the bridge is no longer scalar-only: 320 = 40*8 is the "
            "exact l6 spinor E6/Cartan base block, the same six-channel core appears as the l6 A2 "
            "support, the transport Weyl(A2) order, the six firewall triplet fibers, and the tomotope "
            "triality factor in 96 = 16*6, and the discrete six-mode factorizes both as 320*39 and as "
            "240*52 = 40*6*52, tying the curved channel directly to the W33 edge/E8-root count and the "
            "F4 tomotope/24-cell route; the residual topological mode likewise factors as 40*56 = 320*7. "
            "Better again, those same 40/6/8 channel numbers now come from a genuine operator theorem: "
            "on End(S_48) the corrected l6 spinor package splits into pairwise Frobenius-orthogonal "
            "projector spaces of exact ranks 40, 6, and 8 for E6, A2, and Cartan, so the curved scalar "
            "coefficients are exact rank dressings of live internal projectors rather than anonymous "
            "counts. Sharper still, those promoted exceptional counts now form a native tensor-rank "
            "dictionary: 240 = 40*6 is the E6/A2 tensor-rank, 320 = 40*8 is the E6/Cartan tensor-rank, "
            "96 = 6*16 is the A2 projector rank times the full A2 transfer-block rank, 12480 = 240*52, "
            "and 2240 = 40*56. Even more sharply, those exact pole residues are already the live exceptional "
            "dictionary: the 6-pole is the E6*A2*F4 channel, the rank-39-normalized 6-pole is the "
            "E6*Cartan continuum EH channel, and the 1-pole is the E6*E7(fund) topological channel. "
            "Better again, the same curved tower now reconstructs the electroweak generator itself: "
            "from any three successive refinement levels one gets x = 9 c_EH / c_6 = 3/13, and the "
            "same identity is already visible in the exceptional residue dictionary as "
            "x = 9(40*8)/(40*6*52). So the curved bridge now recovers the promoted Standard Model "
            "package, not only the gravity channel. Better still, the same curved inputs now reconstruct "
            "the native graph geometry too: q = 3, Phi_3 = 13, Phi_6 = 7, the SRG data "
            "(40,12,2,4), and the adjacency spectrum (12,2,-4). So the curved bridge now recovers "
            "the public observables and the internal Rosetta data in one step. The channel-aware continuum value is an exact three-sample discrete extractor on the "
            "refinement tower itself, and the same extractor is already "
            "bidirectional on the promoted exceptional data. The W33 center-quad quotient then "
            "reconstructs an exact 45-point / "
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
            "The transport side is sharper in exactly the same coefficient "
            "direction: the quotient transport data is now an honest "
            "path-groupoid representation into Weyl(A2), a spanning-tree gauge "
            "trivializes every tree edge so the full nontrivial content sits on "
            "fundamental-cycle holonomy, the real A2 local system has no "
            "nonzero flat section, but after reduction mod 3 it acquires a "
            "unique invariant line with quotient character {1,2}. So the field "
            "F3 is now special on both sides simultaneously: it is the natural "
            "homological coefficient field and the first field on which the "
            "nonabelian transport holonomy itself develops a canonical flat "
            "one-dimensional shadow. The same W33 clique complex therefore "
            "supports a real ternary homological code rather than a binary "
            "analogy: on the 240 edge qutrits the exact mod-3 chain complex has "
            "check ranks 39 and 120, logical dimension 81, and exact primal "
            "logical distance 4 via an explicit nontrivial weight-4 cycle. "
            "More sharply, the reduced transport fiber is now exact as a "
            "non-split local-system extension 0 -> 1 -> rho -> sgn -> 0: the "
            "unique invariant line is trivial, the quotient line carries the "
            "binary sign shadow, and there is no invariant complementary line. "
            "Tensoring that exact extension with H1(W33;F3) therefore forces "
            "0 -> 81 -> 162 -> 81 -> 0. So the 162-dimensional matter-flavour "
            "package is now structural and still matches the exact internal "
            "dimension of the finite spectral-action layer. Better still, the "
            "extension class is now explicit: in adapted basis the off-diagonal "
            "entry is a genuine twisted 1-cocycle, it is not a coboundary "
            "because it is already nonzero on sign-trivial elements, and the "
            "fiber shift N=[[0,1],[0,0]] tensors to a canonical square-zero "
            "rank-81 operator on the 162-dimensional matter extension with "
            "image = kernel = 81. Sharper still, the same transport package is "
            "now known to be genuinely curved on transport triangles: every "
            "triangle carries one of the six reduced A2 holonomy classes, the "
            "naive simplicial extension defect is exactly I - H_t in adapted "
            "basis, it vanishes on exactly 528 identity-holonomy triangles, "
            "and it has rank 1 on the remaining 4752 triangles. Sharper still, "
            "the whole reduced holonomy group is exactly the Borel subgroup "
            "B(F3), so the old parity shadow is just the quotient sign: parity-0 "
            "splits as 528 flat + 2592 pure-nilpotent curved triangles, while "
            "parity-1 = 2160 is the semisimple-curved channel. Better, these "
            "pieces now assemble into the actual transport-twisted precomplex: "
            "in adapted basis the first two covariant coboundaries are upper "
            "triangular, the invariant-line block is the ordinary simplicial "
            "complex with h0 = 1 and h1 = 0, the sign-shadow block is the "
            "genuinely curved channel with no flat 0-sections, and the full "
            "curvature d1 d0 factors through the sign quotient with rank 42 "
            "while the cocycle block supplies the off-diagonal rank-36 coupling. "
            "Tensoring that exact precomplex with the 81-dimensional logical "
            "matter sector then separates the internal 162 package cleanly: one "
            "canonical flat 81-dimensional matter copy survives as the protected "
            "transport-flat sector, while the other 81 copy is curvature-sensitive. "
            "On the external harmonic channels this produces exact protected "
            "flat matter counts 243 for CP2_9 and 1944 for K3_16. Better still, "
            "that protected channel is now selected canonically by transport "
            "spectral data itself: on the base W33 side the adjacency matrix has "
            "rank 39 over F3 with unique null line spanned by the all-ones "
            "vector, and on the exact 45-point transport graph the trivial "
            "Bose-Mesner idempotent (T^2 + 2T - 8I)/1080 = J/45 is the long-time "
            "random-walk / heat selector with exact gap 7/8 and Kemeny constant "
            "1952/45. Because the invariant-line subcomplex has h0 = 1 and the "
            "native A2 sector has positive Laplacian gap 24, tensoring that "
            "selector with the exact 81-qutrit matter sector recovers exactly the "
            "protected flat 81-dimensional matter copy. Better again, the "
            "internally curved transport package itself now crosses the 4D bridge "
            "as a genuine symmetric Dirac-type operator on C0 ⊕ C1 ⊕ C2 of total "
            "dimension 12090, with exact diagonal trace split 3276 + 37386 + "
            "34110 = 74772 and exact curvature corner rank 42. Tensoring with the "
            "81-qutrit matter sector upgrades this to a 979290-dimensional curved "
            "internal operator with Tr(D^2)=6056532, still containing the "
            "canonically protected flat 81-sector and its lifts 243/1944 on "
            "CP2_9/K3_16. Because the curved barycentric tower already has exact "
            "chain and trace densities, this full twisted internal operator now "
            "inherits exact first-order heat-density asymptotics across the whole "
            "CP2/K3 refinement family, with universal limits 1450800/19 and "
            "19370040/19 for the transport Dirac package and 117514800/19 and "
            "1568973240/19 for its matter-coupled lift. Better again, those "
            "first-order bridges are now one exact three-mode law: for any "
            "internal package with moments (a0,a2), the curved barycentric tower "
            "splits the first product moment into a universal 120-mode "
            "cosmological term ((860 a0 + 120 a2)/19), an exact 6-mode "
            "Einstein-Hilbert-like channel (12 a0 + 3 a2), and a residual "
            "1-mode topological term a2. So the full finite 480-dimensional W33 "
            "package, the native A2 product bridge, and the transport-curved "
            "Dirac bridge are all specializations of the same exact curved "
            "convolution theorem. Better still, for the full finite W33 package "
            "that 6-mode coefficient is exactly 39 times the continuum "
            "Einstein-Hilbert coefficient 4a0/6 = 320, with the same factor 39 "
            "appearing simultaneously as V-1, rank(d1), rank_GF(3)(A), and "
            "24+15, the total multiplicity of the nontrivial adjacency "
            "spectrum; while the residual 1-mode is exactly (q^3+1)|chi| = "
            "28*80 = 2240. Sharper still, these are exactly the q=3 cyclotomic "
            "factors q*Phi_3 = 3*13 = 39 and (q+1)*Phi_6 = 4*7 = 28, so the "
            "curved first-order gravity/topology bridge is locked to the same "
            "Phi_3 / Phi_6 arithmetic that already governs the rest of the "
            "program. Better again, those same curved compression laws now give "
            "new q=3 selection theorems: requiring the 6-mode to compress "
            "exactly to 2Phi_3 a0 yields the polynomial "
            "q^3 - 2q^2 - 2q - 3 = (q-3)(q^2+q+1), and requiring the 1-mode to "
            "compress exactly to (q+1)Phi_6|chi| yields "
            "q^2 + q - 12 = (q-3)(q+4). Both therefore select q=3 uniquely among "
            "positive integers. Better again, the same "
            "transport Dirac package now has exact quadratic seed and sd^1 data: "
            "Tr(D^4)=2116184 internally and 171410904 after matter coupling, "
            "seed-level quadratic coefficients 39997843/3 and 36601793/3 on "
            "CP2/K3 for the transport package and 1079941761 and 988248411 for "
            "its matter-coupled lift, and first-refinement coefficients "
            "4701453583/360, 5052856873/360 and 42313082247/40, 45475711857/40. "
            "In both cases the CP2/K3 quadratic gap contracts at sd^1. "
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
            "edge stars, the Klitzing partial-a / partial-b seed rows now add an "
            "exact two-sheet count law (8,24,32,8,8) = 2*(4,12,16,4,4), and that "
            "doubling matches the live edge/triangle/cell and flag ratios even "
            "though the monodromy ratio stays quadratic at 4. More basically, the "
            "surface side already comes with a genuine selector law: the complete-"
            "graph and complete-face genus formulas are integral only in the same "
            "0,3,4,7 mod 12 residue classes, the tetrahedron is the self-dual "
            "fixed point at 4, and 7 is the first positive toroidal dual value. "
            "More sharply, the decimal 1/7 side is already in the same shell: "
            "ord_7(10)=6 and the single-surface packet is exactly "
            "84 = 12*7 = 14*6 = 21*4. More physically, that same packet is already "
            "the promoted selector ladder: 84 = gauge-dimension 12 times beta_0 = 7, "
            "168 = 12*14 = 6*28, and 336 = 12*28 = 6*56, so the torus/Klein route "
            "is packaging the same Standard Model, QCD, topological, and quartic "
            "shell integers that already govern the live W33 physics layer. "
            "More sharply still, that same 84 is the Hurwitz coefficient itself, "
            "so the promoted Heawood/Klein symmetry order 168 is exactly the "
            "genus-3 Hurwitz extremal packet 84(g-1), and the full Heawood order "
            "336 is its doubled point-line extension. "
            "More sharply again, the toroidal dual seed is already an exact K7 "
            "spectral shell on both sides: the Csaszar vertex graph and the "
            "Szilassi face-adjacency graph are both K7, so the shared toroidal "
            "shell has adjacency spectrum 6,(-1)^6 and Laplacian spectrum 0,7^6. "
            "That means the torus route already carries one selector line plus "
            "six identical nontrivial Phi_6 modes, and the compressed affine "
            "packet 42 is recovered as Tr(L_K7) = Tr(A_K7^2) = 6*7. "
            "Even the classical Klein signature is now visible directly in the "
            "live finite shell: the torus affine packet is exactly 42 = 2*3*7, "
            "with 2 the duality sheet flip, 3 the field value q, and 7 the "
            "same Phi_6 / QCD selector already governing the promoted physics "
            "side. More sharply again, that same affine packet is the exact "
            "middle shell 42 = 2*21 = 3*14 = 6*7, so the mod-7 affine route, "
            "the Heawood/AG21 packet, the G2 packet, and the shared "
            "physics-facing six-by-seven selector are already one promoted "
            "object before the lifts to 84, 168, and 336. "
            "The M\"obius/Csaszar torus seed splits exactly as two Fano "
            "heptads on the same 7 vertices, that seed has an explicit Szilassi "
            "dual with Heawood 1-skeleton and K7 face adjacency, and that Heawood "
            "skeleton already carries an exact harmonic packet with selector law "
            "B B^T = 2I + J, quartic relation H^4 - 11H^2 + 18I = 0, and gap "
            "3-sqrt(2). More sharply, its bipartition-preserving automorphism "
            "group is exactly the 168-element Fano collineation group, the explicit "
            "polarity i -> -i mod 7 swaps points and lines, and the full Heawood "
            "automorphism order is therefore 336 = 2*168. More sharply again, the "
            "same torus/Fano route already carries the full shell 7 -> 14 -> 21 -> "
            "42 -> 168 -> 336, where 14 = dim(G2), 21 = AG(2,1), and "
            "336 = 24*14 = 21*16 = 42*8, landing the torus/Fano route directly on "
            "the same D4/G2/Klein-code shell already visible on the quartic side. "
            "More sharply, the projective Klein quartic model over GF(3) already "
            "collapses to the same tetrahedral fixed packet: exactly four projective "
            "points, no three collinear, hence a combinatorial K4 with automorphism "
            "order 24 = |Hurwitz units|. "
            "The seven cataloged Euclidean realizations all share the same Z2 half-turn with "
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
            "Push the coupled transport-matter precomplex one level further into a "
            "native curved spectral-action theorem beyond sd^1, now that the "
            "transport-twisted matter package already exists as a genuine symmetric "
            "Dirac-type operator with exact first-order data and exact quadratic "
            "seed/sd^1 coefficients. The whole internal matter/Higgs/gravity ratio "
            "package is now cyclotomically locked, and the matter/Higgs side now has its own "
            "exact q = 3 selection law, so the exact discrete Einstein-Hilbert-like "
            "channel is now identified as the barycentric 6-mode, so the next "
            "internal bridge is therefore the full refinement-tower second-order "
            "theorem and then the genuine cutoff/small-time continuum lift of "
            "that exact 6-mode law rather than a search for where the curvature "
            "channel lives. In parallel, "
            "move beyond the replicated generation-diagonal three-generation seed "
            "that structurally forces Cartan-only l6 selection, explain dynamically "
            "why the exact generation label matrix [[AB,I,A],[AB,I,A],[A,B,0]] is "
            "selected now that both the local-to-global gluing step and the "
            "transport-side ternary extension are exact, push that seed into the "
            "rank-lift or full six-mode regime, extend the exact l3/l4/l5/l6 "
            "tower-cycle theorem to the next gauge-return rung beyond l6, then "
            "prove the small-time / cutoff asymptotics that generate the "
            "Einstein-Hilbert term."
        ),
        "residual_risk": (
            "Tomotope itself remains natively cubic in its explicit Q_k tower. The 4D "
            "geometry must therefore come from an external factor or from a different "
            "genuinely 4D refinement family."
        ),
        "focused_test_stack_size": 700,
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_refinement_bridge_synthesis(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
