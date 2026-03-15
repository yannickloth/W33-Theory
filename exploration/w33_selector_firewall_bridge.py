"""Selection firewall beyond the bare SRG(40,12,2,4) equation.

The master identity

    A^2 + 2A - 8I = 4J

is exactly the strongly regular graph equation for parameters (40,12,2,4).
That identity is real, but it does not by itself isolate the canonical W33
model among all SRGs with those parameters.

This bridge records the exact extra selector package that the live repo already
uses implicitly:

  - the canonical graph is realized as the symplectic orthogonality graph
    W(3,3) on PG(3,3);
  - every neighborhood is exactly 4K3 (four disjoint triangles);
  - the adjacency matrix has rank 39 over GF(3);
  - the symplectic automorphism group has order 51840 = |Sp(4,3)|.

Together with the external classification count 28 for SRG(40,12,2,4), this
gives a clean firewall against overclaiming uniqueness from the quadratic
equation alone.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from w33_three_channel_operator_bridge import build_w33_adjacency


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_selector_firewall_bridge_summary.json"

V = 40
K = 12
LAMBDA = 2
MU = 4
SRG_401224_CLASSIFICATION_COUNT = 28


def _gf3_rank(matrix: np.ndarray) -> int:
    work = matrix.astype(int).copy() % 3
    rows, cols = work.shape
    rank = 0
    pivot_row = 0
    for col in range(cols):
        pivot = None
        for row in range(pivot_row, rows):
            if work[row, col] % 3 != 0:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != pivot_row:
            work[[pivot_row, pivot]] = work[[pivot, pivot_row]]
        if work[pivot_row, col] == 2:
            work[pivot_row] = (2 * work[pivot_row]) % 3
        for row in range(rows):
            if row != pivot_row and work[row, col] % 3 != 0:
                work[row] = (work[row] - work[row, col] * work[pivot_row]) % 3
        rank += 1
        pivot_row += 1
        if pivot_row == rows:
            break
    return rank


def _neighborhood_component_sizes(adjacency: np.ndarray, vertex: int) -> list[int]:
    neighbors = np.flatnonzero(adjacency[vertex]).tolist()
    subgraph = adjacency[np.ix_(neighbors, neighbors)]
    seen: set[int] = set()
    sizes: list[int] = []
    for start in range(len(neighbors)):
        if start in seen:
            continue
        stack = [start]
        component: list[int] = []
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            component.append(node)
            stack.extend(np.flatnonzero(subgraph[node]).tolist())
        sizes.append(len(component))
    return sorted(sizes)


def build_selector_firewall_summary() -> dict[str, Any]:
    adjacency = build_w33_adjacency()
    identity_holds = np.array_equal(
        adjacency @ adjacency + 2 * adjacency - 8 * np.eye(V, dtype=int),
        4 * np.ones((V, V), dtype=int),
    )
    rank_gf3 = _gf3_rank(adjacency)
    neighborhood_sizes = [_neighborhood_component_sizes(adjacency, vertex) for vertex in range(V)]

    return {
        "status": "ok",
        "master_equation": {
            "identity": "A^2 + 2A - 8I = 4J",
            "srg_parameters": [V, K, LAMBDA, MU],
            "identity_holds_for_canonical_w33": identity_holds,
            "classification_count_for_srg_40_12_2_4": SRG_401224_CLASSIFICATION_COUNT,
            "master_equation_alone_does_not_force_unique_graph": True,
        },
        "selector_package": {
            "canonical_realization": "symplectic W(3,3) on PG(3,3)",
            "gf3_rank_of_adjacency": rank_gf3,
            "gf3_rank_selector_matches_v_minus_1": rank_gf3 == V - 1,
            "all_neighborhoods_decompose_as_4K3": all(sizes == [3, 3, 3, 3] for sizes in neighborhood_sizes),
            "neighborhood_component_sizes": neighborhood_sizes[0],
            "symplectic_group_order": 3**4 * (3**2 - 1) * (3**4 - 1),
            "symplectic_group_order_exact": 51840,
        },
        "bridge_verdict": (
            "The quadratic master identity is exact, but it only defines the "
            "SRG(40,12,2,4) family. The canonical W33 model is selected by extra "
            "exact data already present in the live stack: the symplectic "
            "realization on PG(3,3), the GF(3) adjacency rank 39, the local "
            "neighborhood type 4K3, and the symplectic automorphism order 51840. "
            "So uniqueness claims must pass through this selector firewall rather "
            "than through the bare quadratic equation alone."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_selector_firewall_summary(), indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    write_summary()
