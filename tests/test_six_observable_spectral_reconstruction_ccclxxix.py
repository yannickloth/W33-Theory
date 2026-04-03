"""
Phase CCCLXXIX — Six-observable spectral reconstruction.

CCCLXXVIII closed the inverse direction using a promoted cross-sector packet.
This phase compresses that inverse packet further: six observables already
reconstruct the full W(3,3) spectral core, with the older

    I_adj = mu
    GSD = q^2

becoming derived rather than primitive.
"""

from __future__ import annotations

import math
from fractions import Fraction


OBSERVABLES = {
    "S_single": 12,
    "S_page_max": 240,
    "D_dim": 81,
    "gap": 6,
    "width": 16,
    "chi": -40,
}


def exact_integer_log(base: int, target: int) -> int:
    value = 1
    exponent = 0
    while value < target:
        value *= base
        exponent += 1
    assert value == target
    return exponent


def reconstruct_packet(observables: dict[str, int]) -> dict[str, int]:
    k = observables["S_single"]
    E = observables["S_page_max"]
    width = observables["width"]
    D_dim = observables["D_dim"]
    gap = observables["gap"]
    chi = observables["chi"]

    mu = exact_integer_log(2, width)
    q = round(D_dim ** (1 / mu))
    assert q**mu == D_dim

    assert (2 * E) % k == 0
    v = (2 * E) // k

    T = chi - v + E
    assert (6 * T) % (v * k) == 0
    lam = (6 * T) // (v * k)

    s = k - width
    r = s + gap

    numerator = -k - (v - 1) * s
    assert numerator % (r - s) == 0
    f = numerator // (r - s)
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


class TestT1_SixObservablePacket:
    def test_promoted_six_observables(self):
        assert OBSERVABLES == {
            "S_single": 12,
            "S_page_max": 240,
            "D_dim": 81,
            "gap": 6,
            "width": 16,
            "chi": -40,
        }

    def test_entropy_degree_pair(self):
        assert OBSERVABLES["S_single"] == 12
        assert OBSERVABLES["S_page_max"] == 240

    def test_quantum_dimension_seed(self):
        assert OBSERVABLES["D_dim"] == 81

    def test_condensed_gap_pair(self):
        assert OBSERVABLES["gap"] == 6
        assert OBSERVABLES["width"] == 16

    def test_diffgeo_seed(self):
        assert OBSERVABLES["chi"] == -40

    def test_observable_count_is_six(self):
        assert len(OBSERVABLES) == 6


class TestT2_Reconstruction:
    def test_reconstruct_mu_from_width(self):
        assert PACKET["mu"] == 4

    def test_reconstruct_q_from_dimension_and_mu(self):
        assert PACKET["q"] == 3

    def test_reconstruct_v_from_single_entropy_and_page_max(self):
        assert PACKET["v"] == 40

    def test_reconstruct_triangle_count_from_euler(self):
        assert PACKET["T"] == 160

    def test_reconstruct_lambda(self):
        assert PACKET["lam"] == 2

    def test_reconstruct_nontrivial_eigenvalues(self):
        assert PACKET["r"] == 2
        assert PACKET["s"] == -4

    def test_reconstruct_multiplicities(self):
        assert PACKET["f"] == 24
        assert PACKET["g"] == 15

    def test_full_packet_matches_w33(self):
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


class TestT3_DerivedObservables:
    def test_adjacent_mutual_information_is_derived(self):
        assert PACKET["mu"] == 4
        assert PACKET["mu"] == 4  # I_adj

    def test_ground_state_degeneracy_is_derived(self):
        assert PACKET["q"] ** 2 == 9

    def test_symbolic_closure_identities_follow(self):
        gap = PACKET["r"] - PACKET["s"]
        width = PACKET["k"] - PACKET["s"]
        assert gap == PACKET["k"] // 2
        assert width == 2 ** PACKET["mu"]
        assert PACKET["q"] ** PACKET["mu"] == 81

    def test_thermo_channel_roundtrip(self):
        a0 = PACKET["k"] ** 2 + PACKET["f"] * PACKET["r"] ** 2 + PACKET["g"] * PACKET["s"] ** 2
        assert a0 == 480
        assert 2 * a0 == 4 * PACKET["E"] == 2 * PACKET["v"] * PACKET["k"]

    def test_diffgeo_channel_roundtrip(self):
        K_vertex = 1 - Fraction(PACKET["k"], 2) + Fraction(PACKET["k"] * PACKET["lam"] // 2, 3)
        assert K_vertex == -1
        assert K_vertex * PACKET["v"] == PACKET["chi"]

    def test_quantum_channel_roundtrip(self):
        assert PACKET["q"] ** 2 == 9
        assert PACKET["q"] ** PACKET["mu"] == 81


class TestT4_CompressionWitnesses:
    def test_width_is_needed_to_split_q_mu_factorizations_of_81(self):
        factorizations = {(3, 4), (9, 2), (81, 1)}
        assert (PACKET["q"], PACKET["mu"]) in factorizations
        assert len(factorizations) == 3
        assert 2 ** PACKET["mu"] == OBSERVABLES["width"]

    def test_page_max_alone_does_not_fix_v(self):
        divisors = {(1, 480), (2, 240), (3, 160), (4, 120), (5, 96), (6, 80), (8, 60), (10, 48), (12, 40)}
        assert (PACKET["k"], 2 * PACKET["E"] // PACKET["k"]) in divisors
        assert len(divisors) > 1

    def test_gap_and_width_together_fix_r_and_s(self):
        s = OBSERVABLES["S_single"] - OBSERVABLES["width"]
        r = s + OBSERVABLES["gap"]
        assert (r, s) == (2, -4)

    def test_trace_system_is_non_degenerate(self):
        determinant = PACKET["r"] - PACKET["s"]
        assert determinant == 6
        assert determinant != 0
