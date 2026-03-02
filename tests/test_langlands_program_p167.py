"""Tests for Pillar 167 – The Langlands Program (CCLXVII)."""

import pytest
from THEORY_PART_CCLXVII_LANGLANDS_PROGRAM import (
    langlands_foundations,
    reciprocity,
    functoriality,
    automorphic_forms,
    l_functions,
    fundamental_lemma,
    geometric_langlands,
    local_langlands,
    fields_medals,
    connections_to_prior,
    e8_langlands,
    w33_chain,
    trace_formula,
    beyond_langlands,
    complete_chain,
    run_all_checks,
)


# ── 1. Foundations ──────────────────────────────────────────────────────────

class TestFoundations:
    def test_founder(self):
        r = langlands_foundations()
        assert 'Robert Langlands' in r['founder']
        assert r['year'] == 1967

    def test_origin(self):
        r = langlands_foundations()
        assert 'Weil' in r['origin']['letter']
        assert 'class field theory' in r['origin']['class_field_theory']

    def test_three_pillars(self):
        r = langlands_foundations()
        for k in ('reciprocity', 'functoriality', 'l_functions'):
            assert k in r['pillars']


# ── 2. Reciprocity ─────────────────────────────────────────────────────────

class TestReciprocity:
    def test_statement(self):
        r = reciprocity()
        assert 'Galois' in r['statement']['informal']
        assert 'automorphic' in r['statement']['informal']

    def test_gl2_wiles(self):
        r = reciprocity()
        assert 'Wiles' in r['gl2_case']['wiles']
        assert "Fermat" in r['gl2_case']['wiles']

    def test_bcdt(self):
        r = reciprocity()
        assert '2001' in r['gl2_case']['breuil_conrad_diamond_taylor']

    def test_abelian(self):
        r = reciprocity()
        assert 'class field' in r['abelian_case']['gl1'].lower()


# ── 3. Functoriality ───────────────────────────────────────────────────────

class TestFunctoriality:
    def test_l_group_e8(self):
        r = functoriality()
        assert 'E8' in r['l_group']['examples']
        assert 'self-dual' in r['l_group']['examples'].lower()

    def test_principle(self):
        r = functoriality()
        assert 'transfer' in r['principle']['statement'].lower()

    def test_known_cases(self):
        r = functoriality()
        assert 'Arthur' in r['known_cases']['endoscopy']
        assert 'Gelbart' in r['known_cases']['symmetric_square']


# ── 4. Automorphic Forms ───────────────────────────────────────────────────

class TestAutomorphicForms:
    def test_classical_modular(self):
        r = automorphic_forms()
        assert 'modular' in r['definition']['classical'].lower()

    def test_factorization(self):
        r = automorphic_forms()
        assert 'tensor' in r['representation']['factorization'].lower()

    def test_examples(self):
        r = automorphic_forms()
        assert 'Hilbert' in r['examples']['hilbert']
        assert 'Siegel' in r['examples']['siegel']
        assert 'Maass' in r['examples']['maass']


# ── 5. L-Functions ─────────────────────────────────────────────────────────

class TestLFunctions:
    def test_hierarchy(self):
        r = l_functions()
        assert 'Riemann' in r['hierarchy']['riemann_zeta']
        assert 'motiv' in r['hierarchy']['motivic'].lower()

    def test_euler_product(self):
        r = l_functions()
        assert 'Euler product' in r['properties']['euler_product']

    def test_langlands_conjecture(self):
        r = l_functions()
        assert 'automorphic' in r['langlands_conjecture']['statement']


# ── 6. Fundamental Lemma ───────────────────────────────────────────────────

class TestFundamentalLemma:
    def test_ngo(self):
        r = fundamental_lemma()
        assert 'Ngô' in r['proved'] or 'Ngo' in r['proved']
        assert 'Fields' in r['proved']

    def test_hitchin(self):
        r = fundamental_lemma()
        assert 'Hitchin' in r['proof']['method']

    def test_impact(self):
        r = fundamental_lemma()
        assert 'trace formula' in r['impact']['trace_formula'].lower()


