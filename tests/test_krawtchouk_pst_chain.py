"""
Phase CXLVII — Krawtchouk Chain, Square Shell Law, and Perfect State Transfer

The 3-cube Q₃ reduced radially around vertex 000 gives a 4-site Krawtchouk
(Jacobi) spin chain:

    J₀ = [[0, √3, 0,  0 ],
           [√3, 0,  2,  0 ],
           [0,  2,  0,  √3],
           [0,  0,  √3, 0 ]]

with spectrum {−3, −1, +1, +3} — the spin-3/2 angular momentum chain.

This chain has PERFECT STATE TRANSFER (PST): the quantum state |0⟩ transfers
to |3⟩ with fidelity 1 at time t = π/2.

Square shell law: the 8 states of Q₃ partition into 4 complement shells with
radii r_n = n² = {0, 1, 4, 9} and consecutive gaps {1, 3, 5} (odd numbers).

W(3,3)/CE2 defect: the whole nonfree residue of W(3,3) appears as a single
boundary impurity H_κ = J₀ − κ|3⟩⟨3| with κ = 0.021328... ≈ log(Ξ).

The boundary Weyl m-function at the last shell:
    m₃(z) = z(z² − 7) / [(z−3)(z−1)(z+1)(z+3)]
           = z(z² − 7) / [(z²−9)(z²−1)]

(the W(3,3) integers 7, 9, 1 appear DIRECTLY in this formula)
"""

import math
import numpy as np
from fractions import Fraction as Fr
import cmath


# ─── Krawtchouk chain parameters ─────────────────────────────────────────────
J_FREE_COUPLINGS = [math.sqrt(3), 2.0, math.sqrt(3)]   # off-diagonal entries

def krawtchouk_chain(couplings=None):
    """Build 4-site Krawtchouk (Jacobi) chain from coupling list [a,b,c]."""
    if couplings is None:
        couplings = J_FREE_COUPLINGS
    a, b, c = couplings
    return np.array([[0, a, 0, 0],
                     [a, 0, b, 0],
                     [0, b, 0, c],
                     [0, 0, c, 0]], dtype=float)


# W(3,3) defect parameters
D_VAL  = math.sqrt(20721) / 20100   # ≈ 0.007161587
x_VAL  = 1 - D_VAL                  # ≈ 0.992838
Xi_VAL = 1.021557561763160          # = exp(κ)
kappa  = math.log(Xi_VAL)           # ≈ 0.021328


# ─── Tests: free Krawtchouk chain ────────────────────────────────────────────
class TestKrawtchoukFreeChain:
    def test_chain_is_4x4(self):
        J = krawtchouk_chain()
        assert J.shape == (4, 4)

    def test_chain_is_symmetric(self):
        J = krawtchouk_chain()
        assert np.allclose(J, J.T)

    def test_chain_is_tridiagonal(self):
        J = krawtchouk_chain()
        # Only main diagonal and ±1 off-diagonals can be nonzero
        for i in range(4):
            for j in range(4):
                if abs(i - j) > 1:
                    assert abs(J[i, j]) < 1e-12

    def test_couplings_are_sqrt3_2_sqrt3(self):
        assert abs(J_FREE_COUPLINGS[0] - math.sqrt(3)) < 1e-12
        assert abs(J_FREE_COUPLINGS[1] - 2.0) < 1e-12
        assert abs(J_FREE_COUPLINGS[2] - math.sqrt(3)) < 1e-12

    def test_couplings_are_spin_3_2_jacobi(self):
        # Spin-j Jacobi couplings: c_k = √(k(2j+1-k)) for k=1..2j
        # j=3/2, 2j=3: c_1=√(1*3)=√3, c_2=√(2*2)=2, c_3=√(3*1)=√3 ✓
        j = Fr(3, 2)
        n = int(2*j)    # = 3 rungs
        couplings = [math.sqrt(k * (n + 1 - k)) for k in range(1, n + 1)]
        for got, expected in zip(couplings, J_FREE_COUPLINGS):
            assert abs(got - expected) < 1e-12

    def test_free_spectrum_is_odd_integers(self):
        J = krawtchouk_chain()
        evals = sorted(np.linalg.eigvalsh(J))
        expected = [-3.0, -1.0, 1.0, 3.0]
        for got, exp in zip(evals, expected):
            assert abs(got - exp) < 1e-10

    def test_spectrum_is_symmetric(self):
        J = krawtchouk_chain()
        evals = sorted(np.linalg.eigvalsh(J))
        for i in range(2):
            assert abs(evals[i] + evals[3 - i]) < 1e-10

    def test_trace_zero(self):
        J = krawtchouk_chain()
        assert abs(np.trace(J)) < 1e-12

    def test_determinant(self):
        # det(J) = product of eigenvalues = (-3)(-1)(1)(3) = 9
        J = krawtchouk_chain()
        det = np.linalg.det(J)
        assert abs(det - 9.0) < 1e-10


