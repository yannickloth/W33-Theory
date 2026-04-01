def test_ccxxxvi_cm_curvature_root_smoke():
    q, v, lam = 3, 40, 2
    Phi4 = 10
    assert v // 2 == 20
    assert lam * Phi4 == 20
    assert (v // 2) ** 3 == 20 ** 3 == 8000
