"""Current mixed-plane K3 host still fails the cocycle-witness test.

CDXVIII reduced the positive mixed-plane wall to the smallest repo-native
cohomological datum:

- one support-preserving nonzero sign-trivial cocycle value on the canonical
  mixed-plane host.

That witness already forces the reduced fiber shift and therefore the full
qutrit-lifted slot operator. So the current host can now be tested in the
smallest cohomological language available.

The result is sharp: the current mixed-plane host already preserves the full
support package and qutrit lift, but it still carries only the zero cocycle on
the sign-trivial sector. So the live wall is now exactly the first genuine
nonzero sign-trivial cocycle witness on that same fixed host.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_current_k3_mixed_plane_cocycle_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_cocycle_failure_summary() -> dict[str, Any]:
    from w33_current_k3_mixed_plane_fiber_shift_failure_bridge import (
        build_current_k3_mixed_plane_fiber_shift_failure_summary,
    )
    from w33_k3_mixed_plane_cocycle_witness_bridge import (
        build_k3_mixed_plane_cocycle_witness_summary,
    )

    current = build_current_k3_mixed_plane_fiber_shift_failure_summary()
    exact = build_k3_mixed_plane_cocycle_witness_summary()

    current_host = current["current_mixed_plane_fiber_shift_state"]
    exact_cocycle = exact["mixed_plane_cocycle_witness"]

    return {
        "status": "ok",
        "current_mixed_plane_cocycle_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_slot_state"],
            "current_sign_trivial_cocycle_values": [0],
            "current_sign_nontrivial_cocycle_values": [0],
        },
        "exact_mixed_plane_cocycle_witness": exact_cocycle,
        "current_k3_mixed_plane_cocycle_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_current_mixed_plane_host_still_carries_only_the_zero_sign_trivial_cocycle_value": (
                current_host["current_slot_state"] == "zero_by_splitness"
            ),
            "the_exact_mixed_plane_witness_requires_a_nonzero_sign_trivial_cocycle_value": (
                exact_cocycle["field"] == "F3"
                and exact_cocycle["sign_trivial_cocycle_values"] != [0]
                and exact_cocycle["fiber_shift_matrix"] == [[0, 1], [0, 0]]
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_cocycle_witness_test_for_one_reason_only_the_nonzero_sign_trivial_cocycle_value_is_missing": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
                and current_host["current_slot_state"] == "zero_by_splitness"
                and exact_cocycle["sign_trivial_cocycle_values"] != [0]
                and exact_cocycle["fiber_shift_matrix"] == [[0, 1], [0, 0]]
            ),
            "the_live_external_wall_is_now_the_first_genuine_nonzero_sign_trivial_cocycle_witness_on_the_same_fixed_host": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and exact_cocycle["field"] == "F3"
                and exact_cocycle["sign_trivial_cocycle_values"] != [0]
                and exact_cocycle["fiber_shift_matrix"] == [[0, 1], [0, 0]]
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host is already structurally correct "
            "at the level of support and qutrit lift. What it still lacks is "
            "the smallest cohomological datum: a nonzero sign-trivial cocycle "
            "value. So the live wall is now exactly the first genuine nonzero "
            "sign-trivial cocycle witness on that same fixed host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_current_k3_mixed_plane_cocycle_failure_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
