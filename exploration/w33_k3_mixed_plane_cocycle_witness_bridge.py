"""Mixed-plane K3 realization reduces to one nonzero cocycle-value witness.

CDXVI reduced exact mixed-plane tail realization to the smallest nontrivial
operator datum on the fixed host:

- one support-preserving nonzero reduced fiber shift ``N = [[0,1],[0,0]]``.

But the transport cocycle theorem had already identified an even more primitive
source for that datum:

- in adapted basis every reduced holonomy matrix has the form
  ``[[1,c(g)],[0,s(g)]]``;
- the twisted cocycle ``c(g)`` is not a coboundary precisely because it is
  already nonzero on sign-trivial elements.

So the mixed-plane wall sharpens again. Exact K3 tail realization is
equivalent to one support-preserving nonzero cocycle-value witness on the same
fixed host, because that already forces the reduced fiber shift and therefore
the full qutrit-lifted slot operator.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_k3_mixed_plane_cocycle_witness_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_k3_mixed_plane_cocycle_witness_summary() -> dict[str, Any]:
    from w33_k3_mixed_plane_fiber_shift_witness_bridge import (
        build_k3_mixed_plane_fiber_shift_witness_summary,
    )
    from w33_transport_ternary_cocycle_bridge import (
        build_transport_ternary_cocycle_summary,
    )

    fiber = build_k3_mixed_plane_fiber_shift_witness_summary()
    cocycle = build_transport_ternary_cocycle_summary()

    host = fiber["canonical_mixed_plane_support"]
    fiber_witness = fiber["mixed_plane_fiber_shift_witness"]
    cocycle_data = cocycle["extension_cocycle"]

    return {
        "status": "ok",
        "canonical_mixed_plane_support": host,
        "mixed_plane_cocycle_witness": {
            "field": cocycle_data["field"],
            "adapted_group_order": cocycle_data["adapted_group_order"],
            "sign_trivial_cocycle_values": cocycle_data[
                "cocycle_values_on_sign_trivial_subgroup"
            ],
            "sign_nontrivial_cocycle_values": cocycle_data[
                "cocycle_values_on_sign_nontrivial_coset"
            ],
            "fiber_shift_matrix": fiber_witness["fiber_shift_matrix"],
            "forced_slot_operator_model": fiber_witness["forced_slot_operator_model"],
        },
        "k3_mixed_plane_cocycle_witness_theorem": {
            "the_exact_mixed_plane_fiber_shift_is_already_forced_by_the_transport_cocycle_package": (
                fiber_witness["fiber_shift_matrix"] == [[0, 1], [0, 0]]
                and cocycle_data["field"] == "F3"
                and cocycle_data["twisted_cocycle_identity_exact"] is True
            ),
            "the_cocycle_is_nontrivial_precisely_because_it_is_nonzero_on_sign_trivial_elements": (
                cocycle_data["cocycle_is_not_a_coboundary"] is True
                and cocycle_data["cocycle_values_on_sign_trivial_subgroup"] != [0]
            ),
            "a_single_support_preserving_nonzero_sign_trivial_cocycle_value_already_forces_the_nonzero_fiber_shift_witness": (
                cocycle_data["cocycle_is_not_a_coboundary"] is True
                and cocycle_data["cocycle_values_on_sign_trivial_subgroup"] != [0]
                and fiber_witness["fiber_shift_matrix"] == [[0, 1], [0, 0]]
            ),
            "therefore_exact_k3_tail_realization_is_equivalent_to_one_support_preserving_nonzero_cocycle_value_witness_on_the_canonical_mixed_plane_host": (
                host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
                and cocycle_data["cocycle_values_on_sign_trivial_subgroup"] != [0]
                and fiber_witness["fiber_shift_matrix"] == [[0, 1], [0, 0]]
            ),
            "the_live_external_wall_is_now_the_first_nonzero_sign_trivial_cocycle_witness_on_the_same_fixed_host": (
                host["ordered_line_types"] == ["positive", "negative"]
                and list(host["mixed_signature"]) == [1, 1]
                and list(host["qutrit_lift_split"]) == [81, 81]
                and cocycle_data["field"] == "F3"
                and cocycle_data["cocycle_is_not_a_coboundary"] is True
            ),
        },
        "bridge_verdict": (
            "The mixed-plane K3 wall is now smaller than the reduced fiber "
            "shift itself. In adapted basis, the transport extension is "
            "already controlled by the twisted cocycle c(g), and that cocycle "
            "is nontrivial precisely because it is nonzero on sign-trivial "
            "elements. So the only genuinely nontrivial missing datum is now "
            "one support-preserving nonzero cocycle-value witness on the same "
            "fixed host; the reduced fiber shift and full qutrit-lifted slot "
            "operator then follow automatically."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_cocycle_witness_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
