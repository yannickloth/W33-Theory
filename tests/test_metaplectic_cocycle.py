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


def test_additional_patterns():
    # confirm metadata patterns observed during exploration
    involution_found = False
    summary = []
    encountered_patterns: set[tuple[int, int, int]] = set()
    for A in all_symplectic_matrices():
        md = solution_space_metadata(A)
        # number-of-solutions sanity
        assert md["num_solutions"] == 9
        # involution: only one, order 2, phase trivial
        if md["order"] == 2:
            involution_found = True
            # only the origin and eight grades all map to zero
            assert md["dist"] == {0: 9}
        # any element of order>2 must have some nonzero canonical value
        if md["order"] is not None and md["order"] > 2:
            assert any(v != 0 for v in md["canonical"].values())
        # the number of zeros on nonzero grades is always even
        counts = dict(md["dist"])
        counts[0] -= 1
        assert counts.get(0, 0) % 2 == 0

        # record histogram type ignoring value labels 1/2
        nzhist = {k: v for k, v in counts.items() if k != 0}
        pattern = (counts.get(0, 0), nzhist.get(1, 0), nzhist.get(2, 0))
        encountered_patterns.add(pattern)

        summary.append((md["order"], md["trace"], counts))

    assert involution_found, "expected an involution in Sp(2,3)"
    # the only patterns that occur
    assert encountered_patterns == {
        (8, 0, 0),  # involution
        (4, 2, 2),  # balanced 4/2/2
        (2, 6, 0),  # two zeros, six ones
        (2, 0, 6),  # two zeros, six twos (orientation swap)
        (0, 4, 4),  # no zeros
    }
    # print summary for manual inspection
    print("order, trace, nonzero-hist")
    for row in summary:
        print(row)


def test_phi_omega_zero_relation():
    # empirical relation between number of zeros in canonical phase and
    # symplectic-delta omega values for nonzero grades.
    from scripts.grade_weil_phase import GRADES_NONZERO, omega, apply_matrix

    allowed = {(0, 0), (2, 2), (4, 0), (4, 2), (8, 8)}
    for A in all_symplectic_matrices():
        md = solution_space_metadata(A)
        # metadata count includes the (0,0) origin always zero;
        # remove it to compare with omega-values on nonzero grades.
        phi_zeros = md["dist"].get(0, 0) - 1
        wzeros = 0
        for g in GRADES_NONZERO:
            Ag = apply_matrix(A, g)
            d = ((Ag[0] - g[0]) % 3, (Ag[1] - g[1]) % 3)
            if omega(g, d) == 0:
                wzeros += 1
        assert (phi_zeros, wzeros) in allowed


def test_omega_zero_implies_phi_zero():
    """Whenever the symplectic delta is zero, the phase on that grade vanishes."""
    from scripts.grade_weil_phase import GRADES_NONZERO, omega, apply_matrix

    for A in all_symplectic_matrices():
        mu = canonical_phase(A)
        for g in GRADES_NONZERO:
            Ag = apply_matrix(A, g)
            d = ((Ag[0] - g[0]) % 3, (Ag[1] - g[1]) % 3)
            if omega(g, d) == 0:
                assert mu[g] == 0

