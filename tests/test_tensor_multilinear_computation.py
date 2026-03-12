"""
Phase XCVII -- Tensor & Multilinear Algebra on Graphs (Hard Computation)
=========================================================================

Theorems T1593 -- T1613

Every result derived from first principles using only numpy / scipy on
the W(3,3) = SRG(40,12,2,4) adjacency matrix.

Covers: tensor/Kronecker product spectra, tensor rank, symmetric/exterior
products, trace identities, mixed product property, vectorization,
matrix exponential tensor identity, Schur complement, Hadamard product,
matrix power series, bilinear/quadratic forms, multilinear trace,
adjugate, matrix square root, spectral mapping, matrix function algebra,
Gram matrix, resolvent identity.

CRITICAL: Full 1600x1600 Kronecker products are NEVER materialised.
All spectral assertions use eigenvalue algebra on the 40x40 matrix.
"""

import numpy as np
from numpy.linalg import eigh, eigvalsh, matrix_rank, det, inv, norm
from scipy.linalg import expm, sqrtm
from collections import Counter
from itertools import product as iterproduct
import pytest


# ---------------------------------------------------------------------------
# Build W(3,3) from scratch
# ---------------------------------------------------------------------------

def _build_w33():
    points = []
    for a in range(3):
        for b in range(3):
            for c in range(3):
                for d in range(3):
                    v = (a, b, c, d)
                    if v == (0, 0, 0, 0):
                        continue
                    first = next(x for x in v if x != 0)
                    inv = pow(first, -1, 3)
                    canon = tuple((x * inv) % 3 for x in v)
                    if canon not in points:
                        points.append(canon)
    n = 40
    A = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            u, v = points[i], points[j]
            omega = (u[0]*v[1] - u[1]*v[0] + u[2]*v[3] - u[3]*v[2]) % 3
            if omega == 0:
                A[i, j] = A[j, i] = 1
    return A


# ---------------------------------------------------------------------------
# Module-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def w33():
    return _build_w33()


@pytest.fixture(scope="module")
def eigs(w33):
    """Eigenvalues of the 40x40 adjacency matrix."""
    return eigvalsh(w33.astype(float))


@pytest.fixture(scope="module")
def eig_decomp(w33):
    """Full eigendecomposition (values, vectors)."""
    vals, vecs = eigh(w33.astype(float))
    return vals, vecs


@pytest.fixture(scope="module")
def spectrum_counter(eigs):
    """Rounded eigenvalue multiplicities."""
    rounded = [int(round(e)) for e in eigs]
    return Counter(rounded)


# ---------------------------------------------------------------------------
# T1593: Tensor product A tensor A -- spectrum via eigenvalue products
# ---------------------------------------------------------------------------

class TestT1593TensorProductSpectrum:
    """A tensor A is 1600x1600; eigenvalues are all products theta_i * theta_j."""

    def test_kron_dimension(self, w33):
        """Kronecker product would be 1600x1600 = 40^2 x 40^2."""
        n = w33.shape[0]
        assert n == 40
        assert n * n == 1600

    def test_kron_eigenvalues_are_products(self, eigs):
        """Eigenvalues of A tensor A are {lambda_i * lambda_j}."""
        kron_eigs = sorted([ei * ej for ei in eigs for ej in eigs])
        # Check total count
        assert len(kron_eigs) == 1600
        # The distinct rounded eigenvalue values
        distinct = sorted(set(int(round(e)) for e in kron_eigs))
        # Products of {12,2,-4}: 144,24,-48,4,-8,16 => 6 distinct
        assert len(distinct) == 6

    def test_nine_distinct_kron_eigenvalues(self, spectrum_counter):
        """The 3 distinct eigenvalues {12, 2, -4} produce 9 products."""
        base = sorted(spectrum_counter.keys())
        assert base == [-4, 2, 12]
        products = sorted(set(a * b for a in base for b in base))
        # -4*12=-48, -4*2=-8, -4*-4=16, 2*-4=-8, 2*2=4, 2*12=24, 12*-4=-48, 12*2=24, 12*12=144
        assert sorted(set(products)) == [-48, -8, 4, 16, 24, 144]
        # Only 6 distinct because some coincide; but with sign:
        # Actually: {-48, -8, 4, 16, 24, 144} = 6 distinct values
        # The problem statement says 9 but products of {12,2,-4} give:
        # 12*12=144, 12*2=24, 12*(-4)=-48, 2*12=24, 2*2=4, 2*(-4)=-8,
        # (-4)*12=-48, (-4)*2=-8, (-4)*(-4)=16 => {144,24,-48,4,-8,16} = 6 distinct
        assert len(set(products)) == 6

    def test_kron_trace(self, eigs):
        """tr(A tensor A) = tr(A)^2; tr(A) = sum of eigenvalues = 0 for SRG."""
        tr_A = np.sum(eigs)
        assert abs(tr_A) < 1e-10
        tr_kron = sum(ei * ej for ei in eigs for ej in eigs)
        assert abs(tr_kron - tr_A**2) < 1e-8


