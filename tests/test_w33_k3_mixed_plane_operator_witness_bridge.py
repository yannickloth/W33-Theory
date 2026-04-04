from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_operator_witness_bridge import (  # noqa: E402
    build_k3_mixed_plane_operator_witness_summary,
)


def test_mixed_plane_operator_witness_has_expected_shape() -> None:
    summary = build_k3_mixed_plane_operator_witness_summary()
    witness = summary["mixed_plane_operator_witness"]
    assert witness["preserved_support_package"] is True
    assert witness["slot_direction"] == "tail_to_head"
    assert witness["slot_shape"] == [81, 81]
    assert witness["rank"] == 81
    assert witness["nullity"] == 81
    assert witness["square_zero"] is True
    assert witness["operator_model"] == "I_81 ⊗ [[0,1],[0,0]]"
    assert witness["polarized_nilpotent_normal_form"] == "J2^81"


def test_mixed_plane_operator_witness_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_operator_witness_summary()[
        "k3_mixed_plane_operator_witness_theorem"
    ]
    assert theorem[
        "the_mixed_plane_support_package_is_already_frozen_and_the_slot_only_deformation_class_is_unique"
    ] is True
    assert theorem[
        "the_exact_nonzero_slot_operator_has_unique_rank_81_square_zero_normal_form"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_unique_support_preserving_rank_81_square_zero_slot_operator_witness_on_the_canonical_mixed_plane_lift"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_existence_of_that_one_operator_witness_on_genuine_k3_side_data"
    ] is True
