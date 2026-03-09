"""Induced quark Yukawa candidate from the full W(3,3) 27.

The spinor-only 16 exposes the clean leptonic Higgs line but does not carry a
direct hypercharge-compatible quark Yukawa channel. This module integrates out
the heavy singlet-plus-vector 11 inside the exact 27 and packages the first
induced quark-support branch as executable data.

What is implemented:
  - the heavy background search on the exact slots (S, H_2, Hbar_2);
  - a Schur-type induced operator -Y_lh M_hh^+ Y_hl on the 16-spinor sector;
  - hypercharge-compatible 8x8 left-right projections for H_2 and Hbar_2;
  - exact rational quark/lepton channel blocks and residual diagnostics.

What is not claimed:
  - a full Standard Model quark-sector derivation;
  - uniqueness beyond the bounded coefficient search cube;
  - elimination of the remaining weak/color residual on the induced quark line.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import itertools

import numpy as np
import sympy as sp

from w33_finite_spectral_triple import canonical_cubic_tensor_27, canonical_generation_basis
from w33_fermionic_connes_sector import (
    LEFT_DIM,
    RIGHT_DIM,
    canonical_spinor_basis,
    color_generator_16,
    color_generator_names,
    fermionic_dirac_from_yukawa_16,
    left_spinor_basis,
    right_spinor_basis,
    weak_generator_16,
    weak_generator_names,
)


BACKGROUND_SLOT_NAMES = ("S", "H_2", "Hbar_2")
INDUCED_SLOT_NAMES = ("H_2", "Hbar_2")
DEFAULT_SEARCH_BOUND = 3
DEFAULT_BACKGROUND_COEFFS = (3, -3, -2)
UPLIKE_HIGGS_CHARGE = Fraction(1, 2)
DOWNLIKE_HIGGS_CHARGE = Fraction(-1, 2)
ZERO = Fraction(0, 1)
MatrixGrid = tuple[tuple[Fraction, ...], ...]
FLOAT_SUPPORT_TOL = 1e-9


@dataclass(frozen=True)
class HeavyBackgroundSearchResult:
    """Best bounded heavy-background representative for the induced search."""

    background_slots: tuple[str, str, str]
    background_coeffs: tuple[int, int, int]
    search_bound: int
    heavy_background_rank: int
    total_quark_support: int
    total_lepton_support: int
    total_quark_residual: float
    total_projected_residual: float


@dataclass(frozen=True)
class InducedChannelCandidate:
    """Induced hypercharge-compatible channel for one external Higgs slot."""

    external_slot: str
    projected_matrix_8x8: MatrixGrid
    quark_matrix_8x8: MatrixGrid
    lepton_matrix_8x8: MatrixGrid
    supported_sm_pairs: tuple[tuple[str, str], ...]
    quark_support_count: int
    lepton_support_count: int
    quark_rank: int
    lepton_rank: int
    quark_singular_values: tuple[float, ...]
    lepton_singular_values: tuple[float, ...]
    total_residual_norm: float
    quark_residual_norm: float
    lepton_residual_norm: float


@dataclass(frozen=True)
class InducedQuarkYukawaCandidate:
    """Packaged induced quark-support branch from the full 27."""

    background_slots: tuple[str, str, str]
    background_coeffs: tuple[int, int, int]
    search_bound: int
    heavy_basis_slots: tuple[str, ...]
    heavy_background_rank: int
    heavy_background_singular_values: tuple[float, ...]
    total_quark_support: int
    total_lepton_support: int
    up_channel: InducedChannelCandidate
    down_channel: InducedChannelCandidate


def _slot_to_index() -> dict[str, int]:
    return {state.slot: state.local_index for state in canonical_generation_basis()}


@lru_cache(maxsize=1)
def heavy_sector_basis() -> tuple:
    return tuple(
        state
        for state in canonical_generation_basis()
        if state.sector != "spinor"
    )


@lru_cache(maxsize=1)
def heavy_sector_indices_27() -> tuple[int, ...]:
    return tuple(state.local_index for state in heavy_sector_basis())


@lru_cache(maxsize=1)
def light_sector_indices_27() -> tuple[int, ...]:
    return tuple(state.local_index for state in canonical_spinor_basis())


def _integer_tensor() -> np.ndarray:
    return canonical_cubic_tensor_27().astype(np.int64)


def _tensor_block_numpy(
    row_indices: tuple[int, ...],
    col_indices: tuple[int, ...],
    slot: str,
) -> np.ndarray:
    slot_index = _slot_to_index()[slot]
    return _integer_tensor()[np.ix_(row_indices, col_indices, [slot_index])][:, :, 0]


def _sympy_integer_matrix(block: np.ndarray) -> sp.Matrix:
    return sp.Matrix(
        [
            [sp.Integer(int(entry)) for entry in row]
            for row in block.tolist()
        ]
    )


def _fraction_grid_from_sympy(matrix: sp.Matrix) -> MatrixGrid:
    rows = []
    for row in matrix.tolist():
        values = []
        for entry in row:
            exact = sp.simplify(entry)
            if not exact.is_Rational:
                raise ValueError("Expected rational induced entry")
            values.append(Fraction(int(exact.p), int(exact.q)))
        rows.append(tuple(values))
    return tuple(rows)


def _numpy_from_grid(grid: MatrixGrid) -> np.ndarray:
    return np.array([[float(entry) for entry in row] for row in grid], dtype=float)


def _zero_grid() -> MatrixGrid:
    return tuple(
        tuple(ZERO for _ in range(RIGHT_DIM))
        for _ in range(LEFT_DIM)
    )


def _left_row_indices(sm: str) -> tuple[int, ...]:
    return tuple(idx for idx, state in enumerate(left_spinor_basis()) if state.sm == sm)


def _right_col_indices(sm: str) -> tuple[int, ...]:
    return tuple(idx for idx, state in enumerate(right_spinor_basis()) if state.sm == sm)


def _masked_grid(
    grid: MatrixGrid,
    row_indices: tuple[int, ...],
    col_indices: tuple[int, ...],
) -> MatrixGrid:
    data = [list(row) for row in _zero_grid()]
    for row_index in row_indices:
        for col_index in col_indices:
            data[row_index][col_index] = grid[row_index][col_index]
    return tuple(tuple(row) for row in data)


def _grid_support_count(grid: MatrixGrid) -> int:
    return sum(1 for row in grid for entry in row if entry != ZERO)


def _support_count_numpy(matrix: np.ndarray) -> int:
    return int(np.count_nonzero(np.abs(matrix) > FLOAT_SUPPORT_TOL))


def _residual_norm(grid: MatrixGrid) -> float:
    return _residual_norm_from_numpy(_numpy_from_grid(grid))


def _residual_norm_from_numpy(yukawa: np.ndarray) -> float:
    dirac = fermionic_dirac_from_yukawa_16(yukawa)
    total = 0.0
    for weak_name in weak_generator_names():
        weak = weak_generator_16(weak_name)
        for color_name in color_generator_names():
            color = color_generator_16(color_name)
            residual = (dirac @ weak - weak @ dirac) @ color - color @ (dirac @ weak - weak @ dirac)
            total += float(np.linalg.norm(residual) ** 2)
    return float(np.sqrt(total))


def _grid_block_numpy(
    grid: MatrixGrid,
    row_indices: tuple[int, ...],
    col_indices: tuple[int, ...],
) -> np.ndarray:
    return _numpy_from_grid(grid)[np.ix_(row_indices, col_indices)]


def _grid_block_rank(
    grid: MatrixGrid,
    row_indices: tuple[int, ...],
    col_indices: tuple[int, ...],
) -> int:
    block = [
        [sp.Rational(grid[row_index][col_index].numerator, grid[row_index][col_index].denominator) for col_index in col_indices]
        for row_index in row_indices
    ]
    return int(sp.Matrix(block).rank())


def _grid_block_singular_values(
    grid: MatrixGrid,
    row_indices: tuple[int, ...],
    col_indices: tuple[int, ...],
) -> tuple[float, ...]:
    values = np.linalg.svd(_grid_block_numpy(grid, row_indices, col_indices), compute_uv=False)
    return tuple(float(value) for value in values)


def _supported_sm_pairs(grid: MatrixGrid) -> tuple[tuple[str, str], ...]:
    supported = set()
    left_basis = left_spinor_basis()
    right_basis = right_spinor_basis()
    for row_index, left_state in enumerate(left_basis):
        for col_index, right_state in enumerate(right_basis):
            if grid[row_index][col_index] != ZERO:
                supported.add((left_state.sm, right_state.sm))
    return tuple(sorted(supported))


def _slot_charge(slot: str) -> Fraction:
    if slot == "H_2":
        return UPLIKE_HIGGS_CHARGE
    if slot == "Hbar_2":
        return DOWNLIKE_HIGGS_CHARGE
    raise KeyError(f"Unsupported induced slot: {slot}")


def _canonicalize_background_coeffs(
    background_coeffs: tuple[int, int, int],
) -> tuple[int, int, int]:
    for coeff in background_coeffs:
        if coeff < 0:
            return tuple(-value for value in background_coeffs)
        if coeff > 0:
            return background_coeffs
    return background_coeffs


@lru_cache(maxsize=1)
def heavy_background_component_matrices_11() -> dict[str, sp.Matrix]:
    heavy = heavy_sector_indices_27()
    return {
        slot: _sympy_integer_matrix(_tensor_block_numpy(heavy, heavy, slot))
        for slot in BACKGROUND_SLOT_NAMES
    }


@lru_cache(maxsize=1)
def heavy_background_component_matrices_11_numpy() -> dict[str, np.ndarray]:
    heavy = heavy_sector_indices_27()
    return {
        slot: _tensor_block_numpy(heavy, heavy, slot).astype(float)
        for slot in BACKGROUND_SLOT_NAMES
    }


@lru_cache(maxsize=None)
def heavy_background_matrix_11(
    background_coeffs: tuple[int, int, int],
) -> sp.Matrix:
    matrix = sp.zeros(len(heavy_sector_indices_27()), len(heavy_sector_indices_27()))
    for coeff, slot in zip(background_coeffs, BACKGROUND_SLOT_NAMES):
        matrix += coeff * heavy_background_component_matrices_11()[slot]
    return matrix


@lru_cache(maxsize=None)
def heavy_background_pseudoinverse_11(
    background_coeffs: tuple[int, int, int],
) -> sp.Matrix:
    matrix = heavy_background_matrix_11(background_coeffs)
    if matrix.rank() == 0:
        raise ValueError("Heavy background must have positive rank")
    return matrix.pinv()


@lru_cache(maxsize=1)
def induced_component_blocks() -> dict[str, tuple[sp.Matrix, sp.Matrix]]:
    light = light_sector_indices_27()
    heavy = heavy_sector_indices_27()
    return {
        slot: (
            _sympy_integer_matrix(_tensor_block_numpy(light, heavy, slot)),
            _sympy_integer_matrix(_tensor_block_numpy(heavy, light, slot)),
        )
        for slot in INDUCED_SLOT_NAMES
    }


@lru_cache(maxsize=1)
def induced_component_blocks_numpy() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    light = light_sector_indices_27()
    heavy = heavy_sector_indices_27()
    return {
        slot: (
            _tensor_block_numpy(light, heavy, slot).astype(float),
            _tensor_block_numpy(heavy, light, slot).astype(float),
        )
        for slot in INDUCED_SLOT_NAMES
    }


@lru_cache(maxsize=1)
def light_spinor_positions() -> dict[int, int]:
    return {
        local_index: position
        for position, local_index in enumerate(light_sector_indices_27())
    }


@lru_cache(maxsize=None)
def induced_light_operator_16(
    external_slot: str,
    background_coeffs: tuple[int, int, int] = DEFAULT_BACKGROUND_COEFFS,
) -> sp.Matrix:
    y_light_heavy, y_heavy_light = induced_component_blocks()[external_slot]
    # Integrate out the heavy 10 (+) 1 against the selected background branch.
    return -(y_light_heavy * heavy_background_pseudoinverse_11(background_coeffs) * y_heavy_light)


@lru_cache(maxsize=None)
def hypercharge_projected_induced_yukawa_8x8(
    external_slot: str,
    background_coeffs: tuple[int, int, int] = DEFAULT_BACKGROUND_COEFFS,
) -> MatrixGrid:
    if external_slot not in INDUCED_SLOT_NAMES:
        raise KeyError(f"Unsupported induced slot: {external_slot}")

    induced = induced_light_operator_16(external_slot, background_coeffs)
    light_positions = light_spinor_positions()
    projected = sp.zeros(LEFT_DIM, RIGHT_DIM)
    charge = _slot_charge(external_slot)

    for row_index, left_state in enumerate(left_spinor_basis()):
        for col_index, right_state in enumerate(right_spinor_basis()):
            if left_state.hypercharge + right_state.hypercharge + charge != 0:
                continue
            light_row = light_positions[left_state.local_index]
            light_col = light_positions[right_state.local_index]
            projected[row_index, col_index] = sp.simplify(induced[light_row, light_col])

    return _fraction_grid_from_sympy(projected)


def quark_projection_8x8(external_slot: str, grid: MatrixGrid | None = None) -> MatrixGrid:
    if grid is None:
        grid = hypercharge_projected_induced_yukawa_8x8(external_slot)
    if external_slot == "H_2":
        return _masked_grid(grid, _left_row_indices("Q"), _right_col_indices("u_c"))
    if external_slot == "Hbar_2":
        return _masked_grid(grid, _left_row_indices("Q"), _right_col_indices("d_c"))
    raise KeyError(f"Unsupported induced slot: {external_slot}")


def lepton_projection_8x8(external_slot: str, grid: MatrixGrid | None = None) -> MatrixGrid:
    if grid is None:
        grid = hypercharge_projected_induced_yukawa_8x8(external_slot)
    if external_slot == "H_2":
        return _masked_grid(grid, _left_row_indices("L"), _right_col_indices("nu_c"))
    if external_slot == "Hbar_2":
        return _masked_grid(grid, _left_row_indices("L"), _right_col_indices("e_c"))
    raise KeyError(f"Unsupported induced slot: {external_slot}")


def _projected_yukawa_8x8_numpy(
    external_slot: str,
    background_coeffs: tuple[int, int, int],
) -> np.ndarray:
    light_basis = canonical_spinor_basis()
    light_positions = {state.local_index: index for index, state in enumerate(light_basis)}
    projected = np.zeros((LEFT_DIM, RIGHT_DIM), dtype=float)
    charge = _slot_charge(external_slot)

    background = np.zeros((len(heavy_sector_indices_27()), len(heavy_sector_indices_27())), dtype=float)
    for coeff, slot in zip(background_coeffs, BACKGROUND_SLOT_NAMES):
        background += coeff * heavy_background_component_matrices_11_numpy()[slot]
    if np.linalg.matrix_rank(background) == 0:
        raise ValueError("Heavy background must have positive rank")

    y_light_heavy, y_heavy_light = induced_component_blocks_numpy()[external_slot]
    induced = -(y_light_heavy @ np.linalg.pinv(background) @ y_heavy_light)

    for row_index, left_state in enumerate(left_spinor_basis()):
        for col_index, right_state in enumerate(right_spinor_basis()):
            if left_state.hypercharge + right_state.hypercharge + charge != 0:
                continue
            projected[row_index, col_index] = induced[
                light_positions[left_state.local_index],
                light_positions[right_state.local_index],
            ]
    return projected


@lru_cache(maxsize=None)
def best_heavy_background_search(
    search_bound: int = DEFAULT_SEARCH_BOUND,
) -> HeavyBackgroundSearchResult:
    best_key = None
    best_result = None

    q_rows = _left_row_indices("Q")
    l_rows = _left_row_indices("L")
    u_cols = _right_col_indices("u_c")
    d_cols = _right_col_indices("d_c")
    e_cols = _right_col_indices("e_c")
    nu_cols = _right_col_indices("nu_c")

    for raw_coeffs in itertools.product(range(-search_bound, search_bound + 1), repeat=3):
        if raw_coeffs == (0, 0, 0):
            continue

        try:
            up = _projected_yukawa_8x8_numpy("H_2", raw_coeffs)
            down = _projected_yukawa_8x8_numpy("Hbar_2", raw_coeffs)
        except ValueError:
            continue

        up_quark = np.zeros((LEFT_DIM, RIGHT_DIM), dtype=float)
        up_quark[np.ix_(q_rows, u_cols)] = up[np.ix_(q_rows, u_cols)]
        down_quark = np.zeros((LEFT_DIM, RIGHT_DIM), dtype=float)
        down_quark[np.ix_(q_rows, d_cols)] = down[np.ix_(q_rows, d_cols)]

        up_lepton = np.zeros((LEFT_DIM, RIGHT_DIM), dtype=float)
        up_lepton[np.ix_(l_rows, nu_cols)] = up[np.ix_(l_rows, nu_cols)]
        down_lepton = np.zeros((LEFT_DIM, RIGHT_DIM), dtype=float)
        down_lepton[np.ix_(l_rows, e_cols)] = down[np.ix_(l_rows, e_cols)]

        canonical_coeffs = _canonicalize_background_coeffs(raw_coeffs)
        rank = int(np.linalg.matrix_rank(np.array(heavy_background_matrix_11(canonical_coeffs), dtype=float)))
        quark_support = _support_count_numpy(up_quark) + _support_count_numpy(down_quark)
        lepton_support = _support_count_numpy(up_lepton) + _support_count_numpy(down_lepton)
        quark_residual = _residual_norm_from_numpy(up_quark) + _residual_norm_from_numpy(down_quark)
        total_residual = _residual_norm_from_numpy(up) + _residual_norm_from_numpy(down)

        key = (-rank, -quark_support, quark_residual, total_residual, canonical_coeffs)
        if best_key is None or key < best_key:
            best_key = key
            best_result = HeavyBackgroundSearchResult(
                background_slots=BACKGROUND_SLOT_NAMES,
                background_coeffs=canonical_coeffs,
                search_bound=search_bound,
                heavy_background_rank=rank,
                total_quark_support=quark_support,
                total_lepton_support=lepton_support,
                total_quark_residual=quark_residual,
                total_projected_residual=total_residual,
            )

    if best_result is None:
        raise ValueError("No nondegenerate heavy background found in search cube")
    return best_result


def _channel_candidate(
    external_slot: str,
    background_coeffs: tuple[int, int, int],
) -> InducedChannelCandidate:
    projected = hypercharge_projected_induced_yukawa_8x8(external_slot, background_coeffs)
    quark = quark_projection_8x8(external_slot, projected)
    lepton = lepton_projection_8x8(external_slot, projected)

    if external_slot == "H_2":
        quark_rows = _left_row_indices("Q")
        quark_cols = _right_col_indices("u_c")
        lepton_rows = _left_row_indices("L")
        lepton_cols = _right_col_indices("nu_c")
    else:
        quark_rows = _left_row_indices("Q")
        quark_cols = _right_col_indices("d_c")
        lepton_rows = _left_row_indices("L")
        lepton_cols = _right_col_indices("e_c")

    return InducedChannelCandidate(
        external_slot=external_slot,
        projected_matrix_8x8=projected,
        quark_matrix_8x8=quark,
        lepton_matrix_8x8=lepton,
        supported_sm_pairs=_supported_sm_pairs(projected),
        quark_support_count=_grid_support_count(quark),
        lepton_support_count=_grid_support_count(lepton),
        quark_rank=_grid_block_rank(quark, quark_rows, quark_cols),
        lepton_rank=_grid_block_rank(lepton, lepton_rows, lepton_cols),
        quark_singular_values=_grid_block_singular_values(quark, quark_rows, quark_cols),
        lepton_singular_values=_grid_block_singular_values(lepton, lepton_rows, lepton_cols),
        total_residual_norm=_residual_norm(projected),
        quark_residual_norm=_residual_norm(quark),
        lepton_residual_norm=_residual_norm(lepton),
    )


@lru_cache(maxsize=None)
def build_induced_quark_yukawa_candidate(
    search_bound: int = DEFAULT_SEARCH_BOUND,
    background_coeffs: tuple[int, int, int] | None = None,
) -> InducedQuarkYukawaCandidate:
    search = best_heavy_background_search(search_bound)
    if background_coeffs is None:
        background_coeffs = search.background_coeffs
    else:
        background_coeffs = _canonicalize_background_coeffs(background_coeffs)

    heavy_background = np.array(heavy_background_matrix_11(background_coeffs), dtype=float)
    up_channel = _channel_candidate("H_2", background_coeffs)
    down_channel = _channel_candidate("Hbar_2", background_coeffs)

    return InducedQuarkYukawaCandidate(
        background_slots=BACKGROUND_SLOT_NAMES,
        background_coeffs=background_coeffs,
        search_bound=search_bound,
        heavy_basis_slots=tuple(state.slot for state in heavy_sector_basis()),
        heavy_background_rank=int(np.linalg.matrix_rank(heavy_background)),
        heavy_background_singular_values=tuple(float(value) for value in np.linalg.svd(heavy_background, compute_uv=False)),
        total_quark_support=up_channel.quark_support_count + down_channel.quark_support_count,
        total_lepton_support=up_channel.lepton_support_count + down_channel.lepton_support_count,
        up_channel=up_channel,
        down_channel=down_channel,
    )