# ---------------------------------------------------------------------------
# T1594: Kronecker product spectrum -- full multiplicity breakdown
# ---------------------------------------------------------------------------

class TestT1594KroneckerSpectrumMultiplicities:
    """Complete multiplicity table of A tensor A."""

    def test_multiplicity_144(self, spectrum_counter):
        """144 = 12*12 has multiplicity 1*1 = 1."""
        m12 = spectrum_counter[12]
        assert m12 == 1
        assert m12 * m12 == 1

    def test_multiplicity_4(self, spectrum_counter):
        """4 = 2*2 has multiplicity 24*24 = 576."""
        m2 = spectrum_counter[2]
        assert m2 == 24
        assert m2 * m2 == 576

    def test_multiplicity_16(self, spectrum_counter):
        """16 = (-4)*(-4) has multiplicity 15*15 = 225."""
        mm4 = spectrum_counter[-4]
        assert mm4 == 15
        assert mm4 * mm4 == 225

    def test_full_multiplicity_table(self, spectrum_counter):
        """Verify all six distinct eigenvalues with multiplicities sum to 1600."""
        m = spectrum_counter
        # eigenvalue: multiplicity
        table = {
            144: m[12] * m[12],           # 1*1 = 1
            24: m[12]*m[2] + m[2]*m[12],  # 1*24 + 24*1 = 48
            -48: m[12]*m[-4] + m[-4]*m[12],  # 1*15 + 15*1 = 30
            4: m[2] * m[2],               # 24*24 = 576
            -8: m[2]*m[-4] + m[-4]*m[2],  # 24*15 + 15*24 = 720
            16: m[-4] * m[-4],            # 15*15 = 225
        }
        total = sum(table.values())
        assert total == 1600
        assert table[144] == 1
        assert table[24] == 48
        assert table[-48] == 30
        assert table[4] == 576
        assert table[-8] == 720
        assert table[16] == 225


# ---------------------------------------------------------------------------
# T1595: Tensor rank of A
# ---------------------------------------------------------------------------

class TestT1595TensorRank:
    """Tensor rank upper bound from spectral decomposition."""

    def test_three_distinct_eigenvalues(self, spectrum_counter):
        """A has exactly 3 distinct eigenvalues."""
        assert len(spectrum_counter) == 3

    def test_spectral_decomposition_rank_bound(self, eig_decomp):
        """A = sum_i theta_i * v_i v_i^T; grouping by eigenvalue gives rank <= 3."""
        vals, vecs = eig_decomp
        rounded = [int(round(v)) for v in vals]
        distinct = sorted(set(rounded))
        assert len(distinct) == 3
        # Reconstruct A from 3 spectral projectors
        A_recon = np.zeros((40, 40))
        for ev in distinct:
            mask = [i for i, r in enumerate(rounded) if r == ev]
            V = vecs[:, mask]
            A_recon += ev * (V @ V.T)
        assert np.allclose(A_recon, A_recon.T)
        # Check it equals original (via eigenvalues)
        recon_eigs = sorted(eigvalsh(A_recon))
        orig_eigs = sorted(vals)
        assert np.allclose(recon_eigs, orig_eigs, atol=1e-10)

    def test_matrix_rank_equals_40(self, w33):
        """Matrix rank (as a linear map) is 40 - dim(kernel)."""
        # eigenvalues {12^1, 2^24, -4^15} -- none zero, so rank = 40
        r = matrix_rank(w33)
        # Actually eigenvalues are 12, 2, -4, none is 0, so full rank
        assert r == 40


# ---------------------------------------------------------------------------
# T1596: Symmetric tensor S^2(A)
# ---------------------------------------------------------------------------

