"""The fan-adjacent rank-24 sector splits as 1 + 3 + 20.

CDXLI split the live active complement into a fan-adjacent rank-24 sector and
two remote rank-6 K3,3 sectors. The next question is whether the fan-adjacent
sector itself still hides exact structure.

It does. Relative to the anchored inert-fan geometry, the fan-adjacent sector
splits into:

- the anchor column {0}, rank 1;
- the spoke triple {15,16,17}, rank 3;
- the outer shell {1,2,18..35}, rank 20.

So the fan-adjacent side is itself an exact full-rank 1 + 3 + 20 shell split.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_fan_shell_split_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_mixed_plane_fan_shell_split_summary() -> dict[str, Any]:
    from w33_k3_mixed_plane_active_sector_trisection_bridge import (
        build_k3_mixed_plane_active_sector_trisection_summary,
    )
    from w33_transport_twisted_precomplex_bridge import (
        _rank_mod_p,
        adapted_transport_precomplex_data,
    )

    active = build_k3_mixed_plane_active_sector_trisection_summary()
    host = active["canonical_mixed_plane_support"]
    block = np.array(adapted_transport_precomplex_data()["curvature_iq"], dtype=int) % 3

    anchor_columns = [0]
    spoke_columns = [15, 16, 17]
    outer_shell_columns = [1, 2] + list(range(18, 36))
    fan_adjacent_columns = active["mixed_plane_active_sector_trisection"][
        "fan_adjacent_columns"
    ]

    anchor_rank = _rank_mod_p(block[:, anchor_columns])
    spoke_rank = _rank_mod_p(block[:, spoke_columns])
    outer_shell_rank = _rank_mod_p(block[:, outer_shell_columns])
    fan_adjacent_rank = _rank_mod_p(block[:, fan_adjacent_columns])

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "mixed_plane_fan_shell_split": {
            "anchor_columns": anchor_columns,
            "spoke_columns": spoke_columns,
            "outer_shell_columns": outer_shell_columns,
            "anchor_rank": anchor_rank,
            "spoke_rank": spoke_rank,
            "outer_shell_rank": outer_shell_rank,
            "fan_adjacent_rank": fan_adjacent_rank,
        },
        "k3_mixed_plane_fan_shell_split_theorem": {
            "the_fan_adjacent_sector_splits_exactly_as_1_plus_3_plus_20": (
                fan_adjacent_columns
                == [0, 1, 2, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
                and anchor_columns == [0]
                and spoke_columns == [15, 16, 17]
                and outer_shell_columns == [1, 2] + list(range(18, 36))
            ),
            "the_anchor_spoke_and_outer_shell_already_have_full_ranks_1_3_and_20": (
                anchor_rank == 1 and spoke_rank == 3 and outer_shell_rank == 20
            ),
            "therefore_the_fan_adjacent_live_sector_is_itself_an_exact_full_rank_shell_split": (
                fan_adjacent_rank == 24
                and anchor_rank == 1
                and spoke_rank == 3
                and outer_shell_rank == 20
                and host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
            ),
        },
        "bridge_verdict": (
            "The fan-adjacent rank-24 sector already splits exactly as anchor "
            "1 plus spokes 3 plus outer shell 20, each with full rank. So the "
            "fan side of the live wall is itself an exact shell decomposition."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_fan_shell_split_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
