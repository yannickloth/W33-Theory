def test_ccxlix_heat_extension_ladder_smoke():
    lam, Phi6, k, g = 2, 7, 12, 15
    heat = (lam * Phi6) ** 2
    assert heat == 196
    assert heat + 4 * (k - 1) == 240
    assert 240 + g == 255
