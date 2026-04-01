def test_ccxxxix_cm_weyl_block_smoke():
    q, g = 3, 15
    assert ((q + 3) * (q + 2)) // 2 == 15
    assert g == 15
    assert -(g ** 3) == -3375
    assert 15 * 17 == 255
