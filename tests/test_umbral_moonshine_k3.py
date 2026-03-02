"""
Tests for Pillar 132 - Umbral Moonshine: Niemeier Shadows on K3 Surfaces
"""
import pytest

from THEORY_PART_CCXXXII_UMBRAL_MOONSHINE_K3 import (
    k3_invariants, k3_euler_decomposition, k3_intersection_form,
    elliptic_genus_k3, m24_dimension_check, umbral_groups,
    mathieu_moonshine_case, mock_theta_h2, verify_massive_from_mock,
    lambency_table, mukai_theorem, twenty_three_plus_one, k3_physics,
)


# ── K3 Invariants ──────────────────────────────────────────

class TestK3Invariants:
    def test_euler_char(self):
        assert k3_euler_decomposition() == 24

    def test_betti_b2(self):
        k3 = k3_invariants()
        assert k3['betti_numbers'][2] == 22

    def test_betti_sum(self):
        k3 = k3_invariants()
        assert sum(k3['betti_numbers']) == 24

    def test_complex_dim(self):
        k3 = k3_invariants()
        assert k3['complex_dimension'] == 2

    def test_real_dim(self):
        k3 = k3_invariants()
        assert k3['real_dimension'] == 4

    def test_signature(self):
        k3 = k3_invariants()
        assert k3['signature'] == -16


# ── Intersection Form ──────────────────────────────────────

class TestIntersectionForm:
    def test_rank(self):
        f = k3_intersection_form()
        assert f['rank'] == 22

    def test_signature(self):
        f = k3_intersection_form()
        assert f['signature'] == (3, 19)

    def test_even_unimodular(self):
        f = k3_intersection_form()
        assert f['is_even'] and f['is_unimodular']

    def test_e8_copies(self):
        f = k3_intersection_form()
        assert f['neg_e8_copies'] == 2


# ── Elliptic Genus ─────────────────────────────────────────

class TestEllipticGenus:
    def test_massless(self):
        eg = elliptic_genus_k3()
        assert eg['massless_degeneracy'] == 24

    def test_first_massive(self):
        eg = elliptic_genus_k3()
        assert eg['massive_coefficients'][1] == 90

    def test_second_massive(self):
        eg = elliptic_genus_k3()
        assert eg['massive_coefficients'][2] == 462

    def test_third_massive(self):
        eg = elliptic_genus_k3()
        assert eg['massive_coefficients'][3] == 1540

    def test_weight_zero(self):
        eg = elliptic_genus_k3()
        assert eg['weight'] == 0


# ── M_24 Decomposition ────────────────────────────────────

class TestM24Decomposition:
    def test_90_decomposition(self):
        d = m24_dimension_check()
        assert d[90]['irrep'] == 45
        assert d[90]['multiplicity'] == 2

    def test_462_decomposition(self):
        d = m24_dimension_check()
        assert d[462]['irrep'] == 231
        assert d[462]['multiplicity'] == 2

    def test_all_are_m24_irreps(self):
        d = m24_dimension_check()
        for total, info in d.items():
            assert info['is_m24_irrep']
            assert info['product_check']


# ── Umbral Groups ──────────────────────────────────────────

class TestUmbralGroups:
    def test_count(self):
        assert len(umbral_groups()) == 23

    def test_first_is_m24(self):
        ug = umbral_groups()
        assert ug[0] == ("A1^24", "M_24", 244823040)

    def test_last_is_trivial(self):
        ug = umbral_groups()
        assert ug[-1][2] == 1  # D24 umbral group is trivial


# ── Mathieu Moonshine ─────────────────────────────────────

class TestMathieuMoonshine:
    def test_m24(self):
        mm = mathieu_moonshine_case()
        assert mm['umbral_group'] == 'M_24'

    def test_order(self):
        mm = mathieu_moonshine_case()
        assert mm['order'] == 244823040

    def test_lambency(self):
        mm = mathieu_moonshine_case()
        assert mm['lambency'] == 2


# ── Mock Theta Functions ──────────────────────────────────

class TestMockTheta:
    def test_first_coeff(self):
        m = mock_theta_h2()
        assert m[0] == -2

    def test_t1(self):
        m = mock_theta_h2()
        assert m[1] == 45

    def test_t2(self):
        m = mock_theta_h2()
        assert m[2] == 231

    def test_t3(self):
        m = mock_theta_h2()
        assert m[3] == 770

    def test_massive_relation(self):
        v = verify_massive_from_mock()
        for n, info in v.items():
            assert info['check'], f"A_{n} != 2*t_{n}"


# ── Lambency ──────────────────────────────────────────────

class TestLambency:
    def test_count(self):
        assert len(lambency_table()) == 23

    def test_a1_lambency(self):
        lt = lambency_table()
        a1 = [l for l in lt if l['root_system'] == 'A1^24'][0]
        assert a1['lambency'] == 2


# ── Mukai ─────────────────────────────────────────────────

class TestMukai:
    def test_11_groups(self):
        m = mukai_theorem()
        assert m['num_maximal'] == 11

    def test_container(self):
        m = mukai_theorem()
        assert m['container'] == 'M_23'


# ── 23+1 Structure ────────────────────────────────────────

class TestTwentyThreePlusOne:
    def test_total(self):
        t = twenty_three_plus_one()
        assert t['total'] == 24

    def test_deep_holes(self):
        t = twenty_three_plus_one()
        assert t['deep_holes'] == 23


# ── Physics ───────────────────────────────────────────────

class TestPhysics:
    def test_dimension(self):
        p = k3_physics()
        assert p['dimensions']['full'] == 10

    def test_internal(self):
        p = k3_physics()
        assert p['dimensions']['total_internal'] == 6
