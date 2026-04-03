from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_tail_increment_realization_equivalence_bridge import (  # noqa: E402
    build_k3_tail_increment_realization_equivalence_summary,
)


def test_increment_realization_equivalence_theorem_holds() -> None:
    theorem = build_k3_tail_increment_realization_equivalence_summary()[
        "k3_tail_increment_realization_equivalence_theorem"
    ]
    assert theorem[
        "exact_k3_tail_realization_on_the_fixed_package_is_already_equivalent_to_realizing_the_unique_minimal_datum"
    ] is True
    assert theorem[
        "any_one_exact_affine_increment_witness_already_identifies_the_full_affine_target"
    ] is True
    assert theorem[
        "the_full_affine_target_is_just_the_current_zero_point_shifted_by_the_unique_minimal_datum_on_the_same_fixed_package"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_on_the_fixed_package_is_equivalent_to_realizing_any_one_exact_affine_increment_witness"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_exactly_one_affine_increment_witness_existence_problem"
    ] is True
