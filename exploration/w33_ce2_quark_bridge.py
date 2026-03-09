"""Beyond-l4 CE2 quark bridge and trivial-closure no-go.

The global CE2 predictor already knows more about the quark sector than the
first l4 bridge. This module isolates what the predictor actually generates on
the canonical quark-support source ids and packages the result as executable
data.

What is established:
  - on the quark-support source ids Q (+) u_c (+) d_c, the global CE2
    predictor generates all 12 x 12 = 144 source matrix units;
  - on the current induced Dirac bridge only the block-diagonal part contributes,
    giving 36 left Q modes and 9 + 9 right u_c / d_c modes;
  - this CE2 bridge response has the same rank as the augmented target, so the
    strict full SU(3)xSU(2) quark residual can be cancelled exactly;
  - a canonical exact cancellation is already present: the CE2-generated right
    identities on u_c and d_c annihilate the induced quark Yukawa blocks;
  - the full arbitrary Q-u_c / Q-d_c family has screen rank 36 and nullity 0,
    so the zero block is the unique fully clean quark point.

What is not claimed:
  - a nonzero quark mass theorem;
  - a final Standard Model quark-Yukawa derivation;
  - that CE2 is the last higher-tower ingredient needed for the full model.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from ce2_global_cocycle import predict_ce2_uv, predict_dual_g1g2g2_uvw
from w33_finite_spectral_triple import canonical_generation_basis
from w33_fermionic_connes_sector import left_spinor_basis, right_spinor_basis
from w33_l4_quark_dirac_bridge import (
    _basis_left_right_blocks,
    _embedded_original_down,
    _embedded_original_up,
    _down_col_indices,
    _quark_row_indices,
    _up_col_indices,
)
from w33_quark_firewall_obstruction import (
    full_order_one_residual_norm_16,
    full_order_one_residual_vector_16,
)


FLOAT_TOL = 1e-12


@dataclass(frozen=True)
class CE2GeneratedUnitRecord:
    """One CE2-generated source matrix unit on the quark-support 12-set."""

    source_row: int
    source_col: int
    local_row: int
    local_col: int
    row_slot: str
    col_slot: str
    row_sm: str
    col_sm: str
    generating_families: tuple[str, ...]


@dataclass(frozen=True)
class CE2ProjectedMode:
    """One projected CE2 bridge mode acting on the current quark Yukawa pair."""

    kind: str
    source_row: int
    source_col: int
    local_row: int
    local_col: int
    generating_families: tuple[str, ...]


@dataclass(frozen=True)
class CE2QuarkBridgeCertificate:
    """Executable summary of the beyond-l4 CE2 quark bridge."""

    q_source_ids: tuple[int, ...]
    u_source_ids: tuple[int, ...]
    d_source_ids: tuple[int, ...]
    generated_source_unit_count: int
    uv_only_source_unit_count: int
    uvw_only_source_unit_count: int
    uv_and_uvw_source_unit_count: int
    source_matrix_algebra_is_full: bool
    projected_mode_count: int
    left_mode_count: int
    up_right_mode_count: int
    down_right_mode_count: int
    response_rank: int
    augmented_rank: int
    original_total_residual_norm: float
    trivial_closure_total_residual_norm: float
    trivial_closure_up_residual_norm: float
    trivial_closure_down_residual_norm: float
    arbitrary_quark_screen_rank: int
    arbitrary_quark_screen_nullity: int
    zero_is_unique_clean_point: bool
    l4_response_contained_in_ce2: bool
    max_l4_containment_error: float
    right_up_identity_source_pairs: tuple[tuple[int, int], ...]
    right_down_identity_source_pairs: tuple[tuple[int, int], ...]
    generated_units: tuple[CE2GeneratedUnitRecord, ...]
    projected_modes: tuple[CE2ProjectedMode, ...]


def _state_by_source() -> dict[int, object]:
    return {state.source_i27: state for state in canonical_generation_basis()}


def _source_to_local() -> dict[int, int]:
    return {state.source_i27: state.local_index for state in canonical_generation_basis()}


def _q_source_ids() -> tuple[int, ...]:
    return tuple(state.source_i27 for state in left_spinor_basis() if state.sm == "Q")


def _u_source_ids() -> tuple[int, ...]:
    return tuple(state.source_i27 for state in right_spinor_basis() if state.sm == "u_c")


def _d_source_ids() -> tuple[int, ...]:
    return tuple(state.source_i27 for state in right_spinor_basis() if state.sm == "d_c")


def _left_q_local_indices() -> tuple[int, ...]:
    return tuple(state.local_index for state in left_spinor_basis() if state.sm == "Q")


def _right_u_local_indices() -> tuple[int, ...]:
    return tuple(state.local_index for state in right_spinor_basis() if state.sm == "u_c")


def _right_d_local_indices() -> tuple[int, ...]:
    return tuple(state.local_index for state in right_spinor_basis() if state.sm == "d_c")


@lru_cache(maxsize=1)
def ce2_generated_quark_source_units() -> tuple[CE2GeneratedUnitRecord, ...]:
    """All CE2-generated source matrix units on the exact quark-support 12-set."""

    q_sources = _q_source_ids()
    u_sources = _u_source_ids()
    d_sources = _d_source_ids()
    quark_sources = set(q_sources + u_sources + d_sources)
    families_by_pair: dict[tuple[int, int], set[str]] = {}

    for a_i, a_j, b_i, b_j, c_i, c_j in product(
        quark_sources,
        range(3),
        quark_sources,
        range(3),
        quark_sources,
        range(3),
    ):
        try:
            uv = predict_ce2_uv((a_i, a_j), (b_i, b_j), (c_i, c_j))
        except Exception:
            uv = None
        if uv is not None:
            for flat_index, _ in uv.U + uv.V:
                if flat_index < 27 * 27:
                    row_source, col_source = divmod(int(flat_index), 27)
                    if row_source in quark_sources and col_source in quark_sources:
                        families_by_pair.setdefault((row_source, col_source), set()).add(
                            "uv"
                        )

        try:
            uvw = predict_dual_g1g2g2_uvw((a_i, a_j), (b_i, b_j), (c_i, c_j))
        except Exception:
            uvw = None
        if uvw is not None:
            for flat_index, _ in uvw.U + uvw.V + uvw.W:
                if flat_index < 27 * 27:
                    row_source, col_source = divmod(int(flat_index), 27)
                    if row_source in quark_sources and col_source in quark_sources:
                        families_by_pair.setdefault((row_source, col_source), set()).add(
                            "uvw"
                        )

    state_by_source = _state_by_source()
    source_to_local = _source_to_local()
    records = []
    for row_source, col_source in sorted(families_by_pair):
        row_state = state_by_source[row_source]
        col_state = state_by_source[col_source]
        records.append(
            CE2GeneratedUnitRecord(
                source_row=row_source,
                source_col=col_source,
                local_row=source_to_local[row_source],
                local_col=source_to_local[col_source],
                row_slot=row_state.slot,
                col_slot=col_state.slot,
                row_sm=row_state.sm,
                col_sm=col_state.sm,
                generating_families=tuple(sorted(families_by_pair[(row_source, col_source)])),
            )
        )
    return tuple(records)


def ce2_generated_matrix_unit_27(source_row: int, source_col: int) -> np.ndarray:
    """The canonical 27x27 local matrix unit for one CE2-generated source pair."""

    record = next(
        (
            item
            for item in ce2_generated_quark_source_units()
            if item.source_row == source_row and item.source_col == source_col
        ),
        None,
    )
    if record is None:
        raise KeyError(f"Source matrix unit ({source_row}, {source_col}) is not CE2-generated")
    matrix = np.zeros((27, 27), dtype=float)
    matrix[record.local_row, record.local_col] = 1.0
    return matrix


def _projected_mode_from_record(record: CE2GeneratedUnitRecord) -> CE2ProjectedMode | None:
    q_sources = set(_q_source_ids())
    u_sources = set(_u_source_ids())
    d_sources = set(_d_source_ids())

    if record.source_row in q_sources and record.source_col in q_sources:
        kind = "left"
    elif record.source_row in u_sources and record.source_col in u_sources:
        kind = "up_right"
    elif record.source_row in d_sources and record.source_col in d_sources:
        kind = "down_right"
    else:
        return None

    return CE2ProjectedMode(
        kind=kind,
        source_row=record.source_row,
        source_col=record.source_col,
        local_row=record.local_row,
        local_col=record.local_col,
        generating_families=record.generating_families,
    )


@lru_cache(maxsize=1)
def ce2_projected_quark_bridge_modes() -> tuple[CE2ProjectedMode, ...]:
    records = []
    for unit in ce2_generated_quark_source_units():
        mode = _projected_mode_from_record(unit)
        if mode is not None:
            records.append(mode)
    return tuple(records)


def ce2_right_identity_up_27() -> np.ndarray:
    """CE2-generated identity on the canonical u_c source block."""

    total = np.zeros((27, 27), dtype=float)
    for source_pair in ((10, 10), (6, 6), (4, 4)):
        total += ce2_generated_matrix_unit_27(*source_pair)
    return total


def ce2_right_identity_down_27() -> np.ndarray:
    """CE2-generated identity on the canonical d_c source block."""

    total = np.zeros((27, 27), dtype=float)
    for source_pair in ((9, 9), (5, 5), (3, 3)):
        total += ce2_generated_matrix_unit_27(*source_pair)
    return total


def _block_from_matrix(matrix: np.ndarray, indices: tuple[int, ...]) -> np.ndarray:
    return matrix[np.ix_(indices, indices)]


def _response_column_from_mode(mode: CE2ProjectedMode) -> np.ndarray:
    original_up = _embedded_original_up()
    original_down = _embedded_original_down()
    q_rows = _quark_row_indices()
    up_cols = _up_col_indices()
    down_cols = _down_col_indices()
    up_block = original_up[np.ix_(q_rows, up_cols)]
    down_block = original_down[np.ix_(q_rows, down_cols)]
    zero_up = np.zeros_like(full_order_one_residual_vector_16(original_up))
    zero_down = np.zeros_like(full_order_one_residual_vector_16(original_down))

    matrix = ce2_generated_matrix_unit_27(mode.source_row, mode.source_col)
    if mode.kind == "left":
        q_block = _block_from_matrix(matrix, _left_q_local_indices())
        up = np.zeros((8, 8), dtype=float)
        down = np.zeros((8, 8), dtype=float)
        up[np.ix_(q_rows, up_cols)] = q_block @ up_block
        down[np.ix_(q_rows, down_cols)] = q_block @ down_block
        return np.concatenate(
            [full_order_one_residual_vector_16(up), full_order_one_residual_vector_16(down)]
        )

    if mode.kind == "up_right":
        u_block = _block_from_matrix(matrix, _right_u_local_indices())
        up = np.zeros((8, 8), dtype=float)
        up[np.ix_(q_rows, up_cols)] = up_block @ u_block
        return np.concatenate([full_order_one_residual_vector_16(up), zero_down])

    if mode.kind == "down_right":
        d_block = _block_from_matrix(matrix, _right_d_local_indices())
        down = np.zeros((8, 8), dtype=float)
        down[np.ix_(q_rows, down_cols)] = down_block @ d_block
        return np.concatenate([zero_up, full_order_one_residual_vector_16(down)])

    raise KeyError(f"Unknown CE2 projected mode kind: {mode.kind}")


def _trivial_closed_up_quark_yukawa_8x8() -> np.ndarray:
    """Exact trivial CE2 closure on the up-like quark block."""

    original = _embedded_original_up()
    q_rows = _quark_row_indices()
    up_cols = _up_col_indices()
    u_identity = _block_from_matrix(ce2_right_identity_up_27(), _right_u_local_indices())
    closed = original.copy()
    closed[np.ix_(q_rows, up_cols)] = original[np.ix_(q_rows, up_cols)] + original[
        np.ix_(q_rows, up_cols)
    ] @ (-u_identity)
    return closed


def _trivial_closed_down_quark_yukawa_8x8() -> np.ndarray:
    """Exact trivial CE2 closure on the down-like quark block."""

    original = _embedded_original_down()
    q_rows = _quark_row_indices()
    down_cols = _down_col_indices()
    d_identity = _block_from_matrix(ce2_right_identity_down_27(), _right_d_local_indices())
    closed = original.copy()
    closed[np.ix_(q_rows, down_cols)] = original[np.ix_(q_rows, down_cols)] + original[
        np.ix_(q_rows, down_cols)
    ] @ (-d_identity)
    return closed


def ce2_trivial_closed_up_quark_yukawa_8x8() -> np.ndarray:
    """Public wrapper for the canonical CE2 trivial closure on the up block."""

    return _trivial_closed_up_quark_yukawa_8x8().copy()


def ce2_trivial_closed_down_quark_yukawa_8x8() -> np.ndarray:
    """Public wrapper for the canonical CE2 trivial closure on the down block."""

    return _trivial_closed_down_quark_yukawa_8x8().copy()


def _arbitrary_quark_response_matrix() -> np.ndarray:
    columns = []
    for row_index in range(6):
        for col_index in range(3):
            yukawa = np.zeros((8, 8), dtype=float)
            yukawa[row_index, col_index] = 1.0
            columns.append(full_order_one_residual_vector_16(yukawa))
    for row_index in range(6):
        for col_index in range(3, 6):
            yukawa = np.zeros((8, 8), dtype=float)
            yukawa[row_index, col_index] = 1.0
            columns.append(full_order_one_residual_vector_16(yukawa))
    complex_matrix = np.stack(columns, axis=1)
    return np.vstack([complex_matrix.real, complex_matrix.imag])


def _max_l4_containment_error() -> float:
    ce2_complex = np.stack(
        [_response_column_from_mode(mode) for mode in ce2_projected_quark_bridge_modes()],
        axis=1,
    )
    ce2_real = np.vstack([ce2_complex.real, ce2_complex.imag])
    errors = []

    original_up = _embedded_original_up()
    original_down = _embedded_original_down()
    q_rows = _quark_row_indices()
    up_cols = _up_col_indices()
    down_cols = _down_col_indices()
    up_block = original_up[np.ix_(q_rows, up_cols)]
    down_block = original_down[np.ix_(q_rows, down_cols)]
    zero_up = np.zeros_like(full_order_one_residual_vector_16(original_up))
    zero_down = np.zeros_like(full_order_one_residual_vector_16(original_down))

    q_blocks, u_blocks, d_blocks = _basis_left_right_blocks()
    l4_columns = []
    for q_block in q_blocks:
        up = np.zeros((8, 8), dtype=float)
        down = np.zeros((8, 8), dtype=float)
        up[np.ix_(q_rows, up_cols)] = q_block @ up_block
        down[np.ix_(q_rows, down_cols)] = q_block @ down_block
        l4_columns.append(
            np.concatenate(
                [full_order_one_residual_vector_16(up), full_order_one_residual_vector_16(down)]
            )
        )
    for u_block in u_blocks:
        up = np.zeros((8, 8), dtype=float)
        up[np.ix_(q_rows, up_cols)] = up_block @ u_block
        l4_columns.append(np.concatenate([full_order_one_residual_vector_16(up), zero_down]))
    for d_block in d_blocks:
        down = np.zeros((8, 8), dtype=float)
        down[np.ix_(q_rows, down_cols)] = down_block @ d_block
        l4_columns.append(np.concatenate([zero_up, full_order_one_residual_vector_16(down)]))

    for column in l4_columns:
        target = np.concatenate([column.real, column.imag])
        coeffs, *_ = np.linalg.lstsq(ce2_real, target, rcond=None)
        errors.append(float(np.linalg.norm(ce2_real @ coeffs - target)))
    return max(errors)


@lru_cache(maxsize=1)
def build_ce2_quark_bridge_certificate() -> CE2QuarkBridgeCertificate:
    units = ce2_generated_quark_source_units()
    projected_modes = ce2_projected_quark_bridge_modes()
    projected_complex = np.stack(
        [_response_column_from_mode(mode) for mode in projected_modes],
        axis=1,
    )
    projected_real = np.vstack([projected_complex.real, projected_complex.imag])

    target = -np.concatenate(
        [
            full_order_one_residual_vector_16(_embedded_original_up()),
            full_order_one_residual_vector_16(_embedded_original_down()),
        ]
    )
    target_real = np.concatenate([target.real, target.imag])

    arbitrary_quark_real = _arbitrary_quark_response_matrix()

    uv_only = sum(1 for unit in units if unit.generating_families == ("uv",))
    uvw_only = sum(1 for unit in units if unit.generating_families == ("uvw",))
    overlap = sum(1 for unit in units if unit.generating_families == ("uv", "uvw"))

    trivial_up = _trivial_closed_up_quark_yukawa_8x8()
    trivial_down = _trivial_closed_down_quark_yukawa_8x8()
    total_trivial = float(
        np.linalg.norm(
            np.concatenate(
                [
                    full_order_one_residual_vector_16(trivial_up),
                    full_order_one_residual_vector_16(trivial_down),
                ]
            )
        )
    )
    max_l4_err = _max_l4_containment_error()

    return CE2QuarkBridgeCertificate(
        q_source_ids=_q_source_ids(),
        u_source_ids=_u_source_ids(),
        d_source_ids=_d_source_ids(),
        generated_source_unit_count=len(units),
        uv_only_source_unit_count=uv_only,
        uvw_only_source_unit_count=uvw_only,
        uv_and_uvw_source_unit_count=overlap,
        source_matrix_algebra_is_full=len(units) == 12 * 12,
        projected_mode_count=len(projected_modes),
        left_mode_count=sum(1 for mode in projected_modes if mode.kind == "left"),
        up_right_mode_count=sum(1 for mode in projected_modes if mode.kind == "up_right"),
        down_right_mode_count=sum(1 for mode in projected_modes if mode.kind == "down_right"),
        response_rank=int(np.linalg.matrix_rank(projected_real)),
        augmented_rank=int(np.linalg.matrix_rank(np.column_stack([projected_real, target_real]))),
        original_total_residual_norm=float(np.linalg.norm(target)),
        trivial_closure_total_residual_norm=total_trivial,
        trivial_closure_up_residual_norm=full_order_one_residual_norm_16(trivial_up),
        trivial_closure_down_residual_norm=full_order_one_residual_norm_16(trivial_down),
        arbitrary_quark_screen_rank=int(np.linalg.matrix_rank(arbitrary_quark_real)),
        arbitrary_quark_screen_nullity=int(
            arbitrary_quark_real.shape[1] - np.linalg.matrix_rank(arbitrary_quark_real)
        ),
        zero_is_unique_clean_point=bool(
            arbitrary_quark_real.shape[1] == np.linalg.matrix_rank(arbitrary_quark_real)
        ),
        l4_response_contained_in_ce2=bool(max_l4_err < 1e-12),
        max_l4_containment_error=max_l4_err,
        right_up_identity_source_pairs=((10, 10), (6, 6), (4, 4)),
        right_down_identity_source_pairs=((9, 9), (5, 5), (3, 3)),
        generated_units=units,
        projected_modes=projected_modes,
    )
