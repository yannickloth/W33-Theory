"""Curved 4D product bridge for the native A2 transport local system.

This module pairs the exact internal A2 transport local system on the 45-point
center-quad quotient with the explicit curved external Hodge/Dirac-Kahler
operators on CP2_9 and K3_16.

The internal operator used here is the positive A2 transport Laplacian

    L_A2 = 32 I - H_A2

where H_A2 is the exact 90-dimensional A2 local-system transport operator.

This yields:

1. a native internal 90-dimensional positive operator with exact spectrum
   24^20, 33^64, 48^6;
2. exact heat-trace factorization against the explicit curved external spectra;
3. exact product dimensions, traces, and spectral gaps for CP2 and K3 products;
4. exact refined local-density limits 10800/19 and 423000/19 per top simplex.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np

from w33_center_quad_transport_a2_bridge import build_center_quad_transport_a2_summary
from w33_curved_barycentric_density_bridge import (
    universal_chain_density_limit,
    universal_trace_density_limit,
)
from w33_curved_external_hodge_product import (
    external_dirac_kahler_squared_eigenvalues,
    external_heat_trace,
    external_operator_profile,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_a2_transport_product_summary.json"


@dataclass(frozen=True)
class A2InternalProfile:
    total_dimension: int
    laplacian_spectrum: dict[int, int]
    spectral_gap: int
    trace_laplacian: int
    trace_laplacian_squared: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class A2CurvedProductProfile:
    external_name: str
    total_dimension: int
    spectral_gap: int
    trace_product: int
    zero_modes: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProductHeatCheck:
    external_name: str
    t: float
    external_heat_trace: float
    a2_internal_heat_trace: float
    factorized_product_heat_trace: float
    direct_product_heat_trace: float
    abs_error: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    if value.denominator == 1:
        exact = str(value.numerator)
    else:
        exact = f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def a2_transport_laplacian_spectrum() -> dict[int, int]:
    summary = build_center_quad_transport_a2_summary()
    spectrum = summary["a2_transport_operator"]["laplacian_spectrum"]
    return {int(key): int(value) for key, value in spectrum.items()}


@lru_cache(maxsize=1)
def a2_transport_laplacian_eigenvalues() -> np.ndarray:
    parts = []
    for eigenvalue, multiplicity in sorted(a2_transport_laplacian_spectrum().items()):
        parts.append(np.full(multiplicity, float(eigenvalue)))
    return np.concatenate(parts)


@lru_cache(maxsize=1)
def a2_internal_profile() -> A2InternalProfile:
    eigenvalues = a2_transport_laplacian_eigenvalues()
    return A2InternalProfile(
        total_dimension=int(eigenvalues.size),
        laplacian_spectrum=a2_transport_laplacian_spectrum(),
        spectral_gap=int(np.min(eigenvalues)),
        trace_laplacian=int(round(float(np.sum(eigenvalues)))),
        trace_laplacian_squared=int(round(float(np.sum(eigenvalues * eigenvalues)))),
    )


def a2_internal_heat_trace(t: float) -> float:
    if t <= 0.0:
        raise ValueError("t must be positive")
    eigenvalues = a2_transport_laplacian_eigenvalues()
    return float(np.sum(np.exp(-t * eigenvalues)))


@lru_cache(maxsize=None)
def a2_curved_product_profile(name: str) -> A2CurvedProductProfile:
    external = external_operator_profile(name)
    internal = a2_internal_profile()
    external_trace = int(round(external.trace_dk_squared))
    return A2CurvedProductProfile(
        external_name=name,
        total_dimension=external.total_chain_dim * internal.total_dimension,
        spectral_gap=internal.spectral_gap,
        zero_modes=0,
        trace_product=(
            internal.total_dimension * external_trace
            + external.total_chain_dim * internal.trace_laplacian
        ),
    )


def a2_product_heat_trace_factorized(name: str, t: float) -> float:
    return external_heat_trace(name, t) * a2_internal_heat_trace(t)


def a2_product_heat_trace_direct(name: str, t: float) -> float:
    external = external_dirac_kahler_squared_eigenvalues(name)
    internal = a2_transport_laplacian_eigenvalues()
    eigenvalues = (external[:, None] + internal[None, :]).reshape(-1)
    return float(np.sum(np.exp(-t * eigenvalues)))


@lru_cache(maxsize=1)
def build_product_heat_checks(
    names: tuple[str, ...] = ("CP2", "K3"),
    t_values: tuple[float, ...] = (0.05, 0.1, 0.2),
) -> tuple[ProductHeatCheck, ...]:
    checks = []
    for name in names:
        for t in t_values:
            factorized = a2_product_heat_trace_factorized(name, t)
            direct = a2_product_heat_trace_direct(name, t)
            checks.append(
                ProductHeatCheck(
                    external_name=name,
                    t=t,
                    external_heat_trace=external_heat_trace(name, t),
                    a2_internal_heat_trace=a2_internal_heat_trace(t),
                    factorized_product_heat_trace=factorized,
                    direct_product_heat_trace=direct,
                    abs_error=abs(factorized - direct),
                )
            )
    return tuple(checks)


def a2_product_chain_density_limit() -> Fraction:
    return Fraction(a2_internal_profile().total_dimension) * universal_chain_density_limit()


def a2_product_trace_density_limit() -> Fraction:
    internal = a2_internal_profile()
    return (
        Fraction(internal.total_dimension) * universal_trace_density_limit()
        + Fraction(internal.trace_laplacian) * universal_chain_density_limit()
    )


@lru_cache(maxsize=1)
def build_curved_a2_transport_product_summary() -> dict[str, Any]:
    internal = a2_internal_profile()
    cp2 = a2_curved_product_profile("CP2")
    k3 = a2_curved_product_profile("K3")
    checks = build_product_heat_checks()
    return {
        "status": "ok",
        "a2_internal_profile": internal.to_dict(),
        "curved_product_profiles": [cp2.to_dict(), k3.to_dict()],
        "product_heat_checks": [check.to_dict() for check in checks],
        "density_limits": {
            "a2_product_chain_density_per_top_simplex": _fraction_dict(a2_product_chain_density_limit()),
            "a2_product_trace_per_top_simplex": _fraction_dict(a2_product_trace_density_limit()),
            "product_zero_modes_vanish_exactly": True,
        },
        "bridge_verdict": (
            "The native A2 transport local system now pairs directly with the "
            "explicit curved 4D side. Its positive internal Laplacian has exact "
            "spectrum 24, 33, 48 with gap 24, and its product heat traces with "
            "the explicit CP2_9 and K3_16 Hodge/Dirac-Kahler spectra factorize "
            "exactly. This yields exact curved-product dimensions, traces, and "
            "refined local-density limits 10800/19 and 423000/19 per top simplex."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_a2_transport_product_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
