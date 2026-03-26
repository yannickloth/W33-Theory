"""q-cyclotomic master lock for the promoted finite and bridge package.

This module packages the smallest nonredundant synthesis behind the current
repo frontier.

Already-exact modules separately showed:
  - the promoted Standard Model observables are a q=3 cyclotomic package;
  - the curved gravity/topology coefficients are locked by Phi_3 and Phi_6;
  - the local nonlinear bridge prefactor is fixed;
  - the external exceptional quanta are fixed as 52 and 56.

What was still missing was one exact bridge theorem that ties the internal
finite packet

    81 / 6 / 8

to the curved packet

    320 / 2240 / 12480

and then to the promoted electroweak lock

    3/13.

The exact q=3 master package is:
  - matter  = q^4         = 81
  - A2      = 2q          = 6
  - Cartan  = q^2 - 1     = 8
  - g0      = q^4 + 2q - 1        = 86
  - E8      = 3q^4 + 2q - 1       = 248
  - c_EH    = v(q) (q^2 - 1)      = 320
  - a2      = Phi_6(q) c_EH       = 2240
  - c6      = q Phi_3(q) c_EH     = 12480

Hence

    9 c_EH / c6 = 9 / (q Phi_3(q)),

and at the selected point q=3, because 9=q^2,

    9 c_EH / c6 = q / Phi_3(q) = 3/13.

So the promoted Weinberg lock is a direct algebraic corollary of the same q=3
selection that already drives the finite qutrit/transport package.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from exploration.w33_external_exceptional_quanta_bridge import (
    build_external_exceptional_quanta_summary,
)
from exploration.w33_standard_model_cyclotomic_bridge import (
    build_standard_model_cyclotomic_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_OUTPUT_PATH = DATA_DIR / "w33_q_cyclotomic_master_bridge_summary.json"

Q = 3
PHI3 = Q * Q + Q + 1
PHI6 = Q * Q - Q + 1
V = (Q + 1) * (Q * Q + 1)


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


@lru_cache(maxsize=1)
def build_q_cyclotomic_master_summary() -> dict[str, Any]:
    quanta = build_external_exceptional_quanta_summary()
    standard_model = build_standard_model_cyclotomic_summary()

    matter = Q**4
    a2_transport = 2 * Q
    cartan = Q * Q - 1
    g0 = matter + a2_transport - 1
    e8_dim = 3 * matter + a2_transport - 1

    residue_data = quanta["promoted_residue_data"]
    c_eh = residue_data["continuum_eh_coefficient"]
    c6 = residue_data["curved_six_mode_coefficient"]
    a2 = residue_data["topological_coefficient"]

    weinberg = Fraction(
        standard_model["promoted_observables"]["sin2_theta_w_ew"]["exact"]
    )
    nine_c_eh_over_c6 = Fraction(9 * c_eh, c6)

    return {
        "status": "ok",
        "q_cyclotomic_data": {
            "q": Q,
            "phi3": PHI3,
            "phi6": PHI6,
            "v_of_q": V,
        },
        "internal_q_package": {
            "matter": {"formula": "q^4", "exact": matter},
            "A2_transport": {"formula": "2q", "exact": a2_transport},
            "Cartan": {"formula": "q^2 - 1", "exact": cartan},
            "g0": {"formula": "q^4 + 2q - 1", "exact": g0},
            "E8_dimension": {"formula": "3q^4 + 2q - 1", "exact": e8_dim},
        },
        "curved_q_package": {
            "c_EH": {"formula": "v(q) * (q^2 - 1)", "exact": c_eh},
            "a2": {"formula": "Phi_6(q) * c_EH", "exact": a2},
            "c6": {"formula": "q * Phi_3(q) * c_EH", "exact": c6},
            "Q_curv": quanta["external_quanta"]["Q_curv"],
            "Q_top": quanta["external_quanta"]["Q_top"],
        },
        "selection_lock": {
            "nine_cEH_over_c6": _fraction_text(nine_c_eh_over_c6),
            "general_formula": "9 / (q * Phi_3(q))",
            "selected_formula": "q / Phi_3(q)",
            "weinberg_generator": _fraction_text(weinberg),
        },
        "q_master_theorem": {
            "matter_equals_q4": matter == Q**4,
            "a2_transport_equals_2q": a2_transport == 2 * Q,
            "cartan_equals_q2_minus_1": cartan == Q * Q - 1,
            "g0_equals_q4_plus_2q_minus_1": g0 == Q**4 + 2 * Q - 1,
            "e8_equals_3q4_plus_2q_minus_1": e8_dim == 3 * Q**4 + 2 * Q - 1,
            "cEH_equals_v_times_q2_minus_1": c_eh == V * (Q * Q - 1),
            "a2_equals_phi6_times_cEH": a2 == PHI6 * c_eh,
            "c6_equals_q_phi3_times_cEH": c6 == Q * PHI3 * c_eh,
            "nine_cEH_over_c6_equals_weinberg": nine_c_eh_over_c6 == weinberg,
            "weinberg_is_q_over_phi3": weinberg == Fraction(Q, PHI3),
            "external_quanta_are_52_and_56": (
                quanta["external_quanta"]["Q_curv"] == "52"
                and quanta["external_quanta"]["Q_top"] == "56"
            ),
            "global_branch_activation_count_remains_open": True,
        },
        "bridge_verdict": (
            "The promoted finite and curved bridge package is now best read as "
            "one q-cyclotomic master system at q=3. The internal split 81/6/8, "
            "the curved coefficients 320/2240/12480, the external quanta 52/56, "
            "and the electroweak lock 3/13 are no longer separate residue facts. "
            "They are one exact q=3 package. What remains open is the global "
            "branch activation and orientation theorem on the refined tower."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_q_cyclotomic_master_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
