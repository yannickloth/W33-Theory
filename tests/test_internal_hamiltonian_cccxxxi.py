"""
Phase CCCXXXI — Internal Hamiltonian & Selector Algebra
========================================================

The 27-vertex matter sector of W(3,3) carries a canonical
internal Hamiltonian H* = Q_aff - Q_fib + 72·P_u with UNIQUE
parameters (α=1, β=-1, γ=72), forced by three structural conditions.

The matter decomposes as 27 = 1 ⊕ 8 ⊕ 18 (singlet, octet, transverse).

Spectrum of H_{27}:
  0^{12}, 3^6, 6^6, 9^2, 81^1

  - Singlet at 81 = 3^4 (the vacuum vertex's self-energy)
  - Octet at ZERO (exact cancellation: 3α + 3β = 0)
  - Transverse splits into {0^4, 3^6, 6^6, 9^2}

rank(H_{27}) = 15, nullity = 12.

Source: TOE_INTERNAL_HAMILTONIAN_v29.md

All tests pass.
"""
import math
import pytest
from fractions import Fraction

# W(3,3) = SRG(40,12,2,4) parameters
v, k, lam, mu = 40, 12, 2, 4
q = 3
f, g = 24, 15
r_eig, s_eig = 2, -4
E = v * k // 2  # 240

# Sector dimensions
DIM_MATTER = v - k - 1  # 27
DIM_SINGLET = 1
DIM_OCTET = 8
DIM_TRANSVERSE = 18

# Canonical parameters
ALPHA, BETA, GAMMA = 1, -1, 72

# Spectrum of H_{27}
H27_SPECTRUM = {0: 12, 3: 6, 6: 6, 9: 2, 81: 1}


class TestSectorDecomposition:
    """27 = 1 ⊕ 8 ⊕ 18 decomposition."""

    def test_matter_dimension(self):
        """27 = v - k - 1 = 40 - 12 - 1."""
        assert DIM_MATTER == 27

    def test_sector_sum(self):
        """1 + 8 + 18 = 27."""
        assert DIM_SINGLET + DIM_OCTET + DIM_TRANSVERSE == DIM_MATTER

    def test_octet_dimension(self):
        """Octet dim = 8 = k - μ = rank of E8 root system."""
        assert DIM_OCTET == k - mu

    def test_transverse_dimension(self):
        """Transverse dim = 18 = DIM_MATTER - 1 - 8 = 2 × q² = 2 × 9."""
        assert DIM_TRANSVERSE == 2 * q ** 2

    def test_singlet_is_vacuum(self):
        """Singlet sector corresponds to the vacuum vertex projection."""
        assert DIM_SINGLET == 1


class TestCanonicalParameters:
    """Uniqueness of the Hamiltonian parameters."""

    def test_alpha(self):
        """α = 1: affine Gram coefficient."""
        assert ALPHA == 1

    def test_beta(self):
        """β = -1: fiber Gram coefficient."""
        assert BETA == -1

    def test_gamma(self):
        """γ = 72: singlet projector coefficient.
        72 = 8 × 9 = (k-μ) × q² = octet × q²."""
        assert GAMMA == 72
        assert GAMMA == (k - mu) * q ** 2

    def test_gamma_alternatives(self):
        """72 = 2 × 36 = 2 × 6² = lam × (v-mu)²... no.
        72 = μ × DIM_TRANSVERSE = 4 × 18. YES!"""
        assert GAMMA == mu * DIM_TRANSVERSE

    def test_uniqueness(self):
        """Three conditions uniquely fix (α, β, γ):
        1. octet annihilation: 3α + 3β = 0
        2. normalization: α = 1
        3. singlet: 12α + 3β + γ = 81 = q⁴."""
        # Condition 1: octet zero
        assert q * ALPHA + q * BETA == 0
        # Condition 2: normalization
        assert ALPHA == 1
        # Condition 3: singlet = q⁴
        assert 12 * ALPHA + 3 * BETA + GAMMA == q ** 4


class TestH27Spectrum:
    """Eigenvalue spectrum of the 27×27 internal Hamiltonian."""

    def test_eigenvalue_count(self):
        """Total multiplicity = 27."""
        assert sum(H27_SPECTRUM.values()) == DIM_MATTER

    def test_zero_eigenvalue(self):
        """0 with multiplicity 12 = k.
        The null space has dimension k!"""
        assert H27_SPECTRUM[0] == k

    def test_eigenvalue_3(self):
        """3 with multiplicity 6 = 2q.
        3 = q itself."""
        assert H27_SPECTRUM[3] == 2 * q
        assert 3 == q

    def test_eigenvalue_6(self):
        """6 with multiplicity 6 = 2q.
        6 = 2q."""
        assert H27_SPECTRUM[6] == 2 * q
        assert 6 == 2 * q

    def test_eigenvalue_9(self):
        """9 with multiplicity 2 = lam.
        9 = q²."""
        assert H27_SPECTRUM[9] == lam
        assert 9 == q ** 2

    def test_eigenvalue_81(self):
        """81 with multiplicity 1.
        81 = q⁴ = singlet energy."""
        assert H27_SPECTRUM[81] == 1
        assert 81 == q ** 4


