"""
Tests for Pillar 157: Arithmetic Topology
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))

from THEORY_PART_CCLVII_ARITHMETIC_TOPOLOGY import (
    fundamental_dictionary,
    primes_as_knots,
    borromean_primes,
    history,
    alexander_iwasawa,
    etale_fundamental,
    tqft_langlands,
    spec_z,
    ramification_branching,
    deninger_dynamics,
    arithmetic_topology_e8,
    complete_chain,
    run_all_checks,
)


class TestFundamentalDictionary:
    def test_q_s3(self):
        fd = fundamental_dictionary()
        assert fd['analogies']['rationals']['topology'] == 'S^3 (3-sphere)'

    def test_prime_knot(self):
        fd = fundamental_dictionary()
        assert 'Knot' in fd['analogies']['prime']['topology']

    def test_galois(self):
        fd = fundamental_dictionary()
        assert 'Galois' in fd['deeper_analogies']['galois']['arithmetic']

    def test_class_field(self):
        fd = fundamental_dictionary()
        assert 'Class field' in fd['deeper_analogies']['class_field']['arithmetic']


class TestPrimesAsKnots:
    def test_mazur(self):
        pk = primes_as_knots()
        assert pk['mazur']['author'] == 'Barry Mazur'
        assert pk['mazur']['year'] == 1964

    def test_legendre_linking(self):
        pk = primes_as_knots()
        assert 'linking' in pk['legendre_as_linking']['linking'].lower()


class TestBorromeanPrimes:
    def test_primes(self):
        bp = borromean_primes()
        assert bp['prime_triple']['primes'] == [13, 61, 937]

    def test_pairwise_unlinked(self):
        bp = borromean_primes()
        assert bp['verification']['leg_13_61'] == 1
        assert bp['verification']['leg_13_937'] == 1
        assert bp['verification']['leg_61_937'] == 1

    def test_redei(self):
        bp = borromean_primes()
        assert '-1' in bp['prime_triple']['triple']


class TestHistory:
    def test_mumford(self):
        h = history()
        assert 'Mumford' in h['pioneers']['mumford_manin_1960s']

    def test_morishita(self):
        h = history()
        assert 'Morishita' in h['modern']['morishita_2011']


class TestAlexanderIwasawa:
    def test_alexander(self):
        ai = alexander_iwasawa()
        assert 'Alexander' in ai['analogy']['knot_side']['invariant']

    def test_iwasawa(self):
        ai = alexander_iwasawa()
        assert 'Iwasawa' in ai['analogy']['number_side']['invariant']


class TestEtaleFundamental:
    def test_galois(self):
        ef = etale_fundamental()
        assert 'Galois' in ef['definition']['analogy']

    def test_class_number(self):
        ef = etale_fundamental()
        assert 'Class number' in ef['class_field_as_covering']['class_number']


class TestTQFTLanglands:
    def test_kapranov(self):
        tl = tqft_langlands()
        assert 'Kapranov' in tl['kapranov']['paper']

    def test_chern_simons(self):
        tl = tqft_langlands()
        assert 'Chern-Simons' in tl['chern_simons']['topology']


class TestSpecZ:
    def test_cd3(self):
        sz = spec_z()
        assert '3' in sz['cohomological_dimension']['fact']

    def test_poincare(self):
        sz = spec_z()
        assert 'Poincare' in sz['cohomological_dimension']['poincare']


class TestRamification:
    def test_branching(self):
        rb = ramification_branching()
        assert 'branch' in rb['analogy']['branched'].lower()


class TestDeninger:
    def test_year(self):
        assert deninger_dynamics()['year'] == 2002

    def test_closed_orbits(self):
        dd = deninger_dynamics()
        assert 'primes' in dd['idea']['closed_orbits'].lower()


class TestE8Connection:
    def test_w33(self):
        ae = arithmetic_topology_e8()
        assert any('W(3,3)' in p for p in ae['w33_chain']['path'])

    def test_legendre(self):
        ae = arithmetic_topology_e8()
        assert any('Legendre' in p for p in ae['w33_chain']['path'])


class TestCompleteChain:
    def test_length(self):
        assert len(complete_chain()['links']) == 6

    def test_miracle(self):
        assert 'PRIMES ARE KNOTS' in complete_chain()['miracle']['statement']

    def test_starts_w33(self):
        assert complete_chain()['links'][0]['from'] == 'W(3,3)'


class TestRunAllChecks:
    def test_all_pass(self):
        assert run_all_checks() is True
