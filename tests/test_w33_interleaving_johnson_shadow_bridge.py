from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_interleaving_johnson_shadow_bridge import (  # noqa: E402
    adjacency_matrix,
    build_interleaving_johnson_shadow_bridge_summary,
    interleavings,
)


def test_interleaving_state_count_and_degree() -> None:
    states = interleavings()
    adj = adjacency_matrix()
    assert len(states) == 10
    assert adj.shape == (10, 10)
    assert all(int(d) == 6 for d in adj.sum(axis=1))


def test_interleaving_johnson_shadow_summary() -> None:
    summary = build_interleaving_johnson_shadow_bridge_summary()
    theorem = summary["interleaving_johnson_shadow_theorem"]
    assert theorem["interleavings_are_exactly_the_3_subsets_of_a_5_set"]
    assert theorem["natural_one_slot_swap_adjacency_has_uniform_degree_6"]
    assert theorem["adjacency_spectrum_is_6_1_4_minus2_5"]
