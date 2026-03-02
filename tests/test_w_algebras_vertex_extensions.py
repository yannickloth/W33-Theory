"""Tests for Pillar 184 - W-Algebras & Vertex Operator Extensions."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P184():
    return importlib.import_module("THEORY_PART_CCLXXXIV_W_ALGEBRAS_VERTEX_EXTENSIONS")

# ── w_algebra_basics ──────────────────────────────────────
class TestWAlgebraBasics:
    def test_zamolodchikov(self, P184):
        r = P184.w_algebra_basics()
        assert 'Zamolodchikov' in r['w_n']['w_3']

    def test_virasoro_spin2(self, P184):
        r = P184.w_algebra_basics()
        assert 'spin 2' in r['w_n']['virasoro']

    def test_w_n_general(self, P184):
        r = P184.w_algebra_basics()
        assert 'spin' in r['w_n']['w_n_general']

    def test_ds_reduction(self, P184):
        r = P184.w_algebra_basics()
        assert 'Hamiltonian' in r['ds_reduction']['definition'] or 'reduction' in r['ds_reduction']['definition']

    def test_e6_walgebra(self, P184):
        r = P184.w_algebra_basics()
        assert 'E6' in r['w33_connection']['e6_walgebra']

    def test_sp6_subalgebra(self, P184):
        r = P184.w_algebra_basics()
        assert 'Sp(6' in r['w33_connection']['sp6_subalgebra']

# ── agt_correspondence ─────────────────────────────────────
class TestAGTCorrespondence:
    def test_agt_statement(self, P184):
        r = P184.agt_correspondence()
        assert 'conformal block' in r['agt']['statement'].lower() or 'W-algebra' in r['agt']['statement']

    def test_nekrasov(self, P184):
        r = P184.agt_correspondence()
        assert 'Nekrasov' in r['nekrasov']['definition']

    def test_instanton(self, P184):
        r = P184.agt_correspondence()
        assert 'Z_inst' in r['nekrasov']['instanton_counting'] or 'ADHM' in r['nekrasov']['instanton_counting']

    def test_sw_limit(self, P184):
        r = P184.agt_correspondence()
        assert 'Seiberg-Witten' in r['nekrasov']['sw_limit']

    def test_w33_agt(self, P184):
        r = P184.agt_correspondence()
        assert 'E6' in r['w33_agt']['e6_theory']

# ── vertex_algebra_theory ──────────────────────────────────
class TestVertexAlgebraTheory:
    def test_borcherds(self, P184):
        r = P184.vertex_algebra_theory()
        assert 'Borcherds' in r['axioms']['borcherds']

    def test_sugawara(self, P184):
        r = P184.vertex_algebra_theory()
        assert 'Sugawara' in r['affine']['sugawara']

    def test_affine_central_charge(self, P184):
        r = P184.vertex_algebra_theory()
        assert 'k' in r['affine']['central_charge'] and 'dim' in r['affine']['central_charge']

    def test_moonshine(self, P184):
        r = P184.vertex_algebra_theory()
        assert 'moonshine' in r['w33_vertex']['moonshine'].lower() or 'Monster' in r['w33_vertex']['moonshine']

# ── free_field_realizations ────────────────────────────────
class TestFreeFieldRealizations:
    def test_wakimoto(self, P184):
        r = P184.free_field_realizations()
        assert 'Wakimoto' in r['wakimoto']['origin']

    def test_feigin_frenkel(self, P184):
        r = P184.free_field_realizations()
        assert 'Feigin' in r['center']['center_theorem'] or 'Feigin-Frenkel' in r['center']['center_theorem']

    def test_opers(self, P184):
        r = P184.free_field_realizations()
        assert 'oper' in r['center']['opers'].lower()

    def test_langlands(self, P184):
        r = P184.free_field_realizations()
        assert 'Langlands' in r['center']['langlands_dual']

    def test_brst(self, P184):
        r = P184.free_field_realizations()
        assert 'BRST' in r['brst']['complex']

# ── arakawa_rationality ────────────────────────────────────
class TestArakawaRationality:
    def test_lisse(self, P184):
        r = P184.arakawa_rationality()
        assert 'lisse' in r['associated_variety']['lisse'].lower() or 'C_2' in r['associated_variety']['lisse']

    def test_arakawa_2015(self, P184):
        r = P184.arakawa_rationality()
        assert 'Arakawa' in r['associated_variety']['arakawa_2015']

    def test_modular_invariance(self, P184):
        r = P184.arakawa_rationality()
        assert 'SL_2' in r['results']['modular_invariance'] or 'modular' in r['results']['modular_invariance'].lower()

    def test_schur_index(self, P184):
        r = P184.arakawa_rationality()
        assert 'Schur' in r['results']['schur_index']

# ── w_algebras_and_integrable_systems ──────────────────────
class TestIntegrableSystemsW:
    def test_kdv(self, P184):
        r = P184.w_algebras_and_integrable_systems()
        assert 'KdV' in r['classical']['kdv']

    def test_toda(self, P184):
        r = P184.w_algebras_and_integrable_systems()
        assert 'Toda' in r['classical']['toda']

    def test_higher_spin(self, P184):
        r = P184.w_algebras_and_integrable_systems()
        assert 'higher-spin' in r['physics']['higher_spin'].lower() or 'Higher-spin' in r['physics']['higher_spin']

    def test_w33_integrable(self, P184):
        r = P184.w_algebras_and_integrable_systems()
        assert 'W(3,3)' in r['quantum']['w33_integrable']

    def test_hitchin(self, P184):
        r = P184.w_algebras_and_integrable_systems()
        assert 'Hitchin' in r['classical']['hitchin']

# ── self-checks ────────────────────────────────────────────
class TestSelfChecks:
    def test_all_pass(self, P184):
        assert P184.run_self_checks() is True
