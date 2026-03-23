import numpy as np


def hyperdeterminant_2x2x2(t):
    # t: 2x2x2 tensor, indexed [i,j,k]
    a = t[0, 0, 0]
    b = t[0, 0, 1]
    c = t[0, 1, 0]
    d = t[0, 1, 1]
    e = t[1, 0, 0]
    f = t[1, 0, 1]
    g = t[1, 1, 0]
    h = t[1, 1, 1]
    return (
        a*a*h*h + b*b*g*g + c*c*f*f + d*d*e*e
        - 2*(a*b*g*h + a*c*f*h + a*d*e*h + b*c*f*g + b*d*e*g + c*d*e*f)
        + 4*(a*d*f*g + b*c*e*h)
    )


def make_local_filter(u0, u1):
    # lower-triangular local filter as in the v46 description
    return np.array([[1.0 / u0, 0.0], [-u1 / u0, 1.0]], dtype=float)


def apply_local(psi, G, axis):
    # Apply local linear map G to the specified tensor axis.
    out = np.tensordot(G, psi, axes=([1], [axis]))
    # Move the new axis into the original position.
    axes = list(range(out.ndim))
    perm = axes[1:axis+1] + [0] + axes[axis+1:]
    return np.transpose(out, perm)


def test_ghz_gauge_can_remove_rank1_background():
    # random but nondegenerate 1-qubit vectors
    u = np.array([0.6, 0.8], dtype=float)
    v = np.array([0.7, 0.7142857], dtype=float)
    w = np.array([0.9, 0.43589], dtype=float)
    beta = 0.37

    # construct tensor psi = u ⊗ v ⊗ w + beta |111>
    psi = np.zeros((2, 2, 2), dtype=float)
    for i in range(2):
        for j in range(2):
            for k in range(2):
                psi[i, j, k] = u[i] * v[j] * w[k]
    psi[1, 1, 1] += beta

    # apply local gauge filters to remove the rank-1 background
    G1 = make_local_filter(u[0], u[1])
    G2 = make_local_filter(v[0], v[1])
    G3 = make_local_filter(w[0], w[1])

    psi_gauged = apply_local(psi, G1, 0)
    psi_gauged = apply_local(psi_gauged, G2, 1)
    psi_gauged = apply_local(psi_gauged, G3, 2)

    # After gauge, the only nonzero entries should be 000 and 111.
    nonzeros = np.argwhere(np.abs(psi_gauged) > 1e-8)
    assert len(nonzeros) == 2
    assert (0, 0, 0) in map(tuple, nonzeros)
    assert (1, 1, 1) in map(tuple, nonzeros)

    # Verify hyperdeterminant transforms with det^2 factor
    det_factor = np.linalg.det(G1) * np.linalg.det(G2) * np.linalg.det(G3)
    det_factor_sq = det_factor * det_factor
    hd_orig = hyperdeterminant_2x2x2(psi)
    hd_gauged = hyperdeterminant_2x2x2(psi_gauged)
    assert abs(hd_gauged - det_factor_sq * hd_orig) < 1e-10

    # For this class, the hyperdeterminant (up to prefactor) is beta^2
    # after gauge-removal of rank-1 background.
    assert abs(hd_gauged - beta * beta) < 1e-8
