"""Exact exhaustion certificate for the l4-to-Dirac quark bridge.

The first l4-to-Dirac bridge lowers the strict full SU(3)xSU(2) quark
residual and lifts both quark blocks from rank 2 to rank 3, but it does not
close the residual. This module makes that failure precise.

What is established:
  - the nominal 12-parameter l4 bridge family collapses to 6 effective modes;
  - two shared-left modes vanish exactly on the quark Dirac response;
  - four right-acting modes come in exact sign-related pairs;
  - the real stacked response matrix has rank 6 while the augmented system has
    rank 7, so exact cancellation is impossible inside the l4 bridge family;
  - the remaining residual is concentrated on a small set of nonabelian
    weak/color generator pairs.

What is not claimed:
  - a full l5 or l6 closure theorem;
  - a final quark mass derivation;
  - uniqueness of the next bridge beyond l4.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from w33_l4_quark_dirac_bridge import (
    _basis_left_right_blocks,
    _embedded_original_down,
    _embedded_original_up,
    _quark_row_indices,
    _solve_shared_left_fit,
    _up_col_indices,
    bridged_down_quark_yukawa_8x8,
    bridged_up_quark_yukawa_8x8,
    l4_dirac_bridge_basis,
)
from w33_fermionic_connes_sector import right_spinor_basis
from w33_quark_firewall_obstruction import (
    _full_color_generator_16,
    _full_weak_generator_16,
    fermionic_dirac_from_yukawa_16,
    full_order_one_residual_vector_16,
)


FLOAT_TOL = 1e-12
_WEAK_NAMES = ("sigma_x", "sigma_y", "sigma_z")
_COLOR_NAMES = (
    "lambda_1",
    "lambda_2",
    "lambda_3",
    "lambda_4",
    "lambda_5",
    "lambda_6",
    "lambda_7",
    "lambda_8",
)


@dataclass(frozen=True)
class ResidualSectorContribution:
    """One weak/color generator-pair contribution to the residual."""

    weak_name: str
    color_name: str
    norm: float


@dataclass(frozen=True)
class L4DiracBridgeObstructionCertificate:
    """Exact obstruction data for the full l4-to-Dirac bridge family."""

    zero_shared_left_modes: tuple[str, ...]
    exact_mode_relations: tuple[str, ...]
    effective_mode_names: tuple[str, ...]
    response_shape: tuple[int, int]
    response_rank: int
    augmented_rank: int
    original_total_residual_norm: float
    minimal_total_residual_norm: float
    improvement_factor: float
    normal_equation_max_residual: float
    shared_left_coeffs: tuple[float, ...]
    up_right_coeffs: tuple[float, ...]
    down_right_coeffs: tuple[float, ...]
    top_up_residual_pairs: tuple[ResidualSectorContribution, ...]
    top_down_residual_pairs: tuple[ResidualSectorContribution, ...]


def _basis_names() -> tuple[str, ...]:
    return tuple(element.name for element in l4_dirac_bridge_basis())


def _named_response_columns() -> tuple[tuple[str, np.ndarray], ...]:
    q_blocks, u_blocks, d_blocks = _basis_left_right_blocks()
    original_up = _embedded_original_up()
    original_down = _embedded_original_down()
    up_block = original_up[np.ix_(_quark_row_indices(), _up_col_indices())]
    down_block = original_down[np.ix_(_quark_row_indices(), _down_col_indices())]
    zero_up = np.zeros_like(full_order_one_residual_vector_16(original_up))
    zero_down = np.zeros_like(full_order_one_residual_vector_16(original_down))

    columns = []
    for name, q_block in zip(_basis_names(), q_blocks):
        up = np.zeros((8, 8), dtype=float)
        down = np.zeros((8, 8), dtype=float)
        up[np.ix_(_quark_row_indices(), _up_col_indices())] = q_block @ up_block
        down[np.ix_(_quark_row_indices(), _down_col_indices())] = q_block @ down_block
        columns.append(
            (
                f"shared_left:{name}",
                np.concatenate(
                    [
                        full_order_one_residual_vector_16(up),
                        full_order_one_residual_vector_16(down),
                    ]
                ),
            )
        )

    for name, u_block in zip(_basis_names(), u_blocks):
        up = np.zeros((8, 8), dtype=float)
        up[np.ix_(_quark_row_indices(), _up_col_indices())] = up_block @ u_block
        columns.append(
            (
                f"up_right:{name}",
                np.concatenate([full_order_one_residual_vector_16(up), zero_down]),
            )
        )

    for name, d_block in zip(_basis_names(), d_blocks):
        down = np.zeros((8, 8), dtype=float)
        down[np.ix_(_quark_row_indices(), _down_col_indices())] = down_block @ d_block
        columns.append(
            (
                f"down_right:{name}",
                np.concatenate([zero_up, full_order_one_residual_vector_16(down)]),
            )
        )

    return tuple(columns)


def _stacked_real_response_matrix() -> tuple[np.ndarray, np.ndarray, tuple[str, ...]]:
    named_columns = _named_response_columns()
    complex_matrix = np.stack([column for _, column in named_columns], axis=1)
    real_matrix = np.vstack([complex_matrix.real, complex_matrix.imag])
    target = -np.concatenate(
        [
            full_order_one_residual_vector_16(_embedded_original_up()),
            full_order_one_residual_vector_16(_embedded_original_down()),
        ]
    )
    real_target = np.concatenate([target.real, target.imag])
    return real_matrix, real_target, tuple(name for name, _ in named_columns)


def _residual_pair_profile(yukawa: np.ndarray) -> tuple[ResidualSectorContribution, ...]:
    dirac = fermionic_dirac_from_yukawa_16(yukawa)
    contributions = []
    for weak_name in _WEAK_NAMES:
        weak = _full_weak_generator_16(weak_name)
        for color_name in _COLOR_NAMES:
            color = _full_color_generator_16(color_name)
            residual = (dirac @ weak - weak @ dirac) @ color - color @ (
                dirac @ weak - weak @ dirac
            )
            contributions.append(
                ResidualSectorContribution(
                    weak_name=weak_name,
                    color_name=color_name,
                    norm=float(np.linalg.norm(residual)),
                )
            )
    contributions.sort(key=lambda item: (-item.norm, item.weak_name, item.color_name))
    return tuple(contributions)


def _down_col_indices() -> tuple[int, ...]:
    return tuple(idx for idx, state in enumerate(right_spinor_basis()) if state.sm == "d_c")


@lru_cache(maxsize=1)
def build_l4_dirac_bridge_obstruction_certificate() -> L4DiracBridgeObstructionCertificate:
    q_blocks, u_blocks, d_blocks = _basis_left_right_blocks()
    zero_shared_left = tuple(
        name
        for name, q_block in zip(_basis_names(), q_blocks)
        if np.array_equal(q_block, np.zeros_like(q_block))
    )

    exact_relations = (
        "up_right:q23_ud23 = -up_right:ud_23",
        "up_right:q13_ud13 = up_right:ud_13",
        "down_right:q23_ud23 = down_right:ud_23",
        "down_right:q13_ud13 = -down_right:ud_13",
    )
    if not np.array_equal(u_blocks[2], -u_blocks[0]):
        raise ValueError("Expected exact up-right relation q23_ud23 = -ud_23")
    if not np.array_equal(u_blocks[3], u_blocks[1]):
        raise ValueError("Expected exact up-right relation q13_ud13 = ud_13")
    if not np.array_equal(d_blocks[2], d_blocks[0]):
        raise ValueError("Expected exact down-right relation q23_ud23 = ud_23")
    if not np.array_equal(d_blocks[3], -d_blocks[1]):
        raise ValueError("Expected exact down-right relation q13_ud13 = -ud_13")

    response_matrix, target, _ = _stacked_real_response_matrix()
    coeffs, _, _, _ = np.linalg.lstsq(response_matrix, target, rcond=None)
    residual = response_matrix @ coeffs - target

    shared_left, up_right, down_right = _solve_shared_left_fit()
    top_up = _residual_pair_profile(bridged_up_quark_yukawa_8x8())[:3]
    top_down = _residual_pair_profile(bridged_down_quark_yukawa_8x8())[:3]

    original_norm = float(np.linalg.norm(target))
    minimal_norm = float(np.linalg.norm(residual))
    normal_equation = float(np.max(np.abs(response_matrix.T @ residual)))

    return L4DiracBridgeObstructionCertificate(
        zero_shared_left_modes=zero_shared_left,
        exact_mode_relations=exact_relations,
        effective_mode_names=(
            "shared_left:q23_ud23",
            "shared_left:q13_ud13",
            "up_right:ud_23",
            "up_right:ud_13",
            "down_right:ud_23",
            "down_right:ud_13",
        ),
        response_shape=(int(response_matrix.shape[0]), int(response_matrix.shape[1])),
        response_rank=int(np.linalg.matrix_rank(response_matrix)),
        augmented_rank=int(
            np.linalg.matrix_rank(np.column_stack([response_matrix, target]))
        ),
        original_total_residual_norm=original_norm,
        minimal_total_residual_norm=minimal_norm,
        improvement_factor=original_norm / minimal_norm,
        normal_equation_max_residual=normal_equation,
        shared_left_coeffs=shared_left,
        up_right_coeffs=up_right,
        down_right_coeffs=down_right,
        top_up_residual_pairs=top_up,
        top_down_residual_pairs=top_down,
    )
