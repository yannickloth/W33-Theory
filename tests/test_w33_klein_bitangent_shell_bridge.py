from __future__ import annotations

from w33_klein_bitangent_shell_bridge import build_klein_bitangent_shell_summary


def test_bitangent_shell_dresses_all_live_channels() -> None:
    summary = build_klein_bitangent_shell_summary()
    bridge = summary["bitangent_shell_dictionary"]
    assert bridge["bitangent_shell"] == 28
    assert bridge["phi3"] == 13
    assert bridge["a26_rank"] == 26
    assert bridge["quartic_triangle_shell"] == 56
    assert bridge["w33_slice"] == 40
    assert bridge["supertrace_magnitude"] == 80
    assert bridge["euler_magnitude"] == 80
    assert bridge["ambient_pg53_points"] == 364
    assert bridge["sl27_shell_dimension"] == 728
    assert bridge["topological_1_mode_coefficient"] == 2240
    assert bridge["ambient_equals_bitangents_times_phi3"] is True
    assert bridge["sl27_equals_bitangents_times_a26_rank"] is True
    assert bridge["topological_equals_bitangents_times_supertrace_magnitude"] is True
    assert bridge["topological_equals_bitangents_times_euler_magnitude"] is True
    assert bridge["quartic_triangles_equals_two_times_bitangents"] is True
    assert bridge["quartic_triangles_equals_cartan_times_phi6"] is True
    assert bridge["topological_equals_w33_slice_times_quartic_triangles"] is True
    assert bridge["a26_rank_equals_two_times_phi3"] is True


def test_bitangent_shell_ladder_and_ratios_are_exact() -> None:
    summary = build_klein_bitangent_shell_summary()
    bridge = summary["bitangent_shell_dictionary"]
    assert bridge["dressings"] == [1, 13, 26, 80]
    assert bridge["shell_ladder"] == [28, 364, 728, 2240]
    assert bridge["topological_over_ambient"] == "80/13"
    assert bridge["topological_over_sl27"] == "40/13"
