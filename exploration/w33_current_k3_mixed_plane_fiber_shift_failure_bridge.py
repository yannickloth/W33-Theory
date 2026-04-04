"""Current mixed-plane K3 host still fails the fiber-shift witness test.

CDXVI reduced the positive mixed-plane wall to the smallest genuinely
nontrivial datum the repo can recognize:

- one support-preserving nonzero reduced fiber shift ``[[0,1],[0,0]]`` on the
  canonical mixed-plane host.

The full rank-81 slot operator is then forced as the qutrit lift
``I_81 ⊗ [[0,1],[0,0]]``. So the current host can now be tested in the
smallest exact language available.

The result is sharp: the present mixed-plane host is already correct in its
support data and qutrit lift, but it still carries only the zero fiber shift.
So the live wall is now exactly the first genuine nonzero reduced fiber-shift
witness on that same fixed host.
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
    / "w33_current_k3_mixed_plane_fiber_shift_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_fiber_shift_failure_summary() -> dict[str, Any]:
    from w33_current_k3_mixed_plane_operator_witness_failure_bridge import (
        build_current_k3_mixed_plane_operator_witness_failure_summary,
    )
    from w33_k3_mixed_plane_fiber_shift_witness_bridge import (
        build_k3_mixed_plane_fiber_shift_witness_summary,
    )

    current = build_current_k3_mixed_plane_operator_witness_failure_summary()
    exact = build_k3_mixed_plane_fiber_shift_witness_summary()

    current_host = current["current_mixed_plane_operator_state"]
    exact_fiber = exact["mixed_plane_fiber_shift_witness"]

    return {
        "status": "ok",
        "current_mixed_plane_fiber_shift_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_state"],
            "current_fiber_shift_matrix": [[0, 0], [0, 0]],
        },
        "exact_mixed_plane_fiber_shift_witness": exact_fiber,
        "current_k3_mixed_plane_fiber_shift_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_current_mixed_plane_host_still_carries_only_the_zero_fiber_shift": (
                current_host["current_state"] == "zero_by_splitness"
            ),
            "the_exact_mixed_plane_witness_requires_the_unique_nonzero_reduced_fiber_shift": (
                exact_fiber["fiber_shift_matrix"] == [[0, 1], [0, 0]]
                and exact_fiber["fiber_rank"] == 1
                and exact_fiber["fiber_square_zero"] is True
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_fiber_shift_witness_test_for_one_reason_only_the_nonzero_reduced_fiber_shift_is_missing": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
                and current_host["current_state"] == "zero_by_splitness"
                and exact_fiber["fiber_shift_matrix"] == [[0, 1], [0, 0]]
                and exact_fiber["fiber_rank"] == 1
            ),
            "the_live_external_wall_is_now_the_first_genuine_nonzero_reduced_fiber_shift_witness_on_the_same_fixed_host": (
                current_host["current_state"] == "zero_by_splitness"
                and exact_fiber["fiber_shift_matrix"] == [[0, 1], [0, 0]]
                and exact_fiber["fiber_rank"] == 1
                and exact_fiber["fiber_square_zero"] is True
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host is already structurally correct "
            "at the level of support and qutrit lift. What it still lacks is "
            "the smallest nontrivial datum: the reduced nonzero fiber shift "
            "[[0,1],[0,0]]. So the live wall is now exactly the first genuine "
            "nonzero reduced fiber-shift witness on that same fixed host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_current_k3_mixed_plane_fiber_shift_failure_summary(), indent=2
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
