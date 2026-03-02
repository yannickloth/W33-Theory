"""
Tests for Pillar 206: Resurgence and Trans-series and W(3,3)
Module: THEORY_PART_CCCVI_RESURGENCE_TRANSSERIES
"""
import importlib
import pytest

@pytest.fixture(scope="module")
def mod():
    return importlib.import_module("pillars.THEORY_PART_CCCVI_RESURGENCE_TRANSSERIES")


class TestResurgenceBasics:
    def test_borel_transform(self, mod):
        r = mod.resurgence_basics()
        assert "Borel" in r['borel']['transform']

    def test_borel_summation(self, mod):
        r = mod.resurgence_basics()
        assert isinstance(r['borel']['summation'], str)

    def test_stokes_phenomenon(self, mod):
        r = mod.resurgence_basics()
        assert "Stokes" in r['stokes']['phenomenon']

    def test_stokes_wall_crossing(self, mod):
        r = mod.resurgence_basics()
        assert isinstance(r['stokes']['wall_crossing'], str)

    def test_alien_ecalle(self, mod):
        r = mod.resurgence_basics()
        assert "Ecalle" in r['alien']['ecalle'] or "resurgence" in r['alien']['ecalle'].lower()

    def test_alien_derivative(self, mod):
        r = mod.resurgence_basics()
        assert isinstance(r['alien']['alien_derivative'], str)

    def test_asymptotic_factorial(self, mod):
        r = mod.resurgence_basics()
        assert "n!" in r['asymptotic']['factorial'] or "factorial" in r['asymptotic']['factorial'].lower()

    def test_asymptotic_optimal(self, mod):
        r = mod.resurgence_basics()
        assert isinstance(r['asymptotic']['optimal'], str)

    def test_all_sections(self, mod):
        r = mod.resurgence_basics()
        for k in ['borel', 'stokes', 'alien', 'asymptotic']:
            assert k in r

    def test_bridge_equation(self, mod):
        r = mod.resurgence_basics()
        assert isinstance(r['alien']['bridge_equation'], str)


class TestTransseries:
    def test_instanton_saddle(self, mod):
        r = mod.transseries()
        assert "instanton" in r['instanton']['saddle'].lower() or "saddle" in r['instanton']['saddle'].lower()

    def test_structure_instanton_action(self, mod):
        r = mod.transseries()
        assert isinstance(r['structure']['instanton_action'], str)

    def test_structure_definition(self, mod):
        r = mod.transseries()
        assert "trans-series" in r['structure']['definition'].lower() or "Trans" in r['structure']['definition']

    def test_resurgent_relations(self, mod):
        r = mod.transseries()
        assert isinstance(r['resurgent_relations']['large_order'], str)

    def test_formal_vs_actual(self, mod):
        r = mod.transseries()
        assert isinstance(r['formal_vs_actual']['formal'], str)


class TestQuantumMechanicsResurgence:
    def test_bender_wu(self, mod):
        r = mod.quantum_mechanics_resurgence()
        assert "Bender" in r['bender_wu']['analysis'] or "Wu" in r['bender_wu']['analysis']

    def test_exact_wkb(self, mod):
        r = mod.quantum_mechanics_resurgence()
        assert "WKB" in r['exact_wkb']['wkb']

    def test_delabaere_pham(self, mod):
        r = mod.quantum_mechanics_resurgence()
        assert "Delabaere" in r['exact_wkb']['delabaere_pham'] or "Pham" in r['exact_wkb']['delabaere_pham']

    def test_double_well(self, mod):
        r = mod.quantum_mechanics_resurgence()
        assert isinstance(r['double_well']['potential'], str)

    def test_zinn_justin(self, mod):
        r = mod.quantum_mechanics_resurgence()
        assert isinstance(r['zinn_justin']['conjecture'], str)


class TestGaugeTheoryResurgence:
    def test_dunne_unsal(self, mod):
        r = mod.gauge_theory_resurgence()
        assert "Dunne" in r['dunne_unsal']['program'] or "Unsal" in r['dunne_unsal']['program']

    def test_cheshire_cat(self, mod):
        r = mod.gauge_theory_resurgence()
        assert "Cheshire" in r['cheshire_cat']['resurgence'] or "resurgence" in r['cheshire_cat']['resurgence'].lower()

    def test_renormalons(self, mod):
        r = mod.gauge_theory_resurgence()
        assert isinstance(r['renormalons']['ir'], str)

    def test_large_n(self, mod):
        r = mod.gauge_theory_resurgence()
        assert isinstance(r['large_n']['t_hooft'], str)

    def test_bions(self, mod):
        r = mod.gauge_theory_resurgence()
        assert isinstance(r['dunne_unsal']['bions'], str)


class TestStringTheoryResurgence:
    def test_topological_string(self, mod):
        r = mod.string_theory_resurgence()
        assert "Gopakumar" in r['topological_string']['gopakumar_vafa'] or "Vafa" in r['topological_string']['gopakumar_vafa']

    def test_non_perturbative(self, mod):
        r = mod.string_theory_resurgence()
        assert isinstance(r['non_perturbative']['string_perturbation'], str)

    def test_painleve(self, mod):
        r = mod.string_theory_resurgence()
        assert "Painleve" in r['painleve']['transcendents'] or "Painlevé" in r['painleve']['transcendents']

    def test_matrix_models(self, mod):
        r = mod.string_theory_resurgence()
        assert isinstance(r['matrix_models']['partition'], str)

    def test_holomorphic_anomaly(self, mod):
        r = mod.string_theory_resurgence()
        assert isinstance(r['topological_string']['holomorphic_anomaly'], str)


class TestW33ResurgenceSynthesis:
    def test_sp6f2_counting(self, mod):
        r = mod.w33_resurgence_synthesis()
        assert "1451520" in r['sp6f2_counting']['counting']

    def test_w33_vacuum_saddle(self, mod):
        r = mod.w33_resurgence_synthesis()
        assert "40" in r['w33_vacuum']['saddle_points']

    def test_instanton_sectors(self, mod):
        r = mod.w33_resurgence_synthesis()
        assert isinstance(r['instanton_sectors']['orbits'], str)

    def test_stokes_w33(self, mod):
        r = mod.w33_resurgence_synthesis()
        assert isinstance(r['stokes_w33']['alien'], str)

    def test_three_families(self, mod):
        r = mod.w33_resurgence_synthesis()
        assert isinstance(r['stokes_w33']['three_families'], str)
