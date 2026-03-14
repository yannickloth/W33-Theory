from __future__ import annotations

from w33_monster_supertrace_bridge import build_monster_supertrace_summary


def test_spectral_dictionary_locks_e8_and_supertrace() -> None:
    summary = build_monster_supertrace_summary()
    bridge = summary["spectral_dictionary"]
    assert bridge["euler_characteristic"] == -80
    assert bridge["supertrace"] == -80
    assert bridge["supertrace_magnitude"] == 80
    assert bridge["selector_line_dimension"] == 1
    assert bridge["logical_qutrits"] == 81
    assert bridge["generation_states"] == 27
    assert bridge["e8_second_shell"] == 2160
    assert bridge["semisimple_transport_shell"] == 2160
    assert bridge["monster_complement_states"] == 2187
    assert bridge["euler_matches_supertrace_exactly"] is True
    assert bridge["semisimple_equals_e8_second_shell"] is True
    assert bridge["semisimple_equals_generation_times_supertrace_magnitude"] is True
    assert bridge["logical_equals_supertrace_magnitude_plus_selector"] is True
    assert bridge["monster_complement_equals_generation_times_logical"] is True
    assert bridge["monster_complement_equals_e8_second_shell_plus_generation"] is True
