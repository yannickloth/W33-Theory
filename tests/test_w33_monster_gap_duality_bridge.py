from __future__ import annotations

from w33_monster_gap_duality_bridge import build_monster_gap_duality_summary


def test_moonshine_gap_matches_exceptional_and_spacetime_matter_forms() -> None:
    summary = build_monster_gap_duality_summary()
    bridge = summary["moonshine_gap_dictionary"]
    assert bridge["moonshine_gap"] == 324
    assert bridge["gauge_package_rank"] == 54
    assert bridge["shared_six_channel_rank"] == 6
    assert bridge["spacetime_factor"] == 4
    assert bridge["logical_qutrits"] == 81
    assert bridge["gap_equals_exceptional_gauge_rank_times_shared_six"] is True
    assert bridge["gap_equals_spacetime_factor_times_logical_qutrits"] is True
    assert bridge["exceptional_gap_matches_spacetime_matter_gap"] is True


def test_first_moonshine_has_dual_transport_gap_closures() -> None:
    summary = build_monster_gap_duality_summary()
    bridge = summary["moonshine_gap_dictionary"]
    assert bridge["sl27_traceless_dimension"] == 728
    assert bridge["sl27_completed_dimension"] == 729
    assert bridge["directed_transport_edges"] == 270
    assert bridge["first_moonshine_coefficient"] == 196884
    assert bridge["first_moonshine_equals_traceless_transport_plus_exceptional_gap"] is True
    assert bridge["first_moonshine_equals_completed_transport_plus_gauge_rank"] is True


def test_gap_bridge_uses_live_exceptional_rank_data() -> None:
    summary = build_monster_gap_duality_summary()
    bridge = summary["moonshine_gap_dictionary"]
    assert bridge["gauge_rank_equals_e6_plus_a2_plus_cartan"] is True
    assert bridge["shared_six_is_live_a2_rank"] is True
