"""Tests for Pillar 151: Derived Categories & Homological Mirror Symmetry."""
import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))

from THEORY_PART_CCLI_DERIVED_CATEGORIES import (
    derived_categories,
    triangulated_categories,
    coherent_sheaves,
    fourier_mukai,
    homological_mirror_symmetry,
    bridgeland_stability,
    tilting_theory,
    d_branes_derived,
    exceptional_collections,
    a_infinity_categories,
    derived_e8,
    complete_chain,
    run_all_checks,
)


class TestDerivedCategories:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = derived_categories()

    def test_year(self):
        assert self.r['year'] == 1960

    def test_grothendieck(self):
        assert any('Grothendieck' in a for a in self.r['introduced_by'])

    def test_verdier(self):
        assert any('Verdier' in a for a in self.r['introduced_by'])

    def test_ext_formula(self):
        assert 'Ext' in self.r['key_formula']['ext_groups']


class TestTriangulatedCategories:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = triangulated_categories()

    def test_verdier(self):
        assert self.r['axiomatized_by'] == 'Jean-Louis Verdier'

    def test_axioms(self):
        assert len(self.r['structure']['axioms']) >= 1

    def test_enhancements(self):
        assert 'DG' in self.r['problems']['enhancement']


class TestCoherentSheaves:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = coherent_sheaves()

    def test_b_branes(self):
        assert 'B-branes' in self.r['string_theory']['b_branes']

    def test_k_theory(self):
        assert 'K_0' in self.r['invariants']['K_theory']


class TestFourierMukai:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = fourier_mukai()

    def test_orlov_year(self):
        assert self.r['theorem']['year'] == 1997

    def test_orlov_name(self):
        assert 'Orlov' in self.r['theorem']['author']

    def test_abelian_variety(self):
        assert 'Mukai' in self.r['examples']['abelian_variety']['classical']


class TestHMS:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = homological_mirror_symmetry()

    def test_year(self):
        assert self.r['year'] == 1994

    def test_kontsevich(self):
        assert 'Kontsevich' in self.r['conjectured_by']

    def test_statement(self):
        assert 'D^b' in self.r['conjecture']['statement']
        assert 'Fuk' in self.r['conjecture']['statement']

    def test_seidel(self):
        assert self.r['proved_cases']['quartic_surface']['year'] == 2003

    def test_fields_medal(self):
        assert 'Kontsevich' in self.r['significance']['fields_medal']


class TestBridgelandStability:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = bridgeland_stability()

    def test_year(self):
        assert self.r['year'] == 2007

    def test_bps(self):
        assert 'BPS' in self.r['physics']['bps_states']

    def test_complex_manifold(self):
        assert 'complex manifold' in self.r['properties']['stab_manifold']


class TestTiltingTheory:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = tilting_theory()

    def test_beilinson_1978(self):
        assert self.r['examples']['beilinson']['year'] == 1978


class TestDBranesDerived:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = d_branes_derived()

    def test_type_iib(self):
        assert 'D^b(Coh(X))' in self.r['categories']['type_iib']['category']

    def test_k_theory_charges(self):
        assert 'K-theory' in self.r['physical_operations']['k_theory']

    def test_open_strings(self):
        assert 'Ext' in self.r['correspondence']['open_strings']


class TestExceptionalCollections:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = exceptional_collections()

    def test_projective_space(self):
        assert self.r['examples']['projective_space']['variety'] == 'P^n'

    def test_braid_mutations(self):
        assert 'braid' in self.r['mutations']['braid_group'].lower()


class TestAInfinity:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = a_infinity_categories()

    def test_stasheff(self):
        assert 'Stasheff' in self.r['definition']['introduced_by']

    def test_fukaya(self):
        assert 'Fukaya' in self.r['importance']['fukaya']


class TestDerivedE8:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = derived_e8()

    def test_e8_in_k3(self):
        assert 'E8' in self.r['k3_derived']['e8_appears']

    def test_del_pezzo_e8(self):
        assert self.r['del_pezzo']['root_systems']['S_8'] == 'E_8'

    def test_del_pezzo_e6(self):
        assert self.r['del_pezzo']['root_systems']['S_6'] == 'E_6'

    def test_del_pezzo_e7(self):
        assert self.r['del_pezzo']['root_systems']['S_7'] == 'E_7'


class TestCompleteChain:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = complete_chain()

    def test_six_links(self):
        assert len(self.r['links']) == 6

    def test_miracle(self):
        assert 'ALGEBRAIC GEOMETRY' in self.r['miracle']['statement']


class TestRunAllChecks:
    def test_all_checks_pass(self):
        assert run_all_checks() is True
