"""Current mixed-plane K3 host still fails the off-diagonal curvature-witness test.

CDXXIV localized the positive mixed-plane wall at the level of the exact
transport-twisted precomplex:

- one support-preserving nonzero off-diagonal curvature witness on the same
  fixed mixed-plane host.

The current host already has the right support package and qutrit lift, but it
still carries only the split zero increment in the existing slot. So it does
not yet realize the exact nonzero off-diagonal curvature coupling carried by
the transport-twisted precomplex.
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
    / "w33_current_k3_mixed_plane_off_diagonal_curvature_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_off_diagonal_curvature_failure_summary() -> (
    dict[str, Any]
):
    from w33_current_k3_mixed_plane_nilpotent_holonomy_increment_failure_bridge import (
        build_current_k3_mixed_plane_nilpotent_holonomy_increment_failure_summary,
    )
    from w33_k3_mixed_plane_off_diagonal_curvature_witness_bridge import (
        build_k3_mixed_plane_off_diagonal_curvature_witness_summary,
    )

    current = build_current_k3_mixed_plane_nilpotent_holonomy_increment_failure_summary()
    exact = build_k3_mixed_plane_off_diagonal_curvature_witness_summary()

    current_host = current["current_mixed_plane_nilpotent_holonomy_increment_state"]
    exact_curvature = exact["transport_twisted_off_diagonal_curvature_package"]

    return {
        "status": "ok",
        "current_mixed_plane_off_diagonal_curvature_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_slot_state"],
            "current_nilpotent_increment": current_host["current_nilpotent_increment"],
            "current_off_diagonal_curvature_rank": 0,
            "current_off_diagonal_curvature_support_rows": 0,
        },
        "exact_transport_twisted_off_diagonal_curvature": exact_curvature,
        "current_k3_mixed_plane_off_diagonal_curvature_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_current_mixed_plane_host_still_carries_only_zero_off_diagonal_curvature_coupling": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_nilpotent_increment"] == [[0, 0], [0, 0]]
            ),
            "the_exact_mixed_plane_witness_requires_nonzero_off_diagonal_curvature_coupling": (
                exact_curvature["off_diagonal_curvature_rank"] == 36
                and exact_curvature["off_diagonal_curvature_support_rows"] == 4046
                and exact_curvature["upper_right_curvature_identity_exact"] is True
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_off_diagonal_curvature_test_for_one_reason_only_the_nonzero_curvature_coupling_is_missing": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
                and current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_nilpotent_increment"] == [[0, 0], [0, 0]]
                and exact_curvature["off_diagonal_curvature_rank"] == 36
                and exact_curvature["off_diagonal_curvature_support_rows"] == 4046
            ),
            "the_live_external_wall_is_now_the_first_genuine_nonzero_off_diagonal_curvature_witness_on_the_same_fixed_host": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and exact_curvature["off_diagonal_curvature_rank"] == 36
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host is already structurally correct "
            "at the level of support and qutrit lift. What it still lacks is "
            "the first genuine off-diagonal curvature coupling from the exact "
            "transport-twisted precomplex. So the live wall is now exactly "
            "the first nonzero off-diagonal curvature witness on that same "
            "fixed host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_current_k3_mixed_plane_off_diagonal_curvature_failure_summary(),
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
