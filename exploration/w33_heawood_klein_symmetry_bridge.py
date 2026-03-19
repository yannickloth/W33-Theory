"""Exact Heawood/Klein symmetry bridge from the Szilassi dual.

The labeled M"obius/Csaszar torus seed already promotes to an explicit
Szilassi dual with Heawood 1-skeleton. This module closes the next exact step:

- the bipartition-preserving automorphisms of that Heawood graph are exactly
  the 168 Fano collineations;
- the explicit polarity i |-> -i mod 7 swaps points and lines and is itself a
  graph automorphism;
- therefore the full Heawood automorphism package has order 336 = 2 * 168.

So the torus/Fano route lands directly on the same 168/336 shell that already
organizes the promoted Klein-quartic side.
"""

from __future__ import annotations

from collections import deque
from functools import lru_cache
import itertools
import json
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_fano_group_bridge import build_fano_group_summary
from w33_klein_harmonic_vogel_bridge import build_klein_harmonic_vogel_summary
from w33_mobius_szilassi_dual import (
    dual_neighbors,
    dual_vertices,
    heawood_incidence_from_mobius,
)
from w33_surface_neighborly_bridge import dual_pair_total_flags


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_heawood_klein_symmetry_bridge_summary.json"

Permutation7 = tuple[int, ...]
Permutation14 = tuple[int, ...]
DualVertex = tuple[str, int]


def _vertex_order() -> tuple[DualVertex, ...]:
    return dual_vertices()


def _vertex_index() -> dict[DualVertex, int]:
    return {vertex: index for index, vertex in enumerate(_vertex_order())}


def _edge_set() -> frozenset[tuple[int, int]]:
    index = _vertex_index()
    edges = set()
    for vertex in _vertex_order():
        for neighbor in dual_neighbors(vertex):
            left = index[vertex]
            right = index[neighbor]
            edges.add(tuple(sorted((left, right))))
    return frozenset(edges)


def _bipartition() -> tuple[tuple[DualVertex, ...], tuple[DualVertex, ...]]:
    return (
        tuple(vertex for vertex in _vertex_order() if vertex[0] == "A"),
        tuple(vertex for vertex in _vertex_order() if vertex[0] == "B"),
    )


def _adjacency() -> tuple[tuple[int, ...], ...]:
    index = _vertex_index()
    adjacency = {index[vertex]: [] for vertex in _vertex_order()}
    for vertex in _vertex_order():
        source = index[vertex]
        for neighbor in dual_neighbors(vertex):
            adjacency[source].append(index[neighbor])
    return tuple(tuple(sorted(neighbors)) for _, neighbors in sorted(adjacency.items()))


def _connected_bipartition_unique_up_to_swap() -> bool:
    adjacency = _adjacency()
    colors: dict[int, int] = {0: 0}
    queue: deque[int] = deque([0])
    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            expected = 1 - colors[current]
            if neighbor in colors:
                if colors[neighbor] != expected:
                    return False
                continue
            colors[neighbor] = expected
            queue.append(neighbor)
    return len(colors) == len(adjacency)


def _incidence() -> dict[int, tuple[int, int, int]]:
    return heawood_incidence_from_mobius()


def _line_index_by_point_set() -> dict[frozenset[int], int]:
    return {frozenset(points): line for line, points in _incidence().items()}


@lru_cache(maxsize=1)
def _point_collineations() -> tuple[Permutation7, ...]:
    line_index = _line_index_by_point_set()
    collineations = []
    for perm in itertools.permutations(range(7)):
        ok = True
        for points in _incidence().values():
            mapped = frozenset(perm[point] for point in points)
            if mapped not in line_index:
                ok = False
                break
        if ok:
            collineations.append(tuple(perm))
    return tuple(sorted(collineations))


def _induced_line_permutation(point_perm: Permutation7) -> Permutation7:
    line_index = _line_index_by_point_set()
    image = []
    for line in range(7):
        mapped = frozenset(point_perm[point] for point in _incidence()[line])
        image.append(line_index[mapped])
    return tuple(image)


def _line_action_is_unique() -> bool:
    seen = {}
    for point_perm in _point_collineations():
        line_perm = _induced_line_permutation(point_perm)
        if point_perm in seen and seen[point_perm] != line_perm:
            return False
        seen[point_perm] = line_perm
    return True


def _lift_bipartition_preserving(point_perm: Permutation7) -> Permutation14:
    line_perm = _induced_line_permutation(point_perm)
    index = _vertex_index()
    image = [0] * 14
    for point in range(7):
        image[index[("A", point)]] = index[("A", point_perm[point])]
    for line in range(7):
        image[index[("B", line)]] = index[("B", line_perm[line])]
    return tuple(image)


def _compose(left: Permutation14, right: Permutation14) -> Permutation14:
    return tuple(left[index] for index in right)


def _permutes_edges(perm: Permutation14) -> bool:
    edges = _edge_set()
    for left, right in edges:
        image = tuple(sorted((perm[left], perm[right])))
        if image not in edges:
            return False
    return True


def _polarity_index_permutation() -> Permutation7:
    return tuple((-index) % 7 for index in range(7))


