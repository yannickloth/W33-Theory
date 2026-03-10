from __future__ import annotations

import json
from pathlib import Path

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
    assert data["focused_test_stack_size"] == 121
