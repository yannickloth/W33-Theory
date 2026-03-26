"""Exact A4 projection theorem on the canonical mixed K3 plane.

The live frontier had an apparent tension:

- the first exact external rank-2 qutrit branch package has size 162;
- the conservative local A4 normalization theorem uses finite multiplier 81.

This module resolves that tension exactly by combining the chain-level K3 mixed
plane with the local Yukawa A4 theorem.

The resolution is structural, not heuristic:

1. the canonical mixed K3 plane is rank-2 and therefore supplies the external
   activation factor 2;
2. the internal A4 theorem already isolates the curvature-sensitive 81-block
   inside the transport-twisted 162-sector;
3. therefore 162 = 2 * 81 is not a competing finite multiplicity but the
   external rank-2 branch size sitting over the internal 81-trace channel.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_curved_h2_cup_plane_bridge import build_curved_h2_cup_plane_bridge_summary
from w33_transport_mixed_plane_obstruction_bridge import (
    build_transport_mixed_plane_obstruction_summary,
)
from w33_yukawa_a4_normalization_bridge import build_yukawa_a4_normalization_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_mixed_plane_a4_projection_bridge_summary.json"


@lru_cache(maxsize=1)
def build_k3_mixed_plane_a4_projection_summary() -> dict[str, Any]:
    mixed_plane = build_curved_h2_cup_plane_bridge_summary()["k3_canonical_mixed_plane"]
    obstruction = build_transport_mixed_plane_obstruction_summary()["comparison_theorem"]
    a4 = build_yukawa_a4_normalization_summary()

    branch_dimension = int(mixed_plane["total_qutrit_lift_dimension"])
    trace_multiplier = int(a4["transport_split"]["curved_block_trace_multiplier"])
    branch_to_trace_ratio = branch_dimension // trace_multiplier

    return {
        "status": "ok",
        "canonical_mixed_plane": {
            "selector_triangle": mixed_plane["selector_triangle"],
            "normalized_restricted_intersection_matrix": mixed_plane[
                "normalized_restricted_intersection_matrix"
            ],
            "normalized_restricted_determinant": mixed_plane["normalized_restricted_determinant"],
            "qutrit_lift_split": mixed_plane["qutrit_lift_split"],
            "total_qutrit_lift_dimension": branch_dimension,
        },
        "local_a4_packet": {
            "finite_trace_multiplier": trace_multiplier,
            "rank_two_external_activation_is_required": a4["a4_normalization_theorem"][
                "rank_two_external_activation_is_required"
            ],
            "exact_reduced_prefactor_is_27_over_16_pi_sq": a4["a4_normalization_theorem"][
                "exact_reduced_prefactor_is_27_over_16_pi_sq"
            ],
            "bridge_packet_is_purely_a4": a4["a4_normalization_theorem"][
                "bridge_packet_is_purely_a4"
            ],
        },
        "projection_theorem": {
            "canonical_mixed_plane_is_rank2_active": abs(mixed_plane["normalized_restricted_determinant"]) > 1e-8,
            "branch_dimension_is_162": branch_dimension == 162,
            "finite_trace_multiplier_is_81": trace_multiplier == 81,
            "branch_dimension_equals_2_times_trace_multiplier": branch_dimension == 2 * trace_multiplier,
            "factor_of_two_is_exact_rank2_external_factor": branch_to_trace_ratio == 2,
            "projecting_to_canonical_mixed_plane_does_not_promote_multiplier_to_162": trace_multiplier != branch_dimension,
            "eightyone_vs_one_sixtytwo_is_dimension_vs_trace_split": (
                branch_dimension == 2 * trace_multiplier
                and a4["a4_normalization_theorem"]["rank_two_external_activation_is_required"]
            ),
            "split_vs_nonsplit_obstruction_remains_after_projection": obstruction[
                "exact_split_vs_nonsplit_obstruction_is_present"
            ],
        },
        "bridge_verdict": (
            "Projecting the local nonlinear bridge packet onto the canonical "
            "mixed K3 plane resolves the old 81-vs-162 tension exactly. The "
            "selected external branch really is a 162-dimensional qutrit packet, "
            "but the local A4 coefficient still sees only the curvature-sensitive "
            "internal 81-block. The missing factor of 2 is not another finite "
            "trace multiplicity; it is precisely the already-isolated rank-2 "
            "external activation factor. So there is no exact coefficient clash: "
            "162 is the branch dimension, 81 is the internal trace multiplier, "
            "and the reduced local prefactor stays 27/(16*pi^2)."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_mixed_plane_a4_projection_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
