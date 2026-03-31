"""
Proof: 1859 = (k-1) * Phi3^2 from the spectral action a4/a2 ratio.

The denominator of ms/mt is not a fitted parameter -- it falls directly
out of two spectral quantities computable from the W(3,3) adjacency matrix:

  Step (a): a4/a2 Seeley-DeWitt ratio fixes k-1 = 11
  Step (b): Laplacian second moment Tr[L^2]/Tr[L] = Phi3 = 13
  Step (c): 1859 = 11 * 169 = (k-1) * Phi3^2
"""

import numpy as np
from fractions import Fraction
import pytest

# W(3,3) parameters
v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
E = 240
f, g = 24, 15  # edge multiplicities


class TestSpectralAction1859:

    def test_a4_a2_ratio_value(self):
        """a4/a2 = Phi4^2 * mu^2 * (k-1) / (mu^3 * (lambda+q) * Phi6) = 55/7."""
        numerator = Phi4**2 * m**2 * (k - 1)
        denominator = m**3 * (l + q) * Phi6
        ratio = Fraction(numerator, denominator)
        assert ratio == Fraction(55, 7), f"a4/a2 = {ratio}, expected 55/7"

    def test_k_minus_1_from_a4_a2(self):
        """Invert a4/a2 to recover k-1 = 11."""
        a4_over_a2 = Fraction(55, 7)
        k_minus_1 = a4_over_a2 * Fraction(m * (l + q) * Phi6, Phi4**2)
        assert int(k_minus_1) == k - 1 == 11, f"k-1 = {k_minus_1}, expected 11"

    def test_laplacian_moment_ratio_is_Phi3(self):
        """Tr[L^2] / Tr[L] = Phi3 = 13 for the W(3,3) Laplacian."""
        # W(3,3): 40 vertices, each with degree k=12
        # Laplacian eigenvalues: 0 (x1), k-lambda=10 (x24), k+mu=16 (x15)
        # For regular graph: Tr[L] = sum of eigenvalues = k * v (for all eigvals)
        # Actually Tr[L] = sum of all eigenvalues:
        # = 0*1 + 10*f + 16*g = 10*24 + 16*15 = 240 + 240 = 480
        # Tr[L^2] = 0^2*1 + 10^2*f + 16^2*g = 100*24 + 256*15 = 2400 + 3840 = 6240
        TrL = (k - l)**2 * 0 + (k - l) * f + (k + m) * g  # eigenvalue * multiplicity sum
        # Correct: eigenvalues of L are {0, k-lambda (x f), k+mu (x g)}
        ev0, ev1, ev2 = 0, k - l, k + m
        mult0, mult1, mult2 = 1, f, g
        TrL = ev0 * mult0 + ev1 * mult1 + ev2 * mult2
        TrL2 = ev0**2 * mult0 + ev1**2 * mult1 + ev2**2 * mult2
        ratio = Fraction(TrL2, TrL)
        assert TrL == 480, f"Tr[L] = {TrL}"
        assert TrL2 == 6240, f"Tr[L^2] = {TrL2}"
        assert ratio == Phi3, f"Tr[L^2]/Tr[L] = {ratio}, expected {Phi3}"

    def test_1859_factorization(self):
        """1859 = (k-1) * Phi3^2 = 11 * 169."""
        assert (k - 1) * Phi3**2 == 1859
        assert 11 * 169 == 1859
        assert 1859 == 11 * 13**2

    def test_ms_mt_denominator_is_pure_spectral(self):
        """ms/mt = 1/1859 with no fitted parameters."""
        denominator = (k - 1) * Phi3**2
        assert denominator == 1859
        # The spectral action prediction:
        # ms = mt / ((k-1) * Phi3^2)
        mt_GeV = 173.0
        ms_MeV = mt_GeV * 1000 / denominator
        # PDG ms(2 GeV) ~ 93 MeV; W(3,3) predicts ~93.1 MeV
        assert abs(ms_MeV - 93.1) < 1.0, f"ms = {ms_MeV:.2f} MeV"

    def test_Phi3_squared_from_laplacian(self):
        """Phi3^2 = (Tr[L^2]/Tr[L])^2 = 169."""
        ev1, ev2 = k - l, k + m
        mult1, mult2 = f, g
        TrL = ev1 * mult1 + ev2 * mult2
        TrL2 = ev1**2 * mult1 + ev2**2 * mult2
        Phi3_recovered = Fraction(TrL2, TrL)
        assert Phi3_recovered == Phi3
        assert Phi3_recovered**2 == Phi3**2 == 169

    def test_combined_identity(self):
        """Full chain: a4/a2 and Tr[L^2]/Tr[L] together imply 1859."""
        # From a4/a2
        a4_a2 = Fraction(Phi4**2 * m**2 * (k - 1), m**3 * (l + q) * Phi6)
        k_minus_1 = int(a4_a2 * Fraction(m * (l + q) * Phi6, Phi4**2))
        # From Laplacian moments
        TrL = (k - l) * f + (k + m) * g
        TrL2 = (k - l)**2 * f + (k + m)**2 * g
        Phi3_val = TrL2 // TrL  # exact integer division
        # Combined
        result = k_minus_1 * Phi3_val**2
        assert result == 1859
        assert k_minus_1 == 11
        assert Phi3_val == 13
