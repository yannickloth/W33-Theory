"""Exact cosmological / Einstein-Hilbert / topological mode split on the curved tower.

The curved 4D refinement program already established exact formulas for:

- external chain density per top simplex,
- external first Dirac-Kahler squared density per top simplex,
- the native A2 product bridge,
- the curved transport-Dirac bridge.

This module identifies the common exact law behind all of them.

For any internal package with first two moments

    a0 = Tr(1),   a2 = Tr(D_int^2),

the first product moment on the neighborly curved 4D barycentric tower splits
exactly into three barycentric eigenmodes:

    120-mode: cosmological/local term
     6-mode: Einstein-Hilbert-like curvature term
     1-mode: topological correction

More precisely, for every step r,

    density_r
      = ((860 a0 + 120 a2)/19)
        + ((12 a0 + 3 a2) * six/local) * 20^{-r}
        + (a2 * chi/local) * 120^{-r}.

Equivalently, at the integrated level,

    M_r
      = ((860 a0 + 120 a2)/19) * local * 120^r
        + (12 a0 + 3 a2) * six * 6^r
        + a2 * chi.

So the exact first-order bridge already has the full 4D mode hierarchy:
the cosmological term is the universal 120-mode, the Einstein-Hilbert-like
channel is exactly the 6-mode, and the residual topological term is exactly the
1-mode.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_adjacency_dirac_closure_bridge import build_adjacency_dirac_closure_summary
from w33_curved_barycentric_density_bridge import (
    barycentric_subdivision_f_vector,
    cp2_seed,
    k3_seed,
    neighborly_mode_coefficients,
    total_chain_dimension,
    trace_dirac_kahler_squared,
)
from w33_curved_a2_transport_product import a2_internal_profile
from w33_transport_curved_dirac_refinement_bridge import (
    build_transport_curved_dirac_refinement_summary,
    transport_curved_dirac_profile,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_curved_eh_mode_bridge_summary.json"


def _fraction_dict(value: Fraction) -> dict[str, Any]:
    exact = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"exact": exact, "float": float(value)}


@dataclass(frozen=True)
class InternalMomentProfile:
    name: str
    a0: Fraction
    a2: Fraction


def cosmological_density_coefficient(a0: Fraction, a2: Fraction) -> Fraction:
    return (Fraction(860) * a0 + Fraction(120) * a2) / Fraction(19)


def einstein_hilbert_mode_coefficient(a0: Fraction, a2: Fraction) -> Fraction:
    return Fraction(12) * a0 + Fraction(3) * a2


def topological_mode_coefficient(a2: Fraction) -> Fraction:
    return a2


def density_formula(
    a0: Fraction,
    a2: Fraction,
    n_vertices: int,
    step: int,
) -> Fraction:
    coeffs = neighborly_mode_coefficients(n_vertices)
    local = coeffs["local_mode"]
    six = coeffs["six_mode"]
    chi = coeffs["chi_mode"]
    return (
        cosmological_density_coefficient(a0, a2)
        + einstein_hilbert_mode_coefficient(a0, a2) * six / local / (Fraction(20) ** step)
        + topological_mode_coefficient(a2) * chi / local / (Fraction(120) ** step)
    )


def integrated_first_moment_formula(
    a0: Fraction,
    a2: Fraction,
    n_vertices: int,
    step: int,
) -> Fraction:
    coeffs = neighborly_mode_coefficients(n_vertices)
    local = coeffs["local_mode"]
    six = coeffs["six_mode"]
    chi = coeffs["chi_mode"]
    return (
        cosmological_density_coefficient(a0, a2) * local * (Fraction(120) ** step)
        + einstein_hilbert_mode_coefficient(a0, a2) * six * (Fraction(6) ** step)
        + topological_mode_coefficient(a2) * chi
    )


def direct_integrated_first_moment(a0: Fraction, a2: Fraction, n_vertices: int, step: int) -> Fraction:
    seed = cp2_seed() if n_vertices == cp2_seed().vertices else k3_seed()
    refined = barycentric_subdivision_f_vector(seed.f_vector, steps=step)
    chain_total = total_chain_dimension(refined)
    trace_total = trace_dirac_kahler_squared(refined)
    return a0 * Fraction(trace_total) + a2 * Fraction(chain_total)


def _seed_profile(profile: InternalMomentProfile, seed_name: str, n_vertices: int) -> dict[str, Any]:
    coeffs = neighborly_mode_coefficients(n_vertices)
    local = coeffs["local_mode"]
    six = coeffs["six_mode"]
    chi = coeffs["chi_mode"]
    return {
        "seed_name": seed_name,
        "vertices": n_vertices,
        "mode_data": {
            "local_mode": _fraction_dict(local),
            "six_mode": _fraction_dict(six),
            "chi_mode": _fraction_dict(chi),
        },
        "density_formula": {
            "cosmological_limit": _fraction_dict(cosmological_density_coefficient(profile.a0, profile.a2)),
            "einstein_hilbert_density_coefficient": _fraction_dict(
                einstein_hilbert_mode_coefficient(profile.a0, profile.a2) * six / local
            ),
            "topological_density_coefficient": _fraction_dict(
                topological_mode_coefficient(profile.a2) * chi / local
            ),
        },
        "integrated_mode_formula": {
            "cosmological_120_mode": _fraction_dict(cosmological_density_coefficient(profile.a0, profile.a2) * local),
            "einstein_hilbert_6_mode": _fraction_dict(
                einstein_hilbert_mode_coefficient(profile.a0, profile.a2) * six
            ),
            "topological_1_mode": _fraction_dict(topological_mode_coefficient(profile.a2) * chi),
        },
        "sign_matches_signature_for_curvature_mode": (
            (six > 0 and seed_name == "CP2_9") or (six < 0 and seed_name == "K3_16")
        ),
        "samples": [
            {
                "step": step,
                "density_formula": _fraction_dict(density_formula(profile.a0, profile.a2, n_vertices, step)),
                "integrated_formula": _fraction_dict(
                    integrated_first_moment_formula(profile.a0, profile.a2, n_vertices, step)
                ),
                "integrated_direct": _fraction_dict(
                    direct_integrated_first_moment(profile.a0, profile.a2, n_vertices, step)
                ),
            }
            for step in (0, 1, 2)
        ],
    }


@lru_cache(maxsize=1)
def build_curved_eh_mode_bridge_summary() -> dict[str, Any]:
    finite = build_adjacency_dirac_closure_summary()["finite_dirac_closure"]["seeley_dewitt_moments"]
    a2_profile = a2_internal_profile()
    transport_profile = transport_curved_dirac_profile()
    matter_transport = build_transport_curved_dirac_refinement_summary()["matter_coupled_curved_dirac"]

    profiles = [
        InternalMomentProfile("external_chain", Fraction(0), Fraction(1)),
        InternalMomentProfile("external_trace", Fraction(1), Fraction(0)),
        InternalMomentProfile("finite_df2_480", Fraction(finite["a0_f"]), Fraction(finite["a2_f"])),
        InternalMomentProfile("a2_transport", Fraction(a2_profile.total_dimension), Fraction(a2_profile.trace_laplacian)),
        InternalMomentProfile(
            "transport_curved_dirac",
            Fraction(transport_profile["total_dimension"]),
            Fraction(transport_profile["trace_d_squared"]),
        ),
        InternalMomentProfile(
            "matter_coupled_transport_curved_dirac",
            Fraction(matter_transport["total_dimension"]),
            Fraction(matter_transport["trace_d_squared"]),
        ),
    ]

    cp2 = cp2_seed()
    k3 = k3_seed()

    profile_entries = []
    for profile in profiles:
        profile_entries.append(
            {
                "name": profile.name,
                "a0": _fraction_dict(profile.a0),
                "a2": _fraction_dict(profile.a2),
                "global_coefficients": {
                    "cosmological_density_limit": _fraction_dict(cosmological_density_coefficient(profile.a0, profile.a2)),
                    "einstein_hilbert_6_mode_coefficient": _fraction_dict(
                        einstein_hilbert_mode_coefficient(profile.a0, profile.a2)
                    ),
                    "topological_1_mode_coefficient": _fraction_dict(topological_mode_coefficient(profile.a2)),
                },
                "seeds": [
                    _seed_profile(profile, "CP2_9", cp2.vertices),
                    _seed_profile(profile, "K3_16", k3.vertices),
                ],
            }
        )

    return {
        "status": "ok",
        "master_formula": {
            "density": "((860 a0 + 120 a2)/19) + ((12 a0 + 3 a2) * six/local) * 20^{-r} + (a2 * chi/local) * 120^{-r}",
            "integrated": "((860 a0 + 120 a2)/19) * local * 120^r + (12 a0 + 3 a2) * six * 6^r + a2 * chi",
            "mode_split": {
                "120_mode": "cosmological/local term",
                "6_mode": "Einstein-Hilbert-like curvature term",
                "1_mode": "topological correction",
            },
            "exact_scale_separation": "120 / 6 = 20",
        },
        "profiles": profile_entries,
        "bridge_verdict": (
            "The curved first-order bridge is now one exact master law. The "
            "external chain density, external first heat moment, the native A2 "
            "product bridge, the full finite 480-dimensional W33 package, and the "
            "transport-curved Dirac bridge are all special cases of the same "
            "three-mode barycentric convolution theorem. The universal 120-mode is "
            "the cosmological/local term, the exact 6-mode is the discrete "
            "Einstein-Hilbert channel, and the residual 1-mode is purely "
            "topological. So the real remaining 4D problem is no longer to guess "
            "where the Einstein-Hilbert piece lives. It already lives exactly in "
            "the barycentric 6-mode, and the open problem is to lift that exact "
            "discrete mode law to the genuine continuum spectral-action theorem."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_curved_eh_mode_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
