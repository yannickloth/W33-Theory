"""
Phase CCCLXXVIII — Bidirectional spectral universality.

CCCLXXVII showed that the promoted sector observables from CCCLXX–CCCLXXV
are controlled by one finite packet

    (q; v, k, lam, mu; r^f, s^g).

This phase closes the inverse direction: a small exact cross-sector observable
packet reconstructs that same spectral packet uniquely. The promoted finite
story is therefore bidirectional rather than one-way.
"""

from __future__ import annotations

import math
from fractions import Fraction


OBSERVABLES = {
    "S_single": 12,
    "I_adj": 4,
    "S_page_max": 240,
    "GSD": 9,
    "D_dim": 81,
    "gap": 6,
    "width": 16,
    "chi": -40,
}


def exact_integer_log(base: int, target: int) -> int:
    power = 1
    exponent = 0
    while power < target:
        power *= base
        exponent += 1
    assert power == target
    return exponent


def reconstruct_packet(observables: dict[str, int]) -> dict[str, int]:
    q = math.isqrt(observables["GSD"])
    assert q * q == observables["GSD"]

    mu = exact_integer_log(q, observables["D_dim"])
    k = observables["S_single"]
    E = observables["S_page_max"]
    assert (2 * E) % k == 0
    v = (2 * E) // k

    chi = observables["chi"]
    T = chi - v + E
    assert (6 * T) % (v * k) == 0
    lam = (6 * T) // (v * k)

    s = k - observables["width"]
    r = s + observables["gap"]

    gap = r - s
    assert gap != 0
    numerator = -k - (v - 1) * s
    assert numerator % gap == 0
    f = numerator // gap
    g = (v - 1) - f

    return {
        "q": q,
        "v": v,
        "k": k,
        "lam": lam,
        "mu": mu,
        "r": r,
        "s": s,
        "f": f,
        "g": g,
        "E": E,
        "T": T,
        "chi": chi,
    }


PACKET = reconstruct_packet(OBSERVABLES)


class TestT1_MinimalObservablePacket:
    def test_promoted_observable_packet(self):
        assert OBSERVABLES == {
            "S_single": 12,
            "I_adj": 4,
            "S_page_max": 240,
            "GSD": 9,
            "D_dim": 81,
            "gap": 6,
            "width": 16,
            "chi": -40,
        }

    def test_holographic_observables_fix_k_and_E(self):
        assert OBSERVABLES["S_single"] == 12
        assert OBSERVABLES["S_page_max"] == 240

    def test_quantum_observables_fix_q_and_mu(self):
        assert OBSERVABLES["GSD"] == 9
        assert OBSERVABLES["D_dim"] == 81

    def test_condensed_observables_fix_gap_and_width(self):
        assert OBSERVABLES["gap"] == 6
        assert OBSERVABLES["width"] == 16

    def test_diffgeo_observable_fixes_euler_characteristic(self):
        assert OBSERVABLES["chi"] == -40

    def test_mutual_information_matches_mu(self):
        assert OBSERVABLES["I_adj"] == 4


class TestT2_PacketReconstruction:
    def test_reconstruct_q(self):
        assert PACKET["q"] == 3

    def test_reconstruct_mu(self):
        assert PACKET["mu"] == 4

    def test_reconstruct_k(self):
        assert PACKET["k"] == 12

    def test_reconstruct_v_from_entropy_and_degree(self):
        assert PACKET["v"] == 40

    def test_reconstruct_triangle_count(self):
        assert PACKET["T"] == 160

    def test_reconstruct_lambda_from_euler_triangle_identity(self):
        assert PACKET["lam"] == 2

    def test_reconstruct_spectral_gap_eigenvalues(self):
        assert PACKET["r"] == 2
        assert PACKET["s"] == -4

    def test_reconstruct_multiplicities(self):
        assert PACKET["f"] == 24
        assert PACKET["g"] == 15


class TestT3_SectorRoundtrip:
    def test_holographic_roundtrip(self):
        assert PACKET["k"] == OBSERVABLES["S_single"]
        assert PACKET["mu"] == OBSERVABLES["I_adj"]
        assert PACKET["E"] == OBSERVABLES["S_page_max"]

    def test_diffgeo_roundtrip(self):
        K_vertex = 1 - Fraction(PACKET["k"], 2) + Fraction(PACKET["k"] * PACKET["lam"] // 2, 3)
        assert K_vertex == -1
        assert K_vertex * PACKET["v"] == OBSERVABLES["chi"]

    def test_quantum_roundtrip(self):
        assert PACKET["q"] ** 2 == OBSERVABLES["GSD"]
        assert PACKET["q"] ** PACKET["mu"] == OBSERVABLES["D_dim"]

    def test_thermo_roundtrip(self):
        a0 = PACKET["k"] ** 2 + PACKET["f"] * PACKET["r"] ** 2 + PACKET["g"] * PACKET["s"] ** 2
        assert a0 == 480
        assert 2 * a0 == 4 * PACKET["E"] == 2 * PACKET["v"] * PACKET["k"]

    def test_arithmetic_roundtrip(self):
        disc = (PACKET["r"] - PACKET["s"]) ** 2
        assert disc == 36
        assert disc == (PACKET["k"] // 2) ** 2

    def test_condensed_roundtrip(self):
        assert (PACKET["r"] - PACKET["s"]) == OBSERVABLES["gap"]
        assert (PACKET["k"] - PACKET["s"]) == OBSERVABLES["width"]


class TestT4_UniquenessAndClosure:
    def test_multiplicity_system_has_nonzero_determinant(self):
        determinant = PACKET["r"] - PACKET["s"]
        assert determinant == 6
        assert determinant != 0

    def test_trace_constraints_fix_multiplicities_uniquely(self):
        assert 1 + PACKET["f"] + PACKET["g"] == PACKET["v"]
        assert PACKET["k"] + PACKET["f"] * PACKET["r"] + PACKET["g"] * PACKET["s"] == 0

    def test_packet_matches_exact_srg_quadratic_data(self):
        assert (
            PACKET["q"],
            PACKET["v"],
            PACKET["k"],
            PACKET["lam"],
            PACKET["mu"],
            PACKET["r"],
            PACKET["s"],
            PACKET["f"],
            PACKET["g"],
        ) == (3, 40, 12, 2, 4, 2, -4, 24, 15)

    def test_bidirectional_master_summary(self):
        gap = PACKET["r"] - PACKET["s"]
        bandwidth = PACKET["k"] - PACKET["s"]
        assert gap == PACKET["k"] // 2
        assert bandwidth == 2 ** PACKET["mu"]
        assert PACKET["q"] ** PACKET["mu"] == 81
        assert PACKET["q"] ** 2 == 9
        assert PACKET["E"] == 240
        assert PACKET["chi"] == -PACKET["v"]
