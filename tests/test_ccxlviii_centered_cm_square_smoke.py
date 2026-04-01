def test_ccxlviii_centered_cm_square_smoke():
    mu2 = 16
    lam2 = 4
    assert mu2 - lam2 == 12
    assert mu2 - 1 == 15
    assert mu2 + 1 == 17
    assert mu2 + lam2 == 20
    assert 12 + 20 == 15 + 17 == 32
