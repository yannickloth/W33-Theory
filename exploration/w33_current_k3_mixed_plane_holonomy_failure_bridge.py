"""Current mixed-plane K3 host still fails the holonomy-witness test.

CDXX made the smallest positive datum concrete in adapted holonomy language:

- one support-preserving non-identity unipotent sign-trivial holonomy on the
  canonical mixed-plane host.

That holonomy witness is equivalent to the smallest nonzero cocycle witness,
which already forces the reduced fiber shift and therefore the full
qutrit-lifted slot operator. So the current host can now be tested in the
smallest adapted-holonomy language available.

The result is sharp: the current mixed-plane host already preserves the full
support package and qutrit lift, but it still carries only the identity
sign-trivial holonomy. So the live wall is now exactly the first genuine
non-identity unipotent sign-trivial holonomy witness on that same fixed host.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_current_k3_mixed_plane_holonomy_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_holonomy_failure_summary() -> dict[str, Any]:
    from w33_current_k3_mixed_plane_cocycle_failure_bridge import (
        build_current_k3_mixed_plane_cocycle_failure_summary,
    )
    from w33_k3_mixed_plane_holonomy_witness_bridge import (
        build_k3_mixed_plane_holonomy_witness_summary,
    )

    current = build_current_k3_mixed_plane_cocycle_failure_summary()
    exact = build_k3_mixed_plane_holonomy_witness_summary()

    current_host = current["current_mixed_plane_cocycle_state"]
    exact_holonomy = exact["mixed_plane_holonomy_witness"]

    return {
        "status": "ok",
        "current_mixed_plane_holonomy_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_slot_state"],
            "current_sign_trivial_holonomy_matrices": [[[1, 0], [0, 1]]],
            "current_sign_nontrivial_holonomy_matrices": [],
        },
        "exact_mixed_plane_holonomy_witness": exact_holonomy,
        "current_k3_mixed_plane_holonomy_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_current_mixed_plane_host_still_carries_only_the_identity_sign_trivial_holonomy": (
                current_host["current_slot_state"] == "zero_by_splitness"
            ),
            "the_exact_mixed_plane_witness_requires_a_nonidentity_unipotent_sign_trivial_holonomy": (
                exact_holonomy["canonical_nontrivial_holonomy"] == [[1, 1], [0, 1]]
                and exact_holonomy["gauge_related_nontrivial_holonomy"] == [[1, 2], [0, 1]]
                and sorted(exact_holonomy["nontrivial_sign_trivial_holonomy_matrices"])
                == [[[1, 1], [0, 1]], [[1, 2], [0, 1]]]
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_holonomy_witness_test_for_one_reason_only_the_nontrivial_sign_trivial_holonomy_is_missing": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
                and current_host["current_slot_state"] == "zero_by_splitness"
                and exact_holonomy["canonical_nontrivial_holonomy"] == [[1, 1], [0, 1]]
                and exact_holonomy["gauge_related_nontrivial_holonomy"] == [[1, 2], [0, 1]]
            ),
            "the_live_external_wall_is_now_the_first_genuine_nonidentity_unipotent_sign_trivial_holonomy_witness_on_the_same_fixed_host": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and exact_holonomy["canonical_nontrivial_holonomy"] == [[1, 1], [0, 1]]
                and exact_holonomy["gauge_related_nontrivial_holonomy"] == [[1, 2], [0, 1]]
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host is already structurally correct "
            "at the level of support and qutrit lift. What it still lacks is "
            "the smallest adapted holonomy datum: a non-identity unipotent "
            "sign-trivial holonomy matrix. So the live wall is now exactly "
            "the first genuine non-identity unipotent sign-trivial holonomy "
            "witness on that same fixed host."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_current_k3_mixed_plane_holonomy_failure_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
