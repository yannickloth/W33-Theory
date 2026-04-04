"""Current mixed-plane host still vanishes on all three fan shells.

CDXLIII splits the fan-adjacent sector into exact anchor, spoke, and outer
shell pieces. This phase applies that split back to the current host.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_current_k3_mixed_plane_fan_shell_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_fan_shell_failure_summary() -> dict[str, Any]:
    from w33_current_k3_mixed_plane_active_sector_failure_bridge import (
        build_current_k3_mixed_plane_active_sector_failure_summary,
    )
    from w33_k3_mixed_plane_fan_shell_split_bridge import (
        build_k3_mixed_plane_fan_shell_split_summary,
    )

    current = build_current_k3_mixed_plane_active_sector_failure_summary()
    exact = build_k3_mixed_plane_fan_shell_split_summary()

    current_host = current["current_mixed_plane_active_sector_state"]
    fan = exact["mixed_plane_fan_shell_split"]

    return {
        "status": "ok",
        "current_mixed_plane_fan_shell_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_slot_state"],
            "current_anchor_supported_entry_count": 0,
            "current_spoke_supported_entry_count": 0,
            "current_outer_shell_supported_entry_count": 0,
        },
        "exact_mixed_plane_fan_shell_split": fan,
        "current_k3_mixed_plane_fan_shell_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_exact_fan_adjacent_sector_already_splits_into_full_rank_shells_of_ranks_1_3_and_20": (
                fan["anchor_rank"] == 1
                and fan["spoke_rank"] == 3
                and fan["outer_shell_rank"] == 20
            ),
            "the_current_mixed_plane_host_still_carries_zero_supported_entries_on_all_three_fan_shells": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_fan_adjacent_supported_entry_count"] == 0
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_fan_shell_test_for_one_reason_only_all_three_fan_shells_still_vanish": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_fan_adjacent_supported_entry_count"] == 0
                and fan["anchor_rank"] == 1
                and fan["spoke_rank"] == 3
                and fan["outer_shell_rank"] == 20
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host still vanishes on all three exact "
            "fan shells: anchor, spokes, and outer shell. So the fan-adjacent "
            "side of the live wall is now localized to the first nonzero "
            "witness in one of those three exact shell pieces."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_current_k3_mixed_plane_fan_shell_failure_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
