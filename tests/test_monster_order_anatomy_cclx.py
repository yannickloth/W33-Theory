"""
Phase CCLX — Monster Order Anatomy: Exponent Skeleton from W(3,3)
===================================================================

THEOREM (Monster Order Skeleton):
|M| = 2^46 · 3^20 · 5^9 · 7^6 · 11^2 · 13^3 · 17·19·23·29·31·41·47·59·71

decomposes into W(3,3) as:

  |M| = λ^(2f−λ) · q^(v/λ) · (q+λ)^(q²) · Φ₆^(k/λ) · (k−1)^λ · Φ₃^q
        × (f−Φ₆)(k+Φ₆)(f−1)(f+Φ₆−λ)(f+Φ₆)(v+1)(v+Φ₆)(v+k+Φ₆)(Φ₁₂−λ)

STRUCTURAL IDENTITIES:
  • 15 supersingular primes split into:
    - k/λ = 6 multi-exponent primes: {λ, q, q+λ, Φ₆, k−1, Φ₃}
    - q² = 9 simple primes (exp=1): {f−Φ₆, k+Φ₆, f−1, f+Φ₆−λ, f+Φ₆, v+1, v+Φ₆, v+k+Φ₆, Φ₁₂−λ}
    - k/λ + q² = 6 + 9 = g = 15

  • Exponents of the multi-exponent primes:
    - exp(λ=2)   = 46 = 2f − λ = v + Φ₆ − 1
    - exp(q=3)   = 20 = v/λ = f − |s|
    - exp(q+λ=5) = 9  = q²
    - exp(Φ₆=7)  = 6  = k/λ
    - exp(k−1=11)= 2  = λ
    - exp(Φ₃=13) = 3  = q

  • Sum of all exponents = (q+λ)(k+Φ₆) = f + Φ₁₂ − λ = 95
"""
import math
import pytest

# ── W(3,3) parameters ──
q    = 3
v    = 40
k    = 12
lam  = 2
mu   = 4
f    = 24
g    = 15
s    = -(q + 1)   # -4
Phi3 = q**2 + q + 1   # 13
Phi4 = q**2 + 1        # 10
Phi6 = q**2 - q + 1    # 7
Phi12 = q**4 - q**2 + 1  # 73

# ── Monster order ──
MONSTER_ORDER = 808017424794512875886459904961710757005754368000000000

EXPONENTS = {
    lam:         2*f - lam,      # 2^46
    q:           v // lam,       # 3^20
    q + lam:     q**2,           # 5^9
    Phi6:        k // lam,       # 7^6
    k - 1:       lam,            # 11^2
    Phi3:        q,              # 13^3
    f - Phi6:    1,              # 17
    k + Phi6:    1,              # 19
    f - 1:       1,              # 23
    f + Phi6 - lam: 1,           # 29
    f + Phi6:    1,              # 31
    v + 1:       1,              # 41
    v + Phi6:    1,              # 47
    v + k + Phi6: 1,             # 59
    Phi12 - lam: 1,              # 71
}

# Separate into multi-exponent and simple
MULTI = {p: e for p, e in EXPONENTS.items() if e > 1}
SIMPLE = {p for p, e in EXPONENTS.items() if e == 1}


# ================================================================
# T1: Monster order reconstruction
# ================================================================
class TestT1_MonsterOrder:
    """Verify |M| reconstructs from the W(3,3) exponents."""

    def test_order_exact(self):
        computed = math.prod(p**e for p, e in EXPONENTS.items())
        assert computed == MONSTER_ORDER

    def test_15_primes(self):
        assert len(EXPONENTS) == 15


# ================================================================
# T2: Multi-exponent primes are {lam, q, q+lam, Phi6, k-1, Phi3}
# ================================================================
class TestT2_MultiExponentPrimes:
    """6 primes with exponent > 1 are the 'inner' atoms."""

    def test_count(self):
        assert len(MULTI) == 6

    def test_count_is_k_over_lam(self):
        assert len(MULTI) == k // lam

    def test_primes(self):
        assert set(MULTI.keys()) == {2, 3, 5, 7, 11, 13}

    def test_primes_are_inner_atoms(self):
        inner = {lam, q, q + lam, Phi6, k - 1, Phi3}
        assert set(MULTI.keys()) == inner


# ================================================================
# T3: Simple primes (exponent 1) are the 'outer' atoms
# ================================================================
class TestT3_SimplePrimes:
    """9 primes with exponent = 1 are the 'outer' atoms."""

    def test_count(self):
        assert len(SIMPLE) == 9

    def test_count_is_q_squared(self):
        assert len(SIMPLE) == q**2

    def test_primes(self):
        assert SIMPLE == {17, 19, 23, 29, 31, 41, 47, 59, 71}

    def test_primes_are_outer_atoms(self):
        outer = {f - Phi6, k + Phi6, f - 1, f + Phi6 - lam,
                 f + Phi6, v + 1, v + Phi6, v + k + Phi6, Phi12 - lam}
        assert SIMPLE == outer


