"""Current mixed-plane K3 host still fails the row-entry witness test.

CDXXIX reduced the positive mixed-plane wall to the smallest local matrix
datum carried by the exact transport-twisted precomplex:

- one support-preserving nonzero row-entry witness on the same fixed
  mixed-plane host.

The current host already has the right support package and qutrit lift, but it
still carries zero supported rows and therefore zero supported entries.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_current_k3_mixed_plane_row_entry_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_row_entry_failure_summary() -> dict[str, Any]:
    from w33_current_k3_mixed_plane_triangle_row_curvature_failure_bridge import (
        build_current_k3_mixed_plane_triangle_row_curvature_failure_summary,
    )
    from w33_k3_mixed_plane_row_entry_witness_bridge import (
        build_k3_mixed_plane_row_entry_witness_summary,
    )

    current = build_current_k3_mixed_plane_triangle_row_curvature_failure_summary()
    exact = build_k3_mixed_plane_row_entry_witness_summary()

    current_host = current["current_mixed_plane_triangle_row_curvature_state"]
    exact_rows = exact["row_entry_witness"]

    return {
        "status": "ok",
        "current_mixed_plane_row_entry_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_slot_state"],
            "current_supported_row_count": current_host["current_supported_row_count"],
            "current_supported_entry_count": 0,
        },
        "exact_row_entry_witness": exact_rows,
        "current_k3_mixed_plane_row_entry_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_current_mixed_plane_host_still_carries_zero_supported_row_entries": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_supported_row_count"] == 0
            ),
            "the_exact_mixed_plane_witness_requires_nonzero_supported_row_entries": (
                exact_rows["supported_row_count"] == 4046
                and exact_rows["row_support_size_distribution"] == {1: 4046}
                and exact_rows["entry_value_distribution"] == {1: 2029, 2: 2017}
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_row_entry_test_for_one_reason_only_the_nonzero_supported_entry_is_missing": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
                and current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_supported_row_count"] == 0
                and exact_rows["supported_row_count"] == 4046
                and exact_rows["row_support_size_distribution"] == {1: 4046}
            ),
            "the_live_external_wall_is_now_the_first_genuine_nonzero_row_entry_witness_on_the_same_fixed_host": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and exact_rows["row_support_size_distribution"] == {1: 4046}
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host is already structurally correct "
            "at the level of support and qutrit lift. What it still lacks is "
            "the first nonzero supported row entry in the off-diagonal "
            "curvature block. So the live wall is now exactly the first "
            "genuine nonzero row-entry witness on that same fixed host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_current_k3_mixed_plane_row_entry_failure_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
