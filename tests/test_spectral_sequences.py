"""Tests for Pillar 161 — Spectral Sequences."""
import pytest, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT / "pillars") not in sys.path:
    sys.path.insert(0, str(ROOT / "pillars"))

from THEORY_PART_CCLXI_SPECTRAL_SEQUENCES import (
    spectral_sequence_foundations,
    exact_couples,
    filtered_complexes,
    serre_spectral_sequence,
    adams_spectral_sequence,
    grothendieck_spectral_sequence,
    atiyah_hirzebruch,
    hodge_spectral,
    group_cohomology_ss,
    convergence,
    spectral_e8,
    complete_chain,
    run_all_checks,
)


class TestFoundations:
    def test_founder(self):
        assert spectral_sequence_foundations()['founder'] == 'Jean Leray'

    def test_year(self):
        assert spectral_sequence_foundations()['year'] == 1946

    def test_iteration(self):
        r = spectral_sequence_foundations()
        assert 'E_{r+1}' in r['definition']['iteration']

    def test_convergence_idea(self):
        r = spectral_sequence_foundations()
        assert 'approximation' in r['intuition']['successive_approx']


class TestExactCouples:
    def test_massey(self):
        assert exact_couples()['founder'] == 'William Massey'

    def test_year(self):
        assert exact_couples()['year'] == 1952

    def test_serre_example(self):
        assert 'Serre' in exact_couples()['examples'][0]


class TestFilteredComplexes:
    def test_e0(self):
        r = filtered_complexes()
        assert 'associated graded' in r['pages']['E_0']

    def test_convergence(self):
        r = filtered_complexes()
        assert '=>' in r['convergence']['statement']


class TestSerreSpectralSequence:
    def test_founder(self):
        assert serre_spectral_sequence()['founder'] == 'Jean-Pierre Serre'

    def test_e2(self):
        r = serre_spectral_sequence()
        assert 'H^p(B' in r['setup']['e2_page']

    def test_five_term(self):
        r = serre_spectral_sequence()
        assert 'E_2^{1,0}' in r['five_term']['sequence']

    def test_applications(self):
        r = serre_spectral_sequence()
        assert 'homotopy' in r['applications']['homotopy_groups']


class TestAdamsSpectralSequence:
    def test_founder(self):
        assert adams_spectral_sequence()['founder'] == 'J. Frank Adams'

    def test_year(self):
        assert adams_spectral_sequence()['year'] == 1958

    def test_steenrod(self):
        r = adams_spectral_sequence()
        assert 'Steenrod' in r['setup']['e2_page']

    def test_adams_novikov(self):
        r = adams_spectral_sequence()
        assert 'MU' in r['adams_novikov']['generalization']


class TestGrothendieckSS:
    def test_founder(self):
        assert grothendieck_spectral_sequence()['founder'] == 'Alexander Grothendieck'

    def test_e2(self):
        r = grothendieck_spectral_sequence()
        assert 'R^p G' in r['setup']['e2_page']

    def test_leray_example(self):
        r = grothendieck_spectral_sequence()
        assert 'Leray' in r['examples']['leray']


class TestAtiyahHirzebruch:
    def test_authors(self):
        r = atiyah_hirzebruch()
        assert 'Atiyah' in r['authors'][0]

    def test_k_theory(self):
        r = atiyah_hirzebruch()
        assert 'K-theory' in r['applications']['k_theory']


class TestHodgeSpectral:
    def test_degeneration(self):
        r = hodge_spectral()
        assert 'Deligne' in r['hodge_de_rham']['degeneration']

    def test_kahler(self):
        r = hodge_spectral()
        assert 'Kahler' in r['hodge_de_rham']['hodge_decomposition']


class TestGroupCohomologySS:
    def test_e2(self):
        r = group_cohomology_ss()
        assert 'H^p(G/N' in r['setup']['e2_page']

    def test_galois(self):
        r = group_cohomology_ss()
        assert 'Galois' in r['applications']['galois']


class TestConvergence:
    def test_first_quadrant(self):
        r = convergence()
        assert 'First-quadrant' in r['degeneration']['first_quadrant']

    def test_edge_maps(self):
        r = convergence()
        assert 'Edge' in r['tricks']['edge_maps']


class TestE8Connection:
    def test_w33(self):
        r = spectral_e8()
        assert any('W(3,3)' in p for p in r['w33_chain']['path'])

    def test_bott(self):
        r = spectral_e8()
        assert 'Bott' in r['connections']['adams_e8']['bott']


class TestCompleteChain:
    def test_links(self):
        assert len(complete_chain()['links']) == 6

    def test_miracle(self):
        assert 'SUCCESSIVE' in complete_chain()['miracle']['statement']


class TestAllChecks:
    def test_run_all(self):
        assert run_all_checks() is True
