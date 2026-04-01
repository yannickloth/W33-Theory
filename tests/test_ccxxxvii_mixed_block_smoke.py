def test_ccxxxvii_mixed_block_smoke():
    q, mu = 3, 4
    assert 15 + 25 + 15 == 55
    assert 15 + 9 + 15 == 39
    assert 25 - 9 == 16
    assert 16 == mu**2
    assert (q + 2) ** 2 - q**2 == 16
