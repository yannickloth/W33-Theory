"""
Phase CCCLXXXVIII — Continuum tail operator normal form.

CCCLXXXVII reduced the live continuum wall to existence of one nonzero tail
witness on the fixed avatar. This phase sharpens that again: the witness
criterion already forces one unique normalized tail operator profile, with
realized transport operator `217` times that normal form and the matter side an
exact `81`-fold lift.
"""

from __future__ import annotations

from exploration.w33_continuum_tail_operator_normal_form_bridge import (
    build_continuum_tail_operator_normal_form_summary,
)


def test_phase_ccclxxxviii_witness_criterion_forces_unique_operator_profile() -> None:
    theorem = build_continuum_tail_operator_normal_form_summary()[
        "continuum_tail_operator_normal_form_theorem"
    ]
    assert theorem[
        "the_one_witness_criterion_is_equivalent_to_realization_of_this_unique_operator_normal_form"
    ] is True


def test_phase_ccclxxxviii_live_wall_is_one_tail_operator_gauge_class() -> None:
    theorem = build_continuum_tail_operator_normal_form_summary()[
        "continuum_tail_operator_normal_form_theorem"
    ]
    assert theorem[
        "therefore_the_live_continuum_wall_is_existence_of_one_unique_nonzero_tail_operator_gauge_class"
    ] is True
