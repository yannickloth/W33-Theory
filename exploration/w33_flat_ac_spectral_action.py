"""Flat almost-commutative spectral-action coefficients for the W33 bridge.

This module extracts the first small-time coefficients for the product of:

1. a flat 4-dimensional external geometry (the unit 4-torus), and
2. the exact W(3,3) finite internal Dirac operator.

The point is twofold:

- show exactly how the finite W33 data enters the first coefficients;
- record the remaining obstruction: a flat 4-torus has zero scalar curvature,
  so it cannot supply a nontrivial Einstein-Hilbert term by itself.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
from math import exp, pi, sqrt
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

from w33_finite_spectral_triple import finite_dirac_162
from w33_tomotope_ac_bridge import internal_heat_trace


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_flat_ac_spectral_action_summary.json"


@dataclass(frozen=True)
class FlatProductCoefficients:
    internal_dimension: int
    trace_d2: float
    trace_d4: float
    heat_leading_t_minus_2: float
    heat_leading_t_minus_1: float
    heat_leading_t_0: float
    external_scalar_curvature_term: float
    external_is_flat: bool
    needs_curved_external_geometry: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@lru_cache(maxsize=1)
def internal_dirac_moments() -> dict[str, float]:
    dirac = finite_dirac_162().astype(float)
    d2 = dirac @ dirac
    d4 = d2 @ d2
    return {
        "dim": float(dirac.shape[0]),
        "tr_d2": float(np.trace(d2)),
        "tr_d4": float(np.trace(d4)),
    }


def flat_product_coefficients() -> FlatProductCoefficients:
    moments = internal_dirac_moments()
    prefactor = 1.0 / (16.0 * pi**2)
    dim = moments["dim"]
    tr_d2 = moments["tr_d2"]
    tr_d4 = moments["tr_d4"]
    return FlatProductCoefficients(
        internal_dimension=int(dim),
        trace_d2=tr_d2,
        trace_d4=tr_d4,
        heat_leading_t_minus_2=prefactor * dim,
        heat_leading_t_minus_1=-prefactor * tr_d2,
        heat_leading_t_0=(prefactor / 2.0) * tr_d4,
        external_scalar_curvature_term=0.0,
        external_is_flat=True,
        needs_curved_external_geometry=True,
    )


def continuum_circle_heat_trace_dual(t: float, modes: int = 3) -> float:
    """Poisson-dual circle heat trace on the unit circle."""

    if t <= 0.0:
        raise ValueError("t must be positive")
    if modes < 0:
        raise ValueError("modes must be nonnegative")
    prefactor = 1.0 / sqrt(4.0 * pi * t)
    return prefactor * sum(exp(-(m * m) / (4.0 * t)) for m in range(-modes, modes + 1))


def continuum_torus4_heat_trace_dual(t: float, modes: int = 3) -> float:
    one_d = continuum_circle_heat_trace_dual(t, modes=modes)
    return one_d**4


def flat_product_heat_trace_dual(t: float, modes: int = 3) -> float:
    return continuum_torus4_heat_trace_dual(t, modes=modes) * internal_heat_trace(t)


def flat_product_asymptotic_prediction(t: float) -> float:
    coeffs = flat_product_coefficients()
    return (
        coeffs.heat_leading_t_minus_2 / (t**2)
        + coeffs.heat_leading_t_minus_1 / t
        + coeffs.heat_leading_t_0
    )


def renormalized_flat_product_heat(t: float, modes: int = 3) -> float:
    return (t**2) * flat_product_heat_trace_dual(t, modes=modes)


def renormalized_flat_product_prediction(t: float) -> float:
    return (t**2) * flat_product_asymptotic_prediction(t)


def build_flat_product_summary() -> dict[str, Any]:
    coeffs = flat_product_coefficients()
    samples = []
    for t in (1e-4, 2e-4, 5e-4):
        exact = renormalized_flat_product_heat(t)
        predicted = renormalized_flat_product_prediction(t)
        samples.append(
            {
                "t": t,
                "renormalized_exact": exact,
                "renormalized_prediction": predicted,
                "abs_error": abs(exact - predicted),
            }
        )
    return {
        "status": "ok",
        "coefficients": coeffs.to_dict(),
        "samples": samples,
        "verdict": (
            "The W33 finite triple now contributes explicit small-time coefficients "
            "to the flat 4D almost-commutative product. But because the external "
            "geometry is flat, the scalar-curvature / Einstein-Hilbert term is "
            "still zero. The next bridge must therefore use a curved external 4D "
            "refinement family."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_flat_product_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
