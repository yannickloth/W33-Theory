def test_ccxlii_cm_heat_prime_smoke():
    q, v, k, lam = 3, 40, 12, 2
    Phi3, Phi4, Phi6 = 13, 10, 7
    assert (lam * Phi6) ** 2 == 196
    assert v + k + Phi6 == 59
    assert 196 + 59 == 255
    assert 4 * (k - 1) + 15 == 59
    assert q * Phi3 + lam * Phi4 == 59
