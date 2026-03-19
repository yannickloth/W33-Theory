from __future__ import annotations

from w33_hurwitz_237_selector_bridge import build_hurwitz_237_selector_summary


def test_hurwitz_237_selector_bridge_closes_exactly() -> None:
    summary = build_hurwitz_237_selector_summary()
    assert summary["status"] == "ok"

    packet = summary["hurwitz_237_dictionary"]
    factors = summary["exact_factorizations"]

    assert packet["triangle_signature"] == [2, 3, 7]
    assert packet["duality_sheet_flip_order"] == 2
    assert packet["q"] == 3
    assert packet["phi6"] == 7
    assert packet["affine_shell_order"] == 42
    assert packet["single_surface_flags"] == 84
    assert packet["heawood_preserving_order"] == 168
    assert packet["heawood_full_order"] == 336

    assert factors["affine_shell_equals_2_3_7"] is True
    assert factors["affine_shell_is_agl_1_7"] is True
    assert factors["decimal_c6_splits_into_c3_and_z2"] is True
    assert factors["single_surface_flags_equals_2_times_affine_shell"] is True
    assert factors["heawood_preserving_equals_4_times_affine_shell"] is True
    assert factors["heawood_full_equals_8_times_affine_shell"] is True
