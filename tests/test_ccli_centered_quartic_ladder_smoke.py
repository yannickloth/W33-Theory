def test_ccli_centered_quartic_ladder_smoke():
    mu = 4
    E = 240
    root = 255
    assert mu**4 - mu**2 == E
    assert mu**4 - 1 == root
    assert root - E == mu**2 - 1 == 15
