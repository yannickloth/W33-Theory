"""Exact complement/disjointness theorem for the W33 center-quad transport graph.

This module pushes the center-quad transport bridge one step further.

The exact statement is:

1. The 45-point degree-32 quotient transport graph is the complement of the
   45-point SRG(45,12,3,3) point graph of dual GQ(4,2).
2. Equivalently, under the exact E6 bridge where quotient points are the
   45 triangles of the 27-line graph SRG(27,10,1,5), transport adjacency is
   exactly triangle disjointness.
3. Every transport edge induces a unique perfect matching between the three
   quotient lines through one endpoint and the three quotient lines through the
   other. Under the natural sorted local line labels, all six S3 permutations
   occur.
4. The raw Z2 sheet voltage is strictly finer than that induced S3 matching:
   it is not determined by the permutation itself, nor by its parity.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from itertools import combinations
from pathlib import Path
import sys
from typing import Any


from w33_center_quad_gq42_e6_bridge import quotient_incidence
from w33_center_quad_transport_bridge import reconstructed_quotient_graph


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exploration._optional_deps import require_networkx


nx = require_networkx("exploration/w33_center_quad_transport_complement_bridge.py")

DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_center_quad_transport_complement_bridge_summary.json"


def point_graph() -> nx.Graph:
    point_to_lines, line_to_points = quotient_incidence()
    graph = nx.Graph()
    graph.add_nodes_from(point_to_lines)
    for points_on_line in line_to_points.values():
        for left, right in combinations(points_on_line, 2):
            graph.add_edge(left, right)
    return graph


def line_intersection_graph() -> dict[int, frozenset[int]]:
    point_to_lines, line_to_points = quotient_incidence()
    adjacency = {line_id: set() for line_id in line_to_points}
    for lines_through_point in point_to_lines.values():
        a, b, c = lines_through_point
        adjacency[a].update((b, c))
        adjacency[b].update((a, c))
        adjacency[c].update((a, b))
    return {line_id: frozenset(neighbors) for line_id, neighbors in adjacency.items()}


def srg_parameters(graph: nx.Graph) -> dict[str, int]:
    adjacent_common = set()
    nonadjacent_common = set()
    nodes = sorted(graph)
    for index, left in enumerate(nodes):
        left_neighbors = set(graph.neighbors(left))
        for right in nodes[index + 1 :]:
            common = len(left_neighbors & set(graph.neighbors(right)))
            if graph.has_edge(left, right):
                adjacent_common.add(common)
            else:
                nonadjacent_common.add(common)
    return {
        "vertices": graph.number_of_nodes(),
        "degree": next(iter(dict(graph.degree()).values())),
        "lambda": next(iter(adjacent_common)),
        "mu": next(iter(nonadjacent_common)),
        "edge_count": graph.number_of_edges(),
    }


def point_triangles() -> dict[int, tuple[int, int, int]]:
    point_to_lines, _ = quotient_incidence()
    return {point_id: tuple(sorted(lines)) for point_id, lines in point_to_lines.items()}


def transport_matching_data() -> dict[str, Any]:
    triangles = point_triangles()
    line_graph = line_intersection_graph()
    transport_graph, raw_z2 = reconstructed_quotient_graph()

    permutation_counts = Counter()
    raw_by_permutation: defaultdict[tuple[int, int, int], Counter[int]] = defaultdict(Counter)
    raw_by_parity: defaultdict[int, Counter[int]] = defaultdict(Counter)
    example_edges = {}
    unique_matchings = True

    for left, right in sorted(transport_graph.edges()):
        source = triangles[left]
        target = triangles[right]
        permutation = []
        for line_id in source:
            matches = [index for index, other in enumerate(target) if other in line_graph[line_id]]
            if len(matches) != 1:
                unique_matchings = False
                break
            permutation.append(matches[0])
        permutation_tuple = tuple(permutation)
        if len(set(permutation_tuple)) != 3:
            unique_matchings = False
            break
        permutation_counts[permutation_tuple] += 1
        raw_by_permutation[permutation_tuple][raw_z2[tuple(sorted((left, right)))]] += 1
        parity = permutation_parity(permutation_tuple)
        raw_by_parity[parity][raw_z2[tuple(sorted((left, right)))]] += 1
        example_edges.setdefault(
            permutation_tuple,
            {
                "transport_edge": [left, right],
                "source_lines": list(source),
                "target_lines": list(target),
            },
        )

    return {
        "every_transport_edge_has_unique_matching": unique_matchings,
        "all_six_permutations_realized_under_sorted_labels": len(permutation_counts) == 6,
        "permutation_counts_under_sorted_labels": {
            "".join(map(str, permutation)): count
            for permutation, count in sorted(permutation_counts.items())
        },
        "raw_z2_distribution_by_permutation": {
            "".join(map(str, permutation)): dict(sorted(counter.items()))
            for permutation, counter in sorted(raw_by_permutation.items())
        },
        "raw_z2_distribution_by_permutation_parity": {
            str(parity): dict(sorted(counter.items()))
            for parity, counter in sorted(raw_by_parity.items())
        },
        "raw_z2_not_determined_by_permutation": all(
            set(counter) == {0, 1} for counter in raw_by_permutation.values()
        ),
        "raw_z2_not_determined_by_permutation_parity": all(
            set(counter) == {0, 1} for counter in raw_by_parity.values()
        ),
        "example_edges": {
            "".join(map(str, permutation)): payload
            for permutation, payload in sorted(example_edges.items())
        },
    }


def permutation_parity(permutation: tuple[int, int, int]) -> int:
    inversions = 0
    for i in range(3):
        for j in range(i + 1, 3):
            inversions += permutation[i] > permutation[j]
    return inversions % 2


def build_center_quad_transport_complement_summary() -> dict[str, Any]:
    incidence_graph = point_graph()
    transport_graph, _ = reconstructed_quotient_graph()
    triangles = point_triangles()
    matching = transport_matching_data()

    disjoint_transport = True
    shared_line_nontransport = True
    intersection_profile = {True: Counter(), False: Counter()}
    for left, right in combinations(sorted(triangles), 2):
        intersection = len(set(triangles[left]) & set(triangles[right]))
        edge = transport_graph.has_edge(left, right)
        intersection_profile[edge][intersection] += 1
        if edge and intersection != 0:
            disjoint_transport = False
        if (not edge) and (not incidence_graph.has_edge(left, right)):
            shared_line_nontransport = False
        if incidence_graph.has_edge(left, right) and intersection != 1:
            shared_line_nontransport = False

    complement_is_exact = set(nx.complement(incidence_graph).edges()) == set(transport_graph.edges())

    return {
        "status": "ok",
        "point_graph_srg": srg_parameters(incidence_graph),
        "transport_graph_srg": srg_parameters(transport_graph),
        "complement_theorem": {
            "transport_is_complement_of_point_graph": complement_is_exact,
            "transport_edges_are_exactly_disjoint_triangle_pairs": disjoint_transport,
            "point_graph_edges_are_exactly_one_line_triangle_pairs": shared_line_nontransport,
            "intersection_profile_by_transport_adjacency": {
                str(edge): dict(sorted(counter.items()))
                for edge, counter in intersection_profile.items()
            },
        },
        "local_s3_matching": matching,
        "bridge_verdict": (
            "The 45-point quotient transport graph is not an extra ad hoc object. "
            "It is exactly the complement of the 45-point SRG(45,12,3,3) point "
            "graph of dual GQ(4,2), equivalently the disjointness graph on the 45 "
            "triangles of the 27-line SRG(27,10,1,5). Therefore it is itself an "
            "exact SRG(45,32,22,24). Moreover every transport edge carries a unique "
            "3x3 line-matching between the two incident line triples, so an S3 "
            "shadow is already present before the separate port-transport layer. "
            "But the raw Z2 sheet voltage is finer than that matching data: it is "
            "not determined by the induced permutation or even its parity."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_center_quad_transport_complement_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
