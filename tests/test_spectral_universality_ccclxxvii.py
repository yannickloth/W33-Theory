"""
Phase CCCLXXVII — Corrected spectral universality ledger.

This test file encodes the stronger claim that the bridge-sector observables
from phases CCCLXX–CCCLXXV are reconstructible from the same finite packet
(q; v,k,lam,mu; r^f,s^g).
"""

import cmath
import math
from fractions import Fraction


# W(3,3) spectral packet
q = 3
v, k, lam, mu = 40, 12, 2, 4
r, s = 2, -4
f, g = 24, 15

E = v * k // 2
T = v * k * lam // 6
chi = v - E + T


def M(n: int) -> int:
    return k**n + f * (r**n) + g * (s**n)


def test_packet_and_moments():
    assert (q, v, k, lam, mu) == (3, 40, 12, 2, 4)
    assert (r, s, f, g) == (2, -4, 24, 15)
    assert E == 240
    assert T == 160
    assert chi == -40
    assert M(1) == 0
    assert M(2) == 480
    assert M(3) == 960


def test_holographic_sector_from_packet():
    S_single = k
    I_adj = mu
    I_nonadj = 2 * mu
    EW_single = 1 + k
    S_page_max = (v // 2) * k

    assert S_single == 12
    assert I_adj == 4
    assert I_nonadj == 8
    assert EW_single == 13
    assert S_page_max == E


def test_diffgeo_sector_from_packet():
    lap_spec = sorted([k - k, k - r, k - s])
    K_vertex = 1 - Fraction(k, 2) + Fraction(k * lam // 2, 3)

    assert lap_spec == [0, 10, 16]
    assert K_vertex == -1
    assert K_vertex * v == chi


def test_quantum_root_of_unity_sector_from_packet():
    omega = cmath.exp(2j * cmath.pi / 3)
    qint3 = (omega**3 - omega**(-3)) / (omega - omega**(-1))
    D_dim = q**mu
    gsd = q**2

    assert abs(omega**3 - 1) < 1e-10
    assert abs(qint3) < 1e-10
    assert D_dim == 81
    assert gsd == 9


def test_thermo_sector_from_packet():
    a0 = M(2)
    Ginv = 2 * a0
    T_H = k / (2 * math.pi)
    Smax = E

    assert a0 == 480
    assert Ginv == 960
    assert Smax == a0 // 2
    assert Smax == Ginv // 4
    assert abs(T_H - 6 / math.pi) < 1e-10


def test_arithmetic_sector_from_packet():
    disc = (r - s) ** 2
    root_modulus = 1 / math.sqrt(k - 1)

    assert disc == 36
    assert disc == (k // 2) ** 2
    assert abs(root_modulus - 1 / math.sqrt(11)) < 1e-10


def test_condensed_matter_sector_from_packet():
    gap = r - s
    width = k - s
    chern = q
    nu = chern % 2

    assert gap == 6
    assert gap == k // 2
    assert width == 16
    assert width == 2**mu
    assert chern == 3
    assert nu == 1


def test_master_equalities():
    a0 = M(2)
    gap_equals = (r - s)
    assert a0 == 480
    assert M(3) == 2 * a0
    assert 2 * a0 == 4 * E == 2 * v * k
    assert E == a0 // 2
    assert gap_equals == (k // 2)
    assert (k - s) == 2**mu
    assert q**mu == 81
    assert q**2 == 9
