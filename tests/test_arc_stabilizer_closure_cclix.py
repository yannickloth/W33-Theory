"""
Phase CCLIX — Arc-Stabilizer Closure: J₂ < G₂(4) < Suz at q = 3
==================================================================

THEOREM (Arc-Stabilizer Closure at q=3):
The sporadic chain J₂ < G₂(4) < Suz, parametrized by the W(3,3)
order template, has coset indices that equal the Suzuki SRG parameters:

  |G₂(4)| / |J₂|    = 416    = K'_Suz   (valency)
  |Suz|   / |G₂(4)| = 1782   = V'_Suz   (vertex count)
  |Suz|   / |J₂|    = 741312 = V'K' = 2E'_Suz  (arc count)

These three equalities hold simultaneously ONLY at q=3 among
prime powers q = 2..40.

INTERPRETATION: The sporadic tower is not merely an order fit —
it is an orbit-stabilizer decomposition of the Suzuki graph action.

SOURCE: W33_arc_stabilizer_closure_20260330.zip
"""
import pytest

# ── W(3,3) parameters at q = 3 ──
q    = 3
v    = 40
k    = 12
lam  = 2
mu   = 4
r    = q - 1          # 2
s    = -(q + 1)       # -4
f    = 24
g    = 15
Phi3 = q**2 + q + 1   # 13
Phi4 = q**2 + 1        # 10
Phi6 = q**2 - q + 1    # 7
Phi12 = q**4 - q**2 + 1  # 73


# ── Suzuki SRG lift parameters (from W(3,3) formulas) ──
def suz_V(q):
    """Suzuki graph vertex count = 2q⁴(k-1), k = q(q+1)."""
    k_ = q * (q + 1)
    return 2 * q**4 * (k_ - 1)


def suz_K(q):
    """Suzuki graph valency = mu * (k - mu) * Phi3."""
    mu_ = q + 1
    k_ = q * (q + 1)
    Phi3_ = q**2 + q + 1
    return mu_ * (k_ - mu_) * Phi3_


def suz_lam(q):
    """Suzuki lambda = Phi4²."""
    return (q**2 + 1)**2


def suz_mu_srg(q):
    """Suzuki mu = k * r * |s|."""
    k_ = q * (q + 1)
    r_ = q - 1
    s_ = q + 1
    return k_ * r_ * s_


def suz_E(q):
    """Suzuki edge count = V'K'/2."""
    return suz_V(q) * suz_K(q) // 2


# ── Sporadic group order template ──
def order_J2(q):
    """J₂ order from W(3,3) template: 2^Φ₆ · q^q · (q+2)^r · Φ₆."""
    Phi6_ = q**2 - q + 1
    r_ = q - 1
    return (2**Phi6_) * (q**q) * ((q + 2)**r_) * Phi6_


def order_G24(q):
    """G₂(4) order from W(3,3) template: 2^k · q^q · (q+2)^r · Φ₆ · Φ₃."""
    k_ = q * (q + 1)
    Phi3_ = q**2 + q + 1
    Phi6_ = q**2 - q + 1
    r_ = q - 1
    return (2**k_) * (q**q) * ((q + 2)**r_) * Phi6_ * Phi3_


def order_Suz(q):
    """Suz order from W(3,3) template: 2^Φ₃ · q^Φ₆ · (q+2)^r · Φ₆ · (k-1) · Φ₃."""
    k_ = q * (q + 1)
    Phi3_ = q**2 + q + 1
    Phi6_ = q**2 - q + 1
    r_ = q - 1
    return (2**Phi3_) * (q**Phi6_) * ((q + 2)**r_) * Phi6_ * (k_ - 1) * Phi3_


# ── Known group orders for cross-check ──
J2_ORDER  = 604800
G24_ORDER = 251596800
SUZ_ORDER = 448345497600


# ================================================================
# T1: W(3,3) parameter consistency
# ================================================================
class TestT1_Parameters:
    """Verify W(3,3) parameter setup at q=3."""

    def test_v(self):
        assert v == (q + 1) * (q**2 + 1)

    def test_k(self):
        assert k == q * (q + 1)

    def test_Phi3(self):
        assert Phi3 == q**2 + q + 1 == 13

    def test_Phi6(self):
        assert Phi6 == q**2 - q + 1 == 7

    def test_eigenvalues(self):
        assert r == 2 and s == -4


# ================================================================
# T2: Suzuki SRG lift at q=3
# ================================================================
class TestT2_SuzukiSRG:
    """Verify Suzuki graph parameters at q=3."""

    def test_V_prime(self):
        assert suz_V(3) == 1782

    def test_K_prime(self):
        assert suz_K(3) == 416

    def test_lambda_prime(self):
        assert suz_lam(3) == 100

    def test_mu_prime(self):
        assert suz_mu_srg(3) == 96

    def test_E_prime(self):
        assert suz_E(3) == 370656

    def test_arc_count(self):
        """2E' = V'K' = total arc count of Suzuki graph."""
        assert 2 * suz_E(3) == suz_V(3) * suz_K(3) == 741312


# ================================================================
# T3: Sporadic group orders at q=3
# ================================================================
class TestT3_GroupOrders:
    """Template-computed orders match known values."""

    def test_J2(self):
        assert order_J2(3) == J2_ORDER

    def test_G24(self):
        assert order_G24(3) == G24_ORDER

    def test_Suz(self):
        assert order_Suz(3) == SUZ_ORDER


