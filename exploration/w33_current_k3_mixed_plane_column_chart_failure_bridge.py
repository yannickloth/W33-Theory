"""Current mixed-plane host fails every active local curvature-column chart.

CDXXXI shows the exact mixed-plane wall is not a choice among the 36 active
curvature columns: each supported column is already a valid local chart for a nonzero row-entry
witness. The current host therefore fails in the same way in every such chart.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_current_k3_mixed_plane_column_chart_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_column_chart_failure_summary() -> dict[str, Any]:
    from w33_current_k3_mixed_plane_row_entry_failure_bridge import (
        build_current_k3_mixed_plane_row_entry_failure_summary,
    )
    from w33_k3_mixed_plane_column_chart_universality_bridge import (
        build_k3_mixed_plane_column_chart_universality_summary,
    )

    current = build_current_k3_mixed_plane_row_entry_failure_summary()
    exact = build_k3_mixed_plane_column_chart_universality_summary()

    current_host = current["current_mixed_plane_row_entry_state"]
    exact_columns = exact["column_chart_universality"]

    return {
        "status": "ok",
        "current_mixed_plane_column_chart_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_slot_state"],
            "current_supported_column_count": 0,
            "current_supported_entry_count": current_host["current_supported_entry_count"],
        },
        "exact_column_chart_universality": exact_columns,
        "current_k3_mixed_plane_column_chart_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_current_mixed_plane_host_still_carries_zero_supported_entries_in_every_curvature_column": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_supported_entry_count"] == 0
            ),
            "the_exact_mixed_plane_witness_requires_36_active_curvature_columns_to_be_viable_local_charts": (
                exact_columns["curvature_column_count"] == 45
                and exact_columns["supported_column_count"] == 36
                and exact_columns["columns_with_both_row_components"] == 36
                and exact_columns["columns_with_both_nonzero_values"] == 36
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_active_column_chart_test_for_one_reason_only_every_active_column_remains_zero": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_supported_entry_count"] == 0
                and exact_columns["supported_column_count"] == 36
                and exact_columns["columns_with_both_row_components"] == 36
                and exact_columns["columns_with_both_nonzero_values"] == 36
            ),
            "the_live_external_wall_is_now_the_first_genuine_nonzero_active_column_anchored_row_entry_witness_on_the_same_fixed_host": (
                current_host["current_supported_entry_count"] == 0
                and exact_columns["supported_column_count"] == 36
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host is structurally correct, but it "
            "still carries no supported row entries at all. Since every exact "
            "active curvature column is already a viable local chart, the "
            "current host fails for one reason only: every active column "
            "remains zero."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_current_k3_mixed_plane_column_chart_failure_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
