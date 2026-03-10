"""Explicit M\"obius/Csaszar torus seed as two Fano heptads on the same 7 vertices.

This module upgrades the surface/Fano bridge from pure counting to a concrete
triangulation model. On the vertex set Z/7Z define the two cyclic heptads

    A = {i, i+1, i+3},
    B = {i, i+2, i+3},

with indices modulo 7. Then:

- A is the standard cyclic realization of the Fano plane line set;
- B is a second Steiner triple system on the same 7 points;
- A union B is the classical 7-vertex torus triangulation (the M\"obius torus,
  combinatorially the Csaszar seed);
- every edge of K7 lies in exactly one triangle from A and one triangle from B.

So the 14 torus faces split exactly as 7 + 7, i.e. as two Fano heptads on the
same labeled vertex set.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
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

from w33_surface_neighborly_bridge import map_flag_count_from_edges


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_mobius_fano_bridge_summary.json"

Vertex = int
Edge = tuple[int, int]
Triangle = tuple[int, int, int]


@dataclass(frozen=True)
class MobiusFanoSummary:
    standard_heptad_size: int
    complementary_heptad_size: int
    union_face_count: int
    vertex_count: int
    edge_count: int
    euler_characteristic: int
    triangle_vertex_incidences: int
    torus_rank3_flag_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_triangle(a: int, b: int, c: int) -> Triangle:
    return tuple(sorted(((a % 7), (b % 7), (c % 7))))


def cyclic_triangle_heptad(offsets: tuple[int, int, int]) -> tuple[Triangle, ...]:
    return tuple(sorted({normalize_triangle(i + offsets[0], i + offsets[1], i + offsets[2]) for i in range(7)}))


def standard_fano_heptad() -> tuple[Triangle, ...]:
    return cyclic_triangle_heptad((0, 1, 3))


def complementary_fano_heptad() -> tuple[Triangle, ...]:
    return cyclic_triangle_heptad((0, 2, 3))


def complementary_fano_heptad_alias() -> tuple[Triangle, ...]:
    return cyclic_triangle_heptad((0, 1, 5))


def triangle_edges(triangle: Triangle) -> tuple[Edge, Edge, Edge]:
    return tuple(sorted(tuple(sorted(edge)) for edge in combinations(triangle, 2)))


def edge_multiplicities(triangles: tuple[Triangle, ...]) -> dict[Edge, int]:
    counts: dict[Edge, int] = {}
    for triangle in triangles:
        for edge in triangle_edges(triangle):
            counts[edge] = counts.get(edge, 0) + 1
    return counts


def is_steiner_triple_system(triangles: tuple[Triangle, ...]) -> bool:
    counts = edge_multiplicities(triangles)
    return len(triangles) == 7 and len(counts) == 21 and set(counts.values()) == {1}


def mobius_torus_faces() -> tuple[Triangle, ...]:
    return tuple(sorted(set(standard_fano_heptad()) | set(complementary_fano_heptad())))


def torus_edge_membership_by_heptad() -> dict[Edge, tuple[int, int]]:
    standard_counts = edge_multiplicities(standard_fano_heptad())
    complementary_counts = edge_multiplicities(complementary_fano_heptad())
    edges = sorted(set(standard_counts) | set(complementary_counts))
    return {
        edge: (standard_counts.get(edge, 0), complementary_counts.get(edge, 0))
        for edge in edges
    }


def torus_euler_characteristic() -> int:
    vertices = 7
    edges = 21
    faces = len(mobius_torus_faces())
    return vertices - edges + faces


def build_mobius_fano_summary() -> dict[str, Any]:
    standard = standard_fano_heptad()
    complementary = complementary_fano_heptad()
    torus_faces = mobius_torus_faces()
    union_edge_counts = edge_multiplicities(torus_faces)
    per_edge_heptad_membership = torus_edge_membership_by_heptad()
    summary = MobiusFanoSummary(
        standard_heptad_size=len(standard),
        complementary_heptad_size=len(complementary),
        union_face_count=len(torus_faces),
        vertex_count=7,
        edge_count=len(union_edge_counts),
        euler_characteristic=torus_euler_characteristic(),
        triangle_vertex_incidences=3 * len(torus_faces),
        torus_rank3_flag_count=map_flag_count_from_edges(len(union_edge_counts)),
    )

    return {
        "status": "ok",
        "summary": summary.to_dict(),
        "vertex_set": list(range(7)),
        "standard_fano_heptad": standard,
        "complementary_fano_heptad": complementary,
        "complementary_heptad_alias_via_015": complementary_fano_heptad_alias(),
        "steiner_system_checks": {
            "standard_is_sts_7": is_steiner_triple_system(standard),
            "complementary_is_sts_7": is_steiner_triple_system(complementary),
            "two_heptads_are_distinct": set(standard) != set(complementary),
        },
        "mobius_torus_checks": {
            "face_count": len(torus_faces),
            "edge_count": len(union_edge_counts),
            "euler_characteristic": torus_euler_characteristic(),
            "each_edge_lies_in_two_triangles": set(union_edge_counts.values()) == {2},
            "each_edge_seen_once_per_heptad": all(multiplicities == (1, 1) for multiplicities in per_edge_heptad_membership.values()),
        },
        "incidence_lift": {
            "triangle_vertex_incidences": 3 * len(torus_faces),
            "equals_two_fano_flag_sets": (3 * len(torus_faces)) == 2 * 21,
            "rank3_flags": map_flag_count_from_edges(len(union_edge_counts)),
            "matches_csaszar_flag_count": map_flag_count_from_edges(len(union_edge_counts)) == 84,
        },
        "bridge_verdict": (
            "The labeled 7-vertex M\"obius/Csaszar torus seed is literally the union "
            "of two Fano heptads on the same vertex set. Each heptad is an STS(7), "
            "and every edge of K7 belongs to exactly one triangle from each heptad."
        ),
        "scope_note": (
            "This is a labeled cyclic model of the torus seed. It sharpens the "
            "surface/Fano bridge from counts to an explicit face decomposition, but "
            "it does not yet produce a canonical Szilassi-dual or tomotope incidence map."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_mobius_fano_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
