"""
Tests for Pillar 125 - The Binary Golay Code: M_24, Steiner Systems, 759 Octads
"""
import pytest
import numpy as np
from math import comb, factorial
from collections import Counter

from THEORY_PART_CCXXV_BINARY_GOLAY_CODE import (
    golay_parity_matrix, golay_generator_matrix, enumerate_codewords,
    weight_distribution, extract_octads, point_frequency,
    pair_frequency_sample, triple_frequency_sample, five_subset_coverage,
    octad_intersections, m24_order, m24_factorization, verify_m24_order,
    co0_order, hexacode_properties, leech_packing_density, w33_connections,
)


# ── fixtures ──────────────────────────────────────────────────

@pytest.fixture(scope="module")
def generator():
    return golay_generator_matrix()


@pytest.fixture(scope="module")
def codewords(generator):
    return enumerate_codewords(generator)


@pytest.fixture(scope="module")
def dist(codewords):
    return weight_distribution(codewords)


@pytest.fixture(scope="module")
def octads(codewords):
    return extract_octads(codewords)


# ── Generator Matrix ─────────────────────────────────────────

class TestGeneratorMatrix:
    def test_shape(self, generator):
        assert generator.shape == (12, 24)

    def test_rank(self, generator):
        assert np.linalg.matrix_rank(generator.astype(float)) == 12

    def test_identity_block(self, generator):
        assert np.array_equal(generator[:, :12], np.eye(12, dtype=int))

    def test_binary(self, generator):
        assert set(np.unique(generator)).issubset({0, 1})

    def test_self_dual(self, generator):
        GGT = generator @ generator.T % 2
        assert np.all(GGT == 0)


# ── Code Properties ──────────────────────────────────────────

class TestCodeProperties:
    def test_total_codewords(self, codewords):
        assert len(codewords) == 4096

    def test_total_is_power_of_2(self):
        assert 2**12 == 4096

    def test_weight_A0(self, dist):
        assert dist[0] == 1

    def test_weight_A8(self, dist):
        assert dist[8] == 759

    def test_weight_A12(self, dist):
        assert dist[12] == 2576

    def test_weight_A16(self, dist):
        assert dist[16] == 759

    def test_weight_A24(self, dist):
        assert dist[24] == 1

    def test_only_even_weights(self, dist):
        for w in dist:
            assert w % 4 == 0, f"Weight {w} not divisible by 4 (doubly-even)"

    def test_min_distance(self, dist):
        nonzero = [w for w in dist if w > 0]
        assert min(nonzero) == 8

    def test_weight_sum(self, dist):
        assert sum(dist.values()) == 4096


# ── Octads and Steiner System ────────────────────────────────

class TestOctads:
    def test_count_759(self, octads):
        assert len(octads) == 759

    def test_octad_size(self, octads):
        for oc in octads:
            assert len(oc) == 8

    def test_five_subset_steiner(self, octads):
        coverage = five_subset_coverage(octads, num_samples=100)
        assert all(c == 1 for c in coverage)

    def test_point_frequency_253(self, octads):
        freq = point_frequency(octads)
        assert all(f == 253 for f in freq)

    def test_pair_frequency_77(self, octads):
        counts = pair_frequency_sample(octads, num_samples=100)
        assert all(c == 77 for c in counts)

    def test_triple_frequency_21(self, octads):
        counts = triple_frequency_sample(octads, num_samples=100)
        assert all(c == 21 for c in counts)

    def test_intersections_valid(self, octads):
        inters = octad_intersections(octads, num_pairs=500)
        assert all(i in {0, 2, 4, 8} for i in inters)


# ── Numerology ───────────────────────────────────────────────

class TestNumerology:
    def test_253_binomial(self):
        assert comb(23, 2) == 253

    def test_253_so23(self):
        assert 23 * 22 // 2 == 253

    def test_759_eq_3_times_253(self):
        assert 759 == 3 * 253

    def test_77_eq_7_times_11(self):
        assert 77 == 7 * 11

    def test_21_fano(self):
        assert 21 == comb(7, 2)

    def test_24_three_octonions(self):
        assert 24 == 3 * 8

    def test_steiner_formula(self):
        # S(5,8,24): b = C(24,5)/C(8,5) = 42504/56 = 759
        assert comb(24, 5) // comb(8, 5) == 759


# ── M_24 ─────────────────────────────────────────────────────

class TestM24:
    def test_order(self):
        assert m24_order() == 244823040

    def test_factorization(self):
        ok, product = verify_m24_order()
        assert ok
        assert product == 244823040

    def test_divides_co0(self):
        assert co0_order() % m24_order() == 0

    def test_prime_factors(self):
        f = m24_factorization()
        assert set(f.keys()) == {2, 3, 5, 7, 11, 23}
        assert f[2] == 10 and f[3] == 3


# ── Hexacode ─────────────────────────────────────────────────

class TestHexacode:
    def test_codewords_64(self):
        h = hexacode_properties()
        assert h['num_codewords'] == 64

    def test_mog_24(self):
        h = hexacode_properties()
        assert h['mog_total'] == 24

    def test_min_distance(self):
        h = hexacode_properties()
        assert h['min_distance'] == 4


# ── Packing Density ──────────────────────────────────────────

class TestPacking:
    def test_12_factorial(self):
        assert factorial(12) == 479001600

    def test_density_value(self):
        delta, _, _ = leech_packing_density()
        assert abs(delta - 0.001930) < 0.001


# ── W(3,3) Connections ───────────────────────────────────────

class TestW33:
    def test_all_connections(self):
        conns = w33_connections()
        for desc, val in conns.items():
            assert val, f"Failed: {desc}"
