from __future__ import annotations

from w33_k3_three_u_complement_refinement_bridge import (
    build_k3_three_u_complement_refinement_bridge_summary,
)


def test_k3_three_u_complement_refinement_bridge_locks_the_full_split() -> None:
    summary = build_k3_three_u_complement_refinement_bridge_summary()
    theorem = summary["three_u_complement_refinement_theorem"]

    assert summary["status"] == "ok"
    assert theorem["complement_basis_has_shape_22_by_16"] is True
    assert theorem["three_u_and_complement_are_exactly_orthogonal"] is True
    assert theorem["complement_has_signature_0_16"] is True
    assert theorem["complement_form_scales_by_120"] is True
    assert theorem["normalized_complement_form_is_refinement_invariant"] is True
    assert theorem["full_split_form_scales_by_120"] is True
    assert theorem["full_split_cross_terms_remain_zero"] is True
    assert theorem["full_split_signature_survives_first_refinement"] is True
    assert theorem["explicit_k3_lattice_split_is_first_refinement_rigid"] is True


def test_k3_three_u_complement_refinement_bridge_records_expected_seed_data() -> None:
    summary = build_k3_three_u_complement_refinement_bridge_summary()

    assert summary["three_u_complement_basis_shape"] == [22, 16]
    assert summary["three_u_complement_seed_form"][0][0] == -2
    assert summary["three_u_complement_seed_form"][0][2] == -1
    assert summary["three_u_complement_seed_form"][4][4] == -4
    assert summary["three_u_complement_first_refinement_form"][0][0] == -240
    assert summary["three_u_complement_first_refinement_form"][0][2] == -120
    assert summary["three_u_complement_first_refinement_form"][4][4] == -480
    assert summary["full_split_seed_form"][0][1] == 1
    assert summary["full_split_seed_form"][5][4] == 1
    assert summary["full_split_seed_form"][6][6] == -2
    assert summary["full_split_first_refinement_form"][0][1] == 120
    assert summary["full_split_first_refinement_form"][5][4] == 120
    assert summary["full_split_first_refinement_form"][6][6] == -240
