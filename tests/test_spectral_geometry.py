"""
Tests for Pillar 145: Spectral Geometry & Hearing the Shape of Spacetime.
"""

import math
import pytest
from THEORY_PART_CCXLV_SPECTRAL_GEOMETRY import (
    weyl_law,
    heat_kernel,
    hearing_shape_of_drum,
    selberg_trace_formula,
    selberg_zeta,
    isospectrality,
    spectral_action,
    minakshisundaram_pleijel_zeta,
    spectral_geometry_of_lattices,
    spectral_physics,
    heat_trace_modular,
    complete_chain_w33_to_spectral,
    run_all_checks,
)


class TestWeylLaw:
    def test_basics(self):
        w = weyl_law()
        assert w['year'] == 1911
        assert w['discoverer'] == 'Hermann Weyl'

    def test_ball_volumes(self):
        w = weyl_law()
        assert abs(w['unit_ball_volumes'][1] - 2.0) < 0.01
        assert abs(w['unit_ball_volumes'][2] - math.pi) < 0.01
        assert abs(w['unit_ball_volumes'][3] - 4*math.pi/3) < 0.01

    def test_examples(self):
        w = weyl_law()
        assert len(w['examples']) >= 2
        assert w['examples'][0]['domain'] == '1D interval [0,1]'

    def test_weyl_conjecture(self):
        w = weyl_law()
        assert w['weyl_conjecture']['proved_by'] == 'Victor Ivrii'
        assert w['weyl_conjecture']['year'] == 1980

    def test_audible_invariants(self):
        w = weyl_law()
        assert 'Volume' in str(w['audible_invariants'])

    def test_e8_connection(self):
        w = weyl_law()
        assert w['e8_connection']['dimension'] == 8
        assert 'self-dual' in w['e8_connection']['e8_self_dual'].lower()

    def test_ball_volume_dim8(self):
        w = weyl_law()
        expected = math.pi**4 / math.factorial(4)
        assert abs(w['unit_ball_volumes'][8] - expected) < 0.001


class TestHeatKernel:
    def test_basics(self):
        h = heat_kernel()
        assert 'heat equation' in h['equation'].lower() or 'Delta' in h['equation']

    def test_coefficients(self):
        h = heat_kernel()
        assert h['heat_coefficients']['a_0']['meaning'] == 'Volume of the manifold'
        assert 'scalar curvature' in h['heat_coefficients']['a_1']['formula'].lower()

    def test_examples(self):
        h = heat_kernel()
        assert 'flat_torus' in h['examples']
        assert 'sphere_S2' in h['examples']
        assert 'circle_S1' in h['examples']

    def test_e8_heat_trace(self):
        h = heat_kernel()
        assert 'E8 theta function is modular form of weight 4' in h['e8_heat_trace']['theta_function']
        assert 'E_4' in h['e8_heat_trace']['equals_eisenstein']

    def test_jacobi_theta_connection(self):
        h = heat_kernel()
        assert 'theta' in h['examples']['circle_S1']['heat_trace'].lower()


class TestHearingDrum:
    def test_kac(self):
        d = hearing_shape_of_drum()
        assert d['year'] == 1966
        assert 'Kac' in d['posed_by']

    def test_answer_is_no(self):
        d = hearing_shape_of_drum()
        gww = [h for h in d['history'] if h['year'] == 1992][0]
        assert 'No' in gww['answer'] or 'no' in gww['answer'] or 'cannot' in gww['answer']

    def test_milnor_1964(self):
        d = hearing_shape_of_drum()
        milnor = [h for h in d['history'] if h['year'] == 1964][0]
        assert 'Milnor' in milnor['who']
        assert '16' in str(milnor['details'])

    def test_milnor_e8_connection(self):
        d = hearing_shape_of_drum()
        assert d['milnor_e8_connection']['dimension'] == 16
        assert 'E8' in d['milnor_e8_connection']['lattice_1']
        assert 'D16' in d['milnor_e8_connection']['lattice_2']

    def test_sunada(self):
        d = hearing_shape_of_drum()
        sunada = [h for h in d['history'] if h['year'] == 1985][0]
        assert 'Sunada' in sunada['who']

    def test_what_can_be_heard(self):
        d = hearing_shape_of_drum()
        assert 'area' in d['what_can_be_heard']
        assert 'perimeter' in d['what_can_be_heard']

    def test_awards(self):
        d = hearing_shape_of_drum()
        assert len(d['awards']) == 2


class TestSelbergTrace:
    def test_basics(self):
        s = selberg_trace_formula()
        assert s['year'] == 1956
        assert s['discoverer'] == 'Atle Selberg'

    def test_duality(self):
        s = selberg_trace_formula()
        assert 'eigenvalue' in s['duality']['spectral'].lower()
        assert 'geodesic' in s['duality']['geometric'].lower()

    def test_prime_analogy(self):
        s = selberg_trace_formula()
        assert 'prime' in str(s['structure']['analogy']).lower()
        assert 'zeta' in str(s['structure']['analogy']).lower()

    def test_number_theory(self):
        s = selberg_trace_formula()
        assert 'langlands' in str(s['number_theory']).lower()
        assert 'poisson' in str(s['number_theory']).lower()

    def test_modular_connection(self):
        s = selberg_trace_formula()
        assert s['modular_connection']['automorphic_forms_are_eigenfunctions']


