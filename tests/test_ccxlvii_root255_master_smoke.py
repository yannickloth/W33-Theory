def test_ccxlvii_root255_master_smoke():
    q, v, k, lam, mu, g = 3, 40, 12, 2, 4, 15
    Phi3, Phi4, Phi6 = 13, 10, 7
    E = v * k // 2
    assert g * (mu ** 2 + 1) == 15 * 17 == 255
    assert (lam * Phi6) ** 2 + q * Phi3 + lam * Phi4 == 196 + 39 + 20 == 255
    assert E + g == 240 + 15 == 255
    assert (lam * Phi6) ** 2 + (v + k + Phi6) == 196 + 59 == 255
