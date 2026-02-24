import numpy as np
from scripts.grade_weil_phase import all_symplectic_matrices, compute_phase

def test_identity_phase():
    mats = all_symplectic_matrices()
    I = np.array([[1,0],[0,1]], dtype=int)
    mu = compute_phase(I)
    assert mu is not None
    assert all(v == 0 for v in mu.values())

def test_some_nontrivial():
    mats = all_symplectic_matrices()
    # ensure at least one non-identity returns None (no phase)
    nonid = [A for A in mats if not np.array_equal(A, np.eye(2, dtype=int))]
    assert nonid
    any_bad = False
    for A in nonid[:5]:
        mu = compute_phase(A)
        if mu is None:
            any_bad = True
            break
    assert any_bad
