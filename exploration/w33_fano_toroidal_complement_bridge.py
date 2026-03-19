"""Exact complement bridge between the Fano selector and toroidal K7 shell.

The torus/Fano route already carried two exact operators on the same 7-space:

    S_Fano = B B^T = 2I + J
    L_K7   = 7I - J

where ``B`` is the cyclic Fano incidence matrix and ``L_K7`` is the Laplacian
of the shared toroidal ``K7`` shell. Their sum is therefore forced exactly:

    S_Fano + L_K7 = 9I = q^2 I  (at q = 3).

Consequences:

- ``spec(S_Fano) = {9, 2^6}``;
- ``spec(L_K7) = {0, 7^6}``;
- the nontrivial Fano selector trace is ``6*2 = 12`` = Standard Model gauge dim;
- the nontrivial toroidal trace is ``6*7 = 42``;
- together they give ``12 + 42 = 54 = 40 + 6 + 8``;
- ``det(S_Fano) = 9 * 2^6 = 576 = 24^2``.

So the same 7-dimensional torus/Fano packet already splits the square
``q^2 = 9`` into a gauge-facing selector shell ``2`` and a toroidal/QCD shell
``7``, with the combined nontrivial weight recovering the exact promoted
exceptional gauge-package rank.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import sympy as sp

from w33_exceptional_operator_projector_bridge import (
    build_exceptional_operator_projector_summary,
)
from w33_heawood_harmonic_bridge import build_heawood_harmonic_summary
from w33_heawood_shell_ladder_bridge import build_heawood_shell_ladder_summary
from w33_surface_physics_shell_bridge import build_surface_physics_shell_summary
from w33_toroidal_k7_spectral_bridge import build_toroidal_k7_spectral_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_fano_toroidal_complement_bridge_summary.json"


def _spectral_strings(values: list[sp.Expr]) -> list[str]:
    return [str(sp.simplify(v)) for v in values]


@lru_cache(maxsize=1)
def build_fano_toroidal_complement_summary() -> dict[str, Any]:
    heawood = build_heawood_harmonic_summary()
    toroidal = build_toroidal_k7_spectral_summary()
    surface_physics = build_surface_physics_shell_summary()
    exceptional = build_exceptional_operator_projector_summary()
    shell = build_heawood_shell_ladder_summary()

    I7 = sp.eye(7)
    J7 = sp.ones(7)
    selector = 2 * I7 + J7
    toroidal_laplacian = 7 * I7 - J7
    complement = sp.simplify(selector + toroidal_laplacian)

    selector_eigs = [sp.Integer(2)] * 6 + [sp.Integer(9)]
    toroidal_eigs = [sp.Integer(0)] + [sp.Integer(7)] * 6

    selector_trace = int(sp.trace(selector))
    selector_nontrivial_trace = sum(int(v) for v in selector_eigs[:-1])
    toroidal_trace = int(sp.trace(toroidal_laplacian))
    combined_trace = selector_trace + toroidal_trace
    combined_nontrivial_trace = selector_nontrivial_trace + toroidal_trace
    selector_det = int(sp.det(selector))
    selector_det_sqrt = int(sp.sqrt(selector_det))
    exceptional_rank = int(
        exceptional["orthogonal_projectors"]["combined_gauge_package_rank"]
    )
    gauge_dimension = int(surface_physics["standard_model_gauge_dictionary"]["gauge_dimension"])
    ag21_length = int(shell["heawood_shell_dictionary"]["ag21_length"])
    q_squared = 9

    return {
        "status": "ok",
        "operator_dictionary": {
            "space_dimension": 7,
            "fano_selector_formula": "2I + J",
            "toroidal_laplacian_formula": "7I - J",
            "complement_formula": "9I",
            "q_squared": q_squared,
            "selector_spectrum_exact": _spectral_strings(selector_eigs),
            "toroidal_laplacian_spectrum_exact": [int(v) for v in toroidal_eigs],
            "selector_trace": selector_trace,
            "selector_nontrivial_trace": selector_nontrivial_trace,
            "toroidal_trace": toroidal_trace,
            "combined_trace": combined_trace,
            "combined_nontrivial_trace": combined_nontrivial_trace,
            "selector_determinant": selector_det,
            "selector_determinant_square_root": selector_det_sqrt,
            "selector_minimal_polynomial": "x^2 - 11x + 18",
        },
        "exact_factorizations": {
            "complement_operator_equals_q_squared_identity": complement == q_squared * I7,
            "selector_trace_equals_ag21_length": selector_trace == ag21_length,
            "selector_nontrivial_trace_equals_gauge_dimension": (
                selector_nontrivial_trace == gauge_dimension
            ),
            "toroidal_trace_equals_6_times_phi6": (
                toroidal_trace
                == toroidal["toroidal_k7_dictionary"]["shared_six_channel"]
                * toroidal["toroidal_k7_dictionary"]["phi6"]
            ),
            "combined_nontrivial_trace_equals_exceptional_projector_rank": (
                combined_nontrivial_trace == exceptional_rank
            ),
            "selector_determinant_square_root_equals_hurwitz_unit_shell": (
                selector_det_sqrt == shell["heawood_shell_dictionary"]["hurwitz_unit_order"]
            ),
            "selector_quadratic_matches_heawood_quartic_in_x_squared": (
                heawood["heawood_operator"]["adjacency_minimal_polynomial"]
                == "x^4 - 11*x^2 + 18"
            ),
            "gauge_plus_toroidal_equals_exceptional_rank": (
                gauge_dimension + toroidal_trace == exceptional_rank
            ),
        },
        "bridge_verdict": (
            "The torus/Fano route now has an exact complement law on one 7-dimensional "
            "packet. The Fano selector S = 2I + J and the toroidal K7 Laplacian "
            "L = 7I - J satisfy S + L = 9I = q^2 I. So the same q^2 = 9 shell "
            "splits exactly into a gauge-facing selector packet with nontrivial "
            "weight 12 and a toroidal/QCD packet with nontrivial weight 42. Their "
            "sum is 54, the full promoted exceptional gauge-package rank 40 + 6 + 8. "
            "At the same time det(S) = 576 = 24^2, so the selector operator already "
            "lands on the Hurwitz/D4 seed as well."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_fano_toroidal_complement_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
