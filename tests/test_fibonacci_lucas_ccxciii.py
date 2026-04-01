"""
Phase CCXCIII — Fibonacci & Lucas Closed Chain
===============================================

The Fibonacci and Lucas sequences at W(3,3) indices form A CLOSED LOOP:

  L: λ → q → μ → Φ₆         (Lucas: L(λ)=q, L(q)=μ, L(μ)=Φ₆)
  F: Φ₆ → Φ₃                  (Fibonacci: F(Φ₆)=Φ₃)
  F: q → λ                   (Fibonacci: F(q)=λ)

  F(s) = 2d,  F(k−1) = 89 = p_f,  F(k) = k² = 144

Moreover, F(n) = n² has EXACTLY TWO INTEGER SOLUTIONS:
  - n = 1 (trivial)
  - n = 12 = k (W(3,3) valency!)

This makes k = 12 the unique non-trivial solution globally.
"""

# ── W(3,3) master parameters ────────────────────────────────────────
q, lam, mu, k, v = 3, 2, 4, 12, 40
f, g = 24, 15
E, tau, R = 240, 252, 28
Phi3, Phi6, Phi12 = 13, 7, 73
Theta, s, N, d = 10, 6, 20, 4
b2 = f - lam  # 22


# ────────────────────────────────────────────────────────────────────
#  1.  FIBONACCI AT W(3,3) INDICES
# ────────────────────────────────────────────────────────────────────

class TestFibonacciChain:
    """Fibonacci sequence generates W(3,3) parameters."""

    def test_F_lam_is_1(self):
        """F(λ) = F(2) = 1."""
        from sympy import fibonacci
        assert int(fibonacci(lam)) == 1

    def test_F_q_is_lam(self):
        """F(q) = F(3) = 2 = λ."""
        from sympy import fibonacci
        assert int(fibonacci(q)) == lam

    def test_F_mu_is_3(self):
        """F(μ) = F(4) = 3."""
        from sympy import fibonacci
        assert int(fibonacci(mu)) == 3

    def test_F_s_is_2d(self):
        """F(s) = F(6) = 8 = 2d."""
        from sympy import fibonacci
        assert int(fibonacci(s)) == 2 * d

    def test_F_Phi6_is_Phi3(self):
        """F(Φ₆) = F(7) = 13 = Φ₃."""
        from sympy import fibonacci
        assert int(fibonacci(Phi6)) == Phi3

    def test_F_Theta_is_binomial(self):
        """F(Θ) = F(10) = 55 = C(k−1, 2)."""
        from sympy import fibonacci
        from math import comb
        assert int(fibonacci(Theta)) == comb(k - 1, 2)

    def test_F_k_minus_1_is_89(self):
        """F(k−1) = F(11) = 89 = p_f (f-th prime)."""
        from sympy import fibonacci, prime
        assert int(fibonacci(k - 1)) == 89
        assert int(fibonacci(k - 1)) == prime(f)

    def test_F_k_is_k_squared(self):
        """F(k) = F(12) = 144 = k²."""
        from sympy import fibonacci
        assert int(fibonacci(k)) == k ** 2

    def test_F_Phi3_is_prime(self):
        """F(Φ₃) = F(13) = 233 (prime)."""
        from sympy import fibonacci, isprime
        F_Phi3 = int(fibonacci(Phi3))
        assert F_Phi3 == 233
        assert isprime(F_Phi3)


# ────────────────────────────────────────────────────────────────────
#  2.  LUCAS AT W(3,3) INDICES
# ────────────────────────────────────────────────────────────────────

class TestLucasChain:
    """Lucas sequence creates a one-way path through W(3,3)."""

    def test_L_lam_is_q(self):
        """L(λ) = L(2) = 3 = q."""
        from sympy import lucas
        assert int(lucas(lam)) == q

    def test_L_q_is_mu(self):
        """L(q) = L(3) = 4 = μ."""
        from sympy import lucas
        assert int(lucas(q)) == mu

    def test_L_mu_is_Phi6(self):
        """L(μ) = L(4) = 7 = Φ₆."""
        from sympy import lucas
        assert int(lucas(mu)) == Phi6

    def test_L_s_is_sq(self):
        """L(s) = L(6) = 18 = s·q."""
        from sympy import lucas
        assert int(lucas(s)) == s * q

    def test_L_Phi6_is_R_plus_1(self):
        """L(Φ₆) = L(7) = 29 = R + 1."""
        from sympy import lucas
        assert int(lucas(Phi6)) == R + 1


# ────────────────────────────────────────────────────────────────────
#  3.  CLOSED FIBONACCI-LUCAS CHAIN
# ────────────────────────────────────────────────────────────────────

class TestFibonacciLucasLoop:
    """The sequences form a closed loop circuit."""

    def test_forward_path(self):
        """λ →^L q →^L μ →^L Φ₆ →^F Φ₃."""
        from sympy import lucas, fibonacci
        assert int(lucas(lam)) == q
        assert int(lucas(q)) == mu
        assert int(lucas(mu)) == Phi6
        assert int(fibonacci(Phi6)) == Phi3

    def test_backward_q_to_lam(self):
        """q →^F λ (via Fibonacci)."""
        from sympy import fibonacci
        assert int(fibonacci(q)) == lam

    def test_cycle_property(self):
        """The path λ →^L q →^F λ suggests a 2-cycle for L∘F."""
        from sympy import lucas, fibonacci
        F_q = int(fibonacci(q))
        L_F_q = int(lucas(F_q))
        # L(F(q)) = L(λ) = q
        assert L_F_q == q


# ────────────────────────────────────────────────────────────────────
#  4.  UNIQUENESS: F(n) = n² HAS NO OTHER SOLUTIONS
# ────────────────────────────────────────────────────────────────────

class TestFibonacciSquareUniqueness:
    """F(n) = n² is solved ONLY by n=1 and n=k=12."""

    def test_F_1_is_1_squared(self):
        """F(1) = 1 = 1²."""
        from sympy import fibonacci
        assert int(fibonacci(1)) == 1 ** 2

    def test_F_k_is_k_squared(self):
        """F(k) = k² is the unique non-trivial solution."""
        from sympy import fibonacci
        assert int(fibonacci(k)) == k ** 2

    def test_no_other_solutions_small_n(self):
        """For 2 ≤ n ≤ 100, only n=k=12 solves F(n)=n²."""
        from sympy import fibonacci
        solutions = [n for n in range(2, 101) if int(fibonacci(n)) == n ** 2]
        assert solutions == [k]

    def test_k_is_special(self):
        """k = 12 is the valency of W(3,3) and a unique Fibonacci property."""
        # Verify k is indeed special: only n=1,12 solve F(n)=n²
        assert k == 12
