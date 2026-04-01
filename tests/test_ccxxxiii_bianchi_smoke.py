def test_ccxxxiii_bianchi_smoke():
    q, k, lam = 3, 12, 2
    Phi4 = 10
    s = k // lam
    N = lam * Phi4
    assert s == 6
    assert N == 20
    assert ((s + 1) * s) // 2 - 1 == 20
