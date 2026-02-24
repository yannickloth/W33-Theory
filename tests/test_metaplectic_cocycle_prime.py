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

