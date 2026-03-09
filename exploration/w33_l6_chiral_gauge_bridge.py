"""Chirality-preserving l6 gauge dressing on the three-generation Yukawa seed.

The corrected l6 table is the first exact gauge-return rung. On the spinor
sector its A2 and Cartan pieces preserve chirality, so the natural next test is
an infinitesimal chiral dressing of the generation-diagonal induced Yukawa
branch.

What is implemented:
  - extract the exact chirality-preserving l6 modes on the 48 spinor states;
  - lift the exact 8x8 induced H_2/Hbar_2 Yukawas to a 24x24 three-generation
    seed by diagonal replication;
  - solve the real least-squares bridge in delta Y = L Y - Y R against the full
    SU(3)xSU(2) order-one residual on the 48-spinor Dirac operator;
  - record the exact linear-response rank obstruction.

What is established:
  - the 14-mode l6 chiral family has response rank 9, while the augmented
    system has rank 10, so exact cancellation is impossible in this linearized
    l6 family;
  - the optimal bridge lowers the total strict residual from 3.5237290853 to
    0.8266952645;
  - on the generation-diagonal seed the optimal fit uses only Cartan modes; all
    A2 coefficients vanish;
  - the bridged quark blocks lift from rank 6 to rank 9 on the 24x24
    three-generation space while preserving support counts.

What is not claimed:
  - a full non-linear gauge-orbit optimization;
  - a final Standard Model quark Yukawa theorem;
  - the missing 4D refinement/scaling bridge.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from w33_induced_quark_yukawa import (
    DEFAULT_BACKGROUND_COEFFS,
    _projected_yukawa_8x8_numpy,
)
from w33_l6_exceptional_gauge_return import (
    _bracket,
    _l6_scan,
    _state_sc_indices_spinor,
    _structure_data,
)
from w33_quark_firewall_obstruction import (
    _full_color_generator_16,
    _full_weak_generator_16,
)


FLOAT_TOL = 1e-10
LEFT_POSITIONS_48 = tuple(i for g in range(3) for i in range(16 * g, 16 * g + 8))
RIGHT_POSITIONS_48 = tuple(
    i for g in range(3) for i in range(16 * g + 8, 16 * g + 16)
)
QUARK_LEFT_ROWS_24 = tuple(i for g in range(3) for i in range(8 * g, 8 * g + 6))
UP_RIGHT_COLS_24 = tuple(i for g in range(3) for i in range(8 * g, 8 * g + 3))
DOWN_RIGHT_COLS_24 = tuple(i for g in range(3) for i in range(8 * g + 3, 8 * g + 6))


@dataclass(frozen=True)
class L6ChiralGaugeBridgeBlock:
    """Before/after bridge data for one three-generation Yukawa block."""

    original_residual_norm: float
    bridged_residual_norm: float
    original_full_rank: int
    bridged_full_rank: int
    original_quark_rank: int
    bridged_quark_rank: int
    support_count: int


@dataclass(frozen=True)
class L6ChiralGaugeBridgeCertificate:
    """Packaged l6 chiral gauge bridge and its linear-response obstruction."""

    mode_indices: tuple[int, ...]
    a2_mode_indices: tuple[int, ...]
    cartan_mode_indices: tuple[int, ...]
    zero_response_mode_indices: tuple[int, ...]
    response_rank: int
    effective_mode_count: int
    augmented_rank: int
    active_mode_indices: tuple[int, ...]
    active_a2_mode_indices: tuple[int, ...]
    active_cartan_mode_indices: tuple[int, ...]
    coefficients: tuple[float, ...]
    original_total_residual_norm: float
    bridged_total_residual_norm: float
    residual_improvement_factor: float
    residual_reduction_fraction: float
    a2_coefficients_all_zero: bool
    up_block: L6ChiralGaugeBridgeBlock
    down_block: L6ChiralGaugeBridgeBlock
    support_preserved: bool
    route_interpretation: str


def _blockdiag3(operator_16: np.ndarray) -> np.ndarray:
    out = np.zeros((48, 48), dtype=complex)
    for generation in range(3):
        start = 16 * generation
        out[start : start + 16, start : start + 16] = operator_16
    return out


@lru_cache(maxsize=1)
def _full_weak_generators_48() -> tuple[np.ndarray, ...]:
    return tuple(
        _blockdiag3(_full_weak_generator_16(name))
        for name in ("sigma_x", "sigma_y", "sigma_z")
    )


@lru_cache(maxsize=1)
def _full_color_generators_48() -> tuple[np.ndarray, ...]:
    return tuple(
        _blockdiag3(_full_color_generator_16(name))
        for name in (
            "lambda_1",
            "lambda_2",
            "lambda_3",
            "lambda_4",
            "lambda_5",
            "lambda_6",
            "lambda_7",
            "lambda_8",
        )
    )


@lru_cache(maxsize=1)
def l6_chiral_mode_indices() -> tuple[int, ...]:
    scan = _l6_scan()
    return tuple(int(value) for value in scan["a2_support"] + scan["cartan_support"])


def _mode_sector(output_idx: int) -> str:
    if output_idx in _l6_scan()["a2_support"]:
        return "a2"
    if output_idx in _l6_scan()["cartan_support"]:
        return "cartan"
    raise KeyError(f"Mode {output_idx} is not in the chirality-preserving l6 slice")


@lru_cache(maxsize=None)
def l6_spinor_operator_48(output_idx: int) -> np.ndarray:
    state_sc_indices = _state_sc_indices_spinor()
    sc_to_position = {sc_idx: pos for pos, sc_idx in enumerate(state_sc_indices)}
    idx_grade = _structure_data()["idx_grade"]

    matrix = np.zeros((48, 48), dtype=float)
    for source_idx, source_position in sc_to_position.items():
        for target_idx, coeff in _bracket(output_idx, source_idx):
            if idx_grade.get(target_idx) != "g1":
                continue
            target_position = sc_to_position.get(target_idx)
            if target_position is None:
                continue
            matrix[target_position, source_position] += coeff
    return matrix


@lru_cache(maxsize=None)
def l6_chiral_left_right_blocks(output_idx: int) -> tuple[np.ndarray, np.ndarray]:
    operator = l6_spinor_operator_48(output_idx)
    left = operator[np.ix_(LEFT_POSITIONS_48, LEFT_POSITIONS_48)]
    right = operator[np.ix_(RIGHT_POSITIONS_48, RIGHT_POSITIONS_48)]
    return left, right


@lru_cache(maxsize=None)
def generation_diagonal_induced_yukawa_24(external_slot: str) -> np.ndarray:
    if external_slot not in {"H_2", "Hbar_2"}:
        raise KeyError(f"Unsupported external slot: {external_slot}")

    block = _projected_yukawa_8x8_numpy(external_slot, DEFAULT_BACKGROUND_COEFFS)
    matrix = np.zeros((24, 24), dtype=float)
    for generation in range(3):
        start = 8 * generation
        matrix[start : start + 8, start : start + 8] = block
    return matrix


def full_order_one_residual_vector_48(yukawa_24: np.ndarray) -> np.ndarray:
    """Flatten the strict SU(3)xSU(2) order-one residual on the 48-spinor Dirac."""

    dirac = np.zeros((48, 48), dtype=complex)
    dirac[np.ix_(LEFT_POSITIONS_48, RIGHT_POSITIONS_48)] = yukawa_24
    dirac[np.ix_(RIGHT_POSITIONS_48, LEFT_POSITIONS_48)] = yukawa_24.T

    vectors = []
    for weak in _full_weak_generators_48():
        for color in _full_color_generators_48():
            residual = (dirac @ weak - weak @ dirac) @ color - color @ (
                dirac @ weak - weak @ dirac
            )
            vectors.append(residual.reshape(-1))
    return np.concatenate(vectors)


def _bridge_delta(output_idx: int, yukawa_24: np.ndarray) -> np.ndarray:
    left, right = l6_chiral_left_right_blocks(output_idx)
    return left @ yukawa_24 - yukawa_24 @ right


def _support_count(matrix: np.ndarray) -> int:
    return int(np.count_nonzero(np.abs(matrix) > FLOAT_TOL))


def _quark_rank(matrix: np.ndarray, right_cols: tuple[int, ...]) -> int:
    return int(np.linalg.matrix_rank(matrix[np.ix_(QUARK_LEFT_ROWS_24, right_cols)]))


def _zero_response_mode_indices(
    up_seed: np.ndarray,
    down_seed: np.ndarray,
) -> tuple[int, ...]:
    zero_modes = []
    for output_idx in l6_chiral_mode_indices():
        delta_up = _bridge_delta(output_idx, up_seed)
        delta_down = _bridge_delta(output_idx, down_seed)
        if np.isclose(np.linalg.norm(delta_up), 0.0) and np.isclose(
            np.linalg.norm(delta_down), 0.0
        ):
            zero_modes.append(output_idx)
    return tuple(zero_modes)


def _response_matrix(up_seed: np.ndarray, down_seed: np.ndarray) -> np.ndarray:
    columns = []
    for output_idx in l6_chiral_mode_indices():
        delta_up = _bridge_delta(output_idx, up_seed)
        delta_down = _bridge_delta(output_idx, down_seed)
        columns.append(
            np.concatenate(
                [
                    full_order_one_residual_vector_48(delta_up),
                    full_order_one_residual_vector_48(delta_down),
                ]
            )
        )
    return np.stack(columns, axis=1)


def _bridged_yukawa(
    coefficients: np.ndarray,
    seed: np.ndarray,
) -> np.ndarray:
    bridged = seed.copy()
    for coefficient, output_idx in zip(coefficients, l6_chiral_mode_indices()):
        bridged += coefficient * _bridge_delta(output_idx, seed)
    return bridged


@lru_cache(maxsize=1)
def build_l6_chiral_gauge_bridge_certificate() -> L6ChiralGaugeBridgeCertificate:
    up_seed = generation_diagonal_induced_yukawa_24("H_2")
    down_seed = generation_diagonal_induced_yukawa_24("Hbar_2")

    original_up_residual = full_order_one_residual_vector_48(up_seed)
    original_down_residual = full_order_one_residual_vector_48(down_seed)
    original_total = np.concatenate([original_up_residual, original_down_residual])
    response = _response_matrix(up_seed, down_seed)

    response_real = np.vstack([response.real, response.imag])
    target_real = np.concatenate([-original_total.real, -original_total.imag])
    coefficients, *_ = np.linalg.lstsq(response_real, target_real, rcond=None)

    bridged_up = _bridged_yukawa(coefficients, up_seed)
    bridged_down = _bridged_yukawa(coefficients, down_seed)
    bridged_up_residual = full_order_one_residual_vector_48(bridged_up)
    bridged_down_residual = full_order_one_residual_vector_48(bridged_down)
    bridged_total = np.concatenate([bridged_up_residual, bridged_down_residual])

    mode_indices = l6_chiral_mode_indices()
    a2_indices = tuple(idx for idx in mode_indices if _mode_sector(idx) == "a2")
    cartan_indices = tuple(idx for idx in mode_indices if _mode_sector(idx) == "cartan")
    active_mode_indices = tuple(
        idx for idx, coeff in zip(mode_indices, coefficients) if abs(float(coeff)) > FLOAT_TOL
    )
    active_a2_mode_indices = tuple(idx for idx in active_mode_indices if idx in a2_indices)
    active_cartan_mode_indices = tuple(
        idx for idx in active_mode_indices if idx in cartan_indices
    )

    original_total_norm = float(np.linalg.norm(original_total))
    bridged_total_norm = float(np.linalg.norm(bridged_total))

    up_block = L6ChiralGaugeBridgeBlock(
        original_residual_norm=float(np.linalg.norm(original_up_residual)),
        bridged_residual_norm=float(np.linalg.norm(bridged_up_residual)),
        original_full_rank=int(np.linalg.matrix_rank(up_seed)),
        bridged_full_rank=int(np.linalg.matrix_rank(bridged_up)),
        original_quark_rank=_quark_rank(up_seed, UP_RIGHT_COLS_24),
        bridged_quark_rank=_quark_rank(bridged_up, UP_RIGHT_COLS_24),
        support_count=_support_count(bridged_up),
    )
    down_block = L6ChiralGaugeBridgeBlock(
        original_residual_norm=float(np.linalg.norm(original_down_residual)),
        bridged_residual_norm=float(np.linalg.norm(bridged_down_residual)),
        original_full_rank=int(np.linalg.matrix_rank(down_seed)),
        bridged_full_rank=int(np.linalg.matrix_rank(bridged_down)),
        original_quark_rank=_quark_rank(down_seed, DOWN_RIGHT_COLS_24),
        bridged_quark_rank=_quark_rank(bridged_down, DOWN_RIGHT_COLS_24),
        support_count=_support_count(bridged_down),
    )

    route = (
        "On the generation-diagonal three-family seed, the chirality-preserving "
        "l6 family has 14 candidate modes but only a 9-dimensional response. "
        "The augmented rank rises to 10, so exact closure is impossible at this "
        "linearized l6 stage. The optimal bridge sits entirely in the Cartan "
        "slice, leaves all A2 coefficients at zero, lowers the strict residual "
        "by a factor above 4, and lifts the quark blocks from rank 6 to rank 9."
    )

    return L6ChiralGaugeBridgeCertificate(
        mode_indices=mode_indices,
        a2_mode_indices=a2_indices,
        cartan_mode_indices=cartan_indices,
        zero_response_mode_indices=_zero_response_mode_indices(up_seed, down_seed),
        response_rank=int(np.linalg.matrix_rank(response_real)),
        effective_mode_count=int(np.linalg.matrix_rank(response_real)),
        augmented_rank=int(np.linalg.matrix_rank(np.column_stack([response_real, target_real]))),
        active_mode_indices=active_mode_indices,
        active_a2_mode_indices=active_a2_mode_indices,
        active_cartan_mode_indices=active_cartan_mode_indices,
        coefficients=tuple(float(value) for value in coefficients),
        original_total_residual_norm=original_total_norm,
        bridged_total_residual_norm=bridged_total_norm,
        residual_improvement_factor=original_total_norm / bridged_total_norm,
        residual_reduction_fraction=(original_total_norm - bridged_total_norm)
        / original_total_norm,
        a2_coefficients_all_zero=all(abs(float(coefficients[i])) <= FLOAT_TOL for i in range(len(a2_indices))),
        up_block=up_block,
        down_block=down_block,
        support_preserved=bool(
            _support_count(up_seed) == _support_count(bridged_up)
            and _support_count(down_seed) == _support_count(bridged_down)
        ),
        route_interpretation=route,
    )
