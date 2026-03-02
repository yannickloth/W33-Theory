"""
Tests for Pillar 146: Noncommutative Geometry & Spectral Standard Model.
"""

import pytest
from THEORY_PART_CCXLVI_NONCOMMUTATIVE_GEOMETRY import (
    gelfand_naimark_duality,
    spectral_triple,
    noncommutative_standard_model,
    spectral_action_principle,
    cyclic_cohomology,
    noncommutative_torus,
    moyal_product,
    k_theory_operators,
    connes_distance,
    ncg_gauge_theory,
    ncg_number_theory,
    complete_chain_w33_to_ncg,
    run_all_checks,
)


class TestGelfandNaimark:
    def test_basics(self):
        gn = gelfand_naimark_duality()
        assert gn['year'] == 1943
        assert 'Gelfand' in str(gn['authors'])

    def test_dictionary(self):
        gn = gelfand_naimark_duality()
        assert len(gn['dictionary']) >= 8
        assert 'vector_bundle' in gn['dictionary']

    def test_philosophy(self):
        gn = gelfand_naimark_duality()
        assert 'noncommutative' in gn['ncg_philosophy']['idea'].lower()


class TestSpectralTriple:
    def test_definition(self):
        st = spectral_triple()
        assert 'A' in st['definition']
        assert 'H' in st['definition']
        assert 'D' in st['definition']

    def test_reconstruction_axioms(self):
        st = spectral_triple()
        assert len(st['reconstruction']['axioms']) == 5

    def test_commutative_example(self):
        st = spectral_triple()
        assert 'Dirac' in st['commutative_example']['D']

    def test_distance_formula(self):
        st = spectral_triple()
        assert 'Riemannian metric' in st['commutative_example']['meaning']

    def test_ko_dimension(self):
        st = spectral_triple()
        assert 0 in st['real_structure']['table']
        assert 6 in st['real_structure']['table']


class TestNCGStandardModel:
    def test_algebra(self):
        nsm = noncommutative_standard_model()
        assert nsm['finite_geometry']['algebra'] == 'A_F = C + H + M_3(C)'

    def test_gauge_group(self):
        nsm = noncommutative_standard_model()
        assert 'SU(3)' in nsm['finite_geometry']['gauge_group']
        assert 'SU(2)' in nsm['finite_geometry']['gauge_group']
        assert 'U(1)' in nsm['finite_geometry']['gauge_group']

    def test_ko_dim(self):
        nsm = noncommutative_standard_model()
        assert nsm['product_geometry']['KO_dim_F'] == 6

    def test_fermions(self):
        nsm = noncommutative_standard_model()
        assert nsm['fermions_per_generation']['colors'] == 3
        assert '48' in nsm['fermions_per_generation']['total']

    def test_emergent_physics(self):
        nsm = noncommutative_standard_model()
        ep = nsm['emergent_physics']
        assert 'Einstein' in ep['gravity']

    def test_key_papers(self):
        nsm = noncommutative_standard_model()
        years = [p['year'] for p in nsm['key_papers']]
        assert 1996 in years
        assert 2006 in years


class TestSpectralAction:
    def test_basics(self):
        sa = spectral_action_principle()
        assert sa['year'] == 1996
        assert 'Chamseddine' in str(sa['authors'])

    def test_expansion_terms(self):
        sa = spectral_action_principle()
        assert len(sa['physical_terms']) == 3

    def test_cosmological_constant(self):
        sa = spectral_action_principle()
        assert 'Cosmological' in sa['physical_terms'][0]['produces']

    def test_einstein_hilbert(self):
        sa = spectral_action_principle()
        assert 'Einstein' in sa['physical_terms'][1]['produces']

    def test_yang_mills(self):
        sa = spectral_action_principle()
        assert 'Yang-Mills' in sa['physical_terms'][2]['produces']

    def test_higgs_prediction(self):
        sa = spectral_action_principle()
        assert '125' in sa['predictions']['higgs_mass_revised']


class TestCyclicCohomology:
    def test_basics(self):
        cc = cyclic_cohomology()
        assert cc['year'] == 1981
        assert cc['introduced_by'] == 'Alain Connes'

    def test_periodicity(self):
        cc = cyclic_cohomology()
        assert 'S-operator' in cc['properties']['periodicity']

    def test_index_theory(self):
        cc = cyclic_cohomology()
        assert 'Connes-Moscovici' in cc['index_theory']['local_index']


class TestNCTorus:
    def test_relation(self):
        nct = noncommutative_torus()
        assert 'exp' in nct['definition']['relation']
        assert 'theta' in nct['definition']['relation']

    def test_k_theory(self):
        nct = noncommutative_torus()
        assert 'Z + Z' in nct['properties']['K_theory']['K_0']

    def test_physics(self):
        nct = noncommutative_torus()
        assert 'T-duality' in nct['physics']['t_duality']


class TestMoyalProduct:
    def test_basics(self):
        mp = moyal_product()
        assert 'Moyal' in mp['name']

    def test_kontsevich(self):
        mp = moyal_product()
        assert 'Kontsevich' in str(mp['deformation_quantization'])
        assert 'Fields' in str(mp['deformation_quantization'])


class TestKTheory:
    def test_bott_periodicity(self):
        kt = k_theory_operators()
        assert 'period 8' in kt['bott_periodicity']['real']

    def test_examples(self):
        kt = k_theory_operators()
        assert kt['examples']['C']['K_0'] == 'Z'
        assert kt['examples']['A_theta']['K_0'] == 'Z^2'

    def test_physics(self):
        kt = k_theory_operators()
        assert 'D-brane' in kt['physics']['D_brane_charges']


class TestConnesDistance:
    def test_formula(self):
        cd = connes_distance()
        assert 'sup' in cd['formula']
        assert '[D,a]' in cd['formula']

    def test_geodesic(self):
        cd = connes_distance()
        assert 'geodesic' in cd['commutative_case']['result']


class TestNCGGauge:
    def test_inner_fluctuations(self):
        gt = ncg_gauge_theory()
        assert 'D + A' in gt['inner_fluctuations']['formula']

    def test_sm_gauge(self):
        gt = ncg_gauge_theory()
        assert 'U(1) x SU(2) x SU(3)' in gt['standard_model_gauge']['inner_auts']

    def test_higgs_origin(self):
        gt = ncg_gauge_theory()
        assert 'FINITE' in gt['standard_model_gauge']['higgs']['origin']


class TestNCGNumberTheory:
    def test_bost_connes(self):
        nt = ncg_number_theory()
        assert nt['bost_connes']['year'] == 1995
        assert 'zeta' in nt['bost_connes']['partition_function'].lower()

    def test_riemann_hypothesis(self):
        nt = ncg_number_theory()
        assert 'spectral' in nt['riemann_hypothesis']['connes_approach'].lower()


class TestChain:
    def test_links(self):
        ch = complete_chain_w33_to_ncg()
        assert len(ch['links']) == 7
        assert 'W(3,3)' in ch['links'][0]['from']

    def test_miracle(self):
        ch = complete_chain_w33_to_ncg()
        assert 'ALGEBRA' in ch['miracle']['statement']
        assert 'PHYSICS' in ch['miracle']['statement']

    def test_prizes(self):
        ch = complete_chain_w33_to_ncg()
        assert 'Fields' in ch['prizes']['connes_fields_1982']


class TestRunChecks:
    def test_all_pass(self):
        assert run_all_checks()

    def test_returns_bool(self):
        assert isinstance(run_all_checks(), bool)
