"""
Tests for Pillar 179 -- Amplituhedron & Positive Geometry from W(3,3)
"""
import pytest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))
from THEORY_PART_CCLXXIX_AMPLITUHEDRON_POSITIVE_GEOMETRY import (
    amplituhedron_basics, bcfw_recursion,
    positive_geometry, associahedron_connection,
    cosmological_polytopes, emergent_spacetime
)


class TestAmplituhedronBasics:
    def test_grassmannian(self):
        r = amplituhedron_basics()
        assert 'Grassmannian' in r['definition']['space']

    def test_discoverers_2013(self):
        r = amplituhedron_basics()
        assert '2013' in r['definition']['discoverers']

    def test_positive_grassmannian(self):
        r = amplituhedron_basics()
        assert 'positive' in r['grassmannian']['positive'].lower()

    def test_40_vertices(self):
        r = amplituhedron_basics()
        assert r['w33_connection']['vertex_count'] == 40

    def test_240_edges(self):
        r = amplituhedron_basics()
        assert r['w33_connection']['edge_count'] == 240

    def test_positroid(self):
        r = amplituhedron_basics()
        assert 'positroid' in r['grassmannian']['cells'].lower()


class TestBCFW:
    def test_year_2005(self):
        r = bcfw_recursion()
        assert '2005' in r['bcfw']['year']

    def test_on_shell_shift(self):
        r = bcfw_recursion()
        assert 'shift' in r['bcfw']['deformation'].lower() or 'Shift' in r['bcfw']['deformation']

    def test_plabic_graphs(self):
        r = bcfw_recursion()
        assert 'plabic' in r['on_shell_diagrams']['plabic_graphs']

    def test_recursion_formula(self):
        r = bcfw_recursion()
        assert 'A_n' in r['bcfw']['recursion'] or 'sum' in r['bcfw']['recursion']

    def test_w33_n6(self):
        r = bcfw_recursion()
        assert 'n=6' in r['w33_bcfw']['n_equals_6'] or '6' in r['w33_bcfw']['n_equals_6']


class TestPositiveGeometry:
    def test_log_singularities(self):
        r = positive_geometry()
        assert 'log' in r['axioms']['log_singularities'].lower()

    def test_recursive_axiom(self):
        r = positive_geometry()
        assert 'Res' in r['axioms']['recursion'] or 'recursive' in r['axioms']['recursion']

    def test_simplex_volume(self):
        r = positive_geometry()
        assert '1/n!' in r['simplex']['volume']

    def test_w33_boundary(self):
        r = positive_geometry()
        assert '40' in r['w33_positive']['boundary_structure']

    def test_canonical_form(self):
        r = positive_geometry()
        assert 'canonical' in r['axioms']['canonical_form'].lower() or 'Omega' in r['axioms']['canonical_form']


class TestAssociahedron:
    def test_catalan_vertices(self):
        r = associahedron_connection()
        assert 'Catalan' in r['associahedron']['vertices']

    def test_c5_equals_42(self):
        r = associahedron_connection()
        assert r['catalan']['c_5'] == 42

    def test_c4_equals_14(self):
        r = associahedron_connection()
        assert r['catalan']['c_4'] == 14

    def test_catalan_values(self):
        r = associahedron_connection()
        assert r['catalan']['values'][:5] == [1, 1, 2, 5, 14]

    def test_bcj_duality(self):
        r = associahedron_connection()
        assert 'Bern' in r['color_kinematics']['bcj_duality'] or 'BCJ' in r['color_kinematics']['bcj_duality']

    def test_double_copy(self):
        r = associahedron_connection()
        assert 'Gravity' in r['color_kinematics']['double_copy'] or 'gravity' in r['color_kinematics']['double_copy'].lower()


class TestCosmologicalPolytopes:
    def test_year_2017(self):
        r = cosmological_polytopes()
        assert '2017' in r['cosmo_polytopes']['year']

    def test_wavefunction(self):
        r = cosmological_polytopes()
        assert 'wavefunction' in r['w33_cosmology']['wavefunction'].lower()

    def test_surfacehedra(self):
        r = cosmological_polytopes()
        assert 'surfacehedra' in r

    def test_multiverse_40(self):
        r = cosmological_polytopes()
        assert '40' in r['w33_cosmology']['multiverse']


class TestEmergentSpacetime:
    def test_locality_emerges(self):
        r = emergent_spacetime()
        assert 'EMERGES' in r['locality']['amplituhedron']

    def test_unitarity_emerges(self):
        r = emergent_spacetime()
        assert 'EMERGES' in r['unitarity']['amplituhedron']

    def test_dim_10(self):
        r = emergent_spacetime()
        assert '10' in r['w33_emergence']['dim_10']

    def test_gravity_double_copy(self):
        r = emergent_spacetime()
        assert 'double copy' in r['w33_emergence']['gravity_from_w33']

    def test_gauge_from_w33(self):
        r = emergent_spacetime()
        assert 'Grassmannian' in r['w33_emergence']['gauge_from_w33']


class TestSelfChecks:
    def test_all_pass(self):
        from THEORY_PART_CCLXXIX_AMPLITUHEDRON_POSITIVE_GEOMETRY import run_self_checks
        assert run_self_checks() is True