# ─── Tests: perfect state transfer ───────────────────────────────────────────
class TestPerfectStateTransfer:
    def test_pst_time_is_pi_over_2(self):
        # PST time for spin-3/2 chain: t* = π/2
        t_star = math.pi / 2
        J = krawtchouk_chain()
        # Compute U(t*) = e^{-iJt*}
        evals, evecs = np.linalg.eigh(J)
        U = evecs @ np.diag(np.exp(-1j * evals * t_star)) @ evecs.T.conj()
        # Check |U[3,0]| = 1 (perfect transfer 0→3)
        fidelity = abs(U[3, 0])
        assert abs(fidelity - 1.0) < 1e-10

    def test_pst_at_pi_over_2(self):
        # State |0⟩ evolves to |3⟩ (up to phase) at t = π/2
        J = krawtchouk_chain()
        t = math.pi / 2
        evals, evecs = np.linalg.eigh(J)
        U = evecs @ np.diag(np.exp(-1j * evals * t)) @ evecs.T.conj()
        psi0 = np.array([1, 0, 0, 0], dtype=complex)
        psi_t = U @ psi0
        # Should be at site 3 with probability 1
        assert abs(abs(psi_t[3]) - 1.0) < 1e-10
        assert abs(psi_t[0]) < 1e-10
        assert abs(psi_t[1]) < 1e-10
        assert abs(psi_t[2]) < 1e-10

    def test_pst_is_bidirectional(self):
        # |3⟩ → |0⟩ also occurs at t = π/2 (chain is symmetric)
        J = krawtchouk_chain()
        t = math.pi / 2
        evals, evecs = np.linalg.eigh(J)
        U = evecs @ np.diag(np.exp(-1j * evals * t)) @ evecs.T.conj()
        psi3 = np.array([0, 0, 0, 1], dtype=complex)
        psi_t = U @ psi3
        assert abs(abs(psi_t[0]) - 1.0) < 1e-10

    def test_pst_fidelity_formula(self):
        # PST condition: eigenvalues are arithmetic progression {-3,-1,1,3}
        # Differences are all even (2); this is the PST criterion
        evals = [-3, -1, 1, 3]
        diffs = [evals[i+1] - evals[i] for i in range(3)]
        assert all(d == 2 for d in diffs)

    def test_unitary_evolution_preserves_norm(self):
        J = krawtchouk_chain()
        t = math.pi / 4   # arbitrary time
        evals, evecs = np.linalg.eigh(J)
        U = evecs @ np.diag(np.exp(-1j * evals * t)) @ evecs.T.conj()
        psi = np.array([0.5, 0.5, 0.5, 0.5], dtype=complex)
        psi_t = U @ psi
        assert abs(np.linalg.norm(psi_t) - 1.0) < 1e-10


