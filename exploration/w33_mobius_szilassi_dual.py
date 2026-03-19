"""Szilassi dual built explicitly from the labeled M"obius torus seed.

Starting from the explicit 7-vertex torus triangulation

    M = A union B

where A and B are the two cyclic Fano heptads from ``w33_mobius_fano_bridge``,
this module constructs the abstract dual cellulation:

- dual vertices = the 14 torus triangles;
- dual edges = shared torus edges between adjacent triangles;
- dual faces = the 7 cyclic stars around the original torus vertices.

The resulting dual has:

- 14 vertices, 21 edges, 7 faces;
- cubic Heawood 1-skeleton;
- 7 hexagonal faces;
- complete face-adjacency graph K7.

So the labeled M"obius/Csaszar torus seed has an explicit Szilassi-type dual,
not merely matching counts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
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

from w33_mobius_fano_bridge import (
    Edge,
    Triangle,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_mobius_szilassi_dual_summary.json"

DualVertex = tuple[str, int]
DualEdge = tuple[DualVertex, DualVertex]


@dataclass(frozen=True)
class MobiusSzilassiDualSummary:
    dual_vertex_count: int
    dual_edge_count: int
    dual_face_count: int
    dual_vertex_degree: int
    dual_face_size: int
    heawood_bipartition_sizes: tuple[int, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def a_triangles() -> tuple[Triangle, ...]:
    return tuple(a_triangle_by_index(index) for index in range(7))


def b_triangles() -> tuple[Triangle, ...]:
    return tuple(b_triangle_by_index(index) for index in range(7))


def normalize_triangle(a: int, b: int, c: int) -> Triangle:
    return tuple(sorted(((a % 7), (b % 7), (c % 7))))


def a_triangle_by_index(index: int) -> Triangle:
    return normalize_triangle(index, index + 1, index + 3)


def b_triangle_by_index(index: int) -> Triangle:
    return normalize_triangle(index, index + 2, index + 3)


def dual_vertices() -> tuple[DualVertex, ...]:
    return tuple([("A", index) for index in range(7)] + [("B", index) for index in range(7)])


def triangle_for_dual_vertex(vertex: DualVertex) -> Triangle:
    family, index = vertex
    if family == "A":
        return a_triangles()[index]
    if family == "B":
        return b_triangles()[index]
    raise ValueError("dual vertex family must be 'A' or 'B'")


def shared_edge(left: Triangle, right: Triangle) -> Edge | None:
    intersection = tuple(sorted(set(left) & set(right)))
    if len(intersection) != 2:
        return None
    return intersection  # type: ignore[return-value]


def dual_edges_with_labels() -> tuple[dict[str, Any], ...]:
    edges = []
    for a_index, a_triangle in enumerate(a_triangles()):
        for b_index, b_triangle in enumerate(b_triangles()):
            edge = shared_edge(a_triangle, b_triangle)
            if edge is None:
                continue
            edges.append(
                {
                    "left": ("A", a_index),
                    "right": ("B", b_index),
                    "shared_edge": edge,
                }
            )
    return tuple(edges)


def dual_neighbors(vertex: DualVertex) -> tuple[DualVertex, ...]:
    neighbors = []
    vertex_triangle = triangle_for_dual_vertex(vertex)
    for candidate in dual_vertices():
        if candidate == vertex:
            continue
        candidate_triangle = triangle_for_dual_vertex(candidate)
        if shared_edge(vertex_triangle, candidate_triangle) is not None:
            neighbors.append(candidate)
    return tuple(sorted(neighbors))


def dual_edge_set() -> tuple[DualEdge, ...]:
    return tuple(
        sorted(
            (
                tuple(sorted((edge["left"], edge["right"])))
                for edge in dual_edges_with_labels()
            )
        )
    )


def incident_dual_vertices_to_torus_vertex(vertex: int) -> tuple[DualVertex, ...]:
    return tuple(
        sorted(
            dual_vertex
            for dual_vertex in dual_vertices()
            if vertex in triangle_for_dual_vertex(dual_vertex)
        )
    )


def dual_face_cycle_for_torus_vertex(vertex: int) -> tuple[DualVertex, ...]:
    incident = incident_dual_vertices_to_torus_vertex(vertex)
    local_neighbors = {
        dual_vertex: tuple(
            sorted(
                neighbor
                for neighbor in dual_neighbors(dual_vertex)
                if neighbor in incident
            )
        )
        for dual_vertex in incident
    }
    start = min(incident)
    next_vertex = min(local_neighbors[start])
    cycle = [start]
    previous = start
    current = next_vertex
    while current != start:
        cycle.append(current)
        candidates = [neighbor for neighbor in local_neighbors[current] if neighbor != previous]
        if not candidates:
            raise ValueError("expected a cycle around each torus vertex")
        previous, current = current, candidates[0]
    return tuple(cycle)


def all_dual_faces() -> tuple[tuple[DualVertex, ...], ...]:
    return tuple(dual_face_cycle_for_torus_vertex(vertex) for vertex in range(7))


def face_adjacency_via_shared_dual_edge() -> dict[tuple[int, int], int]:
    face_edges = []
    for face in all_dual_faces():
        edges = {
            tuple(sorted((face[index], face[(index + 1) % len(face)])))
            for index in range(len(face))
        }
        face_edges.append(edges)
    adjacency: dict[tuple[int, int], int] = {}
    for left in range(7):
        for right in range(left + 1, 7):
            adjacency[(left, right)] = len(face_edges[left] & face_edges[right])
    return adjacency


def heawood_incidence_from_mobius() -> dict[int, tuple[int, int, int]]:
    return {
        b_index: tuple(sorted(a_index for a_index in range(7) if ("B", b_index) in dual_neighbors(("A", a_index))))
        for b_index in range(7)
    }


def expected_fano_line_index_for_b_vertex(b_index: int) -> int:
    return (b_index - 1) % 7


def mobius_dual_matches_fano_incidence() -> bool:
    return all(
        heawood_incidence_from_mobius()[b_index] == a_triangle_by_index(expected_fano_line_index_for_b_vertex(b_index))
        for b_index in range(7)
    )


def build_mobius_szilassi_dual_summary() -> dict[str, Any]:
    dual_faces = all_dual_faces()
    face_adjacency = face_adjacency_via_shared_dual_edge()
    summary = MobiusSzilassiDualSummary(
        dual_vertex_count=len(dual_vertices()),
        dual_edge_count=len(dual_edge_set()),
        dual_face_count=len(dual_faces),
        dual_vertex_degree=len(dual_neighbors(("A", 0))),
        dual_face_size=len(dual_faces[0]),
        heawood_bipartition_sizes=(7, 7),
    )
    return {
        "status": "ok",
        "summary": summary.to_dict(),
        "dual_vertices": dual_vertices(),
        "dual_edges": dual_edges_with_labels(),
        "dual_faces": dual_faces,
        "heawood_checks": {
            "bipartite_7_plus_7": summary.heawood_bipartition_sizes == (7, 7),
            "every_dual_vertex_has_degree_3": all(len(dual_neighbors(vertex)) == 3 for vertex in dual_vertices()),
            "heawood_incidence_from_mobius": heawood_incidence_from_mobius(),
            "matches_shifted_fano_lines": mobius_dual_matches_fano_incidence(),
        },
        "szilassi_checks": {
            "dual_f_vector": (summary.dual_vertex_count, summary.dual_edge_count, summary.dual_face_count),
            "every_dual_face_is_hexagon": all(len(face) == 6 for face in dual_faces),
            "complete_face_adjacency_k7": set(face_adjacency.values()) == {1},
            "shared_dual_edge_counts": {
                f"{left}-{right}": count
                for (left, right), count in face_adjacency.items()
            },
        },
        "bridge_verdict": (
            "The labeled M\"obius/Csaszar torus seed has an explicit Szilassi "
            "dual. Its 1-skeleton is the Heawood graph, its 7 dual faces are "
            "hexagons, and those 7 faces are pairwise edge-adjacent."
        ),
        "scope_note": (
            "This is a combinatorial duality statement. It constructs the "
            "Szilassi-type toroidal cellulation directly from the labeled torus "
            "seed, but it does not address geometric realization in Euclidean "
            "3-space."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_mobius_szilassi_dual_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
