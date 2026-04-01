def test_ccxliii_cm_exceptional_product_smoke():
    v, k, g, mu = 40, 12, 15, 4
    E = v * k // 2
    assert E == 240
    assert k * (v // 2) == 12 * 20 == 240
    assert g * (mu ** 2) == 15 * 16 == 240
