from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_tail_syzygy_criterion_bridge import (  # noqa: E402
    build_continuum_tail_syzygy_criterion_summary,
)


def test_transport_and_matter_syzygies_vanish_exactly() -> None:
    summary = build_continuum_tail_syzygy_criterion_summary()
    syzygies = summary["tail_line_syzygies"]

    assert syzygies["equations"] == [
        "662*C - 65*L = 0",
        "15650*C - 195*Q_seed = 0",
        "17993*C - 260*Q_sd1 = 0",
    ]
    assert syzygies["transport_operator_syzygies"] == {
        "662C_minus_65L": "0",
        "15650C_minus_195Qseed": "0",
        "17993C_minus_260Qsd1": "0",
    }
    assert syzygies["matter_operator_syzygies"] == {
        "662C_minus_65L": "0",
        "15650C_minus_195Qseed": "0",
        "17993C_minus_260Qsd1": "0",
    }


def test_tail_syzygy_criterion_theorem_is_exact() -> None:
    theorem = build_continuum_tail_syzygy_criterion_summary()[
        "continuum_tail_syzygy_criterion_theorem"
    ]
    assert theorem[
        "the_unique_tail_operator_line_is_cut_out_by_three_exact_avatar_internal_syzygies"
    ] is True
    assert theorem["the_promoted_transport_operator_satisfies_all_syzygies_exactly"] is True
    assert theorem[
        "the_exact_81_fold_matter_lift_satisfies_the_same_projective_syzygies"
    ] is True
    assert theorem[
        "any_candidate_tail_operator_fails_projective_realizability_if_any_syzygy_is_nonzero"
    ] is True
    assert theorem[
        "combined_with_the_promoted_nonzero_witness_criterion_this_forces_the_exact_realized_operator"
    ] is True
    assert theorem[
        "therefore_the_live_continuum_wall_is_exact_projective_tail_line_membership_plus_forced_nonzero_normalization"
    ] is True
