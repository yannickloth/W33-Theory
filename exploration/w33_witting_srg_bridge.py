"""Exact bridge from the Witting 40-ray system to SRG(40,12,2,4) and W(3,3).

This module starts from the explicit 40 Witting rays used in the March 2025
paper ``Scheme of quantum communications based on Witting polytope`` and
derives the exact finite incidence structure behind them:

- ray orthogonality gives a strongly regular graph with parameters
  ``(40, 12, 2, 4)`` and spectrum ``12^1 2^24 (-4)^15``;
- maximal orthogonal tetrads give ``40`` lines of size ``4``;
- each ray lies on ``4`` such lines;
- the off-line uniqueness axiom holds, so the incidence structure is a
  generalized quadrangle of order ``3``;
- the orthogonality graph is explicitly isomorphic to the standard symplectic
  point graph of ``W(3,3)``.

So the Witting 40-state system is not merely analogous to W(3,3): it realizes
the same exact finite geometry.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from functools import lru_cache
from itertools import combinations, product
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_witting_srg_bridge_summary.json"

Line = tuple[int, int, int, int]
ProjectivePoint = tuple[int, int, int, int]


@dataclass(frozen=True)
class StronglyRegularParameters:
    vertices: int
    edges: int
    degree: int
    lambda_parameter: int
    mu_parameter: int
    spectrum: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GeneralizedQuadrangleProfile:
    points: int
    lines: int
    line_size: int
    lines_through_point: int
    incidence_total: int
    unique_collinear_point_on_offline_line: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@lru_cache(maxsize=1)
def construct_witting_rays() -> tuple[np.ndarray, ...]:
    omega = np.exp(2j * np.pi / 3.0)
    sqrt3 = np.sqrt(3.0)
    rays: list[np.ndarray] = []

    for index in range(4):
        ray = np.zeros(4, dtype=complex)
        ray[index] = 1.0
        rays.append(ray)

    for mu, nu in product(range(3), repeat=2):
        rays.append(np.array([0, 1, -(omega**mu), omega**nu], dtype=complex) / sqrt3)
        rays.append(np.array([1, 0, -(omega**mu), -(omega**nu)], dtype=complex) / sqrt3)
        rays.append(np.array([1, -(omega**mu), 0, omega**nu], dtype=complex) / sqrt3)
        rays.append(np.array([1, omega**mu, omega**nu, 0], dtype=complex) / sqrt3)

    return tuple(rays)


def squared_overlap(left: np.ndarray, right: np.ndarray) -> float:
    return float(abs(np.vdot(left, right)) ** 2)


@lru_cache(maxsize=1)
def witting_overlap_profile() -> dict[str, float]:
    rays = construct_witting_rays()
    values = sorted(
        {
            round(squared_overlap(rays[i], rays[j]), 12)
            for i, j in combinations(range(len(rays)), 2)
        }
    )
    return {
        "orthogonal_overlap_squared": values[0],
        "nonzero_overlap_squared": values[-1],
    }


@lru_cache(maxsize=1)
def build_witting_adjacency(tol: float = 1e-8) -> tuple[frozenset[int], ...]:
    rays = construct_witting_rays()
    adjacency = [set() for _ in range(len(rays))]
    for left, right in combinations(range(len(rays)), 2):
        if abs(np.vdot(rays[left], rays[right])) < tol:
            adjacency[left].add(right)
            adjacency[right].add(left)
    return tuple(frozenset(neighbors) for neighbors in adjacency)


def adjacency_matrix(adjacency: tuple[frozenset[int], ...]) -> np.ndarray:
    size = len(adjacency)
    matrix = np.zeros((size, size), dtype=int)
    for vertex, neighbors in enumerate(adjacency):
        for neighbor in neighbors:
            matrix[vertex, neighbor] = 1
    return matrix


@lru_cache(maxsize=1)
def witting_srg_parameters() -> StronglyRegularParameters:
    adjacency = build_witting_adjacency()
    degrees = {len(neighbors) for neighbors in adjacency}
    if len(degrees) != 1:
        raise ValueError("orthogonality graph is not regular")
    degree = next(iter(degrees))

    adjacent_common = {
        len(adjacency[left] & adjacency[right])
        for left, right in combinations(range(len(adjacency)), 2)
        if right in adjacency[left]
    }
    nonadjacent_common = {
        len(adjacency[left] & adjacency[right])
        for left, right in combinations(range(len(adjacency)), 2)
        if right not in adjacency[left]
    }
    if len(adjacent_common) != 1 or len(nonadjacent_common) != 1:
        raise ValueError("orthogonality graph is not strongly regular")

    matrix = adjacency_matrix(adjacency)
    raw_eigenvalues = np.linalg.eigvalsh(matrix)
    spectrum_counts = Counter(int(round(value)) for value in raw_eigenvalues)

    return StronglyRegularParameters(
        vertices=len(adjacency),
        edges=int(matrix.sum() // 2),
        degree=degree,
        lambda_parameter=next(iter(adjacent_common)),
        mu_parameter=next(iter(nonadjacent_common)),
        spectrum={
            str(eigenvalue): multiplicity
            for eigenvalue, multiplicity in sorted(spectrum_counts.items(), reverse=True)
        },
    )


@lru_cache(maxsize=1)
def witting_orthogonal_tetrads() -> tuple[Line, ...]:
    adjacency = build_witting_adjacency()
    lines: set[Line] = set()
    for left, neighbors in enumerate(adjacency):
        for right in neighbors:
            if left >= right:
                continue
            common = sorted(adjacency[left] & adjacency[right])
            if len(common) != 2:
                raise ValueError("adjacent pair does not determine a unique tetrad")
            line = tuple(sorted((left, right, common[0], common[1])))
            lines.add(line)
    return tuple(sorted(lines))


@lru_cache(maxsize=1)
def witting_generalized_quadrangle_profile() -> GeneralizedQuadrangleProfile:
    adjacency = build_witting_adjacency()
    lines = witting_orthogonal_tetrads()
    line_sizes = {len(line) for line in lines}
    if line_sizes != {4}:
        raise ValueError("Witting lines are not 4-point tetrads")

    point_line_counts = [0] * len(adjacency)
    for line in lines:
        for point in line:
            point_line_counts[point] += 1
    line_incidence = set(point_line_counts)
    if len(line_incidence) != 1:
        raise ValueError("points do not lie on a uniform number of lines")

    unique_offline = True
    for point in range(len(adjacency)):
        for line in lines:
            if point in line:
                continue
            hits = sum(1 for line_point in line if line_point in adjacency[point])
            if hits != 1:
                unique_offline = False
                break
        if not unique_offline:
            break

    return GeneralizedQuadrangleProfile(
        points=len(adjacency),
        lines=len(lines),
        line_size=4,
        lines_through_point=next(iter(line_incidence)),
        incidence_total=sum(point_line_counts),
        unique_collinear_point_on_offline_line=unique_offline,
    )


def symplectic_form(left: ProjectivePoint, right: ProjectivePoint) -> int:
    return (
        left[0] * right[2]
        - left[2] * right[0]
        + left[1] * right[3]
        - left[3] * right[1]
    ) % 3


@lru_cache(maxsize=1)
def construct_symplectic_points() -> tuple[ProjectivePoint, ...]:
    points: list[ProjectivePoint] = []
    seen: set[ProjectivePoint] = set()
    for vector in product(range(3), repeat=4):
        if not any(vector):
            continue
        normalized = list(vector)
        for entry in normalized:
            if entry != 0:
                inverse = 1 if entry == 1 else 2
                projective = tuple((inverse * value) % 3 for value in normalized)
                break
        if projective not in seen:
            seen.add(projective)
            points.append(projective)
    return tuple(points)


@lru_cache(maxsize=1)
def build_symplectic_adjacency() -> tuple[frozenset[int], ...]:
    points = construct_symplectic_points()
    adjacency = [set() for _ in range(len(points))]
    for left, right in combinations(range(len(points)), 2):
        if symplectic_form(points[left], points[right]) == 0:
            adjacency[left].add(right)
            adjacency[right].add(left)
    return tuple(frozenset(neighbors) for neighbors in adjacency)


def _is_compatible(
    left_vertex: int,
    right_vertex: int,
    mapping: dict[int, int],
    left_adjacency: tuple[frozenset[int], ...],
    right_adjacency: tuple[frozenset[int], ...],
) -> bool:
    for old_left, old_right in mapping.items():
        if (old_left in left_adjacency[left_vertex]) != (
            old_right in right_adjacency[right_vertex]
        ):
            return False
    return True


def _backtrack_isomorphism(
    order: tuple[int, ...],
    candidates: dict[int, set[int]],
    mapping: dict[int, int],
    used: set[int],
    left_adjacency: tuple[frozenset[int], ...],
    right_adjacency: tuple[frozenset[int], ...],
) -> dict[int, int] | None:
    if len(mapping) == len(order):
        return dict(mapping)

    left_vertex = min(
        (vertex for vertex in order if vertex not in mapping),
        key=lambda vertex: len(candidates[vertex]),
    )

    for right_vertex in list(candidates[left_vertex]):
        if right_vertex in used:
            continue
        if not _is_compatible(
            left_vertex,
            right_vertex,
            mapping,
            left_adjacency,
            right_adjacency,
        ):
            continue

        mapping[left_vertex] = right_vertex
        used.add(right_vertex)
        updated: list[tuple[int, set[int]]] = []
        failed = False

        for other_left in order:
            if other_left in mapping:
                continue
            new_candidates = {
                other_right
                for other_right in candidates[other_left]
                if other_right not in used
                and ((other_left in left_adjacency[left_vertex]) == (
                    other_right in right_adjacency[right_vertex]
                ))
            }
            if not new_candidates:
                failed = True
                break
            if new_candidates != candidates[other_left]:
                updated.append((other_left, candidates[other_left]))
                candidates[other_left] = new_candidates

        if not failed:
            result = _backtrack_isomorphism(
                order,
                candidates,
                mapping,
                used,
                left_adjacency,
                right_adjacency,
            )
            if result is not None:
                return result

        for other_left, old_candidates in updated:
            candidates[other_left] = old_candidates
        used.remove(right_vertex)
        del mapping[left_vertex]

    return None


@lru_cache(maxsize=1)
def witting_to_symplectic_isomorphism() -> dict[int, int]:
    left_adjacency = build_witting_adjacency()
    right_adjacency = build_symplectic_adjacency()
    order = tuple(range(len(left_adjacency)))
    candidates = {vertex: set(range(len(right_adjacency))) for vertex in order}
    mapping = {0: 0}
    used = {0}

    for vertex in order[1:]:
        candidates[vertex] = {
            candidate
            for candidate in candidates[vertex]
            if ((vertex in left_adjacency[0]) == (candidate in right_adjacency[0]))
        }

    result = _backtrack_isomorphism(
        order,
        candidates,
        mapping,
        used,
        left_adjacency,
        right_adjacency,
    )
    if result is None:
        raise ValueError("failed to find Witting/W(3,3) isomorphism")
    return result


def mapped_witting_lines() -> tuple[Line, ...]:
    mapping = witting_to_symplectic_isomorphism()
    return tuple(
        sorted(tuple(sorted(mapping[point] for point in line)) for line in witting_orthogonal_tetrads())
    )


def symplectic_lines() -> tuple[Line, ...]:
    adjacency = build_symplectic_adjacency()
    lines: set[Line] = set()
    for left, neighbors in enumerate(adjacency):
        for right in neighbors:
            if left >= right:
                continue
            common = sorted(adjacency[left] & adjacency[right])
            if len(common) != 2:
                raise ValueError("symplectic adjacency does not define unique lines")
            lines.add(tuple(sorted((left, right, common[0], common[1]))))
    return tuple(sorted(lines))


def build_witting_srg_bridge_summary() -> dict[str, Any]:
    srg = witting_srg_parameters()
    gq = witting_generalized_quadrangle_profile()
    overlap = witting_overlap_profile()
    mapping = witting_to_symplectic_isomorphism()
    mapped_lines = mapped_witting_lines()
    symp_lines = symplectic_lines()

    return {
        "status": "ok",
        "paper_system": {
            "witting_rays": len(construct_witting_rays()),
            "orthogonal_tetrads": len(witting_orthogonal_tetrads()),
            "states_per_tetrad": gq.line_size,
            "tetrads_through_each_state": gq.lines_through_point,
        },
        "overlap_profile": overlap,
        "orthogonality_graph": srg.to_dict(),
        "generalized_quadrangle": gq.to_dict(),
        "symplectic_model": {
            "projective_points": len(construct_symplectic_points()),
            "graph_isomorphic_to_standard_w33": True,
            "mapped_lines_equal_symplectic_lines": mapped_lines == symp_lines,
        },
        "explicit_isomorphism": {str(left): right for left, right in sorted(mapping.items())},
        "bridge_verdict": (
            "The 40 Witting rays and their 40 maximal orthogonal tetrads form an exact "
            "generalized quadrangle of order 3. Equivalently, the Witting ray-"
            "orthogonality graph is the strongly regular graph SRG(40,12,2,4), and "
            "it is explicitly isomorphic to the standard symplectic point graph of "
            "W(3,3)."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_witting_srg_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
