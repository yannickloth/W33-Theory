"""Current mixed-plane host still vanishes on the full-rank remote shell.

CDXXXVII shows the live mixed-plane wall is not confined to the anchored
fan sector. The current host therefore fails on the remote shell as well.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_current_k3_mixed_plane_remote_shell_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_remote_shell_failure_summary() -> dict[str, Any]:
    from w33_current_k3_mixed_plane_inert_fan_failure_bridge import (
        build_current_k3_mixed_plane_inert_fan_failure_summary,
    )
    from w33_k3_mixed_plane_remote_shell_bridge import (
        build_k3_mixed_plane_remote_shell_summary,
    )

    current = build_current_k3_mixed_plane_inert_fan_failure_summary()
    exact = build_k3_mixed_plane_remote_shell_summary()

    current_host = current["current_mixed_plane_inert_fan_state"]
    remote = exact["mixed_plane_remote_shell"]

    return {
        "status": "ok",
        "current_mixed_plane_remote_shell_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_slot_state"],
            "current_supported_entry_count_on_remote_shell": 0,
        },
        "exact_mixed_plane_remote_shell": remote,
        "current_k3_mixed_plane_remote_shell_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_exact_live_wall_already_contains_a_full_rank_remote_12_point_shell": (
                remote["remote_points"] == [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
                and remote["remote_line_count"] == 18
                and remote["remote_column_rank"] == 12
            ),
            "the_current_mixed_plane_host_still_carries_zero_supported_entries_on_that_remote_shell": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and current["current_mixed_plane_inert_fan_state"]["current_supported_entry_count_off_inert_fan"] == 0
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_remote_shell_test_for_one_reason_only_the_full_rank_remote_shell_still_vanishes": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["current_slot_state"] == "zero_by_splitness"
                and current["current_mixed_plane_inert_fan_state"]["current_supported_entry_count_off_inert_fan"] == 0
                and remote["remote_points"] == [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
                and remote["remote_column_rank"] == 12
            ),
            "the_live_external_wall_is_now_known_to_require_a_first_genuine_nonzero_row_entry_witness_either_in_the_fan_adjacent_sector_or_in_the_remote_12_point_shell": (
                current["current_mixed_plane_inert_fan_state"]["current_supported_entry_count_off_inert_fan"] == 0
                and remote["remote_column_rank"] == 12
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host still vanishes on the full-rank "
            "remote 12-point shell as well as on the fan-adjacent sector. So "
            "the live wall is not confined to the anchored fan: a first "
            "genuine nonzero row-entry witness could arise in either active "
            "sector, and currently neither does."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_current_k3_mixed_plane_remote_shell_failure_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
