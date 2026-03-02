"""
Tests for Pillar 136 - AdS/CFT Holography & Bekenstein-Hawking Bridge
"""
import pytest

from THEORY_PART_CCXXXVI_ADS_CFT_HOLOGRAPHY import (
    ads_cft_basics, ads_dimensions,
    brown_henneaux, central_charge_24,
    witten_monster_gravity, extremal_cft,
    bekenstein_hawking, hawking_temperature,
    ryu_takayanagi, entanglement_and_spacetime,
    holographic_dictionary,
    complete_holographic_chain, the_grand_unification,
)


# -- AdS/CFT basics ------------------------------------------------

class TestAdSCFT:
    def test_is_duality(self):
        assert ads_cft_basics()['is_duality'] is True

    def test_year_1997(self):
        assert ads_cft_basics()['year'] == 1997

    def test_strong_weak(self):
        assert ads_cft_basics()['strong_weak'] is True

    def test_three_examples(self):
        assert len(ads_cft_basics()['examples']) == 3

    def test_citations(self):
        assert ads_cft_basics()['citations_by_2015'] >= 10000

    def test_ads3_total_10(self):
        assert ads_dimensions()['ads3']['total'] == 10

    def test_ads5_total_10(self):
        assert ads_dimensions()['ads5']['total'] == 10

    def test_ads4_total_11(self):
        assert ads_dimensions()['ads4']['total'] == 11


# -- Brown-Henneaux & c = 24 ---------------------------------------

class TestBrownHenneaux:
    def test_year_1986(self):
        assert brown_henneaux()['year'] == 1986

    def test_pre_maldacena(self):
        assert brown_henneaux()['pre_maldacena'] is True

    def test_monster_c_24(self):
        assert brown_henneaux()['monster_c'] == 24

    def test_virasoro_symmetry(self):
        bh = brown_henneaux()
        assert 'Virasoro' in bh['symmetry']

    def test_c24_value(self):
        assert central_charge_24()['value'] == 24

    def test_c24_eight_appearances(self):
        assert central_charge_24()['count'] == 8

    def test_c24_smallest_nontrivial(self):
        assert central_charge_24()['smallest_nontrivial'] is True

    def test_c24_modular_constraint(self):
        c24 = central_charge_24()
        assert 'c mod 24 = 0' in c24['modular_invariance_constraint']


# -- Witten Monster gravity ----------------------------------------

class TestWittenMonster:
    def test_central_charge_24(self):
        assert witten_monster_gravity()['central_charge'] == 24

    def test_j_is_partition(self):
        assert witten_monster_gravity()['j_is_partition'] is True

    def test_vacuum_degeneracy_1(self):
        assert witten_monster_gravity()['vacuum_degeneracy'] == 1

    def test_first_excited_196884(self):
        assert witten_monster_gravity()['first_excited'] == 196884

    def test_connection_to_e8(self):
        assert witten_monster_gravity()['connection_to_e8'] is True


# -- Extremal CFT --------------------------------------------------

class TestExtremalCFT:
    def test_v0_1(self):
        assert extremal_cft()['v0'] == 1

    def test_v1_0(self):
        assert extremal_cft()['v1'] == 0

    def test_v2_196884(self):
        assert extremal_cft()['v2'] == 196884

    def test_unique(self):
        assert extremal_cft()['unique'] is True

    def test_monster_symmetry(self):
        assert extremal_cft()['symmetry_group'] == 'Monster M'

    def test_threshold_2(self):
        assert extremal_cft()['threshold'] == 2


# -- Bekenstein-Hawking ---------------------------------------------

class TestBekensteinHawking:
    def test_area_scaling(self):
        assert bekenstein_hawking()['scales_with'] == 'area'

    def test_not_volume(self):
        assert bekenstein_hawking()['not_with'] == 'volume'

    def test_holographic_motivation(self):
        assert bekenstein_hawking()['holographic_motivation'] is True

    def test_monster_counting(self):
        assert bekenstein_hawking()['monster_counting'] is True

    def test_hawking_cardy(self):
        ht = hawking_temperature()
        assert ht['counts_microstates'] is True


# -- Ryu-Takayanagi & entanglement ---------------------------------

class TestRyuTakayanagi:
    def test_generalizes_bh(self):
        assert ryu_takayanagi()['generalizes'] == 'Bekenstein-Hawking'

    def test_year_2006(self):
        assert ryu_takayanagi()['year'] == 2006

    def test_er_epr(self):
        assert ryu_takayanagi()['er_epr'] is True

    def test_breakthrough_prize(self):
        assert ryu_takayanagi()['breakthrough_prize'] == 2015

    def test_entanglement_creates_geometry(self):
        assert entanglement_and_spacetime()['entanglement_creates_geometry'] is True

    def test_ads_cft_is_qec(self):
        assert entanglement_and_spacetime()['ads_cft_is_qec'] is True

    def test_holographic_codes(self):
        assert entanglement_and_spacetime()['holographic_codes'] is True


# -- Holographic dictionary ----------------------------------------

class TestHolographicDict:
    def test_10_entries(self):
        assert holographic_dictionary()['count'] == 10

    def test_is_bijection(self):
        assert holographic_dictionary()['is_bijection'] is True


# -- Chain and grand unification -----------------------------------

class TestChain:
    def test_chain_7_links(self):
        assert len(complete_holographic_chain()) == 7

    def test_chain_starts_w33(self):
        chain = complete_holographic_chain()
        assert chain[0][0] == 'W(3,3)'

    def test_chain_ends_qec(self):
        chain = complete_holographic_chain()
        assert chain[-1][1] == 'QEC'

    def test_grand_unification_pillars(self):
        gu = the_grand_unification()
        assert gu['total_pillars'] == 16

    def test_unifying_number_24(self):
        assert the_grand_unification()['unifying_number'] == 24

    def test_four_themes(self):
        gu = the_grand_unification()
        assert all(k in gu for k in ['mathematics', 'physics', 'geometry', 'information'])
