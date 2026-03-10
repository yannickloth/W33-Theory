"""Realization-level orbit structure for the cataloged Csaszar and Szilassi models.

This module analyzes the seven cataloged Euclidean realizations listed in the
archived ``Cs and Sz Realizations.pdf`` sheet:

- 5 realizations of the Csaszar polyhedron;
- 2 realizations of the Szilassi polyhedron.

The important outcome is not the raw count ``5 + 2 = 7`` by itself. The exact
shared structure is that every one of the seven realizations carries the same
half-turn symmetry

    (x, y, z) -> (-x, -y, z),

and the induced orbit data is dual:

- Csaszar realizations: 4 vertex orbits and 7 face orbits;
- Szilassi realizations: 7 vertex orbits and 4 face orbits.

So the realization layer is governed by a common Z2 involution whose orbit
package already mirrors the combinatorial Csaszar/Szilassi duality.
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


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_realization_orbit_bridge_summary.json"

Point = tuple[float, float, float]
Face = tuple[int, ...]


CSASZAR_FACES: tuple[Face, ...] = (
    (0, 1, 2),
    (0, 2, 5),
    (0, 5, 4),
    (0, 4, 6),
    (0, 6, 3),
    (0, 3, 1),
    (1, 3, 4),
    (1, 4, 5),
    (1, 5, 6),
    (1, 6, 2),
    (2, 6, 4),
    (2, 4, 3),
    (2, 3, 5),
    (5, 3, 6),
)


SZILASSI_FACES: tuple[Face, ...] = (
    (0, 1, 13, 8, 7, 4),
    (0, 4, 3, 2, 10, 12),
    (0, 12, 9, 6, 5, 1),
    (11, 3, 4, 7, 6, 9),
    (11, 9, 12, 10, 8, 13),
    (11, 13, 1, 5, 2, 3),
    (2, 5, 6, 7, 8, 10),
)


CSASZAR_REALIZATIONS: dict[str, tuple[Point, ...]] = {
    "Csaszar1": (
        (3.0, -3.0, -7.5),
        (-3.0, 3.0, -7.5),
        (3.0, 3.0, -6.5),
        (-3.0, -3.0, -6.5),
        (1.0, 2.0, -4.5),
        (-1.0, -2.0, -4.5),
        (0.0, 0.0, 7.5),
    ),
    "Csaszar2": (
        (15.491933384829667, 0.0, -10.0),
        (-15.491933384829667, 0.0, -10.0),
        (0.0, 8.0, -6.0),
        (0.0, -8.0, -6.0),
        (-1.0, 2.0, 1.0),
        (1.0, -2.0, 1.0),
        (0.0, 0.0, 10.0),
    ),
    "Csaszar3": (
        (12.0, 0.0, -8.48528137423857),
        (-12.0, 0.0, -8.48528137423857),
        (0.0, 8.48528137423857, 0.0),
        (0.0, -8.48528137423857, 0.0),
        (3.0, -3.0, -3.0),
        (-3.0, 3.0, -3.0),
        (0.0, 0.0, 8.48528137423857),
    ),
    "Csaszar4": (
        (12.0, 0.0, -8.48528137423857),
        (-12.0, 0.0, -8.48528137423857),
        (0.0, 12.0, 8.48528137423857),
        (0.0, -12.0, 8.48528137423857),
        (-4.0, -3.0, 0.7071067811865476),
        (4.0, 3.0, 0.7071067811865476),
        (0.0, 0.0, 3.7712361663282534),
    ),
    "Csaszar5": (
        (12.0, 0.0, -8.48528137423857),
        (-12.0, 0.0, -8.48528137423857),
        (0.0, 12.0, 8.48528137423857),
        (0.0, -12.0, 8.48528137423857),
        (-3.0, 3.0, 2.8284271247461903),
        (3.0, -3.0, 2.8284271247461903),
        (0.0, 0.0, -2.8284271247461903),
    ),
}


SZILASSI_REALIZATIONS: dict[str, tuple[Point, ...]] = {
    "Szilassi1": (
        (12.0, 0.0, 12.0),
        (-12.0, 0.0, 12.0),
        (0.0, 12.6, -12.0),
        (0.0, -12.6, -12.0),
        (2.0, -5.0, -8.0),
        (-2.0, 5.0, -8.0),
        (3.75, 3.75, -3.0),
        (-3.75, -3.75, -3.0),
        (4.5, -2.5, 2.0),
        (-4.5, 2.5, 2.0),
        (7.0, 0.0, 2.0),
        (-7.0, 0.0, 2.0),
        (7.0, 2.5, 2.0),
        (-7.0, -2.5, 2.0),
    ),
    "Szilassi2": (
        (12.0, 0.0, 12.0),
        (-12.0, 0.0, 12.0),
        (0.0, 12.0, -12.0),
        (0.0, -12.0, -12.0),
        (1.5, -5.25, -9.0),
        (-1.5, 5.25, -9.0),
        (8.0 / 3.0, 4.0, -4.0),
        (-8.0 / 3.0, -4.0, -4.0),
        (20.0 / 3.0, -2.0, 4.0),
        (-20.0 / 3.0, 2.0, 4.0),
        (8.0, 0.0, 4.0),
        (-8.0, 0.0, 4.0),
        (8.0, 2.0, 4.0),
        (-8.0, -2.0, 4.0),
    ),
}


@dataclass(frozen=True)
class RealizationOrbitSummary:
    realization_count: int
    half_turn_symmetry_present_in_all: bool
    vertex_orbit_count: int
    face_orbit_count: int
    fixed_vertex_count: int
    fixed_face_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def half_turn(point: Point) -> Point:
    return (-point[0], -point[1], point[2])


def point_close(left: Point, right: Point, tol: float = 1e-9) -> bool:
    return all(abs(a - b) <= tol for a, b in zip(left, right))


def half_turn_vertex_permutation(points: tuple[Point, ...]) -> tuple[int, ...]:
    permutation = []
    for point in points:
        image = half_turn(point)
        matches = [index for index, candidate in enumerate(points) if point_close(candidate, image)]
        if len(matches) != 1:
            raise ValueError("half-turn image did not match exactly one vertex")
        permutation.append(matches[0])
    return tuple(permutation)


def orbit_decomposition(permutation: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    seen: set[int] = set()
    orbits = []
    for index in range(len(permutation)):
        if index in seen:
            continue
        orbit = tuple(sorted({index, permutation[index]}))
        seen.update(orbit)
        orbits.append(orbit)
    return tuple(orbits)


def face_permutation(permutation: tuple[int, ...], faces: tuple[Face, ...]) -> tuple[int, ...]:
    lookup = {tuple(sorted(face)): index for index, face in enumerate(faces)}
    image = []
    for face in faces:
        moved = tuple(sorted(permutation[vertex] for vertex in face))
        image.append(lookup[moved])
    return tuple(image)


def family_summary(
    realizations: dict[str, tuple[Point, ...]],
    faces: tuple[Face, ...],
) -> dict[str, Any]:
    details = {}
    vertex_orbits_reference: tuple[tuple[int, ...], ...] | None = None
    face_orbits_reference: tuple[tuple[int, ...], ...] | None = None

    for name, points in realizations.items():
        vertex_perm = half_turn_vertex_permutation(points)
        face_perm = face_permutation(vertex_perm, faces)
        vertex_orbits = orbit_decomposition(vertex_perm)
        face_orbits = orbit_decomposition(face_perm)
        details[name] = {
            "vertex_half_turn_permutation": vertex_perm,
            "vertex_orbits": vertex_orbits,
            "face_half_turn_permutation": face_perm,
            "face_orbits": face_orbits,
            "fixed_vertices": [orbit[0] for orbit in vertex_orbits if len(orbit) == 1],
            "fixed_faces": [orbit[0] for orbit in face_orbits if len(orbit) == 1],
        }
        if vertex_orbits_reference is None:
            vertex_orbits_reference = vertex_orbits
            face_orbits_reference = face_orbits
        elif vertex_orbits != vertex_orbits_reference or face_orbits != face_orbits_reference:
            raise ValueError("family does not share a uniform half-turn orbit structure")

    assert vertex_orbits_reference is not None
    assert face_orbits_reference is not None

    summary = RealizationOrbitSummary(
        realization_count=len(realizations),
        half_turn_symmetry_present_in_all=True,
        vertex_orbit_count=len(vertex_orbits_reference),
        face_orbit_count=len(face_orbits_reference),
        fixed_vertex_count=sum(1 for orbit in vertex_orbits_reference if len(orbit) == 1),
        fixed_face_count=sum(1 for orbit in face_orbits_reference if len(orbit) == 1),
    )
    return {
        "summary": summary.to_dict(),
        "details": details,
    }


def build_realization_orbit_summary() -> dict[str, Any]:
    cs = family_summary(CSASZAR_REALIZATIONS, CSASZAR_FACES)
    sz = family_summary(SZILASSI_REALIZATIONS, SZILASSI_FACES)
    return {
        "status": "ok",
        "catalog_counts": {
            "csaszar_realizations": len(CSASZAR_REALIZATIONS),
            "szilassi_realizations": len(SZILASSI_REALIZATIONS),
            "total": len(CSASZAR_REALIZATIONS) + len(SZILASSI_REALIZATIONS),
        },
        "common_symmetry": {
            "map": "(x, y, z) -> (-x, -y, z)",
            "group": "Z2",
            "present_in_all_cataloged_realizations": True,
        },
        "csaszar_family": cs,
        "szilassi_family": sz,
        "dual_orbit_package": {
            "csaszar_vertex_orbits": cs["summary"]["vertex_orbit_count"],
            "csaszar_face_orbits": cs["summary"]["face_orbit_count"],
            "szilassi_vertex_orbits": sz["summary"]["vertex_orbit_count"],
            "szilassi_face_orbits": sz["summary"]["face_orbit_count"],
            "is_dual_swap": (
                cs["summary"]["vertex_orbit_count"] == sz["summary"]["face_orbit_count"]
                and cs["summary"]["face_orbit_count"] == sz["summary"]["vertex_orbit_count"]
            ),
        },
        "bridge_verdict": (
            "The seven cataloged realizations do not currently behave like a verified "
            "7-element algebra. The exact common structure is stronger and simpler: "
            "all seven carry the same half-turn symmetry, and the induced orbit counts "
            "are dual, with Csaszar realizing (4 vertex orbits, 7 face orbits) and "
            "Szilassi realizing (7 vertex orbits, 4 face orbits)."
        ),
        "scope_note": (
            "This is a realization-level symmetry statement. It does not yet classify "
            "the catalog entries up to affine, projective, or isotopic equivalence, "
            "and it does not prove that the catalog count 7 itself is canonical."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_realization_orbit_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
