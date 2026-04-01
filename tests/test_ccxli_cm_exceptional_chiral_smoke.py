def test_ccxli_cm_exceptional_chiral_smoke():
    q, v, k, g = 3, 40, 12, 15
    E = v * k // 2
    assert E == 240
    assert g == 15
    assert E + g == 255