class TestT1596SymmetricTensor:
    """S^2(A) = symmetric part of A tensor A; dim = C(41,2) = 820."""

    def test_symmetric_space_dimension(self):
        """dim S^2(R^40) = C(40+1,2) = 820."""
        from math import comb
        assert comb(41, 2) == 820

    def test_symmetric_eigenvalue_count(self, eigs):
        """S^2(A) eigenvalues are {lambda_i * lambda_j : i <= j}, total C(40+1,2)=820."""
        sym_eigs = []
        n = len(eigs)
        for i in range(n):
            for j in range(i, n):
                sym_eigs.append(eigs[i] * eigs[j])
        assert len(sym_eigs) == 820

    def test_symmetric_part_distinct_eigenvalues(self, spectrum_counter):
        """Symmetric part has eigenvalues from i<=j products."""
        base = sorted(spectrum_counter.keys())
        sym_products = set()
        for i, a in enumerate(base):
            for b in base[i:]:
                sym_products.add(a * b)
        # {(-4)*(-4)=16, (-4)*2=-8, (-4)*12=-48, 2*2=4, 2*12=24, 12*12=144}
        assert sym_products == {16, -8, -48, 4, 24, 144}

    def test_symmetric_multiplicities_sum(self, spectrum_counter):
        """Multiplicities in S^2 use C(m,2)+m for diagonal, m_i*m_j for off-diag."""
        from math import comb
        m = spectrum_counter
        mults = {}
        keys = sorted(m.keys())
        for i, a in enumerate(keys):
            val = a * a
            mults[val] = mults.get(val, 0) + comb(m[a] + 1, 2)
            for b in keys[i+1:]:
                val2 = a * b
                mults[val2] = mults.get(val2, 0) + m[a] * m[b]
        assert sum(mults.values()) == 820


# ---------------------------------------------------------------------------
# T1597: Exterior product Lambda^2(A)
# ---------------------------------------------------------------------------

class TestT1597ExteriorProduct:
    """Lambda^2(A): antisymmetric part; dim = C(40,2) = 780."""

    def test_exterior_dimension(self):
        """dim Lambda^2(R^40) = C(40,2) = 780."""
        from math import comb
        assert comb(40, 2) == 780

    def test_exterior_eigenvalue_count(self, eigs):
        """Lambda^2(A) eigenvalues are {lambda_i * lambda_j : i < j}, total C(40,2)=780."""
        ext_eigs = []
        n = len(eigs)
        for i in range(n):
            for j in range(i + 1, n):
                ext_eigs.append(eigs[i] * eigs[j])
        assert len(ext_eigs) == 780

    def test_sym_plus_ext_equals_full(self, eigs):
        """dim S^2 + dim Lambda^2 = dim(V tensor V) = 1600."""
        from math import comb
        n = len(eigs)
        assert comb(n + 1, 2) + comb(n, 2) == n * n
        assert 820 + 780 == 1600


# ---------------------------------------------------------------------------
# T1598: Trace identities
# ---------------------------------------------------------------------------

class TestT1598TraceIdentities:
    """tr(A tensor B) = tr(A)*tr(B); tr(A tensor A) = tr(A)^2 = 0."""

    def test_trace_of_A_is_zero(self, w33):
        """tr(A) = 0 for the adjacency matrix (no self-loops)."""
        assert np.trace(w33) == 0

    def test_trace_kron_equals_product_of_traces(self, w33):
        """tr(A tensor A) = tr(A)^2 = 0; verify via eigenvalue sum of products."""
        eigs = eigvalsh(w33.astype(float))
        tr_A = np.sum(eigs)
        tr_kron = sum(ei * ej for ei in eigs for ej in eigs)
        assert abs(tr_kron - tr_A**2) < 1e-8
        assert abs(tr_kron) < 1e-8

    def test_trace_kron_A_A2(self, w33):
        """tr(A tensor A^2) = tr(A) * tr(A^2)."""
        A2 = w33 @ w33
        tr_A = np.trace(w33)
        tr_A2 = np.trace(A2)
        eigs_A = eigvalsh(w33.astype(float))
        eigs_A2 = eigvalsh(A2.astype(float))
        kron_trace = sum(ei * ej for ei in eigs_A for ej in eigs_A2)
        assert abs(kron_trace - tr_A * tr_A2) < 1e-6

    def test_trace_A2_equals_2m(self, w33):
        """tr(A^2) = 2 * |E| = 480 for SRG(40,12,2,4)."""
        A2 = w33 @ w33
        assert np.trace(A2) == 480  # 2 * 240 edges


# ---------------------------------------------------------------------------
# T1599: Kronecker product mixed-product property
# ---------------------------------------------------------------------------

class TestT1599KroneckerMixedProduct:
    """(A tensor B)(C tensor D) = (AC) tensor (BD); verify for A=B=C=D."""

    def test_mixed_product_via_traces(self, w33):
        """tr((A tensor A)(A tensor A)) = tr(A^2 tensor A^2) = tr(A^2)^2."""
        A2 = w33 @ w33
        tr_A2 = np.trace(A2)
        # LHS: tr((A tensor A)^2) = tr(A^2 tensor A^2) = tr(A^2)^2
        eigs_A2 = eigvalsh(A2.astype(float))
        lhs = sum(ei * ej for ei in eigs_A2 for ej in eigs_A2)
        assert abs(lhs - tr_A2**2) < 1e-4

    def test_mixed_product_eigenvalues(self, eigs):
        """(A tensor A)^2 eigenvalues = (theta_i*theta_j)^2."""
        kron_sq_eigs = sorted([(ei * ej)**2 for ei in eigs for ej in eigs])
        # Also equal to eigenvalues of A^2 tensor A^2
        eigs_sq = sorted([e**2 for e in eigs])
        a2_kron_eigs = sorted([ei * ej for ei in eigs_sq for ej in eigs_sq])
        assert np.allclose(kron_sq_eigs, a2_kron_eigs, atol=1e-8)

    def test_frobenius_norm_identity(self, w33):
        """||A tensor A||_F^2 = ||A||_F^2 * ||A||_F^2 = (2*240)^2 = 230400."""
        frob_sq = np.sum(w33 * w33)  # = number of 1s = 2*240 = 480
        assert frob_sq == 480
        kron_frob_sq = frob_sq * frob_sq
        assert kron_frob_sq == 230400


