"""Exact torus-shell lift to Klein quartic Hurwitz extremality.

The promoted torus/Klein shell already contains the exact packet

    84 -> 168 -> 336.

This module packages the strongest clean classical interpretation of that
ladder:

    84  = the Hurwitz coefficient,
    168 = 84 (g - 1) at genus g = 3,
    336 = 2 * 168.

The genus-3 case is the Klein quartic, the smallest Hurwitz surface. In the
live repo the same 168 is already the Heawood bipartition-preserving symmetry
order, and the same 336 is already the full Heawood symmetry order. Since the
single toroidal flag packet is exactly 84, the torus shell is already the
Hurwitz coefficient that lifts to the Klein quartic extremal symmetry packet.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_heawood_klein_symmetry_bridge import build_heawood_klein_symmetry_summary
from w33_surface_hurwitz_flag_bridge import build_surface_hurwitz_flag_summary
from w33_surface_physics_shell_bridge import build_surface_physics_shell_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_klein_hurwitz_extremal_bridge_summary.json"

KLEIN_QUARTIC_GENUS = 3


@lru_cache(maxsize=1)
def build_klein_hurwitz_extremal_summary() -> dict[str, Any]:
    heawood = build_heawood_klein_symmetry_summary()
    surface = build_surface_hurwitz_flag_summary()
    physics_shell = build_surface_physics_shell_summary()

    hurwitz_coefficient = int(surface["surface_hurwitz_dictionary"]["single_surface_flags"])
    preserving_order = int(
        heawood["bipartition_preserving_symmetry"]["heawood_bipartition_preserving_order"]
    )
    full_order = int(heawood["full_symmetry"]["full_heawood_automorphism_order"])
    gauge_dimension = int(physics_shell["standard_model_gauge_dictionary"]["gauge_dimension"])
    phi6 = int(physics_shell["standard_model_gauge_dictionary"]["beta0_qcd"])
    g2_dimension = int(physics_shell["standard_model_gauge_dictionary"]["g2_dimension"])

    return {
        "status": "ok",
        "hurwitz_extremal_dictionary": {
            "klein_quartic_genus": KLEIN_QUARTIC_GENUS,
            "hurwitz_coefficient": hurwitz_coefficient,
            "heawood_preserving_order": preserving_order,
            "heawood_full_order": full_order,
            "standard_model_gauge_dimension": gauge_dimension,
            "phi6": phi6,
            "g2_dimension": g2_dimension,
        },
        "exact_factorizations": {
            "preserving_order_equals_hurwitz_bound_at_genus_3": (
                preserving_order == hurwitz_coefficient * (KLEIN_QUARTIC_GENUS - 1)
            ),
            "preserving_order_equals_two_times_hurwitz_coefficient": (
                preserving_order == 2 * hurwitz_coefficient
            ),
            "preserving_order_equals_2_k_phi6": preserving_order == 2 * gauge_dimension * phi6,
            "preserving_order_equals_k_times_g2_dimension": (
                preserving_order == gauge_dimension * g2_dimension
            ),
            "full_order_equals_two_times_preserving_order": full_order == 2 * preserving_order,
            "full_order_equals_four_times_hurwitz_coefficient": full_order == 4 * hurwitz_coefficient,
        },
        "bridge_verdict": (
            "The torus/Klein shell is already the Klein quartic Hurwitz packet in "
            "compressed form. The single toroidal flag packet is exactly 84, which "
            "is the Hurwitz coefficient. At genus 3, the Hurwitz bound gives "
            "84(g-1) = 168, and this is exactly the promoted Heawood/Klein "
            "bipartition-preserving symmetry order. Doubling once more gives the "
            "full Heawood order 336. So the live ladder 84 -> 168 -> 336 is not "
            "just a surface-count pattern: it is the torus shell, the genus-3 "
            "Klein quartic extremal symmetry packet, and the full Heawood symmetry "
            "packet written in one exact sequence."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_klein_hurwitz_extremal_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
