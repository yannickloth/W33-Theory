"""Almost-commutative internal candidate on the W(3,3) spinor sector.

This module upgrades the spinor-only diagnostics to an explicit candidate
representation of A_F = C (+) H (+) M_3(C) on the exact 16-spinor sector.

It also decomposes the exact Higgs families into three pieces:
  - SM-type leptonic Yukawa support;
  - a weak/color-clean but hypercharge-wrong singlet swap;
  - leptoquark contamination, which is exactly the source of the weak/color
    sample order-one residual in the H_1 and Hbar_1 directions.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

import numpy as np

from w33_finite_spectral_triple import quaternion_matrix
from w33_fermionic_connes_sector import (
    HIGGS_SLOT_NAMES,
    color_generator_names,
    color_generator_16,
    fermionic_dirac_from_yukawa_16,
    higgs_yukawa_slices_8x8,
    left_spinor_basis,
    right_spinor_basis,
    sample_order_one_residual_norm,
    weak_generator_names,
    weak_generator_16,
)


LEFT_DIM = 8
RIGHT_DIM = 8
SPINOR_DIM = 16
UPLIKE_FAMILY = ("H_1", "H_2")
DOWNLIKE_FAMILY = ("Hbar_1", "Hbar_2")
UPLIKE_CHARGE = Fraction(1, 2)
DOWNLIKE_CHARGE = Fraction(-1, 2)


@dataclass(frozen=True)
class AlmostCommutativeCandidate:
    """Executable internal-geometry candidate on the spinor 16."""

    left_basis_slots: tuple[str, ...]
    right_basis_slots: tuple[str, ...]
    up_family_slots: tuple[str, ...]
    down_family_slots: tuple[str, ...]
    right_complex_charge_signs: tuple[int, ...]
    weak_clean_slots: tuple[str, ...]


def _zeros() -> np.ndarray:
    return np.zeros((LEFT_DIM, RIGHT_DIM), dtype=np.int64)


def _left_row_indices(sm: str) -> tuple[int, ...]:
    return tuple(
        idx for idx, state in enumerate(left_spinor_basis()) if state.sm == sm
    )


def _right_col_indices(sm: str) -> tuple[int, ...]:
    return tuple(
        idx for idx, state in enumerate(right_spinor_basis()) if state.sm == sm
    )


@lru_cache(maxsize=1)
def right_complex_charge_signs() -> tuple[int, ...]:
    """Standard-model-like complex embedding: up/neutrino vs down/electron."""

    signs = []
    for state in right_spinor_basis():
        if state.sm in {"u_c", "nu_c"}:
            signs.append(1)
        elif state.sm in {"d_c", "e_c"}:
            signs.append(-1)
        else:
            raise ValueError(f"Unexpected right-handed field {state.sm}")
    return tuple(signs)


def left_module_action_16(
    quaternion_alpha: complex,
    quaternion_beta: complex,
    color_matrix: np.ndarray | None = None,
) -> np.ndarray:
    """Left action of the H and M_3(C) factors on the spinor 16."""

    if color_matrix is None:
        color_matrix = np.eye(3, dtype=complex)
    color_matrix = np.asarray(color_matrix, dtype=complex)
    if color_matrix.shape != (3, 3):
        raise ValueError("color_matrix must be 3x3")

    quaternion = quaternion_matrix(quaternion_alpha, quaternion_beta)
    q_block = np.kron(color_matrix, quaternion)
    l_block = quaternion
    left = np.block(
        [
            [q_block, np.zeros((6, 2), dtype=complex)],
            [np.zeros((2, 6), dtype=complex), l_block],
        ]
    )
    return np.block(
        [
            [left, np.zeros((LEFT_DIM, RIGHT_DIM), dtype=complex)],
            [np.zeros((RIGHT_DIM, LEFT_DIM), dtype=complex), np.eye(RIGHT_DIM, dtype=complex)],
        ]
    )


def right_module_action_16(
    lambda_value: complex,
    color_matrix: np.ndarray | None = None,
) -> np.ndarray:
    """Right action of the C and M_3(C) factors on the spinor 16."""

    if color_matrix is None:
        color_matrix = np.eye(3, dtype=complex)
    color_matrix = np.asarray(color_matrix, dtype=complex)
    if color_matrix.shape != (3, 3):
        raise ValueError("color_matrix must be 3x3")

    anti_color = np.conjugate(color_matrix)
    lambda_up = complex(lambda_value)
    lambda_down = np.conjugate(lambda_up)
    right = np.block(
        [
            [lambda_up * anti_color, np.zeros((3, 3), dtype=complex), np.zeros((3, 1), dtype=complex), np.zeros((3, 1), dtype=complex)],
            [np.zeros((3, 3), dtype=complex), lambda_down * anti_color, np.zeros((3, 1), dtype=complex), np.zeros((3, 1), dtype=complex)],
            [np.zeros((1, 3), dtype=complex), np.zeros((1, 3), dtype=complex), np.array([[lambda_down]], dtype=complex), np.zeros((1, 1), dtype=complex)],
            [np.zeros((1, 3), dtype=complex), np.zeros((1, 3), dtype=complex), np.zeros((1, 1), dtype=complex), np.array([[lambda_up]], dtype=complex)],
        ]
    )
    return np.block(
        [
            [np.eye(LEFT_DIM, dtype=complex), np.zeros((LEFT_DIM, RIGHT_DIM), dtype=complex)],
            [np.zeros((RIGHT_DIM, LEFT_DIM), dtype=complex), right],
        ]
    )


def u1_complex_generator_16() -> np.ndarray:
    """Diagonal generator for the complex C factor on the right singlet sector."""

    right = np.diag(right_complex_charge_signs()).astype(complex)
    return np.block(
        [
            [np.eye(LEFT_DIM, dtype=complex), np.zeros((LEFT_DIM, RIGHT_DIM), dtype=complex)],
            [np.zeros((RIGHT_DIM, LEFT_DIM), dtype=complex), right],
        ]
    )


def _project_slot_matrix(slot: str, row_mask: tuple[int, ...], col_mask: tuple[int, ...]) -> np.ndarray:
    projected = _zeros()
    matrix = higgs_yukawa_slices_8x8()[slot]
    for row in row_mask:
        for col in col_mask:
            projected[row, col] = matrix[row, col]
    return projected


def family_sm_leptonic_projection(family_slots: tuple[str, str]) -> dict[str, np.ndarray]:
    if family_slots == UPLIKE_FAMILY:
        cols = _right_col_indices("nu_c")
    elif family_slots == DOWNLIKE_FAMILY:
        cols = _right_col_indices("e_c")
    else:
        raise ValueError(f"Unknown family {family_slots}")
    rows = _left_row_indices("L")
    return {slot: _project_slot_matrix(slot, rows, cols) for slot in family_slots}


def family_singlet_swap_projection(family_slots: tuple[str, str]) -> dict[str, np.ndarray]:
    if family_slots == UPLIKE_FAMILY:
        cols = _right_col_indices("e_c")
    elif family_slots == DOWNLIKE_FAMILY:
        cols = _right_col_indices("nu_c")
    else:
        raise ValueError(f"Unknown family {family_slots}")
    rows = _left_row_indices("L")
    return {slot: _project_slot_matrix(slot, rows, cols) for slot in family_slots}


def family_leptoquark_projection(family_slots: tuple[str, str]) -> dict[str, np.ndarray]:
    q_rows = _left_row_indices("Q")
    l_rows = _left_row_indices("L")
    projected = {}

    for slot in family_slots:
        matrix = _zeros()
        if family_slots == UPLIKE_FAMILY:
            for col in _right_col_indices("nu_c"):
                for row in q_rows:
                    matrix[row, col] = higgs_yukawa_slices_8x8()[slot][row, col]
            for col in _right_col_indices("u_c"):
                for row in l_rows:
                    matrix[row, col] = higgs_yukawa_slices_8x8()[slot][row, col]
        elif family_slots == DOWNLIKE_FAMILY:
            for col in _right_col_indices("e_c"):
                for row in q_rows:
                    matrix[row, col] = higgs_yukawa_slices_8x8()[slot][row, col]
            for col in _right_col_indices("d_c"):
                for row in l_rows:
                    matrix[row, col] = higgs_yukawa_slices_8x8()[slot][row, col]
        else:
            raise ValueError(f"Unknown family {family_slots}")
        projected[slot] = matrix
    return projected


def family_exact_decomposition(
    family_slots: tuple[str, str],
) -> dict[str, dict[str, np.ndarray]]:
    exact = {slot: higgs_yukawa_slices_8x8()[slot] for slot in family_slots}
    leptonic = family_sm_leptonic_projection(family_slots)
    singlet_swap = family_singlet_swap_projection(family_slots)
    leptoquark = family_leptoquark_projection(family_slots)
    return {
        "exact": exact,
        "sm_leptonic": leptonic,
        "singlet_swap": singlet_swap,
        "leptoquark": leptoquark,
    }


def _residual_norm_for_matrix(matrix: np.ndarray) -> float:
    dirac = fermionic_dirac_from_yukawa_16(matrix)
    total = 0.0
    for weak_name in weak_generator_names():
        weak = weak_generator_16(weak_name)
        for color_name in color_generator_names():
            color = color_generator_16(color_name)
            residual = (dirac @ weak - weak @ dirac) @ color - color @ (dirac @ weak - weak @ dirac)
            total += float(np.linalg.norm(residual) ** 2)
    return float(np.sqrt(total))


def family_component_residual_norms(
    family_slots: tuple[str, str],
) -> dict[str, dict[str, float]]:
    decomposition = family_exact_decomposition(family_slots)
    return {
        name: {slot: _residual_norm_for_matrix(matrix) for slot, matrix in matrices.items()}
        for name, matrices in decomposition.items()
    }


def higgs_slot_hypercharge(slot: str) -> Fraction:
    if slot in UPLIKE_FAMILY:
        return UPLIKE_CHARGE
    if slot in DOWNLIKE_FAMILY:
        return DOWNLIKE_CHARGE
    raise KeyError(f"Unknown Higgs slot {slot}")


def channel_hypercharge_records(slot: str, matrix: np.ndarray | None = None) -> tuple[tuple[str, str, int, Fraction], ...]:
    """Return exact charge-balance data for nonzero cubic entries."""

    if matrix is None:
        matrix = higgs_yukawa_slices_8x8()[slot]
    records = []
    slot_charge = higgs_slot_hypercharge(slot)
    left_basis = left_spinor_basis()
    right_basis = right_spinor_basis()
    for row, left_state in enumerate(left_basis):
        for col, right_state in enumerate(right_basis):
            coeff = int(matrix[row, col])
            if coeff == 0:
                continue
            charge_sum = left_state.hypercharge + right_state.hypercharge + slot_charge
            records.append((left_state.slot, right_state.slot, coeff, charge_sum))
    return tuple(records)


def all_channel_charge_sums_vanish(slot: str, matrix: np.ndarray | None = None) -> bool:
    return all(charge == 0 for _, _, _, charge in channel_hypercharge_records(slot, matrix))


@lru_cache(maxsize=1)
def build_almost_commutative_candidate() -> AlmostCommutativeCandidate:
    return AlmostCommutativeCandidate(
        left_basis_slots=tuple(state.slot for state in left_spinor_basis()),
        right_basis_slots=tuple(state.slot for state in right_spinor_basis()),
        up_family_slots=UPLIKE_FAMILY,
        down_family_slots=DOWNLIKE_FAMILY,
        right_complex_charge_signs=right_complex_charge_signs(),
        weak_clean_slots=tuple(
            slot for slot in HIGGS_SLOT_NAMES if np.isclose(sample_order_one_residual_norm(slot), 0.0)
        ),
    )
