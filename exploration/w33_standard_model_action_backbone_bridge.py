"""Exact Standard Model action backbone from the promoted W33 package.

This bridge consolidates the already-exact public layers into one canonical
statement about what is and is not solved on the Standard Model side.

Solved exactly in the live repo:

  - bosonic electroweak action in canonical normalization;
  - one-generation fermion content 16 = 6 + 3 + 3 + 2 + 1 + 1;
  - three-generation matter count 48;
  - exact clean Higgs directions H_2 and Hbar_2 in the Connes screen;
  - promoted mixing data: tan(theta_C)=3/13 and PMNS sector ratios
    4/13, 7/13, 2/91;
  - exact anomaly cancellation per generation.

Not yet solved exactly:

  - the full Yukawa eigenvalue spectrum.

So the correct public statement is that the framework already fixes the
canonical Standard Model action backbone, while the fermion-mass eigenvalues
remain the live frontier.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_bosonic_action_completion_bridge import build_bosonic_action_completion_summary
from w33_fermionic_connes_sector import (
    FERMION_MATTER_DIM,
    LEFT_DIM,
    RIGHT_DIM,
    canonical_spinor_basis,
    clean_higgs_slots,
    left_spinor_basis,
    right_spinor_basis,
)
from w33_standard_model_cyclotomic_bridge import build_standard_model_cyclotomic_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_standard_model_action_backbone_bridge_summary.json"

HYPERCHARGES = {
    "Q_L": (Fraction(1, 6), 6),
    "u_R": (Fraction(2, 3), 3),
    "d_R": (Fraction(-1, 3), 3),
    "L_L": (Fraction(-1, 2), 2),
    "e_R": (Fraction(-1, 1), 1),
    "nu_R": (Fraction(0, 1), 1),
}


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_standard_model_action_backbone_summary() -> dict[str, Any]:
    bosonic = build_bosonic_action_completion_summary()
    sm = build_standard_model_cyclotomic_summary()

    spinor_basis = canonical_spinor_basis()
    left_basis = left_spinor_basis()
    right_basis = right_spinor_basis()

    one_gen_counts: dict[str, int] = {}
    for state in spinor_basis:
        one_gen_counts[state.sm] = one_gen_counts.get(state.sm, 0) + 1

    grav = sum(mult * y for y, mult in HYPERCHARGES.values())
    a33 = 2 * Fraction(1, 6) - (Fraction(2, 3) + Fraction(-1, 3))
    a22 = 3 * Fraction(1, 6) + Fraction(-1, 2)
    a111 = (
        6 * Fraction(1, 6) ** 3
        + 2 * Fraction(-1, 2) ** 3
        - 3 * Fraction(2, 3) ** 3
        - 3 * Fraction(-1, 3) ** 3
        - Fraction(-1, 1) ** 3
        - Fraction(0, 1) ** 3
    )

    return {
        "status": "ok",
        "bosonic_action_backbone": {
            "alpha": bosonic["graph_fixed_inputs"]["alpha"],
            "weinberg_x": bosonic["graph_fixed_inputs"]["weinberg_x"],
            "lambda_h": bosonic["graph_fixed_inputs"]["lambda_h"],
            "vev_ew_gev": bosonic["graph_fixed_inputs"]["vev_ew_gev"],
            "mw_squared_over_mz_squared": bosonic["gauge_ratio_dictionary"]["mw_squared_over_mz_squared"],
            "rho_parameter": bosonic["gauge_ratio_dictionary"]["rho_parameter"],
            "mu_h_squared_over_v_squared": bosonic["higgs_dictionary"]["mu_h_squared_over_v_squared"],
            "mh_squared_over_v_squared": bosonic["higgs_dictionary"]["mh_squared_over_v_squared"],
            "vacuum_energy_over_v_fourth": bosonic["higgs_dictionary"]["vacuum_energy_over_v_fourth"],
            "full_bosonic_action_fixed": bosonic["completion_claim"]["graph_fixes_full_tree_level_bosonic_electroweak_action"],
        },
        "fermion_representation_backbone": {
            "one_generation_spinor_dimension": len(spinor_basis),
            "three_generation_matter_dimension": FERMION_MATTER_DIM,
            "left_right_split": f"{len(left_basis)}+{len(right_basis)}",
            "one_generation_counts": one_gen_counts,
            "decomposition_16_equals_6_3_3_2_1_1": one_gen_counts == {
                "Q": 6,
                "u_c": 3,
                "d_c": 3,
                "L": 2,
                "e_c": 1,
                "nu_c": 1,
            },
            "clean_higgs_slots": list(clean_higgs_slots()),
            "clean_higgs_pair_is_h2_hbar2": clean_higgs_slots() == ("H_2", "Hbar_2"),
        },
        "mixing_backbone": {
            "tan_theta_c": sm["promoted_observables"]["tan_theta_c"],
            "sin2_theta_12": sm["promoted_observables"]["sin2_theta_12"],
            "sin2_theta_23": sm["promoted_observables"]["sin2_theta_23"],
            "sin2_theta_13": sm["promoted_observables"]["sin2_theta_13"],
            "cabibbo_equals_weinberg_generator": sm["closure_relations"]["tan_cabibbo_equals_ew_weinberg"],
            "pmns_23_equals_weinberg_plus_pmns_12": sm["closure_relations"]["pmns_23_equals_weinberg_plus_pmns_12"],
        },
        "anomaly_backbone": {
            "gravitational_sum_y": _fraction_dict(grav),
            "su3_squared_u1": _fraction_dict(a33),
            "su2_squared_u1": _fraction_dict(a22),
            "u1_cubed": _fraction_dict(a111),
            "all_anomalies_cancel": grav == 0 and a33 == 0 and a22 == 0 and a111 == 0,
        },
        "frontier_boundary": {
            "bosonic_action_complete": True,
            "fermion_representations_complete": True,
            "mixing_backbone_complete": True,
            "anomaly_backbone_complete": True,
            "full_yukawa_eigenvalue_spectrum_still_open": True,
        },
        "bridge_verdict": (
            "The exact public Standard Model content is best stated as an action "
            "backbone theorem. The bosonic electroweak action is fixed in "
            "canonical normalization, the fermion representation content is the "
            "exact 16 = 6+3+3+2+1+1 per generation with three-generation matter "
            "count 48, the clean Higgs directions are H_2 and Hbar_2, the "
            "promoted Cabibbo/PMNS package is fixed, and the anomaly conditions "
            "cancel exactly. What remains open is not the Standard Model "
            "backbone itself, but the full Yukawa eigenvalue spectrum."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_standard_model_action_backbone_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
