"""Explicit simplicial 4D bridge seeds: CP2_9 and K3_16.

This module upgrades the external 4D bridge from abstract f-vectors to actual
finite simplicial complexes.

- ``CP2_9`` is reconstructed from Kühnel's 9-vertex orbit description.
- ``K3_16`` is reconstructed from the Casella-Kühnel / Sage permutation-orbit
  construction with two seed facets and a 240-element permutation group.

From these explicit facets we compute:

- full f-vectors;
- boundary ranks;
- Betti numbers;
- total harmonic-form counts.

This is the first point in the bridge program where the curved external factor
is an actual chain complex with executable Hodge data rather than only a
topological placeholder.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from functools import lru_cache
from itertools import combinations
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


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_explicit_curved_4d_complexes_summary.json"

Simplex = tuple[int, ...]
Permutation = tuple[int, ...]


@dataclass(frozen=True)
class ExplicitComplexProfile:
    name: str
    vertices: int
    facets: int
    f_vector: tuple[int, int, int, int, int]
    boundary_ranks: tuple[int, int, int, int]
    betti_numbers: tuple[int, int, int, int, int]
    harmonic_form_total: int
    euler_characteristic: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def permutation_from_cycles(size: int, cycles: tuple[tuple[int, ...], ...]) -> Permutation:
    permutation = list(range(size + 1))
    for cycle in cycles:
        cycle_length = len(cycle)
        for index, value in enumerate(cycle):
            permutation[value] = cycle[(index + 1) % cycle_length]
    return tuple(permutation)


def compose_permutations(left: Permutation, right: Permutation) -> Permutation:
    size = len(left) - 1
    return tuple([0] + [left[right[index]] for index in range(1, size + 1)])


def permutation_closure(generators: tuple[Permutation, ...], size: int) -> tuple[Permutation, ...]:
    identity = tuple(range(size + 1))
    seen = {identity}
    queue: deque[Permutation] = deque([identity])
    while queue:
        current = queue.popleft()
        for generator in generators:
            image = compose_permutations(current, generator)
            if image in seen:
                continue
            seen.add(image)
            queue.append(image)
    return tuple(sorted(seen))


def apply_permutation(permutation: Permutation, simplex: Simplex) -> Simplex:
    return tuple(sorted(permutation[vertex] for vertex in simplex))


@lru_cache(maxsize=1)
def cp2_facets() -> tuple[Simplex, ...]:
    generator = permutation_from_cycles(
        9,
        ((1, 4, 7), (2, 5, 8), (3, 6, 9)),
    )
    orbit_group = permutation_closure((generator,), 9)
    base_facets = (
        (1, 5, 2, 8, 9),
        (1, 2, 3, 8, 9),
        (1, 3, 6, 8, 9),
        (4, 5, 2, 8, 9),
        (4, 2, 3, 8, 9),
        (4, 3, 6, 8, 9),
        (1, 4, 2, 5, 6),
        (1, 4, 3, 5, 6),
        (1, 4, 2, 5, 9),
        (1, 4, 3, 6, 8),
        (1, 4, 7, 2, 6),
        (1, 4, 7, 6, 8),
    )
    facets = {
        apply_permutation(permutation, facet)
        for permutation in orbit_group
        for facet in base_facets
    }
    return tuple(sorted(facets))


@lru_cache(maxsize=1)
def k3_facets() -> tuple[Simplex, ...]:
    generator_one = permutation_from_cycles(
        16,
        ((1, 3, 8, 4, 9, 16, 15, 2, 14, 12, 6, 7, 13, 5, 10),),
    )
    generator_two = permutation_from_cycles(
        16,
        (
            (1, 11, 16),
            (2, 10, 14),
            (3, 12, 13),
            (4, 9, 15),
            (5, 7, 8),
        ),
    )
    orbit_group = permutation_closure((generator_one, generator_two), 16)
    seed_facets = (
        (1, 2, 3, 8, 12),
        (1, 2, 5, 8, 14),
    )
    facets = {
        apply_permutation(permutation, facet)
        for permutation in orbit_group
        for facet in seed_facets
    }
    return tuple(sorted(facets))


def faces_by_dimension(facets: tuple[Simplex, ...]) -> tuple[tuple[Simplex, ...], ...]:
    faces: list[set[Simplex]] = [set() for _ in range(5)]
    for facet in facets:
        for subset_size in range(1, 6):
            for subset in combinations(facet, subset_size):
                faces[subset_size - 1].add(subset)
    return tuple(tuple(sorted(level)) for level in faces)


def boundary_matrix(high_simplices: tuple[Simplex, ...], low_simplices: tuple[Simplex, ...]) -> np.ndarray:
    low_index = {simplex: index for index, simplex in enumerate(low_simplices)}
    matrix = np.zeros((len(low_simplices), len(high_simplices)), dtype=np.int8)
    for column, simplex in enumerate(high_simplices):
        for row_position in range(len(simplex)):
            face = simplex[:row_position] + simplex[row_position + 1 :]
            matrix[low_index[face], column] = -1 if row_position % 2 else 1
    return matrix


def euler_characteristic(f_vector: tuple[int, int, int, int, int]) -> int:
    return int(sum(((-1) ** degree) * count for degree, count in enumerate(f_vector)))


def complex_profile(name: str, facets: tuple[Simplex, ...]) -> ExplicitComplexProfile:
    faces = faces_by_dimension(facets)
    f_vector = tuple(len(level) for level in faces)
    boundaries = tuple(
        boundary_matrix(faces[degree], faces[degree - 1])
        for degree in range(1, 5)
    )
    boundary_ranks = tuple(
        int(np.linalg.matrix_rank(boundary.astype(float))) for boundary in boundaries
    )

    betti = []
    for degree, chain_group in enumerate(faces):
        incoming_rank = boundary_ranks[degree - 1] if degree > 0 else 0
        outgoing_rank = boundary_ranks[degree] if degree < 4 else 0
        betti.append(len(chain_group) - incoming_rank - outgoing_rank)

    return ExplicitComplexProfile(
        name=name,
        vertices=len(faces[0]),
        facets=len(facets),
        f_vector=f_vector,
        boundary_ranks=boundary_ranks,
        betti_numbers=tuple(int(value) for value in betti),
        harmonic_form_total=int(sum(betti)),
        euler_characteristic=euler_characteristic(f_vector),
    )


@lru_cache(maxsize=1)
def cp2_profile() -> ExplicitComplexProfile:
    return complex_profile("CP2", cp2_facets())


@lru_cache(maxsize=1)
def k3_profile() -> ExplicitComplexProfile:
    return complex_profile("K3", k3_facets())


def build_explicit_curved_4d_complexes_summary() -> dict[str, Any]:
    cp2 = cp2_profile()
    k3 = k3_profile()
    return {
        "status": "ok",
        "construction_notes": {
            "cp2_orbit_generator_order": 3,
            "cp2_base_facets": 12,
            "k3_orbit_group_order": 240,
            "k3_seed_facets": 2,
        },
        "profiles": [cp2.to_dict(), k3.to_dict()],
        "bridge_verdict": (
            "The external 4D seeds are now explicit simplicial complexes, not just "
            "f-vector placeholders. CP2_9 and K3_16 carry executable chain "
            "complexes with exact Betti profiles (1,0,1,0,1) and (1,0,22,0,1), "
            "so the curved external side of the bridge now has concrete harmonic "
            "form sectors."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_explicit_curved_4d_complexes_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
