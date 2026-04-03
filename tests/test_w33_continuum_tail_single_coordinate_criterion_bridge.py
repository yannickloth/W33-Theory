from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_tail_single_coordinate_criterion_bridge import (  # noqa: E402
    build_continuum_tail_single_coordinate_criterion_summary,
)


def test_any_one_transport_coordinate_reconstructs_the_rest() -> None:
    summary = build_continuum_tail_single_coordinate_criterion_summary()
    coords = summary["tail_coordinate_normalizations"]

    assert coords["transport_coordinates"] == {
        "C": "14105",
        "L": "143654",
        "Q_seed": "3396050/3",
        "Q_sd1": "3904481/4",
    }
    assert coords["transport_reconstruction_from_C"] == {
        "L": "143654",
        "Q_seed": "3396050/3",
        "Q_sd1": "3904481/4",
    }
    assert coords["transport_reconstruction_from_L"] == {
        "C": "14105",
        "Q_seed": "3396050/3",
        "Q_sd1": "3904481/4",
    }
    assert coords["transport_reconstruction_from_Q_seed"] == {
        "C": "14105",
        "L": "143654",
        "Q_sd1": "3904481/4",
    }
    assert coords["transport_reconstruction_from_Q_sd1"] == {
        "C": "14105",
        "L": "143654",
        "Q_seed": "3396050/3",
    }


def test_single_coordinate_criterion_theorem_is_exact() -> None:
    theorem = build_continuum_tail_single_coordinate_criterion_summary()[
        "continuum_tail_single_coordinate_criterion_theorem"
    ]
    assert theorem[
        "on_the_exact_tail_line_C_equal_14105_forces_the_full_transport_operator"
    ] is True
    assert theorem[
        "on_the_exact_tail_line_L_equal_143654_forces_the_full_transport_operator"
    ] is True
    assert theorem[
        "on_the_exact_tail_line_Qseed_equal_3396050_over_3_forces_the_full_transport_operator"
    ] is True
    assert theorem[
        "on_the_exact_tail_line_Qsd1_equal_3904481_over_4_forces_the_full_transport_operator"
    ] is True
    assert theorem[
        "therefore_any_one_promoted_coordinate_normalization_plus_syzygies_is_necessary_and_sufficient_for_exact_transport_realization"
    ] is True
    assert theorem["the_exact_matter_operator_then_follows_by_the_81_fold_lift"] is True
