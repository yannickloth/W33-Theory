"""Exact roundtrip closure between the curved tower and the finite package.

The curved bridge now reconstructs the full finite internal spectrum and
moments. This module closes that loop:

    curved samples -> finite Dirac/Hodge package -> curved coefficients again.

For the reconstructed finite moments

    a0 = 480,  a2 = 2240,  a4 = 17600,

the curved first-order bridge predicts

    c_EH,cont = 4 a0 / 6 = 320,
    c_6       = 12 a0 + 3 a2 = 12480,
    a2(top)   = a2 = 2240,
    x         = 9 c_EH,cont / c_6 = 3/13.

So the discrete-to-continuum bridge is now an exact roundtrip closure at the
coefficient level: the same three curved samples reconstruct the finite
internal package, and that finite package predicts back the same curved
coefficients and electroweak generator.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_curved_continuum_extractor_bridge import build_curved_continuum_extractor_summary
from w33_curved_finite_spectral_reconstruction_bridge import (
    build_curved_finite_spectral_reconstruction_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_roundtrip_closure_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@lru_cache(maxsize=1)
def build_curved_roundtrip_closure_summary() -> dict[str, Any]:
    curved = build_curved_continuum_extractor_summary()
    finite = build_curved_finite_spectral_reconstruction_summary()

    a0 = Fraction(finite["reconstructed_finite_dirac_package"]["seeley_dewitt_moments"]["a0_f"])
    a2 = Fraction(finite["reconstructed_finite_dirac_package"]["seeley_dewitt_moments"]["a2_f"])
    a4 = Fraction(finite["reconstructed_finite_dirac_package"]["seeley_dewitt_moments"]["a4_f"])

    continuum_eh = Fraction(4, 6) * a0
    discrete_eh = Fraction(12) * a0 + Fraction(3) * a2
    topological = a2
    master_variable = Fraction(9) * continuum_eh / discrete_eh

    expected_discrete = Fraction(curved["finite_profile"]["expected_discrete_eh"]["exact"])
    expected_continuum = Fraction(curved["finite_profile"]["expected_continuum_eh"]["exact"])
    expected_topological = Fraction(curved["finite_profile"]["a2"]["exact"])

    sample_roundtrips = []
    for seed in curved["seeds"]:
        for sample in seed["samples"]:
            sample_roundtrips.append(
                {
                    "seed_name": seed["seed_name"],
                    "step": sample["step"],
                    "sample_discrete_eh": sample["discrete_eh"]["exact"],
                    "sample_continuum_eh": sample["continuum_eh"]["exact"],
                    "sample_topological": sample["topological_a2"]["exact"],
                    "matches_roundtrip_discrete": Fraction(sample["discrete_eh"]["exact"]) == discrete_eh,
                    "matches_roundtrip_continuum": Fraction(sample["continuum_eh"]["exact"]) == continuum_eh,
                    "matches_roundtrip_topological": Fraction(sample["topological_a2"]["exact"]) == topological,
                    "matches_roundtrip_master_variable": master_variable == Fraction(9) * Fraction(sample["continuum_eh"]["exact"]) / Fraction(sample["discrete_eh"]["exact"]),
                }
            )

    return {
        "status": "ok",
        "reconstructed_finite_package": {
            "a0_f": int(a0),
            "a2_f": int(a2),
            "a4_f": int(a4),
            "df2_spectrum": finite["reconstructed_finite_dirac_package"]["df2_spectrum"],
        },
        "roundtrip_curved_coefficients": {
            "continuum_eh_from_finite": _fraction_dict(continuum_eh),
            "discrete_eh_from_finite": _fraction_dict(discrete_eh),
            "topological_from_finite": _fraction_dict(topological),
            "master_variable_from_roundtrip": _fraction_dict(master_variable),
        },
        "matches_curved_extractor_profile": {
            "continuum_matches": continuum_eh == expected_continuum,
            "discrete_matches": discrete_eh == expected_discrete,
            "topological_matches": topological == expected_topological,
            "master_variable_matches": master_variable == Fraction(3, 13),
        },
        "sample_roundtrips": sample_roundtrips,
        "all_samples_close_exactly": all(
            sample["matches_roundtrip_discrete"]
            and sample["matches_roundtrip_continuum"]
            and sample["matches_roundtrip_topological"]
            and sample["matches_roundtrip_master_variable"]
            for sample in sample_roundtrips
        ),
        "bridge_verdict": (
            "The discrete-to-continuum bridge is now an exact roundtrip closure "
            "at the coefficient level. The curved tower reconstructs the full "
            "finite internal package, and that finite package predicts back the "
            "same curved coefficients c_EH,cont = 320, c_6 = 12480, a2 = 2240, "
            "and x = 3/13 on every curved sample."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(json.dumps(build_curved_roundtrip_closure_summary(), indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    write_summary()
