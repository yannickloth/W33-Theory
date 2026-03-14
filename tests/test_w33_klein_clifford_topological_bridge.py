from __future__ import annotations

from w33_klein_clifford_topological_bridge import (
    build_klein_clifford_topological_summary,
)


def test_clifford_quartic_packet_matches_live_topological_channel() -> None:
    summary = build_klein_clifford_topological_summary()
    bridge = summary["clifford_quartic_lift"]
    assert bridge["q"] == 3
    assert bridge["phi3"] == 13
    assert bridge["phi6"] == 7
    assert bridge["clifford_parallelism_external_plane_points"] == 13
    assert bridge["plane_quartic_bitangent_count"] == 28
    assert bridge["klein_quartic_triangle_count"] == 56
    assert bridge["e7_fundamental_dimension"] == 56
    assert bridge["w33_klein_slice_points"] == 40
    assert bridge["topological_1_mode_coefficient"] == 2240
    assert bridge["quartic_triangles_equal_e7_fund"] is True
    assert bridge["quartic_triangles_equal_two_times_bitangents"] is True
    assert bridge["quartic_triangles_equal_cartan_times_phi6"] is True
    assert bridge["bitangents_equal_q_cubic_plus_1"] is True
    assert bridge["topological_equals_w33_slice_times_quartic_triangles"] is True
    assert bridge["topological_equals_w33_slice_times_e7_fund"] is True


def test_ambient_and_sl27_shells_are_the_same_klein_lift() -> None:
    summary = build_klein_clifford_topological_summary()
    shell = summary["ambient_shell_lift"]
    assert shell["ambient_pg53_points"] == 364
    assert shell["sl27_shell_dimension"] == 728
    assert shell["g2_dimension"] == 14
    assert shell["ambient_equals_bitangents_times_phi3"] is True
    assert shell["ambient_equals_g2_times_a26_rank"] is True
    assert shell["sl27_equals_quartic_triangles_times_phi3"] is True
    assert shell["sl27_equals_two_times_ambient"] is True
    assert shell["sl27_equals_e7_fund_times_phi3"] is True
