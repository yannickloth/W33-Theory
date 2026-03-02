"""
Tests for Pillar 158: Tropical Geometry
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))

from THEORY_PART_CCLVIII_TROPICAL_GEOMETRY import (
    tropical_semiring,
    tropical_polynomials,
    tropicalization,
    mikhalkin_correspondence,
    tropical_mirror,
    tropical_curves,
    tropical_physics,
    tropical_grassmannian,
    newton_polygon,
    tropical_clusters,
    tropical_e8,
    complete_chain,
    run_all_checks,
)


class TestTropicalSemiring:
    def test_min(self):
        ts = tropical_semiring()
        assert 'min' in ts['min_convention']['addition']

    def test_plus(self):
        ts = tropical_semiring()
        assert 'x + y' in ts['min_convention']['multiplication']

    def test_simon(self):
        ts = tropical_semiring()
        assert 'Simon' in ts['origin']['named_after']


class TestTropicalPolynomials:
    def test_piecewise_linear(self):
        tp = tropical_polynomials()
        assert 'piecewise-linear' in tp['definition']['properties']

    def test_hypersurface(self):
        tp = tropical_polynomials()
        assert 'twice' in tp['tropical_hypersurface']['definition']


class TestTropicalization:
    def test_fundamental_theorem(self):
        tr = tropicalization()
        assert 'Fundamental Theorem' in tr['map']['fundamental_theorem']

    def test_three_definitions(self):
        assert len(tropicalization()['three_definitions']) == 3

    def test_amoeba(self):
        tr = tropicalization()
        assert 'amoeba' in tr['amoeba']['non_archimedean'].lower()


class TestMikhalkin:
    def test_year(self):
        assert mikhalkin_correspondence()['year'] == 2005

    def test_author(self):
        assert 'Mikhalkin' in mikhalkin_correspondence()['author']

    def test_gw(self):
        mc = mikhalkin_correspondence()
        assert 'Gromov-Witten' in mc['significance']['gromov_witten']


class TestTropicalMirror:
    def test_gross(self):
        tm = tropical_mirror()
        assert 'Gross' in tm['gross_siebert']['authors'][0]

    def test_syz(self):
        tm = tropical_mirror()
        assert 'Strominger' in tm['syz']['name']


class TestTropicalCurves:
    def test_baker_norine(self):
        tc = tropical_curves()
        assert tc['baker_norine']['year'] == 2007

    def test_riemann_roch(self):
        tc = tropical_curves()
        assert 'Riemann-Roch' in tc['baker_norine']['theorem']


class TestTropicalPhysics:
    def test_relu(self):
        tp = tropical_physics()
        assert 'ReLU' in tp['neural_networks']['relu']

    def test_tourkine(self):
        tp = tropical_physics()
        assert 'Tourkine' in tp['string_amplitudes']['tourkine']


class TestTropicalGrassmannian:
    def test_phylogenetics(self):
        tg = tropical_grassmannian()
        assert 'phylogenetic' in tg['phylogenetics']['connection'].lower()


class TestNewtonPolygon:
    def test_viro(self):
        np_r = newton_polygon()
        assert 'Viro' in np_r['viro_patchworking']['author']


class TestTropicalClusters:
    def test_fock_goncharov(self):
        tc = tropical_clusters()
        assert 'Fock-Goncharov' in tc['connections']['fock_goncharov']


class TestTropicalE8:
    def test_w33(self):
        te8 = tropical_e8()
        assert any('W(3,3)' in p for p in te8['w33_chain']['path'])

    def test_27_lines(self):
        te8 = tropical_e8()
        assert '27' in te8['connections']['del_pezzo']['27_lines']


class TestCompleteChain:
    def test_length(self):
        assert len(complete_chain()['links']) == 6

    def test_miracle(self):
        assert 'MIN AND PLUS' in complete_chain()['miracle']['statement']

    def test_starts_w33(self):
        assert complete_chain()['links'][0]['from'] == 'W(3,3)'


class TestRunAllChecks:
    def test_all_pass(self):
        assert run_all_checks() is True
