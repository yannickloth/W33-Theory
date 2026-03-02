"""Tests for Pillar 169 (CCLXIX): Operads."""
import pytest
from THEORY_PART_CCLXIX_OPERADS import (
    operad_foundations,
    classical_operads,
    little_disks_operads,
    koszul_duality,
    infinity_structures,
    deformation_quantization,
    operads_in_physics,
    colored_and_higher,
    grothendieck_teichmuller,
    w33_operad_chain,
    run_self_checks,
)


# -- Foundations --
class TestOperadFoundations:
    def test_name(self):
        r = operad_foundations()
        assert 'operad' in r['name'].lower()

    def test_year(self):
        r = operad_foundations()
        assert r['year'] == 1972

    def test_definition_components(self):
        r = operad_foundations()
        assert 'composition' in r['definition']['components']

    def test_axioms(self):
        r = operad_foundations()
        for ax in ('associativity', 'identity', 'equivariance'):
            assert ax in r['definition']['axioms']

    def test_morphisms(self):
        r = operad_foundations()
        assert 'morphism' in r['morphisms']['definition'].lower() or 'preserv' in r['morphisms']['definition'].lower()


# -- Classical Operads --
class TestClassicalOperads:
    def test_endomorphism(self):
        r = classical_operads()
        assert 'hom' in r['endomorphism']['definition'].lower()

    def test_assoc_koszul_self_dual(self):
        r = classical_operads()
        assert 'assoc' in r['associative']['koszul_dual'].lower()

    def test_comm_lie_duality(self):
        r = classical_operads()
        assert 'lie' in r['commutative']['koszul_dual'].lower()

    def test_lie_jacobi(self):
        r = classical_operads()
        assert 'jacobi' in r['lie']['relation'].lower()

    def test_dimension_formulas(self):
        r = classical_operads()
        assert 'n!' in r['dimension_formula']['assoc_dim']


# -- Little Disks --
class TestLittleDisks:
    def test_definition(self):
        r = little_disks_operads()
        assert 'disk' in r['little_n_disks']['definition'].lower()

    def test_recognition(self):
        r = little_disks_operads()
        assert 'loop' in r['recognition_principle']['may_theorem'].lower()

    def test_homology(self):
        r = little_disks_operads()
        assert 'gerstenhaber' in r['homology']['e2_homology'].lower()

    def test_formality(self):
        r = little_disks_operads()
        assert 'kontsevich' in r['homology']['formality'].lower()


# -- Koszul Duality --
class TestKoszulDuality:
    def test_founders(self):
        r = koszul_duality()
        assert 'ginzburg' in r['founders'].lower()

    def test_comm_lie(self):
        r = koszul_duality()
        assert 'lie' in r['classical_dualities']['comm_lie'].lower()

    def test_a_infinity_resolution(self):
        r = koszul_duality()
        assert 'assoc' in r['resolutions']['a_infinity'].lower()


# -- Infinity Structures --
class TestInfinityStructures:
    def test_a_infinity_stasheff(self):
        r = infinity_structures()
        assert '1963' in r['a_infinity']['stasheff_1963']

    def test_l_infinity_deformation(self):
        r = infinity_structures()
        assert 'deform' in str(r['l_infinity']['applications']).lower()

    def test_e_infinity(self):
        r = infinity_structures()
        assert 'homotop' in r['e_infinity']['algebras'].lower() or 'commut' in r['e_infinity']['algebras'].lower()


# -- Deformation Quantization --
class TestDeformationQuantization:
    def test_kontsevich(self):
        r = deformation_quantization()
        assert 'formal' in r['kontsevich_formality']['theorem'].lower()

    def test_deligne_conjecture(self):
        r = deformation_quantization()
        assert 'hochschild' in r['deligne_conjecture']['statement'].lower()


# -- Physics --
class TestPhysics:
    def test_string_theory(self):
        r = operads_in_physics()
        assert 'moduli' in r['string_theory']['moduli_operad'].lower()

    def test_w33(self):
        r = operads_in_physics()
        assert 'w(3,3)' in r['w33_connection']['multi_input'].lower() or 'w33' in str(r['w33_connection']).lower()


# -- Colored and Higher --
class TestColoredHigher:
    def test_colored(self):
        r = colored_and_higher()
        assert 'color' in r['colored_operads']['definition'].lower()

    def test_props(self):
        r = colored_and_higher()
        assert 'output' in r['props']['definition'].lower()

    def test_modular(self):
        r = colored_and_higher()
        assert 'genus' in r['modular_operads']['definition'].lower()

    def test_infinity_operads(self):
        r = colored_and_higher()
        assert 'lurie' in r['infinity_operads']['lurie'].lower()


# -- GT Group --
class TestGT:
    def test_definition(self):
        r = grothendieck_teichmuller()
        assert 'gal' in r['gt_group']['definition'].lower()

    def test_operadic(self):
        r = grothendieck_teichmuller()
        assert 'e_2' in r['operadic_realization']['automorphisms'].lower() or 'aut' in r['operadic_realization']['automorphisms'].lower()

    def test_multiple_zeta(self):
        r = grothendieck_teichmuller()
        assert 'zeta' in r['connections']['multiple_zeta'].lower()


# -- W33 Chain --
class TestW33Chain:
    def test_chain(self):
        r = w33_operad_chain()
        assert 'e8' in str(r['chain']).lower()

    def test_dimensions(self):
        r = w33_operad_chain()
        assert '248' in str(r['operadic_dimensions'])

    def test_unification(self):
        r = w33_operad_chain()
        assert 'string' in str(r['unification']).lower()


# -- Self-Checks --
class TestSelfChecks:
    def test_all_pass(self):
        checks = run_self_checks()
        for name, val in checks:
            assert val, f"Self-check failed: {name}"

    def test_count(self):
        checks = run_self_checks()
        assert len(checks) == 15
