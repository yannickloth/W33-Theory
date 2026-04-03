"""
Phase CCCXCIII — Continuum tail reduced-fraction criterion.

CCCXCII fixed the primitive tail lattice direction. This phase fixes the exact
reduced fraction on that line: transport realization is `217/12` times the
primitive generator, and matter realization is its exact `81`-fold lift.
"""

from __future__ import annotations

from exploration.w33_continuum_tail_reduced_fraction_bridge import (
    build_continuum_tail_reduced_fraction_summary,
)


def test_phase_cccxciii_transport_fraction_is_forced() -> None:
    theorem = build_continuum_tail_reduced_fraction_summary()[
        "continuum_tail_reduced_fraction_theorem"
    ]
    assert theorem[
        "the_exact_transport_realization_has_reduced_fraction_scale_217_over_12"
    ] is True


def test_phase_cccxciii_matter_fraction_is_exact_lift() -> None:
    theorem = build_continuum_tail_reduced_fraction_summary()[
        "continuum_tail_reduced_fraction_theorem"
    ]
    assert theorem[
        "the_exact_matter_realization_has_reduced_fraction_scale_5859_over_4"
    ] is True
    assert theorem[
        "the_matter_reduced_fraction_is_the_exact_81_fold_lift_of_the_transport_scale"
    ] is True
