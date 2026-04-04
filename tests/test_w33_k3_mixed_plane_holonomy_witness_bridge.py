from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_holonomy_witness_bridge import (  # noqa: E402
    build_k3_mixed_plane_holonomy_witness_summary,
)


def test_mixed_plane_holonomy_witness_has_expected_shape() -> None:
    summary = build_k3_mixed_plane_holonomy_witness_summary()
    witness = summary["mixed_plane_holonomy_witness"]
    assert witness["canonical_nontrivial_holonomy"] == [[1, 1], [0, 1]]
    assert witness["gauge_related_nontrivial_holonomy"] == [[1, 2], [0, 1]]
    assert sorted(witness["nontrivial_sign_trivial_holonomy_matrices"]) == [
        [[1, 1], [0, 1]],
        [[1, 2], [0, 1]],
    ]
    assert witness["conjugated_matrix"] == [[1, 2], [0, 1]]


def test_mixed_plane_holonomy_witness_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_holonomy_witness_summary()[
        "k3_mixed_plane_holonomy_witness_theorem"
    ]
    assert theorem[
        "a_nonzero_sign_trivial_cocycle_value_is_equivalent_to_a_nonidentity_unipotent_adapted_holonomy_matrix"
    ] is True
    assert theorem[
        "the_sign_trivial_sector_has_two_nontrivial_unipotent_matrices_over_f3"
    ] is True
    assert theorem[
        "the_two_nontrivial_sign_trivial_holonomies_are_gauge_equivalent"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_support_preserving_nontrivial_sign_trivial_holonomy_witness_on_the_same_fixed_host"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_the_first_nontrivial_sign_trivial_holonomy_witness_on_the_same_fixed_host"
    ] is True
