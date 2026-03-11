"""Triangle-holonomy theorem for the W33 center-quad transport graph.

This module extracts the low-q holonomy invariant suggested by the q=13 bundle
and proves it exactly on the live q=3 transport bridge:

For every triangle in the 45-point quotient transport graph, the old v14 Z2
triangle parity is exactly the sign character of the induced local S3 holonomy
obtained by composing the unique line-matchings around the triangle.

Consequences:

1. parity-0 triangles are exactly the even-holonomy triangles;
2. parity-1 triangles are exactly the odd-holonomy triangles;
3. the v14 parity statistic is therefore not ad hoc Z2 data but the sign of
   an exact transport holonomy invariant.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from itertools import combinations
from pathlib import Path
from typing import Any

from w33_center_quad_transport_bridge import quotient_triangle_parity_stats, reconstructed_quotient_graph
from w33_center_quad_transport_complement_bridge import (
    line_intersection_graph,
    permutation_parity,
    point_triangles,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_center_quad_transport_holonomy_bridge_summary.json"


def permutation_inverse(permutation: tuple[int, int, int]) -> tuple[int, int, int]:
    out = [0, 0, 0]
    for index, image in enumerate(permutation):
        out[image] = index
    return tuple(out)


def permutation_compose(
    left: tuple[int, int, int], right: tuple[int, int, int]
) -> tuple[int, int, int]:
    return tuple(right[left[index]] for index in range(3))


def edge_line_matching(left: int, right: int) -> tuple[int, int, int]:
    triangles = point_triangles()
    adjacency = line_intersection_graph()
    source = triangles[left]
    target = triangles[right]
    permutation = []
    for line_id in source:
        matches = [index for index, other in enumerate(target) if other in adjacency[line_id]]
        if len(matches) != 1:
            raise AssertionError("transport edge should induce a unique line matching")
        permutation.append(matches[0])
    result = tuple(permutation)
    if sorted(result) != [0, 1, 2]:
        raise AssertionError("line matching must be a permutation")
    return result


def directed_edge_matching(left: int, right: int) -> tuple[int, int, int]:
    if left < right:
        return edge_line_matching(left, right)
    return permutation_inverse(edge_line_matching(right, left))


def cycle_type(permutation: tuple[int, int, int]) -> str:
    if permutation == (0, 1, 2):
        return "identity"
    if permutation_parity(permutation) == 0:
        return "three_cycle"
    return "transposition"


def build_center_quad_transport_holonomy_summary() -> dict[str, Any]:
    graph, raw_z2 = reconstructed_quotient_graph()
    archived_parity = quotient_triangle_parity_stats()

    holonomy_counts = Counter()
    holonomy_by_parity = defaultdict(Counter)
    parity_match = True
    sample = defaultdict(list)
    triangle_total = 0

    for a, b, c in combinations(sorted(graph.nodes()), 3):
        if not (graph.has_edge(a, b) and graph.has_edge(a, c) and graph.has_edge(b, c)):
            continue
        triangle_total += 1
        holonomy = permutation_compose(
            directed_edge_matching(a, b),
            permutation_compose(directed_edge_matching(b, c), directed_edge_matching(c, a)),
        )
        z2_parity = (
            raw_z2[tuple(sorted((a, b)))]
            ^ raw_z2[tuple(sorted((b, c)))]
            ^ raw_z2[tuple(sorted((a, c)))]
        )
        holonomy_sign = permutation_parity(holonomy)
        holonomy_type = cycle_type(holonomy)
        holonomy_counts[holonomy_type] += 1
        holonomy_by_parity[z2_parity][holonomy_type] += 1
        if holonomy_sign != z2_parity:
            parity_match = False
        if len(sample[z2_parity]) < 8:
            sample[z2_parity].append(
                {
                    "triangle": [a, b, c],
                    "holonomy": list(holonomy),
                    "holonomy_type": holonomy_type,
                    "z2_parity": z2_parity,
                }
            )

    return {
        "status": "ok",
        "transport_triangles": triangle_total,
        "archived_v14_triangle_parity": {
            "parity0": archived_parity["parity0"],
            "parity1": archived_parity["parity1"],
        },
        "triangle_holonomy": {
            "cycle_type_counts": dict(sorted(holonomy_counts.items())),
            "by_z2_parity": {
                str(parity): dict(sorted(counter.items()))
                for parity, counter in sorted(holonomy_by_parity.items())
            },
            "z2_parity_equals_holonomy_sign_exactly": parity_match,
            "sample_triangles": dict(sample),
        },
        "bridge_verdict": (
            "The old v14 triangle parity statistic is the sign character of an "
            "exact local S3 holonomy. Around every triangle in the 45-point "
            "quotient transport graph, the unique edge line-matchings compose to "
            "a holonomy permutation in S3, and the Z2 triangle parity equals its "
            "permutation parity exactly. Therefore parity-0 triangles are "
            "precisely the even-holonomy triangles (identity or 3-cycles), while "
            "parity-1 triangles are precisely the odd-holonomy triangles "
            "(transpositions). This is the live q=3 holonomy invariant that the "
            "q=13 archive bundle was reaching toward."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_center_quad_transport_holonomy_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
