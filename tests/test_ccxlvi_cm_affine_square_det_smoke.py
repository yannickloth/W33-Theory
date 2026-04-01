def test_ccxlvi_cm_affine_square_det_smoke():
    k, g = 12, 15
    mu2p1 = 17
    curv = 20
    assert k * curv - g * mu2p1 == -g
