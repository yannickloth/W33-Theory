"""
Tests for Pillar 155: Perfectoid Spaces
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))

from THEORY_PART_CCLV_PERFECTOID_SPACES import (
    perfectoid_fields,
    tilting_equivalence,
    almost_purity,
    weight_monodromy,
    prismatic_cohomology,
    diamonds,
    scholze_lineage,
    local_langlands_perfectoid,
    p_adic_hodge,
    lean_perfectoid,
    perfectoid_e8,
    complete_chain,
    run_all_checks,
)


class TestPerfectoidFields:
    def test_year(self):
        assert perfectoid_fields()['year'] == 2012

    def test_scholze(self):
        assert 'Scholze' in perfectoid_fields()['introduced_by']

    def test_frobenius(self):
        d = perfectoid_fields()['definition']
        assert 'surjective' in d['frobenius'].lower()

    def test_examples(self):
        ex = perfectoid_fields()['examples']
        assert 'p' in str(ex['char_p']['characteristic'])
        assert ex['char_0']['characteristic'] == 0


class TestTiltingEquivalence:
    def test_notation(self):
        te = tilting_equivalence()
        assert 'K^flat' in te['tilt_operation']['notation']

    def test_char_p(self):
        te = tilting_equivalence()
        assert 'p' in te['key_property']['char_p'].lower()

    def test_equivalence(self):
        te = tilting_equivalence()
        assert 'Perf(K) ~ Perf(K^flat)' in te['equivalence']['theorem']

    def test_galois(self):
        te = tilting_equivalence()
        assert 'isomorphic' in te['equivalence']['galois'].lower()


class TestAlmostPurity:
    def test_faltings(self):
        assert 'Faltings' in almost_purity()['original']

    def test_statement(self):
        ap = almost_purity()
        assert 'perfectoid' in ap['statement']['part1'].lower()

    def test_galois(self):
        ap = almost_purity()
        assert 'isomorphic' in ap['galois_implication']['statement'].lower()


class TestWeightMonodromy:
    def test_deligne(self):
        assert 'Deligne' in weight_monodromy()['conjectured_by']

    def test_phd(self):
        wm = weight_monodromy()
        assert '2012' in wm['scholze_proof']['reference']


class TestPrismaticCohomology:
    def test_authors(self):
        pc = prismatic_cohomology()
        assert 'Bhatt' in pc['authors'][0]
        assert 'Scholze' in pc['authors'][1]

    def test_unifies_four(self):
        pc = prismatic_cohomology()
        assert len(pc['unification']['unifies']) == 4

    def test_tao_quote(self):
        pc = prismatic_cohomology()
        assert 'motivic' in pc['significance']['terence_tao'].lower()


class TestDiamonds:
    def test_scholze(self):
        assert 'Scholze' in diamonds()['introduced_by']

    def test_fargues_fontaine(self):
        d = diamonds()
        assert 'Fargues-Fontaine' in d['application']['fargues_fontaine']


class TestScholzeLineage:
    def test_fields(self):
        assert scholze_lineage()['fields_medal'] == 2018

    def test_born(self):
        assert scholze_lineage()['born'] == 1987

    def test_chain_length(self):
        sl = scholze_lineage()
        assert len(sl['lineage']['chain']) == 5

    def test_fields_in_chain(self):
        sl = scholze_lineage()
        assert sl['lineage']['fields_medalists_in_chain'] == 4

    def test_youngest_professor(self):
        sl = scholze_lineage()
        assert '24' in sl['career']['youngest_professor']


class TestLocalLanglands:
    def test_fargues_scholze(self):
        ll = local_langlands_perfectoid()
        assert ll['fargues_scholze']['year'] == 2021

    def test_geometrization(self):
        ll = local_langlands_perfectoid()
        assert 'geometrization' in ll['fargues_scholze']['title'].lower()


class TestPadicHodge:
    def test_fontaine(self):
        ph = p_adic_hodge()
        assert 'Fontaine' in ph['classical']['fontaine']

    def test_prismatic(self):
        ph = p_adic_hodge()
        assert 'prismatic' in ph['scholze_simplification']['prismatic'].lower()


class TestLeanPerfectoid:
    def test_lean(self):
        lp = lean_perfectoid()
        assert 'Lean' in lp['project']['prover']

    def test_year(self):
        assert lean_perfectoid()['project']['year'] == 2019


class TestPerfectoidE8:
    def test_w33(self):
        pe = perfectoid_e8()
        assert any('W(3,3)' in p for p in pe['w33_chain']['path'])

    def test_perfectoid_in_chain(self):
        pe = perfectoid_e8()
        assert any('perfectoid' in p.lower() for p in pe['w33_chain']['path'])


class TestCompleteChain:
    def test_length(self):
        assert len(complete_chain()['links']) == 6

    def test_miracle(self):
        assert 'TILTING' in complete_chain()['miracle']['statement']

    def test_starts_w33(self):
        assert complete_chain()['links'][0]['from'] == 'W(3,3)'


class TestRunAllChecks:
    def test_all_pass(self):
        assert run_all_checks() is True
