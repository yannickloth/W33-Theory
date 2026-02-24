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
