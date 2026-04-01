def test_cclv_codon_chiral_block_smoke():
    q, mu = 3, 4
    Phi3 = 13
    assert mu ** 3 == 64
    assert q * Phi3 == 39
    assert (q + 2) ** 2 == 25
    assert 39 + 25 == 64
    assert 55 - 39 == 25 - 9 == mu ** 2
