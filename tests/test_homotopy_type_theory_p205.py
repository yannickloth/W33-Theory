"""
Tests for Pillar 205: Homotopy Type Theory and W(3,3)
Module: THEORY_PART_CCCV_HOMOTOPY_TYPE_THEORY
"""
import importlib
import pytest

@pytest.fixture(scope="module")
def mod():
    return importlib.import_module("pillars.THEORY_PART_CCCV_HOMOTOPY_TYPE_THEORY")


class TestHoTTFoundations:
    def test_martin_lof(self, mod):
        r = mod.hott_foundations()
        assert "Martin" in r['type_theory']['martin_lof']

    def test_identity_type(self, mod):
        r = mod.hott_foundations()
        assert isinstance(r['type_theory']['identity_type'], str)

    def test_univalence_axiom(self, mod):
        r = mod.hott_foundations()
        assert "Voevodsky" in r['univalence']['axiom'] or "univalence" in r['univalence']['axiom'].lower()

    def test_univalence_ua(self, mod):
        r = mod.hott_foundations()
        assert isinstance(r['univalence']['ua'], str)

    def test_higher_inductive_circle(self, mod):
        r = mod.hott_foundations()
        assert "S^1" in r['higher_inductive']['circle'] or "circle" in r['higher_inductive']['circle'].lower()

    def test_curry_howard(self, mod):
        r = mod.hott_foundations()
        assert "Curry" in r['curry_howard']['correspondence'] or "Howard" in r['curry_howard']['correspondence']

    def test_dependent_product(self, mod):
        r = mod.hott_foundations()
        assert "Pi" in r['type_theory']['dependent_product'] or "dependent" in r['type_theory']['dependent_product'].lower()

    def test_transport(self, mod):
        r = mod.hott_foundations()
        assert isinstance(r['univalence']['transport'], str)

    def test_higher_inductive_suspension(self, mod):
        r = mod.hott_foundations()
        assert isinstance(r['higher_inductive']['suspension'], str)

    def test_all_sections(self, mod):
        r = mod.hott_foundations()
        for k in ['type_theory', 'univalence', 'higher_inductive', 'curry_howard']:
            assert k in r


class TestUnivalentFoundations:
    def test_voevodsky_program(self, mod):
        r = mod.univalent_foundations()
        assert "Voevodsky" in r['program']['voevodsky']

    def test_hott_book(self, mod):
        r = mod.univalent_foundations()
        assert "HoTT" in r['program']['hott_book'] or "book" in r['program']['hott_book'].lower()

    def test_synthetic_homotopy(self, mod):
        r = mod.univalent_foundations()
        assert isinstance(r['synthetic_homotopy']['definition'], str)

    def test_freudenthal(self, mod):
        r = mod.univalent_foundations()
        assert "Freudenthal" in r['synthetic_homotopy']['freudenthal']

    def test_n_types(self, mod):
        r = mod.univalent_foundations()
        assert isinstance(r['n_types']['definition'], str)


class TestHigherGroupoids:
    def test_grothendieck_hypothesis(self, mod):
        r = mod.higher_groupoids()
        assert "Grothendieck" in r['grothendieck']['hypothesis'] or "groupoid" in r['grothendieck']['hypothesis'].lower()

    def test_encode_decode(self, mod):
        r = mod.higher_groupoids()
        assert isinstance(r['encode_decode']['method'], str)

    def test_brunerie(self, mod):
        r = mod.higher_groupoids()
        assert "Brunerie" in r['encode_decode']['brunerie']

    def test_classifying_baut(self, mod):
        r = mod.higher_groupoids()
        assert isinstance(r['classifying']['baut'], str)

    def test_applications(self, mod):
        r = mod.higher_groupoids()
        assert isinstance(r['applications_groupoid']['group_theory'], str)


class TestCubicalTypeTheory:
    def test_cchm_authors(self, mod):
        r = mod.cubical_type_theory()
        assert "Cohen" in r['cchm']['authors'] or "CCHM" in r['cchm']['authors']

    def test_path_type(self, mod):
        r = mod.cubical_type_theory()
        assert isinstance(r['cchm']['path_type'], str)

    def test_cubical_agda(self, mod):
        r = mod.cubical_type_theory()
        assert "Agda" in r['cubical_agda']['implementation'] or "cubical" in r['cubical_agda']['implementation'].lower()

    def test_models_cartesian(self, mod):
        r = mod.cubical_type_theory()
        assert isinstance(r['models']['cartesian'], str)

    def test_advantages_computation(self, mod):
        r = mod.cubical_type_theory()
        assert isinstance(r['advantages']['computation'], str)


class TestFormalization:
    def test_lean(self, mod):
        r = mod.formalization()
        assert "Lean" in r['proof_assistants']['lean']

    def test_unimath(self, mod):
        r = mod.formalization()
        assert "UniMath" in r['proof_assistants']['unimath'] or "Voevodsky" in r['proof_assistants']['unimath']

    def test_synthetic_ag(self, mod):
        r = mod.formalization()
        assert isinstance(r['synthetic_ag']['algebraic_geometry'], str)

    def test_modalities(self, mod):
        r = mod.formalization()
        assert isinstance(r['modalities']['definition'], str)

    def test_physics_gauge(self, mod):
        r = mod.formalization()
        assert isinstance(r['physics']['gauge'], str)


class TestW33HoTTSynthesis:
    def test_univalence_count(self, mod):
        r = mod.w33_hott_synthesis()
        assert "1451520" in r['univalence_w33']['univalence_count']

    def test_aut_group(self, mod):
        r = mod.w33_hott_synthesis()
        assert "Sp(6,F2)" in r['aut_type']['aut_group'] or "Sp" in r['aut_type']['aut_group']

    def test_w33_type_finite(self, mod):
        r = mod.w33_hott_synthesis()
        assert "40" in r['w33_type']['finite_type']

    def test_three_families(self, mod):
        r = mod.w33_hott_synthesis()
        assert isinstance(r['higher_structure']['three_families'], str)

    def test_baut(self, mod):
        r = mod.w33_hott_synthesis()
        assert isinstance(r['aut_type']['baut'], str)
