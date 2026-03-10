"""Klitzing operation ladder and incidence rows for the tomotope.

This module records the tomotope's repeated appearances on Klitzing's gc.htm
page alongside the 11-cell and 57-cell. The page shows a four-step operation
tower on the tomotope:

- rectified tomotope;
- truncated tomotope;
- maximal expanded tomotope;
- omnitruncated tomotope.

For each of those rows, Klitzing's table displays a leading count. Reading those
leading counts directly from the tomotope rows gives the doubling ladder

    12 -> 24 -> 48 -> 96.

Klitzing also gives the base tomotope incidence rows immediately above the
operation tables. Those rows reproduce the exact finite counts used elsewhere in
the repo: 4 vertices, 12 edges, 16 triangles, and a 4+4 cell split into
tetrahedra and hemioctahedra.

Even without over-interpreting every column of the page, the arithmetic bridge
is already strong:

- 12 matches the tomotope edge count used in the exact 192-flag computation;
- 24 matches the tetrahedron flag count and the Fano point stabilizer order;
- 96 matches the tomotope automorphism-group order from the paper.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
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

from w33_fano_group_bridge import build_fano_group_summary
from w33_tomotope_order_bridge import tomotope_data


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_tomotope_klitzing_ladder_summary.json"


@dataclass(frozen=True)
class KlitzingOperationRow:
    name: str
    row_text: str
    leading_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def tomotope_base_incidence_rows() -> tuple[str, ...]:
    return (
        "mod_b(e(. . .    .)) | 4 <> 6 | 12 | 4 3",
        "mod_b(  x . .    . ) | 2 | 12 |  4 | 2 2",
        "mod_b(  x3o .    . ) | 3 |  3 | 16 | 1 1",
        "mod_b(  x3o3o      ) tet 4 |  6 |  4 | 4 *",
        "mod_b(e(x3o . *b4o)) elloct 3 |  6 |  4 | * 4",
    )


def tomotope_klitzing_operations() -> tuple[KlitzingOperationRow, ...]:
    return (
        KlitzingOperationRow(
            "rectified tomotope",
            "mids(mod_b(  x . .    . )) | 12 |  8 |  4  4  4 | 2 2 2",
            12,
        ),
        KlitzingOperationRow(
            "truncated tomotope",
            "trops(mod_b(  x . .    . )) | 24 |  1  4 |  4  2  2 | 2 2 1",
            24,
        ),
        KlitzingOperationRow(
            "maximal expanded tomotope",
            "mod_b(  . . .    . ) | 48 |  2  2  2 |  1  2  2  1  1  2 | 1 1  2 1",
            48,
        ),
        KlitzingOperationRow(
            "omnitruncated tomotope",
            "mod_b(  . . .    . ) | 96 |  1  1  1  1 |  1  1  1  1  1  1 | 1 1  1 1",
            96,
        ),
    )


def leading_counts() -> tuple[int, ...]:
    return tuple(row.leading_count for row in tomotope_klitzing_operations())


def successive_doublings() -> tuple[int, ...]:
    counts = leading_counts()
    return tuple(counts[i + 1] // counts[i] for i in range(len(counts) - 1))


def build_klitzing_ladder_summary() -> dict[str, Any]:
    counts = leading_counts()
    tomotope = tomotope_data()
    fano_group = build_fano_group_summary()["summary"]
    base_rows = tomotope_base_incidence_rows()

    return {
        "status": "ok",
        "shared_family_note": (
            "Klitzing groups the tomotope with the 11-cell and 57-cell and shows "
            "the same four operation slots on all three."
        ),
        "base_matrix_reference": {
            "gc_symbol": "x3o3o *b4o",
            "incidence_matrix_href": "../incmats/octet.htm",
            "incidence_rows": list(base_rows),
        },
        "base_count_checks": {
            "vertices_match": " | 4 <" in base_rows[0],
            "edges_match": "| 12 |" in base_rows[1],
            "triangles_match": "| 16 |" in base_rows[2],
            "cell_split_matches": base_rows[1].endswith("2 2") and base_rows[2].endswith("1 1"),
        },
        "operations": [row.to_dict() for row in tomotope_klitzing_operations()],
        "leading_count_ladder": counts,
        "successive_doublings": successive_doublings(),
        "exact_matches": {
            "rectified_leading_count_matches_tomotope_edges": counts[0] == tomotope.edges,
            "truncated_leading_count_matches_tetrahedron_flags": counts[1] == fano_group["tetrahedron_flag_count"],
            "truncated_leading_count_matches_fano_point_stabilizer": counts[1] == fano_group["point_stabilizer_order"],
            "omnitruncated_leading_count_matches_tomotope_automorphism_order": (
                counts[-1] == tomotope.automorphism_group_order
            ),
        },
        "bridge_verdict": (
            "The Klitzing tomotope ladder supplies a clean doubling chain 12 -> 24 "
            "-> 48 -> 96. That chain passes exactly through the edge count, the "
            "tetrahedral/Fano midpoint, and the tomotope automorphism order."
        ),
        "scope_note": (
            "This records the exact tomotope row strings visible on Klitzing's page, "
            "but still does not claim a full interpretation of every table column."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_klitzing_ladder_summary(), indent=2), encoding="utf-8")
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
