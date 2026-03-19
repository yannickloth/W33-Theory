"""Exact decimal/surface flag shell bridge.

The decimal/Fano side and the toroidal surface selector side meet on one exact
packet:

    84 = 12 * 7 = 14 * 6 = 21 * 4

where

    12 = q(q+1)           is the surface genus denominator at q=3,
    7  = Phi_6(q)         is the first toroidal dual value,
    14 = Heawood vertices = dim(G2),
    6  = ord_7(10)        is the decimal generator order / shared six-channel,
    21 = Heawood edges    = AG(2,1) / Fano-flag packet,
    4  = q+1 = mu         is the tetrahedral fixed point.

So the user-facing mod-12 surface selector and the old decimal 1/7 clue are
already the same rigid shell, not two unrelated numerology tracks.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from w33_mod7_fano_duality_bridge import build_mod7_fano_duality_summary
from w33_surface_congruence_selector_bridge import build_surface_congruence_selector_summary
from w33_surface_hurwitz_flag_bridge import build_surface_hurwitz_flag_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_decimal_surface_flag_bridge_summary.json"


@lru_cache(maxsize=1)
def build_decimal_surface_flag_summary() -> dict[str, Any]:
    mod7 = build_mod7_fano_duality_summary()
    surface_selector = build_surface_congruence_selector_summary()
    flag_shell = build_surface_hurwitz_flag_summary()

    decimal_order = int(mod7["mod7_dictionary"]["decimal_generator_order"])
    decimal_square_order = int(mod7["mod7_dictionary"]["decimal_square_order"])
    genus_denominator = int(flag_shell["surface_hurwitz_dictionary"]["genus_denominator"])
    phi6 = int(flag_shell["surface_hurwitz_dictionary"]["phi6"])
    heawood_vertices = int(flag_shell["surface_hurwitz_dictionary"]["heawood_vertices"])
    heawood_edges = int(flag_shell["surface_hurwitz_dictionary"]["heawood_edges"])
    tetra_fixed_point = int(flag_shell["surface_hurwitz_dictionary"]["tetrahedron_fixed_point"])
    shared_six = int(flag_shell["surface_hurwitz_dictionary"]["shared_six_channel"])
    single_surface_flags = int(flag_shell["surface_hurwitz_dictionary"]["single_surface_flags"])
    first_toroidal_value = int(surface_selector["fixed_and_first_torus_values"]["first_toroidal_dual_value"])

    return {
        "status": "ok",
        "decimal_surface_dictionary": {
            "decimal_generator": 10,
            "decimal_generator_mod_7": int(mod7["mod7_dictionary"]["decimal_generator_mod_7"]),
            "decimal_generator_order_mod_7": decimal_order,
            "decimal_square_order_mod_7": decimal_square_order,
            "genus_denominator": genus_denominator,
            "first_toroidal_dual_value": first_toroidal_value,
            "phi6": phi6,
            "heawood_vertices": heawood_vertices,
            "heawood_edges": heawood_edges,
            "tetrahedral_fixed_point": tetra_fixed_point,
            "shared_six_channel": shared_six,
            "single_surface_flags": single_surface_flags,
        },
        "exact_factorizations": {
            "decimal_order_equals_shared_six_channel": decimal_order == shared_six,
            "first_toroidal_value_equals_phi6": first_toroidal_value == phi6,
            "single_surface_flags_equals_12_times_7": single_surface_flags == genus_denominator * phi6,
            "single_surface_flags_equals_14_times_6": single_surface_flags == heawood_vertices * decimal_order,
            "single_surface_flags_equals_21_times_4": single_surface_flags == heawood_edges * tetra_fixed_point,
            "decimal_order_plus_one_equals_first_toroidal_value": decimal_order + 1 == first_toroidal_value,
        },
        "bridge_verdict": (
            "The old decimal 1/7 clue and the toroidal surface selector already "
            "meet on one exact shell. The decimal generator has order 6 mod 7, "
            "the first toroidal dual value is Phi_6 = 7, the mod-12 surface "
            "denominator is q(q+1) = 12, and the tetrahedral fixed point is 4. "
            "The same single-surface flag packet is therefore simultaneously "
            "84 = 12*7 = 14*6 = 21*4. So the decimal transition length, the "
            "toroidal selector, the G2/Heawood packet, the AG21/Fano packet, "
            "and the tetra fixed point are already one exact object."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_decimal_surface_flag_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
