"""
Tests for Pillar 133 - The Griess Algebra & Monster Vertex Algebra V#
"""
import pytest

from THEORY_PART_CCXXXIII_GRIESS_ALGEBRA_VOA import (
    monster_order, monster_order_approx, monster_primes,
    supersingular_primes, griess_algebra, griess_dimension_factorization,
    j_monster_decomposition, verify_thompson_decomposition,
    v_natural, v_natural_no_currents, borcherds_proof_outline,
    moonshine_dimension_identity, happy_family,
    complete_chain_to_monster, verify_chain_numbers,
)


# ── Monster Group ──────────────────────────────────────────

class TestMonsterGroup:
    def test_order_magnitude(self):
        assert monster_order_approx() == 53

    def test_15_primes(self):
        _, exp = monster_order()
        assert len(exp) == 15

    def test_largest_prime_71(self):
        primes = monster_primes()
        assert max(primes) == 71

    def test_smallest_prime_2(self):
        primes = monster_primes()
        assert min(primes) == 2

    def test_supersingular_count(self):
        assert len(supersingular_primes()) == 15

    def test_supersingular_list(self):
        sp = supersingular_primes()
        assert sp == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 41, 47, 59, 71]


# ── Griess Algebra ─────────────────────────────────────────

class TestGriessAlgebra:
    def test_dimension(self):
        assert griess_algebra()['dimension'] == 196884

    def test_irrep(self):
        assert griess_algebra()['irrep_dimension'] == 196883

    def test_decomposition(self):
        ga = griess_algebra()
        assert ga['trivial_dimension'] + ga['irrep_dimension'] == 196884

    def test_commutative(self):
        assert griess_algebra()['commutative'] is True

    def test_non_associative(self):
        assert griess_algebra()['associative'] is False


# ── Dimension Factorization ───────────────────────────────

class TestDimensionFactorization:
    def test_196883_factors(self):
        gdf = griess_dimension_factorization()
        assert gdf['product'] == 196883
        assert gdf['factors'] == (47, 59, 71)

    def test_all_supersingular(self):
        gdf = griess_dimension_factorization()
        assert gdf['all_supersingular']

    def test_largest_three(self):
        gdf = griess_dimension_factorization()
        assert gdf['are_largest_three']


# ── Thompson Decomposition ────────────────────────────────

class TestThompsonDecomposition:
    def test_level_1(self):
        irreps, decomps = j_monster_decomposition()
        assert decomps[1]['j_coeff'] == 196884
        assert decomps[1]['sum'] == 196884

    def test_level_2(self):
        irreps, decomps = j_monster_decomposition()
        assert decomps[2]['j_coeff'] == 21493760
        assert decomps[2]['sum'] == 21493760

    def test_verify(self):
        results = verify_thompson_decomposition()
        for level, data in results.items():
            assert data['matches']


# ── V-Natural ─────────────────────────────────────────────

class TestVNatural:
    def test_central_charge(self):
        assert v_natural()['central_charge'] == 24

    def test_vacuum(self):
        assert v_natural()['graded_dims'][-1] == 1

    def test_no_weight_0(self):
        assert v_natural()['graded_dims'][0] == 0

    def test_no_currents(self):
        assert v_natural()['graded_dims'][1] == 0

    def test_griess_level(self):
        assert v_natural()['graded_dims'][2] == 196884

    def test_level_3(self):
        assert v_natural()['graded_dims'][3] == 21493760


class TestNoCurrents:
    def test_dim_v1_zero(self):
        vnc = v_natural_no_currents()
        assert vnc['dim_V1'] == 0


# ── Borcherds ─────────────────────────────────────────────

class TestBorcherds:
    def test_year(self):
        bp = borcherds_proof_outline()
        assert bp['year'] == 1992

    def test_fields_medal(self):
        bp = borcherds_proof_outline()
        assert 'Fields Medal' in bp['awarded']

    def test_string_theory(self):
        bp = borcherds_proof_outline()
        assert bp['string_theory_used']


# ── Dimension Identities ─────────────────────────────────

class TestDimensionIdentities:
    def test_196884_leech(self):
        assert 196560 + 324 == 196884

    def test_324_decomposition(self):
        assert 4 * 81 == 324

    def test_81_is_3_to_4(self):
        assert 3**4 == 81

    def test_196883_from_leech(self):
        assert 196560 + 323 == 196883

    def test_323_factorization(self):
        assert 17 * 19 == 323

    def test_323_supersingular(self):
        sp = supersingular_primes()
        assert 17 in sp and 19 in sp


# ── Happy Family ──────────────────────────────────────────

class TestHappyFamily:
    def test_count(self):
        hf = happy_family()
        assert hf['happy_family'] == 20

    def test_pariahs(self):
        hf = happy_family()
        assert hf['pariahs'] == 6

    def test_total(self):
        hf = happy_family()
        assert hf['total_sporadic'] == 26

    def test_first_gen(self):
        hf = happy_family()
        assert len(hf['first_generation']) == 5
        assert 'M_24' in hf['first_generation']


# ── Complete Chain ────────────────────────────────────────

class TestCompleteChain:
    def test_five_links(self):
        chain = complete_chain_to_monster()
        assert len(chain) == 5

    def test_starts_w33(self):
        chain = complete_chain_to_monster()
        assert chain[0][0] == 'W(3,3)'

    def test_ends_monster(self):
        chain = complete_chain_to_monster()
        assert chain[-1][1] == 'Monster'

    def test_chain_numbers(self):
        nums = verify_chain_numbers()
        assert all(nums.values())
