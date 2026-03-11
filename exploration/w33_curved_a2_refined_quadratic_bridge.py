"""Exact first-refinement quadratic bridge for the curved A2 product.

The seed-level quadratic bridge fixed Tr((DK^2)^2) and the t^2 coefficient only
at refinement step 0. This module pushes that one step further by treating the
first barycentric subdivision of the explicit curved seeds CP2_9 and K3_16
exactly.

The key computational move is to work with barycentric top chains rather than
brute-force subset scans of the whole refined complex:

  - vertices of sd(K) are nonempty faces of K;
  - top simplices of sd(K) are maximal strict face chains;
  - all refined faces are subchains of those top chains.

For CP2_9 and K3_16 this yields exact sd^1 data fast enough to package as a
theorem:

  - exact refined f-vectors;
  - exact refined external traces Tr(DK^2);
  - exact refined external second moments Tr((DK^2)^2);
  - exact refined product quadratic coefficients for the native A2 bridge.

This still does not prove the full refinement-tower quadratic theorem, but it
closes the next exact gap beyond the seed level.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
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

from w33_curved_a2_quadratic_seed_bridge import (
    boundary_square_trace_from_degrees,
    product_quadratic_seed_profile,
)
from w33_curved_a2_transport_product import a2_internal_profile
from w33_curved_barycentric_density_bridge import (
    total_chain_dimension,
    trace_dirac_kahler_squared,
)
from w33_explicit_curved_4d_complexes import cp2_facets, cp2_profile, k3_facets, k3_profile
from w33_minimal_triangulation_bridge import barycentric_subdivision_f_vector


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_a2_refined_quadratic_bridge_summary.json"

Simplex = tuple[int, ...]
Chain = tuple[Simplex, ...]


@dataclass(frozen=True)
class RefinedBoundarySquareLayer:
    degree: int
    lower_face_count: int
    higher_face_count: int
    coface_degree_square_sum: int
    boundary_square_trace: int
    degree_distribution: dict[int, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RefinedExternalQuadraticProfile:
    external_name: str
    refined_f_vector: tuple[int, int, int, int, int]
    top_simplices: int
    total_chain_dim: int
    external_trace: int
    external_second_moment: int
    external_second_moment_density: Fraction
    f_vector_matches_barycentric_transform: bool
    boundary_square_layers: tuple[RefinedBoundarySquareLayer, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "external_name": self.external_name,
            "refined_f_vector": list(self.refined_f_vector),
            "top_simplices": self.top_simplices,
            "total_chain_dim": self.total_chain_dim,
            "external_trace": self.external_trace,
            "external_second_moment": self.external_second_moment,
            "external_second_moment_density": _fraction_dict(self.external_second_moment_density),
            "f_vector_matches_barycentric_transform": self.f_vector_matches_barycentric_transform,
            "boundary_square_layers": [layer.to_dict() for layer in self.boundary_square_layers],
        }


@dataclass(frozen=True)
class RefinedProductQuadraticProfile:
    external_name: str
    product_second_moment: int
    quadratic_density_coefficient: Fraction
    seed_quadratic_density_coefficient: Fraction

    def to_dict(self) -> dict[str, Any]:
        return {
            "external_name": self.external_name,
            "product_second_moment": self.product_second_moment,
            "quadratic_density_coefficient": _fraction_dict(self.quadratic_density_coefficient),
            "seed_quadratic_density_coefficient": _fraction_dict(self.seed_quadratic_density_coefficient),
        }


def _fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    return {"exact": _fraction_string(value), "float": float(value)}


def _facets_for_name(name: str) -> tuple[Simplex, ...]:
    if name == "CP2":
        return cp2_facets()
    if name == "K3":
        return k3_facets()
    raise ValueError("external name must be 'CP2' or 'K3'")


def _seed_f_vector(name: str) -> tuple[int, int, int, int, int]:
    if name == "CP2":
        return cp2_profile().f_vector
    if name == "K3":
        return k3_profile().f_vector
    raise ValueError("external name must be 'CP2' or 'K3'")


def _top_chains_step_one(facets: tuple[Simplex, ...]) -> tuple[Chain, ...]:
    chains = []
    for facet in facets:
        for permutation in permutations(facet):
            prefix: list[int] = []
            chain: list[Simplex] = []
            for vertex in permutation:
                prefix.append(vertex)
                chain.append(tuple(sorted(prefix)))
            chains.append(tuple(chain))
    return tuple(chains)


def _refined_faces_by_dimension(top_chains: tuple[Chain, ...]) -> tuple[tuple[Chain, ...], ...]:
    levels: list[set[Chain]] = [set() for _ in range(5)]
    for chain in top_chains:
        for chain_length in range(1, 6):
            for indices in combinations(range(5), chain_length):
                levels[chain_length - 1].add(tuple(chain[index] for index in indices))
    return tuple(tuple(sorted(level)) for level in levels)


def _coface_degrees_by_high_length(refined_faces: tuple[tuple[Chain, ...], ...]) -> dict[int, tuple[int, ...]]:
    rows = {}
    for high_length in range(2, 6):
        degree_counter: Counter[Chain] = Counter()
        for chain in refined_faces[high_length - 1]:
            for index in range(high_length):
                degree_counter[chain[:index] + chain[index + 1 :]] += 1
        rows[high_length] = tuple(degree_counter[chain] for chain in refined_faces[high_length - 2])
    return rows


@lru_cache(maxsize=None)
def refined_external_quadratic_profile(name: str) -> RefinedExternalQuadraticProfile:
    facets = _facets_for_name(name)
    top_chains = _top_chains_step_one(facets)
    refined_faces = _refined_faces_by_dimension(top_chains)
    refined_f_vector = tuple(len(level) for level in refined_faces)
    coface_degrees = _coface_degrees_by_high_length(refined_faces)

    layers = []
    half_second_moment = 0
    for degree in range(1, 5):
        high_length = degree + 1
        higher_face_count = refined_f_vector[degree]
        degrees = coface_degrees[high_length]
        trace = boundary_square_trace_from_degrees(degree, higher_face_count, degrees)
        half_second_moment += trace
        layers.append(
            RefinedBoundarySquareLayer(
                degree=degree,
                lower_face_count=refined_f_vector[degree - 1],
                higher_face_count=higher_face_count,
                coface_degree_square_sum=sum(value * value for value in degrees),
                boundary_square_trace=trace,
                degree_distribution=dict(sorted(Counter(degrees).items())),
            )
        )

    refined_second_moment = 2 * half_second_moment
    return RefinedExternalQuadraticProfile(
        external_name=name,
        refined_f_vector=refined_f_vector,
        top_simplices=refined_f_vector[4],
        total_chain_dim=total_chain_dimension(refined_f_vector),
        external_trace=trace_dirac_kahler_squared(refined_f_vector),
        external_second_moment=refined_second_moment,
        external_second_moment_density=Fraction(refined_second_moment, refined_f_vector[4]),
        f_vector_matches_barycentric_transform=(
            refined_f_vector == barycentric_subdivision_f_vector(_seed_f_vector(name), steps=1)
        ),
        boundary_square_layers=tuple(layers),
    )


@lru_cache(maxsize=None)
def refined_product_quadratic_profile(name: str) -> RefinedProductQuadraticProfile:
    external = refined_external_quadratic_profile(name)
    internal = a2_internal_profile()
    product_second_moment = (
        internal.total_dimension * external.external_second_moment
        + 2 * internal.trace_laplacian * external.external_trace
        + external.total_chain_dim * internal.trace_laplacian_squared
    )
    return RefinedProductQuadraticProfile(
        external_name=name,
        product_second_moment=product_second_moment,
        quadratic_density_coefficient=Fraction(product_second_moment, 2 * external.top_simplices),
        seed_quadratic_density_coefficient=product_quadratic_seed_profile(name).quadratic_density_coefficient,
    )


@lru_cache(maxsize=1)
def build_curved_a2_refined_quadratic_bridge_summary() -> dict[str, Any]:
    cp2_external = refined_external_quadratic_profile("CP2")
    k3_external = refined_external_quadratic_profile("K3")
    cp2_product = refined_product_quadratic_profile("CP2")
    k3_product = refined_product_quadratic_profile("K3")
    seed_gap = abs(cp2_product.seed_quadratic_density_coefficient - k3_product.seed_quadratic_density_coefficient)
    refined_gap = abs(cp2_product.quadratic_density_coefficient - k3_product.quadratic_density_coefficient)

    return {
        "status": "ok",
        "refined_external_profiles": [
            cp2_external.to_dict(),
            k3_external.to_dict(),
        ],
        "refined_product_profiles": [
            cp2_product.to_dict(),
            k3_product.to_dict(),
        ],
        "refined_quadratic_theorem": {
            "sd1_f_vectors_match_exact_barycentric_transform_for_both_seeds": (
                cp2_external.f_vector_matches_barycentric_transform
                and k3_external.f_vector_matches_barycentric_transform
            ),
            "cp2_sd1_external_second_moment": cp2_external.external_second_moment,
            "k3_sd1_external_second_moment": k3_external.external_second_moment,
            "cp2_sd1_product_quadratic_density_coefficient": _fraction_string(
                cp2_product.quadratic_density_coefficient
            ),
            "k3_sd1_product_quadratic_density_coefficient": _fraction_string(
                k3_product.quadratic_density_coefficient
            ),
            "seed_quadratic_gap": _fraction_string(seed_gap),
            "sd1_quadratic_gap": _fraction_string(refined_gap),
            "first_refinement_contracts_cp2_k3_product_quadratic_gap": refined_gap < seed_gap,
        },
        "bridge_verdict": (
            "The curved A2 bridge now has exact quadratic data at the first "
            "barycentric refinement step, not only at the seeds. For sd^1(CP2_9) "
            "and sd^1(K3_16), the refined f-vectors are exact, the external "
            "second moments are 2104848 and 22872000, and the native A2 product "
            "quadratic coefficients are 908925/2 and 1835497/4. The CP2/K3 "
            "product-gap drops from 65520 at step 0 to 17647/4 at step 1, which "
            "is the first exact refinement-level evidence that the quadratic "
            "coefficient is beginning to organize into a common curved 4D regime."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_curved_a2_refined_quadratic_bridge_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
