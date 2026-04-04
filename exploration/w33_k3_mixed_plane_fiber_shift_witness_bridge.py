"""Mixed-plane K3 realization reduces to one nonzero fiber-shift witness.

CDXIV made the exact mixed-plane witness concrete as one unique support-
preserving rank-81 square-zero slot operator on the canonical mixed-plane
lift, with normal form ``I_81 ⊗ [[0,1],[0,0]]``.

But that operator still contains one obvious forced tensor factor:

- the qutrit lift ``I_81`` is already fixed by the host;
- the only genuinely nontrivial part is the reduced transport fiber shift
  ``N = [[0,1],[0,0]]``.

So the positive mixed-plane wall sharpens one more step. Exact K3 tail
realization is equivalent to one unique support-preserving nonzero fiber-shift
witness on the same fixed host, because the full rank-81 slot operator is
then forced as the exact qutrit lift ``I_81 ⊗ N``.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_fiber_shift_witness_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_mixed_plane_fiber_shift_witness_summary() -> dict[str, Any]:
    from w33_k3_mixed_plane_operator_witness_bridge import (
        build_k3_mixed_plane_operator_witness_summary,
    )
    from w33_transport_ternary_cocycle_bridge import (
        build_transport_ternary_cocycle_summary,
    )
    from w33_transport_unique_nonzero_cocycle_orbit_bridge import (
        build_transport_unique_nonzero_cocycle_orbit_bridge_summary,
    )

    operator = build_k3_mixed_plane_operator_witness_summary()
    cocycle = build_transport_ternary_cocycle_summary()
    orbit = build_transport_unique_nonzero_cocycle_orbit_bridge_summary()

    host = operator["canonical_mixed_plane_support"]
    slot_operator = operator["mixed_plane_operator_witness"]
    fiber = cocycle["fiber_nilpotent_operator"]
    matter = cocycle["matter_extension_operator"]
    orbit_data = orbit["ternary_fiber_shift_orbit"]

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "mixed_plane_fiber_shift_witness": {
            "fiber_shift_matrix": fiber["matrix"],
            "fiber_rank": fiber["rank"],
            "fiber_square_zero": fiber["square_zero"],
            "fiber_kernel_equals_image_equals_invariant_line": fiber[
                "kernel_equals_image_equals_invariant_line"
            ],
            "qutrit_lift_dimension": matter["logical_qutrits"],
            "forced_slot_operator_model": slot_operator["operator_model"],
            "nonzero_orbit_size": orbit_data["nonzero_scalar_orbit_size"],
        },
        "k3_mixed_plane_fiber_shift_witness_theorem": {
            "the_exact_mixed_plane_operator_witness_is_already_the_qutrit_lift_of_the_reduced_fiber_shift": (
                slot_operator["operator_model"] == "I_81 ⊗ [[0,1],[0,0]]"
                and matter["logical_qutrits"] == 81
                and fiber["matrix"] == [[0, 1], [0, 0]]
            ),
            "the_only_genuinely_nontrivial_part_of_the_operator_witness_is_the_nonzero_fiber_shift_n": (
                fiber["matrix"] == [[0, 1], [0, 0]]
                and fiber["rank"] == 1
                and fiber["square_zero"] is True
                and fiber["kernel_equals_image_equals_invariant_line"] is True
            ),
            "up_to_the_natural_gauge_there_is_only_one_nonzero_fiber_shift_orbit_available": (
                orbit["transport_unique_nonzero_cocycle_orbit_theorem"][
                    "up_to_the_natural_head_tail_basis_gauge_there_is_a_unique_nonzero_ternary_glue_orbit"
                ]
            ),
            "therefore_exact_k3_tail_realization_is_equivalent_to_one_unique_support_preserving_nonzero_fiber_shift_witness_on_the_canonical_mixed_plane_host": (
                slot_operator["operator_model"] == "I_81 ⊗ [[0,1],[0,0]]"
                and matter["logical_qutrits"] == 81
                and fiber["matrix"] == [[0, 1], [0, 0]]
                and orbit["transport_unique_nonzero_cocycle_orbit_theorem"][
                    "up_to_the_natural_head_tail_basis_gauge_there_is_a_unique_nonzero_ternary_glue_orbit"
                ]
            ),
            "the_live_external_wall_is_now_the_first_nonzero_mixed_plane_fiber_shift_witness_on_the_same_fixed_host": (
                host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
                and fiber["matrix"] == [[0, 1], [0, 0]]
                and matter["logical_qutrits"] == 81
            ),
        },
        "bridge_verdict": (
            "The mixed-plane K3 wall is now smaller than the full slot "
            "operator. The exact witness operator is already forced to be the "
            "qutrit lift I_81 tensor the reduced fiber shift [[0,1],[0,0]]. "
            "So the only genuinely nontrivial missing datum is one nonzero "
            "fiber-shift witness on the same fixed mixed-plane host; the full "
            "rank-81 slot operator then follows automatically."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_fiber_shift_witness_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
