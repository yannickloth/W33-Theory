"""Refinement-family heat-trace bridge for the external 4D torus.

This module keeps the claim narrow and defensible:

1. The scaled discrete 4-torus `(C_n)^4` gives a genuine external refinement
   family with parameter `n`.
2. For fixed positive `t`, its heat trace converges to the continuum flat
   4-torus heat trace.
3. Because the almost-commutative product square factorizes exactly, the W(3,3)
   internal finite factor multiplies this convergence without changing the
   external 4D role.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from math import exp, pi, sin
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_tomotope_ac_bridge import internal_heat_trace


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_torus_refinement_bridge_summary.json"


@dataclass(frozen=True)
class HeatTraceComparison:
    n: int
    t: float
    discrete_torus4: float
    continuum_torus4: float
    external_abs_error: float
    product_abs_error: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def discrete_circle_heat_trace(n: int, t: float) -> float:
    """Heat trace of `n^2 * Delta_{C_n}` on the unit-length circle mesh."""

    _validate_positive_int("n", n)
    total = 0.0
    for k in range(n):
        lam = (n**2) * 4.0 * (sin(pi * k / n) ** 2)
        total += exp(-t * lam)
    return total


def continuum_circle_heat_trace(t: float, modes: int = 24) -> float:
    """Truncated continuum heat trace on the unit circle."""

    _validate_positive_int("modes", modes)
    return sum(exp(-4.0 * (pi**2) * t * (m**2)) for m in range(-modes, modes + 1))


def discrete_torus4_heat_trace(n: int, t: float) -> float:
    one_d = discrete_circle_heat_trace(n, t)
    return one_d**4


def continuum_torus4_heat_trace(t: float, modes: int = 24) -> float:
    one_d = continuum_circle_heat_trace(t, modes=modes)
    return one_d**4


def product_heat_trace_discrete(n: int, t: float) -> float:
    return discrete_torus4_heat_trace(n, t) * internal_heat_trace(t)


def product_heat_trace_continuum(t: float, modes: int = 24) -> float:
    return continuum_torus4_heat_trace(t, modes=modes) * internal_heat_trace(t)


def build_heat_trace_comparisons(
    n_values: tuple[int, ...] = (8, 12, 16, 24),
    t_values: tuple[float, ...] = (0.05, 0.1, 0.2),
    modes: int = 24,
) -> tuple[HeatTraceComparison, ...]:
    comparisons = []
    for t in t_values:
        continuum = continuum_torus4_heat_trace(t, modes=modes)
        continuum_product = product_heat_trace_continuum(t, modes=modes)
        for n in n_values:
            discrete = discrete_torus4_heat_trace(n, t)
            product = product_heat_trace_discrete(n, t)
            comparisons.append(
                HeatTraceComparison(
                    n=n,
                    t=t,
                    discrete_torus4=discrete,
                    continuum_torus4=continuum,
                    external_abs_error=abs(discrete - continuum),
                    product_abs_error=abs(product - continuum_product),
                )
            )
    return tuple(comparisons)


def build_refinement_summary(
    n_values: tuple[int, ...] = (8, 12, 16, 24),
    t_values: tuple[float, ...] = (0.05, 0.1, 0.2),
    modes: int = 24,
) -> dict[str, Any]:
    comparisons = build_heat_trace_comparisons(
        n_values=n_values,
        t_values=t_values,
        modes=modes,
    )
    return {
        "status": "ok",
        "external_family": "(C_n)^4 with n^2-rescaled graph Laplacian",
        "internal_factor": "W33 finite Dirac-square heat trace multiplier",
        "comparisons": [row.to_dict() for row in comparisons],
        "verdict": (
            "For fixed positive t, the scaled discrete 4-torus heat trace moves "
            "toward the continuum 4-torus heat trace as n grows across the tested "
            "range. The W33 internal factor inherits the same convergence exactly "
            "by product factorization."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_refinement_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
