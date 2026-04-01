def test_cclii_monster_carrier_prime_smoke():
    q, v, k = 3, 40, 12
    Phi6 = 7
    lam = 2
    carrier = v + k + Phi6
    assert carrier == 59
    assert (lam * Phi6) ** 2 + carrier == 196 + 59 == 255
    assert 47 * carrier * 71 == 196883
