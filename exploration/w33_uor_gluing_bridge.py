"""UOR-style local-to-global gluing theorem for the canonical V4 flavour seed.

The external UOR framework's most relevant sheaf clue is local-vs-global
consistency: local sections can fail to glue, and the right invariant is not a
count but the existence and uniqueness of a global section.

The exact l6 flavour program now has a clean finite instance of that pattern.
The canonical label matrix

    [[AB, I, A],
     [AB, I, A],
     [ A, B, 0]]

can be reconstructed from four exact local sections furnished by the two
minimal A2 closure routes:

  - forward fan row;
  - reverse fan column;
  - forward completion on the top two rows;
  - reverse completion on the left two columns.

These local sections overlap compatibly and glue to one unique global section
for both H_2 and Hbar_2. This is the strongest UOR-style gluing clue in the
current repo: the open problem is no longer whether the exact flavour data
glues, but what deeper operator principle selects those local sections.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_l6_v4_closure_selection_bridge import (
    FORWARD_FAN,
    REVERSE_FAN,
    _completion_delta,
    _fan_seed,
    _matrix_labels,
)
from w33_l6_v4_seed_reconstruction_bridge import _label_matrix


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_uor_gluing_bridge_summary.json"
GRID_CELLS = tuple((row, col) for row in range(3) for col in range(3))


def _row_cells(row: int) -> tuple[tuple[int, int], ...]:
    return tuple((row, col) for col in range(3))


def _column_cells(col: int) -> tuple[tuple[int, int], ...]:
    return tuple((row, col) for row in range(3))


def _top_two_rows() -> tuple[tuple[int, int], ...]:
    return tuple((row, col) for row in (0, 1) for col in range(3))


def _left_two_columns() -> tuple[tuple[int, int], ...]:
    return tuple((row, col) for row in range(3) for col in (0, 1))


def _section_from_cells(
    label_matrix: tuple[tuple[str, ...], ...],
    cells: tuple[tuple[int, int], ...],
) -> dict[str, str]:
    return {
        f"{row},{col}": label_matrix[row][col]
        for row, col in cells
    }


def _merge_sections(sections: dict[str, dict[str, str]]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for section in sections.values():
        for cell, label in section.items():
            if cell in merged and merged[cell] != label:
                raise AssertionError("local sections do not glue consistently")
            merged[cell] = label
    return merged


def _pairwise_overlap_data(
    sections: dict[str, dict[str, str]]
) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    names = list(sections)
    for index, left_name in enumerate(names):
        left = sections[left_name]
        for right_name in names[index + 1 :]:
            right = sections[right_name]
            overlap_cells = sorted(set(left) & set(right))
            rows[f"{left_name} & {right_name}"] = {
                "cells": overlap_cells,
                "consistent": all(left[cell] == right[cell] for cell in overlap_cells),
            }
    return rows


def _matrix_from_merged_section(merged: dict[str, str]) -> tuple[tuple[str, ...], ...]:
    rows = []
    for row in range(3):
        rows.append(tuple(merged[f"{row},{col}"] for col in range(3)))
    return tuple(rows)


def _slot_cover_profile(external_slot: str) -> dict[str, Any]:
    forward_seed = _matrix_labels(
        external_slot,
        _fan_seed(external_slot, FORWARD_FAN),
        subtract_base_on_diagonal=True,
    )
    reverse_seed = _matrix_labels(
        external_slot,
        _fan_seed(external_slot, REVERSE_FAN),
        subtract_base_on_diagonal=True,
    )
    forward_completion = _matrix_labels(
        external_slot,
        _completion_delta(external_slot, FORWARD_FAN, REVERSE_FAN),
        subtract_base_on_diagonal=False,
    )
    reverse_completion = _matrix_labels(
        external_slot,
        _completion_delta(external_slot, REVERSE_FAN, FORWARD_FAN),
        subtract_base_on_diagonal=False,
    )
    canonical = _label_matrix(external_slot)

    sections = {
        "forward_row": _section_from_cells(forward_seed, _row_cells(2)),
        "reverse_column": _section_from_cells(reverse_seed, _column_cells(2)),
        "top_rows_completion": _section_from_cells(forward_completion, _top_two_rows()),
        "left_columns_completion": _section_from_cells(reverse_completion, _left_two_columns()),
    }
    merged = _merge_sections(sections)
    overlaps = _pairwise_overlap_data(sections)
    route_forward = _merge_sections(
        {
            "forward_row": sections["forward_row"],
            "top_rows_completion": sections["top_rows_completion"],
        }
    )
    route_reverse = _merge_sections(
        {
            "reverse_column": sections["reverse_column"],
            "left_columns_completion": sections["left_columns_completion"],
        }
    )

    return {
        "local_sections": sections,
        "pairwise_overlaps": overlaps,
        "covered_cells": sorted(merged),
        "all_cells_covered": sorted(merged) == [f"{row},{col}" for row, col in GRID_CELLS],
        "pairwise_compatible": all(value["consistent"] for value in overlaps.values()),
        "merged_global_section": [list(row) for row in _matrix_from_merged_section(merged)],
        "forward_route_global_section": [
            list(row) for row in _matrix_from_merged_section(route_forward)
        ],
        "reverse_route_global_section": [
            list(row) for row in _matrix_from_merged_section(route_reverse)
        ],
        "canonical_global_section": [list(row) for row in canonical],
    }


@lru_cache(maxsize=1)
def build_w33_uor_gluing_summary() -> dict[str, Any]:
    slot_profiles = {
        external_slot: _slot_cover_profile(external_slot)
        for external_slot in ("H_2", "Hbar_2")
    }
    expected = [["AB", "I", "A"], ["AB", "I", "A"], ["A", "B", "0"]]

    return {
        "status": "ok",
        "slot_profiles": slot_profiles,
        "gluing_theorem": {
            "all_pairwise_overlaps_are_compatible_for_both_slots": all(
                profile["pairwise_compatible"] for profile in slot_profiles.values()
            ),
            "all_cells_are_covered_for_both_slots": all(
                profile["all_cells_covered"] for profile in slot_profiles.values()
            ),
            "forward_route_glues_to_canonical_section_for_both_slots": all(
                profile["forward_route_global_section"] == expected
                for profile in slot_profiles.values()
            ),
            "reverse_route_glues_to_canonical_section_for_both_slots": all(
                profile["reverse_route_global_section"] == expected
                for profile in slot_profiles.values()
            ),
            "full_cover_has_unique_global_section_for_both_slots": all(
                profile["merged_global_section"] == expected
                for profile in slot_profiles.values()
            ),
            "canonical_global_section_is_slot_independent": all(
                profile["canonical_global_section"] == expected
                for profile in slot_profiles.values()
            ),
        },
        "bridge_verdict": (
            "The canonical V4 flavour matrix is now a genuine local-to-global "
            "gluing object. Four exact local sections coming from the two minimal "
            "A2 closure routes overlap compatibly, cover the full 3x3 generation "
            "grid, and glue to one unique global section for both H_2 and Hbar_2. "
            "So the current flavour bottleneck is no longer gluing failure; it is "
            "the deeper selection principle that produces those exact local sections."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_w33_uor_gluing_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
