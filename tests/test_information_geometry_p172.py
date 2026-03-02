"""Tests for Pillar 172 (CCLXXII): Information Geometry."""
import pytest
from THEORY_PART_CCLXXII_INFORMATION_GEOMETRY import (
    information_geometry_foundations,
    dual_connections,
    exponential_families,
    natural_gradient,
    divergence_functions,
    quantum_information_geometry,
    physics_applications,
    optimization_geometry,
    e8_information_geometry,
    w33_information_chain,
    run_self_checks,
)


class TestFoundations:
    def test_name(self):
        r = information_geometry_foundations()
        assert 'information' in r['name'].lower()

    def test_founders(self):
        r = information_geometry_foundations()
        assert 'rao' in r['founders'].lower()

    def test_fisher_metric(self):
        r = information_geometry_foundations()
        assert 'fisher' in r['fisher_metric']['name'].lower()

    def test_chentsov(self):
        r = information_geometry_foundations()
        assert 'unique' in r['chentsov_theorem']['statement'].lower()

    def test_statistical_manifold(self):
        r = information_geometry_foundations()
        assert 'probabilit' in r['statistical_manifold']['definition'].lower() or 'distribut' in r['statistical_manifold']['definition'].lower()


class TestDualConnections:
    def test_alpha(self):
        r = dual_connections()
        assert 'alpha' in str(r['alpha_connections']['definition']).lower()

    def test_duality(self):
        r = dual_connections()
        assert 'dual' in r['duality']['e_m_dual'].lower()

    def test_e_m_values(self):
        r = dual_connections()
        assert 'exponential' in r['alpha_connections']['alpha_values']['alpha_1'].lower()

    def test_skewness(self):
        r = dual_connections()
        assert 'tensor' in r['torsion']['skewness_tensor'].lower()


class TestExponentialFamilies:
    def test_form(self):
        r = exponential_families()
        assert 'exp' in r['definition']['form'].lower() or 'theta' in r['definition']['form'].lower()

    def test_dually_flat(self):
        r = exponential_families()
        assert 'flat' in r['dually_flat']['e_flat'].lower()

    def test_kl_bregman(self):
        r = exponential_families()
        assert 'bregman' in r['kl_divergence']['equals_bregman'].lower()

    def test_legendre(self):
        r = exponential_families()
        assert 'legendre' in r['dually_flat']['legendre_duality'].lower()


class TestNaturalGradient:
    def test_definition(self):
        r = natural_gradient()
        assert 'fisher' in r['amari_natural_gradient']['definition'].lower() or 'G^{-1}' in r['amari_natural_gradient']['definition']

    def test_amari_1998(self):
        r = natural_gradient()
        assert 'amari' in r['amari_natural_gradient']['amari_1998'].lower()

    def test_invariance(self):
        r = natural_gradient()
        assert 'invariant' in r['amari_natural_gradient']['invariance'].lower() or 'reparam' in r['amari_natural_gradient']['invariance'].lower()

    def test_applications(self):
        r = natural_gradient()
        assert 'neural' in str(r['applications']).lower()


class TestDivergences:
    def test_kl(self):
        r = divergence_functions()
        assert 'kullback' in r['examples']['kl_divergence'].lower()

    def test_f_divergence(self):
        r = divergence_functions()
        assert 'csiszar' in r['examples']['f_divergence'].lower() or 'f(' in r['examples']['f_divergence']

    def test_metric_from_divergence(self):
        r = divergence_functions()
        assert 'fisher' in r['geometric_meaning']['metric_from_divergence'].lower()


class TestQuantum:
    def test_density_matrices(self):
        r = quantum_information_geometry()
        assert 'positive' in r['quantum_states']['density_matrices'].lower() or 'rho' in r['quantum_states']['density_matrices'].lower()

    def test_sld_fisher(self):
        r = quantum_information_geometry()
        assert 'fisher' in r['quantum_fisher']['sld_fisher'].lower()

    def test_cramer_rao(self):
        r = quantum_information_geometry()
        assert 'cramer' in r['quantum_estimation']['cramer_rao'].lower() or 'bound' in r['quantum_estimation']['cramer_rao'].lower()


class TestPhysics:
    def test_ruppeiner(self):
        r = physics_applications()
        assert 'ruppeiner' in r['thermodynamics']['ruppeiner_geometry'].lower()

    def test_zamolodchikov(self):
        r = physics_applications()
        assert 'zamolodchikov' in r['string_theory']['zamolodchikov_metric'].lower()

    def test_ising(self):
        r = physics_applications()
        assert 'ising' in r['statistical_mechanics']['ising_model'].lower()


class TestOptimization:
    def test_mirror_descent(self):
        r = optimization_geometry()
        assert 'bregman' in r['mirror_descent']['definition'].lower()

    def test_em(self):
        r = optimization_geometry()
        assert 'projection' in r['em_algorithm']['e_step'].lower()

    def test_variational(self):
        r = optimization_geometry()
        assert 'kl' in r['variational_methods']['variational_inference'].lower() or 'variat' in r['variational_methods']['variational_inference'].lower()


class TestE8:
    def test_killing(self):
        r = e8_information_geometry()
        assert 'killing' in r['lie_group_geometry']['e8_killing'].lower()

    def test_248(self):
        r = e8_information_geometry()
        assert '248' in r['representation_manifold']['fisher_on_248']

    def test_w33_synthesis(self):
        r = e8_information_geometry()
        assert 'w(3,3)' in r['w33_synthesis']['w33_statistical'].lower() or 'w33' in str(r['w33_synthesis']).lower()


class TestW33Chain:
    def test_chain(self):
        r = w33_information_chain()
        assert 'e8' in str(r['chain']).lower()

    def test_synthesis(self):
        r = w33_information_chain()
        assert 'fisher' in str(r['synthesis']).lower() or 'information' in str(r['synthesis']).lower()


class TestSelfChecks:
    def test_all_pass(self):
        checks = run_self_checks()
        for name, val in checks:
            assert val, f"Self-check failed: {name}"

    def test_count(self):
        checks = run_self_checks()
        assert len(checks) == 15
