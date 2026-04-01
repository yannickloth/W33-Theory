def test_ccxlv_scalar_extension_smoke():
    g, mu = 15, 4
    E = g * (mu ** 2)
    root = g * (mu ** 2 + 1)
    assert E == 240
    assert root == 255
    assert root - E == g == 15
