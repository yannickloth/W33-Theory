def test_ccxxxv_chiral_clifford_gap_smoke():
    q, k, mu = 3, 12, 4
    Phi3 = 13
    assert 2 * ((q + 3) * (q + 2) // 2) + q**2 == 15 + 15 + 9 == 39
    assert q * Phi3 == 39
    assert 5 * (k - 1) == 55
    assert 55 - 39 == mu**2 == 16
