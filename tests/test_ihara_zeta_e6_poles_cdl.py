"""
Phase CDL — Ihara zeta E₆ pole count.

78 complex poles on the critical circle = dim(adj E₆).
Graph-theoretic Riemann hypothesis confirmed. Seidel energy = 240 = E.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_ihara_zeta_e6_poles_bridge import (
    build_ihara_zeta_e6_poles_summary,
)


def test_phase_cdl_ihara_encodes_e6_and_grh() -> None:
    theorem = build_ihara_zeta_e6_poles_summary()[
        "ihara_zeta_e6_poles_theorem"
    ]
    assert theorem[
        "therefore_the_ihara_zeta_encodes_E6_and_satisfies_grh"
    ] is True


def test_phase_cdl_78_poles_on_critical_circle() -> None:
    theorem = build_ihara_zeta_e6_poles_summary()[
        "ihara_zeta_e6_poles_theorem"
    ]
    assert theorem[
        "all_78_complex_poles_lie_on_the_critical_circle"
    ] is True


def test_phase_cdl_pole_count_equals_dim_e6() -> None:
    theorem = build_ihara_zeta_e6_poles_summary()[
        "ihara_zeta_e6_poles_theorem"
    ]
    assert theorem[
        "the_pole_count_78_equals_dim_adj_E6"
    ] is True


def test_phase_cdl_seidel_energy_240() -> None:
    theorem = build_ihara_zeta_e6_poles_summary()[
        "ihara_zeta_e6_poles_theorem"
    ]
    assert theorem[
        "the_seidel_energy_equals_the_edge_count_240"
    ] is True


def test_phase_cdl_discriminant_difference() -> None:
    theorem = build_ihara_zeta_e6_poles_summary()[
        "ihara_zeta_e6_poles_theorem"
    ]
    assert theorem[
        "the_discriminant_difference_equals_k"
    ] is True