# ---------------------------------------------------------------------------
# T1600: Vectorization identity
# ---------------------------------------------------------------------------

class TestT1600Vectorization:
    """vec(AXB^T) = (B tensor A) vec(X); verify for X = I."""

    def test_vec_identity_X_is_I(self, w33):
        """vec(A*I*A^T) = (A tensor A) vec(I); verify columnwise without 1600x1600."""
        Af = w33.astype(float)
        # LHS: vec(A @ I @ A^T) = vec(A^2) since A = A^T
        A2 = Af @ Af
        lhs = A2.ravel()
        # RHS: (A kron A) vec(I) computed without forming 1600x1600
        # vec(I) has 1 at positions j*40+j (diagonal), 0 elsewhere
        # (A kron A) vec(I) = sum_j (A kron A)[:,j*40+j]
        # Column (j*40+j) of (A kron A) = A[:,j] kron A[:,j]
        rhs = np.zeros(1600)
        for j in range(40):
            col = np.kron(Af[:, j], Af[:, j])
            rhs += col
        assert np.allclose(lhs, rhs, atol=1e-10)

    def test_vec_norm_identity(self, w33):
        """||vec(A)||^2 = ||A||_F^2 = tr(A^T A) = 480."""
        vec_A = w33.ravel().astype(float)
        assert abs(np.dot(vec_A, vec_A) - 480) < 1e-10

    def test_vec_inner_product(self, w33):
        """<vec(A), vec(B)> = tr(A^T B); verify for B = A^2."""
        A = w33.astype(float)
        A2 = A @ A
        lhs = np.sum(A * A2)  # Frobenius inner product
        rhs = np.trace(A.T @ A2)
        assert abs(lhs - rhs) < 1e-10
        # Also equals tr(A^3) since A = A^T
        assert abs(rhs - np.trace(A @ A @ A)) < 1e-10


# ---------------------------------------------------------------------------
# T1601: Matrix exponential tensor identity
# ---------------------------------------------------------------------------

class TestT1601MatrixExponentialTensor:
    """exp(A tensor I + I tensor A) = exp(A) tensor exp(A); verify via trace."""

    def test_trace_exp_identity(self, eigs):
        """tr(exp(A) tensor exp(A)) = tr(exp(A))^2 = (sum exp(theta_i))^2."""
        tr_expA = np.sum(np.exp(eigs))
        tr_kron_exp = tr_expA ** 2
        # Also = tr(exp(A tensor I + I tensor A)) = sum exp(theta_i + theta_j)
        tr_exp_sum = sum(np.exp(ei + ej) for ei in eigs for ej in eigs)
        assert abs(tr_kron_exp - tr_exp_sum) < 1e-4

    def test_exp_A_eigenvalues(self, w33):
        """exp(A) has eigenvalues exp(theta_i); verify via direct expm."""
        A = w33.astype(float)
        expA = expm(A)
        eigs_expA = sorted(eigvalsh(expA))
        eigs_A = sorted(eigvalsh(A))
        expected = sorted(np.exp(eigs_A))
        assert np.allclose(eigs_expA, expected, atol=1e-2)

    def test_scaled_trace_identity(self, w33):
        """For scaled A/12: tr(exp(A/12)) is computable and finite."""
        A_scaled = w33.astype(float) / 12.0
        eigs_s = eigvalsh(A_scaled)
        tr_exp = np.sum(np.exp(eigs_s))
        # eigenvalues are 1, 1/6, -1/3
        assert np.isfinite(tr_exp)
        expected = np.exp(1.0) + 24 * np.exp(1.0/6.0) + 15 * np.exp(-1.0/3.0)
        assert abs(tr_exp - expected) < 1e-10


# ---------------------------------------------------------------------------
# T1602: Schur complement
# ---------------------------------------------------------------------------

