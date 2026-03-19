"""Exact partial-a / partial-b sheet split on Klitzing's tomotope rows.

Klitzing's ``gc.htm`` page lists two adjacent seed tables for

    GC(x3o3o *b4o):

- ``partial a`` (Monson-Schulte);
- ``partial b`` ("Tomotope", Monson-Pellicer-Williams).

Reading the principal counts row-by-row gives the packets

    partial_a = (8, 24, 32, 8, 8),
    partial_b = (4, 12, 16, 4, 4).

So the visible page-level relation is exact:

    partial_a = 2 * partial_b.

The lower four slots already land on live promoted data:

- partial-b reproduces the tomotope edge/triangle/cell counts (12,16,4,4);
- partial-a reproduces the universal tetrahedron-hemioctahedron
  edge/triangle/cell counts (24,32,8,8).

At the same time the monodromy orders still differ by 4, not by 2:

    73728 / 18432 = 4.

So the exact page-level doubling law is a genuine two-sheet count collapse, not
just a restatement of the full cover-order tower.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from w33_tomotope_order_bridge import (
    tomotope_data,
    universal_tetrahedron_hemioctahedron_data,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_tomotope_partial_sheet_bridge_summary.json"


def partial_a_rows() -> tuple[str, ...]:
    return (
        "mod_a(e(. . .    .)) | 8 ♦  6 | 12 | 4 3",
        "mod_a(  x . .    . ) | 2 | 24 |  4 | 2 2",
        "mod_a(  x3o .    . ) | 3 |  3 | 32 | 1 1",
        "mod_a(  x3o3o      ) ♦ 4 |  6 |  4 | 8 *",
        "mod_a(e(x3o . *b4o)) ♦ 3 |  6 |  4 | * 8",
    )


def partial_b_rows() -> tuple[str, ...]:
    return (
        "mod_b(e(. . .    .)) | 4 ♦  6 | 12 | 4 3",
        "mod_b(  x . .    . ) | 2 | 12 |  4 | 2 2",
        "mod_b(  x3o .    . ) | 3 |  3 | 16 | 1 1",
        "mod_b(  x3o3o      ) ♦ 4 |  6 |  4 | 4 *",
        "mod_b(e(x3o . *b4o)) ♦ 3 |  6 |  4 | * 4",
    )


def partial_a_principal_counts() -> tuple[int, int, int, int, int]:
    return (8, 24, 32, 8, 8)


def partial_b_principal_counts() -> tuple[int, int, int, int, int]:
    return (4, 12, 16, 4, 4)


def build_tomotope_partial_sheet_summary() -> dict[str, Any]:
    partial_a = partial_a_principal_counts()
    partial_b = partial_b_principal_counts()
    universal = universal_tetrahedron_hemioctahedron_data()
    tomotope = tomotope_data()
    ratio = tuple(a // b for a, b in zip(partial_a, partial_b))

    return {
        "status": "ok",
        "source_anchor": {
            "url": "https://bendwavy.org/klitzing/explain/gc.htm",
            "symbol": "GC(x3o3o *b4o)",
            "partial_a_rows": list(partial_a_rows()),
            "partial_b_rows": list(partial_b_rows()),
        },
        "principal_packets": {
            "partial_a": list(partial_a),
            "partial_b": list(partial_b),
            "entrywise_ratio": list(ratio),
            "partial_a_equals_two_times_partial_b": all(x == 2 for x in ratio),
            "partial_difference_equals_partial_b": [a - b for a, b in zip(partial_a, partial_b)] == list(partial_b),
        },
        "live_count_alignment": {
            "partial_b_matches_tomotope_edge_triangle_cell_counts": list(partial_b[1:]) == [
                tomotope.edges,
                tomotope.triangles,
                tomotope.tetrahedra,
                tomotope.hemioctahedra,
            ],
            "partial_a_matches_universal_edge_triangle_cell_counts": list(partial_a[1:]) == [
                universal.edges,
                universal.triangles,
                universal.tetrahedra,
                universal.hemioctahedra,
            ],
            "automorphism_ratio_matches_sheet_doubling": (
                universal.automorphism_group_order // tomotope.automorphism_group_order == 2
            ),
            "flag_ratio_matches_sheet_doubling": universal.flags // tomotope.flags == 2,
            "monodromy_ratio_is_quadratic_not_linear": (
                universal.monodromy_group_order // tomotope.monodromy_group_order == 4
            ),
        },
        "bridge_verdict": (
            "Klitzing's partial-a / partial-b tomotope seed rows obey an exact "
            "sheet law: (8,24,32,8,8) = 2*(4,12,16,4,4). The lower four slots land "
            "exactly on the universal/tomotope edge-triangle-cell packets, while "
            "the monodromy ratio stays 4 rather than 2, so this is a genuine "
            "two-sheet count collapse rather than a restatement of the cover tower."
        ),
        "scope_note": (
            "This promotes the exact page-level doubling law only. Interpreting it "
            "as a central involution, defect operator, or nonlinear correction axis "
            "is still a model continuation rather than a proved theorem."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_tomotope_partial_sheet_summary(), indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    write_summary()
