"""
Tests for Pillar 137 — The Sporadic Landscape: 26 Exceptions & Happy Family
"""
import pytest

from THEORY_PART_CCXXXVII_SPORADIC_LANDSCAPE import (
    sporadic_groups, happy_family, pariah_groups,
    mckay_e8_observation, thompson_e8_miracle,
    m24_golay_connection, number_24_in_sporadics,
    monster_order_primes, classification_theorem,
    monster_centralizer_chain, complete_chain_w33_to_sporadics,
)


# -- Sporadic groups catalogue ------------------------------------------

class TestSporadicGroups:
    def test_total_26(self):
        assert sporadic_groups()['total'] == 26

    def test_groups_list_length(self):
        assert len(sporadic_groups()['groups']) == 26

    def test_happy_family_count(self):
        assert len(sporadic_groups()['happy_family']) == 20

    def test_pariah_count(self):
        assert len(sporadic_groups()['pariahs']) == 6

    def test_classification_year(self):
        assert sporadic_groups()['classification_year'] == 2004

    def test_monster_is_largest(self):
        groups = sporadic_groups()['groups']
        monster = [g for g in groups if g['name'] == 'M'][0]
        assert monster['order_approx'] == max(g['order_approx'] for g in groups)

    def test_monster_min_rep(self):
        groups = sporadic_groups()['groups']
        monster = [g for g in groups if g['name'] == 'M'][0]
        assert monster['min_rep'] == 196883

    def test_j1_smallest_pariah(self):
        pariahs = sporadic_groups()['pariahs']
        j1 = [g for g in pariahs if g['name'] == 'J1'][0]
        assert j1['order_approx'] == 175560


# -- Happy Family -------------------------------------------------------

class TestHappyFamily:
    def test_size_20(self):
        assert happy_family()['size'] == 20

    def test_gen1_mathieu(self):
        assert happy_family()['generation_1']['count'] == 5

    def test_gen2_leech(self):
        assert happy_family()['generation_2']['count'] == 7

    def test_gen3_monster(self):
        assert happy_family()['generation_3']['count'] == 8

    def test_sum_generations(self):
        hf = happy_family()
        assert hf['count_check'] == 20

    def test_all_in_monster(self):
        assert happy_family()['all_in_monster'] is True

    def test_gen1_name(self):
        assert happy_family()['generation_1']['name'] == 'Mathieu groups'


# -- Pariahs ------------------------------------------------------------

class TestPariahs:
    def test_count(self):
        assert pariah_groups()['count'] == 6

    def test_not_in_monster(self):
        assert pariah_groups()['not_in_monster'] is True

    def test_smallest(self):
        assert pariah_groups()['smallest'] == 'J1'

    def test_largest(self):
        assert pariah_groups()['largest'] == 'J4'

    def test_janko_count(self):
        assert pariah_groups()['janko_count'] == 3


# -- McKay E_8 observation ----------------------------------------------

class TestMcKay:
    def test_node_count(self):
        assert mckay_e8_observation()['node_count'] == 9

    def test_coeff_sum(self):
        assert mckay_e8_observation()['coefficient_sum'] == 30

    def test_e8_dim(self):
        assert mckay_e8_observation()['e8_dimension'] == 248

    def test_year(self):
        assert mckay_e8_observation()['year'] == 1980


# -- Thompson E_8 miracle -----------------------------------------------

class TestThompson:
    def test_min_rep(self):
        assert thompson_e8_miracle()['min_rep_dim'] == 248

    def test_match(self):
        assert thompson_e8_miracle()['match'] is True

    def test_field_f3(self):
        assert thompson_e8_miracle()['field'] == 'F_3'


# -- M_24 / Golay -------------------------------------------------------

class TestM24Golay:
    def test_acts_on_24(self):
        assert m24_golay_connection()['acts_on'] == 24

    def test_is_aut_golay(self):
        assert m24_golay_connection()['is_aut_golay'] is True

    def test_5_transitive(self):
        assert m24_golay_connection()['transitivity'] == 5

    def test_octads(self):
        assert m24_golay_connection()['octads'] == 759


# -- Number 24 everywhere -----------------------------------------------

class TestNumber24:
    def test_count_ge_10(self):
        assert number_24_in_sporadics()['count'] >= 10

    def test_all_24(self):
        assert number_24_in_sporadics()['all_24'] is True

    def test_co1_choose(self):
        assert number_24_in_sporadics()['co1_rep_is_24_choose_2'] is True


# -- Monster primes -----------------------------------------------------

class TestMonsterPrimes:
    def test_prime_count(self):
        assert monster_order_primes()['prime_count'] == 15

    def test_supersingular_match(self):
        assert monster_order_primes()['match_supersingular'] is True

    def test_ogg_year(self):
        assert monster_order_primes()['ogg_year'] == 1975

    def test_largest_prime(self):
        assert monster_order_primes()['largest_prime'] == 71


# -- CFSG ---------------------------------------------------------------

class TestCFSG:
    def test_categories(self):
        assert classification_theorem()['categories'] == 4

    def test_sporadic_count(self):
        assert classification_theorem()['sporadic_count'] == 26

    def test_completion(self):
        assert classification_theorem()['completion_year'] == 2004

    def test_infinite_families(self):
        assert classification_theorem()['infinite_families'] == 18


# -- Centralizer chain --------------------------------------------------

class TestCentralizer:
    def test_count(self):
        assert monster_centralizer_chain()['count'] == 6

    def test_baby_monster(self):
        cs = monster_centralizer_chain()['centralizers']
        assert any(c['involves'] == 'B' for c in cs)


# -- Chain ---------------------------------------------------------------

class TestChain:
    def test_length(self):
        assert len(complete_chain_w33_to_sporadics()) == 6

    def test_starts_w33(self):
        assert complete_chain_w33_to_sporadics()[0][0] == 'W(3,3)'

    def test_ends_sporadics(self):
        assert 'Sporadic' in complete_chain_w33_to_sporadics()[-1][1]