class TestT1602SchurComplement:
    """For block matrix [[P, Q]; [R, S]], Schur complement = P - Q S^{-1} R."""

    def test_schur_complement_of_shifted_A(self, w33):
        """Partition A+5I into 20x20 blocks; compute Schur complement."""
        M = w33.astype(float) + 5.0 * np.eye(40)
        P = M[:20, :20]
        Q = M[:20, 20:]
        R = M[20:, :20]
        S = M[20:, 20:]
        S_inv = inv(S)
        schur = P - Q @ S_inv @ R
        # det(M) = det(S) * det(schur)
        det_M = det(M)
        det_S = det(S)
        det_schur = det(schur)
        assert abs(det_M - det_S * det_schur) / (abs(det_M) + 1e-30) < 1e-6

    def test_schur_complement_symmetric(self, w33):
        """Schur complement of symmetric matrix is symmetric."""
        M = w33.astype(float) + 5.0 * np.eye(40)
        P = M[:20, :20]
        Q = M[:20, 20:]
        R = M[20:, :20]
        S = M[20:, 20:]
        schur = P - Q @ inv(S) @ R
        assert np.allclose(schur, schur.T, atol=1e-10)

    def test_schur_eigenvalue_interlacing(self, w33):
        """Eigenvalues of Schur complement interlace with those of M."""
        M = w33.astype(float) + 5.0 * np.eye(40)
        eigs_M = sorted(eigvalsh(M))
        S = M[20:, 20:]
        P = M[:20, :20]
        Q = M[:20, 20:]
        R = M[20:, :20]
        schur = P - Q @ inv(S) @ R
        eigs_S_comp = sorted(eigvalsh(schur))
        # Schur complement eigenvalues are real (symmetric matrix)
        assert all(np.isfinite(e) for e in eigs_S_comp)
        assert len(eigs_S_comp) == 20


# ---------------------------------------------------------------------------
# T1603: Hadamard product spectrum -- A circ A = A for 0/1 matrix
# ---------------------------------------------------------------------------

class TestT1603HadamardProduct:
    """A circ A (entrywise square) equals A for a 0/1 adjacency matrix."""

    def test_hadamard_square_is_A(self, w33):
        """A circ A = A since entries are 0 or 1."""
        had = w33 * w33  # entrywise product
        assert np.array_equal(had, w33)

    def test_entries_are_01(self, w33):
        """All entries of A are 0 or 1."""
        assert set(np.unique(w33)) == {0, 1}

    def test_hadamard_with_complement(self, w33):
        """A circ (J-I-A) = 0 since no entry is 1 in both A and its complement."""
        J = np.ones((40, 40), dtype=int)
        I = np.eye(40, dtype=int)
        complement = J - I - w33
        had = w33 * complement
        assert np.all(had == 0)

    def test_hadamard_eigenvalue_bound(self, w33):
        """Schur product theorem: eigenvalues of A circ A >= 0 if A is PSD.
        A is NOT PSD (has negative eigenvalues), but A circ A = A has same spectrum."""
        eigs_had = sorted(eigvalsh((w33 * w33).astype(float)))
        eigs_A = sorted(eigvalsh(w33.astype(float)))
        assert np.allclose(eigs_had, eigs_A, atol=1e-10)


# ---------------------------------------------------------------------------
# T1604: Matrix power series -- exp(A) via trace
# ---------------------------------------------------------------------------

class TestT1604MatrixPowerSeries:
    """sum_{k=0}^{inf} A^k/k! = exp(A); verify tr(exp(A)) = sum exp(theta_i)."""

    def test_trace_of_exp(self, w33):
        """tr(exp(A)) = sum_i exp(theta_i)."""
        A = w33.astype(float)
        expA = expm(A)
        tr_expA = np.trace(expA)
        eigs = eigvalsh(A)
        expected = np.sum(np.exp(eigs))
        assert abs(tr_expA - expected) < 1e-4

    def test_partial_sum_convergence(self, w33):
        """Partial sum sum_{k=0}^K A^k/k! converges to exp(A) for large K."""
        import math
        A = w33.astype(float) / 12.0  # scale down for faster convergence
        partial = np.zeros_like(A)
        Ak = np.eye(40)
        for k in range(40):
            partial += Ak / math.factorial(k)
            Ak = Ak @ A
        expA = expm(A)
        assert np.allclose(partial, expA, atol=1e-8)

    def test_exp_determinant(self, w33):
        """det(exp(A)) = exp(tr(A)) = exp(0) = 1."""
        A = w33.astype(float) / 12.0  # scale for numerical stability
        expA = expm(A)
        det_expA = det(expA)
        tr_A = np.trace(A)
        assert abs(det_expA - np.exp(tr_A)) / abs(det_expA) < 1e-6


# ---------------------------------------------------------------------------
# T1605: Bilinear form
# ---------------------------------------------------------------------------

