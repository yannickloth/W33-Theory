def test_ccxxix_curvature_smoke():
    q, k, lam, mu = 3, 12, 2, 4
    Phi3, Phi4 = 13, 10
    assert Phi4 == 10
    assert q**2 == 9
    assert lam * Phi4 == 20
    assert lam * Phi4 == Phi4 + q**2 + 1
    assert q * Phi3 == (lam * Phi4) + Phi4 + q**2
    assert 5 * (k - 1) == 55
