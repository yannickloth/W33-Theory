"""Exact localization of the induced quark obstruction.

This module ties the remaining induced quark residual to the exact repo-side
firewall, Heisenberg/qutrit, and E6 channel structure.

What is implemented:
  - the 9 canonical firewall bad triads as 9 Heisenberg fibers of H27;
  - their exact split into singlet/Higgs, leptonic, antiquark-triplet, and
    quark-triplet sectors;
  - localization of the induced quark support on the six triplet fibers;
  - a heavy-sector test showing that removing T/Tbar kills all induced quark
    support while leaving the clean leptonic support intact;
  - a stronger SU(3)xSU(2) generator screen showing the current quark branch
    has no nonzero fully clean block.

What is not claimed:
  - a final Standard Model quark derivation;
  - removal of the triplet/firewall obstruction;
  - the missing 4D refinement/scaling theorem.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

from w33_finite_spectral_triple import BasisState, canonical_generation_basis
from w33_fermionic_connes_sector import (
    canonical_spinor_basis,
    color_generator_16,
    color_generator_names,
    fermionic_dirac_from_yukawa_16,
    left_spinor_basis,
    right_spinor_basis,
    weak_generator_16,
    weak_generator_names,
)
from w33_induced_quark_yukawa import (
    DEFAULT_BACKGROUND_COEFFS,
    build_induced_quark_yukawa_candidate,
    heavy_background_matrix_11,
    heavy_sector_basis,
    induced_component_blocks,
)


ROOT = Path(__file__).resolve().parents[1]
FIREWALL_PATH = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"
HIGGS_CHARGE_BY_SLOT = {
    "H_2": Fraction(1, 2),
    "Hbar_2": Fraction(-1, 2),
}
TRIPLET_HEAVY_SLOTS = ("T_1", "T_2", "T_3", "Tbar_1", "Tbar_2", "Tbar_3")
NONTRIPLET_HEAVY_SLOTS = ("S", "H_1", "H_2", "Hbar_1", "Hbar_2")
FLOAT_TOL = 1e-10


@dataclass(frozen=True)
class FirewallTriadRecord:
    """One canonical firewall bad triad."""

    triad_index: int
    heisenberg_xy: tuple[int, int]
    e6ids: tuple[int, int, int]
    slots: tuple[str, str, str]
    sms: tuple[str, str, str]
    family: str


@dataclass(frozen=True)
class HeavySubsetSupport:
    """Projected support for one heavy-sector subset."""

    kept_slots: tuple[str, ...]
    up_quark_support: int
    down_quark_support: int
    up_lepton_support: int
    down_lepton_support: int


@dataclass(frozen=True)
class GeneratorScreenSummary:
    """Nullity of the quark block under the partial and full screens."""

    sample_weak_count: int
    sample_color_count: int
    sample_up_nullity: int
    sample_down_nullity: int
    full_weak_count: int
    full_color_count: int
    full_up_nullity: int
    full_down_nullity: int


@dataclass(frozen=True)
class QuarkSupportEntry:
    """One nonzero induced quark-support entry."""

    channel: str
    left_slot: str
    right_slot: str
    left_e6id: int
    right_e6id: int
    left_triad_index: int
    right_triad_index: int
    value: Fraction


@dataclass(frozen=True)
class QuarkFirewallObstruction:
    """Executable summary of the current quark obstruction."""

    firewall_triads: tuple[FirewallTriadRecord, ...]
    quark_triad_indices: tuple[int, ...]
    antiquark_triad_indices: tuple[int, ...]
    triplet_heavy_slots: tuple[str, ...]
    support_light_source_e6ids: tuple[int, ...]
    up_triplet_pairs: tuple[tuple[int, int], ...]
    down_triplet_pairs: tuple[tuple[int, int], ...]
    heavy_subset_support: tuple[HeavySubsetSupport, ...]
    quark_support_vanishes_without_triplets: bool
    leptonic_support_survives_without_triplets: bool
    triplet_only_support_is_quark_only: bool
    screen_summary: GeneratorScreenSummary
    full_clean_quark_block_exists: bool


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to import {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _left_row_indices(sm: str) -> tuple[int, ...]:
    return tuple(idx for idx, state in enumerate(left_spinor_basis()) if state.sm == sm)


def _right_col_indices(sm: str) -> tuple[int, ...]:
    return tuple(
        idx for idx, state in enumerate(right_spinor_basis()) if state.sm == sm
    )


@lru_cache(maxsize=1)
def _source_state_by_e6id() -> dict[int, BasisState]:
    return {state.source_i27: state for state in canonical_generation_basis()}


@lru_cache(maxsize=1)
def _firewall_mapping() -> dict[str, object]:
    return json.loads(FIREWALL_PATH.read_text(encoding="utf-8"))


def _classify_triad_family(sms: tuple[str, str, str]) -> str:
    key = tuple(sorted(sms))
    if key == ("H", "Hbar", "S"):
        return "singlet_higgs"
    if key == ("Hbar", "L", "e_c"):
        return "lepton_down"
    if key == ("H", "L", "nu_c"):
        return "lepton_up"
    if key == ("Q", "Q", "T"):
        return "quark_triplet"
    if key == ("Tbar", "d_c", "u_c"):
        return "antiquark_triplet"
    raise ValueError(f"Unrecognized firewall triad family: {sms}")


@lru_cache(maxsize=1)
def _heisenberg_xy_by_triad_index() -> tuple[tuple[int, int], ...]:
    heisenberg = _load_module(
        ROOT / "scripts" / "w33_heisenberg_qutrit.py",
        "w33_heisenberg_qutrit_for_quark_firewall",
    )
    homology = _load_module(
        ROOT / "scripts" / "w33_homology.py",
        "w33_homology_for_quark_firewall",
    )
    n, _, adj, _ = homology.build_w33()
    adj_s = [set(adj[i]) for i in range(n)]
    n12, h27, triangles, _ = heisenberg.compute_local_structure(0, n, adj_s)
    _, vertex_to_xyz = heisenberg.build_f3_cube(n12, h27, triangles, adj_s)

    coords = []
    for triad in _firewall_mapping()["bad_triangles_H27_local"]:
        xy_values = {
            (vertex_to_xyz[h27[int(local)]][0], vertex_to_xyz[h27[int(local)]][1])
            for local in triad
        }
        if len(xy_values) != 1:
            raise ValueError("Firewall triad should lie in one Heisenberg fiber")
        coords.append(next(iter(xy_values)))
    return tuple(coords)


@lru_cache(maxsize=1)
def firewall_triad_records() -> tuple[FirewallTriadRecord, ...]:
    source_state = _source_state_by_e6id()
    triads = _firewall_mapping()["bad_triangles_Schlafli_e6id"]
    coords = _heisenberg_xy_by_triad_index()
    records = []
    for triad_index, triad in enumerate(triads):
        e6ids = tuple(int(value) for value in triad)
        states = tuple(source_state[e6id] for e6id in e6ids)
        records.append(
            FirewallTriadRecord(
                triad_index=triad_index,
                heisenberg_xy=coords[triad_index],
                e6ids=e6ids,
                slots=tuple(state.slot for state in states),
                sms=tuple(state.sm for state in states),
                family=_classify_triad_family(tuple(state.sm for state in states)),
            )
        )
    return tuple(records)


@lru_cache(maxsize=1)
def triad_index_by_e6id() -> dict[int, int]:
    out = {}
    for record in firewall_triad_records():
        for e6id in record.e6ids:
            out[e6id] = record.triad_index
    return out


def _full_weak_generator_16(name: str) -> np.ndarray:
    generators = {
        "sigma_x": np.array([[0, 1], [1, 0]], dtype=complex),
        "sigma_y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "sigma_z": np.array([[1, 0], [0, -1]], dtype=complex),
    }
    if name not in generators:
        raise KeyError(f"Unknown weak generator: {name}")

    operator = np.eye(16, dtype=complex)
    block = generators[name]
    for start in (0, 2, 4, 6):
        indices = (start, start + 1)
        operator[np.ix_(indices, indices)] = block
    return operator


def _full_color_generator_16(name: str) -> np.ndarray:
    generators = {
        "lambda_1": np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=complex),
        "lambda_2": np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=complex),
        "lambda_3": np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=complex),
        "lambda_4": np.array([[0, 0, 1], [0, 0, 0], [1, 0, 0]], dtype=complex),
        "lambda_5": np.array([[0, 0, -1j], [0, 0, 0], [1j, 0, 0]], dtype=complex),
        "lambda_6": np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=complex),
        "lambda_7": np.array([[0, 0, 0], [0, 0, -1j], [0, 1j, 0]], dtype=complex),
        "lambda_8": (1.0 / np.sqrt(3.0))
        * np.array([[1, 0, 0], [0, 1, 0], [0, 0, -2]], dtype=complex),
    }
    if name not in generators:
        raise KeyError(f"Unknown color generator: {name}")

    color = generators[name]
    operator = np.eye(16, dtype=complex)
    operator[np.ix_(range(0, 6), range(0, 6))] = np.kron(
        color, np.eye(2, dtype=complex)
    )
    operator[np.ix_(range(8, 11), range(8, 11))] = np.conjugate(color)
    operator[np.ix_(range(11, 14), range(11, 14))] = np.conjugate(color)
    return operator


def full_order_one_residual_vector_16(yukawa: np.ndarray) -> np.ndarray:
    """Flatten the full SU(3)xSU(2) order-one residual on the spinor 16."""

    dirac = fermionic_dirac_from_yukawa_16(yukawa)
    vectors = []
    for weak_name in ("sigma_x", "sigma_y", "sigma_z"):
        weak = _full_weak_generator_16(weak_name)
        for color_name in (
            "lambda_1",
            "lambda_2",
            "lambda_3",
            "lambda_4",
            "lambda_5",
            "lambda_6",
            "lambda_7",
            "lambda_8",
        ):
            color = _full_color_generator_16(color_name)
            residual = (dirac @ weak - weak @ dirac) @ color - color @ (
                dirac @ weak - weak @ dirac
            )
            vectors.append(residual.reshape(-1))
    return np.concatenate(vectors)


def full_order_one_residual_norm_16(yukawa: np.ndarray) -> float:
    """Norm of the full SU(3)xSU(2) order-one residual on the spinor 16."""

    return float(np.linalg.norm(full_order_one_residual_vector_16(yukawa)))


def _quark_block_residual_vector(
    block: np.ndarray,
    right_cols: tuple[int, ...],
    weak_operators: tuple[np.ndarray, ...],
    color_operators: tuple[np.ndarray, ...],
) -> np.ndarray:
    yukawa = np.zeros((8, 8), dtype=complex)
    yukawa[np.ix_(_left_row_indices("Q"), right_cols)] = block
    dirac = fermionic_dirac_from_yukawa_16(yukawa)
    vectors = []
    for weak in weak_operators:
        for color in color_operators:
            residual = (dirac @ weak - weak @ dirac) @ color - color @ (
                dirac @ weak - weak @ dirac
            )
            vectors.append(residual.reshape(-1))
    return np.concatenate(vectors)


def _screen_nullity(
    right_sm: str,
    *,
    use_full_generators: bool,
) -> int:
    right_cols = _right_col_indices(right_sm)
    if use_full_generators:
        weak_operators = tuple(
            _full_weak_generator_16(name)
            for name in ("sigma_x", "sigma_y", "sigma_z")
        )
        color_operators = tuple(
            _full_color_generator_16(name)
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
    else:
        weak_operators = tuple(
            weak_generator_16(name) for name in weak_generator_names()
        )
        color_operators = tuple(
            color_generator_16(name) for name in color_generator_names()
        )

    basis_vectors = []
    for row in range(len(_left_row_indices("Q"))):
        for col in range(len(right_cols)):
            block = np.zeros((6, 3), dtype=float)
            block[row, col] = 1.0
            basis_vectors.append(
                _quark_block_residual_vector(
                    block, right_cols, weak_operators, color_operators
                )
            )
    matrix = np.stack(basis_vectors, axis=1)
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    rank = int(np.sum(singular_values > FLOAT_TOL))
    return int(matrix.shape[1] - rank)


def _support_count(matrix: np.ndarray) -> int:
    return int(np.count_nonzero(np.abs(matrix) > FLOAT_TOL))


def _projected_yukawa_with_subset(
    external_slot: str,
    kept_slots: tuple[str, ...],
) -> np.ndarray:
    heavy_slots = tuple(state.slot for state in heavy_sector_basis())
    keep_indices = tuple(
        idx for idx, slot in enumerate(heavy_slots) if slot in set(kept_slots)
    )
    background = np.array(heavy_background_matrix_11(DEFAULT_BACKGROUND_COEFFS), dtype=float)
    background = background[np.ix_(keep_indices, keep_indices)]
    if np.linalg.matrix_rank(background) == 0:
        raise ValueError("Heavy subset is degenerate")

    light_to_heavy, heavy_to_light = induced_component_blocks()[external_slot]
    induced = -(
        np.array(light_to_heavy, dtype=float)[:, keep_indices]
        @ np.linalg.pinv(background)
        @ np.array(heavy_to_light, dtype=float)[keep_indices, :]
    )

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


def _heavy_subset_support(kept_slots: tuple[str, ...]) -> HeavySubsetSupport:
    up = _projected_yukawa_with_subset("H_2", kept_slots)
    down = _projected_yukawa_with_subset("Hbar_2", kept_slots)

    up_quark = np.zeros_like(up)
    down_quark = np.zeros_like(down)
    up_lepton = np.zeros_like(up)
    down_lepton = np.zeros_like(down)

    up_quark[np.ix_(_left_row_indices("Q"), _right_col_indices("u_c"))] = up[
        np.ix_(_left_row_indices("Q"), _right_col_indices("u_c"))
    ]
    down_quark[np.ix_(_left_row_indices("Q"), _right_col_indices("d_c"))] = down[
        np.ix_(_left_row_indices("Q"), _right_col_indices("d_c"))
    ]
    up_lepton[np.ix_(_left_row_indices("L"), _right_col_indices("nu_c"))] = up[
        np.ix_(_left_row_indices("L"), _right_col_indices("nu_c"))
    ]
    down_lepton[np.ix_(_left_row_indices("L"), _right_col_indices("e_c"))] = down[
        np.ix_(_left_row_indices("L"), _right_col_indices("e_c"))
    ]

    return HeavySubsetSupport(
        kept_slots=kept_slots,
        up_quark_support=_support_count(up_quark),
        down_quark_support=_support_count(down_quark),
        up_lepton_support=_support_count(up_lepton),
        down_lepton_support=_support_count(down_lepton),
    )


def _quark_support_entries() -> tuple[QuarkSupportEntry, ...]:
    triad_by_e6id = triad_index_by_e6id()
    candidate = build_induced_quark_yukawa_candidate()
    entries = []
    for channel, grid in (
        ("up", candidate.up_channel.quark_matrix_8x8),
        ("down", candidate.down_channel.quark_matrix_8x8),
    ):
        right_sm = "u_c" if channel == "up" else "d_c"
        for row_index, left_state in enumerate(left_spinor_basis()):
            if left_state.sm != "Q":
                continue
            for col_index, right_state in enumerate(right_spinor_basis()):
                if right_state.sm != right_sm:
                    continue
                value = grid[row_index][col_index]
                if value == Fraction(0, 1):
                    continue
                entries.append(
                    QuarkSupportEntry(
                        channel=channel,
                        left_slot=left_state.slot,
                        right_slot=right_state.slot,
                        left_e6id=left_state.source_i27,
                        right_e6id=right_state.source_i27,
                        left_triad_index=triad_by_e6id[left_state.source_i27],
                        right_triad_index=triad_by_e6id[right_state.source_i27],
                        value=value,
                    )
                )
    return tuple(entries)


@lru_cache(maxsize=1)
def build_quark_firewall_obstruction() -> QuarkFirewallObstruction:
    triads = firewall_triad_records()
    entries = _quark_support_entries()
    up_pairs = sorted(
        {
            (entry.left_triad_index, entry.right_triad_index)
            for entry in entries
            if entry.channel == "up"
        }
    )
    down_pairs = sorted(
        {
            (entry.left_triad_index, entry.right_triad_index)
            for entry in entries
            if entry.channel == "down"
        }
    )
    support_e6ids = sorted(
        {entry.left_e6id for entry in entries} | {entry.right_e6id for entry in entries}
    )

    subset_nontriplet = _heavy_subset_support(NONTRIPLET_HEAVY_SLOTS)
    subset_triplet = _heavy_subset_support(TRIPLET_HEAVY_SLOTS + ("S",))
    subset_full = _heavy_subset_support(
        tuple(state.slot for state in heavy_sector_basis())
    )

    screen = GeneratorScreenSummary(
        sample_weak_count=len(weak_generator_names()),
        sample_color_count=len(color_generator_names()),
        sample_up_nullity=_screen_nullity("u_c", use_full_generators=False),
        sample_down_nullity=_screen_nullity("d_c", use_full_generators=False),
        full_weak_count=3,
        full_color_count=8,
        full_up_nullity=_screen_nullity("u_c", use_full_generators=True),
        full_down_nullity=_screen_nullity("d_c", use_full_generators=True),
    )

    return QuarkFirewallObstruction(
        firewall_triads=triads,
        quark_triad_indices=tuple(
            record.triad_index
            for record in triads
            if record.family == "quark_triplet"
        ),
        antiquark_triad_indices=tuple(
            record.triad_index
            for record in triads
            if record.family == "antiquark_triplet"
        ),
        triplet_heavy_slots=TRIPLET_HEAVY_SLOTS,
        support_light_source_e6ids=tuple(support_e6ids),
        up_triplet_pairs=tuple(up_pairs),
        down_triplet_pairs=tuple(down_pairs),
        heavy_subset_support=(subset_full, subset_nontriplet, subset_triplet),
        quark_support_vanishes_without_triplets=(
            subset_nontriplet.up_quark_support == 0
            and subset_nontriplet.down_quark_support == 0
        ),
        leptonic_support_survives_without_triplets=(
            subset_nontriplet.up_lepton_support > 0
            and subset_nontriplet.down_lepton_support > 0
        ),
        triplet_only_support_is_quark_only=(
            subset_triplet.up_quark_support > 0
            and subset_triplet.down_quark_support > 0
            and subset_triplet.up_lepton_support == 0
            and subset_triplet.down_lepton_support == 0
        ),
        screen_summary=screen,
        full_clean_quark_block_exists=(
            screen.full_up_nullity > 0 or screen.full_down_nullity > 0
        ),
    )