class TestSelbergZeta:
    def test_definition(self):
        sz = selberg_zeta()
        assert 'geodesic' in str(sz['variables']).lower()

    def test_riemann_analogy(self):
        sz = selberg_zeta()
        d = sz['riemann_analogy']['dictionary']
        assert 'prime' in str(d).lower()
        assert 'geodesic' in str(d).lower()

    def test_properties(self):
        sz = selberg_zeta()
        assert 'meromorphic' in str(sz['properties']).lower()

    def test_spectral_determinant(self):
        sz = selberg_zeta()
        assert 'det' in str(sz['spectral_determinant']).lower()


class TestIsospectrality:
    def test_even_unimodular_counts(self):
        iso = isospectrality()
        assert iso['even_unimodular'][8]['count'] == 1
        assert iso['even_unimodular'][16]['count'] == 2
        assert iso['even_unimodular'][24]['count'] == 24

    def test_milnor(self):
        iso = isospectrality()
        assert iso['milnor_example']['dimension'] == 16
        assert iso['milnor_example']['same_theta']
        assert not iso['milnor_example']['not_isometric'] == False

    def test_sunada_method(self):
        iso = isospectrality()
        assert iso['sunada_method']['year'] == 1985
        assert len(iso['sunada_method']['applications']) >= 3

    def test_e8_unique(self):
        iso = isospectrality()
        assert iso['even_unimodular'][8]['lattices'] == ['E8']


class TestSpectralAction:
    def test_basics(self):
        sa = spectral_action()
        assert 'Connes' in str(sa['authors'])
        assert sa['year'] == 1996

    def test_output_contains_sm(self):
        sa = spectral_action()
        assert 'einstein_hilbert' in sa['output']
        assert 'yang_mills' in sa['output']
        assert 'higgs' in sa['output']

    def test_spectral_triple(self):
        sa = spectral_action()
        assert 'algebra' in sa['spectral_triple']
        assert 'hilbert_space' in sa['spectral_triple']
        assert 'dirac' in sa['spectral_triple']

    def test_sm_algebra(self):
        sa = spectral_action()
        assert 'C + H + M_3(C)' in sa['standard_model_from_algebra']['algebra']

    def test_heat_kernel_expansion(self):
        sa = spectral_action()
        assert 'Cosmological constant' in str(sa['heat_kernel_expansion']['terms'])


class TestMPZeta:
    def test_basics(self):
        z = minakshisundaram_pleijel_zeta()
        assert z['year'] == 1949

    def test_determinant(self):
        z = minakshisundaram_pleijel_zeta()
        assert 'exp' in z['determinant']['definition']

    def test_heat_kernel_relation(self):
        z = minakshisundaram_pleijel_zeta()
        assert 'integral' in z['heat_kernel_relation']['mellin_transform'].lower()
        assert 'Gamma' in z['heat_kernel_relation']['mellin_transform']

    def test_lattice_zeta(self):
        z = minakshisundaram_pleijel_zeta()
        assert z['lattice_zeta']['is_epstein_zeta']


class TestSpectralLattices:
    def test_e8_shell_counts(self):
        sg = spectral_geometry_of_lattices()
        assert sg['e8_spectrum']['shell_counts'][2] == 240
        assert sg['e8_spectrum']['shell_counts'][4] == 2160
        assert sg['e8_spectrum']['shell_counts'][6] == 6720

    def test_e4_coefficients(self):
        sg = spectral_geometry_of_lattices()
        assert sg['e4_coefficients'][1] == 240
        assert sg['e4_coefficients'][2] == 2160
        assert sg['e4_coefficients'][3] == 6720

    def test_e4_equals_theta(self):
        sg = spectral_geometry_of_lattices()
        assert sg['e8_spectrum']['equals_E4']

    def test_moonshine(self):
        sg = spectral_geometry_of_lattices()
        assert 'j' in str(sg['moonshine']).lower()
        assert 'monster' in str(sg['moonshine']).lower()


class TestSpectralPhysics:
    def test_casimir(self):
        sp = spectral_physics()
        assert sp['casimir']['measured']
        assert '240' in str(sp['casimir']['formula'])

    def test_quantum_chaos(self):
        sp = spectral_physics()
        assert 'GUE' in sp['quantum_chaos']['random_matrices']
        assert 'zeta' in sp['quantum_chaos']['montgomery_odlyzko'].lower()

    def test_string_theory(self):
        sp = spectral_physics()
        assert sp['string_theory']['critical_dimension'] == 'd=26 (bosonic) or d=10 (super) from spectral anomaly'


class TestHeatTraceModular:
    def test_e8_case(self):
        htm = heat_trace_modular()
        assert htm['e8_case']['modular_weight'] == 4
        assert 'E_4' in htm['e8_case']['theta_E8']

    def test_j_invariant(self):
        htm = heat_trace_modular()
        assert '196884' in str(htm['j_invariant'])
        assert 'moonshine' in str(htm['j_invariant']).lower()

    def test_poisson_summation(self):
        htm = heat_trace_modular()
        assert 'Self-dual' in htm['poisson_summation']['for_E8']

    def test_jacobi(self):
        htm = heat_trace_modular()
        assert 'theta_3' in str(htm['jacobi'])


class TestChain:
    def test_links(self):
        ch = complete_chain_w33_to_spectral()
        assert len(ch['links']) == 8
        assert 'W(3,3)' in ch['links'][0]['from']

    def test_miracle(self):
        ch = complete_chain_w33_to_spectral()
        assert 'SPECTRAL' in ch['miracle']['statement']

    def test_numerical_echoes(self):
        ch = complete_chain_w33_to_spectral()
        assert ch['numerical_echoes']['240'] is not None
        assert ch['numerical_echoes']['24'] is not None


class TestRunChecks:
    def test_all_pass(self):
        assert run_all_checks()

    def test_returns_bool(self):
        result = run_all_checks()
        assert isinstance(result, bool)
