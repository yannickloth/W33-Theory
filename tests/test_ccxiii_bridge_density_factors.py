import numpy as np


def _make_normalized_columns(a1, b1, a2, b2):
    v1 = np.array([1.0 + 0j, a1, b1], dtype=np.complex128)
    v2 = np.array([1.0 + 0j, a2, b2], dtype=np.complex128)
    # normalize columns
    n1 = np.sqrt(np.vdot(v1, v1))
    n2 = np.sqrt(np.vdot(v2, v2))
    psi1 = v1 / n1
    psi2 = v2 / n2
    Psi = np.column_stack((psi1, psi2))
    return Psi


def test_plucker_det_vanishes_quadratically_under_plane_degen():
    # For quadratic scaling, columns must be identical at s=0 (det=0 there).
    # As s grows, the second column separates and det grows as s^2.
    a1 = 0.2 + 0.1j
    b1 = -0.3 + 0.05j
    # perturbation direction for the second column
    da = 0.5 + 0.3j
    db = -0.4 + 0.2j

    scales = [1e-3, 3e-3, 1e-2, 3e-2]
    vals = []
    for s in scales:
        # second column starts identical to first, moves away with scale s
        Psi = _make_normalized_columns(a1, b1, a1 + s * da, b1 + s * db)
        det = np.linalg.det(Psi.conj().T @ Psi)
        vals.append(abs(det))

    # check approximate quadratic scaling: vals[i] / scales[i]^2 ≈ constant
    ratios = [vals[i] / (scales[i] ** 2) for i in range(len(scales))]
    assert np.std(ratios) / np.mean(ratios) < 0.5


def test_det_kext_change_of_basis_identity():
    # For any 2x2 Hermitian Q and invertible 2x2 M, det(M.T @ Q @ M) == det(Q) * det(M)^2
    rng = np.random.RandomState(17)
    # random Hermitian Q
    A = rng.randn(2, 2) + 1j * rng.randn(2, 2)
    Q = A + A.conj().T
    # random invertible M
    while True:
        M = rng.randn(2, 2) + 1j * rng.randn(2, 2)
        if abs(np.linalg.det(M)) > 1e-6:
            break

    lhs = np.linalg.det(M.T @ Q @ M)
    rhs = np.linalg.det(Q) * (np.linalg.det(M) ** 2)
    assert np.allclose(lhs, rhs, atol=1e-10)