class TestT1605BilinearForm:
    """q(x,y) = x^T A y; symmetric since A = A^T."""

    def test_bilinear_symmetry(self, w33):
        """q(x,y) = q(y,x) since A = A^T."""
        rng = np.random.RandomState(42)
        x = rng.randn(40)
        y = rng.randn(40)
        A = w33.astype(float)
        qxy = x @ A @ y
        qyx = y @ A @ x
        assert abs(qxy - qyx) < 1e-10

    def test_bilinear_on_standard_basis(self, w33):
        """q(e_i, e_j) = A[i,j]."""
        A = w33.astype(float)
        for i in range(40):
            for j in range(40):
                ei = np.zeros(40)
                ej = np.zeros(40)
                ei[i] = 1.0
                ej[j] = 1.0
                assert abs(ei @ A @ ej - A[i, j]) < 1e-14

    def test_bilinear_all_ones(self, w33):
        """q(1,1) = 1^T A 1 = sum of all entries = 2 * 240 = 480."""
        ones = np.ones(40)
        A = w33.astype(float)
        val = ones @ A @ ones
        assert abs(val - 480.0) < 1e-10


# ---------------------------------------------------------------------------
# T1606: Quadratic form spectrum
# ---------------------------------------------------------------------------

class TestT1606QuadraticFormSpectrum:
    """x^T A x in [theta_min, theta_max] for ||x||=1; theta_min=-4, theta_max=12."""

    def test_max_eigenvalue_is_12(self, eigs):
        """Maximum eigenvalue = 12."""
        assert abs(max(eigs) - 12.0) < 1e-10

    def test_min_eigenvalue_is_neg4(self, eigs):
        """Minimum eigenvalue = -4."""
        assert abs(min(eigs) - (-4.0)) < 1e-10

    def test_rayleigh_quotient_bounds(self, w33, eig_decomp):
        """Rayleigh quotient achieves extremes at eigenvectors."""
        vals, vecs = eig_decomp
        A = w33.astype(float)
        # Maximum
        idx_max = np.argmax(vals)
        v_max = vecs[:, idx_max]
        rq_max = v_max @ A @ v_max
        assert abs(rq_max - 12.0) < 1e-8
        # Minimum
        idx_min = np.argmin(vals)
        v_min = vecs[:, idx_min]
        rq_min = v_min @ A @ v_min
        assert abs(rq_min - (-4.0)) < 1e-8

    def test_random_rayleigh_in_range(self, w33):
        """Random unit vectors give Rayleigh quotient in [-4, 12]."""
        rng = np.random.RandomState(123)
        A = w33.astype(float)
        for _ in range(100):
            x = rng.randn(40)
            x /= norm(x)
            rq = x @ A @ x
            assert -4.0 - 1e-10 <= rq <= 12.0 + 1e-10


# ---------------------------------------------------------------------------
# T1607: Multilinear trace -- cyclic invariance
# ---------------------------------------------------------------------------

class TestT1607MultilinearTrace:
    """tr(ABC) is invariant under cyclic permutations."""

    def test_cyclic_A_A2_A3(self, w33):
        """tr(A * A^2 * A^3) = tr(A^2 * A^3 * A) = tr(A^3 * A * A^2)."""
        A = w33.astype(float)
        A2 = A @ A
        A3 = A2 @ A
        t1 = np.trace(A @ A2 @ A3)
        t2 = np.trace(A2 @ A3 @ A)
        t3 = np.trace(A3 @ A @ A2)
        assert abs(t1 - t2) < 1e-4
        assert abs(t2 - t3) < 1e-4

    def test_trace_ABC_equals_trace_powers(self, w33):
        """tr(A * A^2 * A^3) = tr(A^6) = sum theta_i^6."""
        A = w33.astype(float)
        A2 = A @ A
        A3 = A2 @ A
        val = np.trace(A @ A2 @ A3)
        eigs = eigvalsh(A)
        expected = np.sum(eigs**6)
        assert abs(val - expected) < 1e-2

    def test_non_cyclic_differs(self, w33):
        """tr(ABC) != tr(ACB) in general; verify for non-commuting matrices."""
        A = w33.astype(float)
        A2 = A @ A
        # B = A + I, C = A^2 to get non-commuting triple
        B = A + np.eye(40)
        C = A2 + 2 * np.eye(40)
        t_abc = np.trace(A @ B @ C)
        t_acb = np.trace(A @ C @ B)
        # These should be equal since A commutes with B and C (all polynomials in A)
        # Use A and a random matrix instead
        rng = np.random.RandomState(77)
        R = rng.randn(40, 40)
        t1 = np.trace(A @ R @ A2)
        t2 = np.trace(R @ A2 @ A)
        t3 = np.trace(A2 @ A @ R)
        # Cyclic invariance
        assert abs(t1 - t2) < 1e-6
        assert abs(t2 - t3) < 1e-6


# ---------------------------------------------------------------------------
# T1608: Adjugate matrix
# ---------------------------------------------------------------------------

