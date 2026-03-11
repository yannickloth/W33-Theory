"""Exact second-order heat data for the curved A2 bridge at the seed level.

This module pushes the native A2 transport bridge one order deeper in small
time, but only where the proof is exact right now: the explicit curved seeds
CP2_9 and K3_16.

For the product of the explicit external Dirac-Kahler square with the native
internal A2 transport Laplacian, the normalized heat trace per top simplex has
an exact step-zero expansion

    h_0(t) = a_0 - b_0 t + c_0 t^2 + O(t^3)

with:

- exact constant and linear coefficients already fixed by the first-order
  bridge;
- an exact quadratic coefficient recovered from Tr(L^2);
- an exact combinatorial recovery of the external second moment from coface
  degree-square sums.

This does not yet prove the full refinement-tower quadratic theorem. It closes
the next exact gap at the explicit curved seeds.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import lru_cache
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

from w33_curved_a2_heat_density_asymptotics import (
    a2_product_chain_density_formula,
    a2_product_trace_density_formula,
)
from w33_curved_a2_transport_product import a2_internal_profile, a2_product_heat_trace_direct
from w33_curved_external_hodge_product import (
    external_dirac_kahler_squared_eigenvalues,
    external_operator_profile,
)
from w33_explicit_curved_4d_complexes import cp2_facets, faces_by_dimension, k3_facets


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_a2_quadratic_seed_bridge_summary.json"
TOL = 1e-8


@dataclass(frozen=True)
class BoundarySquareLayer:
    degree: int
    lower_face_count: int
    higher_face_count: int
    coface_degree_square_sum: int
    boundary_square_trace: int
    degree_distribution: dict[int, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalSecondMomentProfile:
    external_name: str
    top_simplices: int
    external_trace: int
    external_second_moment: int
    combinatorial_equals_spectral: bool
    boundary_square_layers: tuple[BoundarySquareLayer, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "external_name": self.external_name,
            "top_simplices": self.top_simplices,
            "external_trace": self.external_trace,
            "external_second_moment": self.external_second_moment,
            "combinatorial_equals_spectral": self.combinatorial_equals_spectral,
            "boundary_square_layers": [layer.to_dict() for layer in self.boundary_square_layers],
        }


@dataclass(frozen=True)
class ProductQuadraticSeedProfile:
    external_name: str
    constant_density: Fraction
    linear_density: Fraction
    quadratic_density_coefficient: Fraction
    product_second_moment: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "external_name": self.external_name,
            "constant_density": _fraction_dict(self.constant_density),
            "linear_density": _fraction_dict(self.linear_density),
            "quadratic_density_coefficient": _fraction_dict(self.quadratic_density_coefficient),
            "product_second_moment": self.product_second_moment,
        }


@dataclass(frozen=True)
class SecondOrderHeatCheck:
    external_name: str
    t: float
    exact_density: float
    first_order_prediction: float
    second_order_prediction: float
    first_order_abs_error: float
    second_order_abs_error: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    if value.denominator == 1:
        exact = str(value.numerator)
    else:
        exact = f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _facets_for_name(name: str) -> tuple[tuple[int, ...], ...]:
    if name == "CP2":
        return cp2_facets()
    if name == "K3":
        return k3_facets()
    raise ValueError("external name must be 'CP2' or 'K3'")


def _seed_vertices(name: str) -> int:
    if name == "CP2":
        return 9
    if name == "K3":
        return 16
    raise ValueError("external name must be 'CP2' or 'K3'")


def _coface_degrees(
    lower_faces: tuple[tuple[int, ...], ...],
    higher_faces: tuple[tuple[int, ...], ...],
) -> tuple[int, ...]:
    degrees = []
    higher_sets = [set(face) for face in higher_faces]
    for lower in lower_faces:
        lower_set = set(lower)
        degrees.append(sum(1 for higher in higher_sets if lower_set.issubset(higher)))
    return tuple(degrees)


def boundary_square_trace_from_degrees(
    degree: int,
    higher_face_count: int,
    coface_degrees: tuple[int, ...],
) -> int:
    return sum(value * value for value in coface_degrees) + degree * (degree + 1) * higher_face_count


def rounded_second_moment_from_spectrum(eigenvalues: np.ndarray) -> int:
    second_moment = np.sum(eigenvalues * eigenvalues)
    rounded = int(round(float(second_moment)))
    if abs(float(second_moment) - rounded) > TOL:
        raise AssertionError("expected integral second moment")
    return rounded


@lru_cache(maxsize=None)
def external_second_moment_profile(name: str) -> ExternalSecondMomentProfile:
    faces = faces_by_dimension(_facets_for_name(name))
    layers = []
    half_second_moment = 0
    for degree in range(1, 5):
        lower_faces = faces[degree - 1]
        higher_faces = faces[degree]
        coface_degrees = _coface_degrees(lower_faces, higher_faces)
        trace = boundary_square_trace_from_degrees(degree, len(higher_faces), coface_degrees)
        layers.append(
            BoundarySquareLayer(
                degree=degree,
                lower_face_count=len(lower_faces),
                higher_face_count=len(higher_faces),
                coface_degree_square_sum=sum(value * value for value in coface_degrees),
                boundary_square_trace=trace,
                degree_distribution=dict(sorted(Counter(coface_degrees).items())),
            )
        )
        half_second_moment += trace

    spectral = rounded_second_moment_from_spectrum(external_dirac_kahler_squared_eigenvalues(name))
    combinatorial = 2 * half_second_moment
    return ExternalSecondMomentProfile(
        external_name=name,
        top_simplices=len(faces[4]),
        external_trace=int(round(external_operator_profile(name).trace_dk_squared)),
        external_second_moment=combinatorial,
        combinatorial_equals_spectral=(combinatorial == spectral),
        boundary_square_layers=tuple(layers),
    )


@lru_cache(maxsize=None)
def product_quadratic_seed_profile(name: str) -> ProductQuadraticSeedProfile:
    external = external_second_moment_profile(name)
    external_operator = external_operator_profile(name)
    internal = a2_internal_profile()
    product_second_moment = (
        internal.total_dimension * external.external_second_moment
        + 2 * internal.trace_laplacian * external.external_trace
        + external_operator.total_chain_dim * internal.trace_laplacian_squared
    )
    top = external.top_simplices
    return ProductQuadraticSeedProfile(
        external_name=name,
        constant_density=a2_product_chain_density_formula(_seed_vertices(name), 0),
        linear_density=a2_product_trace_density_formula(_seed_vertices(name), 0),
        quadratic_density_coefficient=Fraction(product_second_moment, 2 * top),
        product_second_moment=product_second_moment,
    )


def step_zero_second_order_heat_checks(
    t_values: tuple[float, ...] = (1e-4, 2e-4, 5e-4),
) -> tuple[SecondOrderHeatCheck, ...]:
    checks = []
    for name in ("CP2", "K3"):
        profile = product_quadratic_seed_profile(name)
        top = external_second_moment_profile(name).top_simplices
        constant = float(profile.constant_density)
        linear = float(profile.linear_density)
        quadratic = float(profile.quadratic_density_coefficient)
        for t in t_values:
            exact_density = a2_product_heat_trace_direct(name, t) / top
            first_order = constant - linear * t
            second_order = first_order + quadratic * t * t
            checks.append(
                SecondOrderHeatCheck(
                    external_name=name,
                    t=t,
                    exact_density=exact_density,
                    first_order_prediction=first_order,
                    second_order_prediction=second_order,
                    first_order_abs_error=abs(exact_density - first_order),
                    second_order_abs_error=abs(exact_density - second_order),
                )
            )
    return tuple(checks)


@lru_cache(maxsize=1)
def build_curved_a2_quadratic_seed_bridge_summary() -> dict[str, Any]:
    cp2 = external_second_moment_profile("CP2")
    k3 = external_second_moment_profile("K3")
    cp2_product = product_quadratic_seed_profile("CP2")
    k3_product = product_quadratic_seed_profile("K3")
    checks = step_zero_second_order_heat_checks()
    return {
        "status": "ok",
        "external_second_moment_profiles": [cp2.to_dict(), k3.to_dict()],
        "product_quadratic_seed_profiles": [cp2_product.to_dict(), k3_product.to_dict()],
        "step_zero_second_order_heat_checks": [check.to_dict() for check in checks],
        "bridge_verdict": (
            "The curved A2 bridge now has exact second-order seed data. For the "
            "explicit CP2_9 and K3_16 seeds, the external second moment "
            "Tr((DK^2)^2) is recovered exactly from coface degree-square sums, and "
            "the native A2 product heat density has exact step-zero expansions "
            "1275/2 - 24720 t + 491580 t^2 + O(t^3) and "
            "1065/2 - 20940 t + 426060 t^2 + O(t^3). The second-order prediction "
            "beats the first-order one by orders of magnitude at small t, but the "
            "full refinement-tower quadratic theorem remains open."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_a2_quadratic_seed_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
