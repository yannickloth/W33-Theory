"""Current mixed-plane K3 host still fails the triangle-row curvature-witness test.

CDXXVI reduced the positive mixed-plane wall to the smallest local geometric
datum carried by the exact transport-twisted precomplex:

- one support-preserving nonzero triangle-row curvature witness on the same
  fixed mixed-plane host.

The current host already has the right support package and qutrit lift, but it
still carries only the zero off-diagonal curvature coupling. So it has no
supported triangle rows at all.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT
    / "data"
    / "w33_current_k3_mixed_plane_triangle_row_curvature_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_triangle_row_curvature_failure_summary() -> (
    dict[str, Any]
):
    from w33_current_k3_mixed_plane_off_diagonal_curvature_failure_bridge import (
        build_current_k3_mixed_plane_off_diagonal_curvature_failure_summary,
    )
    from w33_k3_mixed_plane_triangle_row_curvature_witness_bridge import (
        build_k3_mixed_plane_triangle_row_curvature_witness_summary,
    )

    current = build_current_k3_mixed_plane_off_diagonal_curvature_failure_summary()
    exact = build_k3_mixed_plane_triangle_row_curvature_witness_summary()

    current_host = current["current_mixed_plane_off_diagonal_curvature_state"]
    exact_rows = exact["triangle_row_curvature_witness"]

    return {
        "status": "ok",
        "current_mixed_plane_triangle_row_curvature_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_slot_state"],
            "current_off_diagonal_curvature_rank": current_host[
                "current_off_diagonal_curvature_rank"
            ],
            "current_supported_triangle_count": 0,
            "current_supported_row_count": 0,
        },
        "exact_triangle_row_curvature_witness": exact_rows,
        "current_k3_mixed_plane_triangle_row_curvature_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_current_mixed_plane_host_still_carries_zero_supported_triangle_rows": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_off_diagonal_curvature_rank"] == 0
            ),
            "the_exact_mixed_plane_witness_requires_supported_nonzero_triangle_rows": (
                exact_rows["supported_triangle_count"] == 2428
                and exact_rows["supported_row_count"] == 4046
                and exact_rows["triangle_row_support_distribution"] == {1: 810, 2: 1618}
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_triangle_row_curvature_test_for_one_reason_only_the_nonzero_supported_rows_are_missing": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
                and current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_off_diagonal_curvature_rank"] == 0
                and exact_rows["supported_triangle_count"] == 2428
                and exact_rows["supported_row_count"] == 4046
            ),
            "the_live_external_wall_is_now_the_first_genuine_nonzero_triangle_row_curvature_witness_on_the_same_fixed_host": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and exact_rows["supported_row_count"] == 4046
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host is already structurally correct "
            "at the level of support and qutrit lift. What it still lacks is "
            "the first nonzero supported triangle row in the off-diagonal "
            "curvature block of the exact transport-twisted precomplex. So "
            "the live wall is now exactly the first genuine nonzero "
            "triangle-row curvature witness on that same fixed host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_current_k3_mixed_plane_triangle_row_curvature_failure_summary(),
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
