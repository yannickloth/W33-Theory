from __future__ import annotations

from math import isclose

from w33_monster_triangle_landauer_bridge import build_monster_triangle_landauer_summary


def test_triangle_stabilizer_is_native_w33_moonshine_gap() -> None:
    summary = build_monster_triangle_landauer_summary()
    bridge = summary["triangle_landauer_dictionary"]
    assert bridge["triangle_count"] == 160
    assert bridge["automorphism_order"] == 51840
    assert bridge["triangle_stabilizer"] == 324
    assert bridge["triangle_stabilizer_matches_general_formula"] is True
    assert bridge["triangle_stabilizer_equals_moonshine_gap"] is True


def test_triangle_stabilizer_matches_live_exceptional_and_matter_forms() -> None:
    summary = build_monster_triangle_landauer_summary()
    bridge = summary["triangle_landauer_dictionary"]
    assert bridge["degree"] == 12
    assert bridge["generation_block"] == 27
    assert bridge["gauge_package_rank"] == 54
    assert bridge["shared_six_channel_rank"] == 6
    assert bridge["spacetime_factor"] == 4
    assert bridge["logical_qutrits"] == 81
    assert bridge["triangle_stabilizer_equals_degree_times_generation"] is True
    assert bridge["triangle_stabilizer_equals_exceptional_times_shared_six"] is True
    assert bridge["triangle_stabilizer_equals_spacetime_times_logical_qutrits"] is True
    assert bridge["first_moonshine_equals_transport_traceless_plus_triangle_stabilizer"] is True


def test_triangle_stabilizer_has_exact_landauer_splits() -> None:
    summary = build_monster_triangle_landauer_summary()
    bridge = summary["triangle_landauer_dictionary"]
    assert bridge["landauer_gap_over_kT"]["exact"] == "ln(324)"
    assert bridge["landauer_exceptional_split"] == "ln(54) + ln(6)"
    assert bridge["landauer_matter_split"] == "ln(4) + ln(81)"
    assert bridge["landauer_exceptional_split_matches"] is True
    assert bridge["landauer_matter_split_matches"] is True
    assert isclose(bridge["landauer_gap_over_kT"]["float"], 5.780743515792329, rel_tol=0.0, abs_tol=1e-12)
