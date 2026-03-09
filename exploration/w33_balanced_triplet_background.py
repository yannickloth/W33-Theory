"""Balanced triplet-background family for the induced quark branch.

The first induced quark candidate searched only the scalar/Higgs branch
`(S, H_2, Hbar_2)`. The quark/firewall obstruction localizes the remaining
problem on the triplet fibers, so the next exact move is to deform the heavy
background in a way that treats those triplet fibers coherently.

This module studies the one-parameter family

    S : H_2 : Hbar_2 : T : Tbar = 1 : -n : -n : n : n

where the three `T_i` share the same coefficient `n` and the three `Tbar_i`
share the same coefficient `n`.

What is implemented:
  - exact induced quark/lepton blocks for each integer `n >= 1`;
  - full SU(3)xSU(2) residuals on the quark blocks;
  - a scale-invariant normalized full-screen score;
  - comparison to the current `(3, -3, -2)` branch.

What is not claimed:
  - a final quark solution;
  - a nonzero fully clean quark block;
  - a Vogel-theoretic closure theorem.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

import numpy as np

from w33_finite_spectral_triple import canonical_cubic_tensor_27, canonical_generation_basis
from w33_fermionic_connes_sector import (
    canonical_spinor_basis,
    fermionic_dirac_from_yukawa_16,
    left_spinor_basis,
    right_spinor_basis,
)
from w33_induced_quark_yukawa import (
    build_induced_quark_yukawa_candidate,
    heavy_sector_basis,
    heavy_sector_indices_27,
    light_sector_indices_27,
)
from w33_quark_firewall_obstruction import (
    build_quark_firewall_obstruction,
    triad_index_by_e6id,
)


FAMILY_LINE = "S : H_2 : Hbar_2 : T : Tbar = 1 : -n : -n : n : n"
DEFAULT_MAX_SCALE = 6
HIGGS_CHARGE_BY_SLOT = {
    "H_2": Fraction(1, 2),
    "Hbar_2": Fraction(-1, 2),
}


@dataclass(frozen=True)
class BalancedTripletFamilyMember:
    """One member of the balanced triplet family."""

    n: int
    family_coeffs: tuple[int, int, int, int, int]
    heavy_background_rank: int
    total_quark_support: int
    total_lepton_support: int
    up_quark_support: int
    down_quark_support: int
    up_quark_rank: int
    down_quark_rank: int
    full_quark_residual_total: float
    quark_frobenius_total: float
    normalized_full_quark_ratio: float
    up_triplet_pairs: tuple[tuple[int, int], ...]
    down_triplet_pairs: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class BalancedTripletBackgroundSummary:
    """Packaged comparison against the current induced branch."""

    family_line: str
    scanned_scales: tuple[int, ...]
    members: tuple[BalancedTripletFamilyMember, ...]
    baseline_background_coeffs: tuple[int, int, int]
    baseline_total_quark_support: int
    baseline_total_lepton_support: int
    baseline_normalized_full_quark_ratio: float
    best_scale_within_scan: int
    best_member: BalancedTripletFamilyMember
    improvement_factor_over_baseline: float
    full_screen_nullity: int


def _slot_to_index() -> dict[str, int]:
    return {state.slot: state.local_index for state in canonical_generation_basis()}


def _tensor_block_numpy(
    row_indices: tuple[int, ...],
    col_indices: tuple[int, ...],
    slot: str,
) -> np.ndarray:
    tensor = canonical_cubic_tensor_27().astype(np.int64)
    slot_index = _slot_to_index()[slot]
    return tensor[np.ix_(row_indices, col_indices, [slot_index])][:, :, 0].astype(float)


@lru_cache(maxsize=1)
def _heavy_component_matrices_11() -> dict[str, np.ndarray]:
    heavy = heavy_sector_indices_27()
    return {
        state.slot: _tensor_block_numpy(heavy, heavy, state.slot)
        for state in heavy_sector_basis()
    }


@lru_cache(maxsize=1)
def _mixed_component_blocks() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    light = light_sector_indices_27()
    heavy = heavy_sector_indices_27()
    return {
        slot: (
            _tensor_block_numpy(light, heavy, slot),
            _tensor_block_numpy(heavy, light, slot),
        )
        for slot in HIGGS_CHARGE_BY_SLOT
    }


@lru_cache(maxsize=1)
def _full_weak_generators_16() -> tuple[np.ndarray, ...]:
    generators = {
        "sigma_x": np.array([[0, 1], [1, 0]], dtype=complex),
        "sigma_y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "sigma_z": np.array([[1, 0], [0, -1]], dtype=complex),
    }
    operators = []
    for block in generators.values():
        operator = np.eye(16, dtype=complex)
        for start in (0, 2, 4, 6):
            indices = (start, start + 1)
            operator[np.ix_(indices, indices)] = block
        operators.append(operator)
    return tuple(operators)


@lru_cache(maxsize=1)
def _full_color_generators_16() -> tuple[np.ndarray, ...]:
    generators = (
        np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=complex),
        np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=complex),
        np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=complex),
        np.array([[0, 0, 1], [0, 0, 0], [1, 0, 0]], dtype=complex),
        np.array([[0, 0, -1j], [0, 0, 0], [1j, 0, 0]], dtype=complex),
        np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=complex),
        np.array([[0, 0, 0], [0, 0, -1j], [0, 1j, 0]], dtype=complex),
        (1.0 / np.sqrt(3.0))
        * np.array([[1, 0, 0], [0, 1, 0], [0, 0, -2]], dtype=complex),
    )
    operators = []
    for color in generators:
        operator = np.eye(16, dtype=complex)
        operator[np.ix_(range(0, 6), range(0, 6))] = np.kron(
            color, np.eye(2, dtype=complex)
        )
        operator[np.ix_(range(8, 11), range(8, 11))] = np.conjugate(color)
        operator[np.ix_(range(11, 14), range(11, 14))] = np.conjugate(color)
        operators.append(operator)
    return tuple(operators)


def _left_row_indices(sm: str) -> tuple[int, ...]:
    return tuple(idx for idx, state in enumerate(left_spinor_basis()) if state.sm == sm)


def _right_col_indices(sm: str) -> tuple[int, ...]:
    return tuple(
        idx for idx, state in enumerate(right_spinor_basis()) if state.sm == sm
    )


def _heavy_background_matrix_11(n: int) -> np.ndarray:
    components = _heavy_component_matrices_11()
    return (
        components["S"]
        - n * components["H_2"]
        - n * components["Hbar_2"]
        + n * components["T_1"]
        + n * components["T_2"]
        + n * components["T_3"]
        + n * components["Tbar_1"]
        + n * components["Tbar_2"]
        + n * components["Tbar_3"]
    )


def _projected_yukawa(external_slot: str, n: int) -> np.ndarray:
    background = _heavy_background_matrix_11(n)
    light_to_heavy, heavy_to_light = _mixed_component_blocks()[external_slot]
    induced = -(light_to_heavy @ np.linalg.pinv(background) @ heavy_to_light)

    projected = np.zeros((8, 8), dtype=float)
    light_positions = {
        state.local_index: index
        for index, state in enumerate(canonical_spinor_basis())
    }
    charge = HIGGS_CHARGE_BY_SLOT[external_slot]
    for row_index, left_state in enumerate(left_spinor_basis()):
        for col_index, right_state in enumerate(right_spinor_basis()):
            if left_state.hypercharge + right_state.hypercharge + charge != 0:
                continue
            projected[row_index, col_index] = induced[
                light_positions[left_state.local_index],
                light_positions[right_state.local_index],
            ]
    return projected


def _quark_projection(external_slot: str, projected: np.ndarray) -> np.ndarray:
    quark = np.zeros_like(projected)
    if external_slot == "H_2":
        quark[np.ix_(_left_row_indices("Q"), _right_col_indices("u_c"))] = projected[
            np.ix_(_left_row_indices("Q"), _right_col_indices("u_c"))
        ]
        return quark
    quark[np.ix_(_left_row_indices("Q"), _right_col_indices("d_c"))] = projected[
        np.ix_(_left_row_indices("Q"), _right_col_indices("d_c"))
    ]
    return quark


def _lepton_projection(external_slot: str, projected: np.ndarray) -> np.ndarray:
    lepton = np.zeros_like(projected)
    if external_slot == "H_2":
        lepton[np.ix_(_left_row_indices("L"), _right_col_indices("nu_c"))] = projected[
            np.ix_(_left_row_indices("L"), _right_col_indices("nu_c"))
        ]
        return lepton
    lepton[np.ix_(_left_row_indices("L"), _right_col_indices("e_c"))] = projected[
        np.ix_(_left_row_indices("L"), _right_col_indices("e_c"))
    ]
    return lepton


def _quark_residual_norm(matrix: np.ndarray) -> float:
    dirac = fermionic_dirac_from_yukawa_16(matrix)
    total = 0.0
    for weak in _full_weak_generators_16():
        for color in _full_color_generators_16():
            residual = (dirac @ weak - weak @ dirac) @ color - color @ (
                dirac @ weak - weak @ dirac
            )
            total += float(np.linalg.norm(residual) ** 2)
    return float(np.sqrt(total))


def _support_count(matrix: np.ndarray) -> int:
    return int(np.count_nonzero(np.abs(matrix) > 1e-10))


def _block_rank(matrix: np.ndarray, row_indices: tuple[int, ...], col_indices: tuple[int, ...]) -> int:
    return int(np.linalg.matrix_rank(matrix[np.ix_(row_indices, col_indices)]))


def _triplet_pairs(external_slot: str, quark_matrix: np.ndarray) -> tuple[tuple[int, int], ...]:
    triad_by_e6id = triad_index_by_e6id()
    right_sm = "u_c" if external_slot == "H_2" else "d_c"
    pairs = set()
    for row_index, left_state in enumerate(left_spinor_basis()):
        if left_state.sm != "Q":
            continue
        for col_index, right_state in enumerate(right_spinor_basis()):
            if right_state.sm != right_sm:
                continue
            if abs(quark_matrix[row_index, col_index]) <= 1e-10:
                continue
            pairs.add(
                (
                    triad_by_e6id[left_state.source_i27],
                    triad_by_e6id[right_state.source_i27],
                )
            )
    return tuple(sorted(pairs))


@lru_cache(maxsize=None)
def balanced_triplet_family_member(n: int) -> BalancedTripletFamilyMember:
    if n < 1:
        raise ValueError("n must be positive")

    background = _heavy_background_matrix_11(n)
    up_projected = _projected_yukawa("H_2", n)
    down_projected = _projected_yukawa("Hbar_2", n)
    up_quark = _quark_projection("H_2", up_projected)
    down_quark = _quark_projection("Hbar_2", down_projected)
    up_lepton = _lepton_projection("H_2", up_projected)
    down_lepton = _lepton_projection("Hbar_2", down_projected)

    full_quark_residual_total = _quark_residual_norm(up_quark) + _quark_residual_norm(
        down_quark
    )
    quark_frobenius_total = float(np.linalg.norm(up_quark) + np.linalg.norm(down_quark))

    return BalancedTripletFamilyMember(
        n=n,
        family_coeffs=(1, -n, -n, n, n),
        heavy_background_rank=int(np.linalg.matrix_rank(background)),
        total_quark_support=_support_count(up_quark) + _support_count(down_quark),
        total_lepton_support=_support_count(up_lepton) + _support_count(down_lepton),
        up_quark_support=_support_count(up_quark),
        down_quark_support=_support_count(down_quark),
        up_quark_rank=_block_rank(
            up_quark, _left_row_indices("Q"), _right_col_indices("u_c")
        ),
        down_quark_rank=_block_rank(
            down_quark, _left_row_indices("Q"), _right_col_indices("d_c")
        ),
        full_quark_residual_total=full_quark_residual_total,
        quark_frobenius_total=quark_frobenius_total,
        normalized_full_quark_ratio=full_quark_residual_total / quark_frobenius_total,
        up_triplet_pairs=_triplet_pairs("H_2", up_quark),
        down_triplet_pairs=_triplet_pairs("Hbar_2", down_quark),
    )


def _baseline_normalized_ratio() -> float:
    candidate = build_induced_quark_yukawa_candidate()
    up = np.array(
        [[float(entry) for entry in row] for row in candidate.up_channel.quark_matrix_8x8],
        dtype=float,
    )
    down = np.array(
        [[float(entry) for entry in row] for row in candidate.down_channel.quark_matrix_8x8],
        dtype=float,
    )
    total_residual = _quark_residual_norm(up) + _quark_residual_norm(down)
    total_norm = float(np.linalg.norm(up) + np.linalg.norm(down))
    return total_residual / total_norm


@lru_cache(maxsize=1)
def build_balanced_triplet_background_summary(
    max_scale: int = DEFAULT_MAX_SCALE,
) -> BalancedTripletBackgroundSummary:
    members = tuple(balanced_triplet_family_member(n) for n in range(1, max_scale + 1))
    best = min(
        members,
        key=lambda member: (
            member.normalized_full_quark_ratio,
            -member.total_quark_support,
            -member.total_lepton_support,
            -member.heavy_background_rank,
            member.n,
        ),
    )
    baseline = build_induced_quark_yukawa_candidate()
    baseline_ratio = _baseline_normalized_ratio()
    obstruction = build_quark_firewall_obstruction()

    return BalancedTripletBackgroundSummary(
        family_line=FAMILY_LINE,
        scanned_scales=tuple(range(1, max_scale + 1)),
        members=members,
        baseline_background_coeffs=baseline.background_coeffs,
        baseline_total_quark_support=baseline.total_quark_support,
        baseline_total_lepton_support=baseline.total_lepton_support,
        baseline_normalized_full_quark_ratio=baseline_ratio,
        best_scale_within_scan=best.n,
        best_member=best,
        improvement_factor_over_baseline=baseline_ratio / best.normalized_full_quark_ratio,
        full_screen_nullity=obstruction.screen_summary.full_up_nullity,
    )
