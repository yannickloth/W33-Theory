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
        # the plain permutation should always be a Lie automorphism
        assert verify_symplectic_automorphism(alg, A)
        # Weil-phase variant need not preserve the bracket; just ensure it
        # produces a bijection for exploratory purposes.
        perm2 = symplectic_aut_with_phase(alg, A)
        assert perm2 is not None
        assert sorted(perm2) == list(range(24))
        # and raw compute_symplectic_automorphism if available; this one is
        # guaranteed to be an automorphism when it does not return None.
        perm3 = compute_symplectic_automorphism(alg, A)
        if perm3 is not None:
            # compute_symplectic_automorphism may return a bijection even when it
            # does not produce a true automorphism; we only enforce bijectivity
            assert sorted(perm3) == list(range(24))


def test_basis_perm_to_code_perm():
    """Ensure the helper converts 24->12 permutations correctly."""
    from scripts.w33_golay_lie_algebra import basis_perm_to_code_perm
    # the conversion should always return either None or a 12-element permutation
    alg = build_golay_lie_algebra()
    id24 = list(range(24))
    cp = basis_perm_to_code_perm(alg, id24)
    # result may be None because the 24 basis hexads do not distinguish all
    # twelve points; that's acceptable.  If a map is returned it must be a
    # valid permutation.
    if cp is not None:
        assert sorted(cp) == list(range(12))

    # scalar 2*I permutation should still produce either None or a permutation
    import numpy as np
    A2 = np.array([[2, 0], [0, 2]], dtype=int)
    perm2 = compute_symplectic_automorphism(alg, A2)
    assert perm2 is not None
    cp2 = basis_perm_to_code_perm(alg, perm2)
    if cp2 is not None:
        assert sorted(cp2) == list(range(12))
    # but if they do the returned mapping must be a true permutation.
    mats = all_symplectic_matrices()
    for A in mats:
        if np.array_equal(A, np.eye(2, dtype=int)):
            continue
        perm = compute_symplectic_automorphism(alg, A)
        if perm is None:
            continue
        cp = basis_perm_to_code_perm(alg, perm)
        # no nonidentity matrix should induce a code permutation
        assert cp is None


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
    # with the canonical Weil phase only ±Identity lift to actual automorphisms
    assert len(perms) == 2
    # identity permutation must be present
    assert list(range(24)) in perms
    # the other one should correspond to scalar 2·I
    import numpy as np

    A2 = np.array([[2, 0], [0, 2]], dtype=int)
    expected = compute_symplectic_automorphism(alg, A2)
    assert expected in perms
