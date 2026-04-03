from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_transport_realization_wall_bridge import (  # noqa: E402
    build_continuum_transport_realization_wall_summary,
)


def test_locked_continuum_package_is_exact() -> None:
    summary = build_continuum_transport_realization_wall_summary()
    locked = summary["locked_continuum_package"]

    assert locked["a0"] == 480
    assert locked["c_EH"] == 320
    assert locked["a2"] == 2240
    assert locked["a4"] == 17600
    assert locked["c6"] == 12480
    assert locked["higgs_ratio_square"] == "14/55"
    assert locked["q"] == 3
    assert locked["phi3"] == 13
    assert locked["phi6"] == 7
    assert locked["v_of_q"] == 40


def test_transport_channel_split_is_exact() -> None:
    summary = build_continuum_transport_realization_wall_summary()
    split = summary["transport_channel_split"]

    assert split["matter_extension_dimension"] == 162
    assert split["protected_head_dimension"] == 81
    assert split["tail_channel_dimension"] == 81
    assert split["curvature_sensitive_rank"] == 3402
    assert split["head_plus_tail_equals_extension_dimension"] is True
    assert split["protected_head_is_exactly_one_81_copy"] is True
    assert split["curvature_hits_only_tail_channel"] is True

    cp2, k3 = split["protected_harmonic_lifts"]
    assert cp2["external_name"] == "CP2"
    assert cp2["protected_flat_matter_zero_modes"] == 243
    assert k3["external_name"] == "K3"
    assert k3["protected_flat_matter_zero_modes"] == 1944


def test_fixed_realization_avatar_is_preserved() -> None:
    summary = build_continuum_transport_realization_wall_summary()
    avatar = summary["fixed_realization_avatar"]

    assert avatar["head_line_dimension"] == 81
    assert avatar["tail_line_dimension"] == 81
    assert avatar["ordered_filtration_dimensions"] == [81, 162, 81]
    assert avatar["glue_direction"] == "tail_to_head"
    assert avatar["external_glue_rank"] == 0
    assert avatar["external_glue_state"] == "zero_by_splitness"


def test_realization_wall_theorem_is_exact() -> None:
    summary = build_continuum_transport_realization_wall_summary()
    theorem = summary["continuum_transport_realization_wall_theorem"]

    assert theorem[
        "promoted_continuum_coefficients_are_already_fixed_before_external_realization"
    ] is True
    assert theorem[
        "the_matter_coupled_transport_object_has_one_protected_flat_81_head_copy"
    ] is True
    assert theorem[
        "the_remaining_81_copy_is_the_curvature_sensitive_tail_channel"
    ] is True
    assert theorem[
        "any_exact_completion_must_preserve_the_fixed_avatar_shell_and_head_tail_lines"
    ] is True
    assert theorem[
        "any_exact_k3_side_realization_must_be_a_carrier_preserving_transport_twisted_lift"
    ] is True
    assert theorem[
        "therefore_the_remaining_continuum_wall_is_tail_channel_realization_on_a_fixed_carrier_package"
    ] is True

