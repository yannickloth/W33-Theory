from __future__ import annotations


def test_golay_side_outer_normalizer_exists() -> None:
    from scripts.w33_2m12_outer_normalizer import analyze

    rep = analyze(compute_full_order=False)
    assert rep.get("available") is True
    assert int(rep.get("field_p", 0) or 0) == 3

    orders = rep.get("orders", {})
    assert isinstance(orders, dict)
    assert int(orders.get("base_order", 0) or 0) == 190_080

    outer = rep.get("outer", {})
    assert isinstance(outer, dict)
    assert int(outer.get("predicted_full_order", 0) or 0) == 380_160
    assert outer.get("X2_pblock_in_H") is True
    assert outer.get("minus_I6_in_H") is True
    assert int(outer.get("dual_sign", 0) or 0) in {1, 2}

    xord = int(outer.get("X_order", 0) or 0)
    assert xord > 0 and xord % 2 == 0

    pol = rep.get("polarization", {})
    assert isinstance(pol, dict)
    assert int(pol.get("commutant_dim", 0) or 0) == 2
    assert pol.get("found_involution") is True
    assert pol.get("involution_is_scalar") is False
    assert pol.get("involution_squares_to_I") is True
    assert pol.get("eigenspace_dims") == {"+1": 6, "-1": 6}
    assert pol.get("plus_isotropic") is True
    assert pol.get("minus_isotropic") is True
    assert pol.get("x_conjugates_J_to_minus_J") is True
