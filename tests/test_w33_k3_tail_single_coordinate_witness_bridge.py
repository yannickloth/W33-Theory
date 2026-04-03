from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_single_coordinate_witness_bridge import (  # noqa: E402
    build_k3_tail_single_coordinate_witness_summary,
)


def test_each_coordinate_witness_recovers_same_scale() -> None:
    summary = build_k3_tail_single_coordinate_witness_summary()
    witnesses = summary["exact_coordinate_witnesses"]
    assert witnesses["C"]["recovered_scale"] == "217/12"
    assert witnesses["L"]["recovered_scale"] == "217/12"
    assert witnesses["Q_seed"]["recovered_scale"] == "217/12"
    assert witnesses["Q_sd1"]["recovered_scale"] == "217/12"


def test_k3_tail_single_coordinate_witness_theorem_holds() -> None:
    theorem = build_k3_tail_single_coordinate_witness_summary()[
        "k3_tail_single_coordinate_witness_theorem"
    ]
    assert theorem[
        "the_unique_minimal_datum_already_lies_on_the_fixed_exact_tail_line"
    ] is True
    assert theorem[
        "each_promoted_coordinate_witness_recovers_the_same_exact_scale_217_over_12"
    ] is True
    assert theorem[
        "therefore_on_the_fixed_tail_line_any_one_promoted_coordinate_witness_identifies_the_unique_minimal_datum"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_tail_line_membership_plus_any_one_coordinate_witness"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_existence_of_any_one_exact_coordinate_witness_from_genuine_k3_side_data_on_the_fixed_line_class"
    ] is True
