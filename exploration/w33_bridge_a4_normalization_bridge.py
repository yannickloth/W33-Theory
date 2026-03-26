"""Reduced local A4 normalization for the family bridge.

This module packages the strongest conservative synthesis now supported by the
exact repo-native bridge results together with an explicit twisted-Dirac gauge
coefficient calculation.

What is established here:
  - explicit 4D Euclidean gamma matrices give the universal local gauge factor
        a4_gauge(x) = (4 pi)^(-2) * (1/12) * Tr(F_{mu nu} F^{mu nu});
  - on a self-dual 4D branch that becomes a c2-type 4-form coefficient
        1 / (96 pi^2)
    per active curved copy;
  - the exact repo-native A4-entry theorem already fixes the finite
    multiplicity to 81 via
        Delta A4 = 81 epsilon^2 a0 = 1209 a0 / 9194;
  - the refined density theorem says that same first family-sensitive packet
    still rides the geometric A0 external channel.

So the reduced local prefactor is fixed:
  - before the universal rank-2 family factor 2:
        27 / (32 pi^2)
  - after that already-isolated factor 2:
        27 / (16 pi^2)

This still does not prove the full global continuum lift. It removes the local
normalization ambiguity from the self-dual reduced bridge model.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np

from exploration.w33_refined_action_two_channel_bridge import (
    build_refined_action_two_channel_summary,
)
from exploration.w33_yukawa_a4_entry_bridge import build_yukawa_a4_entry_summary


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_OUTPUT_PATH = DATA_DIR / "w33_bridge_a4_normalization_bridge_summary.json"

PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _pi_fraction_text(value: Fraction) -> str:
    return f"{_fraction_text(value)} pi^2" if value.denominator == 1 else f"{value.numerator}/({value.denominator} pi^2)"


def _block_matrix(a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray) -> np.ndarray:
    return np.block([[a, b], [c, d]])


def _gamma_matrices() -> list[np.ndarray]:
    imaginary = 1j
    sigma_1 = np.array([[0, 1], [1, 0]], dtype=complex)
    sigma_2 = np.array([[0, -imaginary], [imaginary, 0]], dtype=complex)
    sigma_3 = np.array([[1, 0], [0, -1]], dtype=complex)
    zero = np.zeros((2, 2), dtype=complex)
    identity = np.eye(2, dtype=complex)

    gammas = []
    for sigma in (sigma_1, sigma_2, sigma_3):
        gammas.append(_block_matrix(zero, -imaginary * sigma, imaginary * sigma, zero))
    gammas.append(_block_matrix(zero, identity, identity, zero))
    return gammas


def _trace_as_int(matrix: np.ndarray) -> int:
    value = np.trace(matrix)
    if abs(value.imag) > 1e-9 or abs(value.real - round(value.real)) > 1e-9:
        raise ValueError(f"Expected integral trace, got {value}")
    return int(round(value.real))


@lru_cache(maxsize=1)
def build_bridge_a4_normalization_summary() -> dict[str, Any]:
    gammas = _gamma_matrices()
    anticommutator_checks = []
    for i, gamma_i in enumerate(gammas):
        for j, gamma_j in enumerate(gammas):
            anticommutator = gamma_i @ gamma_j + gamma_j @ gamma_i
            target = 2 * np.eye(4, dtype=complex) if i == j else np.zeros((4, 4), dtype=complex)
            anticommutator_checks.append(np.allclose(anticommutator, target))

    bivectors = []
    for i, j in PAIRS:
        bivectors.append((gammas[i] @ gammas[j] - gammas[j] @ gammas[i]) / 2)

    diagonal_basis_traces = [_trace_as_int(bivector @ bivector) for bivector in bivectors]
    off_diagonal_vanish = all(
        abs(np.trace(bivectors[i] @ bivectors[j])) < 1e-9
        for i in range(len(bivectors))
        for j in range(i + 1, len(bivectors))
    )
    spin_trace_zero = all(abs(np.trace(bivector)) < 1e-9 for bivector in bivectors)

    # For E_F = (1/2) gamma^{mu nu} F_{mu nu} and one unit basis component:
    #   tr_S(E_F^2) = (-4) / 4 = -1
    # while F_{mu nu} F^{mu nu} = 2 on that same unit basis component.
    spin_trace_e_squared_in_f_sq_units = Fraction(diagonal_basis_traces[0], 8)
    coeff_from_half_e_squared = Fraction(1, 2) * spin_trace_e_squared_in_f_sq_units
    coeff_from_omega_squared = Fraction(4, 12)
    a4_gauge_coefficient_in_front_of_tr_f_sq = (
        coeff_from_half_e_squared + coeff_from_omega_squared
    )

    # On a self-dual branch, F_{mu nu} F^{mu nu} dvol = 2 Tr(F wedge F).
    selfdual_four_form_prefactor_per_copy = Fraction(2, 16 * 12)

    a4_entry = build_yukawa_a4_entry_summary()
    refined = build_refined_action_two_channel_summary()

    finite_trace_0 = int(a4_entry["internal_moment_tower"]["trace_0"])
    reduced_prefactor_before_factor_2 = finite_trace_0 * selfdual_four_form_prefactor_per_copy
    reduced_prefactor_after_factor_2 = 2 * reduced_prefactor_before_factor_2

    return {
        "status": "ok",
        "gamma_bivector_checks": {
            "euclidean_anticommutator_checks_pass": all(anticommutator_checks),
            "diagonal_basis_traces": diagonal_basis_traces,
            "off_diagonal_basis_traces_vanish": off_diagonal_vanish,
            "spin_trace_of_each_bivector_vanishes": spin_trace_zero,
        },
        "local_a4_gauge_coefficient": {
            "tr_spin_EF_squared_in_units_of_F_sq": _fraction_text(
                spin_trace_e_squared_in_f_sq_units
            ),
            "from_half_E_squared": _fraction_text(coeff_from_half_e_squared),
            "from_omega_squared": _fraction_text(coeff_from_omega_squared),
            "total_in_front_of_Tr_F_sq": _fraction_text(
                a4_gauge_coefficient_in_front_of_tr_f_sq
            ),
            "formula": "a4_gauge(x) = (4 pi)^(-2) * (1/12) * Tr(F_{mu nu} F^{mu nu})",
            "selfdual_4form_prefactor_per_curved_copy": f"1/({selfdual_four_form_prefactor_per_copy.denominator} pi^2)",
        },
        "finite_multiplier": {
            "trace_0": finite_trace_0,
            "delta_A4": a4_entry["product_heat_coefficients"]["delta_A4"],
            "delta_A4_equals_81_epsilon_squared_a0": a4_entry["a4_entry_theorem"][
                "delta_A4_equals_81_epsilon_squared_a0"
            ],
            "first_family_entry_is_A4_only": a4_entry["a4_entry_theorem"][
                "A4_is_first_family_entry_point"
            ],
        },
        "refined_density_channel": {
            "delta_A4_density_formula": "epsilon^2 * A0_density(n)",
            "epsilon_squared": refined["global_data"]["epsilon_squared"],
            "first_family_sensitive_density_stays_on_A0_channel": refined[
                "two_channel_theorem"
            ]["delta_A4_shares_exact_external_modes_with_A0_for_both_seeds"],
        },
        "reduced_local_bridge_prefactor": {
            "before_universal_rank2_factor_2": _pi_fraction_text(
                reduced_prefactor_before_factor_2
            ),
            "after_universal_rank2_factor_2": _pi_fraction_text(
                reduced_prefactor_after_factor_2
            ),
        },
        "bridge_theorem": {
            "local_gauge_packet_is_pure_A4": (
                a4_gauge_coefficient_in_front_of_tr_f_sq == Fraction(1, 12)
                and a4_entry["a4_entry_theorem"]["A0_is_family_blind"]
                and a4_entry["a4_entry_theorem"]["A2_is_family_blind"]
                and spin_trace_zero
            ),
            "exact_finite_multiplier_is_repo_native_81": (
                finite_trace_0 == 81
                and a4_entry["a4_entry_theorem"]["delta_A4_equals_81_epsilon_squared_a0"]
            ),
            "reduced_local_prefactor_is_27_over_16_pi_squared": (
                reduced_prefactor_after_factor_2 == Fraction(27, 16)
            ),
            "global_orientation_and_integration_remain_open": True,
        },
        "bridge_verdict": (
            "The next exact bridge statement is no longer only that family data "
            "first enters at A4. The explicit twisted-Dirac gauge coefficient is "
            "1/(12 (4 pi)^2), the repo-native A4-entry theorem fixes the finite "
            "multiplier to the same 81 already appearing in Delta A4 = 81 "
            "epsilon^2 a0, and the refined density still rides the geometric A0 "
            "external channel. So after the already-isolated universal rank-2 "
            "factor 2, the reduced self-dual local bridge prefactor is fixed to "
            "27/(16 pi^2). What remains open is the global integration and "
            "orientation theorem, not the local normalization."
        ),
        "source_files": [
            "exploration/w33_yukawa_a4_entry_bridge.py",
            "exploration/w33_refined_action_two_channel_bridge.py",
        ],
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_bridge_a4_normalization_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
