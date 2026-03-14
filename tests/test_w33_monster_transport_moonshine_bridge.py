from __future__ import annotations

from w33_monster_transport_moonshine_bridge import (
    build_monster_transport_moonshine_summary,
)


def test_transport_moonshine_dictionary_closes_leech_exactly() -> None:
    summary = build_monster_transport_moonshine_summary()
    bridge = summary["transport_moonshine_dictionary"]
    assert bridge["sl27_traceless_dimension"] == 728
    assert bridge["directed_transport_edges"] == 270
    assert bridge["leech_kissing_number"] == 196560
    assert bridge["leech_equals_sl27_traceless_times_transport_edges"] is True


def test_transport_moonshine_dictionary_closes_first_coefficient_exactly() -> None:
    summary = build_monster_transport_moonshine_summary()
    bridge = summary["transport_moonshine_dictionary"]
    assert bridge["sl27_completed_dimension"] == 729
    assert bridge["gauge_package_rank"] == 54
    assert bridge["moonshine_gap"] == 324
    assert bridge["first_moonshine_coefficient"] == 196884
    assert bridge["first_moonshine_equals_completed_sl27_times_transport_plus_gauge_rank"] is True
    assert bridge["moonshine_gap_equals_transport_plus_gauge_rank"] is True
    assert bridge["gauge_package_rank_equals_e6_plus_a2_plus_cartan"] is True
