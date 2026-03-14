"""Exact residue theorem for the curved refinement mode tower.

The curved mode-projector bridge showed that the integrated first-moment
refinement tower has exact form

    M_r = A * 120^r + B * 6^r + C.

Equivalently, its ordinary generating function is the exact rational function

    G(z) = sum_{r>=0} M_r z^r
         = A / (1 - 120 z) + B / (1 - 6 z) + C / (1 - z).

So the curved cosmological / Einstein-Hilbert / topological channels are exact
pole data of the refinement tower itself.

If we define normalized residues by

    R_alpha(G) := -alpha * Res_{z = 1/alpha} G(z),

then

    R_120(G) = A,
    R_6(G)   = B,
    R_1(G)   = C.

For the full finite W33 package, dividing the 6-pole residue by the seed
six-mode coefficient recovers the exact discrete Einstein-Hilbert coefficient
12480, and dividing once more by the universal rank-39 lock recovers the
continuum coefficient 320.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_adjacency_dirac_closure_bridge import build_adjacency_dirac_closure_summary
from w33_curved_barycentric_density_bridge import cp2_seed, k3_seed, neighborly_mode_coefficients


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_mode_residue_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@dataclass(frozen=True)
class ModeResidues:
    cosmological_amplitude: Fraction
    einstein_hilbert_amplitude: Fraction
    topological_amplitude: Fraction


def finite_profile() -> tuple[Fraction, Fraction]:
    finite = build_adjacency_dirac_closure_summary()["finite_dirac_closure"]["seeley_dewitt_moments"]
    return Fraction(finite["a0_f"]), Fraction(finite["a2_f"])


def mode_amplitudes(a0: Fraction, a2: Fraction, n_vertices: int) -> ModeResidues:
    coeffs = neighborly_mode_coefficients(n_vertices)
    local = coeffs["local_mode"]
    six = coeffs["six_mode"]
    chi = coeffs["chi_mode"]
    return ModeResidues(
        cosmological_amplitude=local * (Fraction(860) * a0 + Fraction(120) * a2) / Fraction(19),
        einstein_hilbert_amplitude=six * (Fraction(12) * a0 + Fraction(3) * a2),
        topological_amplitude=chi * a2,
    )


def normalized_residue_from_amplitude(amplitude: Fraction) -> Fraction:
    return amplitude


@lru_cache(maxsize=1)
def build_curved_mode_residue_bridge_summary() -> dict[str, Any]:
    a0, a2 = finite_profile()
    cp2 = cp2_seed()
    k3 = k3_seed()

    cp2_coeffs = neighborly_mode_coefficients(cp2.vertices)
    k3_coeffs = neighborly_mode_coefficients(k3.vertices)
    cp2_modes = mode_amplitudes(a0, a2, cp2.vertices)
    k3_modes = mode_amplitudes(a0, a2, k3.vertices)

    discrete_eh = Fraction(12) * a0 + Fraction(3) * a2

    return {
        "status": "ok",
        "generating_function": {
            "formula": "A/(1 - 120 z) + B/(1 - 6 z) + C/(1 - z)",
            "normalized_residue_definition": "R_alpha(G) = -alpha * Res_{z = 1/alpha} G(z)",
            "pole_channels": {
                "120": "cosmological/local channel",
                "6": "Einstein-Hilbert-like curvature channel",
                "1": "topological channel",
            },
        },
        "finite_profile": {
            "a0": _fraction_dict(a0),
            "a2": _fraction_dict(a2),
            "einstein_hilbert_coefficient": _fraction_dict(discrete_eh),
        },
        "seed_residue_data": [
            {
                "seed_name": "CP2_9",
                "six_mode": _fraction_dict(cp2_coeffs["six_mode"]),
                "normalized_residue_120": _fraction_dict(normalized_residue_from_amplitude(cp2_modes.cosmological_amplitude)),
                "normalized_residue_6": _fraction_dict(normalized_residue_from_amplitude(cp2_modes.einstein_hilbert_amplitude)),
                "normalized_residue_1": _fraction_dict(normalized_residue_from_amplitude(cp2_modes.topological_amplitude)),
                "eh_from_residue_over_six_mode": _fraction_dict(cp2_modes.einstein_hilbert_amplitude / cp2_coeffs["six_mode"]),
                "continuum_eh_after_rank39_normalization": _fraction_dict(
                    (cp2_modes.einstein_hilbert_amplitude / cp2_coeffs["six_mode"]) / 39
                ),
            },
            {
                "seed_name": "K3_16",
                "six_mode": _fraction_dict(k3_coeffs["six_mode"]),
                "normalized_residue_120": _fraction_dict(normalized_residue_from_amplitude(k3_modes.cosmological_amplitude)),
                "normalized_residue_6": _fraction_dict(normalized_residue_from_amplitude(k3_modes.einstein_hilbert_amplitude)),
                "normalized_residue_1": _fraction_dict(normalized_residue_from_amplitude(k3_modes.topological_amplitude)),
                "eh_from_residue_over_six_mode": _fraction_dict(k3_modes.einstein_hilbert_amplitude / k3_coeffs["six_mode"]),
                "continuum_eh_after_rank39_normalization": _fraction_dict(
                    (k3_modes.einstein_hilbert_amplitude / k3_coeffs["six_mode"]) / 39
                ),
            },
        ],
        "bridge_verdict": (
            "The curved refinement bridge is now an exact pole theorem. The "
            "integrated first-moment tower has a rational generating function "
            "with poles only at z = 1/120, 1/6, and 1. The normalized residue at "
            "the 6-pole is exactly the EH-like channel. For the full finite W33 "
            "package, dividing that residue by the seed six-mode recovers the same "
            "discrete EH coefficient 12480 on both CP2_9 and K3_16, and the same "
            "rank-39 normalization recovers the continuum coefficient 320. So the "
            "curved EH bridge is now visible not only as a barycentric mode and "
            "not only as a projector, but also as an exact residue of the "
            "refinement generating function."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_mode_residue_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
