"""Exact barycentric-density bridge for curved 4D refinement families.

This module extracts a clean theorem from the curved external refinement side.
For a 4-dimensional simplicial complex, barycentric subdivision acts linearly on
the f-vector. On the 5-dimensional f-vector space in degree 0..4, the
subdivision matrix has eigenvalues 1, 2, 6, 24, 120.

For the 3-neighborly combinatorial 4-manifold seeds used here, something much
sharper happens: their f-vectors live exactly in the span of the 1-, 6-, and
120-modes. The 2- and 24-modes vanish identically. As a result:

- the Euler-characteristic mode is the eigenvalue-1 piece;
- the only decaying correction is the eigenvalue-6 mode;
- the local 4D density is governed by the universal eigenvalue-120 mode.

This yields exact universal local limits for the external chain density and the
first Dirac-Kahler squared moment per top simplex, together with exact
convergence rates under repeated barycentric refinement.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import factorial
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

from w33_flat_ac_spectral_action import internal_dirac_moments
from w33_minimal_triangulation_bridge import (
    barycentric_subdivision_f_vector,
    cp2_seed,
    k3_seed,
    stirling_second_kind,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_barycentric_density_bridge_summary.json"

Matrix5 = tuple[tuple[int, int, int, int, int], ...]
Vector5 = tuple[Fraction, Fraction, Fraction, Fraction, Fraction]


@dataclass(frozen=True)
class DensitySample:
    step: int
    top_simplices: int
    chain_density_per_top_simplex: Fraction
    trace_density_per_top_simplex: Fraction
    chain_density_abs_error: Fraction
    trace_density_abs_error: Fraction

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "top_simplices": self.top_simplices,
            "chain_density_per_top_simplex": _fraction_dict(self.chain_density_per_top_simplex),
            "trace_density_per_top_simplex": _fraction_dict(self.trace_density_per_top_simplex),
            "chain_density_abs_error": _fraction_dict(self.chain_density_abs_error),
            "trace_density_abs_error": _fraction_dict(self.trace_density_abs_error),
        }


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    return {
        "exact": _fraction_string(value),
        "float": float(value),
    }


def _fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def barycentric_subdivision_matrix() -> Matrix5:
    rows = []
    for j in range(5):
        row = []
        for i in range(5):
            if i < j:
                row.append(0)
                continue
            row.append(factorial(j + 1) * stirling_second_kind(i + 1, j + 1))
        rows.append(tuple(row))
    return tuple(rows)  # type: ignore[return-value]


def eigenvector_for_upper_triangular(matrix: Matrix5, eigenvalue: int) -> Vector5:
    values = [Fraction(0) for _ in range(5)]
    pivot = max(index for index in range(5) if matrix[index][index] == eigenvalue)
    values[pivot] = Fraction(1)
    for row in range(3, -1, -1):
        if row == pivot:
            continue
        total = sum(Fraction(matrix[row][column]) * values[column] for column in range(row + 1, 5))
        values[row] = total / Fraction(eigenvalue - matrix[row][row])
    return tuple(values)  # type: ignore[return-value]


def relevant_eigenmodes() -> dict[int, Vector5]:
    matrix = barycentric_subdivision_matrix()
    return {
        1: (Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0)),
        6: eigenvector_for_upper_triangular(matrix, 6),
        120: eigenvector_for_upper_triangular(matrix, 120),
    }


def neighborly_mode_coefficients(n_vertices: int) -> dict[str, Fraction]:
    n = Fraction(n_vertices)
    return {
        "chi_mode": n * (n * n - 15 * n + 74) / 60,
        "six_mode": -n * (n - 1) * (5 * n - 58) / 114,
        "local_mode": n * (n - 1) * (n - 4) / 10,
    }


def exact_neighborly_f_vector_from_modes(n_vertices: int, steps: int = 0) -> tuple[int, int, int, int, int]:
    coefficients = neighborly_mode_coefficients(n_vertices)
    modes = relevant_eigenmodes()
    vector = [Fraction(0) for _ in range(5)]
    for index in range(5):
        vector[index] = (
            coefficients["chi_mode"] * modes[1][index]
            + coefficients["six_mode"] * (Fraction(6) ** steps) * modes[6][index]
            + coefficients["local_mode"] * (Fraction(120) ** steps) * modes[120][index]
        )
    return tuple(int(entry) for entry in vector)  # type: ignore[return-value]


def total_chain_dimension(f_vector: tuple[int, int, int, int, int]) -> int:
    return sum(f_vector)


def trace_dirac_kahler_squared(f_vector: tuple[int, int, int, int, int]) -> int:
    _, f1, f2, f3, f4 = f_vector
    return 4 * f1 + 6 * f2 + 8 * f3 + 10 * f4


def universal_chain_density_limit() -> Fraction:
    return sum(relevant_eigenmodes()[120], start=Fraction(0))


def universal_trace_density_limit() -> Fraction:
    _, f1, f2, f3, f4 = relevant_eigenmodes()[120]
    return 4 * f1 + 6 * f2 + 8 * f3 + 10 * f4


def product_chain_density_limit() -> Fraction:
    internal_dim = int(internal_dirac_moments()["dim"])
    return Fraction(internal_dim) * universal_chain_density_limit()


def product_trace_density_limit() -> Fraction:
    moments = internal_dirac_moments()
    internal_dim = Fraction(int(moments["dim"]))
    internal_trace_d2 = Fraction(int(moments["tr_d2"]))
    return (
        internal_dim * universal_trace_density_limit()
        + internal_trace_d2 * universal_chain_density_limit()
    )


def exact_chain_density_formula(n_vertices: int, step: int) -> Fraction:
    coefficients = neighborly_mode_coefficients(n_vertices)
    local_mode = coefficients["local_mode"]
    return (
        universal_chain_density_limit()
        + Fraction(3) * coefficients["six_mode"] / local_mode / (Fraction(20) ** step)
        + coefficients["chi_mode"] / local_mode / (Fraction(120) ** step)
    )


def exact_trace_density_formula(n_vertices: int, step: int) -> Fraction:
    coefficients = neighborly_mode_coefficients(n_vertices)
    local_mode = coefficients["local_mode"]
    return universal_trace_density_limit() + Fraction(12) * coefficients["six_mode"] / local_mode / (Fraction(20) ** step)


def seed_density_samples(
    n_vertices: int,
    base_f_vector: tuple[int, int, int, int, int],
    max_step: int = 4,
) -> tuple[DensitySample, ...]:
    samples = []
    for step in range(max_step + 1):
        refined = barycentric_subdivision_f_vector(base_f_vector, steps=step)
        top = refined[4]
        chain_density = Fraction(total_chain_dimension(refined), top)
        trace_density = Fraction(trace_dirac_kahler_squared(refined), top)
        samples.append(
            DensitySample(
                step=step,
                top_simplices=top,
                chain_density_per_top_simplex=chain_density,
                trace_density_per_top_simplex=trace_density,
                chain_density_abs_error=abs(chain_density - universal_chain_density_limit()),
                trace_density_abs_error=abs(trace_density - universal_trace_density_limit()),
            )
        )
    return tuple(samples)


def build_curved_barycentric_density_bridge_summary() -> dict[str, Any]:
    modes = relevant_eigenmodes()
    cp2 = cp2_seed()
    k3 = k3_seed()
    cp2_coeffs = neighborly_mode_coefficients(cp2.vertices)
    k3_coeffs = neighborly_mode_coefficients(k3.vertices)
    return {
        "status": "ok",
        "barycentric_subdivision_matrix": barycentric_subdivision_matrix(),
        "relevant_eigenmodes": {
            str(key): [_fraction_string(value) for value in vector]
            for key, vector in modes.items()
        },
        "neighborly_mode_formulas": {
            "chi_mode": "n(n^2 - 15n + 74) / 60",
            "six_mode": "-n(n - 1)(5n - 58) / 114",
            "local_mode": "n(n - 1)(n - 4) / 10",
            "vanishing_modes": [2, 24],
        },
        "universal_local_limits": {
            "external_chain_density_per_top_simplex": _fraction_dict(universal_chain_density_limit()),
            "external_trace_dk_squared_per_top_simplex": _fraction_dict(universal_trace_density_limit()),
            "product_chain_density_per_top_simplex": _fraction_dict(product_chain_density_limit()),
            "product_trace_per_top_simplex": _fraction_dict(product_trace_density_limit()),
            "product_zero_modes_vanish_exactly": True,
        },
        "seed_decompositions": [
            {
                "name": cp2.name,
                "vertices": cp2.vertices,
                "chi_mode": _fraction_dict(cp2_coeffs["chi_mode"]),
                "six_mode": _fraction_dict(cp2_coeffs["six_mode"]),
                "local_mode": _fraction_dict(cp2_coeffs["local_mode"]),
                "density_samples": [sample.to_dict() for sample in seed_density_samples(cp2.vertices, cp2.f_vector)],
            },
            {
                "name": k3.name,
                "vertices": k3.vertices,
                "chi_mode": _fraction_dict(k3_coeffs["chi_mode"]),
                "six_mode": _fraction_dict(k3_coeffs["six_mode"]),
                "local_mode": _fraction_dict(k3_coeffs["local_mode"]),
                "density_samples": [sample.to_dict() for sample in seed_density_samples(k3.vertices, k3.f_vector)],
            },
        ],
        "bridge_verdict": (
            "The curved 4D barycentric refinement family now has an exact mode "
            "decomposition. For every 3-neighborly 4-manifold seed, the f-vector "
            "splits into a topological eigenvalue-1 mode, a decaying eigenvalue-6 "
            "mode, and a universal local eigenvalue-120 mode, with the 2- and "
            "24-modes absent. Therefore the external chain density and the first "
            "Dirac-Kahler squared moment per top simplex converge exactly to the "
            "universal limits 120/19 and 860/19, while Euler characteristic stays "
            "seed-specific and topological. This is the first exact local-density "
            "theorem in the curved 4D refinement program."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_barycentric_density_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
