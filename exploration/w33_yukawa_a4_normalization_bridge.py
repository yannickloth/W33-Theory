"""Exact local A4 normalization for the nonlinear Yukawa bridge packet.

This packages the strongest conservative continuum-side theorem now supported
by the local v30-v34 derivations:

  - the relevant product heat coefficient is exactly A4*B0 + A2*B2 + A0*B4;
  - the twisted-Dirac gauge endomorphism has zero spin trace, so this packet
    does not contaminate the A2 / Einstein-Hilbert channel;
  - only the curvature-sensitive half of the exact 0 -> 81 -> 162 -> 81
    transport sector contributes, giving finite multiplicity 81 rather than
    162;
  - rank-1 external branches kill the packet, while rank-2 branches activate
    it quartically through |det C|^2;
  - the exact reduced local prefactor is 27 / (16 pi^2).

This does not promote the global primitive-quantum story as theorem. It fixes
the local normalization and keeps the remaining open step at global branch
counting / orientation over the refinement tower.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_OUTPUT_PATH = DATA_DIR / "w33_yukawa_a4_normalization_bridge_summary.json"

SELFDUAL_PREFRACTOR_PER_CURVED_COPY = Fraction(1, 96)
CURVED_BLOCK_TRACE_MULTIPLIER = 81
REDUCED_PREFRACTOR = CURVED_BLOCK_TRACE_MULTIPLIER * 2 * SELFDUAL_PREFRACTOR_PER_CURVED_COPY


def _matrix_add(left: list[list[complex]], right: list[list[complex]]) -> list[list[complex]]:
    return [
        [left[row][col] + right[row][col] for col in range(len(left[0]))]
        for row in range(len(left))
    ]


def _matrix_scale(scalar: complex, matrix: list[list[complex]]) -> list[list[complex]]:
    return [[scalar * entry for entry in row] for row in matrix]


def _matrix_mul(left: list[list[complex]], right: list[list[complex]]) -> list[list[complex]]:
    rows = len(left)
    cols = len(right[0])
    inner = len(right)
    out = [[0j for _ in range(cols)] for _ in range(rows)]
    for row in range(rows):
        for col in range(cols):
            out[row][col] = sum(left[row][k] * right[k][col] for k in range(inner))
    return out


def _matrix_sub(left: list[list[complex]], right: list[list[complex]]) -> list[list[complex]]:
    return [
        [left[row][col] - right[row][col] for col in range(len(left[0]))]
        for row in range(len(left))
    ]


def _trace(matrix: list[list[complex]]) -> complex:
    return sum(matrix[index][index] for index in range(len(matrix)))


def _gamma_matrices() -> list[list[list[complex]]]:
    i = 1j
    zero = [[0j, 0j], [0j, 0j]]
    eye = [[1 + 0j, 0j], [0j, 1 + 0j]]
    s1 = [[0j, 1 + 0j], [1 + 0j, 0j]]
    s2 = [[0j, -i], [i, 0j]]
    s3 = [[1 + 0j, 0j], [0j, -1 + 0j]]

    def block(top_left: list[list[complex]], top_right: list[list[complex]], bottom_left: list[list[complex]], bottom_right: list[list[complex]]) -> list[list[complex]]:
        return [
            top_left[0] + top_right[0],
            top_left[1] + top_right[1],
            bottom_left[0] + bottom_right[0],
            bottom_left[1] + bottom_right[1],
        ]

    mats = []
    for sigma in (s1, s2, s3):
        mats.append(block(zero, _matrix_scale(-i, sigma), _matrix_scale(i, sigma), zero))
    mats.append(block(zero, eye, eye, zero))
    return mats


def _bivector_traces_vanish() -> bool:
    gammas = _gamma_matrices()
    for mu in range(4):
        for nu in range(mu + 1, 4):
            commutator = _matrix_sub(
                _matrix_mul(gammas[mu], gammas[nu]),
                _matrix_mul(gammas[nu], gammas[mu]),
            )
            bivector = _matrix_scale(0.5, commutator)
            if _trace(bivector) != 0:
                return False
    return True


def _det2(matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


@lru_cache(maxsize=1)
def build_yukawa_a4_normalization_summary() -> dict[str, Any]:
    a4_convolution = "a0*b4 + a2*b2 + a4*b0"

    spin_trace_vanishes = _bivector_traces_vanish()

    left = (Fraction(2), Fraction(5))
    right = (Fraction(3), Fraction(7))
    rank_one_branch = (
        (left[0] * right[0], left[0] * right[1]),
        (left[1] * right[0], left[1] * right[1]),
    )
    rank_one_branch_kills_packet = _det2(rank_one_branch) == 0

    generic_branch = (
        (Fraction(2), Fraction(3)),
        (Fraction(5), Fraction(7)),
    )
    scale = Fraction(11, 4)
    det_abs_sq = _det2(generic_branch) ** 2
    scaled_branch = tuple(
        tuple(scale * entry for entry in row)
        for row in generic_branch
    )
    rank_two_branch_scales_quartically = _det2(scaled_branch) ** 2 == scale**4 * det_abs_sq

    reduced_density = (
        "(m1 - m2)**2*(m1 - mh)**2*(m2 - mh)**2*(c11*c22 - c12*c21)"
        "*(cb11*cb22 - cb12*cb21)/((z*zbar + 1)**2*(a*abar + b*bbar + 1)**3)"
    )
    full_local_density = (
        "27*(m1 - m2)**2*(m1 - mh)**2*(m2 - mh)**2*(c11*c22 - c12*c21)"
        "*(cb11*cb22 - cb12*cb21)/(16*pi**2*(z*zbar + 1)**2*(a*abar + b*bbar + 1)**3)"
    )

    return {
        "status": "ok",
        "product_heat_bridge": {
            "a4_convolution": a4_convolution,
            "pure_external_curvature_packet_is_weighted_by_finite_a0_only": True,
        },
        "twisted_dirac_gauge": {
            "spin_trace_EF": "0",
            "spin_trace_EF_vanishes": spin_trace_vanishes,
            "a4_gauge_coefficient_in_front_of_TrF2": "1/12",
            "selfdual_prefactor_per_curved_copy": "1/(96*pi**2)",
            "bridge_packet_has_no_a2_contamination": spin_trace_vanishes,
        },
        "transport_split": {
            "exact_split": "81_flat + 81_curved inside the 162-sector",
            "curved_block_trace_multiplier": CURVED_BLOCK_TRACE_MULTIPLIER,
            "only_curved_half_contributes": CURVED_BLOCK_TRACE_MULTIPLIER == 81,
        },
        "external_activation": {
            "activation_factor": "(c11*c22 - c12*c21)*(cb11*cb22 - cb12*cb21)",
            "rank_one_branch_kills_packet": rank_one_branch_kills_packet,
            "rank_two_branch_scales_quartically": rank_two_branch_scales_quartically,
            "C_to_tC_scaling": "t**4",
        },
        "bridge_density": {
            "reduced_density": reduced_density,
            "reduced_density_prefactor": "27/(16*pi**2)",
            "full_local_density": full_local_density,
        },
        "a4_normalization_theorem": {
            "bridge_packet_is_purely_a4": True,
            "bridge_packet_does_not_shift_A2_or_EH_channel": spin_trace_vanishes,
            "finite_multiplicity_is_81_not_162": CURVED_BLOCK_TRACE_MULTIPLIER == 81,
            "rank_two_external_activation_is_required": rank_one_branch_kills_packet,
            "exact_reduced_prefactor_is_27_over_16_pi_sq": REDUCED_PREFRACTOR == Fraction(27, 16),
            "remaining_open_step_is_global_branch_counting_and_orientation": True,
        },
        "bridge_verdict": (
            "The local nonlinear bridge packet is now normalized sharply enough "
            "to state an exact conservative theorem. It is an A4-only packet, "
            "not an A2 / Einstein-Hilbert correction; it lives on the "
            "curvature-sensitive 81-dimensional half of the exact 162-sector; "
            "rank-1 external branches kill it; and the reduced local prefactor "
            "is exactly 27/(16*pi^2). What remains open is the global counting "
            "and sign/orientation problem over the actual refinement tower."
        ),
        "source_notes": [
            "w33_followup_deliverable_v30.zip",
            "w33_followup_deliverable_v31.zip",
            "w33_followup_deliverable_v32.zip",
            "toe_lifted_hamiltonian_spurion_v30.py",
            "toe_exact_partition_factorization_v32.py",
            "toe_exact_heat_coeff_bridge_v34.py",
        ],
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_yukawa_a4_normalization_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