# ── 7. Geometric Langlands ─────────────────────────────────────────────────

class TestGeometricLanglands:
    def test_proof_2024(self):
        r = geometric_langlands()
        assert r['proof_2024']['year'] == 2024
        assert 'Gaitsgory' in r['proof_2024']['authors']

    def test_conjecture_bun_g(self):
        r = geometric_langlands()
        assert 'Bun_G' in r['conjecture']['bun_g']

    def test_physics(self):
        r = geometric_langlands()
        assert 'Kapustin-Witten' in r['connections']['physics']
        assert 'S-duality' in r['connections']['physics']


# ── 8. Local Langlands ─────────────────────────────────────────────────────

class TestLocalLanglands:
    def test_gln(self):
        r = local_langlands()
        assert 'Harris-Taylor' in r['proofs']['gln_char0']

    def test_scholze(self):
        r = local_langlands()
        assert 'perfectoid' in r['proofs']['scholze'].lower()

    def test_l_packets(self):
        r = local_langlands()
        assert 'singleton' in r['l_packets']['singleton'].lower()


# ── 9. Fields Medals ───────────────────────────────────────────────────────

class TestFieldsMedals:
    def test_four_medals(self):
        r = fields_medals()
        for key in ('drinfeld_1990', 'lafforgue_2002', 'ngo_2010', 'scholze_2018'):
            assert key in r['medals']

    def test_gaitsgory(self):
        r = fields_medals()
        assert 'Gaitsgory' in r['related']['gaitsgory_2024']


# ── 10. Connections ────────────────────────────────────────────────────────

class TestConnections:
    def test_prior_pillars(self):
        r = connections_to_prior()
        assert 'motivic' in r['motivic_P166']['connection'].lower()
        assert 'D-modules' in r['derived_P164']['detail']


# ── 11. E8 Langlands ──────────────────────────────────────────────────────

class TestE8Langlands:
    def test_self_dual(self):
        r = e8_langlands()
        assert 'self-dual' in r['e8_self_dual']['property'].lower()

    def test_248(self):
        r = e8_langlands()
        assert '248' in r['automorphic_e8']['l_function']

    def test_hitchin(self):
        r = e8_langlands()
        assert 'Hitchin' in r['geometric']['hitchin']


# ── 12. W33 Chain ──────────────────────────────────────────────────────────

class TestW33Chain:
    def test_path(self):
        r = w33_chain()
        assert any('W(3,3)' in p for p in r['path'])
        assert len(r['path']) >= 5

    def test_deep_connection(self):
        r = w33_chain()
        assert 'self-referential' in r['deep_connection']


# ── 13. Trace Formula ─────────────────────────────────────────────────────

class TestTraceFormula:
    def test_selberg(self):
        r = trace_formula()
        assert 'Selberg' in r['selberg']['original']

    def test_arthur(self):
        r = trace_formula()
        assert 'Arthur' in r['arthur']['invariant']

    def test_applications(self):
        r = trace_formula()
        assert len(r['applications']) >= 4


# ── 14. Beyond Langlands ──────────────────────────────────────────────────

class TestBeyondLanglands:
    def test_p_adic(self):
        r = beyond_langlands()
        assert 'perfectoid' in r['p_adic']['scholze_perfectoid'].lower()

    def test_relative(self):
        r = beyond_langlands()
        assert 'Gan-Gross-Prasad' in r['relative']['gan_gross_prasad']


# ── 15. Complete Chain ─────────────────────────────────────────────────────

class TestCompleteChain:
    def test_links(self):
        r = complete_chain()
        assert len(r['links']) == 6

    def test_miracle(self):
        r = complete_chain()
        assert 'MIRACLE' in r['miracle']['statement']
        assert 'Rosetta Stone' in r['miracle']['depth']


# ── Integration ────────────────────────────────────────────────────────────

class TestSelfChecks:
    def test_all_pass(self):
        assert run_all_checks()
