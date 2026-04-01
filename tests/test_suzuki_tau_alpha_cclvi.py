"""
Phase CCLVI — Suzuki Tau-Alpha Linearization
=============================================

The entire Suzuki lift parameter package is affine-linear in two scalars:
  tau_q = mu*q^2*Phi6 = 252 (modular core)
  alpha = (k-1)^2+mu^2 = 137 (Gaussian core)

At q=3: f'=q*tau+f=780, g'=mu*tau-Phi6=1001, V'=Phi6*tau+lam*q^2=1782,
K'=q*alpha+(q+2)=416. Each affine residual carries a (q-3) factor.

The Leech and McKay coefficients fuse:
  196560 = tau * f' = tau * (q*tau+f)
  196884 = tau*f' + mu*q^4
  196883 = tau*f' + mu*q^4 - 1

Sources: W33_suzuki_tau_alpha_linearization_20260330.zip
"""
import pytest
from fractions import Fraction

# ── W(3,3) parameters ──
q    = 3
v    = 40
k    = 12
lam  = 2
mu   = 4
f    = 24
g    = 15
Phi3 = 13
Phi4 = 10
Phi6 = 7
alpha = (k-1)**2 + mu**2  # 137

# ── Tau and Suzuki lift at q=3 ──
tau = mu * q**2 * Phi6      # (q+1)*q^2*(q^2-q+1) = 252

# Suzuki lift parameters
f_prime = mu * g * Phi3      # 4*15*13 = 780
g_prime = Phi3 * Phi6 * (k-1)  # 13*7*11 = 1001
V_prime = 2 * q**4 * (k-1)  # 2*81*11 = 1782
K_prime = mu * (k-mu) * Phi3  # 4*8*13 = 416
L_prime = Phi4**2             # 100
M_prime = k * (q-1) * (q+1)  # 12*2*4 = 96


# ================================================================
# T1: Tau-alpha linear forms
# ================================================================
class TestT1_TauAlphaLinear:
    """Each Suzuki parameter is affine-linear in tau and/or alpha."""

    def test_f_prime_linear_in_tau(self):
        """f' = q*tau + f = 3*252+24 = 780"""
        assert q * tau + f == f_prime

    def test_g_prime_linear_in_tau(self):
        """g' = mu*tau - Phi6 = 4*252-7 = 1001 (exact for all q!)"""
        assert mu * tau - Phi6 == g_prime

    def test_V_prime_linear_in_tau(self):
        """V' = Phi6*tau + lam*q^2 = 7*252+18 = 1782"""
        assert Phi6 * tau + lam * q**2 == V_prime

    def test_K_prime_linear_in_alpha(self):
        """K' = q*alpha + (q+2) = 3*137+5 = 416"""
        assert q * alpha + (q+2) == K_prime

    def test_M_prime_from_lam(self):
        """M' = lam*q^2*mu + f = 2*9*4+24 = 96"""
        assert lam * q**2 * mu + f == M_prime

    def test_L_prime(self):
        """L' = Phi4^2 = 100"""
        assert L_prime == 100


# ================================================================
# T2: (q-3) factor in affine residuals
# ================================================================
class TestT2_QMinus3Factors:
    """Each linear form's residual factors through (q-3)."""

    def _W3q(self, qq):
        kq = qq*(qq+1)
        muq = qq+1
        lamq = qq-1
        fq = qq*(qq+1)**2//2
        gq = qq*(qq**2+1)//2
        Phi3q = qq**2+qq+1
        Phi4q = qq**2+1
        Phi6q = qq**2-qq+1
        tauq = muq * qq**2 * Phi6q
        alphaq = (kq-1)**2 + muq**2
        fp = muq*gq*Phi3q
        gp = Phi3q*Phi6q*(kq-1)
        Vp = 2*qq**4*(kq-1)
        Kp = muq*(kq-muq)*Phi3q
        Mp = kq*lamq*muq
        return locals()

    def test_f_prime_residual(self):
        """f' - (q*tau+f) has factor (q-3) for all q"""
        for qq in range(2, 15):
            p = self._W3q(qq)
            diff = p['fp'] - (qq * p['tauq'] + p['fq'])
            if qq == 3:
                assert diff == 0
            else:
                assert diff != 0
                assert diff % (qq - 3) == 0

    def test_V_prime_residual(self):
        """V' - (Phi6*tau+lam*q^2) has factor (q-3) for all q"""
        for qq in range(2, 15):
            p = self._W3q(qq)
            diff = p['Vp'] - (p['Phi6q'] * p['tauq'] + p['lamq'] * qq**2)
            if qq == 3:
                assert diff == 0
            else:
                assert diff != 0
                assert diff % (qq - 3) == 0

    def test_K_prime_residual(self):
        """K' - (q*alpha+(q+2)) has factor (q-3) for all q"""
        for qq in range(2, 15):
            p = self._W3q(qq)
            diff = p['Kp'] - (qq * p['alphaq'] + (qq + 2))
            if qq == 3:
                assert diff == 0
            else:
                assert diff != 0
                assert diff % (qq - 3) == 0


