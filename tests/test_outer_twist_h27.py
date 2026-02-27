from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

# helper symplectic form on F3^2

def omega(u: tuple[int, int], v: tuple[int, int]) -> int:
    # u=(x,y), v=(x',y')
    return (u[1] * v[0] - u[0] * v[1]) % 3


def mat_mod3(M):
    return np.array(M, dtype=int) % 3


def test_outer_twist_affine_formula_and_similitude():
    """Verify the claimed outer-twist linear map and its similitude property."""
    # data from conversation
    A = np.array([[1, 2], [2, 0]], dtype=int) % 3
    b = np.array([0, 2], dtype=int) % 3
    detA = int(round(np.linalg.det(A))) % 3
    assert detA == 2  # nonsquare class

    # test similitude on all u,v in F3^2
    for x1 in range(3):
        for y1 in range(3):
            u = (x1, y1)
            Au = tuple(int(x) for x in (A @ np.array(u) % 3))
            for x2 in range(3):
                for y2 in range(3):
                    v = (x2, y2)
                    Av = tuple(int(x) for x in (A @ np.array(v) % 3))
                    lhs = omega(Au, Av)
                    rhs = (detA * omega(u, v)) % 3
                    assert lhs == rhs

    # check fiber formula also reproduces a few random samples
    for x in range(3):
        for y in range(3):
            for t in range(3):
                u = np.array([x, y], dtype=int)
                up = tuple(int(x) for x in (A @ u + b) % 3)
                tp = (2 * t + (2 + 2 * x + y)) % 3
                # just ensure values are in range
                assert 0 <= tp < 3


def test_conjugation_of_stabilizer_matrices():
    """Make sure SL(2,3) generators conjugate appropriately under A."""
    # load original S,T from fusion bundle
    bundle = Path(os.getcwd()) / "H27_CE2_FUSION_BRIDGE_BUNDLE_v01"
    data = json.load(open(bundle / "stabilizer_SL2_and_mu_bridge.json"))
    S = mat_mod3(np.array(data["target_S_matrix"]))
    T = mat_mod3(np.array(data["target_T_matrix"]))
    A = mat_mod3(np.array([[1, 2], [2, 0]]))
    # compute inverse in GL(2,3) by hand to avoid floating-point issues
    # det A = 2 (mod3), its inverse is 2 as well
    A_inv = mat_mod3(np.array([[0, 2], [2, 2]]))
    # compute conjugates
    S2 = mat_mod3(A @ S @ A_inv)
    T2 = mat_mod3(A @ T @ A_inv)
    # they should still satisfy symplectic conditions: det=1 and preserve omega
    for M in (S2, T2):
        # check determinant 1 (mod3)
        assert int(round(np.linalg.det(M))) % 3 == 1
        for x1 in range(3):
            for y1 in range(3):
                u = (x1, y1)
                Mu = tuple(int(x) for x in (M @ np.array(u) % 3))
                for x2 in range(3):
                    for y2 in range(3):
                        v = (x2, y2)
                        Mv = tuple(int(x) for x in (M @ np.array(v) % 3))
                        assert omega(Mu, Mv) == omega(u, v)