"""The active mixed-plane wall also contains a full-rank remote 12-point shell.

The anchored inert-fan picture is exact, but it is not the whole active
geometry. Off the three core points {0,1,2} and their nine incident lines
through the spokes {15,16,17}, there remains a remote 12-point shell:

- points 3..14;
- none lie on any of the 9 core/spoke lines;
- the induced quotient-point graph on those 12 points is 3-regular with 18
  edges;
- the restricted off-diagonal curvature block on those 12 columns already has
  full rank 12.

So the live wall is not confined to the fan sector. There is already a
full-rank remote shell available for a first genuine nonzero row-entry witness.
"""

from __future__ import annotations

from functools import lru_cache
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_remote_shell_bridge_summary.json"
)


def _rank_mod_3(matrix: np.ndarray) -> int:
    reduced = np.array(matrix, dtype=int) % 3
    rows, cols = reduced.shape
    rank = 0
    for column in range(cols):
        pivot = None
        for row in range(rank, rows):
            if reduced[row, column] % 3:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != rank:
            reduced[[rank, pivot]] = reduced[[pivot, rank]]
        inverse = 1 if int(reduced[rank, column]) == 1 else 2
        reduced[rank, :] = (inverse * reduced[rank, :]) % 3
        for row in range(rows):
            if row != rank and reduced[row, column] % 3:
                reduced[row, :] = (
                    reduced[row, :] - reduced[row, column] * reduced[rank, :]
                ) % 3
        rank += 1
        if rank == rows:
            break
    return rank


@lru_cache(maxsize=1)
def build_k3_mixed_plane_remote_shell_summary() -> dict[str, Any]:
    from w33_center_quad_gq42_e6_bridge import quotient_incidence
    from w33_k3_mixed_plane_inert_fan_geometry_bridge import (
        build_k3_mixed_plane_inert_fan_geometry_summary,
    )
    from w33_transport_twisted_precomplex_bridge import adapted_transport_precomplex_data

    fan = build_k3_mixed_plane_inert_fan_geometry_summary()
    host = fan["canonical_mixed_plane_support"]

    point_to_lines, line_to_points = quotient_incidence()
    core_points = {0, 1, 2}
    spoke_points = {15, 16, 17}
    core_spoke_lines = sorted({line for point in core_points for line in point_to_lines[point]})
    core_spoke_shell = sorted({point for line in core_spoke_lines for point in line_to_points[line]})
    remote_points = [point for point in range(45) if point not in core_spoke_shell]

    remote_line_profiles = []
    remote_graph = {point: set() for point in remote_points}
    for line_id, line_points in line_to_points.items():
        remote_on_line = sorted(point for point in line_points if point in remote_graph)
        if remote_on_line:
            remote_line_profiles.append(
                {
                    "line_id": line_id,
                    "remote_points": remote_on_line,
                    "full_line": list(line_points),
                }
            )
            for left, right in combinations(remote_on_line, 2):
                remote_graph[left].add(right)
                remote_graph[right].add(left)

    block = np.array(adapted_transport_precomplex_data()["curvature_iq"], dtype=int) % 3
    remote_rank = _rank_mod_3(block[:, remote_points])

    degree_distribution = {
        degree: sum(1 for point in remote_points if len(remote_graph[point]) == degree)
        for degree in sorted({len(remote_graph[point]) for point in remote_points})
    }

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "mixed_plane_remote_shell": {
            "core_points": sorted(core_points),
            "spoke_points": sorted(spoke_points),
            "core_spoke_lines": core_spoke_lines,
            "core_spoke_shell": core_spoke_shell,
            "remote_points": remote_points,
            "remote_line_count": len(remote_line_profiles),
            "remote_graph_degree_distribution": degree_distribution,
            "remote_column_rank": remote_rank,
        },
        "k3_mixed_plane_remote_shell_theorem": {
            "the_remote_shell_is_exactly_the_12_points_3_through_14_outside_the_9_core_spoke_lines": (
                core_spoke_lines == list(range(9))
                and remote_points == [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
            ),
            "the_remote_shell_carries_an_exact_3_regular_12_point_quotient_subgraph_supported_by_18_lines": (
                len(remote_line_profiles) == 18
                and all(len(profile["remote_points"]) == 2 for profile in remote_line_profiles)
                and degree_distribution == {3: 12}
            ),
            "the_restricted_off_diagonal_curvature_on_the_remote_shell_already_has_full_rank_12": (
                remote_rank == 12
            ),
            "therefore_the_live_mixed_plane_wall_is_not_confined_to_the_fan_sector_and_already_contains_a_full_rank_remote_12_point_shell": (
                remote_points == [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
                and len(remote_line_profiles) == 18
                and degree_distribution == {3: 12}
                and remote_rank == 12
                and host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
            ),
        },
        "bridge_verdict": (
            "The anchored fan is exact but not exhaustive. The 12 points 3..14 "
            "form a remote shell outside the 9 core/spoke lines, carrying a "
            "3-regular 12-point quotient subgraph on 18 lines and a full-rank "
            "12-column curvature block. So the live mixed-plane wall is not "
            "confined to the fan sector."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_remote_shell_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
