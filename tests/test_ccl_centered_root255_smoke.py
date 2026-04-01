def test_ccl_centered_root255_smoke():
    mu = 4
    root = 255
    assert mu**2 - 1 == 15
    assert mu**2 + 1 == 17
    assert (mu**2 - 1) * (mu**2 + 1) == root
    assert mu**4 - 1 == root
