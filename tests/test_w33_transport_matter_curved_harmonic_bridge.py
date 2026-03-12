from __future__ import annotations

from w33_transport_matter_curved_harmonic_bridge import (
    build_transport_matter_curved_harmonic_summary,
)


def test_matter_coupled_precomplex_has_expected_dimensions_and_ranks() -> None:
    summary = build_transport_matter_curved_harmonic_summary()
    bridge = summary["matter_coupled_precomplex"]
    assert bridge["logical_qutrits"] == 81
    assert bridge["matter_extension_dimension"] == 162
    assert bridge["coupled_c0_dimension"] == 7290
    assert bridge["coupled_c1_dimension"] == 116640
    assert bridge["coupled_c2_dimension"] == 855360
    assert bridge["protected_flat_h0_dimension"] == 81
    assert bridge["protected_flat_h1_dimension"] == 0
    assert bridge["full_curvature_rank"] == 3402
    assert bridge["off_diagonal_curvature_rank"] == 2916
    assert bridge["semisimple_curvature_rank"] == 3402
    assert bridge["protected_flat_sector_is_exactly_one_81_copy"] is True
    assert bridge["curvature_hits_only_the_other_81_copy"] is True


def test_curved_external_harmonic_channels_are_exact() -> None:
    summary = build_transport_matter_curved_harmonic_summary()
    cp2, k3 = summary["curved_external_harmonic_channels"]

    assert cp2["external_name"] == "CP2"
    assert cp2["external_harmonic_form_total"] == 3
    assert cp2["protected_flat_matter_zero_modes"] == 243
    assert cp2["matter_curvature_rank_on_external_harmonics"] == 10206
    assert cp2["matter_off_diagonal_curvature_rank_on_external_harmonics"] == 8748
    assert cp2["matter_semisimple_curvature_rank_on_external_harmonics"] == 10206
    assert cp2["protected_flat_matter_matches_81_times_external_harmonics"] is True

    assert k3["external_name"] == "K3"
    assert k3["external_harmonic_form_total"] == 24
    assert k3["protected_flat_matter_zero_modes"] == 1944
    assert k3["matter_curvature_rank_on_external_harmonics"] == 81648
    assert k3["matter_off_diagonal_curvature_rank_on_external_harmonics"] == 69984
    assert k3["matter_semisimple_curvature_rank_on_external_harmonics"] == 81648
    assert k3["protected_flat_matter_matches_81_times_external_harmonics"] is True
