"""
Phase CDXLVIII — Gaussian integer spectral depth.

Verifies completeness of the ℤ[i] decomposition of the vertex propagator:
every eigenvalue = (k-1) × |z+i|², pole sum 139 = next prime after 137.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_gaussian_spectral_depth_bridge import (
    build_gaussian_spectral_depth_summary,
)


def test_phase_cdxlviii_gaussian_decomposition_complete() -> None:
    theorem = build_gaussian_spectral_depth_summary()[
        "gaussian_spectral_depth_theorem"
    ]
    assert theorem[
        "therefore_the_gaussian_spectral_decomposition_is_complete"
    ] is True


def test_phase_cdxlviii_every_eigenvalue_is_nb_times_norm() -> None:
    theorem = build_gaussian_spectral_depth_summary()[
        "gaussian_spectral_depth_theorem"
    ]
    assert theorem[
        "every_propagator_eigenvalue_is_nb_times_a_gaussian_norm"
    ] is True


def test_phase_cdxlviii_trace_gaussian_factorization() -> None:
    theorem = build_gaussian_spectral_depth_summary()[
        "gaussian_spectral_depth_theorem"
    ]
    assert theorem[
        "the_trace_factors_as_v_times_nb_times_gaussian_norm_of_mu_plus_i"
    ] is True


def test_phase_cdxlviii_pole_sum_139() -> None:
    theorem = build_gaussian_spectral_depth_summary()[
        "gaussian_spectral_depth_theorem"
    ]
    assert theorem[
        "the_pole_sum_139_is_the_next_prime_after_alpha_int_137"
    ] is True
