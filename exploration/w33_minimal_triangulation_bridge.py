"""Minimal-triangulation bridge for the external 4D geometry.

This module links the current almost-commutative bridge to concrete curved
4-manifold seeds. Two standard vertex-minimal simplicial examples are:

- CP^2 with 9 vertices;
- K3 with 16 vertices.

Both are 3-neighborly combinatorial 4-manifolds, so their f-vectors are forced
by vertex count and the Dehn-Sommerville relations. Repeated barycentric
subdivision then gives a bona fide 4D refinement family.

The key bridge point is topological:

- closed flat manifolds have Euler characteristic 0;
- CP^2 has chi = 3;
- K3 has chi = 24.

So these seeds are intrinsically non-flat external candidates, unlike the flat
4-torus used in the previous bridge stage.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
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


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_minimal_triangulation_bridge_summary.json"


@dataclass(frozen=True)
class MinimalTriangulationSeed:
    name: str
    vertices: int
    euler_characteristic: int
    f_vector: tuple[int, int, int, int, int]
    flat_metric_topologically_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def max_euler_characteristic_three_neighborly_4manifold(n_vertices: int) -> float:
    """Upper envelope from 3-neighborly 4-manifold combinatorics."""

    if n_vertices < 0:
        raise ValueError("n_vertices must be nonnegative")
    n = n_vertices
    return n * (n * n - 15 * n + 74) / 60.0


def minimum_vertices_for_euler_characteristic(chi: int, max_vertices: int = 200) -> int:
    """Smallest `n` with the 3-neighborly upper envelope at least `chi`."""

    for n in range(0, max_vertices + 1):
        if max_euler_characteristic_three_neighborly_4manifold(n) >= chi:
            return n
    raise ValueError("max_vertices too small for requested chi")


def neighborly_4manifold_f_vector(n_vertices: int) -> tuple[int, int, int, int, int]:
    """Forced f-vector for a 3-neighborly combinatorial 4-manifold."""

    n = n_vertices
    f0 = n
    f1 = comb(n, 2)
    f2 = comb(n, 3)
    numerator_f4 = 3 * f2 - 2 * f1
    if numerator_f4 % 5 != 0:
        raise ValueError("No integral 4-simplex count for this 3-neighborly 4-manifold seed")
    f4 = numerator_f4 // 5
    numerator_f3 = 5 * f4
    if numerator_f3 % 2 != 0:
        raise ValueError("No integral 3-simplex count for this 3-neighborly 4-manifold seed")
    f3 = numerator_f3 // 2
    return (f0, f1, f2, f3, f4)


def euler_characteristic_from_f_vector(f_vector: tuple[int, int, int, int, int]) -> int:
    f0, f1, f2, f3, f4 = f_vector
    return f0 - f1 + f2 - f3 + f4


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
    f_vector: tuple[int, int, int, int, int],
    steps: int = 1,
) -> tuple[int, int, int, int, int]:
    """f-vector after repeated barycentric subdivision of a 4-complex."""

    if steps < 0:
        raise ValueError("steps must be nonnegative")

    current = tuple(int(x) for x in f_vector)
    for _ in range(steps):
        next_vector = []
        for j in range(5):
            total = 0
            for i in range(j, 5):
                # For barycentric subdivision, j-faces correspond to strict chains
                # of nonempty faces ending in an i-face, counted by
                # (j+1)! * S(i+1, j+1).
                total += current[i] * factorial(j + 1) * stirling_second_kind(i + 1, j + 1)
            next_vector.append(total)
        current = tuple(next_vector)
    return current


def flat_metric_topologically_forbidden(euler_characteristic: int) -> bool:
    """Closed flat manifolds necessarily have Euler characteristic 0."""

    return euler_characteristic != 0


def cp2_seed() -> MinimalTriangulationSeed:
    f_vector = neighborly_4manifold_f_vector(9)
    chi = euler_characteristic_from_f_vector(f_vector)
    return MinimalTriangulationSeed(
        name="CP2",
        vertices=9,
        euler_characteristic=chi,
        f_vector=f_vector,
        flat_metric_topologically_forbidden=flat_metric_topologically_forbidden(chi),
    )


def k3_seed() -> MinimalTriangulationSeed:
    f_vector = neighborly_4manifold_f_vector(16)
    chi = euler_characteristic_from_f_vector(f_vector)
    return MinimalTriangulationSeed(
        name="K3",
        vertices=16,
        euler_characteristic=chi,
        f_vector=f_vector,
        flat_metric_topologically_forbidden=flat_metric_topologically_forbidden(chi),
    )


def build_minimal_triangulation_summary() -> dict[str, Any]:
    cp2 = cp2_seed()
    k3 = k3_seed()
    cp2_sd1 = barycentric_subdivision_f_vector(cp2.f_vector, steps=1)
    k3_sd1 = barycentric_subdivision_f_vector(k3.f_vector, steps=1)

    return {
        "status": "ok",
        "seeds": [cp2.to_dict(), k3.to_dict()],
        "three_neighborly_bound": {
            "cp2_min_vertices_from_chi": minimum_vertices_for_euler_characteristic(cp2.euler_characteristic),
            "k3_min_vertices_from_chi": minimum_vertices_for_euler_characteristic(k3.euler_characteristic),
            "formula": "chi <= n(n^2 - 15n + 74) / 60",
        },
        "barycentric_subdivision": {
            "cp2_sd1_f_vector": cp2_sd1,
            "k3_sd1_f_vector": k3_sd1,
            "top_simplex_multiplier_per_step": 120,
        },
        "bridge_verdict": (
            "Minimal triangulations of CP2 and K3 provide curved 4D simplicial "
            "seed geometries. Repeated barycentric subdivision gives an actual 4D "
            "refinement family, and chi != 0 blocks the flat-metric obstruction "
            "that limited the torus stage."
        ),
        "count_overlap_note": (
            "K3 uses 16 vertices, which matches the tomotope 16-face / Reye "
            "16-line count. This is only a count-level overlap until an explicit "
            "map is constructed."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_minimal_triangulation_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
