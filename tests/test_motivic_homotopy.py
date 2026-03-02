"""
Tests for Pillar 154: Motivic Homotopy Theory
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))

from THEORY_PART_CCLIV_MOTIVIC_HOMOTOPY import (
    a1_homotopy_category,
    motivic_spheres,
    milnor_conjecture,
    bloch_kato,
    motivic_cohomology,
    stable_motivic,
    motivic_steenrod,
    mixed_motives,
    a1_enumerative,
    voevodsky_legacy,
    motivic_e8,
    complete_chain,
    run_all_checks,
)


class TestA1HomotopyCategory:
    def test_authors(self):
        r = a1_homotopy_category()
        assert 'Morel' in r['authors'][0]
        assert 'Voevodsky' in r['authors'][1]

    def test_year(self):
        assert a1_homotopy_category()['year'] == 1999

    def test_construction_topology(self):
        c = a1_homotopy_category()['construction']
        assert 'Nisnevich' in c['topology']

    def test_a1_contractible(self):
        c = a1_homotopy_category()['construction']
        assert 'A^1' in c['localization']

    def test_key_analogy(self):
        k = a1_homotopy_category()['key_analogy']
        assert '[0,1]' in k['topology']
        assert 'A^1' in k['algebraic']


class TestMotivicSpheres:
    def test_two_spheres(self):
        ms = motivic_spheres()
        assert 'simplicial' in ms['two_spheres']
        assert 'algebraic' in ms['two_spheres']

    def test_gm(self):
        ms = motivic_spheres()
        assert 'G_m' in ms['two_spheres']['algebraic']['notation']

    def test_bigraded(self):
        ms = motivic_spheres()
        assert 'p,q' in ms['bigraded']['sphere']

    def test_classical_recovery(self):
        ms = motivic_spheres()
        assert 'q=0' in ms['bigraded']['classical']

    def test_eta_rho(self):
        ms = motivic_spheres()
        assert 'eta' in ms['significance']['new_phenomena']
        assert 'rho' in ms['significance']['new_phenomena']


class TestMilnorConjecture:
    def test_proved_by(self):
        mc = milnor_conjecture()
        assert 'Voevodsky' in mc['proved_by']

    def test_year(self):
        mc = milnor_conjecture()
        assert mc['year_proved'] == 1996

    def test_fields(self):
        assert milnor_conjecture()['fields_medal'] == 2002

    def test_statement(self):
        s = milnor_conjecture()['statement']
        assert 'K_n^M' in s['precise']
        assert 'isomorphism' in s['precise']

    def test_proof_ingredients(self):
        pi = milnor_conjecture()['proof_ingredients']
        assert 'Steenrod' in pi['steenrod_operations']


class TestBlochKato:
    def test_proved_year(self):
        assert bloch_kato()['year_proved'] == 2011

    def test_rost(self):
        bk = bloch_kato()
        assert 'Rost' in bk['proof']['rost_part']

    def test_general_primes(self):
        s = bloch_kato()['statement']
        assert 'prime' in s['general_l'].lower() or 'l' in s['general_l']

    def test_consequences(self):
        c = bloch_kato()['consequences']
        assert len(c) >= 3


class TestMotivicCohomology:
    def test_chow_groups(self):
        mc = motivic_cohomology()
        assert 'CH^q' in mc['connections']['chow_groups']

    def test_bigraded(self):
        mc = motivic_cohomology()
        assert 'p,q' in mc['definition']['bigraded']

    def test_realizations(self):
        mm = mixed_motives()
        r = mm['fundamental']['realizations']
        assert 'betti' in r
        assert 'de_rham' in r


class TestStableMotivic:
    def test_notation(self):
        assert stable_motivic()['notation'] == 'SH(S)'

    def test_spectra(self):
        ks = stable_motivic()['key_spectra']
        assert 'kgl' in ks
        assert 'mgl' in ks

    def test_bachmann(self):
        b = stable_motivic()['bachmann']
        assert b['year'] == 2018
        assert 'SH' in b['theorem']


class TestMotivicSteenrod:
    def test_operations(self):
        ms = motivic_steenrod()
        assert 'Sq^i' in ms['operations']['sq']

    def test_voevodsky(self):
        ms = motivic_steenrod()
        assert 'Voevodsky' in ms['voevodsky_construction']['author']


class TestMixedMotives:
    def test_grothendieck(self):
        mm = mixed_motives()
        assert 'Grothendieck' in mm['history']['grothendieck']

    def test_tate_motives(self):
        mm = mixed_motives()
        assert 'Z(n)' in mm['fundamental']['tate_motives']


class TestA1Enumerative:
    def test_27_lines(self):
        ae = a1_enumerative()
        assert '27' in ae['example']['lines_on_cubic']['classical']

    def test_quadratic_form(self):
        ae = a1_enumerative()
        assert 'quadratic form' in ae['key_idea']['quadratic_form']

    def test_w33_connection(self):
        ae = a1_enumerative()
        assert 'W(E6)' in ae['example']['lines_on_cubic']['w33_connection']


class TestVoevodskyLegacy:
    def test_fields(self):
        assert voevodsky_legacy()['fields_medal'] == 2002

    def test_death(self):
        assert voevodsky_legacy()['died'] == 2017

    def test_two_revolutions(self):
        vl = voevodsky_legacy()
        assert 'homotopy' in vl['two_revolutions']['revolution_1'].lower()
        assert 'foundations' in vl['two_revolutions']['revolution_2'].lower()

    def test_contributions(self):
        c = voevodsky_legacy()['contributions']
        assert len(c) >= 5


class TestMotivicE8:
    def test_w33_chain(self):
        me = motivic_e8()
        assert any('W(3,3)' in p for p in me['w33_chain']['path'])

    def test_gw(self):
        me = motivic_e8()
        assert any('GW' in p for p in me['w33_chain']['path'])


class TestCompleteChain:
    def test_chain_length(self):
        ch = complete_chain()
        assert len(ch['links']) == 6

    def test_miracle(self):
        ch = complete_chain()
        assert 'ALGEBRAIC TOPOLOGY' in ch['miracle']['statement']

    def test_chain_starts_w33(self):
        ch = complete_chain()
        assert ch['links'][0]['from'] == 'W(3,3)'


class TestRunAllChecks:
    def test_all_pass(self):
        assert run_all_checks() is True
