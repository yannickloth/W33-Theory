from __future__ import annotations

import numpy as np


def test_all_solutions_p_identity_p5() -> None:
    from scripts.metaplectic_cocycle import all_solutions_p

    p = 5
    A = np.eye(2, dtype=int)
    sols = all_solutions_p(A, p)
    assert len(sols) == p * p

    expected = []
    for a in range(p):
        for b in range(p):
            mu = {}
            for x in range(p):
                for y in range(p):
                    mu[(x, y)] = (a * x + b * y) % p
            expected.append(mu)
    for mu in expected:
        assert mu in sols


def test_all_solutions_p_various_matrices_primes() -> None:
    """Verify solver returns exactly p^2 solutions for a handful of primes and A's."""
    from scripts.metaplectic_cocycle import all_solutions_p

    candidates = [
        lambda p: np.eye(2, dtype=int),
        lambda p: np.array([[1, 1], [0, 1]], dtype=int),
        lambda p: np.array([[0, 1], [-1, 0]], dtype=int),
    ]
    for p in (3, 5, 7):
        for maker in candidates:
            A = maker(p) % p
            sols = all_solutions_p(A, p)
            assert len(sols) == p * p

