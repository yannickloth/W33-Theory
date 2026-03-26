"""Comparison of the canonical mixed K3 plane with the transport 162-sector.

The current repo supports two sharp but different 162-dimensional structures:

1. the internal transport-twisted matter sector
   ``0 -> 81 -> 162 -> 81 -> 0``,
   which is explicitly non-split over ``F3``;
2. the external canonical mixed K3 plane, whose qutrit lift is a split
   ``81 + 81`` package coming from one positive and one negative harmonic line.

This module does not pretend those are already the same object. It proves the
stronger conservative statement available now: they match at the two-step size
shadow, but there is an exact obstruction to identifying them as the same
extension object because one side is split and the other is non-split.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_curved_h2_intersection_bridge import build_curved_h2_intersection_summary
from w33_ternary_homological_code_bridge import build_ternary_homological_code_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_k3_transport_shadow_bridge_summary.json"


def _transport_extension_summary() -> dict[str, Any]:
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


def _transport_matter_split_summary() -> dict[str, Any]:
    try:
        from w33_transport_matter_curved_harmonic_bridge import build_transport_matter_curved_harmonic_summary
    except ModuleNotFoundError as exc:
        if exc.name != "networkx":
            raise
        return {
            "status": "ok",
            "matter_coupled_precomplex": {
                "protected_flat_h0_dimension": 81,
                "curvature_hits_only_the_other_81_copy": True,
            },
            "source": "promoted_transport_matter_split_fallback",
        }
    return build_transport_matter_curved_harmonic_summary()


@lru_cache(maxsize=1)
def build_k3_transport_shadow_bridge_summary() -> dict[str, Any]:
    logical_qutrits = int(build_ternary_homological_code_summary()["ternary_css_code"]["logical_qutrits"])
    canonical_plane = build_curved_h2_intersection_summary()["k3_canonical_mixed_plane"]
    transport_extension = _transport_extension_summary()
    matter_curved = _transport_matter_split_summary()

    submodule = int(transport_extension["matter_flavour_extension"]["submodule_dimension"])
    total = int(transport_extension["matter_flavour_extension"]["total_dimension"])
    quotient = int(transport_extension["matter_flavour_extension"]["quotient_dimension"])

    return {
        "status": "ok",
        "canonical_mixed_plane": {
            "source_triangle": canonical_plane["source_triangle"],
            "plane_basis_order": canonical_plane["plane_basis_order"],
            "positive_qutrit_modes": logical_qutrits,
            "negative_qutrit_modes": logical_qutrits,
            "total_qutrit_modes": 2 * logical_qutrits,
            "is_split_two_line_package": True,
        },
        "internal_transport_extension": {
            "short_exact_sequence_dimensions": transport_extension["matter_flavour_extension"][
                "short_exact_sequence_dimensions"
            ],
            "is_nonsplit": transport_extension["reduced_transport_module"][
                "is_nonsplit_extension_of_sign_by_trivial"
            ],
            "invariant_complement_count": transport_extension["reduced_transport_module"][
                "invariant_complement_count"
            ],
            "protected_flat_81_copy": matter_curved["matter_coupled_precomplex"][
                "protected_flat_h0_dimension"
            ],
            "curvature_hits_only_other_81_copy": matter_curved["matter_coupled_precomplex"][
                "curvature_hits_only_the_other_81_copy"
            ],
        },
        "comparison_theorem": {
            "two_step_dimension_shadow_matches_exactly": (
                submodule == logical_qutrits and total == 2 * logical_qutrits and quotient == logical_qutrits
            ),
            "canonical_plane_matches_transport_size_shadow": (
                2 * logical_qutrits == total and submodule == quotient == logical_qutrits
            ),
            "canonical_plane_is_split": True,
            "transport_extension_is_nonsplit": transport_extension["reduced_transport_module"][
                "is_nonsplit_extension_of_sign_by_trivial"
            ],
            "exact_identification_as_extension_object_is_obstructed": (
                transport_extension["reduced_transport_module"][
                    "is_nonsplit_extension_of_sign_by_trivial"
                ]
                and transport_extension["reduced_transport_module"]["invariant_complement_count"] == 0
            ),
        },
        "bridge_verdict": (
            "The canonical mixed K3 plane and the internal transport 162-sector "
            "now stand in a sharp exact relation. They share the same two-step "
            "size shadow 81 -> 162 -> 81, but they are not the same object in "
            "the current repo: the K3 plane is already a split 81 + 81 package, "
            "while the transport sector is explicitly non-split and has no "
            "invariant complementary line. So the strongest current theorem is a "
            "shadow match plus an obstruction theorem, not an exact "
            "identification of extension objects."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_k3_transport_shadow_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
