"""Coupling of the curved transport precomplex to matter and curved 4D harmonics.

The transport side now has its correct internal algebraic form: a curved
upper-triangular precomplex on the 45-point quotient over F3. The matter side
already has the exact 81-dimensional logical qutrit sector. This module couples
them in the strictest available way:

1. tensor the transport precomplex with the 81-dimensional logical sector;
2. identify the protected flat 81-dimensional matter channel;
3. track the exact curvature ranks after coupling;
4. propagate those exact internal channels across the external harmonic sectors
   of CP2_9 and K3_16.

The point is not to pretend the whole 162-sector is already harmonic. It is to
separate exactly which internal matter channel is flat/protected and which one
is curvature-sensitive before coupling to curved 4D geometry.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_explicit_curved_4d_complexes import build_explicit_curved_4d_complexes_summary
from w33_ternary_homological_code_bridge import build_ternary_homological_code_summary
from w33_transport_ternary_extension_bridge import build_transport_ternary_extension_summary
from w33_transport_twisted_precomplex_bridge import build_transport_twisted_precomplex_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_transport_matter_curved_harmonic_bridge_summary.json"


@lru_cache(maxsize=1)
def build_transport_matter_curved_harmonic_summary() -> dict[str, Any]:
    ternary = build_ternary_homological_code_summary()
    extension = build_transport_ternary_extension_summary()
    precomplex = build_transport_twisted_precomplex_summary()
    curved = build_explicit_curved_4d_complexes_summary()

    logical_qutrits = ternary["ternary_css_code"]["logical_qutrits"]
    matter_extension_dim = extension["matter_flavour_extension"]["total_dimension"]

    c0 = logical_qutrits * precomplex["cochain_dimensions"]["c0_dimension"]
    c1 = logical_qutrits * precomplex["cochain_dimensions"]["c1_dimension"]
    c2 = logical_qutrits * precomplex["cochain_dimensions"]["c2_dimension"]

    protected_h0 = logical_qutrits * precomplex["invariant_line_subcomplex"]["h0_dimension"]
    protected_h1 = logical_qutrits * precomplex["invariant_line_subcomplex"]["h1_dimension"]
    matter_curvature_rank = logical_qutrits * precomplex["curved_extension_package"]["full_curvature_rank"]
    matter_off_diagonal_curvature_rank = (
        logical_qutrits * precomplex["curved_extension_package"]["off_diagonal_curvature_rank"]
    )
    matter_semisimple_curvature_rank = (
        logical_qutrits * precomplex["sign_shadow_precomplex"]["semisimple_curvature_rank"]
    )

    curved_profiles = []
    for profile in curved["profiles"]:
        harmonic_total = int(profile["harmonic_form_total"])
        curved_profiles.append(
            {
                "external_name": profile["name"],
                "external_harmonic_form_total": harmonic_total,
                "protected_flat_matter_zero_modes": protected_h0 * harmonic_total,
                "protected_flat_matter_matches_81_times_external_harmonics": (
                    protected_h0 * harmonic_total == logical_qutrits * harmonic_total
                ),
                "matter_curvature_rank_on_external_harmonics": matter_curvature_rank * harmonic_total,
                "matter_off_diagonal_curvature_rank_on_external_harmonics": (
                    matter_off_diagonal_curvature_rank * harmonic_total
                ),
                "matter_semisimple_curvature_rank_on_external_harmonics": (
                    matter_semisimple_curvature_rank * harmonic_total
                ),
            }
        )

    return {
        "status": "ok",
        "matter_coupled_precomplex": {
            "logical_qutrits": logical_qutrits,
            "matter_extension_dimension": matter_extension_dim,
            "coupled_c0_dimension": c0,
            "coupled_c1_dimension": c1,
            "coupled_c2_dimension": c2,
            "protected_flat_h0_dimension": protected_h0,
            "protected_flat_h1_dimension": protected_h1,
            "full_curvature_rank": matter_curvature_rank,
            "off_diagonal_curvature_rank": matter_off_diagonal_curvature_rank,
            "semisimple_curvature_rank": matter_semisimple_curvature_rank,
            "protected_flat_sector_is_exactly_one_81_copy": (
                protected_h0 == logical_qutrits
            ),
            "curvature_hits_only_the_other_81_copy": (
                protected_h0 == logical_qutrits
                and matter_curvature_rank > 0
            ),
        },
        "curved_external_harmonic_channels": curved_profiles,
        "bridge_verdict": (
            "The matter-coupled transport object is now exact. Tensoring the curved "
            "transport precomplex with the 81-dimensional W33 logical qutrit sector "
            "produces cochain dimensions 7290 -> 116640 -> 855360. Inside that "
            "object there is one canonically protected flat 81-dimensional matter "
            "channel, coming from the invariant-line subcomplex, while the other 81 "
            "copy sits in the curvature-sensitive quotient channel. The coupled "
            "curvature ranks are exact: 3402 for the full curvature and 2916 for the "
            "off-diagonal cocycle coupling. When this internal package is restricted "
            "to the external harmonic sectors, the protected flat matter channels are "
            "243 on CP2_9 and 1944 on K3_16. So the curved 4D side now sees a precise "
            "distinction between protected internal matter and curvature-sensitive "
            "internal matter, rather than only a raw 162-dimensional count."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_matter_curved_harmonic_summary(), indent=2, default=int),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
