"""Surface-neighborly bridge from Csaszar/Szilassi to minimal triangulations.

This module isolates the 2-dimensional prototype behind the 4-dimensional
minimal-triangulation bridge:

- the Csaszar polyhedron is the toroidal 7-vertex triangulation with 1-skeleton K7;
- the Szilassi polyhedron is the dual 7-face toroidal polyhedron with face-adjacency
  graph K7.

For an orientable triangular embedding of K_n, Euler's relation gives

    g = (n - 3)(n - 4) / 12.

Dually, for a toroidal polyhedral surface whose faces are pairwise edge-adjacent,

    g = (f - 3)(f - 4) / 12.

So the Csaszar/Szilassi pair is the genus-1 surface prototype of the same
extremal-neighborly mechanism that later reappears in the 4D CP2/K3 seeds.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import lru_cache
import json
from math import comb, factorial
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_surface_neighborly_bridge_summary.json"


@dataclass(frozen=True)
class SurfaceNeighborlySeed:
    name: str
    genus: int
    vertices: int
    edges: int
    faces: int
    complete_vertex_adjacency: bool
    complete_face_adjacency: bool
    one_skeleton_graph: str
    face_adjacency_graph: str
    convex_cell_realization_obstructed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def tetrahedron_counts() -> dict[str, int]:
    """Combinatorial counts for the regular tetrahedron."""

    vertices, edges, faces = complete_graph_triangulation_counts(4)
    return {
        "vertices": vertices,
        "edges": edges,
        "faces": faces,
        "genus": 0,
        "flags": map_flag_count_from_edges(edges),
        "automorphism_group_order": 24,
    }


def fano_plane_counts() -> dict[str, int]:
    """Basic point-line incidence data for the Fano plane."""

    points = 7
    lines = 7
    incidences_per_point = 3
    incidences_per_line = 3
    flags = points * incidences_per_point
    return {
        "points": points,
        "lines": lines,
        "incidences_per_point": incidences_per_point,
        "incidences_per_line": incidences_per_line,
        "flags": flags,
    }


def orientable_surface_complete_graph_genus(n_vertices: int) -> Fraction:
    """Genus forced by a triangular embedding of the complete graph K_n."""

    if n_vertices < 0:
        raise ValueError("n_vertices must be nonnegative")
    return Fraction((n_vertices - 3) * (n_vertices - 4), 12)


def orientable_surface_complete_face_adjacency_genus(n_faces: int) -> Fraction:
    """Dual genus forced by a complete face-adjacency graph K_f."""

    if n_faces < 0:
        raise ValueError("n_faces must be nonnegative")
    return Fraction((n_faces - 3) * (n_faces - 4), 12)


def complete_graph_triangulation_counts(n_vertices: int) -> tuple[int, int, int]:
    """Counts for a triangular K_n embedding when the Euler data is integral."""

    if n_vertices < 0:
        raise ValueError("n_vertices must be nonnegative")
    edges = comb(n_vertices, 2)
    double_faces = 2 * edges
    if double_faces % 3 != 0:
        raise ValueError("No triangular complete-graph embedding counts for this n")
    faces = double_faces // 3
    return (n_vertices, edges, faces)


def complete_face_adjacency_surface_counts(n_faces: int) -> tuple[int, int, int]:
    """Counts for the trivalent dual of a triangular K_f embedding."""

    if n_faces < 0:
        raise ValueError("n_faces must be nonnegative")
    edges = comb(n_faces, 2)
    double_edges = 2 * edges
    if double_edges % 3 != 0:
        raise ValueError("No trivalent complete-face-adjacency counts for this f")
    vertices = double_edges // 3
    return (vertices, edges, n_faces)


def minimum_vertices_for_complete_graph_seed_genus(genus: int, max_vertices: int = 200) -> int:
    """Smallest n whose complete-graph seed genus is at least the target genus."""

    if genus < 0:
        raise ValueError("genus must be nonnegative")
    for n in range(4, max_vertices + 1):
        if orientable_surface_complete_graph_genus(n) >= genus:
            return n
    raise ValueError("max_vertices too small for requested genus")


def minimum_faces_for_complete_face_adjacency_genus(genus: int, max_faces: int = 200) -> int:
    """Smallest f whose complete face-adjacency seed genus is at least the target genus."""

    if genus < 0:
        raise ValueError("genus must be nonnegative")
    for f in range(4, max_faces + 1):
        if orientable_surface_complete_face_adjacency_genus(f) >= genus:
            return f
    raise ValueError("max_faces too small for requested genus")


@lru_cache(maxsize=None)
def stirling_second_kind(n: int, k: int) -> int:
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0 or k > n:
        return 0
    if k == 1 or k == n:
        return 1
    return stirling_second_kind(n - 1, k - 1) + k * stirling_second_kind(n - 1, k)


def barycentric_subdivision_f_vector(
    f_vector: tuple[int, ...],
    steps: int = 1,
) -> tuple[int, ...]:
    """Generic barycentric subdivision f-vector transform."""

    if steps < 0:
        raise ValueError("steps must be nonnegative")

    current = tuple(int(x) for x in f_vector)
    dim = len(current) - 1
    for _ in range(steps):
        next_vector = []
        for j in range(dim + 1):
            total = 0
            for i in range(j, dim + 1):
                total += current[i] * factorial(j + 1) * stirling_second_kind(i + 2, j + 2)
            next_vector.append(total)
        current = tuple(next_vector)
    return current


def convex_cell_realization_obstructed_for_complete_graph(order: int) -> bool:
    """K_n contains K_5 for n >= 5, triggering the convex-cell obstruction."""

    if order < 0:
        raise ValueError("order must be nonnegative")
    return order >= 5


def map_flag_count_from_edges(n_edges: int) -> int:
    """Flags in a closed rank-3 map, inferred as 4 per edge."""

    if n_edges < 0:
        raise ValueError("n_edges must be nonnegative")
    return 4 * n_edges


def dual_pair_total_flags() -> int:
    """Combined flag count of the Csaszar/Szilassi dual pair."""

    return map_flag_count_from_edges(21) + map_flag_count_from_edges(21)


def fano_flag_stabilizer_order() -> int:
    """Orbit-stabilizer size for a Fano flag under the order-168 collineation group."""

    counts = fano_plane_counts()
    return 168 // counts["flags"]


def tomotope_flag_count_from_local_incidence() -> int:
    """Flag count from the local edge incidence of the tomotope.

    The tomotope has 12 edges. Each edge supports:

    - 2 incident vertices;
    - 4 incident triangles;
    - 2 incident cells for each incident triangle (one tetrahedron and one
      hemioctahedron).

    Therefore the number of flags through a fixed edge is 2 * 4 * 2 = 16, and
    the total number of flags is 12 * 16 = 192.
    """

    edges = 12
    vertices_per_edge = 2
    triangles_per_edge = 4
    cells_per_edge_triangle = 2
    return edges * vertices_per_edge * triangles_per_edge * cells_per_edge_triangle


def csaszar_seed() -> SurfaceNeighborlySeed:
    vertices, edges, faces = complete_graph_triangulation_counts(7)
    genus = orientable_surface_complete_graph_genus(vertices)
    if genus.denominator != 1:
        raise ValueError("Csaszar seed must have integral genus")
    return SurfaceNeighborlySeed(
        name="Csaszar",
        genus=genus.numerator,
        vertices=vertices,
        edges=edges,
        faces=faces,
        complete_vertex_adjacency=True,
        complete_face_adjacency=False,
        one_skeleton_graph="K7",
        face_adjacency_graph="Heawood graph",
        convex_cell_realization_obstructed=True,
    )


def szilassi_seed() -> SurfaceNeighborlySeed:
    vertices, edges, faces = complete_face_adjacency_surface_counts(7)
    genus = orientable_surface_complete_face_adjacency_genus(faces)
    if genus.denominator != 1:
        raise ValueError("Szilassi seed must have integral genus")
    return SurfaceNeighborlySeed(
        name="Szilassi",
        genus=genus.numerator,
        vertices=vertices,
        edges=edges,
        faces=faces,
        complete_vertex_adjacency=False,
        complete_face_adjacency=True,
        one_skeleton_graph="Heawood graph",
        face_adjacency_graph="K7",
        convex_cell_realization_obstructed=convex_cell_realization_obstructed_for_complete_graph(faces),
    )


def build_surface_neighborly_summary() -> dict[str, Any]:
    csaszar = csaszar_seed()
    szilassi = szilassi_seed()
    fano = fano_plane_counts()
    tetrahedron = tetrahedron_counts()
    csaszar_sd1 = barycentric_subdivision_f_vector((csaszar.vertices, csaszar.edges, csaszar.faces), steps=1)
    csaszar_flags = map_flag_count_from_edges(csaszar.edges)
    szilassi_flags = map_flag_count_from_edges(szilassi.edges)
    total_flags = dual_pair_total_flags()
    midpoint_total = csaszar_flags + tetrahedron["flags"] + szilassi_flags
    tomotope_flags = tomotope_flag_count_from_local_incidence()

    return {
        "status": "ok",
        "surface_genus_formulas": {
            "complete_graph_seed": "g = (n - 3)(n - 4) / 12",
            "complete_face_adjacency_seed": "g = (f - 3)(f - 4) / 12",
        },
        "seeds": [csaszar.to_dict(), szilassi.to_dict()],
        "torus_minimality": {
            "minimum_complete_graph_seed_vertices_for_genus_1": minimum_vertices_for_complete_graph_seed_genus(1),
            "minimum_complete_face_seed_faces_for_genus_1": minimum_faces_for_complete_face_adjacency_genus(1),
            "csaszar_saturates_vertex_bound": csaszar.vertices == 7,
            "szilassi_saturates_face_bound": szilassi.faces == 7,
        },
        "barycentric_subdivision": {
            "csaszar_sd1_f_vector": csaszar_sd1,
            "top_simplex_multiplier_per_step": 6,
        },
        "adjacency_graph_realizability": {
            "szilassi_face_adjacency_graph": szilassi.face_adjacency_graph,
            "arbitrary_polygon_realization_exists": True,
            "convex_polygon_realization_obstructed_by_k5": szilassi.convex_cell_realization_obstructed,
        },
        "fano_bridge": {
            "fano_plane": fano,
            "heawood_graph_edges_equal_fano_flags": szilassi.edges == fano["flags"],
            "csaszar_flag_count": csaszar_flags,
            "szilassi_flag_count": szilassi_flags,
            "flags_per_fano_flag_per_polyhedron": csaszar_flags // fano["flags"],
            "dual_pair_total_flags": total_flags,
            "dual_pair_flags_per_fano_flag": total_flags // fano["flags"],
            "fano_automorphism_group_order": 168,
            "fano_flag_stabilizer_order": fano_flag_stabilizer_order(),
            "note": (
                "The 21 Heawood edges model the 21 point-line flags of the Fano plane. "
                "Each toroidal map contributes 4 rank-3 flags per edge, so the dual pair "
                "contributes 8 local flags per Fano incidence."
            ),
        },
        "catalog_realization_counts": {
            "dmccooey_csaszar_versions": 5,
            "dmccooey_szilassi_versions": 2,
            "total_versions": 7,
            "note": "These are cataloged geometric realizations, not combinatorial invariants.",
        },
        "tetrahedral_midpoint_bridge": {
            "tetrahedron": tetrahedron,
            "midpoint_sum_flags": midpoint_total,
            "matches_tomotope_flags": midpoint_total == tomotope_flags,
            "tomotope_flag_count": tomotope_flags,
            "note": (
                "The tetrahedron is the self-dual genus-0 midpoint of the surface "
                "equations. Since the tetrahedron is regular, its flag count and "
                "full automorphism-group order are both 24."
            ),
        },
        "bridge_verdict": (
            "The Csaszar/Szilassi toroidal pair is the 2D prototype of the 4D "
            "neighborly-seed mechanism. Csaszar saturates the vertex-minimal "
            "triangulation side, Szilassi saturates the dual face-adjacency side, "
            "and barycentric subdivision turns the minimal torus seed into a real "
            "2D refinement tower."
        ),
        "bridge_to_4d_note": (
            "The surface formulas are the 2-neighborly analogue of the 4D "
            "3-neighborly CP2/K3 relation chi <= n(n^2 - 15n + 74) / 60. In both "
            "cases the key object is an extremal minimal seed whose combinatorics "
            "saturates an Euler/Dehn-Sommerville bound."
        ),
        "group_theoretic_note": (
            "The equality 84 + 84 = 168 is stronger than raw numerology because "
            "168 = 21 x 8 also comes from orbit-stabilizer on Fano flags. What is "
            "still missing is a canonical PSL(3,2) action on the disjoint union of "
            "the two toroidal flag sets."
        ),
        "cross_dimensional_note": (
            "Adding the tetrahedral midpoint gives 84 + 24 + 84 = 192, which matches "
            "the tomotope flag count derived from its local edge incidence."
        ),
        "scope_note": (
            "This is an analogue-level bridge. It does not by itself construct an "
            "explicit tomotope-to-K3 or Reye-to-Szilassi incidence map."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_surface_neighborly_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
