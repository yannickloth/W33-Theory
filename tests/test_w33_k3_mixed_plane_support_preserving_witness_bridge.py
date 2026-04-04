from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_support_preserving_witness_bridge import (  # noqa: E402
    build_k3_mixed_plane_support_preserving_witness_summary,
)


def test_canonical_mixed_plane_support_is_fixed() -> None:
    summary = build_k3_mixed_plane_support_preserving_witness_summary()
    support = summary["canonical_mixed_plane_support"]
    assert support["ordered_line_types"] == ["positive", "negative"]
    assert support["mixed_signature"] == [1, 1]
    assert support["qutrit_lift_split"] == [81, 81]
    assert support["total_qutrit_lift_dimension"] == 162
    assert support["first_refinement_scale_factor"] == 120


def test_support_preserving_witness_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_support_preserving_witness_summary()[
        "k3_mixed_plane_support_preserving_witness_theorem"
    ]
    assert theorem[
        "the_canonical_mixed_plane_support_data_are_already_fixed_on_the_external_side"
    ] is True
    assert theorem[
        "the_canonical_mixed_plane_support_is_first_refinement_rigid"
    ] is True
    assert theorem[
        "exact_k3_tail_realization_is_already_equivalent_to_a_nonzero_extension_witness_on_that_same_mixed_plane_lift"
    ] is True
    assert theorem[
        "therefore_any_exact_k3_tail_witness_must_preserve_the_canonical_mixed_plane_support_package_and_only_change_the_extension_class"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_one_support_preserving_mixed_plane_deformation_witness_problem"
    ] is True
