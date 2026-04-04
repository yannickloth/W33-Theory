from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_extension_witness_bridge import (  # noqa: E402
    build_k3_mixed_plane_extension_witness_summary,
)


def test_canonical_mixed_plane_qutrit_lift_is_the_fixed_external_host() -> None:
    summary = build_k3_mixed_plane_extension_witness_summary()
    host = summary["canonical_mixed_k3_plane_qutrit_lift"]
    assert host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
    assert host["qutrit_lift_split"] == [81, 81]
    assert host["total_qutrit_lift_dimension"] == 162


def test_mixed_plane_extension_witness_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_extension_witness_summary()[
        "k3_mixed_plane_extension_witness_theorem"
    ]
    assert theorem[
        "the_current_external_162_sector_is_already_the_split_qutrit_lift_of_the_canonical_mixed_k3_plane"
    ] is True
    assert theorem[
        "the_fixed_k3_tail_exactness_channel_is_already_carried_by_that_same_mixed_plane_qutrit_lift"
    ] is True
    assert theorem[
        "exact_k3_tail_realization_is_already_equivalent_to_any_nonzero_extension_class_witness_in_the_existing_tail_slot"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_a_nonzero_extension_witness_on_the_canonical_mixed_k3_plane_qutrit_lift"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_one_mixed_plane_deformation_witness_problem_not_a_search_for_a_new_162_host"
    ] is True
