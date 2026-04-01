def test_cclix_packet118_master_smoke():
    q, v, k, mu = 3, 40, 12, 4
    Phi3, Phi6 = 13, 7
    g = 15
    carrier = v + k + Phi6
    assert 2 * carrier == 118
    assert mu ** 3 + q * Phi3 + g == 64 + 39 + 15 == 118
    assert 47 + 71 == 118
