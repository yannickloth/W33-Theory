"""Tests for Pillar 175 — Tropical Geometry."""

import pytest
from THEORY_PART_CCLXXV_TROPICAL_GEOMETRY import (
    tropical_semiring,
    tropical_varieties,
    tropical_curves,
    tropical_linear_algebra,
    tropical_grassmannian,
    tropical_mirror_symmetry,
    tropical_arithmetic,
    e8_tropical_connection,
)


class TestTropicalSemiring:
    def test_definition(self):
        r = tropical_semiring()
        assert 'min' in r['definition']['addition']
        assert '∞' in r['definition']['zero']
        assert '0' in r['definition']['one']

    def test_properties(self):
        r = tropical_semiring()
        assert 'idempotent' in r['properties']['idempotent']
        assert 'min' in r['properties']['distributive']
        assert 'inverse' in r['properties']['not_ring'].lower()

    def test_conventions(self):
        r = tropical_semiring()
        assert 'min' in r['conventions']['min_plus']
        assert 'max' in r['conventions']['max_plus']

    def test_polynomials(self):
        r = tropical_semiring()
        assert 'piecewise' in r['polynomials']['piecewise_linear'].lower()
        assert 'minimum' in r['polynomials']['tropical_root'].lower()


class TestTropicalVarieties:
    def test_hypersurface(self):
        r = tropical_varieties()
        assert 'polyhedral' in r['hypersurface']['structure'].lower()
        assert 'Newton' in r['hypersurface']['dual_subdivision']

    def test_balancing(self):
        r = tropical_varieties()
        assert 'balanced' in r['balancing']['structure_theorem'].lower()
        assert 'weight' in r['balancing']['multiplicity'].lower()

    def test_tropicalization(self):
        r = tropical_varieties()
        assert 'valuation' in r['tropicalization']['valuation'].lower()
        assert 'Kapranov' in r['tropicalization']['kapranov']

    def test_intersection(self):
        r = tropical_varieties()
        assert 'Bézout' in r['intersection']['bezout'] or 'Bezout' in r['intersection']['bezout']


class TestTropicalCurves:
    def test_abstract(self):
        r = tropical_curves()
        assert 'metric graph' in r['abstract']['definition'].lower()
        assert 'b₁' in r['abstract']['genus']

    def test_plane_curves(self):
        r = tropical_curves()
        assert 'balanced' in r['plane_curves']['definition'].lower()

    def test_mikhalkin(self):
        r = tropical_curves()
        assert '2005' in r['mikhalkin']['year']
        assert 'Annals' in r['mikhalkin']['year']
        assert 'enumerative' in r['mikhalkin']['significance'].lower()

    def test_jacobian(self):
        r = tropical_curves()
        assert 'Baker-Norine' in r['jacobian']['baker_norine']
        assert 'Riemann-Roch' in r['jacobian']['riemann_roch']


class TestTropicalLinearAlgebra:
    def test_matrices(self):
        r = tropical_linear_algebra()
        assert 'min' in r['matrices']['tropical_product']
        assert 'path' in r['matrices']['interpretation'].lower()

    def test_determinant(self):
        r = tropical_linear_algebra()
        assert 'assignment' in r['determinant']['assignment_problem']
        assert 'Hungarian' in r['determinant']['hungarian']

    def test_convexity(self):
        r = tropical_linear_algebra()
        assert 'polyhedral' in r['convexity']['develin_sturmfels'].lower()

    def test_optimization(self):
        r = tropical_linear_algebra()
        assert 'scheduling' in r['optimization']['scheduling'].lower()


class TestTropicalGrassmannian:
    def test_definition(self):
        r = tropical_grassmannian()
        assert 'phylogenetic' in r['definition']['gr_2_n']
        assert 'Speyer' in r['definition']['year']

    def test_matroids(self):
        r = tropical_grassmannian()
        assert 'matroid' in r['matroids']['tropical_linear_space']
        assert 'Bergman' in r['matroids']['bergman_fan']

    def test_phylogenetics(self):
        r = tropical_grassmannian()
        assert 'tree' in r['phylogenetics']['tree_space'].lower()
        assert 'biology' in r['phylogenetics']['applications'].lower()


class TestTropicalMirrorSymmetry:
    def test_syz(self):
        r = tropical_mirror_symmetry()
        assert 'Gross-Siebert' in r['syz']['gross_siebert']
        assert 'SYZ' in r['syz']['conjecture'] or 'torus' in r['syz']['conjecture'].lower()

    def test_enumerative(self):
        r = tropical_mirror_symmetry()
        assert 'Gromov-Witten' in r['enumerative']['gromov_witten']

    def test_amoebas(self):
        r = tropical_mirror_symmetry()
        assert 'Log' in r['amoebas']['definition'] or 'log' in r['amoebas']['definition']
        assert 'spine' in r['amoebas']['spine'].lower()

    def test_feynman(self):
        r = tropical_mirror_symmetry()
        assert 'Feynman' in r['feynman']['tropical']


class TestTropicalArithmetic:
    def test_non_archimedean(self):
        r = tropical_arithmetic()
        assert 'Berkovich' in r['non_archimedean']['berkovich']
        assert 'skeleton' in r['non_archimedean']['skeleton'].lower()

    def test_moduli(self):
        r = tropical_arithmetic()
        assert 'cone complex' in r['moduli']['M_g_n_trop']
        assert '2021' in r['moduli']['chan_galatius_payne']


class TestE8TropicalConnection:
    def test_e8_tropical(self):
        r = e8_tropical_connection()
        assert '240' in r['e8_tropical']['dimension']
        assert 'root' in r['e8_tropical']['root_system'].lower()

    def test_tropical_lie(self):
        r = e8_tropical_connection()
        assert '696729600' in r['tropical_lie']['weyl_group']

    def test_w33_chain(self):
        r = e8_tropical_connection()
        assert 'W33' in r['w33_chain']['tropical_limit']
        assert 'bridge' in r['w33_chain']['architecture'].lower()

    def test_computation(self):
        r = e8_tropical_connection()
        assert 'polymake' in r['computation']['polymake'].lower()
