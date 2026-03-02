"""Tests for Pillar 159 — Floer Homology."""
import pytest, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT / "pillars") not in sys.path:
    sys.path.insert(0, str(ROOT / "pillars"))

from THEORY_PART_CCLIX_FLOER_HOMOLOGY import (
    floer_foundations,
    symplectic_floer,
    instanton_floer,
    monopole_floer,
    heegaard_floer,
    ech,
    grand_isomorphisms,
    lagrangian_floer,
    manolescu_triangulation,
    floer_tqft,
    floer_e8,
    complete_chain,
    run_all_checks,
)


class TestFloerFoundations:
    def test_founder(self):
        r = floer_foundations()
        assert r['founder'] == 'Andreas Floer'

    def test_year(self):
        assert floer_foundations()['year'] == 1988

    def test_critical_points(self):
        r = floer_foundations()
        assert 'Critical points' in r['idea']['critical_points']

    def test_gradient_flows(self):
        r = floer_foundations()
        assert 'pseudoholomorphic' in r['idea']['gradient_flows']

    def test_gromov(self):
        r = floer_foundations()
        assert 'Gromov' in r['key_ingredients']['gromov']


class TestSymplecticFloer:
    def test_generators(self):
        r = symplectic_floer()
        assert 'Fixed points' in r['definition']['generators']

    def test_arnold_conjecture(self):
        r = symplectic_floer()
        assert 'Betti' in r['arnold_conjecture']['statement']

    def test_pss(self):
        r = symplectic_floer()
        assert 'PSS' in r['pss']['name']
        assert 'quantum' in r['pss']['statement'].lower()


class TestInstantonFloer:
    def test_chern_simons(self):
        r = instanton_floer()
        assert 'Chern-Simons' in r['construction']['functional']

    def test_flat_connections(self):
        r = instanton_floer()
        assert 'Flat' in r['construction']['critical_points']

    def test_tqft(self):
        r = instanton_floer()
        assert 'TQFT' in r['properties']['tqft']

    def test_casson(self):
        r = instanton_floer()
        assert 'Casson' in r['properties']['casson']


class TestMonopoleFloer:
    def test_authors(self):
        r = monopole_floer()
        assert 'Kronheimer' in r['authors'][0]
        assert 'Mrowka' in r['authors'][1]

    def test_year(self):
        assert monopole_floer()['year'] == 2007

    def test_three_versions(self):
        r = monopole_floer()
        v = r['construction']['three_versions']
        assert 'HM_check' in v
        assert 'HM_hat' in v
        assert 'HM_bar' in v


class TestHeegaardFloer:
    def test_authors(self):
        r = heegaard_floer()
        assert 'Ozsvath' in r['authors'][0]
        assert 'Szabo' in r['authors'][1]

    def test_year(self):
        assert heegaard_floer()['year'] == 2004

    def test_versions(self):
        v = heegaard_floer()['versions']
        assert 'HF_hat' in v and 'HF_plus' in v

    def test_knot_floer_categorifies(self):
        r = heegaard_floer()
        assert 'Alexander' in r['knot_floer']['categorifies']

    def test_knot_detects_genus(self):
        r = heegaard_floer()
        assert 'Genus' in r['knot_floer']['detects']

    def test_combinatorial(self):
        r = heegaard_floer()
        assert 'grid' in r['combinatorial']['grid_diagrams'].lower()


class TestECH:
    def test_founder(self):
        assert ech()['founder'] == 'Michael Hutchings'

    def test_isomorphic_to_swf(self):
        r = ech()
        assert 'Taubes' in r['isomorphisms']['swf']

    def test_weinstein(self):
        r = ech()
        assert 'Taubes' in r['weinstein']['proved_by']


class TestGrandIsomorphisms:
    def test_hf_swf(self):
        r = grand_isomorphisms()
        assert 'Kutluhan' in r['theorems']['hf_swf']['proved_by']

    def test_ech_swf(self):
        r = grand_isomorphisms()
        assert 'Taubes' in r['theorems']['ech_swf']['proved_by']

    def test_significance(self):
        r = grand_isomorphisms()
        assert 'SAME' in r['significance']['unification']


class TestLagrangianFloer:
    def test_fukaya_hms(self):
        r = lagrangian_floer()
        assert 'Kontsevich' in r['fukaya_category']['hms']

    def test_a_infinity(self):
        r = lagrangian_floer()
        assert 'A-infinity' in r['a_infinity']['relations']

    def test_generators_intersection(self):
        r = lagrangian_floer()
        assert 'Intersection' in r['definition']['generators']


class TestManolescu:
    def test_year(self):
        assert manolescu_triangulation()['year'] == 2013

    def test_disproved(self):
        r = manolescu_triangulation()
        assert 'FALSE' in r['triangulation_conjecture']['disproved']


class TestFloerTQFT:
    def test_atiyah_floer(self):
        r = floer_tqft()
        assert 'Atiyah-Floer' in r['atiyah_floer']['conjecture']

    def test_cobordism(self):
        r = floer_tqft()
        assert 'Cobordism' in r['tqft_structure']['cobordism_maps']


class TestE8Connections:
    def test_poincare_sphere(self):
        r = floer_e8()
        assert 'Poincare' in r['connections']['e8_plumbing']['fact']

    def test_donaldson(self):
        r = floer_e8()
        assert 'Donaldson' in r['connections']['donaldson']['fact']

    def test_w33_chain(self):
        r = floer_e8()
        assert any('W(3,3)' in p for p in r['w33_chain']['path'])


class TestCompleteChain:
    def test_links_count(self):
        assert len(complete_chain()['links']) == 6

    def test_miracle(self):
        r = complete_chain()
        assert 'INFINITE-DIMENSIONAL' in r['miracle']['statement']


class TestAllChecks:
    def test_run_all(self):
        assert run_all_checks() is True
