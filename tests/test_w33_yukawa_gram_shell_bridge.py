from __future__ import annotations

from w33_yukawa_gram_shell_bridge import (
    build_yukawa_gram_shell_summary,
)


def test_all_active_template_gram_packets_live_on_common_240_shell() -> None:
    summary = build_yukawa_gram_shell_summary()
    theorem = summary["gram_shell_theorem"]

    assert summary["root_denominator"] == 240
    assert summary["gram_denominator"] == 57600
    assert theorem["all_template_grams_scale_exactly_to_integer_shell"] is True

    h2 = summary["slot_profiles"]["H_2"]
    hbar2 = summary["slot_profiles"]["Hbar_2"]

    assert h2["+-"]["g00_numerator_matrix"] == [[1475, 0], [0, 1321]]
    assert h2["+-"]["g11_numerator_matrix"] == [[600, 0], [0, 576]]
    assert h2["+-"]["g01_numerator_matrix"] == [[-900, 0], [0, -864]]
    assert h2["+-"]["base_gram_numerator_matrix"] == [[275, 0], [0, 169]]

    assert h2["-+"]["base_gram_numerator_matrix"] == [[367, -55], [-55, 175]]
    assert hbar2["+-"]["base_gram_numerator_matrix"] == [[323, 275, 0], [275, 659, 0], [0, 0, 169]]
    assert hbar2["-+"]["base_gram_numerator_matrix"] == [[323]]


def test_plus_minus_slots_share_exact_phi3_mode_on_root_denominator() -> None:
    summary = build_yukawa_gram_shell_summary()
    theorem = summary["gram_shell_theorem"]

    assert theorem["plus_minus_slots_share_exact_phi3_mode_13_over_240"] is True
    assert theorem["residual_frontier_is_two_integer_2x2_blocks_plus_exact_scalar_channels"] is True
    assert theorem["h2_minus_plus_residual_block_numerator"] == [[367, -55], [-55, 175]]
    assert theorem["hbar2_plus_minus_residual_block_numerator"] == [[323, 275], [275, 659]]
    assert theorem["exact_scalar_channel_numerators"] == {
        "shared_phi3_mode": 169,
        "h2_plus_minus_companion": 275,
        "hbar2_minus_plus_scalar": 323,
    }
    assert summary["slot_profiles"]["H_2"]["+-"]["contains_exact_phi3_mode_13_over_240"] is True
    assert summary["slot_profiles"]["Hbar_2"]["+-"]["contains_exact_phi3_mode_13_over_240"] is True
    assert summary["slot_profiles"]["H_2"]["-+"]["contains_exact_phi3_mode_13_over_240"] is False
    assert summary["slot_profiles"]["Hbar_2"]["-+"]["contains_exact_phi3_mode_13_over_240"] is False
