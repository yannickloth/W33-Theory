from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_affine_increment_witness_bridge import (  # noqa: E402
    build_k3_tail_affine_increment_witness_summary,
)


def test_each_affine_increment_recovers_same_scale() -> None:
    summary = build_k3_tail_affine_increment_witness_summary()
    witnesses = summary["affine_increment_witnesses"]
    assert witnesses["dC"]["recovered_scale"] == "217/12"
    assert witnesses["dL"]["recovered_scale"] == "217/12"
    assert witnesses["dQ_seed"]["recovered_scale"] == "217/12"
    assert witnesses["dQ_sd1"]["recovered_scale"] == "217/12"


def test_affine_increment_witness_theorem_holds() -> None:
    theorem = build_k3_tail_affine_increment_witness_summary()[
        "k3_tail_affine_increment_witness_theorem"
    ]
    assert theorem[
        "the_current_refined_k3_point_is_zero_so_affine_increments_equal_the_exact_witness_coordinates"
    ] is True
    assert theorem[
        "each_promoted_affine_increment_recovers_the_same_exact_scale_217_over_12"
    ] is True
    assert theorem[
        "therefore_any_one_promoted_affine_increment_identifies_the_full_affine_witness_target"
    ] is True
    assert theorem[
        "therefore_the_live_external_wall_is_existence_of_any_one_exact_affine_increment_witness_on_the_same_fixed_package"
    ] is True
