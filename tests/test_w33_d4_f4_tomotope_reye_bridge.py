from __future__ import annotations

from w33_d4_f4_tomotope_reye_bridge import build_d4_f4_tomotope_reye_summary


def test_d4_lock_matches_tomotope_flags_and_double_automorphisms() -> None:
    summary = build_d4_f4_tomotope_reye_summary()
    lock = summary["d4_lock"]
    assert lock["weyl_d4_order"] == 192
    assert lock["tomotope_flag_count"] == 192
    assert lock["tomotope_automorphism_order"] == 96
    assert lock["weyl_d4_equals_tomotope_flags"] is True
    assert lock["weyl_d4_equals_2_times_tomotope_automorphism"] is True


def test_q8_and_reye_shadow_counts_match_d4_and_24cell() -> None:
    summary = build_d4_f4_tomotope_reye_summary()
    q8 = summary["q8_to_24cell_bridge"]
    shadow = summary["reye_shadow"]
    assert q8["aut_q8_order"] == 24
    assert q8["d4_root_count"] == 24
    assert q8["twenty_four_cell_vertex_count"] == 24
    assert q8["aut_q8_equals_d4_root_count"] is True
    assert q8["d4_root_count_equals_24cell_vertices"] is True
    assert shadow["tomotope_edges"] == 12
    assert shadow["reye_points"] == 12
    assert shadow["d4_root_pairs"] == 12
    assert shadow["twenty_four_cell_axes"] == 12
    assert shadow["all_twelve_counts_agree"] is True
    assert shadow["tomotope_triangles"] == 16
    assert shadow["reye_lines"] == 16
    assert shadow["twenty_four_cell_hexagon_shadow_count"] == 16
    assert shadow["all_sixteen_counts_agree"] is True


def test_f4_is_triality_lift_of_the_same_tomotope_package() -> None:
    summary = build_d4_f4_tomotope_reye_summary()
    lift = summary["f4_triality_lift"]
    assert lift["outer_d4_order"] == 6
    assert lift["weyl_f4_order"] == 1152
    assert lift["twenty_four_cell_rotational_symmetry_order"] == 576
    assert lift["weyl_f4_equals_triality_times_weyl_d4"] is True
    assert lift["weyl_f4_equals_triality_times_tomotope_flags"] is True
    assert lift["weyl_f4_equals_twelve_times_tomotope_automorphism"] is True
    assert lift["rotational_24_equals_triality_times_tomotope_automorphism"] is True
    assert lift["weyl_f4_equals_2_times_rotational_24"] is True
