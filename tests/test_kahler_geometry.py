"""Tests for Pillar 188 - Kahler Geometry & Calabi-Yau Metrics."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P188():
    return importlib.import_module("THEORY_PART_CCLXXXVIII_KAHLER_GEOMETRY")

# ── kahler_manifolds ──────────────────────────────────────
class TestKahlerManifolds:
    def test_kahler_def(self, P188):
        r = P188.kahler_manifolds()
        assert 'Kahler' in r['kahler_structure']['definition']

    def test_hodge_decomposition(self, P188):
        r = P188.kahler_manifolds()
        assert 'Hodge' in r['hodge']['decomposition']

    def test_hard_lefschetz(self, P188):
        r = P188.kahler_manifolds()
        assert 'Lefschetz' in r['hodge']['hard_lefschetz'] or 'isomorphism' in r['hodge']['hard_lefschetz']

    def test_hodge_conjecture(self, P188):
        r = P188.kahler_manifolds()
        assert 'Millennium' in r['hodge']['hodge_conjecture'] or 'algebraic' in r['hodge']['hodge_conjecture']

    def test_w33_kahler(self, P188):
        r = P188.kahler_manifolds()
        assert 'W(3,3)' in r['w33_kahler']['finite_kahler']

# ── calabi_yau_theorem ─────────────────────────────────────
class TestCalabiYauTheorem:
    def test_calabi_1954(self, P188):
        r = P188.calabi_yau_theorem()
        assert '1954' in r['calabi']['conjecture']

    def test_yau_1978(self, P188):
        r = P188.calabi_yau_theorem()
        assert '1978' in r['yau']['year']

    def test_fields_medal(self, P188):
        r = P188.calabi_yau_theorem()
        assert 'Fields' in r['yau']['fields_medal']

    def test_monge_ampere(self, P188):
        r = P188.calabi_yau_theorem()
        assert 'Monge-Ampere' in r['calabi']['monge_ampere']

    def test_cy3(self, P188):
        r = P188.calabi_yau_theorem()
        assert 'CY3' in r['cy_manifolds']['cy3'] or 'complex dimension 3' in r['cy_manifolds']['cy3']

    def test_quintic(self, P188):
        r = P188.calabi_yau_theorem()
        assert 'quintic' in r['cy_manifolds']['examples'].lower() or 'Quintic' in r['cy_manifolds']['examples']

# ── kahler_einstein ────────────────────────────────────────
class TestKahlerEinstein:
    def test_ytd(self, P188):
        r = P188.kahler_einstein()
        assert 'K-polystable' in r['ytd']['statement'] or 'K-stability' in r['ytd']['statement']

    def test_cds_2015(self, P188):
        r = P188.kahler_einstein()
        assert '2015' in r['ytd']['chen_donaldson_sun']

    def test_fano(self, P188):
        r = P188.kahler_einstein()
        assert 'Fano' in r['ke_metrics']['fano']

    def test_futaki(self, P188):
        r = P188.kahler_einstein()
        assert 'Futaki' in r['ke_metrics']['obstruction']

# ── special_holonomy ──────────────────────────────────────
class TestSpecialHolonomy:
    def test_g2_dim7(self, P188):
        r = P188.special_holonomy()
        assert r['g2_manifolds']['dimension'] == 7

    def test_joyce(self, P188):
        r = P188.special_holonomy()
        assert 'Joyce' in r['g2_manifolds']['joyce']

    def test_su_n(self, P188):
        r = P188.special_holonomy()
        assert 'SU(n)' in r['berger']['su_n']

    def test_spin7(self, P188):
        r = P188.special_holonomy()
        assert 'Spin(7)' in r['berger']['spin7']

    def test_m_theory(self, P188):
        r = P188.special_holonomy()
        assert 'M-theory' in r['g2_manifolds']['m_theory']

# ── mirror_symmetry_deep ──────────────────────────────────
class TestMirrorSymmetryDeep:
    def test_2875_lines(self, P188):
        r = P188.mirror_symmetry_deep()
        assert r['enumerative']['n_1'] == 2875

    def test_609250_conics(self, P188):
        r = P188.mirror_symmetry_deep()
        assert r['enumerative']['n_2'] == 609250

    def test_kontsevich_hms(self, P188):
        r = P188.mirror_symmetry_deep()
        assert 'Kontsevich' in r['mirror']['homological']

    def test_syz(self, P188):
        r = P188.mirror_symmetry_deep()
        assert 'SYZ' in r['mirror']['syz'] or 'T-dual' in r['mirror']['syz']

    def test_self_mirror(self, P188):
        r = P188.mirror_symmetry_deep()
        assert 'self-mirror' in r['w33_mirror']['self_mirror']

# ── metrics_and_geometry ──────────────────────────────────
class TestMetricsAndGeometry:
    def test_fubini_study(self, P188):
        r = P188.metrics_and_geometry()
        assert 'Fubini-Study' in r['explicit_metrics']['fubini_study']

    def test_diameter(self, P188):
        r = P188.metrics_and_geometry()
        assert '2' in r['w33_geometry']['diameter']

    def test_girth(self, P188):
        r = P188.metrics_and_geometry()
        assert '3' in r['w33_geometry']['girth']

    def test_kahler_ricci_flow(self, P188):
        r = P188.metrics_and_geometry()
        assert 'Kahler-Ricci' in r['flows']['kahler_ricci'] or 'Ricci' in r['flows']['kahler_ricci']

    def test_numerical_metrics(self, P188):
        r = P188.metrics_and_geometry()
        assert 'Donaldson' in r['explicit_metrics']['numerical'] or 'numerical' in r['explicit_metrics']['numerical']

# ── self-checks ────────────────────────────────────────────
class TestSelfChecks:
    def test_all_pass(self, P188):
        assert P188.run_self_checks() is True