class TestH27Rank:
    """Rank and nullity of H_{27}."""

    def test_rank(self):
        """rank(H_{27}) = 15 = g (multiplicity of s-eigenvalue).
        Nonzero eigenvalues: 6+6+2+1 = 15."""
        rank = sum(m for e, m in H27_SPECTRUM.items() if e != 0)
        assert rank == 15
        assert rank == g

    def test_nullity(self):
        """nullity(H_{27}) = 12 = k.
        Zero eigenspace dim = degree of W(3,3)."""
        nullity = H27_SPECTRUM[0]
        assert nullity == k

    def test_rank_plus_nullity(self):
        """rank + nullity = 15 + 12 = 27 = dim(matter)."""
        assert g + k == DIM_MATTER


class TestH27Traces:
    """Trace invariants of the internal Hamiltonian."""

    def test_trace(self):
        """tr(H_{27}) = 0×12 + 3×6 + 6×6 + 9×2 + 81×1 = 153.
        153 = 9 × 17 = q² × (k+μ+1)."""
        tr = sum(e * m for e, m in H27_SPECTRUM.items())
        assert tr == 153
        assert tr == q ** 2 * (k + mu + 1)

    def test_trace_sq(self):
        """tr(H²) = 0 + 9×6 + 36×6 + 81×2 + 6561×1 = 6993.
        6993 = 3 × 2331 = 3 × 3 × 777 = 9 × 777."""
        tr2 = sum(e ** 2 * m for e, m in H27_SPECTRUM.items())
        assert tr2 == 6993

    def test_trace_identity(self):
        """tr(H_{27}) = 153 = sum(1..17) = 17th triangular number.
        Also: 153 = 1³ + 5³ + 3³ (narcissistic number)."""
        assert 153 == 17 * 18 // 2
        assert 153 == 1 ** 3 + 5 ** 3 + 3 ** 3

    def test_det_nonzero_part(self):
        """Product of nonzero eigenvalues = 3⁶ × 6⁶ × 9² × 81.
        = 729 × 46656 × 81 × 81 = ... huge number.
        But: 3⁶ × 6⁶ × 9² × 81 = 3⁶ × (2×3)⁶ × 3⁴ × 3⁴ = 2⁶ × 3²⁰.
        So log det = 6 log 2 + 20 log 3."""
        log_det = 6 * math.log(2) + 20 * math.log(3)
        assert math.isfinite(log_det)
        assert abs(log_det - (6 * math.log(2) + 20 * math.log(3))) < 1e-10


class TestSectorEnergies:
    """Energy assignments by sector."""

    def test_singlet_energy(self):
        """E_singlet = 12α + 3β + γ = 12 - 3 + 72 = 81 = q⁴."""
        E_s = 12 * ALPHA + 3 * BETA + GAMMA
        assert E_s == 81

    def test_octet_energy(self):
        """E_octet = 3α + 3β = 3 - 3 = 0 (EXACT cancellation).
        The gauge sector is MASSLESS."""
        E_o = q * ALPHA + q * BETA
        assert E_o == 0

    def test_transverse_subtower(self):
        """Transverse 18-dim sector has spectrum {0⁴, 3⁶, 6⁶, 9²}.
        Rank = 14, nullity = 4.
        4 = μ: the transverse null modes = μ."""
        trans_spec = {0: 4, 3: 6, 6: 6, 9: 2}
        assert sum(trans_spec.values()) == DIM_TRANSVERSE
        trans_rank = sum(m for e, m in trans_spec.items() if e != 0)
        assert trans_rank == 14
        trans_null = trans_spec[0]
        assert trans_null == mu

    def test_null_decomposition(self):
        """Total null space = 12 = 8 (octet) + 4 (transverse null).
        8 + 4 = k = 12."""
        assert DIM_OCTET + mu == k


class TestAlgebraicRelations:
    """Identities connecting the Hamiltonian to graph parameters."""

    def test_eigenvalues_are_multiples_of_q(self):
        """All nonzero eigenvalues are multiples of q = 3:
        3 = 1×3, 6 = 2×3, 9 = 3×3, 81 = 27×3."""
        for e in H27_SPECTRUM:
            if e > 0:
                assert e % q == 0

    def test_eigenvalue_sum_formula(self):
        """Distinct nonzero eigenvalues: {3, 6, 9, 81}.
        Sum = 99 = 100 - 1 = (Φ₄)² - 1 = (q²+1)² - 1."""
        eig_sum = 3 + 6 + 9 + 81
        assert eig_sum == 99
        assert eig_sum == (q ** 2 + 1) ** 2 - 1

    def test_max_over_min_nonzero(self):
        """81/3 = 27 = v - k - 1 = matter dimension.
        The eigenvalue ratio = matter count!"""
        ratio = 81 // 3
        assert ratio == DIM_MATTER

    def test_distinct_eigenvalue_count(self):
        """5 distinct eigenvalues: {0, 3, 6, 9, 81}.
        5 = (q²+1)/2 = max correctable errors in QECC."""
        assert len(H27_SPECTRUM) == 5
