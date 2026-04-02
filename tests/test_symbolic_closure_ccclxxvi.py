"""
Phase CCCLXXVI — Symbolic closure ledger from the latest bridge phases.

This file keeps the closure statement deliberately exact and conservative:
it only tests identities that follow directly from the W(3,3) packet and the
new bridge phases CCCLXX–CCCLXXV.
"""

from fractions import Fraction
import cmath
import math


# W(3,3) packet
v, k, lam, mu = 40, 12, 2, 4
r, s = 2, -4
f, g = 24, 15
E = v * k // 2
T = v * k * lam // 6
a0 = k**2 + f * r**2 + g * s**2
q = 3


def test_basic_packet():
    assert (v, k, lam, mu) == (40, 12, 2, 4)
    assert E == 240
    assert T == 160
    assert a0 == 480
    assert 1 + f + g == v


def test_laplacian_channel():
    lap_spec = sorted([k - k, k - r, k - s])
    assert lap_spec == [0, 10, 16]
    assert (k - r) == 10
    assert (k - s) == 16


def test_entropy_gravity_closure():
    Ginv = 2 * a0
    Smax = E
    assert Ginv == 960
    assert Ginv == 4 * E
    assert Ginv == 2 * v * k
    assert Smax == a0 // 2
    assert Smax == Ginv // 4


def test_euler_betti_closure():
    chi = v - E + T
    b1 = v + 1
    assert chi == -40
    assert chi == -v
    assert 1 - b1 == chi
    assert b1 == 41


def test_quantum_root_of_unity_closure():
    omega = cmath.exp(2j * cmath.pi / 3)
    assert abs(omega**3 - 1) < 1e-10
    assert abs(omega - 1) > 0.1
    qint3 = (omega**3 - omega**(-3)) / (omega - omega**(-1))
    assert abs(qint3) < 1e-10
    assert q**mu == 81
    assert q**2 == 9


def test_topological_sector_closure():
    gap = r - s
    bandwidth = k - s
    chern = q
    nu = chern % 2
    assert gap == 6
    assert gap == k // 2
    assert bandwidth == 16
    assert bandwidth == 2**mu
    assert chern == 3
    assert nu == 1


def test_arithmetic_kernel_packet():
    def P(ev, u):
        return 1 - ev * u + (k - 1) * u * u

    assert P(k, 0) == 1
    assert P(r, 0) == 1
    assert P(s, 0) == 1

    disc_r = r * r - 4 * (k - 1)
    disc_s = s * s - 4 * (k - 1)
    assert disc_r < 0
    assert disc_s < 0

    root_modulus = 1 / math.sqrt(k - 1)
    assert abs(root_modulus - 1 / math.sqrt(11)) < 1e-10


def test_symbolic_bridge_summary():
    # Compact ledger of the exact bridge identities added in the note.
    assert 2 * a0 == 4 * E == 2 * v * k
    assert E == a0 // 2
    assert (r - s) == (k // 2)
    assert (k - s) == 2**mu
    assert q**mu == 81
    assert q**2 == 9
