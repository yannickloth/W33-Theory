def test_ccxl_cm_packet_sum_smoke():
    q, lam = 3, 2
    Phi3, Phi4, Phi6 = 13, 10, 7
    assert (lam * Phi6) ** 2 == 196
    assert q * Phi3 == 39
    assert lam * Phi4 == 20
    assert 196 + 39 + 20 == 255
