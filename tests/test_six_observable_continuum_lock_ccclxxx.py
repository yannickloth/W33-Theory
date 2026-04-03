"""
Phase CCCLXXX — Six-observable continuum coefficient lock.

CCCLXXIX showed that six promoted observables already reconstruct the full
W(3,3) spectral packet. This phase pushes that compression into the
continuum-facing coefficient package: the same six-observable shell already
fixes the promoted continuum / spectral-action coefficients and Higgs ratio.
"""

from __future__ import annotations

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
    D_dim = observables["D_dim"]
    gap = observables["gap"]
    width = observables["width"]
    chi = observables["chi"]

    mu = exact_integer_log(2, width)
    q = round(D_dim ** (1 / mu))
    assert q**mu == D_dim

    v = (2 * E) // k
    T = chi - v + E
    lam = (6 * T) // (v * k)
    s = k - width
    r = s + gap
    f = (-k - (v - 1) * s) // (r - s)
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
    }


PACKET = reconstruct_packet(OBSERVABLES)

PHI3 = PACKET["k"] + 1
PHI6 = 1 + (PACKET["r"] - PACKET["s"])
X = Fraction(PACKET["q"], PHI3)

A0 = PACKET["k"] ** 2 + PACKET["f"] * PACKET["r"] ** 2 + PACKET["g"] * PACKET["s"] ** 2
C_EH = Fraction(2, PACKET["q"]) * A0
A2 = PHI6 * C_EH
A4 = (Fraction(8, 1) / X + 2) * A0
C6 = PACKET["q"] * PHI3 * C_EH
HIGGS_RATIO = Fraction(2, 1) * (1 - 2 * X) / (4 + X)


class TestT1_CyclotomicDataFromSixObservables:
    def test_reconstruct_packet(self):
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

    def test_phi3_is_k_plus_one(self):
        assert PHI3 == 13

    def test_phi6_is_one_plus_gap(self):
        assert PHI6 == 7

    def test_weinberg_generator_from_six_observables(self):
        assert X == Fraction(3, 13)

    def test_weinberg_generator_is_q_over_phi3(self):
        assert X == Fraction(PACKET["q"], PHI3)


class TestT2_ContinuumCoefficientLock:
    def test_a0_from_packet(self):
        assert A0 == 480

    def test_continuum_eh_coefficient(self):
        assert C_EH == 320

    def test_a2_coefficient(self):
        assert A2 == 2240

    def test_a4_coefficient(self):
        assert A4 == 17600

    def test_c6_coefficient(self):
        assert C6 == 12480

    def test_all_continuum_coefficients_are_integers(self):
        assert all(value.denominator == 1 for value in (Fraction(A0), C_EH, A2, A4, C6))


class TestT3_RatioTower:
    def test_ceh_over_a0(self):
        assert C_EH / A0 == Fraction(2, 3)

    def test_a2_over_a0(self):
        assert A2 / A0 == Fraction(14, 3)

    def test_a4_over_a0(self):
        assert A4 / A0 == Fraction(110, 3)

    def test_c6_over_a0(self):
        assert C6 / A0 == 26

    def test_c6_over_ceh(self):
        assert C6 / C_EH == 39

    def test_a2_over_ceh(self):
        assert A2 / C_EH == 7


class TestT4_HiggsAndBridgeClosure:
    def test_higgs_ratio_square(self):
        assert HIGGS_RATIO == Fraction(14, 55)

    def test_higgs_ratio_matches_phi6_formula(self):
        assert HIGGS_RATIO == Fraction(2 * PHI6, 4 * PHI3 + PACKET["q"])

    def test_gap_width_package_feeds_continuum_coefficients(self):
        assert PHI6 == 1 + OBSERVABLES["gap"]
        assert 2 ** PACKET["mu"] == OBSERVABLES["width"]

    def test_entropy_dimension_package_feeds_continuum_coefficients(self):
        assert PACKET["q"] ** PACKET["mu"] == OBSERVABLES["D_dim"]
        assert PACKET["E"] == OBSERVABLES["S_page_max"]

    def test_continuum_package_is_generated_by_x(self):
        assert Fraction(2, 1) / X - 4 == Fraction(14, 3)
        assert Fraction(8, 1) / X + 2 == Fraction(110, 3)
        assert Fraction(6, 1) / X == 26

    def test_continuum_side_is_coefficient_complete(self):
        assert (A0, C_EH, A2, A4, C6, HIGGS_RATIO) == (
            480,
            320,
            2240,
            17600,
            12480,
            Fraction(14, 55),
        )
