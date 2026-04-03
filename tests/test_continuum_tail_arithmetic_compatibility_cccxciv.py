"""
Phase CCCXCIV — Continuum tail arithmetic compatibility.

CCCXCIII fixed the exact reduced fraction on the primitive tail line. This
phase re-expresses that exact realization directly in terms of external
coordinate arithmetic: denominator-lcm and cleared-coordinate gcd.
"""

from __future__ import annotations

from exploration.w33_continuum_tail_arithmetic_compatibility_bridge import (
    build_continuum_tail_arithmetic_compatibility_summary,
)


def test_phase_cccxciv_transport_pair_is_forced() -> None:
    theorem = build_continuum_tail_arithmetic_compatibility_summary()[
        "continuum_tail_arithmetic_compatibility_theorem"
    ]
    assert theorem[
        "the_exact_transport_realization_has_compatibility_pair_lcm12_gcd217"
    ] is True


def test_phase_cccxciv_matter_pair_is_exact_lift() -> None:
    theorem = build_continuum_tail_arithmetic_compatibility_summary()[
        "continuum_tail_arithmetic_compatibility_theorem"
    ]
    assert theorem[
        "the_exact_matter_realization_has_compatibility_pair_lcm4_gcd5859"
    ] is True
    assert theorem[
        "the_matter_compatibility_pair_is_the_exact_81_fold_lift_of_the_transport_pair"
    ] is True
