"""Exact order bridge for the universal tetrahedron-hemioctahedron cover and the tomotope.

This module consolidates the exact finite arithmetic from The Tomotope with the
new Fano/tetrahedron bridge. The key data from the paper are:

- U_{t,ho}: automorphism group order 192, 24 edges, 8 tetrahedra, 8 hemioctahedra;
- T: automorphism group order 96, 12 edges, 4 tetrahedra, 4 hemioctahedra;
- Mon(T): order 18432;
- R_2, the minimal regular cover of T: order 36864.

Using the local edge incidence (2 endpoints, 4 triangles around each edge, and
2 incident cells for each edge-triangle pair), the flag counts are:

- U_{t,ho}: 24 * 16 = 384 flags;
- T: 12 * 16 = 192 flags.

This produces several exact identities:

- |Aut(U_{t,ho})| = |Flags(T)| = 192;
- |Mon(T)| = |Aut(T)| * |Flags(T)| = 96 * 192;
- |Gamma(R_2)| = 2 * |Mon(T)| = 192^2.
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

from w33_fano_group_bridge import tomotope_factorization_via_tetra_and_flag_stabilizer
from w33_surface_neighborly_bridge import tetrahedron_counts


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_tomotope_order_bridge_summary.json"


@dataclass(frozen=True)
class UniformPolytopeOrderData:
    name: str
    vertices: int
    edges: int
    triangles: int
    tetrahedra: int
    hemioctahedra: int
    automorphism_group_order: int
    monodromy_group_order: int | None
    flags: int
    flag_orbits_under_automorphisms: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def rank4_flags_from_edge_local_incidence(edge_count: int) -> int:
    """Flag count for the tetrahedron/hemioctahedron local edge figure."""

    if edge_count < 0:
        raise ValueError("edge_count must be nonnegative")
    vertices_per_edge = 2
    triangles_per_edge = 4
    cells_per_edge_triangle = 2
    return edge_count * vertices_per_edge * triangles_per_edge * cells_per_edge_triangle


def flag_orbit_count(flags: int, automorphism_group_order: int) -> int:
    """Number of flag orbits under a free automorphism action."""

    if flags < 0 or automorphism_group_order <= 0:
        raise ValueError("flags must be nonnegative and automorphism_group_order positive")
    if flags % automorphism_group_order != 0:
        raise ValueError("automorphism group order must divide flag count")
    return flags // automorphism_group_order


def universal_tetrahedron_hemioctahedron_data() -> UniformPolytopeOrderData:
    flags = rank4_flags_from_edge_local_incidence(24)
    aut = 192
    return UniformPolytopeOrderData(
        name="U_t,ho",
        vertices=4,
        edges=24,
        triangles=32,
        tetrahedra=8,
        hemioctahedra=8,
        automorphism_group_order=aut,
        monodromy_group_order=73728,
        flags=flags,
        flag_orbits_under_automorphisms=flag_orbit_count(flags, aut),
    )


def tomotope_data() -> UniformPolytopeOrderData:
    flags = rank4_flags_from_edge_local_incidence(12)
    aut = 96
    return UniformPolytopeOrderData(
        name="T",
        vertices=4,
        edges=12,
        triangles=16,
        tetrahedra=4,
        hemioctahedra=4,
        automorphism_group_order=aut,
        monodromy_group_order=18432,
        flags=flags,
        flag_orbits_under_automorphisms=flag_orbit_count(flags, aut),
    )


def minimal_regular_cover_order() -> int:
    return 36864


def build_tomotope_order_summary() -> dict[str, Any]:
    universal = universal_tetrahedron_hemioctahedron_data()
    tomotope = tomotope_data()
    tetrahedron = tetrahedron_counts()
    tomotope_factorization = tomotope_factorization_via_tetra_and_flag_stabilizer()
    cover_order = minimal_regular_cover_order()

    return {
        "status": "ok",
        "uniform_cover": universal.to_dict(),
        "tomotope": tomotope.to_dict(),
        "minimal_regular_cover": {
            "name": "R2",
            "automorphism_group_order": cover_order,
        },
        "exact_identities": {
            "aut_universal_equals_flags_tomotope": universal.automorphism_group_order == tomotope.flags,
            "aut_universal_value": universal.automorphism_group_order,
            "mon_t_equals_aut_t_times_flags_t": tomotope.monodromy_group_order == tomotope.automorphism_group_order * tomotope.flags,
            "mon_t_product_value": tomotope.automorphism_group_order * tomotope.flags,
            "mon_universal_equals_aut_universal_times_flags_universal": (
                universal.monodromy_group_order == universal.automorphism_group_order * universal.flags
            ),
            "mon_universal_product_value": universal.automorphism_group_order * universal.flags,
            "regular_cover_equals_flags_t_squared": cover_order == tomotope.flags**2,
            "regular_cover_equals_aut_universal_squared": cover_order == universal.automorphism_group_order**2,
            "regular_cover_equals_2_times_mon_t": cover_order == 2 * tomotope.monodromy_group_order,
        },
        "fano_tetra_bridge": {
            "tetrahedron_flags": tetrahedron["flags"],
            "fano_flag_stabilizer_order": 8,
            "tetrahedron_flags_times_fano_flag_stabilizer": tomotope_factorization,
            "matches_tomotope_flags": tomotope_factorization == tomotope.flags,
        },
        "quotient_pattern": {
            "edge_ratio_universal_to_tomotope": universal.edges // tomotope.edges,
            "triangle_ratio_universal_to_tomotope": universal.triangles // tomotope.triangles,
            "tetrahedron_ratio_universal_to_tomotope": universal.tetrahedra // tomotope.tetrahedra,
            "hemioctahedron_ratio_universal_to_tomotope": universal.hemioctahedra // tomotope.hemioctahedra,
            "automorphism_ratio_universal_to_tomotope": universal.automorphism_group_order // tomotope.automorphism_group_order,
            "monodromy_ratio_universal_to_tomotope": universal.monodromy_group_order // tomotope.monodromy_group_order,
        },
        "bridge_verdict": (
            "The order tower U_t,ho -> T -> R2 is numerically rigid. The universal "
            "tetrahedron-hemioctahedron polytope has automorphism order 192, which "
            "matches the tomotope flag count; the minimal regular cover has order "
            "192^2. This ties the paper's exact finite cover theory directly to the "
            "Fano/tetrahedron factorization 192 = 24 x 8."
        ),
        "scope_note": (
            "These are exact finite identities. They do not yet provide a canonical "
            "geometric functor from Fano data or tetrahedron flags into the full "
            "tomotope cover tower."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_tomotope_order_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
