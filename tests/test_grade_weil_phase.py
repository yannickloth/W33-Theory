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
        if any(int(v) % 3 != 0 for v in mu.values()):
            any_nontrivial = True
            break
    assert any_nontrivial
