"""Current mixed-plane K3 host still fails the operator-witness test.

CDXIV identified the exact witness shape the repo can now recognize on the
canonical mixed-plane lift:

- preserve the full mixed-plane support package;
- keep the existing tail-to-head slot of shape ``81 x 81``;
- realize the unique nonzero rank-81 square-zero operator normal form.

The present mixed-plane host is already correct in every structural way except
the last one. It still carries the split zero operator in that existing slot.
So the remaining wall is now precisely the first genuine nonzero mixed-plane
slot operator witness on the same fixed host.
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
    / "w33_current_k3_mixed_plane_operator_witness_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_operator_witness_failure_summary() -> dict[str, Any]:
    from w33_external_glue_zero_forcing_bridge import (
        build_external_glue_zero_forcing_bridge_summary,
    )
    from w33_k3_mixed_plane_operator_witness_bridge import (
        build_k3_mixed_plane_operator_witness_summary,
    )

    external = build_external_glue_zero_forcing_bridge_summary()
    witness = build_k3_mixed_plane_operator_witness_summary()

    current_host = external["current_external_transport_object"]
    current_slot = external["external_glue_slot"]
    exact = witness["mixed_plane_operator_witness"]

    return {
        "status": "ok",
        "current_mixed_plane_operator_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "slot_direction": current_slot["slot_direction"],
            "slot_shape": list(current_slot["slot_shape"]),
            "current_rank": current_slot["current_external_rank"],
            "current_state": current_slot["current_external_state"],
        },
        "exact_mixed_plane_operator_witness": exact,
        "current_k3_mixed_plane_operator_witness_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_current_mixed_plane_host_still_carries_the_split_zero_operator_in_the_existing_slot": (
                current_slot["slot_direction"] == "tail_to_head"
                and list(current_slot["slot_shape"]) == [81, 81]
                and current_slot["current_external_rank"] == 0
                and current_slot["current_external_state"] == "zero_by_splitness"
            ),
            "the_exact_mixed_plane_witness_requires_the_unique_nonzero_rank_81_square_zero_operator": (
                exact["slot_direction"] == "tail_to_head"
                and list(exact["slot_shape"]) == [81, 81]
                and exact["rank"] == 81
                and exact["nullity"] == 81
                and exact["square_zero"] is True
                and exact["operator_model"] == "I_81 ⊗ [[0,1],[0,0]]"
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_operator_witness_test_for_one_reason_only_the_nonzero_slot_operator_is_missing": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
                and current_slot["current_external_rank"] == 0
                and current_slot["current_external_state"] == "zero_by_splitness"
                and exact["rank"] == 81
                and exact["square_zero"] is True
            ),
            "the_live_external_wall_is_now_the_first_genuine_nonzero_mixed_plane_slot_operator_witness_on_the_same_fixed_host": (
                current_slot["current_external_state"] == "zero_by_splitness"
                and exact["rank"] == 81
                and exact["square_zero"] is True
                and exact["operator_model"] == "I_81 ⊗ [[0,1],[0,0]]"
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host is already structurally correct: "
            "it preserves the canonical support package and carries the right "
            "81x81 tail slot. What it still lacks is only the nonzero slot "
            "operator. The present host carries the split zero operator, "
            "while the exact witness requires the unique rank-81 square-zero "
            "normal form. So the live wall is now the first genuine nonzero "
            "mixed-plane slot-operator witness on this same fixed host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(
            build_current_k3_mixed_plane_operator_witness_failure_summary(), indent=2
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
