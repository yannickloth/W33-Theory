"""Exact double-Johnson shadow on support and factor interleavings.

Two different bridge layers now expose the same finite 10-state object:

- the support shell uses the 10 ways of choosing which 3 of 5 support slots
  carry the exact bridge core;
- the five-factor diagnostic shell uses the 10 ways of choosing which 3 of 5
  factor slots carry the hyperbolic sector.

Each layer is therefore a copy of the Johnson graph ``J(5,3)`` under the
natural one-slot-swap adjacency. The current exact bridge is asymmetric on
those two copies: the support theorem fixes one vertex, while the factor-copy
remains free on the exact diagnostic shell.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

QISKIT_TOOLS = ROOT / "tools" / "qiskit"
if str(QISKIT_TOOLS) not in sys.path:
    sys.path.insert(0, str(QISKIT_TOOLS))

from toe_bridge_diagnostic_order_search import (  # noqa: E402
    interleaving_patterns as factor_interleavings,
)
from toe_bridge_diagnostic_relaxation_search import (  # noqa: E402
    MODE_FORMAL_COMPLETION,
    RELAXATION_EXACT,
    build_marked_indices as build_diagnostic_marked_indices,
)
from toe_support_diagnostic_search import (  # noqa: E402
    build_marked_indices as build_support_marked_indices,
    marked_support_interleaving,
    support_interleavings,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_double_interleaving_johnson_bridge_summary.json"
)


def _adjacency_matrix(states: list[tuple[int, int, int]]) -> np.ndarray:
    n = len(states)
    adj = np.zeros((n, n), dtype=int)
    sets = [set(state) for state in states]
    for i, sa in enumerate(sets):
        for j, sb in enumerate(sets):
            if i != j and len(sa & sb) == 2:
                adj[i, j] = 1
    return adj


@lru_cache(maxsize=1)
def build_double_interleaving_johnson_bridge_summary() -> dict[str, Any]:
    support_states = support_interleavings()
    factor_states = factor_interleavings()
    support_adj = _adjacency_matrix(support_states)
    factor_adj = _adjacency_matrix(factor_states)
    support_spectrum = sorted(
        np.linalg.eigvalsh(support_adj).round(10).tolist(),
        reverse=True,
    )
    factor_spectrum = sorted(
        np.linalg.eigvalsh(factor_adj).round(10).tolist(),
        reverse=True,
    )

    support_marked_states, support_marked = build_support_marked_indices()
    _support_permutations, diagnostic_states, diagnostic_marked = (
        build_diagnostic_marked_indices(MODE_FORMAL_COMPLETION, RELAXATION_EXACT)
    )
    target_support_interleaving = support_states.index(marked_support_interleaving())
    support_interleavings_seen = {
        support_marked_states[idx][0] for idx in support_marked
    }
    factor_interleavings_seen = {
        diagnostic_states[idx][1] for idx in diagnostic_marked
    }

    return {
        "status": "ok",
        "support_interleaving_count": len(support_states),
        "factor_interleaving_count": len(factor_states),
        "joint_double_interleaving_state_count": len(support_states) * len(factor_states),
        "support_interleavings": [list(state) for state in support_states],
        "factor_interleavings": [list(state) for state in factor_states],
        "support_adjacency_degree_sequence": sorted(
            support_adj.sum(axis=1).astype(int).tolist(),
            reverse=True,
        ),
        "factor_adjacency_degree_sequence": sorted(
            factor_adj.sum(axis=1).astype(int).tolist(),
            reverse=True,
        ),
        "support_adjacency_spectrum": support_spectrum,
        "factor_adjacency_spectrum": factor_spectrum,
        "current_bridge_interleaving_asymmetry": {
            "marked_support_interleaving": list(marked_support_interleaving()),
            "support_exact_marked_count": len(support_marked),
            "support_exact_interleaving_count": len(support_interleavings_seen),
            "diagnostic_exact_marked_count": len(diagnostic_marked),
            "diagnostic_exact_factor_interleaving_count": len(factor_interleavings_seen),
        },
        "double_interleaving_johnson_bridge_theorem": {
            "support_interleavings_are_the_3_subsets_of_a_5_set": support_states
            == factor_states,
            "factor_interleavings_are_the_3_subsets_of_a_5_set": factor_states
            == support_states,
            "support_copy_is_johnson_j_5_3": all(
                int(d) == 6 for d in support_adj.sum(axis=1)
            )
            and support_spectrum == [6.0, 1.0, 1.0, 1.0, 1.0, -2.0, -2.0, -2.0, -2.0, -2.0],
            "factor_copy_is_johnson_j_5_3": all(
                int(d) == 6 for d in factor_adj.sum(axis=1)
            )
            and factor_spectrum == [6.0, 1.0, 1.0, 1.0, 1.0, -2.0, -2.0, -2.0, -2.0, -2.0],
            "the_identity_map_is_a_graph_isomorphism_between_the_two_copies": np.array_equal(
                support_adj, factor_adj
            ),
            "the_joint_interleaving_shadow_has_exact_size_100": len(support_states)
            * len(factor_states)
            == 100,
            "the_current_support_theorem_freezes_one_vertex_of_the_support_copy": (
                len(support_marked) == 2
                and len(support_interleavings_seen) == 1
                and next(iter(support_interleavings_seen)) == target_support_interleaving
            ),
            "the_current_exact_diagnostic_shell_leaves_the_factor_copy_free": (
                len(diagnostic_marked) == len(support_marked) * len(factor_states)
                and len(factor_interleavings_seen) == len(factor_states)
            ),
        },
        "bridge_verdict": (
            "The bridge now carries two canonical copies of the same 10-state "
            "Johnson object J(5,3): one on the support-core interleavings and "
            "one on the hyperbolic-factor interleavings. Their joint shadow has "
            "exact size 100. The current exact bridge is asymmetric on those "
            "two copies: the support theorem freezes one support vertex, while "
            "the factor copy remains free on the exact diagnostic shell."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_double_interleaving_johnson_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
