from __future__ import annotations

from w33_s12_klein_projective_bridge import build_s12_klein_projective_summary


def test_harmonic_cube_square_projects_to_pg53() -> None:
    summary = build_s12_klein_projective_summary()
    bridge = summary["harmonic_cube_square_dictionary"]
    assert bridge["q"] == 3
    assert bridge["harmonic_cube_order"] == 27
    assert bridge["ternary_golay_code_size"] == 729
    assert bridge["sl27_shell_dimension"] == 728
    assert bridge["projectivized_shell_size"] == 364
    assert bridge["ambient_pg53_points"] == 364
    assert bridge["harmonic_cube_square_equals_golay_size"] is True
    assert bridge["nonzero_golay_equals_sl27_dimension"] is True
    assert bridge["projectivized_nonzero_shell_equals_pg53_points"] is True


def test_projective_shell_splits_as_klein_slice_plus_moonshine_gap() -> None:
    summary = build_s12_klein_projective_summary()
    bridge = summary["harmonic_cube_square_dictionary"]
    assert bridge["w33_klein_slice_points"] == 40
    assert bridge["moonshine_gap"] == 324
    assert bridge["projective_shell_minus_w33_klein_slice_equals_gap"] is True
    assert bridge["projective_shell_splits_as_w33_slice_plus_gap"] is True


def test_projective_weight_distribution_is_exact() -> None:
    summary = build_s12_klein_projective_summary()
    bridge = summary["weight_projectivization"]
    assert bridge["full_weight_distribution"] == {6: 264, 9: 440, 12: 24}
    assert bridge["projective_weight_distribution"] == {6: 132, 9: 220, 12: 12}
    assert bridge["projective_weight_distribution_sums_to_pg53"] is True
    assert bridge["weight_6_projects_to_132"] is True
    assert bridge["weight_9_projects_to_220"] is True
    assert bridge["weight_12_projects_to_12"] is True


def test_quartic_parallelism_guide_rail_counts_lock() -> None:
    summary = build_s12_klein_projective_summary()
    bridge = summary["quartic_parallelism_guide_rail"]
    assert bridge["clifford_parallelism_external_plane_points"] == 13
    assert bridge["plane_quartic_bitangent_count"] == 28
    assert bridge["ambient_pg53_equals_bitangents_times_external_plane_points"] is True
    assert bridge["external_plane_points_equals_phi3"] is True