def _polarity_is_incidence_duality() -> bool:
    polarity = _polarity_index_permutation()
    incidence = _incidence()
    for point in range(7):
        for line in range(7):
            if (point in incidence[line]) != (polarity[line] in incidence[polarity[point]]):
                return False
    return True


def _lift_polarity_swap() -> Permutation14:
    polarity = _polarity_index_permutation()
    index = _vertex_index()
    image = [0] * 14
    for point in range(7):
        image[index[("A", point)]] = index[("B", polarity[point])]
    for line in range(7):
        image[index[("B", line)]] = index[("A", polarity[line])]
    return tuple(image)


def _generated_full_group() -> tuple[Permutation14, ...]:
    preserving = {_lift_bipartition_preserving(perm) for perm in _point_collineations()}
    swap = _lift_polarity_swap()
    seen = set(preserving) | {swap}
    frontier = list(seen)
    while frontier:
        current = frontier.pop()
        for generator in tuple(preserving) + (swap,):
            for candidate in (_compose(generator, current), _compose(current, generator)):
                if candidate not in seen:
                    seen.add(candidate)
                    frontier.append(candidate)
    return tuple(sorted(seen))


def _edge_stabilizer_order(group: tuple[Permutation14, ...]) -> int:
    reference_edge = min(_edge_set())
    return sum(
        1
        for perm in group
        if tuple(sorted((perm[reference_edge[0]], perm[reference_edge[1]]))) == reference_edge
    )


@lru_cache(maxsize=1)
def build_heawood_klein_symmetry_summary() -> dict[str, Any]:
    preserving_group = tuple(
        sorted(_lift_bipartition_preserving(perm) for perm in _point_collineations())
    )
    full_group = _generated_full_group()
    polarity = _lift_polarity_swap()
    fano_group = build_fano_group_summary()
    klein = build_klein_harmonic_vogel_summary()

    klein_order = int(klein["harmonic_quartic_dictionary"]["klein_quartic_automorphism_order"])
    dual_pair_flags = dual_pair_total_flags()

    return {
        "status": "ok",
        "heawood_graph": {
            "vertex_count": len(_vertex_order()),
            "edge_count": len(_edge_set()),
            "bipartition_sizes": [len(_bipartition()[0]), len(_bipartition()[1])],
            "connected_bipartition_unique_up_to_swap": _connected_bipartition_unique_up_to_swap(),
            "is_levi_graph_of_fano_plane": True,
        },
        "bipartition_preserving_symmetry": {
            "point_collineation_order": len(_point_collineations()),
            "line_action_is_unique": _line_action_is_unique(),
            "heawood_bipartition_preserving_order": len(preserving_group),
            "flag_edge_stabilizer_order": _edge_stabilizer_order(preserving_group),
            "matches_fano_collineation_order": (
                len(_point_collineations()) == fano_group["summary"]["group_order"]
            ),
            "matches_fano_flag_stabilizer_order": (
                _edge_stabilizer_order(preserving_group)
                == fano_group["summary"]["flag_stabilizer_order"]
            ),
            "matches_dual_toroidal_pair_flag_count": len(preserving_group) == dual_pair_flags,
        },
        "point_line_duality": {
            "polarity_formula": "i -> -i mod 7",
            "polarity_permutation": list(_polarity_index_permutation()),
            "polarity_is_incidence_duality": _polarity_is_incidence_duality(),
            "polarity_swap_is_edge_automorphism": _permutes_edges(polarity),
            "polarity_swap_is_involution": _compose(polarity, polarity) == tuple(range(14)),
        },
        "full_symmetry": {
            "full_heawood_automorphism_order": len(full_group),
            "full_equals_two_times_bipartition_preserving": len(full_group) == 2 * len(preserving_group),
            "edge_stabilizer_order": _edge_stabilizer_order(full_group),
            "generated_by_collineations_and_polarity": True,
            "all_generated_permutations_preserve_edges": all(_permutes_edges(perm) for perm in full_group),
            "full_order_equals_two_times_dual_toroidal_pair_flags": len(full_group) == 2 * dual_pair_flags,
        },
        "klein_quartic_bridge": {
            "klein_quartic_orientation_preserving_order": klein_order,
            "matches_klein_quartic_orientation_preserving_order": len(preserving_group) == klein_order,
            "full_heawood_order_is_double_klein_order": len(full_group) == 2 * klein_order,
            "preserving_order_equals_8_times_21": len(preserving_group) == 8 * len(_edge_set()),
            "full_order_equals_16_times_21": len(full_group) == 16 * len(_edge_set()),
        },
        "bridge_verdict": (
            "The Szilassi/Heawood dual now lands directly on the promoted Klein "
            "shell. Its bipartition-preserving automorphism group is exactly the "
            "168-element Fano collineation group, while the explicit polarity "
            "i -> -i mod 7 swaps points and lines and doubles that to the full "
            "Heawood automorphism order 336. So the torus dual is no longer only "
            "a Heawood count or spectral packet: it already carries the same "
            "168/336 symmetry ladder as the Klein-quartic side."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_heawood_klein_symmetry_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
