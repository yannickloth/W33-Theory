from __future__ import annotations

from w33_uor_transport_shadow_bridge import build_w33_uor_transport_shadow_summary


def test_uor_transport_shadow_recovers_full_nonabelian_group_and_z2_shadow() -> None:
    summary = build_w33_uor_transport_shadow_summary()
    bridge = summary["weyl_group_shadow"]
    assert summary["status"] == "ok"
    assert bridge["realized_edge_weyl_matrices"] == 6
    assert bridge["group_closure_order"] == 6
    assert bridge["sign_kernel_order"] == 3
    assert bridge["sign_nontrivial_coset_order"] == 3
    assert bridge["even_weyl_edge_classes"] == 3
    assert bridge["odd_weyl_edge_classes"] == 3
    assert bridge["edge_sign_character_is_surjective"] is True


def test_uor_transport_shadow_matches_triangle_parity_and_forgets_nonabelian_detail() -> None:
    summary = build_w33_uor_transport_shadow_summary()
    triangle = summary["triangle_shadow"]
    assert triangle["triangle_cycle_type_counts"] == {
        "identity": 240,
        "three_cycle": 2880,
        "transposition": 2160,
    }
    assert triangle["triangle_parity_equals_holonomy_sign_exactly"] is True
    assert triangle["z2_shadow_forgets_identity_vs_three_cycle"] is True


def test_uor_transport_bridge_verdict_stays_on_holonomy_not_raw_voltage() -> None:
    summary = build_w33_uor_transport_shadow_summary()
    alignment = summary["uor_alignment"]
    assert alignment["coefficient_shadow_ring"] == "Z/2Z"
    assert alignment["nonabelian_transport_group"] == "Weyl(A2) ~= S3 ~= D3"
    assert alignment["right_binary_shadow_is_holonomy_sign_not_raw_edge_voltage"] is True