# ================================================================
# T4: Arc-Stabilizer Closure — the main theorem
# ================================================================
class TestT4_ArcStabilizerClosure:
    """
    THEOREM: At q=3 the coset indices of J₂ < G₂(4) < Suz
    equal the Suzuki SRG orbit data: K', V', V'K'.
    """

    def test_G24_over_J2_is_K_prime(self):
        """Valency orbit: |G₂(4)|/|J₂| = K'_Suz = 416."""
        ratio = order_G24(3) // order_J2(3)
        assert ratio == suz_K(3) == 416

    def test_Suz_over_G24_is_V_prime(self):
        """Vertex orbit: |Suz|/|G₂(4)| = V'_Suz = 1782."""
        ratio = order_Suz(3) // order_G24(3)
        assert ratio == suz_V(3) == 1782

    def test_Suz_over_J2_is_arc_count(self):
        """Arc orbit: |Suz|/|J₂| = V'K' = 2E' = 741312."""
        ratio = order_Suz(3) // order_J2(3)
        assert ratio == suz_V(3) * suz_K(3) == 741312

    def test_Suz_over_J2_is_2E(self):
        """|Suz|/|J₂| = 2E'_Suz."""
        assert order_Suz(3) // order_J2(3) == 2 * suz_E(3)


# ================================================================
# T5: Ratio factorizations (sharper identities)
# ================================================================
class TestT5_RatioFactorizations:
    """Coset ratios admit W(3,3) factorizations."""

    def test_G24_over_J2_formula(self):
        """2^(k-Phi6) * Phi3 = 2^5 * 13 = 416."""
        assert 2**(k - Phi6) * Phi3 == 416
        assert order_G24(3) // order_J2(3) == 2**(k - Phi6) * Phi3

    def test_G24_over_J2_alpha_formula(self):
        """K'_Suz = q*alpha + (q+2) where alpha = (k-1)² + mu²."""
        alpha = (k - 1)**2 + mu**2
        assert alpha == 137
        assert q * alpha + (q + 2) == 416

    def test_Suz_over_G24_alpha_formula(self):
        """V'_Suz = 1 + Phi3 * alpha."""
        alpha = (k - 1)**2 + mu**2
        assert 1 + Phi3 * alpha == 1782

    def test_alpha_value(self):
        """alpha = (k-1)^2 + mu^2 = 121 + 16 = 137, the fine-structure denominator."""
        alpha = (k - 1)**2 + mu**2
        assert alpha == 137


# ================================================================
# T6: Uniqueness scan — only q=3
# ================================================================
class TestT6_UniquenessQ3:
    """Among prime powers q=2..40, only q=3 satisfies the closure."""

    @pytest.fixture(scope="class")
    def scan_results(self):
        hits_K = []
        hits_V = []
        hits_arc = []
        for q_ in range(2, 41):
            J2 = order_J2(q_)
            G = order_G24(q_)
            S = order_Suz(q_)
            if G // J2 == suz_K(q_):
                hits_K.append(q_)
            if S // G == suz_V(q_):
                hits_V.append(q_)
            if S // J2 == suz_V(q_) * suz_K(q_):
                hits_arc.append(q_)
        return hits_K, hits_V, hits_arc

    def test_K_unique(self, scan_results):
        hits_K, _, _ = scan_results
        assert hits_K == [3]

    def test_V_unique(self, scan_results):
        _, hits_V, _ = scan_results
        assert hits_V == [3]

    def test_arc_unique(self, scan_results):
        _, _, hits_arc = scan_results
        assert hits_arc == [3]


# ================================================================
# T7: Orbit-stabilizer interpretation
# ================================================================
class TestT7_OrbitStabilizer:
    """The chain encodes a proper orbit-stabilizer decomposition."""

    def test_J2_is_arc_stabilizer_scale(self):
        """|J₂| = |Suz| / (V'K') — arc stabilizer of Suz on Suzuki graph."""
        assert SUZ_ORDER // (suz_V(3) * suz_K(3)) == J2_ORDER

    def test_G24_is_vertex_stabilizer_scale(self):
        """|G₂(4)| = |Suz| / V' — vertex stabilizer of Suz on Suzuki graph."""
        assert SUZ_ORDER // suz_V(3) == G24_ORDER

    def test_chain_decomposes(self):
        """
        |Suz| = |J₂| * K' * V'
        J₂ stabilizes an arc; multiplying by K' reaches G₂(4)
        (vertex stabilizer); multiplying by V' reaches Suz.
        """
        assert J2_ORDER * suz_K(3) * suz_V(3) == SUZ_ORDER


# ================================================================
# T8: Connection to W(3,3) arc stabilizer
# ================================================================
class TestT8_W33ArcStabilizer:
    """W(3,3) arc stabilizer = |Aut(W(3,3))| / (2E) = 108."""

    AUT_W33 = 51840  # |Sp(4,3)|
    E_W33 = 240

    def test_arc_stabilizer_value(self):
        assert self.AUT_W33 // (2 * self.E_W33) == 108

    def test_arc_stabilizer_is_mu_times_27(self):
        """108 = mu * 27 = mu * q^3."""
        assert 108 == mu * q**3

    def test_vertex_stabilizer(self):
        """Vertex stabilizer = |Aut|/v = 1296 = 6^4."""
        assert self.AUT_W33 // v == 1296 == 6**4

    def test_edge_stabilizer(self):
        """Edge stabilizer = |Aut|/E = 216 = 6^3."""
        assert self.AUT_W33 // self.E_W33 == 216 == 6**3
