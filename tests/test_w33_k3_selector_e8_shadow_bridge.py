from __future__ import annotations

import pytest

from w33_k3_selector_e8_shadow_bridge import build_k3_selector_e8_shadow_bridge_summary


def test_k3_selector_e8_shadow_bridge_resolves_the_selector_over_named_factors() -> None:
    summary = build_k3_selector_e8_shadow_bridge_summary()
    theorem = summary["selector_e8_shadow_theorem"]

    assert summary["status"] == "ok"
    assert summary["reconstruction_error_linf"] < 1e-10
    assert theorem["selector_projection_on_three_u_is_positive_definite"] is True
    assert theorem["selector_projection_on_e8_factor_one_is_negative_definite"] is True
    assert theorem["selector_projection_on_e8_factor_two_is_negative_definite"] is True
    assert theorem["selector_projection_on_e8_factor_one_is_nonzero"] is True
    assert theorem["selector_projection_on_e8_factor_two_is_nonzero"] is True
    assert theorem["e8_factor_projections_are_exactly_orthogonal"] is True
    assert theorem["selector_decomposes_orthogonally_across_three_u_and_both_e8_factors"] is True
    assert theorem["selector_is_not_supported_on_three_u_alone"] is True
    assert theorem["selector_is_not_supported_on_single_e8_factor"] is True
    assert theorem["selector_bridges_three_u_and_both_e8_factors"] is True


def test_k3_selector_e8_shadow_bridge_records_expected_forms() -> None:
    summary = build_k3_selector_e8_shadow_bridge_summary()

    assert summary["three_u_component_form"] == pytest.approx(
        [
            [2.8024851868998474, 0.42573374396135524],
            [0.4257337439613557, 0.2518300164126374],
        ]
    )
    assert summary["e8_factor_one_component_form"] == pytest.approx(
        [
            [-0.2369081557707725, 0.06887889155688198],
            [0.06887889155688342, -0.1479147677425762],
        ]
    )
    assert summary["e8_factor_two_component_form"] == pytest.approx(
        [
            [-2.395055948174911, -0.49461263551823957],
            [-0.49461263551823807, -0.23012717536646647],
        ]
    )
