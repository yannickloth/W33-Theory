from scripts.inner_auto_group import compute_inner_aut_group


def test_inner_group_limit():
    # ensure the enumerator respects the limit parameter and returns matrices
    G = compute_inner_aut_group(limit=20)
    assert isinstance(G, list)
    assert len(G) == 20
    for M in G:
        assert M.shape == (24, 24)


def test_inner_group_growth():
    # a tiny limit should produce at least that many distinct matrices
    G = compute_inner_aut_group(limit=3)
    assert len(G) >= 3
    # first element should be the identity
    import numpy as np
    I = np.eye(24, dtype=int)
    assert any(np.array_equal(M, I) for M in G)


def test_symplectic_conjugates_transvection_generators():
    from scripts.inner_auto_group import symplectic_conjugates_transvection_generators

    assert symplectic_conjugates_transvection_generators() is True
