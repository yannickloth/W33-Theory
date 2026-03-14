from __future__ import annotations

from w33_monster_moonshine_lift_bridge import build_monster_moonshine_lift_summary


def test_moonshine_lift_dictionary_closes_leech_exactly() -> None:
    summary = build_monster_moonshine_lift_summary()
    bridge = summary["moonshine_lift_dictionary"]
    assert bridge["q"] == 3
    assert bridge["phi3"] == 13
    assert bridge["phi6"] == 7
    assert bridge["cyclotomic_lift_factor"] == 91
    assert bridge["local_second_shell"] == 2160
    assert bridge["leech_kissing_number"] == 196560
    assert bridge["local_second_shell_matches_theta_e8_second_shell"] is True
    assert bridge["leech_equals_local_second_shell_times_phi3_phi6"] is True


def test_moonshine_lift_dictionary_closes_first_coefficient_exactly() -> None:
    summary = build_monster_moonshine_lift_summary()
    bridge = summary["moonshine_lift_dictionary"]
    assert bridge["logical_qutrits"] == 81
    assert bridge["spacetime_factor"] == 4
    assert bridge["moonshine_gap"] == 324
    assert bridge["first_moonshine_coefficient"] == 196884
    assert bridge["smallest_monster_irrep"] == 196883
    assert bridge["selector_line_dimension"] == 1
    assert bridge["moonshine_gap_equals_q_plus_1_times_logical_qutrits"] is True
    assert bridge["moonshine_gap_equals_q_plus_1_times_q_to_four"] is True
    assert bridge["first_moonshine_equals_leech_plus_gap"] is True
    assert bridge["first_moonshine_equals_selector_plus_smallest_monster_irrep"] is True
    assert bridge["first_moonshine_equals_cyclotomic_lifted_shell_plus_spacetime_matter"] is True