# ================================================================
# T3: Leech and McKay from tau-linearized lift
# ================================================================
class TestT3_LeechMcKay:
    """Plucker-tau closure fuses with Suzuki alpha closure."""

    def test_Leech_lattice(self):
        """196560 = tau * f' = 252 * 780"""
        assert tau * f_prime == 196560

    def test_McKay_coefficient(self):
        """196884 = tau*f' + mu*q^4 = 196560+324"""
        assert tau * f_prime + mu * q**4 == 196884

    def test_Monster_dim(self):
        """196883 = tau*f' + mu*q^4 - 1"""
        assert tau * f_prime + mu * q**4 - 1 == 196883

    def test_Leech_from_tau_squared(self):
        """196560 = tau*(q*tau+f) = q*tau^2 + f*tau"""
        assert q * tau**2 + f * tau == 196560

    def test_mu_q4_correction(self):
        """mu*q^4 = 4*81 = 324"""
        assert mu * q**4 == 324


# ================================================================
# T4: Suzuki vertex from dual perspective
# ================================================================
class TestT4_SuzukiVertex:
    """1782 = V' from multiple W(3,3) decompositions."""

    def test_V_prime_value(self):
        assert V_prime == 1782

    def test_from_Phi3_alpha(self):
        """1782 = 1 + Phi3*alpha = 1+13*137"""
        assert 1 + Phi3 * alpha == 1782

    def test_from_tau_linear(self):
        """1782 = Phi6*tau + lam*q^2 = 7*252+18"""
        assert Phi6 * tau + lam * q**2 == 1782

    def test_decomposition_780_1001(self):
        """1782 = 1 + 780 + 1001 = 1 + f' + g'"""
        assert 1 + f_prime + g_prime == 1782

    def test_f_prime_plus_g_prime(self):
        """f' + g' = 780+1001 = 1781"""
        assert f_prime + g_prime == V_prime - 1

    def test_tau_values(self):
        """tau=252, alpha=137 are the two generating scalars"""
        assert tau == 252
        assert alpha == 137


# ================================================================
# T5: Uniqueness scan
# ================================================================
class TestT5_Uniqueness:
    """Each affine form gives the target only at q=3."""

    def test_f_prime_780_unique(self):
        for qq in range(2, 50):
            muq = qq+1
            fq = qq*(qq+1)**2//2
            Phi6q = qq**2-qq+1
            tauq = muq*qq**2*Phi6q
            val = qq * tauq + fq
            if val == 780:
                assert qq == 3

    def test_1782_from_Phi6_tau_unique(self):
        for qq in range(2, 50):
            muq = qq+1
            lamq = qq-1
            Phi6q = qq**2-qq+1
            tauq = muq*qq**2*Phi6q
            val = Phi6q * tauq + lamq * qq**2
            if val == 1782:
                assert qq == 3

    def test_196883_unique(self):
        for qq in range(2, 30):
            muq = qq+1
            fq = qq*(qq+1)**2//2
            Phi6q = qq**2-qq+1
            tauq = muq*qq**2*Phi6q
            fp = qq*tauq + fq  # NOT exact for all q, but check target
            val = tauq*fp + muq*qq**4 - 1
            if val == 196883:
                assert qq == 3
