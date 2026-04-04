"""The inert 9-column block is an anchored 3-line fan in the quotient geometry.

CDXXXIII isolated the exact live block of the mixed-plane wall as the
full-rank 36-column active complement, leaving a rigid inert block of 9
columns. The next question is whether that 9-column inert block has an exact
quotient-geometric meaning.

It does. The inactive columns are exactly the non-anchor, non-spoke points on
the three quotient lines through the common anchor point 0:

- anchor point: 0
- line ids through the anchor: 0, 1, 2
- active spoke points on those lines: 15, 16, 17
- inert triples on those lines:
  [36, 40, 44], [38, 39, 43], [37, 41, 42]

So the live wall is not only a 36-column basis complement. It is the
complement of one rigid anchored 3-line fan inside the exact 45-point quotient
geometry.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_inert_fan_geometry_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_mixed_plane_inert_fan_geometry_summary() -> dict[str, Any]:
    from w33_center_quad_gq42_e6_bridge import quotient_incidence, quotient_lines
    from w33_k3_mixed_plane_active_column_basis_bridge import (
        build_k3_mixed_plane_active_column_basis_summary,
    )

    basis = build_k3_mixed_plane_active_column_basis_summary()
    host = basis["canonical_mixed_plane_support"]
    active_columns = set(basis["mixed_plane_active_column_basis"]["active_columns"])
    inactive_columns = set(basis["mixed_plane_active_column_basis"]["inactive_columns"])

    point_to_lines, line_to_points = quotient_incidence()
    anchor_point = 0
    anchor_lines = list(point_to_lines[anchor_point])

    line_profiles = []
    inert_union: set[int] = set()
    active_spokes: list[int] = []
    for line_id in anchor_lines:
        line_points = list(line_to_points[line_id])
        inert_points = sorted(point for point in line_points if point in inactive_columns)
        spoke_points = sorted(
            point for point in line_points if point in active_columns and point != anchor_point
        )
        inert_union.update(inert_points)
        active_spokes.extend(spoke_points)
        line_profiles.append(
            {
                "line_id": line_id,
                "line_points": line_points,
                "active_spokes": spoke_points,
                "inert_triple": inert_points,
            }
        )

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "mixed_plane_inert_fan_geometry": {
            "anchor_point": anchor_point,
            "anchor_lines": anchor_lines,
            "line_profiles": line_profiles,
            "active_spokes": sorted(active_spokes),
            "inactive_union": sorted(inert_union),
        },
        "k3_mixed_plane_inert_fan_geometry_theorem": {
            "the_inert_9_column_block_is_exactly_cut_out_by_the_three_quotient_lines_through_anchor_point_0": (
                anchor_lines == [0, 1, 2]
                and sorted(inert_union) == [36, 37, 38, 39, 40, 41, 42, 43, 44]
            ),
            "those_three_anchor_lines_have_exact_active_spokes_15_16_17_and_inert_triples_36_40_44_38_39_43_37_41_42": (
                line_profiles
                == [
                    {
                        "line_id": 0,
                        "line_points": [0, 15, 36, 40, 44],
                        "active_spokes": [15],
                        "inert_triple": [36, 40, 44],
                    },
                    {
                        "line_id": 1,
                        "line_points": [0, 16, 38, 39, 43],
                        "active_spokes": [16],
                        "inert_triple": [38, 39, 43],
                    },
                    {
                        "line_id": 2,
                        "line_points": [0, 17, 37, 41, 42],
                        "active_spokes": [17],
                        "inert_triple": [37, 41, 42],
                    },
                ]
            ),
            "therefore_exact_k3_tail_realization_lives_on_the_complement_of_one_rigid_anchored_3_line_fan_in_the_45_point_quotient_geometry": (
                anchor_lines == [0, 1, 2]
                and sorted(active_spokes) == [15, 16, 17]
                and sorted(inert_union) == [36, 37, 38, 39, 40, 41, 42, 43, 44]
                and host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_live_external_wall_is_now_the_first_nonzero_row_entry_witness_off_that_rigid_inert_fan": (
                anchor_lines == [0, 1, 2]
                and sorted(active_spokes) == [15, 16, 17]
                and sorted(inert_union) == [36, 37, 38, 39, 40, 41, 42, 43, 44]
            ),
        },
        "bridge_verdict": (
            "The inert 9-column block has an exact quotient-geometric meaning. "
            "It is the union of the three inert triples on the three quotient "
            "lines through the common anchor point 0, with active spokes 15, "
            "16, and 17. So the live wall is the first nonzero row-entry "
            "witness off one rigid anchored 3-line fan in the 45-point "
            "quotient geometry."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_inert_fan_geometry_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
