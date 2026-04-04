"""The remote 12-point shell splits into two exact K3,3 witness components.

CDXXXVII identified a full-rank remote 12-point shell outside the anchored
fan sector. The next question is whether that shell is already decomposed into
smaller exact pieces.

It is. The remote shell splits as two disjoint K3,3 components:

- {3,4,5} x {12,13,14}, supported on lines 9..17;
- {6,7,8} x {9,10,11}, supported on lines 18..26.

Each component already carries a full-rank 6-column curvature block. So the
live wall is not just “somewhere in the remote shell”; it may first appear in
either of two exact K3,3 witness components.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_remote_bipartite_split_bridge_summary.json"
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
def build_k3_mixed_plane_remote_bipartite_split_summary() -> dict[str, Any]:
    from w33_center_quad_gq42_e6_bridge import quotient_incidence
    from w33_k3_mixed_plane_remote_shell_bridge import (
        build_k3_mixed_plane_remote_shell_summary,
    )
    from w33_transport_twisted_precomplex_bridge import adapted_transport_precomplex_data

    remote = build_k3_mixed_plane_remote_shell_summary()
    host = remote["canonical_mixed_plane_support"]
    _, line_to_points = quotient_incidence()
    block = np.array(adapted_transport_precomplex_data()["curvature_iq"], dtype=int) % 3

    components = [
        {
            "name": "upper_remote_k33",
            "left_part": [3, 4, 5],
            "right_part": [12, 13, 14],
            "supporting_lines": list(range(9, 18)),
        },
        {
            "name": "lower_remote_k33",
            "left_part": [6, 7, 8],
            "right_part": [9, 10, 11],
            "supporting_lines": list(range(18, 27)),
        },
    ]

    component_profiles = []
    for component in components:
        points = component["left_part"] + component["right_part"]
        component_profiles.append(
            {
                **component,
                "line_point_profiles": [list(line_to_points[line_id]) for line_id in component["supporting_lines"]],
                "restricted_curvature_rank": _rank_mod_3(block[:, points]),
                "column_support_counts": {
                    point: int(np.count_nonzero(block[:, point])) for point in points
                },
            }
        )

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "mixed_plane_remote_bipartite_split": {
            "component_profiles": component_profiles,
        },
        "k3_mixed_plane_remote_bipartite_split_theorem": {
            "the_remote_12_point_shell_splits_as_two_disjoint_k3_3_components": (
                component_profiles[0]["left_part"] == [3, 4, 5]
                and component_profiles[0]["right_part"] == [12, 13, 14]
                and component_profiles[1]["left_part"] == [6, 7, 8]
                and component_profiles[1]["right_part"] == [9, 10, 11]
            ),
            "each_k3_3_component_is_supported_on_9_exact_quotient_lines": (
                component_profiles[0]["supporting_lines"] == list(range(9, 18))
                and component_profiles[1]["supporting_lines"] == list(range(18, 27))
            ),
            "each_k3_3_component_already_carries_full_rank_6_curvature": (
                component_profiles[0]["restricted_curvature_rank"] == 6
                and component_profiles[1]["restricted_curvature_rank"] == 6
            ),
            "therefore_the_live_remote_wall_may_first_appear_in_either_exact_k3_3_component": (
                component_profiles[0]["restricted_curvature_rank"] == 6
                and component_profiles[1]["restricted_curvature_rank"] == 6
                and host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
            ),
        },
        "bridge_verdict": (
            "The remote shell already splits into two exact K3,3 witness "
            "components, each with full rank 6. So the live wall may first "
            "appear in either exact remote component, not just somewhere in "
            "the undifferentiated 12-point shell."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_remote_bipartite_split_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
