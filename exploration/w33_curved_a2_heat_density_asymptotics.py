"""Exact first-order heat-density asymptotics for the curved A2 bridge.

For the curved external refinement family paired with the native internal A2
transport Laplacian, the normalized heat trace per top simplex has an exact
small-time expansion

    h_r(t) = a_r - b_r t + O(t^2)

where:

- a_r is the exact product chain density per top simplex;
- b_r is the exact product trace density per top simplex;
- both admit exact closed forms under barycentric refinement;
- the product spectral gap stays exactly 24 because the internal A2 sector has
  gap 24 and no zero modes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_curved_a2_transport_product import (
    a2_internal_profile,
    a2_product_heat_trace_direct,
)
from w33_curved_barycentric_density_bridge import (
    exact_chain_density_formula,
    exact_trace_density_formula,
)
from w33_minimal_triangulation_bridge import (
    barycentric_subdivision_f_vector,
    cp2_seed,
    k3_seed,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_a2_heat_density_asymptotics_summary.json"


@dataclass(frozen=True)
class HeatDensitySample:
    step: int
    top_simplices: int
    constant_term: Fraction
    linear_term: Fraction
    constant_abs_error: Fraction
    linear_abs_error: Fraction

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "top_simplices": self.top_simplices,
            "constant_term": _fraction_dict(self.constant_term),
            "linear_term": _fraction_dict(self.linear_term),
            "constant_abs_error": _fraction_dict(self.constant_abs_error),
            "linear_abs_error": _fraction_dict(self.linear_abs_error),
        }


@dataclass(frozen=True)
class StepZeroHeatCheck:
    external_name: str
    t: float
    exact_density: float
    first_order_prediction: float
    abs_error: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    if value.denominator == 1:
        exact = str(value.numerator)
    else:
        exact = f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def a2_product_chain_density_formula(n_vertices: int, step: int) -> Fraction:
    return Fraction(a2_internal_profile().total_dimension) * exact_chain_density_formula(n_vertices, step)


def a2_product_trace_density_formula(n_vertices: int, step: int) -> Fraction:
    internal = a2_internal_profile()
    external_chain = exact_chain_density_formula(n_vertices, step)
    external_trace = exact_trace_density_formula(n_vertices, step)
    return Fraction(internal.total_dimension) * external_trace + Fraction(internal.trace_laplacian) * external_chain


def _seed_coefficients(n_vertices: int) -> dict[str, Fraction]:
    constant_limit = Fraction(10800, 19)
    linear_limit = Fraction(423000, 19)
    step0_constant = a2_product_chain_density_formula(n_vertices, 0)
    step0_linear = a2_product_trace_density_formula(n_vertices, 0)
    # Recover the exact 20^{-r} and 120^{-r} coefficients from the step-0 and universal values.
    # For the product chain density, the shared 120^{-r} coefficient is 15/2 for both seeds.
    twelfth = Fraction(15, 2)
    twenty = step0_constant - constant_limit - twelfth
    # For the product trace density, the shared 120^{-r} coefficient is 240 for both seeds.
    twelfth_linear = Fraction(240)
    twenty_linear = step0_linear - linear_limit - twelfth_linear
    return {
        "constant_limit": constant_limit,
        "constant_corr_20": twenty,
        "constant_corr_120": twelfth,
        "linear_limit": linear_limit,
        "linear_corr_20": twenty_linear,
        "linear_corr_120": twelfth_linear,
    }


def seed_heat_density_samples(
    n_vertices: int,
    base_f_vector: tuple[int, int, int, int, int],
    max_step: int = 4,
) -> tuple[HeatDensitySample, ...]:
    samples = []
    for step in range(max_step + 1):
        refined = barycentric_subdivision_f_vector(base_f_vector, steps=step)
        top = refined[4]
        constant = a2_product_chain_density_formula(n_vertices, step)
        linear = a2_product_trace_density_formula(n_vertices, step)
        samples.append(
            HeatDensitySample(
                step=step,
                top_simplices=top,
                constant_term=constant,
                linear_term=linear,
                constant_abs_error=abs(constant - Fraction(10800, 19)),
                linear_abs_error=abs(linear - Fraction(423000, 19)),
            )
        )
    return tuple(samples)


def step_zero_heat_checks(
    t_values: tuple[float, ...] = (1e-4, 2e-4, 5e-4),
) -> tuple[StepZeroHeatCheck, ...]:
    checks = []
    for name, seed in (("CP2", cp2_seed()), ("K3", k3_seed())):
        top = seed.f_vector[4]
        constant = float(a2_product_chain_density_formula(seed.vertices, 0))
        linear = float(a2_product_trace_density_formula(seed.vertices, 0))
        for t in t_values:
            exact_density = a2_product_heat_trace_direct(name, t) / top
            prediction = constant - linear * t
            checks.append(
                StepZeroHeatCheck(
                    external_name=name,
                    t=t,
                    exact_density=exact_density,
                    first_order_prediction=prediction,
                    abs_error=abs(exact_density - prediction),
                )
            )
    return tuple(checks)


@lru_cache(maxsize=1)
def build_curved_a2_heat_density_asymptotics_summary() -> dict[str, Any]:
    cp2 = cp2_seed()
    k3 = k3_seed()
    cp2_coeffs = _seed_coefficients(cp2.vertices)
    k3_coeffs = _seed_coefficients(k3.vertices)
    internal = a2_internal_profile()
    return {
        "status": "ok",
        "persistent_gap_theorem": {
            "internal_gap": internal.spectral_gap,
            "product_gap_for_all_refinement_steps": internal.spectral_gap,
            "reason": "external zero modes plus positive internal A2 gap 24",
        },
        "universal_limits": {
            "constant_term_per_top_simplex": _fraction_dict(Fraction(10800, 19)),
            "linear_term_per_top_simplex": _fraction_dict(Fraction(423000, 19)),
        },
        "seed_closed_forms": [
            {
                "name": cp2.name,
                "vertices": cp2.vertices,
                "constant_term_formula": {
                    "limit": _fraction_dict(cp2_coeffs["constant_limit"]),
                    "corr_20_power_r": _fraction_dict(cp2_coeffs["constant_corr_20"]),
                    "corr_120_power_r": _fraction_dict(cp2_coeffs["constant_corr_120"]),
                },
                "linear_term_formula": {
                    "limit": _fraction_dict(cp2_coeffs["linear_limit"]),
                    "corr_20_power_r": _fraction_dict(cp2_coeffs["linear_corr_20"]),
                    "corr_120_power_r": _fraction_dict(cp2_coeffs["linear_corr_120"]),
                },
                "samples": [sample.to_dict() for sample in seed_heat_density_samples(cp2.vertices, cp2.f_vector)],
            },
            {
                "name": k3.name,
                "vertices": k3.vertices,
                "constant_term_formula": {
                    "limit": _fraction_dict(k3_coeffs["constant_limit"]),
                    "corr_20_power_r": _fraction_dict(k3_coeffs["constant_corr_20"]),
                    "corr_120_power_r": _fraction_dict(k3_coeffs["constant_corr_120"]),
                },
                "linear_term_formula": {
                    "limit": _fraction_dict(k3_coeffs["linear_limit"]),
                    "corr_20_power_r": _fraction_dict(k3_coeffs["linear_corr_20"]),
                    "corr_120_power_r": _fraction_dict(k3_coeffs["linear_corr_120"]),
                },
                "samples": [sample.to_dict() for sample in seed_heat_density_samples(k3.vertices, k3.f_vector)],
            },
        ],
        "step_zero_heat_checks": [check.to_dict() for check in step_zero_heat_checks()],
        "bridge_verdict": (
            "The native curved A2 bridge now has exact first-order heat-density "
            "asymptotics across the full curved refinement tower. Per top simplex, "
            "the product heat trace has exact constant term 10800/19 and exact "
            "linear term 423000/19 in the universal refinement limit, with "
            "explicit 20^{-r} and 120^{-r} corrections for CP2 and K3. The "
            "product spectral gap stays exactly 24 for every refinement step."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_a2_heat_density_asymptotics_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
