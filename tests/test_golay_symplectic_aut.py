import numpy as np
from scripts.w33_golay_lie_algebra import (
    build_golay_lie_algebra,
    symplectic_aut_permutation,
    symplectic_aut_with_phase,
    compute_symplectic_automorphism,
    _verify_permutation_is_aut,
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
        # also test the Weil phase variant (should still be an automorphism)
        perm2 = symplectic_aut_with_phase(alg, A)
        assert perm2 is not None
        assert _verify_permutation_is_aut(alg, perm2)
        # and raw compute_symplectic_automorphism if available
        perm3 = compute_symplectic_automorphism(alg, A)
        if perm3 is not None:
            assert _verify_permutation_is_aut(alg, perm3)


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

def test_symplectic_automorphisms_helper():
    from scripts.w33_golay_lie_algebra import symplectic_automorphisms

    alg = build_golay_lie_algebra()
    perms = symplectic_automorphisms(alg)
    # there are 24 symplectic matrices; helper should find 24 valid perms
    assert len(perms) == 24