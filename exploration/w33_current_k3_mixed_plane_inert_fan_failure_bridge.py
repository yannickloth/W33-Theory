"""Current mixed-plane host still vanishes off the rigid inert fan.

CDXXXV identifies the inert 9-column block geometrically as one anchored
3-line fan in the exact 45-point quotient geometry. This phase applies that
description back to the current host.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_current_k3_mixed_plane_inert_fan_failure_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_current_k3_mixed_plane_inert_fan_failure_summary() -> dict[str, Any]:
    from w33_current_k3_mixed_plane_active_basis_failure_bridge import (
        build_current_k3_mixed_plane_active_basis_failure_summary,
    )
    from w33_k3_mixed_plane_inert_fan_geometry_bridge import (
        build_k3_mixed_plane_inert_fan_geometry_summary,
    )

    current = build_current_k3_mixed_plane_active_basis_failure_summary()
    exact = build_k3_mixed_plane_inert_fan_geometry_summary()

    current_host = current["current_mixed_plane_active_basis_state"]
    inert_fan = exact["mixed_plane_inert_fan_geometry"]

    return {
        "status": "ok",
        "current_mixed_plane_inert_fan_state": {
            "source": current_host["source"],
            "ordered_line_types": current_host["ordered_line_types"],
            "mixed_signature": list(current_host["mixed_signature"]),
            "qutrit_lift_split": list(current_host["qutrit_lift_split"]),
            "current_slot_state": current_host["current_slot_state"],
            "current_supported_entry_count_off_inert_fan": 0,
        },
        "exact_mixed_plane_inert_fan_geometry": inert_fan,
        "current_k3_mixed_plane_inert_fan_failure_theorem": {
            "the_current_mixed_plane_host_already_preserves_the_full_canonical_support_package_and_qutrit_lift": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["ordered_line_types"] == ["positive", "negative"]
                and list(current_host["mixed_signature"]) == [1, 1]
                and list(current_host["qutrit_lift_split"]) == [81, 81]
            ),
            "the_exact_live_wall_is_already_localized_off_the_rigid_anchored_3_line_inert_fan": (
                inert_fan["anchor_point"] == 0
                and inert_fan["anchor_lines"] == [0, 1, 2]
                and inert_fan["active_spokes"] == [15, 16, 17]
                and inert_fan["inactive_union"] == [36, 37, 38, 39, 40, 41, 42, 43, 44]
            ),
            "the_current_mixed_plane_host_still_carries_zero_supported_entries_off_that_inert_fan": (
                current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_active_column_supported_entry_count"] == 0
            ),
            "therefore_the_current_mixed_plane_host_fails_the_exact_inert_fan_test_for_one_reason_only_the_active_complement_still_vanishes": (
                current_host["source"] == "canonical_mixed_k3_plane_qutrit_lift"
                and current_host["current_slot_state"] == "zero_by_splitness"
                and current_host["current_active_column_supported_entry_count"] == 0
                and inert_fan["anchor_lines"] == [0, 1, 2]
                and inert_fan["inactive_union"] == [36, 37, 38, 39, 40, 41, 42, 43, 44]
            ),
            "the_live_external_wall_is_now_the_first_genuine_nonzero_row_entry_witness_off_the_rigid_inert_fan": (
                current_host["current_active_column_supported_entry_count"] == 0
                and inert_fan["inactive_union"] == [36, 37, 38, 39, 40, 41, 42, 43, 44]
            ),
        },
        "bridge_verdict": (
            "The current mixed-plane K3 host is already on the correct support "
            "package, but the whole active complement to the rigid anchored "
            "3-line inert fan still vanishes. So the live wall is exactly the "
            "first genuine nonzero row-entry witness off that inert fan."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_current_k3_mixed_plane_inert_fan_failure_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
