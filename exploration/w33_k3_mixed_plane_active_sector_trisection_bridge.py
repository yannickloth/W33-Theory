"""The 36-column live mixed-plane wall splits as 24 + 6 + 6.

CDXXXIII localized the live wall to a full-rank 36-column active complement.
CDXXXIX refined the remote 12-column shell into two exact rank-6 K3,3
components. Putting those together gives the first exact sector decomposition
of the whole live active block.

The split is:

- a 24-column fan-adjacent sector on columns 0,1,2,15..35;
- an upper remote K3,3 sector on {3,4,5,12,13,14};
- a lower remote K3,3 sector on {6,7,8,9,10,11}.

Each sector already has full rank equal to its column count, so the live wall
is not just a 36-column basis block. It is the disjoint union of three exact
full-rank sectors of sizes 24, 6, and 6.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_active_sector_trisection_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_mixed_plane_active_sector_trisection_summary() -> dict[str, Any]:
    from w33_k3_mixed_plane_active_column_basis_bridge import (
        build_k3_mixed_plane_active_column_basis_summary,
    )
    from w33_k3_mixed_plane_remote_bipartite_split_bridge import (
        build_k3_mixed_plane_remote_bipartite_split_summary,
    )
    from w33_transport_twisted_precomplex_bridge import (
        _rank_mod_p,
        adapted_transport_precomplex_data,
    )

    active = build_k3_mixed_plane_active_column_basis_summary()
    remote = build_k3_mixed_plane_remote_bipartite_split_summary()

    host = active["canonical_mixed_plane_support"]
    block = np.array(adapted_transport_precomplex_data()["curvature_iq"], dtype=int) % 3

    active_columns = active["mixed_plane_active_column_basis"]["active_columns"]
    remote_profiles = remote["mixed_plane_remote_bipartite_split"]["component_profiles"]
    upper_remote_columns = (
        remote_profiles[0]["left_part"] + remote_profiles[0]["right_part"]
    )
    lower_remote_columns = (
        remote_profiles[1]["left_part"] + remote_profiles[1]["right_part"]
    )
    fan_adjacent_columns = [
        column
        for column in active_columns
        if column not in upper_remote_columns and column not in lower_remote_columns
    ]

    fan_adjacent_rank = _rank_mod_p(block[:, fan_adjacent_columns])
    upper_remote_rank = _rank_mod_p(block[:, upper_remote_columns])
    lower_remote_rank = _rank_mod_p(block[:, lower_remote_columns])

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "mixed_plane_active_sector_trisection": {
            "fan_adjacent_columns": fan_adjacent_columns,
            "upper_remote_columns": upper_remote_columns,
            "lower_remote_columns": lower_remote_columns,
            "fan_adjacent_rank": fan_adjacent_rank,
            "upper_remote_rank": upper_remote_rank,
            "lower_remote_rank": lower_remote_rank,
        },
        "k3_mixed_plane_active_sector_trisection_theorem": {
            "the_live_36_column_active_complement_splits_exactly_as_24_plus_6_plus_6": (
                fan_adjacent_columns
                == [
                    0,
                    1,
                    2,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                ]
                and upper_remote_columns == [3, 4, 5, 12, 13, 14]
                and lower_remote_columns == [6, 7, 8, 9, 10, 11]
            ),
            "the_fan_adjacent_sector_already_has_full_rank_24": (
                len(fan_adjacent_columns) == 24 and fan_adjacent_rank == 24
            ),
            "the_two_remote_k3_3_sectors_already_have_full_rank_6_each": (
                len(upper_remote_columns) == 6
                and len(lower_remote_columns) == 6
                and upper_remote_rank == 6
                and lower_remote_rank == 6
            ),
            "therefore_the_live_wall_splits_into_three_exact_full_rank_sectors": (
                len(fan_adjacent_columns) == 24
                and fan_adjacent_rank == 24
                and len(upper_remote_columns) == 6
                and len(lower_remote_columns) == 6
                and upper_remote_rank == 6
                and lower_remote_rank == 6
                and host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
            ),
        },
        "bridge_verdict": (
            "The 36-column active complement already splits as three exact "
            "full-rank sectors: a 24-column fan-adjacent block and two remote "
            "K3,3 blocks of rank 6 each. So the live wall is not a generic "
            "36-column basis problem; it may first appear in any of these "
            "three exact sectors."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_active_sector_trisection_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
