from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_current_k3_tail_coordinate_witness_failure_bridge import (  # noqa: E402
    build_current_k3_tail_coordinate_witness_failure_summary,
)


def test_current_k3_tail_candidate_matches_none_of_the_promoted_witnesses() -> None:
    summary = build_current_k3_tail_coordinate_witness_failure_summary()
    comparison = summary["witness_comparison"]
    assert comparison["C"]["current_value"] == "0"
    assert comparison["L"]["current_value"] == "0"
    assert comparison["Q_seed"]["current_value"] == "0"
    assert comparison["Q_sd1"]["current_value"] == "0"
    assert all(
        value["matches_promoted_witness"] is False for value in comparison.values()
    )


def test_current_k3_tail_coordinate_witness_failure_theorem_holds() -> None:
    theorem = build_current_k3_tail_coordinate_witness_failure_summary()[
        "current_k3_tail_coordinate_witness_failure_theorem"
    ]
    assert theorem[
        "the_present_refined_k3_object_has_zero_in_all_promoted_tail_coordinates"
    ] is True
    assert theorem[
        "the_present_refined_k3_object_exhibits_no_exact_coordinate_witness"
    ] is True
    assert theorem[
        "by_cd_any_one_promoted_coordinate_witness_would_already_identify_the_unique_minimal_tail_datum"
    ] is True
    assert theorem[
        "therefore_the_present_refined_k3_object_fails_exact_tail_realization_exactly_by_lacking_any_promoted_coordinate_witness"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_the_first_nonzero_coordinate_witness_on_the_same_fixed_k3_package"
    ] is True
