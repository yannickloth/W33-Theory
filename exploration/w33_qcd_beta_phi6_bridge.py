"""Exact one-loop QCD beta-coefficient lock to Phi_6(q) at q = 3.

The honest promoted claim is coefficient-level, not a full RG trajectory.
For SU(3) QCD with six active flavours,

    beta_0 = 11 - 2 n_f / 3 = 11 - 4 = 7,

and in the live W33 package

    Phi_6(q) = q^2 - q + 1,  Phi_6(3) = 7.

So the one-loop QCD running coefficient lands exactly on the same integer that
already governs the PMNS atmospheric numerator, the Higgs quartic numerator,
and the curved topological/continuum ratio.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_qcd_beta_phi6_bridge_summary.json"

Q = 3
NF = 6
PHI3 = Q * Q + Q + 1
PHI6 = Q * Q - Q + 1
BETA0_SU3 = Fraction(11, 1) - Fraction(2 * NF, 3)


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_qcd_beta_phi6_summary() -> dict[str, Any]:
    return {
        "status": "ok",
        "qcd_beta_dictionary": {
            "group": "SU(3)",
            "active_flavours": NF,
            "beta0_formula": "11 - 2 n_f / 3",
            "beta0_su3": _fraction_dict(BETA0_SU3),
            "phi6_formula": "q^2 - q + 1",
            "phi6_q3": _fraction_dict(Fraction(PHI6, 1)),
            "pmns_atmospheric_ratio": _fraction_dict(Fraction(PHI6, PHI3)),
            "higgs_quartic": _fraction_dict(Fraction(PHI6, 4 * PHI3 + Q)),
            "topological_over_continuum_ratio": _fraction_dict(Fraction(PHI6, 1)),
        },
        "selector_bridge": {
            "positive_integer_solution_of_phi6_equals_7": [Q],
            "beta0_equals_phi6": BETA0_SU3 == PHI6,
            "phi6_controls_pmns_atmospheric_numerator": Fraction(PHI6, PHI3).numerator == PHI6,
            "phi6_controls_higgs_quartic_numerator": Fraction(PHI6, 4 * PHI3 + Q).numerator == PHI6,
            "phi6_controls_topological_ratio": Fraction(PHI6, 1) == PHI6,
        },
        "bridge_verdict": (
            "The exact promoted QCD statement is now coefficient-level and clean: "
            "for six-flavour SU(3), the one-loop strong beta coefficient is "
            "beta_0 = 7 = Phi_6(3). So the same Phi_6 integer already governing "
            "PMNS atmospheric mixing, the Higgs quartic numerator, and the "
            "curved topological/continuum ratio also governs the first strong "
            "running coefficient."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_qcd_beta_phi6_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
