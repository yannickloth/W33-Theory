def test_ccxliv_cm_affine_square_smoke():
    q = 3
    k = 12
    g = 15
    mu2p1 = 17
    curv = 20
    assert g - k == q
    assert curv - mu2p1 == q
    assert mu2p1 - k == q + 2
    assert curv - g == q + 2
