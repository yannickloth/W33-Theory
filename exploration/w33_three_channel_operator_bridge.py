"""Exact three-channel operator calculus bridge for recent hard-computation phases.

The recent hard-computation phases on W(3,3) cover clustering, Cayley-Hamilton,
spectral moments, perturbation theory, random matrices, connectivity, spectral
geometry, resistance distance, spectral gaps, homomorphisms, and partitioning.
Taken phase-by-phase, that looks like a large pile of unrelated facts.

The exact structural reason they cohere is simpler:

1. the W(3,3) adjacency matrix A has exactly three eigenvalues 12, 2, -4;
2. therefore every spectral/operator expression f(A) lies in the 3-dimensional
   Bose-Mesner algebra span{I, A, J};
3. every such kernel is tri-local: one value on the diagonal, one on edges,
   one on non-edges.

This module packages that as a reusable bridge theorem and recovers several of
the recent hard-computation invariants from one exact interpolation calculus.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_three_channel_operator_bridge_summary.json"

N = 40
K = 12
R = 2
S = -4


def build_w33_adjacency() -> np.ndarray:
    """Construct the 40-vertex W(3,3) symplectic graph."""
    points: list[tuple[int, int, int, int]] = []
    for a in range(3):
        for b in range(3):
            for c in range(3):
                for d in range(3):
                    v = (a, b, c, d)
                    if v == (0, 0, 0, 0):
                        continue
                    first = next(x for x in v if x != 0)
                    inverse = pow(first, -1, 3)
                    canon = tuple((x * inverse) % 3 for x in v)
                    if canon not in points:
                        points.append(canon)

    adjacency = np.zeros((N, N), dtype=int)
    for i in range(N):
        for j in range(i + 1, N):
            u, v = points[i], points[j]
            omega = (u[0] * v[1] - u[1] * v[0] + u[2] * v[3] - u[3] * v[2]) % 3
            if omega == 0:
                adjacency[i, j] = adjacency[j, i] = 1
    return adjacency


def _coerce_fraction(value: Fraction | int | float) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    return Fraction(value).limit_denominator()


def interpolate_three_channel(
    value_at_12: Fraction | int | float,
    value_at_2: Fraction | int | float,
    value_at_minus_4: Fraction | int | float,
) -> tuple[Fraction, Fraction, Fraction]:
    """Return coefficients (x, y, z) with f(A) = x I + y A + z J."""
    f12 = _coerce_fraction(value_at_12)
    f2 = _coerce_fraction(value_at_2)
    fm4 = _coerce_fraction(value_at_minus_4)
    x = (2 * f2 + fm4) / 3
    y = (f2 - fm4) / 6
    z = (3 * f12 - 8 * f2 + 5 * fm4) / 120
    return x, y, z


def coefficient_matrix(
    coefficients: tuple[Fraction, Fraction, Fraction],
    adjacency: np.ndarray | None = None,
) -> np.ndarray:
    if adjacency is None:
        adjacency = build_w33_adjacency()
    identity = np.eye(adjacency.shape[0], dtype=float)
    ones = np.ones_like(adjacency, dtype=float)
    x, y, z = coefficients
    return float(x) * identity + float(y) * adjacency.astype(float) + float(z) * ones


def three_channel_entry_values(
    coefficients: tuple[Fraction, Fraction, Fraction],
) -> dict[str, str]:
    x, y, z = coefficients
    return {
        "diagonal": str(x + z),
        "edge": str(y + z),
        "nonedge": str(z),
    }


def spectral_projector_coefficients() -> dict[str, tuple[Fraction, Fraction, Fraction]]:
    return {
        "E0": interpolate_three_channel(1, 0, 0),
        "E1": interpolate_three_channel(0, 1, 0),
        "E2": interpolate_three_channel(0, 0, 1),
        "E_nonnegative": interpolate_three_channel(1, 1, 0),
    }


def laplacian_pseudoinverse_coefficients() -> tuple[Fraction, Fraction, Fraction]:
    return interpolate_three_channel(Fraction(0, 1), Fraction(1, 10), Fraction(1, 16))


def random_walk_power_coefficients(step: int) -> tuple[Fraction, Fraction, Fraction]:
    return interpolate_three_channel(
        Fraction(1, 1),
        Fraction(1, 6**step),
        Fraction((-1) ** step, 3**step),
    )


def resolvent_coefficients(z_value: Fraction | int) -> tuple[Fraction, Fraction, Fraction]:
    z = _coerce_fraction(z_value)
    return interpolate_three_channel(
        Fraction(1, z - 12),
        Fraction(1, z - 2),
        Fraction(1, z + 4),
    )


def adjacency_moment(moment: int) -> int:
    return 12**moment + 24 * 2**moment + 15 * ((-4) ** moment)


@lru_cache(maxsize=1)
def build_three_channel_operator_summary() -> dict[str, Any]:
    adjacency = build_w33_adjacency()
    identity = np.eye(N, dtype=float)
    ones = np.ones((N, N), dtype=float)

    projector_coeffs = spectral_projector_coefficients()
    e0 = coefficient_matrix(projector_coeffs["E0"], adjacency)
    e1 = coefficient_matrix(projector_coeffs["E1"], adjacency)
    e2 = coefficient_matrix(projector_coeffs["E2"], adjacency)

    lplus_coeffs = laplacian_pseudoinverse_coefficients()
    random_walk_6_coeffs = random_walk_power_coefficients(6)
    resolvent_5_coeffs = resolvent_coefficients(5)

    lplus_entry = three_channel_entry_values(lplus_coeffs)
    positive_entry = three_channel_entry_values(projector_coeffs["E_nonnegative"])

    kemeny = Fraction(24, 1) / Fraction(5, 6) + Fraction(15, 1) / Fraction(4, 3)
    resistance_adj = Fraction(13, 80)
    resistance_non = Fraction(7, 40)

    phase_window = {
        "CIII-CVII": [
            "spectral clustering",
            "Cayley algebraic structure",
            "graph decomposition",
            "spectral moments",
            "perturbation theory",
        ],
        "CVIII-CXII": [
            "random matrix theory",
            "spectral geometry",
            "linear algebra",
            "extremal combinatorics",
            "polynomial methods",
        ],
        "CXIII-CXVII": [
            "connectivity and flow",
            "spectral bounds",
            "automorphism",
            "covering",
            "incidence geometry",
        ],
        "CXVIII-CXXII": [
            "resistance distance",
            "Cayley-Hamilton applications",
            "spectral gap",
            "graph homomorphism",
            "spectral partitioning",
        ],
    }

    return {
        "status": "ok",
        "graph": {
            "vertices": N,
            "degree": K,
            "edges": int(np.sum(adjacency) // 2),
            "spectrum": {"12": 1, "2": 24, "-4": 15},
            "minimal_polynomial": "x^3 - 10x^2 - 32x + 96",
            "srg_identity": "A^2 = -2A + 8I + 4J",
        },
        "operator_calculus": {
            "basis": ["I", "A", "J"],
            "interpolation_formula": {
                "x": "(2 f(2) + f(-4)) / 3",
                "y": "(f(2) - f(-4)) / 6",
                "z": "(3 f(12) - 8 f(2) + 5 f(-4)) / 120",
            },
            "every_kernel_is_three_valued": True,
            "three_entry_classes": ["diagonal", "edge", "nonedge"],
            "phase_window": phase_window,
        },
        "spectral_projectors": {
            "E0_rank": int(round(np.trace(e0))),
            "E1_rank": int(round(np.trace(e1))),
            "E2_rank": int(round(np.trace(e2))),
            "positive_projector_entry_values": positive_entry,
        },
        "moment_bridge": {
            "M2": adjacency_moment(2),
            "M3": adjacency_moment(3),
            "M4": adjacency_moment(4),
            "M5": adjacency_moment(5),
            "M6": adjacency_moment(6),
        },
        "resistance_bridge": {
            "laplacian_pseudoinverse_coefficients": {
                "I": str(lplus_coeffs[0]),
                "A": str(lplus_coeffs[1]),
                "J": str(lplus_coeffs[2]),
            },
            "laplacian_pseudoinverse_entry_values": lplus_entry,
            "effective_resistance_adjacent": str(resistance_adj),
            "effective_resistance_nonadjacent": str(resistance_non),
            "kirchhoff_index": "267/2",
            "kemeny_constant": str(kemeny),
        },
        "mixing_bridge": {
            "random_walk_eigenvalues": {"1": 1, "1/6": 24, "-1/3": 15},
            "step_6_coefficients": {
                "I": str(random_walk_6_coeffs[0]),
                "A": str(random_walk_6_coeffs[1]),
                "J": str(random_walk_6_coeffs[2]),
            },
            "step_6_entry_values": three_channel_entry_values(random_walk_6_coeffs),
            "max_nontrivial_abs_eigenvalue": "1/3",
            "exact_mixing_rate": "1/3",
        },
        "resolvent_bridge": {
            "z": 5,
            "coefficients": {
                "I": str(resolvent_5_coeffs[0]),
                "A": str(resolvent_5_coeffs[1]),
                "J": str(resolvent_5_coeffs[2]),
            },
            "entry_values": three_channel_entry_values(resolvent_5_coeffs),
        },
        "bridge_verdict": (
            "The recent hard-computation phase stack is controlled by one exact "
            "three-channel operator calculus: because W(3,3) has only the three "
            "eigenvalues 12, 2, -4, every spectral kernel f(A) collapses to "
            "span{I, A, J} and therefore has exactly three entry values "
            "(diagonal / edge / non-edge). Spectral clustering, moments, "
            "perturbative resolvents, resistance distance, mixing, and "
            "partitioning are therefore not independent scraps; they are one "
            "rigid tri-local propagator package on the finite internal geometry."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_three_channel_operator_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