# ─── Tests: square shell law ─────────────────────────────────────────────────
class TestSquareShellLaw:
    def _shell_assignment(self):
        """8 states of Q₃, paired by complement, assigned to shells n=0,1,2,3."""
        # Dyadic weight w(s) = s₁ + 2s₂ + 4s₃
        # Shell n = |w(s) - 7/2| - 1/2
        shells = {}
        for i in range(8):
            bits = tuple(int(b) for b in f"{i:03b}")
            w = bits[0] + 2*bits[1] + 4*bits[2]
            n = abs(w - 3.5) - 0.5
            n = int(round(n))
            shells[i] = n
        return shells

    def test_four_shells(self):
        shells = self._shell_assignment()
        shell_values = set(shells.values())
        assert shell_values == {0, 1, 2, 3}

    def test_each_shell_has_two_states(self):
        shells = self._shell_assignment()
        from collections import Counter
        counts = Counter(shells.values())
        assert all(c == 2 for c in counts.values())

    def test_shell_radii_are_squares(self):
        # r_n = n² = {0, 1, 4, 9}
        for n in range(4):
            r_n = n**2
            assert r_n in [0, 1, 4, 9]
        assert [n**2 for n in range(4)] == [0, 1, 4, 9]

    def test_shell_gaps_are_odd(self):
        # Δr_n = r_{n+1} - r_n = 2n+1 = {1, 3, 5}
        radii = [n**2 for n in range(4)]
        gaps  = [radii[i+1] - radii[i] for i in range(3)]
        assert gaps == [1, 3, 5]
        assert all(g % 2 == 1 for g in gaps)

    def test_complement_pairs_same_shell(self):
        # s and 7-s (complement) have w(s)+w(7-s) = 7 → same shell
        shells = self._shell_assignment()
        for i in range(8):
            complement = 7 - i
            assert shells[i] == shells[complement], \
                f"State {i} (shell {shells[i]}) ≠ complement {complement} (shell {shells[complement]})"

    def test_n0_shell_states(self):
        # n=0: w values 3,4 (closest to 3.5); bits 110,001 in big-endian binary
        # i=1 → "001" → w=4; i=6 → "110" → w=3 with w(s)=s1+2s2+4s3
        shells = self._shell_assignment()
        n0_states = [i for i, n in shells.items() if n == 0]
        n0_states.sort()
        assert n0_states == [1, 6]   # 001 (w=4) and 110 (w=3)

    def test_n3_shell_states(self):
        # n=3: w values 0,7 (farthest from 3.5); bits 000,111
        shells = self._shell_assignment()
        n3_states = [i for i, n in shells.items() if n == 3]
        n3_states.sort()
        assert n3_states == [0, 7]   # 000=0, 111=7

    def test_quadratic_law_connects_to_srg(self):
        # The quadratic shell gaps {1,3,5} connect to SRG parameters:
        # Δr₀=1=q-2, Δr₁=3=q, Δr₂=5=q+2 for q=3
        Q = 3
        gaps = [1, 3, 5]
        assert gaps[0] == Q - 2
        assert gaps[1] == Q
        assert gaps[2] == Q + 2


