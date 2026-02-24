from __future__ import annotations

import numpy as np

from scripts.grade_weil_phase import all_symplectic_matrices
from scripts.metaplectic_cocycle import (
    all_solutions,
    canonical_phase,
    difference_is_linear,
    linear_functionals,
    solution_space_metadata,
)


def test_solver_matches_canonical():
    mats = all_symplectic_matrices()
    for A in mats:
        sols = all_solutions(A)
        assert sols, "no solution found for A"
        mu2 = canonical_phase(A)
        # canonical phase should appear among the solutions
        assert mu2 in sols
        # the solution space should be affine over the space of linear maps
        # (which has size 9 = 3^2).  metadata helper captures this as well.
        md = solution_space_metadata(A)
        assert md["num_solutions"] == 9
        assert md["num_solutions"] == len(sols)
        # difference between any two solutions should be a linear functional
        for i in range(len(sols)):
            for j in range(i + 1, len(sols)):
                assert difference_is_linear(sols[i], sols[j])
        # ensure every solution differs from canonical by a linear map
        for mu in sols:
            assert difference_is_linear(mu, mu2)


def test_solver_space_dimension():
    A = np.array([[1,0],[0,1]], dtype=int)
    sols = all_solutions(A)
    # identity case should produce exactly 9 solutions (one for each linear functional)
    assert len(sols) == 9
    # check they are exactly the linear maps
    expected = linear_functionals()
    for mu in expected:
        assert mu in sols

