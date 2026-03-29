from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_double_interleaving_johnson_bridge import (  # noqa: E402
    build_double_interleaving_johnson_bridge_summary,
)


def test_double_interleaving_johnson_summary() -> None:
    summary = build_double_interleaving_johnson_bridge_summary()
    theorem = summary["double_interleaving_johnson_bridge_theorem"]
    assert theorem["support_interleavings_are_the_3_subsets_of_a_5_set"]
    assert theorem["factor_interleavings_are_the_3_subsets_of_a_5_set"]
    assert theorem["support_copy_is_johnson_j_5_3"]
    assert theorem["factor_copy_is_johnson_j_5_3"]
    assert theorem["the_identity_map_is_a_graph_isomorphism_between_the_two_copies"]
    assert theorem["the_joint_interleaving_shadow_has_exact_size_100"]
    assert theorem["the_current_support_theorem_freezes_one_vertex_of_the_support_copy"]
    assert theorem["the_current_exact_diagnostic_shell_leaves_the_factor_copy_free"]
