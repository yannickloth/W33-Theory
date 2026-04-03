"""
Phase CCCXC — Continuum tail syzygy criterion.

CCCLXXXIX reduced the live continuum wall to existence of one nonzero point on
one exact tail-operator line. This phase makes that line concrete on the fixed
avatar: three exact syzygies cut it out projectively, and once a nonzero point
exists the promoted witness normalization forces the exact realized operator.
"""

from __future__ import annotations

from exploration.w33_continuum_tail_syzygy_criterion_bridge import (
    build_continuum_tail_syzygy_criterion_summary,
)


def test_phase_cccxc_tail_line_is_cut_out_by_exact_syzygies() -> None:
    theorem = build_continuum_tail_syzygy_criterion_summary()[
        "continuum_tail_syzygy_criterion_theorem"
    ]
    assert theorem[
        "the_unique_tail_operator_line_is_cut_out_by_three_exact_avatar_internal_syzygies"
    ] is True


def test_phase_cccxc_live_wall_is_projective_line_membership_plus_normalization() -> None:
    theorem = build_continuum_tail_syzygy_criterion_summary()[
        "continuum_tail_syzygy_criterion_theorem"
    ]
    assert theorem[
        "therefore_the_live_continuum_wall_is_exact_projective_tail_line_membership_plus_forced_nonzero_normalization"
    ] is True
