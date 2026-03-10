from __future__ import annotations

import json
from pathlib import Path

from w33_surface_neighborly_bridge import (
    barycentric_subdivision_f_vector,
    build_surface_neighborly_summary,
    complete_face_adjacency_surface_counts,
    complete_graph_triangulation_counts,
    convex_cell_realization_obstructed_for_complete_graph,
    csaszar_seed,
    dual_pair_total_flags,
    fano_flag_stabilizer_order,
    fano_plane_counts,
    map_flag_count_from_edges,
    minimum_faces_for_complete_face_adjacency_genus,
    minimum_vertices_for_complete_graph_seed_genus,
    orientable_surface_complete_face_adjacency_genus,
    orientable_surface_complete_graph_genus,
    szilassi_seed,
    tetrahedron_counts,
    tomotope_flag_count_from_local_incidence,
    write_summary,
)


def test_vertex_and_face_genus_formulas_match_by_duality() -> None:
    assert orientable_surface_complete_graph_genus(4) == 0
    assert orientable_surface_complete_graph_genus(7) == 1
    assert orientable_surface_complete_graph_genus(12) == 6
    assert orientable_surface_complete_graph_genus(7) == orientable_surface_complete_face_adjacency_genus(7)


def test_csaszar_seed_matches_classical_toroidal_counts() -> None:
    seed = csaszar_seed()
    assert seed.genus == 1
    assert (seed.vertices, seed.edges, seed.faces) == (7, 21, 14)
    assert seed.complete_vertex_adjacency is True
    assert seed.one_skeleton_graph == "K7"


def test_szilassi_seed_matches_dual_toroidal_counts() -> None:
    seed = szilassi_seed()
    assert seed.genus == 1
    assert (seed.vertices, seed.edges, seed.faces) == (14, 21, 7)
    assert seed.complete_face_adjacency is True
    assert seed.one_skeleton_graph == "Heawood graph"
    assert seed.face_adjacency_graph == "K7"


def test_complete_seed_counts_match_formulae() -> None:
    assert complete_graph_triangulation_counts(7) == (7, 21, 14)
    assert complete_face_adjacency_surface_counts(7) == (14, 21, 7)


def test_fano_counts_lift_to_toroidal_flag_counts() -> None:
    fano = fano_plane_counts()
    assert fano["flags"] == 21
    assert csaszar_seed().edges == fano["flags"]
    assert szilassi_seed().edges == fano["flags"]
    assert map_flag_count_from_edges(21) == 84
    assert dual_pair_total_flags() == 168
    assert fano_flag_stabilizer_order() == 8


def test_tetrahedral_midpoint_sum_matches_tomotope_flags() -> None:
    tetrahedron = tetrahedron_counts()
    assert tetrahedron["flags"] == 24
    assert tetrahedron["automorphism_group_order"] == 24
    midpoint_total = map_flag_count_from_edges(21) + tetrahedron["flags"] + map_flag_count_from_edges(21)
    assert midpoint_total == 192
    assert tomotope_flag_count_from_local_incidence() == 192


def test_torus_seed_saturates_surface_bounds() -> None:
    assert minimum_vertices_for_complete_graph_seed_genus(1) == 7
    assert minimum_faces_for_complete_face_adjacency_genus(1) == 7


def test_barycentric_subdivision_turns_csaszar_into_refinement_family() -> None:
    csaszar = csaszar_seed()
    sd1 = barycentric_subdivision_f_vector((csaszar.vertices, csaszar.edges, csaszar.faces), steps=1)
    sd2 = barycentric_subdivision_f_vector((csaszar.vertices, csaszar.edges, csaszar.faces), steps=2)
    assert len(sd1) == 3
    assert sd1[-1] == 6 * csaszar.faces
    assert sd2[-1] == 6 * sd1[-1]
    assert sd2[0] > sd1[0] > csaszar.vertices


def test_k5_convex_cell_obstruction_explains_szilassi_nonconvexity() -> None:
    assert convex_cell_realization_obstructed_for_complete_graph(4) is False
    assert convex_cell_realization_obstructed_for_complete_graph(5) is True
    assert convex_cell_realization_obstructed_for_complete_graph(7) is True
    assert szilassi_seed().convex_cell_realization_obstructed is True


def test_summary_records_surface_to_4d_bridge() -> None:
    summary = build_surface_neighborly_summary()
    assert summary["status"] == "ok"
    assert summary["torus_minimality"]["minimum_complete_graph_seed_vertices_for_genus_1"] == 7
    assert summary["adjacency_graph_realizability"]["szilassi_face_adjacency_graph"] == "K7"
    assert summary["fano_bridge"]["dual_pair_total_flags"] == 168
    assert summary["fano_bridge"]["dual_pair_flags_per_fano_flag"] == 8
    assert summary["catalog_realization_counts"]["total_versions"] == 7
    assert summary["tetrahedral_midpoint_bridge"]["midpoint_sum_flags"] == 192
    assert summary["tetrahedral_midpoint_bridge"]["matches_tomotope_flags"] is True
    assert summary["barycentric_subdivision"]["top_simplex_multiplier_per_step"] == 6
    assert "2D prototype of the 4D" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_surface_neighborly_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert len(data["seeds"]) == 2