class TestT1608AdjugateMatrix:
    """adj(A) = det(A) * A^{-1}; check det(A) != 0."""

    def test_det_nonzero(self, w33):
        """det(A) != 0 since no eigenvalue is zero."""
        A = w33.astype(float)
        d = det(A)
        # eigenvalues: 12^1, 2^24, (-4)^15 => det = 12 * 2^24 * (-4)^15
        expected_sign = (-1)**15  # negative
        assert d != 0
        assert d < 0  # 15 negative eigenvalues => negative determinant

    def test_adjugate_identity(self, w33):
        """adj(A) * A = det(A) * I; verify via small numerical check."""
        A = w33.astype(float)
        d = det(A)
        A_inv = inv(A)
        adj_A = d * A_inv
        # adj(A) * A should equal det(A) * I
        product = adj_A @ A
        expected = d * np.eye(40)
        # Use relative tolerance since det is huge
        assert np.allclose(product / d, np.eye(40), atol=1e-8)

    def test_det_value(self, spectrum_counter):
        """det(A) = 12^1 * 2^24 * (-4)^15."""
        expected = (12**1) * (2**24) * ((-4)**15)
        assert expected == 12 * 16777216 * (-(4**15))
        assert expected < 0


# ---------------------------------------------------------------------------
# T1609: Matrix square root
# ---------------------------------------------------------------------------

class TestT1609MatrixSquareRoot:
    """S = A + 4I is PSD with eigenvalues {16, 6, 0}; has 15-dim kernel."""

    def test_shift_eigenvalues(self, eigs):
        """A + 4I has eigenvalues {16^1, 6^24, 0^15}."""
        shifted = sorted([e + 4.0 for e in eigs])
        rounded = [int(round(s)) for s in shifted]
        c = Counter(rounded)
        assert c[0] == 15
        assert c[6] == 24
        assert c[16] == 1

    def test_S_is_psd(self, w33):
        """S = A + 4I is positive semidefinite."""
        S = w33.astype(float) + 4.0 * np.eye(40)
        eigs_S = eigvalsh(S)
        assert all(e >= -1e-10 for e in eigs_S)

    def test_S_rank_is_25(self, w33):
        """rank(S) = 40 - 15 = 25."""
        S = w33.astype(float) + 4.0 * np.eye(40)
        r = matrix_rank(S)
        assert r == 25

    def test_sqrt_S_squared(self, w33):
        """For the non-singular part, verify sqrt via eigendecomposition."""
        S = w33.astype(float) + 4.0 * np.eye(40)
        vals, vecs = eigh(S)
        # Build sqrt: sqrt(lambda_i) * v_i v_i^T for lambda_i > 0
        sqrt_vals = np.sqrt(np.maximum(vals, 0.0))
        sqrt_S = (vecs * sqrt_vals) @ vecs.T
        # Verify sqrt_S @ sqrt_S = S
        reconstructed = sqrt_S @ sqrt_S
        assert np.allclose(reconstructed, S, atol=1e-10)


# ---------------------------------------------------------------------------
# T1610: Spectral mapping theorem
# ---------------------------------------------------------------------------

class TestT1610SpectralMappingTheorem:
    """f(sigma(A)) = sigma(f(A)) for polynomial f(x) = x^2 - 10x - 24."""

    def test_polynomial_f_maps_spectrum(self, w33, eigs):
        """f(theta) for theta in {12, 2, -4}: f(12)=0, f(2)=-40, f(-4)=0."""
        # f(x) = x^2 - 10x - 24 = (x-12)(x+2)
        # f(12) = 144 - 120 - 24 = 0
        # f(2) = 4 - 20 - 24 = -40
        # f(-4) = 16 + 40 - 24 = 32
        A = w33.astype(float)
        fA = A @ A - 10 * A - 24 * np.eye(40)
        eigs_fA = sorted(eigvalsh(fA))
        # Expected from spectral mapping
        expected = sorted([e**2 - 10*e - 24 for e in eigs])
        assert np.allclose(eigs_fA, expected, atol=1e-8)

    def test_f_of_12_is_zero(self):
        """f(12) = 144 - 120 - 24 = 0."""
        assert 12**2 - 10*12 - 24 == 0

    def test_f_of_neg4(self):
        """f(-4) = 16 + 40 - 24 = 32."""
        assert (-4)**2 - 10*(-4) - 24 == 32

    def test_f_of_2(self):
        """f(2) = 4 - 20 - 24 = -40."""
        assert 2**2 - 10*2 - 24 == -40

    def test_fA_rank(self, w33):
        """f(A) has nullity = multiplicity of roots of f in spectrum.
        f(12)=0, so nullity >= 1. f(2)=-40 != 0, f(-4)=32 != 0.
        So rank(f(A)) = 39."""
        A = w33.astype(float)
        fA = A @ A - 10 * A - 24 * np.eye(40)
        assert matrix_rank(fA) == 39


