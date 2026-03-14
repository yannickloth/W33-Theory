"""Exact continuum extractor from three refinement samples.

The curved mode-projector and residue bridges isolate the 120-, 6-, and 1-mode
channels of the integrated first-moment refinement tower. This module pushes
that one step further:

for the full finite W33 package, the continuum Einstein-Hilbert coefficient is
recoverable exactly from any three successive refinement levels of the curved
tower.

If M_r denotes the integrated first moment on a fixed curved seed, then

    c_EH,disc
      = -(M_{r+2} - 121 M_{r+1} + 120 M_r) / (570 * six * 6^r)

is independent of r and equal to 12480, while

    c_EH,cont = c_EH,disc / 39 = 320.

Likewise,

    a2
      = (M_{r+2} - 126 M_{r+1} + 720 M_r) / (595 * chi)

and the cosmological 120-mode amplitude are extracted exactly from the same
three samples.

So the discrete refinement tower is not merely approaching the continuum EH
coefficient; it already contains an exact three-sample continuum extractor.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_adjacency_dirac_closure_bridge import build_adjacency_dirac_closure_summary
from w33_curved_barycentric_density_bridge import cp2_seed, k3_seed, neighborly_mode_coefficients
from w33_curved_eh_mode_bridge import integrated_first_moment_formula


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_continuum_extractor_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def _sequence(a0: Fraction, a2: Fraction, n_vertices: int, length: int = 5) -> list[Fraction]:
    return [integrated_first_moment_formula(a0, a2, n_vertices, r) for r in range(length)]


def extract_discrete_eh(sequence: list[Fraction], six: Fraction, step: int) -> Fraction:
    return -(sequence[step + 2] - 121 * sequence[step + 1] + 120 * sequence[step]) / (
        Fraction(570) * six * (Fraction(6) ** step)
    )


def extract_continuum_eh(sequence: list[Fraction], six: Fraction, step: int) -> Fraction:
    return extract_discrete_eh(sequence, six, step) / 39


def extract_topological(sequence: list[Fraction], chi: Fraction, step: int) -> Fraction:
    return (sequence[step + 2] - 126 * sequence[step + 1] + 720 * sequence[step]) / (
        Fraction(595) * chi
    )


def extract_cosmological_amplitude(sequence: list[Fraction], step: int) -> Fraction:
    return (sequence[step + 2] - 7 * sequence[step + 1] + 6 * sequence[step]) / (
        Fraction(13566) * (Fraction(120) ** step)
    )


@lru_cache(maxsize=1)
def build_curved_continuum_extractor_summary() -> dict[str, Any]:
    finite = build_adjacency_dirac_closure_summary()["finite_dirac_closure"]["seeley_dewitt_moments"]
    a0 = Fraction(finite["a0_f"])
    a2 = Fraction(finite["a2_f"])
    cp2 = cp2_seed()
    k3 = k3_seed()

    seeds = []
    for seed in (cp2, k3):
        coeffs = neighborly_mode_coefficients(seed.vertices)
        sequence = _sequence(a0, a2, seed.vertices)
        samples = []
        for step in (0, 1, 2):
            samples.append(
                {
                    "step": step,
                    "discrete_eh": _fraction_dict(extract_discrete_eh(sequence, coeffs["six_mode"], step)),
                    "continuum_eh": _fraction_dict(extract_continuum_eh(sequence, coeffs["six_mode"], step)),
                    "topological_a2": _fraction_dict(extract_topological(sequence, coeffs["chi_mode"], step)),
                    "cosmological_amplitude": _fraction_dict(extract_cosmological_amplitude(sequence, step)),
                }
            )
        seeds.append(
            {
                "seed_name": seed.name,
                "vertices": seed.vertices,
                "six_mode": _fraction_dict(coeffs["six_mode"]),
                "chi_mode": _fraction_dict(coeffs["chi_mode"]),
                "samples": samples,
            }
        )

    return {
        "status": "ok",
        "extractor_formulas": {
            "discrete_eh": "-(M_{r+2} - 121 M_{r+1} + 120 M_r) / (570 * six * 6^r)",
            "continuum_eh": "-(M_{r+2} - 121 M_{r+1} + 120 M_r) / (570 * six * 39 * 6^r)",
            "topological_a2": "(M_{r+2} - 126 M_{r+1} + 720 M_r) / (595 * chi)",
            "cosmological_amplitude": "(M_{r+2} - 7 M_{r+1} + 6 M_r) / (13566 * 120^r)",
        },
        "finite_profile": {
            "a0": _fraction_dict(a0),
            "a2": _fraction_dict(a2),
            "expected_discrete_eh": _fraction_dict(Fraction(12) * a0 + Fraction(3) * a2),
            "expected_continuum_eh": _fraction_dict((Fraction(12) * a0 + Fraction(3) * a2) / 39),
        },
        "seeds": seeds,
        "bridge_verdict": (
            "The curved refinement bridge now has an exact three-sample continuum "
            "extractor. From any three successive refinement levels of either "
            "CP2_9 or K3_16, the same formulas recover the discrete EH "
            "coefficient 12480, the continuum EH coefficient 320, and the "
            "topological coefficient a2 = 2240 exactly. So the continuum EH "
            "normalization is already a rigid invariant of the discrete "
            "refinement tower itself."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_continuum_extractor_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
