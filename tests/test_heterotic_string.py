"""
Tests for Pillar 127 - Heterotic String Partition Function: E8xE8 and 496
"""
import pytest
from math import comb

from THEORY_PART_CCXXVII_HETEROTIC_STRING import (
    dim_e8, dim_e8_times_e8, dim_so, roots_e8, roots_e8_times_e8,
    roots_d16, is_perfect, perfect_number_form, sigma_k,
    eisenstein_e4, eisenstein_e8_weight8, e4_squared, multiply_series,
    delta_coefficients, ramanujan_tau, even_unimodular_counts,
    e8_to_e6_su3_branching, standard_model_dim, critical_dimensions,
    partition_function_series,
)


# ── Gauge Group Dimensions ───────────────────────────────────

class TestGaugeDimensions:
    def test_dim_e8(self):
        assert dim_e8() == 248

    def test_dim_e8_times_e8(self):
        assert dim_e8_times_e8() == 496

    def test_dim_so32(self):
        assert dim_so(32) == 496

    def test_roots_e8(self):
        assert roots_e8() == 240

    def test_roots_e8e8(self):
        assert roots_e8_times_e8() == 480

    def test_roots_d16(self):
        assert roots_d16() == 480

    def test_248_eq_240_plus_8(self):
        assert dim_e8() == roots_e8() + 8


# ── Perfect Number ───────────────────────────────────────────

class TestPerfectNumber:
    def test_496_perfect(self):
        ok, _ = is_perfect(496)
        assert ok

    def test_6_perfect(self):
        ok, _ = is_perfect(6)
        assert ok

    def test_28_perfect(self):
        ok, _ = is_perfect(28)
        assert ok

    def test_euclid_euler_form(self):
        ok, p, mersenne = perfect_number_form(496)
        assert ok
        assert p == 5
        assert mersenne == 31


# ── Modular Forms ────────────────────────────────────────────

class TestModularForms:
    def test_e4_squared_eq_e8(self):
        e4sq = e4_squared(8)
        e8 = eisenstein_e8_weight8(8)
        assert e4sq == e8

    def test_e8_480(self):
        e8 = eisenstein_e8_weight8(5)
        assert e8[1] == 480

    def test_e8_61920(self):
        e8 = eisenstein_e8_weight8(5)
        assert e8[2] == 61920

    def test_sigma7_values(self):
        assert sigma_k(1, 7) == 1
        assert sigma_k(2, 7) == 129
        assert sigma_k(3, 7) == 2188


# ── Ramanujan Tau ────────────────────────────────────────────

class TestRamanujanTau:
    def test_tau_1(self):
        tau = ramanujan_tau(5)
        assert tau[0] == 1

    def test_tau_2(self):
        tau = ramanujan_tau(5)
        assert tau[1] == -24

    def test_tau_3(self):
        tau = ramanujan_tau(5)
        assert tau[2] == 252

    def test_tau_2_hurwitz(self):
        """tau(2) = -24 = -|Hurwitz units|."""
        tau = ramanujan_tau(5)
        assert abs(tau[1]) == 24

    def test_full_tau(self):
        tau = ramanujan_tau(8)
        expected = [1, -24, 252, -1472, 4830, -6048, -16744, 84480]
        assert tau == expected


# ── Even Unimodular Lattices ─────────────────────────────────

class TestLattices:
    def test_dim_8(self):
        assert even_unimodular_counts()[8] == 1

    def test_dim_16(self):
        assert even_unimodular_counts()[16] == 2

    def test_dim_24(self):
        assert even_unimodular_counts()[24] == 24


# ── E8 Branching ─────────────────────────────────────────────

class TestBranching:
    def test_total_dim(self):
        reps = e8_to_e6_su3_branching()
        assert sum(r[3] for r in reps) == 248

    def test_four_representations(self):
        assert len(e8_to_e6_su3_branching()) == 4

    def test_27_triplet(self):
        """The (27,3) gives 3 generations of 27-plets."""
        reps = e8_to_e6_su3_branching()
        found = any(r[1] == 27 and r[2] == 3 for r in reps)
        assert found

    def test_standard_model_dim(self):
        assert standard_model_dim() == 12


# ── Critical Dimensions ──────────────────────────────────────

class TestCriticalDims:
    def test_bosonic(self):
        assert critical_dimensions()['bosonic'] == 26

    def test_superstring(self):
        assert critical_dimensions()['superstring'] == 10

    def test_compactification(self):
        cd = critical_dimensions()
        assert cd['bosonic'] - cd['superstring'] == 16

    def test_16_eq_rank(self):
        """16 = rank(E8 x E8) = compactification dimension."""
        assert 16 == 8 + 8


# ── W(3,3) Chain ─────────────────────────────────────────────

class TestW33Chain:
    def test_240_edges(self):
        assert roots_e8() == 240

    def test_480_double(self):
        assert roots_e8_times_e8() == 2 * 240

    def test_496_total(self):
        assert dim_e8_times_e8() == 480 + 16

    def test_12_regularity(self):
        assert standard_model_dim() == 12

    def test_moonshine_equation(self):
        assert 196884 == 196560 + 4 * 81

    def test_partition_function(self):
        pf = partition_function_series(3)
        assert int(round(pf[0])) == 1
