from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_qutrit_scaling_bridge import (  # noqa: E402
    build_continuum_qutrit_scaling_bridge_summary,
)


def test_all_residual_gap_ratios_are_exactly_81() -> None:
    summary = build_continuum_qutrit_scaling_bridge_summary()
    scaling = summary["residual_gap_scaling"]

    assert scaling["logical_qutrit_factor"] == 81
    assert scaling["first_order_constant_r20_ratio"]["exact"] == "81"
    assert scaling["first_order_linear_r20_ratio"]["exact"] == "81"
    assert scaling["quadratic_seed_gap_ratio"]["exact"] == "81"
    assert scaling["quadratic_sd1_gap_ratio"]["exact"] == "81"


def test_continuum_qutrit_scaling_theorem_is_exact() -> None:
    theorem = build_continuum_qutrit_scaling_bridge_summary()[
        "continuum_qutrit_scaling_theorem"
    ]

    assert theorem["first_order_local_constant_seed_gap_scales_by_exactly_81"] is True
    assert theorem["first_order_local_linear_seed_gap_scales_by_exactly_81"] is True
    assert theorem["quadratic_seed_gap_scales_by_exactly_81"] is True
    assert theorem["quadratic_sd1_gap_scales_by_exactly_81"] is True
    assert theorem[
        "therefore_the_matter_coupled_residual_seed_dependence_is_transport_tail_dependence_tensored_with_the_exact_logical_qutrit_packet"
    ] is True
