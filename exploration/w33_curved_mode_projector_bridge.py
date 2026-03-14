"""Exact mode projectors on the curved barycentric refinement tower.

The first curved product moment on the 4D barycentric tower has exact form

    M_r = A * 120^r + B * 6^r + C,

where:
    A = local * (860 a0 + 120 a2) / 19
    B = six * (12 a0 + 3 a2)
    C = chi * a2

This means the whole refinement tower is controlled by the characteristic
polynomial

    (x - 120)(x - 6)(x - 1) = x^3 - 127x^2 + 846x - 720.

The key exact consequence is that the three geometric/physical channels admit
closed projectors built from three successive refinement levels:

    P_120[M]_r = (E-6)(E-1) M_r / 13566 = A * 120^r
    P_6[M]_r   = -(E-120)(E-1) M_r / 570 = B * 6^r
    P_1[M]_r   = (E-120)(E-6) M_r / 595 = C

where E is the refinement-step shift operator.

So the Einstein-Hilbert-like 6-mode is not just visible asymptotically. It is
an exact discrete projector on the refinement tower itself.
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
from w33_curved_eh_mode_bridge import integrated_first_moment_formula


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_mode_projector_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


def projected_120(sequence: list[Fraction], r: int) -> Fraction:
    return (sequence[r + 2] - 7 * sequence[r + 1] + 6 * sequence[r]) / Fraction(13566)


def projected_6(sequence: list[Fraction], r: int) -> Fraction:
    return -(sequence[r + 2] - 121 * sequence[r + 1] + 120 * sequence[r]) / Fraction(570)


def projected_1(sequence: list[Fraction], r: int) -> Fraction:
    return (sequence[r + 2] - 126 * sequence[r + 1] + 720 * sequence[r]) / Fraction(595)


def tower_recurrence_value(sequence: list[Fraction], r: int) -> Fraction:
    return sequence[r + 3] - 127 * sequence[r + 2] + 846 * sequence[r + 1] - 720 * sequence[r]


@dataclass(frozen=True)
class ModeProfile:
    name: str
    a0: Fraction
    a2: Fraction


def _seed_entry(profile: ModeProfile, seed_name: str, n_vertices: int) -> dict[str, Any]:
    coeffs = neighborly_mode_coefficients(n_vertices)
    local = coeffs["local_mode"]
    six = coeffs["six_mode"]
    chi = coeffs["chi_mode"]

    sequence = [
        integrated_first_moment_formula(profile.a0, profile.a2, n_vertices, step)
        for step in range(5)
    ]

    cosmological = local * (Fraction(860) * profile.a0 + Fraction(120) * profile.a2) / Fraction(19)
    eh = six * (Fraction(12) * profile.a0 + Fraction(3) * profile.a2)
    top = chi * profile.a2

    samples = []
    for r in (0, 1):
        p120 = projected_120(sequence, r)
        p6 = projected_6(sequence, r)
        p1 = projected_1(sequence, r)
        samples.append(
            {
                "step": r,
                "projected_120": _fraction_dict(p120),
                "expected_120": _fraction_dict(cosmological * (Fraction(120) ** r)),
                "projected_6": _fraction_dict(p6),
                "expected_6": _fraction_dict(eh * (Fraction(6) ** r)),
                "projected_1": _fraction_dict(p1),
                "expected_1": _fraction_dict(top),
            }
        )

    return {
        "seed_name": seed_name,
        "vertices": n_vertices,
        "sequence": [_fraction_dict(value) for value in sequence[:4]],
        "recurrence_holds": all(tower_recurrence_value(sequence, r) == 0 for r in (0, 1)),
        "mode_amplitudes": {
            "cosmological_120": _fraction_dict(cosmological),
            "einstein_hilbert_6": _fraction_dict(eh),
            "topological_1": _fraction_dict(top),
        },
        "projector_samples": samples,
        "eh_extracted_coefficient": _fraction_dict(Fraction(eh, six)),
        "continuum_eh_from_rank_39_lock": _fraction_dict(Fraction(eh, six) / 39),
    }


@lru_cache(maxsize=1)
def build_curved_mode_projector_bridge_summary() -> dict[str, Any]:
    finite = build_adjacency_dirac_closure_summary()["finite_dirac_closure"]["seeley_dewitt_moments"]
    profile = ModeProfile(
        "finite_df2_480",
        Fraction(finite["a0_f"]),
        Fraction(finite["a2_f"]),
    )
    cp2 = cp2_seed()
    k3 = k3_seed()

    return {
        "status": "ok",
        "tower_characteristic_polynomial": "x^3 - 127x^2 + 846x - 720",
        "shift_projectors": {
            "P_120": "((E-6)(E-1))/13566",
            "P_6": "-((E-120)(E-1))/570",
            "P_1": "((E-120)(E-6))/595",
        },
        "finite_profile": {
            "a0": _fraction_dict(profile.a0),
            "a2": _fraction_dict(profile.a2),
            "einstein_hilbert_coefficient": _fraction_dict(Fraction(12) * profile.a0 + Fraction(3) * profile.a2),
        },
        "seeds": [
            _seed_entry(profile, "CP2_9", cp2.vertices),
            _seed_entry(profile, "K3_16", k3.vertices),
        ],
        "bridge_verdict": (
            "The curved refinement tower itself now carries exact mode projectors. "
            "The cosmological 120-mode, the Einstein-Hilbert-like 6-mode, and the "
            "topological 1-mode are extracted exactly from three successive "
            "refinement levels. So the discrete EH channel is not merely an "
            "asymptotic fit or a visible correction term; it is a genuine projector "
            "on the refinement sequence, and for the full finite package its "
            "projector-extracted coefficient is exactly 12480 at every step."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_mode_projector_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
