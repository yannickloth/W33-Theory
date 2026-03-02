"""Tests for Pillar 186 - Higher Category Theory & Infinity-Categories."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P186():
    return importlib.import_module("THEORY_PART_CCLXXXVI_HIGHER_CATEGORY_THEORY")

# ── infinity_categories ────────────────────────────────────
class TestInfinityCategories:
    def test_joyal(self, P186):
        r = P186.infinity_categories()
        assert 'Joyal' in r['quasi_categories']['joyal']

    def test_lurie(self, P186):
        r = P186.infinity_categories()
        assert 'Lurie' in r['quasi_categories']['lurie']

    def test_nerve(self, P186):
        r = P186.infinity_categories()
        assert 'nerve' in r['quasi_categories']['nerve'].lower() or 'Nerve' in r['quasi_categories']['nerve']

    def test_40_objects(self, P186):
        r = P186.infinity_categories()
        assert '40' in r['w33_infty']['objects']

    def test_homotopy_hypothesis(self, P186):
        r = P186.infinity_categories()
        assert 'Grothendieck' in r['quasi_categories']['homotopy_hypothesis'] or 'groupoid' in r['quasi_categories']['homotopy_hypothesis']

    def test_higher_morphisms(self, P186):
        r = P186.infinity_categories()
        assert 'homotop' in r['structures']['higher'].lower()

# ── cobordism_hypothesis ──────────────────────────────────
class TestCobordismHypothesis:
    def test_baez_dolan(self, P186):
        r = P186.cobordism_hypothesis()
        assert '1995' in r['hypothesis']['baez_dolan']

    def test_lurie_proof(self, P186):
        r = P186.cobordism_hypothesis()
        assert 'Lurie' in r['hypothesis']['lurie_proof']

    def test_dualizable(self, P186):
        r = P186.cobordism_hypothesis()
        assert 'dualizable' in r['hypothesis']['classification']

    def test_fully_dualizable(self, P186):
        r = P186.cobordism_hypothesis()
        assert 'dualizable' in r['dualizable']['fully_dual'].lower()

    def test_w33_cobordism(self, P186):
        r = P186.cobordism_hypothesis()
        assert 'W(3,3)' in r['w33_cobordism']['w33_as_point_value']

# ── stable_infinity_categories ─────────────────────────────
class TestStableInfinityCategories:
    def test_triangulated(self, P186):
        r = P186.stable_infinity_categories()
        assert 'triangulated' in r['stability']['triangulated']

    def test_spectra(self, P186):
        r = P186.stable_infinity_categories()
        assert 'Spectrum' in r['spectra']['definition'] or 'spectrum' in r['spectra']['definition']

    def test_tmf(self, P186):
        r = P186.stable_infinity_categories()
        assert 'tmf' in r['spectra']['tmf'] or 'topological modular' in r['spectra']['tmf'].lower()

    def test_sphere_spectrum(self, P186):
        r = P186.stable_infinity_categories()
        assert 'Sphere' in r['spectra']['sphere'] or 'sphere' in r['spectra']['sphere']

# ── higher_topos_theory ────────────────────────────────────
class TestHigherToposTheory:
    def test_htt_pages(self, P186):
        r = P186.higher_topos_theory()
        assert '944' in r['topoi']['lurie_htt']

    def test_dag(self, P186):
        r = P186.higher_topos_theory()
        assert 'E_infinity' in r['dag']['definition'] or 'ring spectra' in r['dag']['definition']

    def test_toen_vezzosi(self, P186):
        r = P186.higher_topos_theory()
        assert 'Toen' in r['dag']['toen_vezzosi'] or 'HAG' in r['dag']['toen_vezzosi']

    def test_w33_topos(self, P186):
        r = P186.higher_topos_theory()
        assert 'Sp(6,F2)' in r['w33_topos']['classifying_space']

# ── enriched_and_internal ──────────────────────────────────
class TestEnrichedAndInternal:
    def test_e1(self, P186):
        r = P186.enriched_and_internal()
        assert 'E_1' in r['monoidal']['e_1']

    def test_e2(self, P186):
        r = P186.enriched_and_internal()
        assert 'E_2' in r['monoidal']['e_2']

    def test_e_infinity(self, P186):
        r = P186.enriched_and_internal()
        assert 'E_infinity' in r['monoidal']['e_infinity']

    def test_dunn(self, P186):
        r = P186.enriched_and_internal()
        assert 'E_{m+n}' in r['monoidal']['dunn_additivity']

    def test_factorization(self, P186):
        r = P186.enriched_and_internal()
        assert 'Factorization' in r['monoidal']['factorization'] or 'factorization' in r['monoidal']['factorization']

# ── applications_to_physics ────────────────────────────────
class TestApplicationsToPhysics:
    def test_atiyah_segal(self, P186):
        r = P186.applications_to_physics()
        assert 'Atiyah' in r['tft_classification']['atiyah_segal']

    def test_higher_gauge(self, P186):
        r = P186.applications_to_physics()
        assert 'Higher gauge' in r['gauge_theory']['higher_gauge'] or 'higher gauge' in r['gauge_theory']['higher_gauge'].lower()

    def test_two_group(self, P186):
        r = P186.applications_to_physics()
        assert '2-group' in r['gauge_theory']['two_group']

    def test_condensed(self, P186):
        r = P186.applications_to_physics()
        assert 'Scholze' in r['state_of_art']['condensed'] or 'Clausen' in r['state_of_art']['condensed']

# ── self-checks ────────────────────────────────────────────
class TestSelfChecks:
    def test_all_pass(self, P186):
        assert P186.run_self_checks() is True
