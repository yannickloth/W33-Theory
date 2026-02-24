from __future__ import annotations


def test_suz_contains_m12_2_by_atlas_words() -> None:
    from scripts.w33_2suz_m12_2_subgroup import analyze

    rep = analyze(compute_orders=True)
    assert rep.get("available") is True

    orders = rep.get("orders", {})
    assert isinstance(orders, dict)
    # The preimage of M12:2 inside 2.Suz has order 2*|M12:2| = 380,160.
    assert int(orders.get("full_order", 0) or 0) == 380_160
    # The derived subgroup projects to M12, so its preimage should be 2.M12 (order 190,080).
    assert int(orders.get("derived_order", 0) or 0) == 190_080
    assert int(orders.get("projective_order_div2", 0) or 0) == 190_080

