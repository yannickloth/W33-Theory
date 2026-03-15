from __future__ import annotations

from w33_yukawa_base_spectrum_bridge import build_yukawa_base_spectrum_summary


def test_base_squared_spectra_close_as_exact_scalar_channels_and_two_radical_pairs() -> None:
    summary = build_yukawa_base_spectrum_summary()
    theorem = summary["base_spectrum_theorem"]
    spectra = summary["base_squared_spectra"]

    assert summary["gram_denominator"] == 57600
    assert theorem["all_base_squared_spectra_are_exact_algebraic_numbers_on_240_shell"] is True
    assert theorem["residual_base_frontier_is_two_radical_pairs_plus_exact_scalar_channels"] is True

    assert spectra["h2_plus_minus"] == ["169/57600", "275/57600"]
    assert spectra["h2_minus_plus"] == [
        "271/57600 - sqrt(12241)/57600",
        "sqrt(12241)/57600 + 271/57600",
    ]
    assert spectra["hbar2_plus_minus"] == [
        "169/57600",
        "491/57600 - sqrt(103849)/57600",
        "sqrt(103849)/57600 + 491/57600",
    ]
    assert spectra["hbar2_minus_plus"] == ["323/57600"]


def test_residual_blocks_have_exact_trace_and_determinant_dictionary() -> None:
    summary = build_yukawa_base_spectrum_summary()
    theorem = summary["base_spectrum_theorem"]
    packets = summary["radical_packet_dictionary"]

    assert theorem["h2_minus_plus_block_trace"] == 542
    assert theorem["h2_minus_plus_block_determinant"] == 61200
    assert theorem["hbar2_plus_minus_block_trace"] == 982
    assert theorem["hbar2_plus_minus_block_determinant"] == 137232
    assert packets["shared_phi3_scalar_channel"] == "169/57600"
    assert packets["h2_plus_minus_companion_scalar_channel"] == "275/57600"
    assert packets["hbar2_minus_plus_scalar_channel"] == "323/57600"