# ================================================================
# T4: Inner/outer count decomposition
# ================================================================
class TestT4_CountDecomposition:
    """k/lam + q^2 = 6 + 9 = g = 15."""

    def test_sum(self):
        assert len(MULTI) + len(SIMPLE) == g

    def test_k_lam_plus_q_sq(self):
        assert k // lam + q**2 == g


# ================================================================
# T5: Each multi-exponent is a W(3,3) parameter
# ================================================================
class TestT5_ExponentExpressions:
    """Each exponent is itself a W(3,3) expression."""

    def test_exp_2_is_2f_minus_lam(self):
        """2^46: 46 = 2f - lam."""
        assert EXPONENTS[2] == 2 * f - lam == 46

    def test_exp_2_alt(self):
        """46 = v + Phi6 - 1."""
        assert 2 * f - lam == v + Phi6 - 1

    def test_exp_3_is_v_over_lam(self):
        """3^20: 20 = v/lam."""
        assert EXPONENTS[3] == v // lam == 20

    def test_exp_3_alt(self):
        """20 = f + s = f - (q+1)."""
        assert v // lam == f + s

    def test_exp_5_is_q_squared(self):
        """5^9: 9 = q^2."""
        assert EXPONENTS[5] == q**2 == 9

    def test_exp_7_is_k_over_lam(self):
        """7^6: 6 = k/lam."""
        assert EXPONENTS[7] == k // lam == 6

    def test_exp_11_is_lam(self):
        """11^2: 2 = lam."""
        assert EXPONENTS[11] == lam == 2

    def test_exp_13_is_q(self):
        """13^3: 3 = q."""
        assert EXPONENTS[13] == q == 3


# ================================================================
# T6: Sum of exponents
# ================================================================
class TestT6_ExponentSum:
    """Sum of exponents = 95 = (q+lam)(k+Phi6) = f + Phi12 - lam."""

    def test_sum_value(self):
        assert sum(EXPONENTS.values()) == 95

    def test_product_formula(self):
        assert sum(EXPONENTS.values()) == (q + lam) * (k + Phi6)

    def test_additive_formula(self):
        assert sum(EXPONENTS.values()) == f + Phi12 - lam

    def test_sum_multi_only(self):
        """Sum of multi-exponents = 46+20+9+6+2+3 = 86."""
        multi_sum = sum(MULTI.values())
        assert multi_sum == 86

    def test_sum_simple(self):
        """Sum of simple exponents = 9*1 = 9 = q^2."""
        simple_sum = len(SIMPLE) * 1
        assert simple_sum == q**2


# ================================================================
# T7: Exponent-prime duality
# ================================================================
class TestT7_ExponentPrimeDuality:
    """
    The exponent of p_i in |M| uses atoms from a 'dual' layer:
    Large atom (far from q) => small exponent (near q).
    """

    def test_largest_prime_exp_1(self):
        """71 (largest atom) has exponent 1 (smallest)."""
        assert EXPONENTS[71] == 1

    def test_smallest_prime_largest_exp(self):
        """2 (smallest atom) has exponent 46 (largest)."""
        assert EXPONENTS[2] == max(EXPONENTS.values())

    def test_exponents_broadly_decrease(self):
        """Exponents broadly decrease: inner 6 primes carry all multi-exponents,
        outer 9 primes all have exponent 1."""
        sorted_items = sorted(EXPONENTS.items())
        inner = [(p, e) for p, e in sorted_items if e > 1]
        outer = [(p, e) for p, e in sorted_items if e == 1]
        # All inner primes < all outer primes
        assert max(p for p, _ in inner) < min(p for p, _ in outer)


# ================================================================
# T8: Full formula verification
# ================================================================
class TestT8_FullFormula:
    """
    |M| = lam^(2f-lam) * q^(v/lam) * (q+lam)^(q^2) * Phi6^(k/lam)
        * (k-1)^lam * Phi3^q
        * (f-Phi6)*(k+Phi6)*(f-1)*(f+Phi6-lam)*(f+Phi6)
        * (v+1)*(v+Phi6)*(v+k+Phi6)*(Phi12-lam)
    """

    def test_formula(self):
        M = (lam**(2*f - lam)
             * q**(v // lam)
             * (q + lam)**(q**2)
             * Phi6**(k // lam)
             * (k - 1)**lam
             * Phi3**q
             * (f - Phi6) * (k + Phi6) * (f - 1) * (f + Phi6 - lam)
             * (f + Phi6) * (v + 1) * (v + Phi6) * (v + k + Phi6)
             * (Phi12 - lam))
        assert M == MONSTER_ORDER
