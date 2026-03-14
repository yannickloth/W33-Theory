"""Exact Monster/E8/supertrace completion bridge.

The transport-shell theorem already identified the local Monster complement as

    3^7 = 2160 + 27,

with ``2160`` the semisimple transport shell and ``27`` the generation block.

The next structural question is whether that same split already knows about the
exact finite spectral side.

It does.  The same ``2160`` is also

    - the second E8 theta coefficient,
    - generation_states * |chi(W33)| = 27 * 80,

while the full local Monster complement is

    2187 = 27 * 81 = 27 * (80 + 1).

Here ``80`` is the exact McKean-Singer / Euler magnitude of the full 480-chain
package and ``1`` is the unique selector line. So the complement is exactly

    generation * (supertrace magnitude + selector)
    = E8 second shell + generation.

This is the sharpest finite spectral realization yet of the local Monster
complement.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration", ROOT / "scripts", ROOT / "tools", ROOT / "pillars"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from THEORY_PART_CCXXIII_E8_THETA_SERIES import theta_coefficient_direct
from w33_curved_finite_spectral_reconstruction_bridge import (
    build_curved_finite_spectral_reconstruction_summary,
)
from w33_monster_transport_shell_bridge import build_monster_transport_shell_summary
from w33_transport_spectral_selector_bridge import build_transport_spectral_selector_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_supertrace_bridge_summary.json"


@lru_cache(maxsize=1)
def build_monster_supertrace_summary() -> dict[str, Any]:
    finite = build_curved_finite_spectral_reconstruction_summary()
    monster_transport = build_monster_transport_shell_summary()
    selector = build_transport_spectral_selector_summary()

    f0 = int(finite["reconstructed_graph_geometry"]["line_count"])
    f1 = int(finite["reconstructed_graph_geometry"]["edge_count"])
    f2 = int(finite["reconstructed_graph_geometry"]["triangle_count"])
    f3 = int(finite["reconstructed_graph_geometry"]["tetrahedron_count"])
    chi = f0 - f1 + f2 - f3
    chi_abs = abs(chi)

    b0 = int(finite["reconstructed_hodge_data"]["betti_numbers"]["b0"])
    b1 = int(finite["reconstructed_hodge_data"]["betti_numbers"]["b1"])
    b2 = int(finite["reconstructed_hodge_data"]["betti_numbers"]["b2"])
    b3 = int(finite["reconstructed_hodge_data"]["betti_numbers"]["b3"])
    supertrace = b0 - b1 + b2 - b3
    supertrace_abs = abs(supertrace)

    semisimple_transport_shell = int(
        monster_transport["transport_shell_dictionary"]["semisimple_transport_shell"]
    )
    generation_states = int(
        monster_transport["transport_shell_dictionary"]["generation_states"]
    )
    monster_complement_states = int(
        monster_transport["transport_shell_dictionary"]["monster_complement_states"]
    )
    selector_line = int(
        selector["dynamic_selection_bridge"]["invariant_line_h0_dimension"]
    )
    logical_qutrits = int(selector["dynamic_selection_bridge"]["logical_qutrits"])
    e8_second_shell = int(theta_coefficient_direct(2))

    return {
        "status": "ok",
        "spectral_dictionary": {
            "euler_characteristic": chi,
            "supertrace": supertrace,
            "supertrace_magnitude": supertrace_abs,
            "selector_line_dimension": selector_line,
            "logical_qutrits": logical_qutrits,
            "generation_states": generation_states,
            "e8_second_shell": e8_second_shell,
            "semisimple_transport_shell": semisimple_transport_shell,
            "monster_complement_states": monster_complement_states,
            "euler_matches_supertrace_exactly": chi == supertrace,
            "semisimple_equals_e8_second_shell": semisimple_transport_shell == e8_second_shell,
            "semisimple_equals_generation_times_supertrace_magnitude": (
                semisimple_transport_shell == generation_states * supertrace_abs
            ),
            "logical_equals_supertrace_magnitude_plus_selector": (
                logical_qutrits == supertrace_abs + selector_line
            ),
            "monster_complement_equals_generation_times_logical": (
                monster_complement_states == generation_states * logical_qutrits
            ),
            "monster_complement_equals_e8_second_shell_plus_generation": (
                monster_complement_states == e8_second_shell + generation_states
            ),
        },
        "bridge_verdict": (
            "The local Monster complement now has an exact finite spectral "
            "realization. The semisimple shell 2160 is simultaneously the second "
            "E8 theta coefficient and generation times the exact McKean-Singer "
            "supertrace magnitude: 2160 = 27*80. The full complement is then "
            "27*81 = 27*(80+1), where 1 is the unique selector line, so "
            "3^7 = 2160 + 27 is exactly generation*(supertrace magnitude + "
            "selector) = E8 second shell + generation. This ties the Monster "
            "closure directly to the exact finite 480-dimensional spectral "
            "package, not only to transport counts."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_supertrace_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
