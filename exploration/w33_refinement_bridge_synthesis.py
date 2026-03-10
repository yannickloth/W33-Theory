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
from w33_exceptional_triad_bridge import build_exceptional_triad_summary
from w33_curved_4d_curvature_budget import build_curved_4d_curvature_budget_summary
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


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_refinement_bridge_synthesis_summary.json"


def build_refinement_bridge_synthesis() -> dict[str, Any]:
    cover = build_cover_bridge_summary()
    ac_bridge = build_bridge_summary()
    torus = build_refinement_summary()
    flat = build_flat_product_summary()
    curvature_budget = build_curved_4d_curvature_budget_summary()
    triangulations = build_minimal_triangulation_summary()
    surface = build_surface_neighborly_summary()
    mobius = build_mobius_fano_summary()
    mobius_dual = build_mobius_szilassi_dual_summary()
    realization = build_realization_orbit_summary()
    witting = build_witting_srg_bridge_summary()
    fano_group = build_fano_group_summary()
    fano_square = build_fano_square_tomotope_summary()
    order = build_tomotope_order_summary()
    klitzing = build_klitzing_ladder_summary()
    exceptional = build_exceptional_triad_summary()

    cp2 = triangulations["seeds"][0]
    k3 = triangulations["seeds"][1]
    cp2_budget = curvature_budget["curved_seeds"][0]
    k3_budget = curvature_budget["curved_seeds"][1]
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
            "tetrads, the tomotope gives a genuine infinite cover family, the "
            "Fano/tetrahedron bridge gives a concrete D8 local model for tomotope "
            "edge stars, the M\"obius/Csaszar torus seed splits exactly as two Fano "
            "heptads on the same 7 vertices, that seed has an explicit abstract "
            "Szilassi dual with Heawood 1-skeleton and K7 face adjacency, the seven "
            "cataloged Euclidean realizations all share the same Z2 half-turn with "
            "dual orbit package (Csaszar: 4V/7F, Szilassi: 7V/4F), and minimal "
            "triangulations of CP2 and K3 supply curved 4D simplicial seed geometries "
            "with true refinement towers and a signature-forced nonzero Weyl-curvature "
            "budget. What remains open is the curved 4D spectral-action theorem for "
            "an almost-commutative product built from that exact internal data and a "
            "genuine curved 4D refinement family."
        ),
        "next_theorem_target": (
            "Construct a curved external 4D refinement family with controllable Dirac/"
            "Hodge asymptotics, pair it with the exact W33 finite triple, and prove the "
            "small-time / cutoff asymptotics that generate the Einstein-Hilbert term."
        ),
        "residual_risk": (
            "Tomotope itself remains natively cubic in its explicit Q_k tower. The 4D "
            "geometry must therefore come from an external factor or from a different "
            "genuinely 4D refinement family."
        ),
        "focused_test_stack_size": 121,
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_refinement_bridge_synthesis(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
