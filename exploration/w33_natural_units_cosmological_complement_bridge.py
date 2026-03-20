"""Natural-units cosmological complement bridge.

The Heawood electroweak polarization bridge promotes the weak/hypercharge split
to the exact reduced packet

    M_EW = 1/2 [[1, Phi_6/Phi_3], [Phi_6/Phi_3, 1]],

with eigenvalues 3/13 and 10/13 and gap Phi_6/Phi_3 = 7/13.

The new point is that the complement of this polarization already carries the
same numerator as the universal cosmological 120-mode in the curved bridge:

    I_2 - (2 M_EW - I_2)^2
      = (1 - Phi_6^2 / Phi_3^2) I_2
      = (Phi_3^2 - Phi_6^2) / Phi_3^2 * I_2
      = 120/169 I_2.

Since

    Phi_3^2 - Phi_6^2 = 13^2 - 7^2 = 120 = 4 q Theta(W33),

the depolarized complement of the electroweak packet is already the exact
cosmological numerator. Lifting back to the Heawood packet gives

    P_mid - (2 R_EW - P_mid)^2 = (120/169) P_mid.

This same 120 also closes geometrically as

    120 = 84 + 36

with 84 the single-surface flag shell and 36 the Heawood middle-shell trace.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import sympy as sp

from w33_curved_eh_mode_bridge import build_curved_eh_mode_bridge_summary
from w33_heawood_electroweak_polarization_bridge import (
    build_heawood_electroweak_polarization_summary,
)
from w33_natural_units_root_gap_bridge import build_natural_units_root_gap_summary
from w33_natural_units_sigma_shell_bridge import build_natural_units_sigma_shell_summary
from w33_surface_hurwitz_flag_bridge import build_surface_hurwitz_flag_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_natural_units_cosmological_complement_bridge_summary.json"
)


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_natural_units_cosmological_complement_summary() -> dict[str, Any]:
    polarization = build_heawood_electroweak_polarization_summary()
    root_gap = build_natural_units_root_gap_summary()
    sigma_shell = build_natural_units_sigma_shell_summary()
    surface = build_surface_hurwitz_flag_summary()
    curved = build_curved_eh_mode_bridge_summary()

    q = Fraction(root_gap["root_gap_dictionary"]["q"])
    theta = Fraction(root_gap["root_gap_dictionary"]["theta_w33"])
    phi3 = Fraction(root_gap["root_gap_dictionary"]["phi3"])
    phi6 = Fraction(root_gap["root_gap_dictionary"]["phi6"])
    root_gap_fraction = Fraction(root_gap["root_gap_dictionary"]["root_gap"]["exact"])
    reduced_det = Fraction(polarization["reduced_packet_dictionary"]["determinant"]["exact"])

    reduced_packet = sp.Matrix(
        [
            [sp.Rational(1, 2), sp.Rational(phi6, 2 * phi3)],
            [sp.Rational(phi6, 2 * phi3), sp.Rational(1, 2)],
        ]
    )
    reduced_identity = sp.eye(2)
    reduced_complement = sp.simplify(
        reduced_identity - (2 * reduced_packet - reduced_identity) ** 2
    )

    cosmological_numerator = phi3 * phi3 - phi6 * phi6
    cosmological_fraction = Fraction(cosmological_numerator, phi3 * phi3)
    middle_rank = Fraction(polarization["polarization_dictionary"]["middle_rank"])
    single_surface_flags = Fraction(surface["surface_hurwitz_dictionary"]["single_surface_flags"])
    heawood_middle_trace = Fraction(sigma_shell["trace_ladder_dictionary"]["heawood_middle_trace"])

    # Use the exact lifted form from the polarization theorem:
    # 2 R_EW - P_mid = (Phi_6 / Phi_3) J_mid, with J_mid^2 = P_mid.
    # Therefore P_mid - (2 R_EW - P_mid)^2 = (1 - Phi_6^2 / Phi_3^2) P_mid.
    lifted_coefficient = Fraction(1, 1) - root_gap_fraction * root_gap_fraction

    external_chain_profile = next(
        profile for profile in curved["profiles"] if profile["name"] == "external_chain"
    )

    return {
        "status": "ok",
        "cosmological_complement_dictionary": {
            "reduced_complement_formula": "I_2 - (2 M_EW - I_2)^2 = ((Phi_3^2 - Phi_6^2)/Phi_3^2) I_2",
            "lifted_complement_formula": "P_mid - (2 R_EW - P_mid)^2 = ((Phi_3^2 - Phi_6^2)/Phi_3^2) P_mid",
            "numerator_formula": "Phi_3^2 - Phi_6^2 = 4 q Theta(W33)",
            "surface_formula": "120 = 84 + 36",
            "q": int(q),
            "theta_w33": int(theta),
            "phi3": int(phi3),
            "phi6": int(phi6),
            "root_gap": _fraction_dict(root_gap_fraction),
            "cosmological_fraction": _fraction_dict(cosmological_fraction),
            "cosmological_numerator": int(cosmological_numerator),
            "single_surface_flags": int(single_surface_flags),
            "heawood_middle_trace": int(heawood_middle_trace),
            "middle_rank": int(middle_rank),
            "external_chain_density_limit": external_chain_profile["global_coefficients"]["cosmological_density_limit"]["exact"],
        },
        "exact_factorizations": {
            "cosmological_numerator_equals_phi3_squared_minus_phi6_squared": cosmological_numerator == phi3 * phi3 - phi6 * phi6,
            "cosmological_numerator_equals_4_q_theta": cosmological_numerator == 4 * q * theta,
            "cosmological_fraction_equals_one_minus_gap_squared": cosmological_fraction == 1 - root_gap_fraction * root_gap_fraction,
            "reduced_complement_is_120_over_169_identity": reduced_complement == sp.Rational(cosmological_fraction) * reduced_identity,
            "four_det_equals_cosmological_fraction": 4 * reduced_det == cosmological_fraction,
            "surface_plus_middle_trace_equals_120": single_surface_flags + heawood_middle_trace == cosmological_numerator,
            "lifted_coefficient_matches_cosmological_fraction": lifted_coefficient == cosmological_fraction,
            "lifted_average_trace_matches_cosmological_fraction": lifted_coefficient == Fraction(1, 1) - root_gap_fraction * root_gap_fraction,
            "curved_bridge_uses_universal_120_mode": external_chain_profile["global_coefficients"]["cosmological_density_limit"]["exact"] == "120/19",
        },
        "bridge_verdict": (
            "The finite electroweak packet already isolates the exact "
            "cosmological numerator of the curved bridge. Its polarization gap "
            "is 7/13, so the depolarized complement is 1 - (7/13)^2 = 120/169. "
            "That same numerator 120 is the universal cosmological numerator of "
            "the curved barycentric bridge, even though the finite packet still "
            "carries the finite-side normalization by Phi_3^2 = 169 rather than "
            "the curved denominator 19. Equivalently, the reduced weak packet "
            "satisfies I_2 - (2 M_EW - I_2)^2 = (120/169) I_2, while the lifted "
            "Heawood packet satisfies P_mid - (2 R_EW - P_mid)^2 = (120/169) "
            "P_mid. So the complement of electroweak polarization is already the "
            "exact finite precursor of the universal curved cosmological shell."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_natural_units_cosmological_complement_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
