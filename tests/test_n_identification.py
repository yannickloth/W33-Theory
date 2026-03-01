"""Tests for Pillar 101: N ≅ Aut(C₂ × Q₈) identification."""

import json
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Import pillar
import importlib
import sys
sys.path.insert(0, str(ROOT))
from THEORY_PART_CCI_N_IDENTIFICATION import (
    compute_aut_c2q8,
    group_fingerprint,
    load_N_fingerprint,
    identify_N,
    _g_mul,
    _g_inv,
    _g_order,
    _q8_mul,
)


class TestQ8:
    """Test the Q₈ multiplication infrastructure."""

    def test_q8_identity(self):
        """1 is the identity of Q₈."""
        for x in range(8):
            assert _q8_mul(0, x) == x
            assert _q8_mul(x, 0) == x

    def test_q8_squares(self):
        """i²=j²=k²=-1."""
        assert _q8_mul(2, 2) == 1  # i*i = -1
        assert _q8_mul(4, 4) == 1  # j*j = -1
        assert _q8_mul(6, 6) == 1  # k*k = -1

    def test_q8_ijk(self):
        """ij=k, ji=-k."""
        assert _q8_mul(2, 4) == 6  # ij = k
        assert _q8_mul(4, 2) == 7  # ji = -k


class TestC2Q8:
    """Test C₂ × Q₈ group operations."""

    def test_order_16(self):
        """C₂ × Q₈ has 16 elements."""
        # Generate all elements
        orders = [_g_order(x) for x in range(16)]
        assert all(o is not None and o > 0 for o in orders)

    def test_identity(self):
        """Element 0 is the identity."""
        for x in range(16):
            assert _g_mul(0, x) == x
            assert _g_mul(x, 0) == x

    def test_inverses(self):
        """Every element has an inverse."""
        for x in range(16):
            assert _g_mul(x, _g_inv(x)) == 0
            assert _g_mul(_g_inv(x), x) == 0

    def test_element_order_distribution(self):
        """Element orders: {1:1, 2:3, 4:12}."""
        from collections import Counter
        dist = Counter(_g_order(x) for x in range(16))
        assert dist == {1: 1, 2: 3, 4: 12}


class TestAutC2Q8:
    """Test the automorphism group computation."""

    @pytest.fixture(scope="class")
    def aut_perms(self):
        return compute_aut_c2q8()

    def test_aut_order_192(self, aut_perms):
        """|Aut(C₂ × Q₈)| = 192."""
        assert len(aut_perms) == 192

    def test_identity_present(self, aut_perms):
        """Identity permutation is in Aut(G)."""
        assert tuple(range(16)) in aut_perms

    def test_all_bijections(self, aut_perms):
        """Every automorphism is a bijection on {0,...,15}."""
        for p in aut_perms:
            assert sorted(p) == list(range(16))


class TestFingerprint:
    """Test that fingerprints match."""

    @pytest.fixture(scope="class")
    def aut_fp(self):
        return group_fingerprint(compute_aut_c2q8())

    def test_center_trivial(self, aut_fp):
        """|Z(Aut(C₂×Q₈))| = 1."""
        assert aut_fp["center_order"] == 1

    def test_derived_48(self, aut_fp):
        """|[Aut,Aut]| = 48."""
        assert aut_fp["derived_order"] == 48

    def test_second_derived_16(self, aut_fp):
        """|G''| = 16."""
        assert aut_fp["second_derived_order"] == 16

    def test_14_conjugacy_classes(self, aut_fp):
        """14 conjugacy classes."""
        assert aut_fp["num_conjugacy_classes"] == 14

    def test_element_orders(self, aut_fp):
        """Element order distribution matches."""
        expected = {1: 1, 2: 43, 3: 32, 4: 84, 6: 32}
        assert aut_fp["element_orders"] == expected

    def test_fingerprint_exact(self, aut_fp):
        """Full conjugacy class fingerprint matches expected."""
        expected = [
            (1, 1), (2, 3), (2, 4), (2, 6), (2, 6),
            (2, 12), (2, 12), (3, 32),
            (4, 12), (4, 12), (4, 12), (4, 24), (4, 24),
            (6, 32),
        ]
        assert aut_fp["conjugacy_class_fingerprint"] == expected


class TestIdentification:
    """Test the full identification N ≅ Aut(C₂ × Q₈)."""

    @pytest.fixture(scope="class")
    def summary(self):
        return identify_N()

    def test_all_match(self, summary):
        """All invariants match."""
        assert summary["all_invariants_match"] is True

    def test_identification_string(self, summary):
        """Identification string is correct."""
        assert "Aut" in summary["identification"]
        assert "Q" in summary["identification"]

    def test_smallgroup_id(self, summary):
        """SmallGroup ID is [192, 955]."""
        assert summary["SmallGroup_ID"] == [192, 955]
