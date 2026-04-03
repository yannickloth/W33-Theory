"""
Phase CCCLXXXI — Continuum transport realization wall.

The promoted six-observable shell already fixes the finite packet and the
continuum-facing coefficient package. This phase packages what is still open:
actual external realization is localized to the curvature-sensitive transport
tail channel on the fixed carrier/avatar package.
"""

from __future__ import annotations

from fractions import Fraction

from exploration.w33_continuum_transport_realization_wall_bridge import (
    build_continuum_transport_realization_wall_summary,
)


def test_phase_ccclxxxi_continuum_package_is_locked() -> None:
    summary = build_continuum_transport_realization_wall_summary()
    locked = summary["locked_continuum_package"]

    assert locked["a0"] == 480
    assert locked["c_EH"] == 320
    assert locked["a2"] == 2240
    assert locked["a4"] == 17600
    assert locked["c6"] == 12480
    assert locked["higgs_ratio_square"] == "14/55"


def test_phase_ccclxxxi_head_tail_channel_split_is_exact() -> None:
    summary = build_continuum_transport_realization_wall_summary()
    split = summary["transport_channel_split"]

    assert split["matter_extension_dimension"] == 162
    assert split["protected_head_dimension"] == 81
    assert split["tail_channel_dimension"] == 81
    assert split["curvature_sensitive_rank"] == 3402
    assert split["protected_head_is_exactly_one_81_copy"] is True
    assert split["curvature_hits_only_tail_channel"] is True


def test_phase_ccclxxxi_external_harmonic_head_lifts_are_exact() -> None:
    summary = build_continuum_transport_realization_wall_summary()
    cp2, k3 = summary["transport_channel_split"]["protected_harmonic_lifts"]

    assert cp2["external_harmonic_form_total"] == 3
    assert cp2["protected_flat_matter_zero_modes"] == 243
    assert k3["external_harmonic_form_total"] == 24
    assert k3["protected_flat_matter_zero_modes"] == 1944


def test_phase_ccclxxxi_avatar_shell_remains_fixed() -> None:
    summary = build_continuum_transport_realization_wall_summary()
    avatar = summary["fixed_realization_avatar"]

    assert avatar["ordered_filtration_dimensions"] == [81, 162, 81]
    assert avatar["glue_direction"] == "tail_to_head"
    assert avatar["external_glue_rank"] == 0
    assert avatar["external_glue_state"] == "zero_by_splitness"


def test_phase_ccclxxxi_remaining_wall_is_realization_not_coefficients() -> None:
    theorem = build_continuum_transport_realization_wall_summary()[
        "continuum_transport_realization_wall_theorem"
    ]
    assert theorem[
        "promoted_continuum_coefficients_are_already_fixed_before_external_realization"
    ] is True
    assert theorem[
        "therefore_the_remaining_continuum_wall_is_tail_channel_realization_on_a_fixed_carrier_package"
    ] is True


def test_phase_ccclxxxi_ratio_package_is_unchanged() -> None:
    summary = build_continuum_transport_realization_wall_summary()
    locked = summary["locked_continuum_package"]

    assert Fraction(locked["c_EH"], locked["a0"]) == Fraction(2, 3)
    assert Fraction(locked["a2"], locked["a0"]) == Fraction(14, 3)
    assert Fraction(locked["a4"], locked["a0"]) == Fraction(110, 3)
    assert Fraction(locked["c6"], locked["a0"]) == 26
    assert Fraction(locked["c6"], locked["c_EH"]) == 39
