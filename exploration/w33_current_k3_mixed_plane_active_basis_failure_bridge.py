"""Current mixed-plane host still vanishes on the full-rank active complement.

CDXXXIII shows the live wall lives on a full-rank 36-column active complement,
not on all 45 sign channels. The current host therefore fails in the strongest
possible basis language too: the entire active complement remains zero.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_current_k3_mixed_plane_active_basis_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_active_basis_failure_summary() -> dict[str, Any]:
    from w33_current_k3_mixed_plane_column_chart_failure_bridge import (
        build_current_k3_mixed_plane_column_chart_failure_summary,
    )
    from w33_k3_mixed_plane_active_column_basis_bridge import (
        build_k3_mixed_plane_active_column_basis_summary,
    )

    current = build_current_k3_mixed_plane_column_chart_failure_summary()
    exact = build_k3_mixed_plane_active_column_basis_summary()

    current_host = current["current_mixed_plane_column_chart_state"]
    exact_basis = exact["mixed_plane_active_column_basis"]

    return {
        "status": "ok",
        "current_mixed_plane_active_basis_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_slot_state"],
            "current_active_column_supported_entry_count": 0,
            "current_inactive_column_supported_entry_count": 0,
        },
        "exact_mixed_plane_active_basis": exact_basis,
        "current_k3_mixed_plane_active_basis_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_exact_mixed_plane_wall_lives_on_a_full_rank_36_column_active_complement": (
                exact_basis["active_column_count"] == 36
                and exact_basis["off_diagonal_curvature_rank"] == 36
                and exact_basis["active_column_restricted_rank"] == 36
            ),
            "the_current_mixed_plane_host_still_carries_zero_supported_entries_on_that_entire_active_complement": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_supported_entry_count"] == 0
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_active_basis_test_for_one_reason_only_the_full_rank_36_column_complement_remains_zero": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_supported_entry_count"] == 0
                and exact_basis["active_column_count"] == 36
                and exact_basis["active_column_restricted_rank"] == 36
            ),
            "the_live_external_wall_is_now_the_first_genuine_nonzero_row_entry_witness_on_the_full_rank_36_column_active_complement": (
                current_host["current_supported_entry_count"] == 0
                and exact_basis["active_column_count"] == 36
                and exact_basis["active_column_restricted_rank"] == 36
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host is already on the correct fixed "
            "support package, but it still vanishes on the whole full-rank "
            "36-column active complement. So the live wall is now exactly the "
            "first genuine nonzero row-entry witness on that active basis "
            "block."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_current_k3_mixed_plane_active_basis_failure_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
