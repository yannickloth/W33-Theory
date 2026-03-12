"""Bridge from transport holonomy to the canonical ternary matter line.

This module chains the two exact breakthroughs together:

1. the W33 clique complex gives an 81-qutrit homological sector over F3;
2. the mod-3 reduction of the transport A2 local system acquires a unique
   invariant line.

Therefore q = 3 is special on both sides simultaneously. It is the coefficient
field of the homology, and it is also the first coefficient field on which the
nonabelian transport holonomy admits a canonical flat one-dimensional shadow.
Tensoring that invariant line with H1(W33; F3) gives a canonical transport-
stable 81-dimensional qutrit matter sector. Keeping the full reduced A2 fiber
gives a 162-dimensional matter-flavour sector, matching the exact internal
dimension already seen in the finite spectral-action layer.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_flat_ac_spectral_action import build_flat_product_summary
from w33_ternary_homological_code_bridge import build_ternary_homological_code_summary
from w33_transport_path_groupoid_bridge import build_transport_path_groupoid_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_transport_ternary_line_bridge_summary.json"


@lru_cache(maxsize=1)
def build_transport_ternary_line_summary() -> dict[str, Any]:
    transport = build_transport_path_groupoid_summary()
    ternary = build_ternary_homological_code_summary()
    flat = build_flat_product_summary()

    logical_qutrits = ternary["ternary_css_code"]["logical_qutrits"]
    invariant_line_rank = transport["ternary_reduction"]["common_fixed_subspace_dimension"]
    full_reduced_fiber_rank = 2
    canonical_sector_dimension = logical_qutrits * invariant_line_rank
    matter_flavour_dimension = logical_qutrits * full_reduced_fiber_rank
    internal_dimension = flat["coefficients"]["internal_dimension"]

    return {
        "status": "ok",
        "transport_side": {
            "real_flat_section_dimension": transport["real_local_system"]["common_fixed_subspace_dimension"],
            "ternary_flat_section_dimension": transport["ternary_reduction"]["common_fixed_subspace_dimension"],
            "invariant_line": transport["ternary_reduction"]["unique_invariant_projective_line"],
            "quotient_character_values": transport["ternary_reduction"]["quotient_character_values"],
        },
        "matter_side": {
            "homological_field": ternary["ternary_css_code"]["field"],
            "logical_qutrits": logical_qutrits,
            "canonical_transport_stable_sector_dimension": canonical_sector_dimension,
        },
        "combined_sector": {
            "full_reduced_a2_fiber_rank": full_reduced_fiber_rank,
            "matter_flavour_dimension": matter_flavour_dimension,
            "flat_internal_dimension": internal_dimension,
            "matches_flat_internal_dimension_exactly": matter_flavour_dimension == internal_dimension,
        },
        "bridge_verdict": (
            "The transport and homology breakthroughs now lock together. Over Z "
            "the A2 transport local system has no nonzero flat section, but over "
            "F3 it acquires a unique invariant line. Since the W33 homological "
            "matter sector is already exactly 81-dimensional over F3, that line "
            "selects a canonical transport-stable 81-qutrit sector. Keeping the "
            "full reduced A2 fiber doubles that to 162, and 81 x 2 matches the "
            "exact internal dimension of the finite spectral-action layer. So q = 3 "
            "is now special on both sides simultaneously: it is the homological "
            "coefficient field and the first field on which transport holonomy "
            "develops a canonical flat line."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_ternary_line_summary(), indent=2, default=int),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
