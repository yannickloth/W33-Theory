def test_ccxxxii_neutrino_curvature_smoke():
    q, v, k, lam = 3, 40, 12, 2
    Phi3, Phi4 = 13, 10
    assert v - k + 1 == 29
    assert lam * Phi4 + q**2 == 20 + 9 == 29
    assert q * Phi3 == 39
    assert v - k + 1 == q * Phi3 - Phi4
    assert lam * (v - k + 1) == 58
