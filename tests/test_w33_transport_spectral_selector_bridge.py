from __future__ import annotations

from fractions import Fraction

from exploration.w33_transport_spectral_selector_bridge import (
    build_transport_spectral_selector_summary,
)


def test_w33_base_selector_is_unique_trivial_line() -> None:
    summary = build_transport_spectral_selector_summary()
    base = summary["w33_base_selector"]

    assert base["projector_equals_j_over_40_exactly"] is True
    assert base["projector_idempotent"] is True
    assert base["projector_rank"] == 1
    assert base["rank_mod_3"] == 39
    assert base["kernel_dimension_mod_3"] == 1
    assert base["all_ones_spans_mod_3_kernel"] is True


def test_transport_selector_has_exact_srg_walk_data() -> None:
    summary = build_transport_spectral_selector_summary()
    selector = summary["transport_selector"]

    assert selector["projector_equals_j_over_45_exactly"] is True
    assert selector["projector_idempotent"] is True
    assert selector["projector_rank"] == 1
    assert selector["random_walk_eigenvalues"] == {"1": 1, "1/16": 24, "-1/8": 20}
    assert selector["max_nontrivial_abs_eigenvalue"]["exact"] == "1/8"
    assert selector["spectral_gap"]["exact"] == "7/8"
    assert selector["kemeny_constant"]["exact"] == "1952/45"
    assert selector["long_time_walk_limit_is_projector"] is True


def test_transport_heat_selection_matches_protected_matter_sector() -> None:
    summary = build_transport_spectral_selector_summary()
    dynamic = summary["dynamic_selection_bridge"]

    assert dynamic["invariant_line_h0_dimension"] == 1
    assert dynamic["constant_invariant_section_is_closed"] is True
    assert dynamic["a2_positive_laplacian_gap"] == 24
    assert dynamic["a2_standard_sector_has_no_zero_mode"] is True
    assert dynamic["logical_qutrits"] == 81
    assert dynamic["protected_flat_selector_rank_after_tensoring"] == 81
    assert dynamic["matches_protected_flat_matter_dimension"] is True
    assert dynamic["protected_flat_curved_harmonic_lifts"] == {
        "CP2_9": 243,
        "K3_16": 1944,
    }


def test_exact_fraction_data_is_consistent() -> None:
    summary = build_transport_spectral_selector_summary()
    selector = summary["transport_selector"]

    gap = Fraction(
        selector["spectral_gap"]["numerator"],
        selector["spectral_gap"]["denominator"],
    )
    kemeny = Fraction(
        selector["kemeny_constant"]["numerator"],
        selector["kemeny_constant"]["denominator"],
    )

    assert gap == Fraction(7, 8)
    assert kemeny == Fraction(1952, 45)
