from __future__ import annotations

from math import isclose

from w33_k3_selector_three_u_shadow_bridge import (
    build_k3_selector_three_u_shadow_bridge_summary,
)


def test_k3_selector_three_u_shadow_bridge_splits_selector_between_core_and_complement() -> None:
    summary = build_k3_selector_three_u_shadow_bridge_summary()
    assert summary["status"] == "ok"

    theorem = summary["selector_three_u_shadow_theorem"]
    assert theorem["selector_plane_is_mixed_signature"] is True
    assert theorem["selector_plane_shadow_on_three_u_is_positive_definite"] is True
    assert theorem["selector_plane_residual_on_rank16_complement_is_negative_definite"] is True
    assert theorem["selector_plane_is_not_contained_in_three_u_core"] is True
    assert theorem["selector_plane_is_not_contained_in_rank16_negative_complement"] is True
    assert theorem["selector_plane_straddles_both_k3_lattice_pieces"] is True
    assert theorem["selector_plane_has_no_numerical_line_of_intersection_with_three_u_core"] is True


def test_k3_selector_three_u_shadow_bridge_records_expected_shadow_forms() -> None:
    summary = build_k3_selector_three_u_shadow_bridge_summary()

    selector_form = summary["selector_plane_form"]
    shadow_form = summary["three_u_shadow_form"]
    residual_form = summary["rank16_residual_form"]
    principal_cosines = summary["principal_cosines_against_three_u_core"]

    assert isclose(selector_form[0][0], 0.1705210828229612, rel_tol=0.0, abs_tol=1e-12)
    assert isclose(selector_form[0][1], 0.0, rel_tol=0.0, abs_tol=1e-10)
    assert isclose(selector_form[1][1], -0.1262119267461511, rel_tol=0.0, abs_tol=1e-12)

    assert isclose(shadow_form[0][0], 2.8024851868813414, rel_tol=0.0, abs_tol=1e-12)
    assert isclose(shadow_form[0][1], 0.42573374061191585, rel_tol=0.0, abs_tol=1e-8)
    assert isclose(shadow_form[1][1], 0.2518300163799658, rel_tol=0.0, abs_tol=1e-12)

    assert isclose(residual_form[0][0], -2.6319641040583726, rel_tol=0.0, abs_tol=1e-12)
    assert isclose(residual_form[0][1], -0.4257337406119194, rel_tol=0.0, abs_tol=1e-8)
    assert isclose(residual_form[1][1], -0.37804194312612105, rel_tol=0.0, abs_tol=1e-12)

    assert isclose(principal_cosines[0], 0.6939852722886527, rel_tol=0.0, abs_tol=1e-8)
    assert isclose(principal_cosines[1], 0.4318086483648292, rel_tol=0.0, abs_tol=1e-8)