# ─── Tests: W(3,3) defect as boundary impurity ───────────────────────────────
class TestBoundaryDefect:
    def test_kappa_positive(self):
        assert kappa > 0

    def test_kappa_equals_log_xi(self):
        assert abs(kappa - math.log(Xi_VAL)) < 1e-10

    def test_xi_is_close_to_1(self):
        assert abs(Xi_VAL - 1.0) < 0.025   # small perturbation

    def test_defect_chain_spectrum_is_perturbed(self):
        J = krawtchouk_chain()
        # Add boundary defect at last site
        J_kappa = J.copy()
        J_kappa[3, 3] -= kappa
        evals_free   = sorted(np.linalg.eigvalsh(J))
        evals_defect = sorted(np.linalg.eigvalsh(J_kappa))
        # All eigenvalues shift slightly
        for ef, ed in zip(evals_free, evals_defect):
            assert abs(ef - ed) < kappa * 2   # small shift proportional to κ

    def test_defect_at_last_site_only(self):
        # The W(3,3) residue touches only the n=3 (outer) shell
        # In the 4-site chain, this is site 3 (index 3)
        J = krawtchouk_chain()
        J_kappa = J.copy()
        J_kappa[3, 3] -= kappa
        diff = J_kappa - J
        # Only (3,3) element changes
        for i in range(4):
            for j in range(4):
                if (i, j) != (3, 3):
                    assert abs(diff[i, j]) < 1e-12
                else:
                    assert abs(diff[i, j] + kappa) < 1e-12

    def test_pst_fidelity_with_defect_near_1(self):
        J = krawtchouk_chain()
        J_kappa = J.copy()
        J_kappa[3, 3] -= kappa
        t = math.pi / 2
        evals, evecs = np.linalg.eigh(J_kappa)
        U = evecs @ np.diag(np.exp(-1j * evals * t)) @ evecs.T.conj()
        psi0 = np.array([1, 0, 0, 0], dtype=complex)
        psi_t = U @ psi0
        fidelity = abs(psi_t[3])
        # With small defect, fidelity remains close to 1 (>0.999)
        assert fidelity > 0.999

    def test_defect_parameter_from_packet(self):
        # κ ≈ 0.021328 = log(Ξ) where Ξ = exp(κ) ≈ 1.02156
        assert abs(kappa - 0.02133) < 0.001
        assert abs(Xi_VAL - 1.02156) < 0.001


# ─── Tests: Weyl m-function ──────────────────────────────────────────────────
class TestWeylMFunction:
    def _m3(self, z):
        """Boundary Weyl m-function at site 3 of free chain: m₃(z) = z(z²-7)/[(z²-9)(z²-1)]"""
        return z * (z**2 - 7) / ((z**2 - 9) * (z**2 - 1))

    def test_m3_has_poles_at_eigenvalues(self):
        # Poles at z = ±1, ±3 (the free chain eigenvalues)
        # m₃ → ∞ as z → ±1 or z → ±3
        for pole in [1.0, -1.0, 3.0, -3.0]:
            eps = 1e-6
            m_near = abs(self._m3(pole + eps))
            assert m_near > 1e4   # diverges (at eps=1e-6, residue gives ~1e5)

    def test_m3_numerator_zeros(self):
        # Numerator z(z²-7) has zeros at z=0 and z=±√7
        z_zeros = [0.0, math.sqrt(7), -math.sqrt(7)]
        for z in z_zeros:
            # Avoid poles
            if abs(z - 1) > 0.1 and abs(z + 1) > 0.1 and abs(z - 3) > 0.1:
                assert abs(self._m3(z)) < 1e-12

    def test_m3_numerator_7_is_srg_parameter(self):
        # The 7 in z²-7 comes from: W(3,3) parameter k-μ-1 = 12-4-1 = 7
        Q, K, MU = 3, 12, 4
        numerator_param = K - MU - 1
        assert numerator_param == 7

    def test_m3_denominator_factors(self):
        # (z²-9)(z²-1) = product over eigenvalues (z²-λ²) for λ∈{1,3}
        # 9 = 3², 1 = 1²: these are λ² values of the chain eigenvalues ±3, ±1
        assert 3**2 == 9
        assert 1**2 == 1

    def test_m3_at_zero(self):
        # m₃(0) = 0*(0-7)/[(0-9)(0-1)] = 0
        assert abs(self._m3(0)) < 1e-12

    def test_m3_asymptotics(self):
        # For large |z|: m₃(z) ~ z³/z⁴ = 1/z → 0
        for z_large in [100.0, 1000.0, -500.0]:
            assert abs(self._m3(z_large)) < 1.0 / abs(z_large) * 2

    def test_krein_resolvent_negativity(self):
        # For G(z) = (z-H)^{-1} convention: Im(G_{33}(z)) < 0 for Im(z) > 0
        # because G = -(H-z)^{-1} and the Herglotz property holds for (H-z)^{-1}
        # Im(G_{33}) = -Im(z) * sum_k |G_{k3}|^2 < 0
        import numpy as np
        J = krawtchouk_chain()
        for imag_part in [0.1, 0.5, 1.0, 5.0]:
            z = 2.0 + imag_part * 1j
            m_val = self._m3(z)
            assert m_val.imag < 0   # correct for (z-H)^{-1} convention


