"""
Phase CCCXCII — Continuum tail primitive generator.

CCCXCI reduced exact transport realization to tail-line membership plus any one
promoted coordinate normalization. This phase sharpens that arithmetically: the
fixed tail line has one primitive integral generator, and the exact transport
operator is a single rational multiple of it.
"""

from __future__ import annotations

from exploration.w33_continuum_tail_primitive_generator_bridge import (
    build_continuum_tail_primitive_generator_summary,
)


def test_phase_cccxcii_primitive_generator_is_unique() -> None:
    theorem = build_continuum_tail_primitive_generator_summary()[
        "continuum_tail_primitive_generator_theorem"
    ]
    assert theorem[
        "the_exact_tail_line_has_a_unique_primitive_integral_generator_up_to_sign"
    ] is True


def test_phase_cccxcii_transport_scale_is_forced() -> None:
    theorem = build_continuum_tail_primitive_generator_summary()[
        "continuum_tail_primitive_generator_theorem"
    ]
    assert theorem[
        "the_exact_transport_operator_is_217_over_12_times_the_primitive_generator"
    ] is True
    assert theorem[
        "therefore_the_live_continuum_wall_is_now_a_fixed_primitive_tail_lattice_direction_plus_one_rational_scale"
    ] is True
