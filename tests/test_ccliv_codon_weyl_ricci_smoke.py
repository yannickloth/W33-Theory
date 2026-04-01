def test_ccliv_codon_weyl_ricci_smoke():
    q, k, mu = 3, 12, 4
    assert mu ** 3 == 64
    assert 5 * (k - 1) == 55
    assert q ** 2 == 9
    assert 55 + 9 == 64
