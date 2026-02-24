import numpy as np
from scripts.w33_golay_lie_algebra import (
    build_golay_lie_algebra,
    symplectic_aut_permutation,
    verify_symplectic_automorphism,
)
from scripts.grade_weil_phase import all_symplectic_matrices


def test_all_symplectic_are_automorphisms():
    alg = build_golay_lie_algebra()
    mats = all_symplectic_matrices()
    assert len(mats) == 24
    for A in mats:
        perm = symplectic_aut_permutation(alg, A)
        assert perm is not None
        # check bijectivity
        assert sorted(perm) == list(range(24))
        assert verify_symplectic_automorphism(alg, A)


def test_nontrivial_action_exists():
    # at least one non-identity matrix should move some basis vector
    alg = build_golay_lie_algebra()
    mats = all_symplectic_matrices()
    I = np.eye(2, dtype=int)
    moved = False
    for A in mats:
        if np.array_equal(A, I):
            continue
        perm = symplectic_aut_permutation(alg, A)
        assert perm is not None
        if any(perm[i] != i for i in range(24)):
            moved = True
            break
    assert moved, "no nonidentity symplectic automorphism moves any basis element"