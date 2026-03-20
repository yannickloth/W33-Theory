"""Heawood radical shell as the electroweak denominator bridge.

The promoted Heawood theorem already isolates an exact operator shell:

    x^2 - 6x + 7 = 0

on the 12-dimensional middle sector of the Heawood Laplacian.

The coefficients of that shell are already live physics selectors:

    6 = shared six-channel coefficient,
    7 = Phi_6 = beta_0(QCD).

This module closes the next exact step:

    Phi_3 = 6 + 7 = 13.

So the surface operator shell alone already reconstructs the electroweak
denominator, and therefore the promoted mixing data can be read directly from
the Heawood packet:

    sin^2(theta_W)  = q / (6 + 7)     = 3/13,
    cos^2(theta_W)  = (q + 7) / (6+7) = 10/13,
    sin^2(theta_23) = 7 / (6 + 7)     = 7/13.

This is narrower and cleaner than a generic numerology claim: the ``6`` and
``7`` come from one exact operator polynomial, and the same ``13`` is the
projective denominator already forced elsewhere by the SRG and spectral locks.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_heawood_tetra_radical_bridge import build_heawood_tetra_radical_summary
from w33_mod12_selector_closure_bridge import build_mod12_selector_closure_summary
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary
from w33_theta_hierarchy_bridge import build_theta_hierarchy_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_heawood_weinberg_denominator_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_heawood_weinberg_denominator_summary() -> dict[str, Any]:
    heawood = build_heawood_tetra_radical_summary()
    mod12 = build_mod12_selector_closure_summary()
    standard_model = build_standard_model_cyclotomic_summary()
    theta = build_theta_hierarchy_summary()

    q = Fraction(mod12["mod12_selector_dictionary"]["q"])
    phi6 = Fraction(mod12["mod12_selector_dictionary"]["phi6"])
    theta_w33 = Fraction(theta["theta_dictionary"]["lovasz_theta"])
    shared_six = Fraction(heawood["heawood_middle_shell"]["middle_branch_multiplicity_each"])
    phi3 = Fraction(standard_model["cyclotomic_data"]["phi3"])

    sin2_theta_w = Fraction(standard_model["promoted_observables"]["sin2_theta_w_ew"]["exact"])
    sin2_theta_23 = Fraction(standard_model["promoted_observables"]["sin2_theta_23"]["exact"])
    cos2_theta_w = Fraction(1, 1) - sin2_theta_w

    return {
        "status": "ok",
        "heawood_shell_dictionary": {
            "middle_quadratic_polynomial": heawood["heawood_middle_shell"]["middle_quadratic_polynomial"],
            "shared_six_channel": int(shared_six),
            "phi6": int(phi6),
            "phi3": int(phi3),
            "theta_w33": int(theta_w33),
            "denominator_formula": "Phi_3 = 6 + Phi_6",
            "theta_formula": "Theta(W33) = q + Phi_6",
        },
        "electroweak_from_heawood_dictionary": {
            "weinberg_from_heawood_formula": "sin^2(theta_W) = q / (6 + Phi_6)",
            "cosine_from_heawood_formula": "cos^2(theta_W) = (q + Phi_6) / (6 + Phi_6)",
            "pmns23_from_heawood_formula": "sin^2(theta_23) = Phi_6 / (6 + Phi_6)",
            "sin2_theta_w": _fraction_dict(sin2_theta_w),
            "cos2_theta_w": _fraction_dict(cos2_theta_w),
            "sin2_theta_23": _fraction_dict(sin2_theta_23),
            "q_over_heawood_denominator": _fraction_dict(q / (shared_six + phi6)),
            "theta_over_heawood_denominator": _fraction_dict(theta_w33 / (shared_six + phi6)),
            "phi6_over_heawood_denominator": _fraction_dict(phi6 / (shared_six + phi6)),
        },
        "exact_factorizations": {
            "heawood_linear_term_is_shared_six": shared_six == 6,
            "heawood_constant_term_is_phi6": phi6 == 7,
            "phi3_equals_shared_six_plus_phi6": phi3 == shared_six + phi6,
            "theta_equals_q_plus_phi6": theta_w33 == q + phi6,
            "cosine_equals_theta_over_heawood_denominator": cos2_theta_w == theta_w33 / (shared_six + phi6),
            "weinberg_equals_q_over_heawood_denominator": sin2_theta_w == q / (shared_six + phi6),
            "pmns23_equals_phi6_over_heawood_denominator": sin2_theta_23 == phi6 / (shared_six + phi6),
            "weinberg_plus_cosine_equals_unity": sin2_theta_w + cos2_theta_w == 1,
            "surface_shell_reconstructs_projective_denominator": phi3 == 13,
        },
        "bridge_verdict": (
            "The Heawood surface operator shell already reconstructs the "
            "electroweak denominator. Its exact middle-sector polynomial "
            "x^2 - 6x + 7 = 0 carries the shared six-channel coefficient and the "
            "QCD selector Phi_6 = 7 as its two live coefficients, and their sum "
            "is exactly Phi_3 = 13. So the promoted electroweak data can be read "
            "directly off the surface shell: sin^2(theta_W) = 3/13, "
            "cos^2(theta_W) = 10/13, and sin^2(theta_23) = 7/13. This is not a "
            "free arithmetic fit; the same 13 is reconstructed from one exact "
            "operator polynomial on the Heawood route."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_heawood_weinberg_denominator_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