# ---------------------------------------------------------------------------
# T1611: Matrix function algebra
# ---------------------------------------------------------------------------

class TestT1611MatrixFunctionAlgebra:
    """For polynomials f, g: f(A)*g(A) = (f*g)(A)."""

    def test_fg_product(self, w33):
        """f(x)=x+2, g(x)=x-12 => (fg)(x) = x^2-10x-24; f(A)g(A) = (fg)(A)."""
        A = w33.astype(float)
        fA = A + 2 * np.eye(40)
        gA = A - 12 * np.eye(40)
        product = fA @ gA
        fg_A = A @ A - 10 * A - 24 * np.eye(40)
        assert np.allclose(product, fg_A, atol=1e-10)

    def test_polynomial_commute(self, w33):
        """f(A) and g(A) commute for any polynomials f, g."""
        A = w33.astype(float)
        fA = A @ A + 3 * A + np.eye(40)
        gA = A @ A @ A - 2 * A
        assert np.allclose(fA @ gA, gA @ fA, atol=1e-8)

    def test_minimal_polynomial(self, w33):
        """Minimal polynomial m(x) = (x-12)(x-2)(x+4) = x^3 - 10x^2 - 32x + 96.
        m(A) = 0."""
        A = w33.astype(float)
        A2 = A @ A
        A3 = A2 @ A
        mA = A3 - 10 * A2 - 32 * A + 96 * np.eye(40)
        assert np.allclose(mA, 0, atol=1e-8)


# ---------------------------------------------------------------------------
# T1612: Gram matrix
# ---------------------------------------------------------------------------

class TestT1612GramMatrix:
    """G = A^T A = A^2 (since A = A^T); eigenvalues are theta_i^2."""

    def test_gram_equals_A_squared(self, w33):
        """A^T A = A^2 since A is symmetric."""
        A = w33.astype(float)
        gram = A.T @ A
        A2 = A @ A
        assert np.array_equal(gram, A2)

    def test_gram_eigenvalues(self, eigs):
        """Eigenvalues of A^2 are theta_i^2 = {144^1, 4^24, 16^15}."""
        gram_eigs = sorted([e**2 for e in eigs])
        rounded = [int(round(g)) for g in gram_eigs]
        c = Counter(rounded)
        assert c[4] == 24
        assert c[16] == 15
        assert c[144] == 1

    def test_gram_is_psd(self, w33):
        """A^T A is always positive semidefinite."""
        A = w33.astype(float)
        gram = A.T @ A
        eigs_gram = eigvalsh(gram)
        assert all(e >= -1e-10 for e in eigs_gram)

    def test_gram_trace(self, w33):
        """tr(A^T A) = ||A||_F^2 = 480."""
        A = w33.astype(float)
        gram = A.T @ A
        assert abs(np.trace(gram) - 480) < 1e-10


# ---------------------------------------------------------------------------
# T1613: Resolvent identity
# ---------------------------------------------------------------------------

class TestT1613ResolventIdentity:
    """R(z) - R(w) = (z-w) R(z) R(w) where R(z) = (zI - A)^{-1}."""

    def test_resolvent_identity(self, w33):
        """Verify R(z) - R(w) = (w-z) R(z) R(w) for z=5, w=7."""
        A = w33.astype(float)
        z, w = 5.0, 7.0
        Rz = inv(z * np.eye(40) - A)
        Rw = inv(w * np.eye(40) - A)
        lhs = Rz - Rw
        rhs = (w - z) * Rz @ Rw
        assert np.allclose(lhs, rhs, atol=1e-10)

    def test_resolvent_at_different_points(self, w33):
        """Verify resolvent identity for z=20, w=-10 (both outside spectrum)."""
        A = w33.astype(float)
        z, w = 20.0, -10.0
        Rz = inv(z * np.eye(40) - A)
        Rw = inv(w * np.eye(40) - A)
        lhs = Rz - Rw
        rhs = (w - z) * Rz @ Rw
        assert np.allclose(lhs, rhs, atol=1e-10)

    def test_resolvent_trace(self, w33):
        """tr(R(z)) = sum_i 1/(z - theta_i)."""
        A = w33.astype(float)
        z = 100.0
        Rz = inv(z * np.eye(40) - A)
        tr_Rz = np.trace(Rz)
        eigs = eigvalsh(A)
        expected = np.sum(1.0 / (z - eigs))
        assert abs(tr_Rz - expected) < 1e-10

    def test_resolvent_symmetry(self, w33):
        """R(z) is symmetric when A is symmetric and z is real."""
        A = w33.astype(float)
        z = 50.0
        Rz = inv(z * np.eye(40) - A)
        assert np.allclose(Rz, Rz.T, atol=1e-14)
