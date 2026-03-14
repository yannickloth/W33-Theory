"""Exact local-to-global moonshine lift from the live Monster shell.

The local Monster/Landauer bridge already pins down the exact semisimple shell

    2160 = Theta_E8[2],

inside the local ``3B`` complement ``3^7 = 2160 + 27``.

The next structural question is whether that local shell already knows the
first global moonshine coefficient. It does.

The same cyclotomic pair that controls the promoted W33 package,

    Phi_3 = 13,  Phi_6 = 7,

lifts the local shell to the Leech kissing number:

    196560 = 2160 * Phi_3 * Phi_6 = 2160 * 91.

The first nontrivial moonshine coefficient is then recovered by adding the
exact four-dimensional matter selector:

    196884 = 196560 + 4 * 81 = 196560 + (q+1) * q^4.

So the live data already carries a complete local-to-global chain

    2160 -> 196560 -> 196884

through the same q=3, Phi_3, Phi_6, and 81-state structures that govern the
rest of the promoted theory.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration", ROOT / "tools", ROOT / "pillars"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from THEORY_PART_CCXXIII_E8_THETA_SERIES import moonshine_decompositions, theta_coefficient_direct
from w33_monster_supertrace_bridge import build_monster_supertrace_summary
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary
from w33_transport_spectral_selector_bridge import build_transport_spectral_selector_summary


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_monster_moonshine_lift_bridge_summary.json"


@lru_cache(maxsize=1)
def build_monster_moonshine_lift_summary() -> dict[str, Any]:
    cyclotomic = build_standard_model_cyclotomic_summary()
    monster_supertrace = build_monster_supertrace_summary()
    selector = build_transport_spectral_selector_summary()
    moonshine = moonshine_decompositions()

    q = int(cyclotomic["cyclotomic_data"]["q"])
    phi3 = int(cyclotomic["cyclotomic_data"]["phi3"])
    phi6 = int(cyclotomic["cyclotomic_data"]["phi6"])
    local_second_shell = int(monster_supertrace["spectral_dictionary"]["e8_second_shell"])
    logical_qutrits = int(selector["dynamic_selection_bridge"]["logical_qutrits"])
    selector_line = int(selector["dynamic_selection_bridge"]["invariant_line_h0_dimension"])

    leech_kissing_number = int(moonshine["196560"])
    moonshine_gap = int(moonshine["324"])
    first_moonshine_coefficient = int(moonshine["196884"])
    smallest_monster_irrep = int(moonshine["196883"])

    cyclotomic_lift_factor = phi3 * phi6
    spacetime_factor = q + 1

    return {
        "status": "ok",
        "moonshine_lift_dictionary": {
            "q": q,
            "phi3": phi3,
            "phi6": phi6,
            "cyclotomic_lift_factor": cyclotomic_lift_factor,
            "local_second_shell": local_second_shell,
            "leech_kissing_number": leech_kissing_number,
            "logical_qutrits": logical_qutrits,
            "spacetime_factor": spacetime_factor,
            "moonshine_gap": moonshine_gap,
            "first_moonshine_coefficient": first_moonshine_coefficient,
            "smallest_monster_irrep": smallest_monster_irrep,
            "selector_line_dimension": selector_line,
            "local_second_shell_matches_theta_e8_second_shell": (
                local_second_shell == int(theta_coefficient_direct(2))
            ),
            "leech_equals_local_second_shell_times_phi3_phi6": (
                leech_kissing_number == local_second_shell * cyclotomic_lift_factor
            ),
            "moonshine_gap_equals_q_plus_1_times_logical_qutrits": (
                moonshine_gap == spacetime_factor * logical_qutrits
            ),
            "moonshine_gap_equals_q_plus_1_times_q_to_four": (
                moonshine_gap == spacetime_factor * q**4
            ),
            "first_moonshine_equals_leech_plus_gap": (
                first_moonshine_coefficient == leech_kissing_number + moonshine_gap
            ),
            "first_moonshine_equals_selector_plus_smallest_monster_irrep": (
                first_moonshine_coefficient == selector_line + smallest_monster_irrep
            ),
            "first_moonshine_equals_cyclotomic_lifted_shell_plus_spacetime_matter": (
                first_moonshine_coefficient
                == local_second_shell * cyclotomic_lift_factor
                + spacetime_factor * logical_qutrits
            ),
        },
        "bridge_verdict": (
            "The live Monster shell now lifts exactly to the first global "
            "moonshine coefficient. The local semisimple shell 2160 is already "
            "the second E8 theta shell, and multiplying it by the same promoted "
            "cyclotomic pair Phi_3*Phi_6 = 13*7 gives the Leech kissing number "
            "196560. Adding the exact four-dimensional matter selector "
            "(q+1)*q^4 = 4*81 = 324 then gives 196884. So the chain "
            "2160 -> 196560 -> 196884 is already carried by the same q=3, "
            "Phi_3, Phi_6, and 81-state structures that govern the promoted "
            "W33 package."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_monster_moonshine_lift_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
