"""Current mixed-plane host still vanishes on both remote K3,3 components.

CDXXXIX shows the remote shell splits into two exact K3,3 witness components.
This phase applies that split back to the current host.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_current_k3_mixed_plane_remote_bipartite_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_remote_bipartite_failure_summary() -> dict[str, Any]:
    from w33_current_k3_mixed_plane_remote_shell_failure_bridge import (
        build_current_k3_mixed_plane_remote_shell_failure_summary,
    )
    from w33_k3_mixed_plane_remote_bipartite_split_bridge import (
        build_k3_mixed_plane_remote_bipartite_split_summary,
    )

    current = build_current_k3_mixed_plane_remote_shell_failure_summary()
    exact = build_k3_mixed_plane_remote_bipartite_split_summary()

    current_host = current["current_mixed_plane_remote_shell_state"]
    remote = exact["mixed_plane_remote_bipartite_split"]["component_profiles"]

    return {
        "status": "ok",
        "current_mixed_plane_remote_bipartite_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_slot_state"],
            "current_upper_remote_supported_entry_count": 0,
            "current_lower_remote_supported_entry_count": 0,
        },
        "exact_remote_bipartite_split": remote,
        "current_k3_mixed_plane_remote_bipartite_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_exact_remote_wall_already_splits_into_two_full_rank_k3_3_components": (
                remote[0]["restricted_curvature_rank"] == 6
                and remote[1]["restricted_curvature_rank"] == 6
            ),
            "the_current_mixed_plane_host_still_carries_zero_supported_entries_on_both_remote_components": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_supported_entry_count_on_remote_shell"] == 0
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_remote_bipartite_test_for_one_reason_only_both_remote_k3_3_components_still_vanish": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_supported_entry_count_on_remote_shell"] == 0
                and remote[0]["restricted_curvature_rank"] == 6
                and remote[1]["restricted_curvature_rank"] == 6
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host still vanishes on both exact "
            "remote K3,3 witness components. So the remote-side existence wall "
            "is now reduced to the first nonzero row-entry witness in either "
            "of those two rank-6 components."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_current_k3_mixed_plane_remote_bipartite_failure_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
