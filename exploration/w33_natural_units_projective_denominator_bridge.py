"""Natural-units projective denominator bridge for the promoted W33 package.

The natural-units bridges already prove three exact local facts:

    B B^T = 2I + J,                (Heawood/Fano selector)
    R_K G_0 = 2,                   (quantum metrology shell)
    L_K7 = 7I - J = Phi_6 I - J.   (toroidal/QCD shell)

So on the shared 7-packet, the selector coefficient is already the metrology
coefficient:

    2 = R_K G_0,
    B B^T + L_K7 = (R_K G_0 + Phi_6) I = q^2 I.

This gives a more physical decomposition of the projective denominator:

    Phi_3 = q^2 + q + 1
          = (R_K G_0 + Phi_6) + q + 1
          = 1 + q + R_K G_0 + Phi_6.

Hence the promoted electroweak data can be read as

    sin^2(theta_W) = q / (1 + q + R_K G_0 + Phi_6),
    cos^2(theta_W) = (1 + R_K G_0 + Phi_6) / (1 + q + R_K G_0 + Phi_6).

So the weak denominator 13 is not just projective arithmetic. In natural
units it already splits into selector line + projective share + metrology
shell + toroidal/QCD shell.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_natural_units_electroweak_split_bridge import (
    build_natural_units_electroweak_split_summary,
)
from w33_natural_units_topological_bridge import build_natural_units_topological_summary
from w33_quantum_vacuum_standards_bridge import build_quantum_vacuum_standards_summary
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_natural_units_projective_denominator_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_natural_units_projective_denominator_summary() -> dict[str, Any]:
    natural_topology = build_natural_units_topological_summary()
    natural_ew = build_natural_units_electroweak_split_summary()
    quantum = build_quantum_vacuum_standards_summary()
    standard_model = build_standard_model_cyclotomic_summary()

    selector_line = Fraction(1, 1)
    q = Fraction(natural_topology["local_shell_dictionary"]["q"])
    phi6 = Fraction(natural_topology["local_shell_dictionary"]["phi6"])
    q_squared = Fraction(natural_topology["local_shell_dictionary"]["q_squared"])
    rk_times_g0 = Fraction(quantum["exact_quantum_standards"]["rk_times_g0"]["exact"])
    theta_w33 = Fraction(natural_ew["nested_complement_dictionary"]["theta_w33"])
    phi3 = Fraction(standard_model["cyclotomic_data"]["phi3"])
    sin2 = Fraction(standard_model["promoted_observables"]["sin2_theta_w_ew"]["exact"])
    cos2 = Fraction(1, 1) - sin2

    denominator = selector_line + q + rk_times_g0 + phi6
    theta_from_shells = selector_line + rk_times_g0 + phi6

    return {
        "status": "ok",
        "metrology_shell_dictionary": {
            "fano_selector_formula": "B B^T = 2I + J",
            "metrology_selector_formula": "B B^T = (R_K G_0) I + J",
            "toroidal_shell_formula": "L_K7 = Phi_6 I - J",
            "local_sum_formula": "B B^T + L_K7 = (R_K G_0 + Phi_6) I = q^2 I",
            "q_from_selector_and_metrology_formula": "q = 1 + R_K G_0",
            "shared_six_formula": "6 = 1 + q + R_K G_0",
            "selector_line": int(selector_line),
            "q": int(q),
            "rk_times_g0": _fraction_dict(rk_times_g0),
            "phi6": int(phi6),
            "q_squared": int(q_squared),
        },
        "projective_denominator_dictionary": {
            "phi3_formula": "Phi_3 = 1 + q + R_K G_0 + Phi_6",
            "theta_formula": "Theta(W33) = 1 + R_K G_0 + Phi_6",
            "phi3": int(phi3),
            "theta_w33": int(theta_w33),
            "selector_plus_projective_plus_shells": _fraction_dict(denominator),
            "theta_from_selector_and_shells": _fraction_dict(theta_from_shells),
            "sin2_theta_w_formula": "sin^2(theta_W) = q / (1 + q + R_K G_0 + Phi_6)",
            "cos2_theta_w_formula": "cos^2(theta_W) = (1 + R_K G_0 + Phi_6) / (1 + q + R_K G_0 + Phi_6)",
            "sin2_theta_w": _fraction_dict(sin2),
            "cos2_theta_w": _fraction_dict(cos2),
            "q_over_projective_denominator": _fraction_dict(q / denominator),
            "theta_over_projective_denominator": _fraction_dict(theta_from_shells / denominator),
        },
        "exact_factorizations": {
            "selector_coefficient_equals_metrology_coefficient": rk_times_g0 == 2,
            "q_equals_selector_line_plus_metrology_shell": q == selector_line + rk_times_g0,
            "shared_six_equals_selector_plus_projective_plus_metrology_shell": 6 == selector_line + q + rk_times_g0,
            "metrology_plus_qcd_shell_equals_q_squared": rk_times_g0 + phi6 == q_squared,
            "phi3_equals_selector_plus_projective_plus_shells": phi3 == denominator,
            "theta_equals_selector_plus_shells": theta_w33 == theta_from_shells,
            "weinberg_equals_q_over_projective_denominator": sin2 == q / denominator,
            "cosine_equals_theta_over_projective_denominator": cos2 == theta_from_shells / denominator,
            "weinberg_plus_cosine_equals_unity": sin2 + cos2 == 1,
            "projective_denominator_rebuilds_from_natural_units_shells": (
                phi3 == selector_line + q + rk_times_g0 + phi6
            ),
        },
        "bridge_verdict": (
            "The projective denominator now has a natural-units decomposition. "
            "On the shared Heawood/Fano packet, the selector coefficient 2 is "
            "already the exact metrology coefficient R_K G_0, while the toroidal "
            "shell contributes Phi_6 = 7. Their sum is q^2 = 9, so "
            "Phi_3 = q^2 + q + 1 becomes Phi_3 = 1 + q + R_K G_0 + Phi_6 = 13. "
            "That means the weak denominator is already split into selector line, "
            "projective share, metrology shell, and toroidal/QCD shell. In this "
            "reading sin^2(theta_W) = 3/13 is the projective share of the full "
            "natural-units denominator, while cos^2(theta_W) = 10/13 is the "
            "remaining selector-plus-shell share."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_natural_units_projective_denominator_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
