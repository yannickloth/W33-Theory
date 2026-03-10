"""Group-theoretic bridge from the Fano plane to tetrahedron and tomotope counts.

This module upgrades the earlier count-level observations into an explicit model
using the collineation group of the Fano plane. Over F_2 one has

    PSL(3,2) = PGL(3,2) = GL(3,2),

so the full collineation group has order 168. The main exact bridge points are:

- Fano plane: 7 points, 7 lines, 21 flags;
- point stabilizer: order 24, canonically inducing S4 on the 4 lines not through
  the fixed point;
- flag stabilizer: order 8;
- dual toroidal pair: 84 + 84 = 168 flags;
- tomotope: 192 = 24 x 8 flags.

The tetrahedral midpoint is no longer only an additive count: it arises
canonically as the point stabilizer acting on a 4-element set.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
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

from w33_surface_neighborly_bridge import (
    dual_pair_total_flags,
    fano_flag_stabilizer_order as surface_fano_flag_stabilizer_order,
    fano_plane_counts as surface_fano_plane_counts,
    tetrahedron_counts,
    tomotope_flag_count_from_local_incidence,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_fano_group_bridge_summary.json"

Vector = tuple[int, int, int]
Matrix = tuple[Vector, Vector, Vector]
Permutation = tuple[int, ...]


@dataclass(frozen=True)
class FanoGroupSummary:
    group_order: int
    points: int
    lines: int
    flags: int
    point_stabilizer_order: int
    line_stabilizer_order: int
    flag_stabilizer_order: int
    tetrahedral_permutation_group_order: int
    tetrahedron_flag_count: int
    toroidal_dual_pair_flag_count: int
    tomotope_flag_count: int
    tomotope_factorization_via_tetra_and_flag_stabilizer: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def xor_vectors(left: Vector, right: Vector) -> Vector:
    return (left[0] ^ right[0], left[1] ^ right[1], left[2] ^ right[2])


def mat_vec_mul(matrix: Matrix, vector: Vector) -> Vector:
    return tuple(
        (matrix[row][0] & vector[0]) ^ (matrix[row][1] & vector[1]) ^ (matrix[row][2] & vector[2])
        for row in range(3)
    )


def determinant_mod2(matrix: Matrix) -> int:
    a00, a01, a02 = matrix[0]
    a10, a11, a12 = matrix[1]
    a20, a21, a22 = matrix[2]
    return (
        (a00 & ((a11 & a22) ^ (a12 & a21)))
        ^ (a01 & ((a10 & a22) ^ (a12 & a20)))
        ^ (a02 & ((a10 & a21) ^ (a11 & a20)))
    ) & 1


@lru_cache(maxsize=1)
def nonzero_vectors() -> tuple[Vector, ...]:
    return tuple(
        (x0, x1, x2)
        for x0, x1, x2 in itertools.product((0, 1), repeat=3)
        if (x0, x1, x2) != (0, 0, 0)
    )


@lru_cache(maxsize=1)
def gl32_group() -> tuple[Matrix, ...]:
    matrices = []
    for rows in itertools.product(nonzero_vectors() + ((0, 0, 0),), repeat=3):
        matrix = rows
        if determinant_mod2(matrix) == 1:
            matrices.append(matrix)
    return tuple(matrices)


@lru_cache(maxsize=1)
def fano_points() -> tuple[Vector, ...]:
    return nonzero_vectors()


@lru_cache(maxsize=1)
def fano_lines() -> tuple[tuple[Vector, Vector, Vector], ...]:
    lines = set()
    points = fano_points()
    for i, point_a in enumerate(points):
        for point_b in points[i + 1 :]:
            if point_a == point_b:
                continue
            point_c = xor_vectors(point_a, point_b)
            line = tuple(sorted((point_a, point_b, point_c)))
            lines.add(line)
    return tuple(sorted(lines))


@lru_cache(maxsize=1)
def fano_flags() -> tuple[tuple[Vector, tuple[Vector, Vector, Vector]], ...]:
    return tuple(
        (point, line)
        for line in fano_lines()
        for point in line
    )


def apply_matrix_to_line(matrix: Matrix, line: tuple[Vector, Vector, Vector]) -> tuple[Vector, Vector, Vector]:
    return tuple(sorted(mat_vec_mul(matrix, point) for point in line))


def point_stabilizer(point: Vector) -> tuple[Matrix, ...]:
    return tuple(matrix for matrix in gl32_group() if mat_vec_mul(matrix, point) == point)


def line_stabilizer(line: tuple[Vector, Vector, Vector]) -> tuple[Matrix, ...]:
    return tuple(matrix for matrix in gl32_group() if apply_matrix_to_line(matrix, line) == line)


def flag_stabilizer(point: Vector, line: tuple[Vector, Vector, Vector]) -> tuple[Matrix, ...]:
    return tuple(matrix for matrix in point_stabilizer(point) if apply_matrix_to_line(matrix, line) == line)


def off_line_points(line: tuple[Vector, Vector, Vector]) -> tuple[Vector, ...]:
    return tuple(point for point in fano_points() if point not in line)


def lines_not_through(point: Vector) -> tuple[tuple[Vector, Vector, Vector], ...]:
    return tuple(line for line in fano_lines() if point not in line)


def induced_tetrahedral_permutations(point: Vector) -> tuple[Permutation, ...]:
    ambient_lines = lines_not_through(point)
    index = {line: i for i, line in enumerate(ambient_lines)}
    perms = set()
    for matrix in point_stabilizer(point):
        perm = tuple(index[apply_matrix_to_line(matrix, line)] for line in ambient_lines)
        perms.add(perm)
    return tuple(sorted(perms))


def symmetric_group_order_on_four_letters() -> int:
    return 24


def tetrahedral_action_is_full_s4(point: Vector) -> bool:
    return len(induced_tetrahedral_permutations(point)) == symmetric_group_order_on_four_letters()


def compose_permutations(left: Permutation, right: Permutation) -> Permutation:
    return tuple(left[index] for index in right)


def dihedral_square_permutations() -> tuple[Permutation, ...]:
    """D8 on a labeled square with vertices 0,1,2,3."""

    rotation = (2, 3, 1, 0)
    reflection = (1, 0, 2, 3)
    identity = (0, 1, 2, 3)
    seen = {identity}
    frontier = [identity]
    generators = (rotation, reflection)
    while frontier:
        current = frontier.pop()
        for generator in generators:
            candidate = compose_permutations(generator, current)
            if candidate not in seen:
                seen.add(candidate)
                frontier.append(candidate)
    return tuple(sorted(seen))


def flag_stabilizer_off_line_point_permutations(
    point: Vector,
    line: tuple[Vector, Vector, Vector],
) -> tuple[Permutation, ...]:
    points = off_line_points(line)
    index = {candidate: i for i, candidate in enumerate(points)}
    perms = set()
    for matrix in flag_stabilizer(point, line):
        perm = tuple(index[mat_vec_mul(matrix, candidate)] for candidate in points)
        perms.add(perm)
    return tuple(sorted(perms))


def flag_stabilizer_is_dihedral_square(point: Vector, line: tuple[Vector, Vector, Vector]) -> bool:
    return flag_stabilizer_off_line_point_permutations(point, line) == dihedral_square_permutations()


def tomotope_factorization_via_tetra_and_flag_stabilizer() -> int:
    return tetrahedron_counts()["flags"] * len(flag_stabilizer(*fano_flags()[0]))


def build_fano_group_summary() -> dict[str, Any]:
    point = fano_points()[0]
    line = next(line for line in fano_lines() if point in line)
    tetrahedron = tetrahedron_counts()
    summary = FanoGroupSummary(
        group_order=len(gl32_group()),
        points=len(fano_points()),
        lines=len(fano_lines()),
        flags=len(fano_flags()),
        point_stabilizer_order=len(point_stabilizer(point)),
        line_stabilizer_order=len(line_stabilizer(line)),
        flag_stabilizer_order=len(flag_stabilizer(point, line)),
        tetrahedral_permutation_group_order=len(induced_tetrahedral_permutations(point)),
        tetrahedron_flag_count=tetrahedron["flags"],
        toroidal_dual_pair_flag_count=dual_pair_total_flags(),
        tomotope_flag_count=tomotope_flag_count_from_local_incidence(),
        tomotope_factorization_via_tetra_and_flag_stabilizer=tomotope_factorization_via_tetra_and_flag_stabilizer(),
    )
    return {
        "status": "ok",
        "summary": summary.to_dict(),
        "fano_consistency_checks": {
            "surface_module_points_lines_flags_match": surface_fano_plane_counts() == {
                "points": summary.points,
                "lines": summary.lines,
                "incidences_per_point": 3,
                "incidences_per_line": 3,
                "flags": summary.flags,
            },
            "surface_module_flag_stabilizer_matches": surface_fano_flag_stabilizer_order() == summary.flag_stabilizer_order,
        },
        "tetrahedral_bridge": {
            "chosen_point": point,
            "lines_not_through_point": lines_not_through(point),
            "point_stabilizer_induces_full_s4": tetrahedral_action_is_full_s4(point),
            "note": (
                "Fixing a Fano point leaves four lines not through that point. "
                "The point stabilizer of order 24 acts on those four lines as the full "
                "symmetric group S4, giving a canonical tetrahedral action."
            ),
        },
        "local_square_bridge": {
            "chosen_flag": {
                "point": point,
                "line": line,
            },
            "off_line_point_count": len(off_line_points(line)),
            "flag_stabilizer_off_line_point_permutations": flag_stabilizer_off_line_point_permutations(point, line),
            "flag_stabilizer_is_dihedral_square": flag_stabilizer_is_dihedral_square(point, line),
            "dihedral_square_group_order": len(dihedral_square_permutations()),
            "tomotope_triangles_around_each_edge": 4,
            "note": (
                "Fixing a Fano flag leaves 4 points off the chosen line. The flag "
                "stabilizer of order 8 acts on those 4 points as D8, the symmetry "
                "group of a square. This matches the tomotope's 4 triangles around "
                "each edge."
            ),
        },
        "toroidal_bridge": {
            "dual_pair_total_flags": dual_pair_total_flags(),
            "matches_fano_group_order": dual_pair_total_flags() == len(gl32_group()),
            "note": (
                "The combined flag count of the Csaszar/Szilassi dual pair equals "
                "the order of the Fano collineation group."
            ),
        },
        "tomotope_bridge": {
            "tetrahedron_flags_times_fano_flag_stabilizer": tomotope_factorization_via_tetra_and_flag_stabilizer(),
            "matches_tomotope_flags": tomotope_factorization_via_tetra_and_flag_stabilizer() == tomotope_flag_count_from_local_incidence(),
            "note": (
                "The tomotope flag count factors as 192 = 24 x 8, where 24 is the "
                "tetrahedron flag count and 8 is the D8 order of the Fano flag "
                "stabilizer."
            ),
        },
        "bridge_verdict": (
            "The tetrahedral midpoint is canonical at the group level: it is the "
            "stabilizer of a Fano point, while the local order-8 factor is the "
            "square group D8 coming from a Fano flag. This upgrades the earlier "
            "count pattern from raw arithmetic to an explicit Fano-group mechanism."
        ),
        "scope_note": (
            "This still does not produce an explicit bijection from tomotope flags "
            "to tetrahedron flags times a chosen Fano flag stabilizer. The current "
            "result is a verified factorization and group-action model."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_fano_group_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
