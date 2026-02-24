import numpy as np
from scripts.grade_weil_phase import all_symplectic_matrices, compute_phase, apply_matrix

def test_identity_phase():
    I = np.array([[1,0],[0,1]], dtype=int)
    mu = compute_phase(I)
    assert mu is not None
    assert all(v == 0 for v in mu.values())

def test_some_nontrivial():
    mats = all_symplectic_matrices()
    # for our section cocycle, every symplectic A should admit a phase correction,
    # and at least one non-identity should produce a nontrivial mu.
    nonid = [A for A in mats if not np.array_equal(A, np.eye(2, dtype=int))]
    assert nonid

    any_nontrivial = False
    for A in nonid:
        mu = compute_phase(A)
        assert mu is not None
        # check gauge-formula holds for returned phase
        from scripts.grade_weil_phase import gauge_f, apply_matrix
        for g, val in mu.items():
            expect = (gauge_f(apply_matrix(A, g)) - gauge_f(g)) % 3
            assert int(val) == int(expect)
        if any(int(v) % 3 != 0 for v in mu.values()):
            any_nontrivial = True
            break
    assert any_nontrivial

    # Weil 1-cocycle check for the induced Heisenberg automorphisms:
    # (A,mu_A)∘(B,mu_B) = (AB, mu_B + mu_A∘B).
    def key(M: np.ndarray) -> tuple[int, ...]:
        return tuple(int(x) % 3 for x in M.reshape(-1))

    mu_by_key = {key(A): compute_phase(A) for A in mats}
    assert all(v is not None for v in mu_by_key.values())

    for A in mats:
        muA = mu_by_key[key(A)]
        assert muA is not None
        for B in mats:
            AB = (A @ B) % 3
            muAB = mu_by_key[key(AB)]
            muB = mu_by_key[key(B)]
            assert muAB is not None and muB is not None
            for g in muA:
                Bg = apply_matrix(B, g)
                assert muAB[g] == (muB[g] + muA[Bg]) % 3