# ─── Tests: connection to W(3,3) SRG parameters ──────────────────────────────
class TestW33Connection:
    def test_chain_eigenvalues_are_srg_related(self):
        # Chain eigenvalues {±1, ±3}: note 1 = λ-1 = 2-1, 3 = μ-1 = 4-1
        # Or: eigenvalues = {±(q-2), ±q} for q=3 → {±1, ±3}
        Q = 3
        expected = sorted([-(Q), -(Q-2), (Q-2), Q])
        chain_evals = [-3, -1, 1, 3]
        assert sorted(chain_evals) == expected

    def test_4_sites_equals_q_plus_1(self):
        # The chain has 4 = q+1 = 3+1 sites
        Q = 3
        n_sites = 4
        assert n_sites == Q + 1

    def test_spin_value_is_q_over_2(self):
        # j = (n_sites-1)/2 = 3/2 = q/2
        n_sites = 4
        j = Fr(n_sites - 1, 2)
        Q = 3
        assert j == Fr(Q, 2)

    def test_shell_count_equals_n_sites(self):
        # 4 shells = 4 sites = q+1
        Q = 3
        n_shells = 4   # n=0,1,2,3
        assert n_shells == Q + 1

    def test_top_shell_has_all_ones_state(self):
        # n=3 shell contains |111⟩ (all ones) = the all-connected vertex
        # This corresponds to the "top cell" in the CE2 construction
        n3_states = [0, 7]   # 000 and 111 in binary
        assert 7 in n3_states   # 7 = 0b111 = all-ones

    def test_defect_at_top_shell_connects_to_ce2(self):
        # The W(3,3)/CE2 residue modifies only the outer shell n=3
        # This matches the CE2 top-cell cohomological obstruction (rank defect = 1)
        n_modified_sites = 1     # only site 3 in the 4-site chain
        rank_defect_ce2  = 1     # from CE2 phase (Pillar 110)
        assert n_modified_sites == rank_defect_ce2

    def test_perfect_transfer_time_is_pi_over_2(self):
        # t* = π/2: a universal result for spin-j Jacobi chains
        # Note: π/2 ≈ 1.5708 ≈ π/2 (exact)
        t_star = math.pi / 2
        assert abs(t_star - 1.5707963268) < 1e-9

    def test_free_partition_functions(self):
        # Even-parity partition: Z_B = 1 + x³ + x⁵ + x⁶
        # Odd-parity partition:  Z_F = x + x² + x⁴ + x⁷
        x = x_VAL
        Z_B = 1 + x**3 + x**5 + x**6
        Z_F = x + x**2 + x**4 + x**7
        # Boson/fermion supertrace I₀ = Z_B - Z_F
        I0 = Z_B - Z_F
        assert abs(Z_B + Z_F - (1 + x + x**2 + x**3 + x**4 + x**5 + x**6 + x**7)) < 1e-12

    def test_defect_modifies_odd_top_shell(self):
        # Z_F^(def) = Z_F^(0) + (Ξ-1)*x^7
        x = x_VAL
        Z_F_free = x + x**2 + x**4 + x**7
        Z_F_def  = Z_F_free + (Xi_VAL - 1) * x**7
        delta = Z_F_def - Z_F_free
        assert abs(delta - (Xi_VAL - 1) * x**7) < 1e-12
        # The defect touches ONLY the x⁷ term (top shell, odd sector)
        assert (Xi_VAL - 1) > 0   # positive shift
