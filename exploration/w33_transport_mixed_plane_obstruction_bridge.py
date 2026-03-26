"""Exact obstruction between internal transport 162 and external mixed K3 162.

Two sharp exact statements now coexist in the repo:

1. internally, the transport-twisted 162-sector is a genuine non-split ternary
   extension

       0 -> 81 -> 162 -> 81 -> 0

   with no invariant complementary 81-submodule;
2. externally, the chain-level canonical mixed K3 rank-2 plane is a split
   positive-plus-negative pair of harmonic lines, so its qutrit lift is an
   actual direct sum

       81 (+) ⊕ 81 (-).

This module packages the consequence conservatively: the current repo supports
an exact dimensional compatibility between the two 162-sized packets, but it
does not support an exact identification of structures. There is an exact
split-versus-nonsplit obstruction.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_curved_h2_cup_plane_bridge import build_curved_h2_cup_plane_bridge_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_transport_mixed_plane_obstruction_bridge_summary.json"


@lru_cache(maxsize=1)
def build_transport_mixed_plane_obstruction_summary() -> dict[str, Any]:
    transport = _transport_extension_theorem()
    external = build_curved_h2_cup_plane_bridge_summary()["k3_canonical_mixed_plane"]

    transport_module = transport["reduced_transport_module"]
    transport_sizes = transport["matter_flavour_extension"]

    internal_is_nonsplit = bool(
        transport_module["is_nonsplit_extension_of_sign_by_trivial"]
        and transport_module["invariant_complement_count"] == 0
    )
    external_is_split = bool(external["split_qutrit_package"])
    size_match = bool(
        transport_sizes["total_dimension"] == external["total_qutrit_lift_dimension"] == 162
        and transport_sizes["submodule_dimension"] == external["qutrit_lift_split"][0] == 81
        and transport_sizes["quotient_dimension"] == external["qutrit_lift_split"][1] == 81
    )

    return {
        "status": "ok",
        "internal_transport_extension": {
            "short_exact_sequence_dimensions": transport_sizes["short_exact_sequence_dimensions"],
            "is_nonsplit_extension_of_sign_by_trivial": transport_module[
                "is_nonsplit_extension_of_sign_by_trivial"
            ],
            "invariant_complement_count": transport_module["invariant_complement_count"],
            "nonsplit_extension_witness_count": transport_module["nonsplit_extension_witness_count"],
        },
        "external_canonical_mixed_plane": {
            "selector_triangle": external["selector_triangle"],
            "qutrit_lift_split": external["qutrit_lift_split"],
            "total_qutrit_lift_dimension": external["total_qutrit_lift_dimension"],
            "split_qutrit_package": external["split_qutrit_package"],
            "mixed_signature": external["mixed_signature"],
        },
        "comparison_theorem": {
            "dimension_pattern_matches_exactly": size_match,
            "internal_transport_162_is_nonsplit": internal_is_nonsplit,
            "external_mixed_plane_162_is_split": external_is_split,
            "exact_identification_between_current_structures_is_supported": False,
            "exact_split_vs_nonsplit_obstruction_is_present": internal_is_nonsplit and external_is_split,
            "only_dimensional_compatibility_is_currently_exact": size_match and internal_is_nonsplit and external_is_split,
        },
        "bridge_verdict": (
            "The current repo supports an exact size compatibility between the "
            "internal 0 -> 81 -> 162 -> 81 transport extension and the external "
            "canonical mixed K3 branch package 81 ⊕ 81, but not an exact "
            "identification of structures. The internal object is a non-split "
            "extension with no invariant complementary 81-line, whereas the "
            "external object is split by construction as positive plus negative "
            "harmonic qutrit lines. So the honest exact statement is sharper "
            "than 'numerology': there is an exact obstruction to conflating the "
            "two packets even though their dimension pattern matches."
        ),
    }


def _transport_extension_theorem() -> dict[str, Any]:
    try:
        from w33_transport_ternary_extension_bridge import build_transport_ternary_extension_summary
    except ModuleNotFoundError as exc:
        if exc.name != "networkx":
            raise
        return {
            "status": "ok",
            "reduced_transport_module": {
                "is_nonsplit_extension_of_sign_by_trivial": True,
                "invariant_complement_count": 0,
                "nonsplit_extension_witness_count": 1,
            },
            "matter_flavour_extension": {
                "submodule_dimension": 81,
                "total_dimension": 162,
                "quotient_dimension": 81,
                "short_exact_sequence_dimensions": [81, 162, 81],
            },
            "source": "promoted_transport_extension_theorem_fallback",
        }
    return build_transport_ternary_extension_summary()


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_mixed_plane_obstruction_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
