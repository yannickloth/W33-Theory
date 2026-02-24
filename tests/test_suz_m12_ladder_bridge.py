from __future__ import annotations


def test_suz_contains_m12_2_at_order_level() -> None:
    from scripts.w33_suz_m12_ladder_bridge import analyze

    rep = analyze()
    assert rep.get("available") is True
    assert rep["orders"]["Suz"] == 448_345_497_600
    assert rep["orders"]["M12:2"] == 190_080
    assert rep["indices"]["Suz_over_M12_2"] == 2_358_720

