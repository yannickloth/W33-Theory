"""Tests for Pillar 174 — Symplectic Geometry."""

import pytest
from THEORY_PART_CCLXXIV_SYMPLECTIC_GEOMETRY import (
    symplectic_manifolds,
    hamiltonian_mechanics,
    lagrangian_submanifolds,
    gromov_nonsqueezing,
    floer_homology,
    fukaya_category,
    symplectic_reduction,
    contact_geometry,
    e8_symplectic_connection,
)


class TestSymplecticManifolds:
    def test_definition(self):
        r = symplectic_manifolds()
        assert 'dω = 0' in r['definition']['symplectic_form']
        assert '2n' in r['definition']['even_dimensional']
        assert 'orientable' in r['definition']['orientable'].lower()

    def test_darboux(self):
        r = symplectic_manifolds()
        assert '1882' in r['darboux_theorem']['year']
        assert 'local' in r['darboux_theorem']['statement'].lower()

    def test_examples(self):
        r = symplectic_manifolds()
        assert 'T*Q' in r['examples']['cotangent_bundle']
        assert 'Kähler' in r['examples']['kahler_manifolds']

    def test_symplectic_group(self):
        r = symplectic_manifolds()
        assert 'Sp(2n' in r['symplectic_group']['definition']
        assert 'U(n)' in r['symplectic_group']['maximal_compact']

    def test_cohomology(self):
        r = symplectic_manifolds()
        assert 'isomorphism' in r['cohomology']['hard_lefschetz']
        assert 'symplectic' in r['cohomology']['non_symplectic']


class TestHamiltonianMechanics:
    def test_hamiltons_equations(self):
        r = hamiltonian_mechanics()
        assert 'X_H' in r['hamiltons_equations']['hamiltonian_vector_field']
        assert 'symplectomorphism' in r['hamiltons_equations']['flow']

    def test_poisson_bracket(self):
        r = hamiltonian_mechanics()
        assert len(r['poisson_bracket']['properties']) >= 4
        assert 'Lie algebra' in r['poisson_bracket']['lie_algebra']

    def test_liouville(self):
        r = hamiltonian_mechanics()
        assert 'volume' in r['liouville_theorem']['statement'].lower()

    def test_noether(self):
        r = hamiltonian_mechanics()
        assert 'g*' in r['noether_moment_map']['moment_map']
        assert 'μ⁻¹(0)/G' in r['noether_moment_map']['marsden_weinstein']


class TestLagrangianSubmanifolds:
    def test_definition(self):
        r = lagrangian_submanifolds()
        assert 'ω|_L = 0' in r['definition']['conditions']
        assert 'isotropic' in r['definition']['maximal_isotropic'].lower()

    def test_examples(self):
        r = lagrangian_submanifolds()
        assert 'Zero section' in r['examples']['zero_section']
        assert 'dS' in r['examples']['graph_of_dS']

    def test_arnold_conjecture(self):
        r = lagrangian_submanifolds()
        assert 'Floer' in r['arnold_conjecture']['proof']
        assert 'fixed point' in r['arnold_conjecture']['statement'].lower()

    def test_weinstein(self):
        r = lagrangian_submanifolds()
        assert 'T*L' in r['weinstein']['theorem']


class TestGromovNonsqueezing:
    def test_nonsqueezing(self):
        r = gromov_nonsqueezing()
        assert 'r ≤ R' in r['nonsqueezing']['theorem']
        assert '1985' in r['nonsqueezing']['year']
        assert 'camel' in r['nonsqueezing']['nickname'].lower()

    def test_capacities(self):
        r = gromov_nonsqueezing()
        assert 'π' in r['capacities']['normalized']
        assert 'sup' in r['capacities']['gromov_width']

    def test_rigidity(self):
        r = gromov_nonsqueezing()
        assert 'closed' in r['rigidity']['symplectic_rigidity']
        assert 'Fibonacci' in r['rigidity']['mcduff_schlenk']


class TestFloerHomology:
    def test_hamiltonian_floer(self):
        r = floer_homology()
        assert 'periodic' in r['hamiltonian_floer']['critical_points'].lower()
        assert 'holomorphic' in r['hamiltonian_floer']['gradient_flow'].lower() or 'J' in r['hamiltonian_floer']['gradient_flow']

    def test_properties(self):
        r = floer_homology()
        assert 'QH' in r['properties']['pss_isomorphism']
        assert 'Arnold' in r['properties']['arnold_conjecture']

    def test_lagrangian_floer(self):
        r = floer_homology()
        assert 'intersection' in r['lagrangian_floer']['generators']
        assert 'strip' in r['lagrangian_floer']['differential']


class TestFukayaCategory:
    def test_definition(self):
        r = fukaya_category()
        assert 'Lagrangian' in r['definition']['objects']
        assert 'triangle' in r['definition']['composition'].lower()

    def test_mirror_symmetry(self):
        r = fukaya_category()
        assert '1994' in r['mirror_symmetry']['year']
        assert 'Kontsevich' in r['mirror_symmetry']['year']
        assert 'DFuk' in r['mirror_symmetry']['kontsevich_conjecture']

    def test_wrapped(self):
        r = fukaya_category()
        assert 'Abouzaid' in r['wrapped']['generation']


class TestSymplecticReduction:
    def test_marsden_weinstein(self):
        r = symplectic_reduction()
        assert 'μ⁻¹(0)/G' in r['marsden_weinstein']['reduced_space']
        assert '2·dim(G)' in r['marsden_weinstein']['dimension']

    def test_examples(self):
        r = symplectic_reduction()
        assert 'ℂPⁿ' in r['examples']['projective_space']
        assert 'toric' in r['examples']['toric_manifolds'].lower()

    def test_convexity(self):
        r = symplectic_reduction()
        assert 'convex polytope' in r['convexity']['theorem']
        assert '1982' in r['convexity']['year']


class TestContactGeometry:
    def test_definition(self):
        r = contact_geometry()
        assert 'α' in r['definition']['contact_form']
        assert '2n+1' in r['definition']['odd_dimensional']

    def test_reeb(self):
        r = contact_geometry()
        assert 'Reeb orbit' in r['reeb']['weinstein_conjecture']
        assert 'Taubes' in r['reeb']['proved_dim3']


class TestE8SymplecticConnection:
    def test_e8_coadjoint(self):
        r = e8_symplectic_connection()
        assert 'coadjoint' in r['e8_coadjoint']['coadjoint_orbits']
        assert '240' in str(r['e8_coadjoint']['dimension_248'])

    def test_gauge_theory(self):
        r = e8_symplectic_connection()
        assert 'curvature' in r['gauge_theory']['moment_map'].lower()

    def test_w33_chain(self):
        r = e8_symplectic_connection()
        assert 'Fukaya' in r['w33_chain']['fukaya']
        assert 'mirror' in r['w33_chain']['mirror'].lower()

    def test_sft(self):
        r = e8_symplectic_connection()
        assert 'Kontsevich' in r['sft']['quantization']
