from __future__ import annotations


def test_2m12_golay_lifts_embed_in_sp12() -> None:
    from scripts.w33_2m12_sp12_embedding import analyze

    rep = analyze()
    assert rep.get("available") is True
    assert int(rep.get("field_p", 0) or 0) == 3

    golay = rep.get("golay", {})
    assert isinstance(golay, dict)
    assert golay.get("systematic_generator") is True
    assert golay.get("A_symmetric") is True

    symp = rep.get("symplectic", {})
    assert isinstance(symp, dict)
    assert int(symp.get("J0_rank", 0) or 0) == 12
    assert symp.get("S_preserves_J0") is True
    assert symp.get("gens_preserve_J0") is True

    g = rep.get("2m12", {})
    assert isinstance(g, dict)
    # In the 2-cover, an order-2 element may lift to order 2 or 4; similarly
    # an order-3 element may lift to order 3 or 6.
    assert int(g.get("b11_order", 0) or 0) in {2, 4}
    assert int(g.get("b21_order", 0) or 0) in {3, 6}
