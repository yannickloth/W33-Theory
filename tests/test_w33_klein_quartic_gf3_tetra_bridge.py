from __future__ import annotations

from w33_klein_quartic_gf3_tetra_bridge import build_klein_quartic_gf3_tetra_summary


def test_klein_quartic_gf3_packet_is_exact_tetrahedron() -> None:
    summary = build_klein_quartic_gf3_tetra_summary()
    packet = summary["gf3_klein_quartic_packet"]
    assert packet["field"] == 3
    assert packet["point_count"] == 4
    assert packet["projective_points"] == [
        [0, 0, 1],
        [0, 1, 0],
        [1, 0, 0],
        [1, 1, 1],
    ]
    assert packet["explicit_packet_matches_exactly"] is True
    assert packet["point_count_equals_q_plus_1"] is True
    assert packet["point_count_equals_mu"] is True
    assert packet["no_three_points_are_collinear"] is True
    assert packet["induced_projective_packet_is_k4"] is True
    assert packet["complete_graph_edge_count"] == 6


def test_klein_quartic_gf3_packet_matches_surface_and_hurwitz_data() -> None:
    summary = build_klein_quartic_gf3_tetra_summary()
    bridge = summary["surface_and_hurwitz_dictionary"]
    assert bridge["mu"] == 4
    assert bridge["tetrahedron_fixed_point_value"] == 4
    assert bridge["first_toroidal_dual_value"] == 7
    assert bridge["hurwitz_unit_order"] == 24
    assert bridge["point_count_matches_surface_fixed_point"] is True
    assert bridge["tetra_automorphism_order_matches_hurwitz_units"] is True
