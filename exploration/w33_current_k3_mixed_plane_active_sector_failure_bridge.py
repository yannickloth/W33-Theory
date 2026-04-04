"""Current mixed-plane host still vanishes on all three exact active sectors.

CDXLI splits the full live active complement into three exact full-rank
sectors. This phase applies that decomposition back to the current host.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_current_k3_mixed_plane_active_sector_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_active_sector_failure_summary() -> dict[str, Any]:
    from w33_current_k3_mixed_plane_remote_bipartite_failure_bridge import (
        build_current_k3_mixed_plane_remote_bipartite_failure_summary,
    )
    from w33_k3_mixed_plane_active_sector_trisection_bridge import (
        build_k3_mixed_plane_active_sector_trisection_summary,
    )

    current = build_current_k3_mixed_plane_remote_bipartite_failure_summary()
    exact = build_k3_mixed_plane_active_sector_trisection_summary()

    current_host = current["current_mixed_plane_remote_bipartite_state"]
    sectors = exact["mixed_plane_active_sector_trisection"]

    return {
        "status": "ok",
        "current_mixed_plane_active_sector_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_slot_state"],
            "current_fan_adjacent_supported_entry_count": 0,
            "current_upper_remote_supported_entry_count": 0,
            "current_lower_remote_supported_entry_count": 0,
        },
        "exact_mixed_plane_active_sector_trisection": sectors,
        "current_k3_mixed_plane_active_sector_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_exact_live_wall_already_splits_into_three_full_rank_active_sectors_of_ranks_24_6_and_6": (
                sectors["fan_adjacent_rank"] == 24
                and sectors["upper_remote_rank"] == 6
                and sectors["lower_remote_rank"] == 6
            ),
            "the_current_mixed_plane_host_still_carries_zero_supported_entries_on_all_three_active_sectors": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and current["current_mixed_plane_remote_bipartite_state"][
                    "current_upper_remote_supported_entry_count"
                ]
                == 0
                and current["current_mixed_plane_remote_bipartite_state"][
                    "current_lower_remote_supported_entry_count"
                ]
                == 0
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_three_sector_test_for_one_reason_only_all_three_live_active_sectors_still_vanish": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["current_slot_state"] == "zero_by_splitness"
                and sectors["fan_adjacent_rank"] == 24
                and sectors["upper_remote_rank"] == 6
                and sectors["lower_remote_rank"] == 6
                and current["current_mixed_plane_remote_bipartite_state"][
                    "current_upper_remote_supported_entry_count"
                ]
                == 0
                and current["current_mixed_plane_remote_bipartite_state"][
                    "current_lower_remote_supported_entry_count"
                ]
                == 0
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host still vanishes on all three exact "
            "full-rank active sectors: the 24-column fan-adjacent block and "
            "both remote rank-6 K3,3 blocks. So the three-sector existence map "
            "is exact, but every live sector still vanishes on the current host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_current_k3_mixed_plane_active_sector_failure_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
