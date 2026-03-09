"""Shared-left l4 dressing of the induced quark Dirac sector.

The exact l4 quark self-energy sector proves that the clean quark action first
appears at higher tower level, not inside the raw cubic span. The next question
is whether that exact self-energy image can be turned into a chirality-mixing
quark Dirac/Yukawa correction on the spinor 16.

This module implements the first nontrivial bridge:
  - extract an exact four-element clean l4 quark-self-energy basis;
  - project it to left Q and right (u_c, d_c) blocks on the spinor sector;
  - dress the induced H_2/Hbar_2 quark Yukawas by a shared-left / separate-right
    linear family;
  - solve the least-squares problem against the full SU(3)xSU(2) order-one
    residual on the 16-spinor sector.

What is established:
  - the bridge preserves exact quark support on Q-u_c and Q-d_c only;
  - the strict full-screen quark residual decreases;
  - both quark blocks lift from rank 2 to rank 3.

What is not claimed:
  - exact cancellation of the quark residual;
  - a final Standard Model quark mass theorem;
  - uniqueness of this bridge family.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from w33_fermionic_connes_sector import left_spinor_basis, right_spinor_basis
from w33_induced_quark_yukawa import (
    DEFAULT_BACKGROUND_COEFFS,
    _projected_yukawa_8x8_numpy,
)
from w33_l4_quark_self_energy import (
    CountertermEntry,
    CountertermTerm,
    contracted_l4_operator_27,
)
from w33_quark_firewall_obstruction import (
    full_order_one_residual_norm_16,
    full_order_one_residual_vector_16,
)


FLOAT_TOL = 1e-10
BRIDGE_BASIS_DATA = (
    (
        "ud_23",
        (
            (-1, ("u_c_2", "Tbar_1", "d_c_3")),
            (-1, ("d_c_3", "Tbar_1", "u_c_2")),
            (1, ("d_c_1", "Tbar_2", "u_c_3")),
            (1, ("u_c_1", "Tbar_3", "d_c_2")),
        ),
    ),
    (
        "ud_13",
        (
            (-1, ("u_c_2", "Tbar_1", "d_c_3")),
            (1, ("d_c_1", "Tbar_2", "u_c_3")),
            (-1, ("u_c_3", "Tbar_2", "d_c_1")),
            (1, ("d_c_2", "Tbar_3", "u_c_1")),
        ),
    ),
    (
        "q23_ud23",
        (
            (-1, ("u_c_3", "d_c_1", "Tbar_2")),
            (1, ("d_c_2", "u_c_1", "Tbar_3")),
            (1, ("Q_1_1", "Q_2_2", "T_3")),
            (1, ("Q_1_2", "Q_3_1", "T_2")),
        ),
    ),
    (
        "q13_ud13",
        (
            (-1, ("d_c_3", "u_c_2", "Tbar_1")),
            (-1, ("d_c_2", "u_c_1", "Tbar_3")),
            (-1, ("Q_1_1", "Q_2_2", "T_3")),
            (1, ("Q_2_1", "Q_3_2", "T_1")),
        ),
    ),
)


@dataclass(frozen=True)
class L4DiracBridgeBasisElement:
    """One exact clean l4 quark-self-energy basis element."""

    name: str
    terms: tuple[CountertermTerm, ...]
    entries: tuple[CountertermEntry, ...]


@dataclass(frozen=True)
class BridgedQuarkBlock:
    """Before/after data for one bridged quark Yukawa block."""

    original_residual_norm: float
    bridged_residual_norm: float
    original_rank: int
    bridged_rank: int
    support_count: int
    original_singular_values: tuple[float, ...]
    bridged_singular_values: tuple[float, ...]
    right_coeffs: tuple[float, ...]


@dataclass(frozen=True)
class L4QuarkDiracBridgeCandidate:
    """Packaged l4-to-Dirac bridge candidate on the spinor 16."""

    basis_names: tuple[str, ...]
    basis: tuple[L4DiracBridgeBasisElement, ...]
    shared_left_coeffs: tuple[float, ...]
    up_block: BridgedQuarkBlock
    down_block: BridgedQuarkBlock
    original_total_residual_norm: float
    bridged_total_residual_norm: float
    residual_improvement_factor: float
    residual_reduction_fraction: float
    support_preserved: bool


def _slot_to_local_index() -> dict[str, int]:
    return {state.slot: state.local_index for state in left_spinor_basis() + right_spinor_basis()}


def _basis_matrix_from_terms(
    terms: tuple[tuple[int, tuple[str, str, str]], ...],
) -> np.ndarray:
    total = np.zeros((27, 27), dtype=float)
    for coefficient, ordered_slots in terms:
        total += coefficient * contracted_l4_operator_27(ordered_slots)
    return total


def _counterterm_entries(matrix: np.ndarray) -> tuple[CountertermEntry, ...]:
    slot_by_local = {}
    for state in left_spinor_basis() + right_spinor_basis():
        slot_by_local[state.local_index] = state.slot
    entries = []
    for row_index in range(matrix.shape[0]):
        for col_index in range(matrix.shape[1]):
            value = matrix[row_index, col_index]
            if abs(value) > FLOAT_TOL:
                entries.append(
                    CountertermEntry(
                        row_slot=slot_by_local.get(row_index, f"slot_{row_index}"),
                        col_slot=slot_by_local.get(col_index, f"slot_{col_index}"),
                        value=int(round(value)),
                    )
                )
    return tuple(entries)


@lru_cache(maxsize=1)
def l4_dirac_bridge_basis() -> tuple[L4DiracBridgeBasisElement, ...]:
    basis = []
    for name, raw_terms in BRIDGE_BASIS_DATA:
        terms = tuple(
            CountertermTerm(coefficient=coefficient, ordered_slots=ordered_slots)
            for coefficient, ordered_slots in raw_terms
        )
        matrix = _basis_matrix_from_terms(raw_terms)
        basis.append(
            L4DiracBridgeBasisElement(
                name=name,
                terms=terms,
                entries=_counterterm_entries(matrix),
            )
        )
    return tuple(basis)


def basis_matrix_27(name: str) -> np.ndarray:
    for basis_name, raw_terms in BRIDGE_BASIS_DATA:
        if basis_name == name:
            return _basis_matrix_from_terms(raw_terms)
    raise KeyError(f"Unknown l4 Dirac bridge basis element: {name}")


def _quark_row_indices() -> tuple[int, ...]:
    return tuple(index for index, state in enumerate(left_spinor_basis()) if state.sm == "Q")


def _up_col_indices() -> tuple[int, ...]:
    return tuple(index for index, state in enumerate(right_spinor_basis()) if state.sm == "u_c")


def _down_col_indices() -> tuple[int, ...]:
    return tuple(index for index, state in enumerate(right_spinor_basis()) if state.sm == "d_c")


def _block_from_matrix(matrix: np.ndarray, states: tuple) -> np.ndarray:
    block = np.zeros((len(states), len(states)), dtype=float)
    for row_index, row_state in enumerate(states):
        for col_index, col_state in enumerate(states):
            block[row_index, col_index] = matrix[row_state.local_index, col_state.local_index]
    return block


@lru_cache(maxsize=1)
def _basis_left_right_blocks() -> tuple[tuple[np.ndarray, ...], tuple[np.ndarray, ...], tuple[np.ndarray, ...]]:
    q_states = tuple(state for state in left_spinor_basis() if state.sm == "Q")
    u_states = tuple(state for state in right_spinor_basis() if state.sm == "u_c")
    d_states = tuple(state for state in right_spinor_basis() if state.sm == "d_c")
    q_blocks = []
    u_blocks = []
    d_blocks = []
    for name, _ in BRIDGE_BASIS_DATA:
        matrix = basis_matrix_27(name)
        q_blocks.append(_block_from_matrix(matrix, q_states))
        u_blocks.append(_block_from_matrix(matrix, u_states))
        d_blocks.append(_block_from_matrix(matrix, d_states))
    return tuple(q_blocks), tuple(u_blocks), tuple(d_blocks)


def _embedded_original_up() -> np.ndarray:
    yukawa = np.zeros((8, 8), dtype=float)
    up = _projected_yukawa_8x8_numpy("H_2", DEFAULT_BACKGROUND_COEFFS)
    yukawa[np.ix_(_quark_row_indices(), _up_col_indices())] = up[
        np.ix_(_quark_row_indices(), _up_col_indices())
    ]
    return yukawa


def _embedded_original_down() -> np.ndarray:
    yukawa = np.zeros((8, 8), dtype=float)
    down = _projected_yukawa_8x8_numpy("Hbar_2", DEFAULT_BACKGROUND_COEFFS)
    yukawa[np.ix_(_quark_row_indices(), _down_col_indices())] = down[
        np.ix_(_quark_row_indices(), _down_col_indices())
    ]
    return yukawa


def _solve_shared_left_fit() -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    q_blocks, u_blocks, d_blocks = _basis_left_right_blocks()
    original_up = _embedded_original_up()
    original_down = _embedded_original_down()
    up_block = original_up[np.ix_(_quark_row_indices(), _up_col_indices())]
    down_block = original_down[np.ix_(_quark_row_indices(), _down_col_indices())]

    zero_up = np.zeros_like(full_order_one_residual_vector_16(original_up))
    zero_down = np.zeros_like(full_order_one_residual_vector_16(original_down))

    columns = []
    for q_block in q_blocks:
        up = np.zeros((8, 8), dtype=float)
        down = np.zeros((8, 8), dtype=float)
        up[np.ix_(_quark_row_indices(), _up_col_indices())] = q_block @ up_block
        down[np.ix_(_quark_row_indices(), _down_col_indices())] = q_block @ down_block
        columns.append(
            np.concatenate(
                [
                    full_order_one_residual_vector_16(up),
                    full_order_one_residual_vector_16(down),
                ]
            )
        )
    for u_block in u_blocks:
        up = np.zeros((8, 8), dtype=float)
        up[np.ix_(_quark_row_indices(), _up_col_indices())] = up_block @ u_block
        columns.append(
            np.concatenate([full_order_one_residual_vector_16(up), zero_down])
        )
    for d_block in d_blocks:
        down = np.zeros((8, 8), dtype=float)
        down[np.ix_(_quark_row_indices(), _down_col_indices())] = down_block @ d_block
        columns.append(
            np.concatenate([zero_up, full_order_one_residual_vector_16(down)])
        )

    bridge_matrix = np.stack(columns, axis=1)
    target = -np.concatenate(
        [
            full_order_one_residual_vector_16(original_up),
            full_order_one_residual_vector_16(original_down),
        ]
    )

    # Solve in real form to enforce numerically real bridge coefficients.
    bridge_real = np.vstack([bridge_matrix.real, bridge_matrix.imag])
    target_real = np.concatenate([target.real, target.imag])
    coeffs, *_ = np.linalg.lstsq(bridge_real, target_real, rcond=None)
    return (
        tuple(float(value) for value in coeffs[:4]),
        tuple(float(value) for value in coeffs[4:8]),
        tuple(float(value) for value in coeffs[8:12]),
    )


def bridged_up_quark_yukawa_8x8() -> np.ndarray:
    shared_left, up_right, _ = _solve_shared_left_fit()
    q_blocks, u_blocks, _ = _basis_left_right_blocks()
    bridged = _embedded_original_up().astype(float)
    core = bridged[np.ix_(_quark_row_indices(), _up_col_indices())].copy()
    original = core.copy()
    for coefficient, q_block in zip(shared_left, q_blocks):
        core += coefficient * (q_block @ original)
    for coefficient, u_block in zip(up_right, u_blocks):
        core += coefficient * (original @ u_block)
    bridged[np.ix_(_quark_row_indices(), _up_col_indices())] = core
    return bridged


def bridged_down_quark_yukawa_8x8() -> np.ndarray:
    shared_left, _, down_right = _solve_shared_left_fit()
    q_blocks, _, d_blocks = _basis_left_right_blocks()
    bridged = _embedded_original_down().astype(float)
    core = bridged[np.ix_(_quark_row_indices(), _down_col_indices())].copy()
    original = core.copy()
    for coefficient, q_block in zip(shared_left, q_blocks):
        core += coefficient * (q_block @ original)
    for coefficient, d_block in zip(down_right, d_blocks):
        core += coefficient * (original @ d_block)
    bridged[np.ix_(_quark_row_indices(), _down_col_indices())] = core
    return bridged


@lru_cache(maxsize=1)
def build_l4_quark_dirac_bridge_candidate() -> L4QuarkDiracBridgeCandidate:
    shared_left, up_right, down_right = _solve_shared_left_fit()
    original_up = _embedded_original_up()
    original_down = _embedded_original_down()
    bridged_up = bridged_up_quark_yukawa_8x8()
    bridged_down = bridged_down_quark_yukawa_8x8()

    up_rows = _quark_row_indices()
    up_cols = _up_col_indices()
    down_cols = _down_col_indices()

    original_up_block = original_up[np.ix_(up_rows, up_cols)]
    bridged_up_block = bridged_up[np.ix_(up_rows, up_cols)]
    original_down_block = original_down[np.ix_(up_rows, down_cols)]
    bridged_down_block = bridged_down[np.ix_(up_rows, down_cols)]

    original_total = float(
        np.linalg.norm(
            np.concatenate(
                [
                    full_order_one_residual_vector_16(original_up),
                    full_order_one_residual_vector_16(original_down),
                ]
            )
        )
    )
    bridged_total = float(
        np.linalg.norm(
            np.concatenate(
                [
                    full_order_one_residual_vector_16(bridged_up),
                    full_order_one_residual_vector_16(bridged_down),
                ]
            )
        )
    )

    return L4QuarkDiracBridgeCandidate(
        basis_names=tuple(name for name, _ in BRIDGE_BASIS_DATA),
        basis=l4_dirac_bridge_basis(),
        shared_left_coeffs=shared_left,
        up_block=BridgedQuarkBlock(
            original_residual_norm=full_order_one_residual_norm_16(original_up),
            bridged_residual_norm=full_order_one_residual_norm_16(bridged_up),
            original_rank=int(np.linalg.matrix_rank(original_up_block)),
            bridged_rank=int(np.linalg.matrix_rank(bridged_up_block)),
            support_count=int(np.count_nonzero(np.abs(bridged_up) > FLOAT_TOL)),
            original_singular_values=tuple(
                float(value)
                for value in np.linalg.svd(original_up_block, compute_uv=False)
            ),
            bridged_singular_values=tuple(
                float(value)
                for value in np.linalg.svd(bridged_up_block, compute_uv=False)
            ),
            right_coeffs=up_right,
        ),
        down_block=BridgedQuarkBlock(
            original_residual_norm=full_order_one_residual_norm_16(original_down),
            bridged_residual_norm=full_order_one_residual_norm_16(bridged_down),
            original_rank=int(np.linalg.matrix_rank(original_down_block)),
            bridged_rank=int(np.linalg.matrix_rank(bridged_down_block)),
            support_count=int(np.count_nonzero(np.abs(bridged_down) > FLOAT_TOL)),
            original_singular_values=tuple(
                float(value)
                for value in np.linalg.svd(original_down_block, compute_uv=False)
            ),
            bridged_singular_values=tuple(
                float(value)
                for value in np.linalg.svd(bridged_down_block, compute_uv=False)
            ),
            right_coeffs=down_right,
        ),
        original_total_residual_norm=original_total,
        bridged_total_residual_norm=bridged_total,
        residual_improvement_factor=original_total / bridged_total,
        residual_reduction_fraction=(original_total - bridged_total) / original_total,
        support_preserved=bool(
            np.count_nonzero(np.abs(original_up) > FLOAT_TOL)
            == np.count_nonzero(np.abs(bridged_up) > FLOAT_TOL)
            and np.count_nonzero(np.abs(original_down) > FLOAT_TOL)
            == np.count_nonzero(np.abs(bridged_down) > FLOAT_TOL)
        ),
    )

