"""Curved Dirac-type transport bridge across the full 4D refinement tower.

The transport side now has the correct curved algebraic object: an upper-
triangular adapted precomplex over F3 with exact curvature. The next step is to
package that object in the operator language that can actually couple to the
curved 4D refinement family.

This module does two things.

1. It forms the symmetric Dirac-type operator

       D_tr = [[0, d0^T, 0], [d0, 0, d1^T], [0, d1, 0]]

   on the integer lift of the adapted transport precomplex. Its square keeps
   the Hodge-style diagonal blocks while retaining the transport curvature in
   the corner blocks.

2. It carries that exact internal operator package across the curved external
   barycentric refinement tower. At first order in the heat expansion, only the
   internal dimension and Tr(D_tr^2) matter, so the full twisted transport
   object now acquires exact universal density limits and exact seed-dependent
   correction formulas on CP2_9 and K3_16.

This is the first place where the internally curved transport package itself,
not only its protected harmonic shadow, crosses the curved 4D refinement
bridge.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np

from w33_curved_barycentric_density_bridge import (
    exact_chain_density_formula,
    exact_trace_density_formula,
    neighborly_mode_coefficients,
)
from w33_minimal_triangulation_bridge import cp2_seed, k3_seed
from w33_ternary_homological_code_bridge import build_ternary_homological_code_summary
from w33_transport_matter_curved_harmonic_bridge import (
    build_transport_matter_curved_harmonic_summary,
)
from w33_transport_twisted_precomplex_bridge import (
    MODULUS,
    adapted_transport_precomplex_data,
    build_transport_twisted_precomplex_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_transport_curved_dirac_refinement_bridge_summary.json"
)


@dataclass(frozen=True)
class HeatDensitySample:
    step: int
    constant_term: Fraction
    linear_term: Fraction

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "constant_term": _fraction_dict(self.constant_term),
            "linear_term": _fraction_dict(self.linear_term),
        }


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _signed_lift_mod3(matrix: np.ndarray) -> np.ndarray:
    lifted = np.array(matrix, dtype=int) % MODULUS
    lifted[lifted == MODULUS - 1] = -1
    return lifted


@lru_cache(maxsize=1)
def lifted_transport_coboundaries() -> tuple[np.ndarray, np.ndarray]:
    data = adapted_transport_precomplex_data()
    return _signed_lift_mod3(data["d0"]), _signed_lift_mod3(data["d1"])


@lru_cache(maxsize=1)
def transport_curved_dirac_profile() -> dict[str, int | bool]:
    d0, d1 = lifted_transport_coboundaries()
    precomplex = build_transport_twisted_precomplex_summary()

    trace_l0 = int(np.sum(d0 * d0))
    trace_l2 = int(np.sum(d1 * d1))
    trace_l1 = trace_l0 + trace_l2

    return {
        "c0_dimension": int(d0.shape[1]),
        "c1_dimension": int(d0.shape[0]),
        "c2_dimension": int(d1.shape[0]),
        "total_dimension": int(d0.shape[1] + d0.shape[0] + d1.shape[0]),
        "trace_l0": trace_l0,
        "trace_l1": trace_l1,
        "trace_l2": trace_l2,
        "trace_d_squared": trace_l0 + trace_l1 + trace_l2,
        "curvature_corner_rank": int(precomplex["curved_extension_package"]["full_curvature_rank"]),
        "cocycle_corner_rank": int(precomplex["curved_extension_package"]["off_diagonal_curvature_rank"]),
        "symmetric_dirac_by_construction": True,
    }


def _seed_first_order_profile(
    total_dimension: int,
    trace_d_squared: int,
    n_vertices: int,
    max_step: int = 4,
) -> dict[str, Any]:
    coefficients = neighborly_mode_coefficients(n_vertices)
    local_mode = coefficients["local_mode"]
    chi_mode = coefficients["chi_mode"]
    six_mode = coefficients["six_mode"]

    chain_limit = Fraction(total_dimension) * Fraction(120, 19)
    chain_corr_20 = Fraction(total_dimension) * Fraction(3) * six_mode / local_mode
    chain_corr_120 = Fraction(total_dimension) * chi_mode / local_mode

    linear_limit = (
        Fraction(total_dimension) * Fraction(860, 19)
        + Fraction(trace_d_squared) * Fraction(120, 19)
    )
    linear_corr_20 = (
        Fraction(total_dimension) * Fraction(12) * six_mode / local_mode
        + Fraction(trace_d_squared) * Fraction(3) * six_mode / local_mode
    )
    linear_corr_120 = Fraction(trace_d_squared) * chi_mode / local_mode

    samples = []
    for step in range(max_step + 1):
        samples.append(
            HeatDensitySample(
                step=step,
                constant_term=Fraction(total_dimension) * exact_chain_density_formula(n_vertices, step),
                linear_term=(
                    Fraction(total_dimension) * exact_trace_density_formula(n_vertices, step)
                    + Fraction(trace_d_squared) * exact_chain_density_formula(n_vertices, step)
                ),
            )
        )

    return {
        "constant_term_formula": {
            "limit": _fraction_dict(chain_limit),
            "corr_20_power_r": _fraction_dict(chain_corr_20),
            "corr_120_power_r": _fraction_dict(chain_corr_120),
        },
        "linear_term_formula": {
            "limit": _fraction_dict(linear_limit),
            "corr_20_power_r": _fraction_dict(linear_corr_20),
            "corr_120_power_r": _fraction_dict(linear_corr_120),
        },
        "samples": [sample.to_dict() for sample in samples],
    }


@lru_cache(maxsize=1)
def build_transport_curved_dirac_refinement_summary() -> dict[str, Any]:
    transport_profile = transport_curved_dirac_profile()
    ternary = build_ternary_homological_code_summary()
    matter_bridge = build_transport_matter_curved_harmonic_summary()

    logical_qutrits = int(ternary["ternary_css_code"]["logical_qutrits"])
    matter_total_dimension = logical_qutrits * int(transport_profile["total_dimension"])
    matter_trace_d_squared = logical_qutrits * int(transport_profile["trace_d_squared"])
    matter_corner_rank = logical_qutrits * int(transport_profile["curvature_corner_rank"])

    protected_curved_lifts = {}
    for profile in matter_bridge["curved_external_harmonic_channels"]:
        name = profile["external_name"]
        if name == "CP2":
            name = "CP2_9"
        elif name == "K3":
            name = "K3_16"
        protected_curved_lifts[name] = int(profile["protected_flat_matter_zero_modes"])

    cp2 = cp2_seed()
    k3 = k3_seed()

    return {
        "status": "ok",
        "transport_curved_dirac": {
            "c0_dimension": int(transport_profile["c0_dimension"]),
            "c1_dimension": int(transport_profile["c1_dimension"]),
            "c2_dimension": int(transport_profile["c2_dimension"]),
            "total_dimension": int(transport_profile["total_dimension"]),
            "trace_l0": int(transport_profile["trace_l0"]),
            "trace_l1": int(transport_profile["trace_l1"]),
            "trace_l2": int(transport_profile["trace_l2"]),
            "trace_d_squared": int(transport_profile["trace_d_squared"]),
            "curvature_corner_rank": int(transport_profile["curvature_corner_rank"]),
            "cocycle_corner_rank": int(transport_profile["cocycle_corner_rank"]),
            "symmetric_dirac_by_construction": bool(
                transport_profile["symmetric_dirac_by_construction"]
            ),
        },
        "matter_coupled_curved_dirac": {
            "logical_qutrits": logical_qutrits,
            "total_dimension": matter_total_dimension,
            "trace_d_squared": matter_trace_d_squared,
            "curvature_corner_rank": matter_corner_rank,
            "protected_flat_subsector_dimension": int(
                matter_bridge["matter_coupled_precomplex"]["protected_flat_h0_dimension"]
            ),
            "protected_flat_curved_harmonic_lifts": protected_curved_lifts,
        },
        "curved_refinement_first_order_bridge": {
            "transport": [
                {
                    "name": cp2.name,
                    "vertices": cp2.vertices,
                    **_seed_first_order_profile(
                        int(transport_profile["total_dimension"]),
                        int(transport_profile["trace_d_squared"]),
                        cp2.vertices,
                    ),
                },
                {
                    "name": k3.name,
                    "vertices": k3.vertices,
                    **_seed_first_order_profile(
                        int(transport_profile["total_dimension"]),
                        int(transport_profile["trace_d_squared"]),
                        k3.vertices,
                    ),
                },
            ],
            "matter_coupled": [
                {
                    "name": cp2.name,
                    "vertices": cp2.vertices,
                    **_seed_first_order_profile(
                        matter_total_dimension,
                        matter_trace_d_squared,
                        cp2.vertices,
                    ),
                },
                {
                    "name": k3.name,
                    "vertices": k3.vertices,
                    **_seed_first_order_profile(
                        matter_total_dimension,
                        matter_trace_d_squared,
                        k3.vertices,
                    ),
                },
            ],
        },
        "bridge_verdict": (
            "The internally curved transport package now crosses the curved 4D "
            "bridge as a genuine operator, not only through protected harmonic "
            "counts. The integer lift of the adapted transport precomplex defines "
            "a symmetric Dirac-type operator on C0 ⊕ C1 ⊕ C2 of total dimension "
            "12090. Its square keeps the Hodge-style diagonal blocks with exact "
            "trace split 3276 + 37386 + 34110 = 74772, while the corner blocks "
            "retain the exact transport curvature of rank 42 and its cocycle part "
            "of rank 36. Tensoring with the exact 81-qutrit matter sector upgrades "
            "this to a 979290-dimensional curved internal operator with Tr(D^2) = "
            "6056532, still containing the canonically protected flat 81-sector and "
            "its exact curved harmonic lifts 243 on CP2_9 and 1944 on K3_16. "
            "Because the external curved barycentric tower already has exact chain "
            "and trace densities, this full twisted internal object now acquires "
            "exact first-order heat-density asymptotics across the whole curved "
            "refinement family. So the transport-twisted matter package is no longer "
            "tied only to harmonic channels; it now has an exact first-order curved "
            "spectral-action bridge over the full 4D refinement tower."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_curved_dirac_refinement_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
