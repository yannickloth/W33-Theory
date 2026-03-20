"""Natural-units neutral-current shell bridge for the promoted W33 package.

The natural-units electroweak split already fixes the neutral-current share as

    (4 pi alpha) / g_Z^2 = q Theta(W33) / Phi_3^2 = 30/169.

The new point is that the same numerator ``30`` already has an exact shell
interpretation on the torus/Heawood side:

    q Theta(W33) = q(1 + R_K G_0 + Phi_6)
                 = q + q(R_K G_0) + q Phi_6
                 = 3 + 6 + 21.

Here

    6  = sigma               (the nontrivial toroidal mode count),
    21 = AG(2,1)            (the Heawood/Fano edge packet).

So the neutral-current numerator is already the exact sum

    30 = 3 + 6 + 21.

More sharply, the single toroidal flag shell splits as

    84 = 54 + 30,

where

    54 = sigma q^2 = 6 * 9

is the promoted internal gauge-package shell, while ``30`` is the exact
neutral-current shell.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path

from w33_fano_toroidal_complement_bridge import build_fano_toroidal_complement_summary
from w33_heawood_shell_ladder_bridge import build_heawood_shell_ladder_summary
from w33_natural_units_electroweak_split_bridge import (
    build_natural_units_electroweak_split_summary,
)
from w33_natural_units_projective_denominator_bridge import (
    build_natural_units_projective_denominator_summary,
)
from w33_natural_units_sigma_shell_bridge import build_natural_units_sigma_shell_summary
from w33_surface_hurwitz_flag_bridge import build_surface_hurwitz_flag_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_natural_units_neutral_shell_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, object]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_natural_units_neutral_shell_summary() -> dict[str, object]:
    ew = build_natural_units_electroweak_split_summary()
    projective = build_natural_units_projective_denominator_summary()
    sigma_shell = build_natural_units_sigma_shell_summary()
    heawood_shell = build_heawood_shell_ladder_summary()
    complement = build_fano_toroidal_complement_summary()
    surface = build_surface_hurwitz_flag_summary()

    q = int(ew["nested_complement_dictionary"]["q"])
    theta = int(ew["nested_complement_dictionary"]["theta_w33"])
    phi3 = int(ew["nested_complement_dictionary"]["phi3"])
    rk_times_g0 = int(projective["metrology_shell_dictionary"]["rk_times_g0"]["exact"])
    phi6 = int(projective["metrology_shell_dictionary"]["phi6"])
    sigma = int(sigma_shell["sigma_shell_dictionary"]["sigma"])
    q_squared = int(projective["metrology_shell_dictionary"]["q_squared"])
    ag21 = int(heawood_shell["heawood_shell_dictionary"]["ag21_length"])
    neutral_numerator = q * theta
    neutral_reciprocal = Fraction(neutral_numerator, phi3 * phi3)
    complement_trace = int(complement["operator_dictionary"]["combined_nontrivial_trace"])
    single_surface_flags = int(surface["surface_hurwitz_dictionary"]["single_surface_flags"])

    return {
        "status": "ok",
        "neutral_shell_dictionary": {
            "neutral_numerator_formula": "q Theta(W33)",
            "neutral_reciprocal_formula": "(4 pi alpha) / g_Z^2 = q Theta(W33) / Phi_3^2",
            "q": q,
            "theta_w33": theta,
            "phi3": phi3,
            "sigma": sigma,
            "q_squared": q_squared,
            "rk_times_g0": rk_times_g0,
            "phi6": phi6,
            "ag21_length": ag21,
            "neutral_numerator": neutral_numerator,
            "neutral_reciprocal": _fraction_dict(neutral_reciprocal),
            "single_surface_flags": single_surface_flags,
            "complement_trace": complement_trace,
        },
        "exact_factorizations": {
            "neutral_numerator_equals_q_times_theta": neutral_numerator == q * theta,
            "neutral_reciprocal_equals_q_theta_over_phi3_squared": (
                neutral_reciprocal == Fraction(q * theta, phi3 * phi3)
            ),
            "q_times_rk_times_g0_equals_sigma": q * rk_times_g0 == sigma,
            "q_times_phi6_equals_ag21": q * phi6 == ag21,
            "neutral_numerator_equals_q_plus_sigma_plus_ag21": (
                neutral_numerator == q + sigma + ag21
            ),
            "complement_trace_equals_sigma_times_q_squared": (
                complement_trace == sigma * q_squared
            ),
            "surface_flags_equals_complement_trace_plus_neutral_numerator": (
                single_surface_flags == complement_trace + neutral_numerator
            ),
        },
        "bridge_verdict": (
            "The neutral-current packet is now a torus-side shell law rather than "
            "just a coupling fraction. Its exact numerator is q Theta(W33) = 30, "
            "so (4 pi alpha)/g_Z^2 = 30/169. The same 30 already decomposes as "
            "3 + 6 + 21 = q + sigma + AG(2,1), tying the neutral-current shell to "
            "the projective share, the nontrivial toroidal mode count, and the "
            "Heawood/Fano edge packet. More sharply, the single toroidal flag shell "
            "splits exactly as 84 = 54 + 30, where 54 is the promoted internal "
            "gauge-package shell and 30 is the neutral-current shell."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_natural_units_neutral_shell_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
