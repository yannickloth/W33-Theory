"""
Tests for Pillar 156: Higher Algebra — Operads & E_n Structures
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))

from THEORY_PART_CCLVI_HIGHER_ALGEBRA import (
    operads,
    little_disks,
    en_algebras,
    a_infinity,
    factorization_algebras,
    lurie_higher_algebra,
    deformation_quantization,
    koszul_duality,
    structured_ring_spectra,
    grothendieck_teichmuller,
    higher_algebra_e8,
    complete_chain,
    run_all_checks,
)


class TestOperads:
    def test_may(self):
        assert '1972' in operads()['history']['may']

    def test_koszul_dual(self):
        assert 'Koszul dual' in operads()['key_examples']['koszul_duality']

    def test_examples(self):
        ex = operads()['key_examples']
        assert 'associative' in ex['associative'].lower()
        assert 'Lie' in ex['lie']


class TestLittleDisks:
    def test_name(self):
        assert 'E_n' in little_disks()['name']

    def test_recognition(self):
        assert 'loop space' in little_disks()['recognition']['statement'].lower()

    def test_hierarchy(self):
        h = little_disks()['hierarchy']
        assert 'A-infinity' in h['E_1']
        assert 'commutative' in h['E_infinity'].lower()


class TestEnAlgebras:
    def test_vector_spaces(self):
        ea = en_algebras()
        assert 'Associative' in ea['in_vector_spaces']['E_1']

    def test_categories(self):
        ea = en_algebras()
        assert 'Monoidal' in ea['in_categories']['E_1']
        assert 'Braided' in ea['in_categories']['E_2']

    def test_chain_complexes(self):
        ea = en_algebras()
        assert 'DISTINCT' in ea['in_chain_complexes']['key']


class TestAInfinity:
    def test_stasheff(self):
        ai = a_infinity()
        assert ai['year'] == 1963
        assert 'Stasheff' in ai['inventor']

    def test_pentagon(self):
        assert 'Pentagon' in a_infinity()['stasheff_associahedra']['K_4']

    def test_catalan(self):
        assert 'Catalan' in a_infinity()['stasheff_associahedra']['catalan']


class TestFactorizationAlgebras:
    def test_en_connection(self):
        assert 'E_n' in factorization_algebras()['definition']['en_connection']

    def test_costello(self):
        assert 'Costello' in factorization_algebras()['physics']['costello_gwilliam']


class TestLurieHigherAlgebra:
    def test_pages(self):
        assert lurie_higher_algebra()['pages'] == 1553

    def test_author(self):
        assert 'Lurie' in lurie_higher_algebra()['author']

    def test_dunn(self):
        assert 'E_{m+n}' in lurie_higher_algebra()['key_results']['additivity']


class TestDeformationQuantization:
    def test_kontsevich(self):
        dq = deformation_quantization()
        assert 'Kontsevich' in dq['kontsevich']['theorem']

    def test_poisson(self):
        assert 'Poisson' in deformation_quantization()['kontsevich']['consequence']

    def test_e2(self):
        assert 'E_2' in deformation_quantization()['operadic_view']['key_role']


class TestKoszulDuality:
    def test_comm_lie(self):
        assert 'Lie' in koszul_duality()['examples']['comm_lie']

    def test_assoc_selfdual(self):
        assert 'self-dual' in koszul_duality()['examples']['assoc_assoc'].lower()

    def test_en_selfdual(self):
        assert 'self-dual' in koszul_duality()['examples']['en_en'].lower()


class TestStructuredRingSpectra:
    def test_tmf(self):
        srs = structured_ring_spectra()
        assert 'TMF' in srs['hierarchy']['examples']['tmf']

    def test_e8_link(self):
        assert 'E8' in structured_ring_spectra()['tmf']['e8_link']


class TestGT:
    def test_galois(self):
        assert 'Galois' in grothendieck_teichmuller()['definition']['contains']

    def test_e2(self):
        assert 'E_2' in grothendieck_teichmuller()['operadic_connection']['e2']


class TestHigherAlgebraE8:
    def test_w33(self):
        he = higher_algebra_e8()
        assert any('W(3,3)' in p for p in he['w33_chain']['path'])

    def test_lie_operad(self):
        he = higher_algebra_e8()
        assert any('Lie operad' in p for p in he['w33_chain']['path'])


class TestCompleteChain:
    def test_length(self):
        assert len(complete_chain()['links']) == 6

    def test_miracle(self):
        assert 'OPERADS' in complete_chain()['miracle']['statement']

    def test_starts_w33(self):
        assert complete_chain()['links'][0]['from'] == 'W(3,3)'


class TestRunAllChecks:
    def test_all_pass(self):
        assert run_all_checks() is True
