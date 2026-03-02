"""
Tests for Pillar 147: Twistor Theory & The Amplituhedron.
"""

import pytest
from THEORY_PART_CCXLVII_TWISTOR_AMPLITUHEDRON import (
    twistor_space,
    ward_construction,
    twistor_string_theory,
    bcfw_recursion,
    scattering_amplitudes,
    positive_grassmannian,
    amplituhedron,
    mhv_amplitudes,
    supertwistors,
    momentum_twistors,
    exceptional_connections,
    complete_chain_w33_to_twistors,
    run_all_checks,
)


class TestTwistorSpace:
    def test_basics(self):
        ts = twistor_space()
        assert ts['year'] == 1967
        assert ts['introduced_by'] == 'Roger Penrose'

    def test_cp3(self):
        ts = twistor_space()
        assert 'CP^3' in ts['definition']['PT']

    def test_penrose_transform(self):
        ts = twistor_space()
        assert 'scalar' in ts['penrose_transform']['examples']
        assert 'graviton' in ts['penrose_transform']['examples']

    def test_incidence(self):
        ts = twistor_space()
        assert 'omega' in ts['incidence_relation']['formula']

    def test_fundamental_insight(self):
        ts = twistor_space()
        assert 'SECONDARY' in ts['fundamental_insight']['statement']


class TestWardConstruction:
    def test_basics(self):
        wc = ward_construction()
        assert wc['year'] == 1977
        assert 'Ward' in wc['author']

    def test_adhm(self):
        wc = ward_construction()
        assert wc['adhm']['year'] == 1978
        assert 'Atiyah' in wc['adhm']['authors']

    def test_nonlinear_graviton(self):
        wc = ward_construction()
        assert wc['nonlinear_graviton']['year'] == 1976


class TestTwistorStringTheory:
    def test_basics(self):
        wts = twistor_string_theory()
        assert wts['year'] == 2003
        assert wts['author'] == 'Edward Witten'

    def test_target_space(self):
        wts = twistor_string_theory()
        assert 'CP' in wts['key_ideas']['target_space']

    def test_n4_sym(self):
        wts = twistor_string_theory()
        assert len(wts['n4_sym']['properties']) >= 4


class TestBCFW:
    def test_basics(self):
        bcfw = bcfw_recursion()
        assert bcfw['year'] == 2005
        assert 'Britto' in str(bcfw['authors'])

    def test_revolution(self):
        bcfw = bcfw_recursion()
        assert 'n!' in bcfw['revolution']['before']
        assert 'n^2' in bcfw['revolution']['after']

    def test_parke_taylor(self):
        bcfw = bcfw_recursion()
        assert bcfw['parke_taylor']['year'] == 1986

    def test_yangian(self):
        bcfw = bcfw_recursion()
        assert 'Yangian' in bcfw['twistor_formulation']['yangian']


class TestScatteringAmplitudes:
    def test_bcj(self):
        sa = scattering_amplitudes()
        assert sa['color_kinematics']['year'] == 2008

    def test_double_copy(self):
        sa = scattering_amplitudes()
        assert 'Gravity' in sa['color_kinematics']['double_copy']

    def test_klt(self):
        sa = scattering_amplitudes()
        assert sa['klt']['year'] == 1986
        assert 'square' in sa['klt']['interpretation'].lower()

    def test_soft_theorems(self):
        sa = scattering_amplitudes()
        assert 'BMS' in str(sa['soft_theorems'])


class TestPositiveGrassmannian:
    def test_basics(self):
        pg = positive_grassmannian()
        assert pg['year'] == 2012
        assert 'Arkani-Hamed' in str(pg['key_developers'])

    def test_grassmannian(self):
        pg = positive_grassmannian()
        assert 'k*(n-k)' in pg['grassmannian']['dimension']


class TestAmplituhedron:
    def test_basics(self):
        amp = amplituhedron()
        assert amp['year'] == 2013
        assert 'Arkani-Hamed' in str(amp['authors'])

    def test_emergent(self):
        amp = amplituhedron()
        assert amp['key_properties']['locality_emergent']
        assert amp['key_properties']['unitarity_emergent']

    def test_physics(self):
        amp = amplituhedron()
        assert 'N=4' in amp['physics']['theory']

    def test_implications(self):
        amp = amplituhedron()
        assert 'derived' in amp['implications']['spacetime_emergent'].lower()


class TestMHV:
    def test_parke_taylor(self):
        m = mhv_amplitudes()
        assert m['parke_taylor']['year'] == 1986
        assert '<ij>^4' in m['parke_taylor']['formula']

    def test_spinor_helicity(self):
        m = mhv_amplitudes()
        assert '<ij>' in m['spinor_helicity']['notation']

    def test_classification(self):
        m = mhv_amplitudes()
        assert 'MHV' in m['classification']
        assert 'NMHV' in m['classification']


class TestSupertwistors:
    def test_basics(self):
        st = supertwistors()
        assert st['year'] == 1978
        assert 'Ferber' in st['introduced_by']

    def test_n4_states(self):
        st = supertwistors()
        assert '16' in st['n4_sym']['total_states']

    def test_e8_connection(self):
        st = supertwistors()
        assert 'W(3,3)' in st['e8_connection']['w33_chain']


class TestMomentumTwistors:
    def test_basics(self):
        mt = momentum_twistors()
        assert mt['year'] == 2009
        assert 'Hodges' in mt['introduced_by']

    def test_advantages(self):
        mt = momentum_twistors()
        assert mt['advantages']['amplituhedron_lives_here'] is not None


class TestExceptional:
    def test_e_type(self):
        ec = exceptional_connections()
        assert 'E7' in str(ec['e_type']['e7_in_4d'])

    def test_chain(self):
        ec = exceptional_connections()
        assert 'W(3,3)' in str(ec['w33_chain']['path'])

    def test_division_algebras(self):
        ec = exceptional_connections()
        assert 'dim 3, 4, 6, 10' in ec['octonion_connection']['baez_huerta']


class TestChain:
    def test_links(self):
        ch = complete_chain_w33_to_twistors()
        assert len(ch['links']) == 6
        assert 'W(3,3)' in ch['links'][0]['from']

    def test_miracle(self):
        ch = complete_chain_w33_to_twistors()
        assert 'EMERGENT' in ch['miracle']['statement']

    def test_prizes(self):
        ch = complete_chain_w33_to_twistors()
        assert 'Nobel' in ch['prizes']['penrose_2020']


class TestRunChecks:
    def test_all_pass(self):
        assert run_all_checks()

    def test_returns_bool(self):
        assert isinstance(run_all_checks(), bool)
