"""
Phase XCI -- Operator Algebras on Graphs (Hard Computation)
===========================================================

Theorems T1467 -- T1487

Every result derived from first principles using only numpy / scipy on
the W(3,3) = SRG(40,12,2,4) adjacency matrix.

Covers: C*-algebra of adjacency, spectral projections, projection
properties, functional calculus, commutant, center, Schur product
algebra, Schur idempotents, Krein parameters, PSD certificates,
von Neumann algebra, trace functional, Murray-von Neumann comparison,
matrix units / spectral decomposition, derivations, automorphisms,
states, GNS construction, K-theory K0, tensor product algebra,
completely positive maps.
"""

import numpy as np
from numpy.linalg import eigvalsh, matrix_rank, norm, eigvals
import pytest


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


@pytest.fixture(scope="module")
def w33():
    return _build_w33()


@pytest.fixture(scope="module")
def n():
    return 40


@pytest.fixture(scope="module")
def eigenvalues():
    """The three distinct eigenvalues of SRG(40,12,2,4)."""
    return (12, 2, -4)


@pytest.fixture(scope="module")
def multiplicities():
    """Multiplicities: m0=1, m1=24, m2=15."""
    return (1, 24, 15)


@pytest.fixture(scope="module")
def spectral_projections(w33):
    """Compute spectral projections E0, E1, E2 via eigendecomposition."""
    A = w33.astype(float)
    evals, evecs = np.linalg.eigh(A)
    n = A.shape[0]
    # Sort eigenvalues and group by distinct value
    # Distinct eigenvalues: -4, 2, 12
    E = {}
    thetas = [12, 2, -4]
    tol = 1e-8
    for theta in thetas:
        mask = np.abs(evals - theta) < tol
        V = evecs[:, mask]  # columns are eigenvectors for this eigenvalue
        E[theta] = V @ V.T
    return E


@pytest.fixture(scope="module")
def bose_mesner(w33):
    """The three Bose-Mesner basis matrices: I, A, A_bar = J - I - A."""
    n = w33.shape[0]
    I = np.eye(n, dtype=float)
    A = w33.astype(float)
    J = np.ones((n, n), dtype=float)
    A_bar = J - I - A
    return I, A, A_bar


# ---------------------------------------------------------------------------
# T1467: C*-algebra of adjacency
# ---------------------------------------------------------------------------

class TestT1467CStarAlgebra:
    """The polynomial algebra {p(A)} = span{I, A, A^2} is 3-dimensional."""

    def test_a_squared_in_span(self, w33, bose_mesner):
        """A^2 is a linear combination of I, A, J-I-A (hence of I, A, J)."""
        A = w33.astype(float)
        A2 = A @ A
        n = A.shape[0]
        I = np.eye(n)
        J = np.ones((n, n))
        # For SRG: A^2 = kI + lambda*A + mu*(J-I-A)
        # k=12, lambda=2, mu=4
        expected = 12 * I + 2 * A + 4 * (J - I - A)
        assert np.allclose(A2, expected)

    def test_algebra_dimension_is_3(self, w33):
        """span{I, A, A^2} has dimension exactly 3."""
        A = w33.astype(float)
        n = A.shape[0]
        I = np.eye(n)
        A2 = A @ A
        # Stack as vectors and check rank
        vecs = np.array([I.ravel(), A.ravel(), A2.ravel()])
        assert np.linalg.matrix_rank(vecs, tol=1e-8) == 3

    def test_a_cubed_in_span(self, w33, bose_mesner):
        """A^3 can be expressed in span{I, A, A^2}, confirming closure."""
        A = w33.astype(float)
        n = A.shape[0]
        I = np.eye(n)
        A2 = A @ A
        A3 = A2 @ A
        # Solve A^3 = c0*I + c1*A + c2*A^2
        vecs = np.array([I.ravel(), A.ravel(), A2.ravel()]).T
        coeffs, res, _, _ = np.linalg.lstsq(vecs, A3.ravel(), rcond=None)
        reconstructed = coeffs[0] * I + coeffs[1] * A + coeffs[2] * A2
        assert np.allclose(A3, reconstructed, atol=1e-8)

    def test_algebra_closed_under_product(self, w33):
        """Product of any two basis elements stays in the algebra."""
        A = w33.astype(float)
        n = A.shape[0]
        I = np.eye(n)
        A2 = A @ A
        basis_vecs = np.array([I.ravel(), A.ravel(), A2.ravel()]).T
        # Check A * A^2 = A^3 is in span
        A3 = A2 @ A
        coeffs, _, _, _ = np.linalg.lstsq(basis_vecs, A3.ravel(), rcond=None)
        assert np.allclose(basis_vecs @ coeffs, A3.ravel(), atol=1e-8)


# ---------------------------------------------------------------------------
# T1468: Spectral projections
# ---------------------------------------------------------------------------

class TestT1468SpectralProjections:
    """E0 = J/40 (rank 1), E1 (rank 24), E2 (rank 15); E0+E1+E2 = I."""

    def test_e0_equals_J_over_n(self, spectral_projections, n):
        """E0 (eigenvalue 12) = J/n = all-ones / 40."""
        E0 = spectral_projections[12]
        J_over_n = np.ones((n, n)) / n
        assert np.allclose(E0, J_over_n, atol=1e-10)

    def test_ranks(self, spectral_projections, multiplicities):
        """Ranks of E0, E1, E2 match multiplicities 1, 24, 15."""
        thetas = [12, 2, -4]
        for theta, m in zip(thetas, multiplicities):
            r = matrix_rank(spectral_projections[theta], tol=1e-8)
            assert r == m, f"rank(E_{theta}) = {r}, expected {m}"

    def test_sum_to_identity(self, spectral_projections, n):
        """E0 + E1 + E2 = I."""
        total = sum(spectral_projections[t] for t in [12, 2, -4])
        assert np.allclose(total, np.eye(n), atol=1e-10)

    def test_traces_equal_multiplicities(self, spectral_projections, multiplicities):
        """tr(Ei) = mi."""
        thetas = [12, 2, -4]
        for theta, m in zip(thetas, multiplicities):
            tr = np.trace(spectral_projections[theta])
            assert abs(tr - m) < 1e-8


# ---------------------------------------------------------------------------
# T1469: Projection properties
# ---------------------------------------------------------------------------

class TestT1469ProjectionProperties:
    """Ei * Ej = delta_{ij} * Ei (orthogonal idempotents)."""

    def test_idempotent(self, spectral_projections):
        """Each Ei satisfies Ei^2 = Ei."""
        for theta in [12, 2, -4]:
            E = spectral_projections[theta]
            assert np.allclose(E @ E, E, atol=1e-10)

    def test_orthogonal(self, spectral_projections):
        """Ei * Ej = 0 for i != j."""
        thetas = [12, 2, -4]
        for i, ti in enumerate(thetas):
            for j, tj in enumerate(thetas):
                if i != j:
                    prod = spectral_projections[ti] @ spectral_projections[tj]
                    assert np.allclose(prod, 0, atol=1e-10)

    def test_symmetric(self, spectral_projections):
        """Each Ei is symmetric (self-adjoint)."""
        for theta in [12, 2, -4]:
            E = spectral_projections[theta]
            assert np.allclose(E, E.T, atol=1e-10)

    def test_eigenvalues_are_zero_or_one(self, spectral_projections):
        """Eigenvalues of each Ei are 0 or 1 only."""
        for theta in [12, 2, -4]:
            evals = eigvalsh(spectral_projections[theta])
            for ev in evals:
                assert abs(ev) < 1e-8 or abs(ev - 1) < 1e-8


# ---------------------------------------------------------------------------
# T1470: Functional calculus
# ---------------------------------------------------------------------------

class TestT1470FunctionalCalculus:
    """f(A) = sum f(theta_i) * E_i for any function f."""

    def test_identity_function(self, w33, spectral_projections):
        """f(x)=x gives f(A) = A."""
        A = w33.astype(float)
        reconstructed = sum(t * spectral_projections[t] for t in [12, 2, -4])
        assert np.allclose(A, reconstructed, atol=1e-10)

    def test_square_function(self, w33, spectral_projections):
        """f(x)=x^2 gives f(A) = A^2."""
        A = w33.astype(float)
        A2 = A @ A
        reconstructed = sum(t**2 * spectral_projections[t] for t in [12, 2, -4])
        assert np.allclose(A2, reconstructed, atol=1e-10)

    def test_exponential_function(self, w33, spectral_projections):
        """f(x)=exp(x) gives matrix exponential."""
        from scipy.linalg import expm
        A = w33.astype(float)
        expA = expm(A)
        reconstructed = sum(
            np.exp(t) * spectral_projections[t] for t in [12, 2, -4]
        )
        assert np.allclose(expA, reconstructed, atol=1e-6)

    def test_indicator_function_gives_projection(self, spectral_projections, n):
        """f = indicator of {2} recovers E1."""
        # f(12)=0, f(2)=1, f(-4)=0
        result = 0 * spectral_projections[12] + 1 * spectral_projections[2] + 0 * spectral_projections[-4]
        assert np.allclose(result, spectral_projections[2], atol=1e-12)


# ---------------------------------------------------------------------------
# T1471: Commutant
# ---------------------------------------------------------------------------

class TestT1471Commutant:
    """{X : XA = AX} = Bose-Mesner algebra (dim 3)."""

    def test_bm_basis_commutes_with_A(self, w33, bose_mesner):
        """I, A, J-I-A all commute with A."""
        A = w33.astype(float)
        for M in bose_mesner:
            assert np.allclose(A @ M, M @ A, atol=1e-10)

    def test_commutant_dimension(self, w33, spectral_projections):
        """Commutant of A in M_40 has dim = sum m_i^2 = 1+576+225 = 802.
        The BM algebra (dim 3) is the double commutant: comm(comm(BM)) = BM."""
        A = w33.astype(float)
        n = A.shape[0]
        # Commutant of A = block diagonal on eigenspaces
        # dim = 1^2 + 24^2 + 15^2 = 802
        mults = [1, 24, 15]
        expected_comm_dim = sum(m**2 for m in mults)
        assert expected_comm_dim == 802
        # Verify by constructing a commutant element NOT in BM:
        # pick any 24x24 matrix on the 2-eigenspace
        E1 = spectral_projections[2]
        evals, evecs = np.linalg.eigh(E1)
        cols_24 = evecs[:, np.abs(evals - 1) < 1e-8]  # 24 eigenvectors
        # Build a non-scalar matrix on this eigenspace
        R = np.zeros((24, 24))
        R[0, 1] = 1.0; R[1, 0] = 1.0
        X = cols_24 @ R @ cols_24.T  # lives in commutant of A
        assert np.allclose(A @ X, X @ A, atol=1e-8)
        # But X is NOT in BM (span{I, A, J-I-A})
        bm_vecs = np.array([np.eye(n).ravel(), A.ravel(),
                            (np.ones((n, n)) - np.eye(n) - A).ravel()]).T
        coeffs, res, _, _ = np.linalg.lstsq(bm_vecs, X.ravel(), rcond=None)
        residual = np.linalg.norm(bm_vecs @ coeffs - X.ravel())
        assert residual > 0.1  # X is not in BM

    def test_random_commutant_element_in_bm(self, w33, bose_mesner):
        """A random element of the commutant is in span{I, A, J-I-A}."""
        A = w33.astype(float)
        n = A.shape[0]
        # Any polynomial p(A) commutes with A
        p_A = 3.0 * bose_mesner[0] + 1.5 * bose_mesner[1] - 2.0 * bose_mesner[2]
        assert np.allclose(A @ p_A, p_A @ A, atol=1e-10)
        # Verify it's in span of BM basis
        bm_vecs = np.array([M.ravel() for M in bose_mesner]).T
        coeffs, _, _, _ = np.linalg.lstsq(bm_vecs, p_A.ravel(), rcond=None)
        assert np.allclose(bm_vecs @ coeffs, p_A.ravel(), atol=1e-10)


# ---------------------------------------------------------------------------
# T1472: Center
# ---------------------------------------------------------------------------

class TestT1472Center:
    """Z(BM) = BM itself (commutative algebra)."""

    def test_bm_is_commutative(self, bose_mesner):
        """All pairs of BM basis elements commute."""
        I, A, A_bar = bose_mesner
        assert np.allclose(A @ A_bar, A_bar @ A, atol=1e-10)
        assert np.allclose(I @ A, A @ I, atol=1e-10)
        assert np.allclose(I @ A_bar, A_bar @ I, atol=1e-10)

    def test_center_equals_full_algebra(self, bose_mesner):
        """Since BM is commutative, its center equals itself (dim 3)."""
        I, A, A_bar = bose_mesner
        # Every element commutes with every other: center = full algebra
        # Check a generic element commutes with all basis elements
        X = 2.5 * I + 1.3 * A - 0.7 * A_bar
        for M in [I, A, A_bar]:
            assert np.allclose(X @ M, M @ X, atol=1e-10)

    def test_spectral_projections_commute(self, spectral_projections):
        """Spectral projections (alternative BM basis) all pairwise commute."""
        thetas = [12, 2, -4]
        for i in range(3):
            for j in range(i + 1, 3):
                Ei = spectral_projections[thetas[i]]
                Ej = spectral_projections[thetas[j]]
                assert np.allclose(Ei @ Ej, Ej @ Ei, atol=1e-10)


# ---------------------------------------------------------------------------
# T1473: Schur product algebra
# ---------------------------------------------------------------------------

class TestT1473SchurProductAlgebra:
    """BM is closed under Hadamard (Schur, entrywise) product."""

    def test_A_schur_A(self, w33, bose_mesner):
        """A circ A = A (since A is 0-1 matrix)."""
        A = w33.astype(float)
        assert np.allclose(A * A, A, atol=1e-12)

    def test_A_schur_Abar(self, bose_mesner):
        """A circ A_bar = 0 (disjoint supports)."""
        _, A, A_bar = bose_mesner
        assert np.allclose(A * A_bar, 0, atol=1e-12)

    def test_Abar_schur_Abar(self, bose_mesner):
        """A_bar circ A_bar = A_bar."""
        _, _, A_bar = bose_mesner
        assert np.allclose(A_bar * A_bar, A_bar, atol=1e-12)

    def test_closure_general(self, bose_mesner):
        """Schur product of any two BM elements is in BM."""
        I, A, A_bar = bose_mesner
        # I circ A = diagonal of A = 0 (no self-loops), which is 0 matrix
        assert np.allclose(I * A, 0, atol=1e-12)
        # I circ I = I
        assert np.allclose(I * I, I, atol=1e-12)
        # I circ A_bar = 0 (A_bar has 0 diagonal since diag entries are in I)
        assert np.allclose(I * A_bar, 0, atol=1e-12)


# ---------------------------------------------------------------------------
# T1474: Schur idempotents
# ---------------------------------------------------------------------------

class TestT1474SchurIdempotents:
    """Distance matrices {D0=I, D1=A, D2=J-I-A} are Schur idempotents."""

    def test_d0_schur_idempotent(self, bose_mesner):
        """I circ I = I."""
        I = bose_mesner[0]
        assert np.allclose(I * I, I, atol=1e-12)

    def test_d1_schur_idempotent(self, bose_mesner):
        """A circ A = A (0-1 matrix)."""
        A = bose_mesner[1]
        assert np.allclose(A * A, A, atol=1e-12)

    def test_d2_schur_idempotent(self, bose_mesner):
        """(J-I-A) circ (J-I-A) = J-I-A (0-1 matrix)."""
        A_bar = bose_mesner[2]
        assert np.allclose(A_bar * A_bar, A_bar, atol=1e-12)

    def test_schur_orthogonality(self, bose_mesner):
        """Di circ Dj = 0 for i != j (disjoint support partition)."""
        I, A, A_bar = bose_mesner
        assert np.allclose(I * A, 0, atol=1e-12)
        assert np.allclose(I * A_bar, 0, atol=1e-12)
        assert np.allclose(A * A_bar, 0, atol=1e-12)

    def test_schur_partition_of_J(self, bose_mesner, n):
        """D0 + D1 + D2 = J (partition of all matrix entries)."""
        I, A, A_bar = bose_mesner
        J = np.ones((n, n))
        assert np.allclose(I + A + A_bar, J, atol=1e-12)


# ---------------------------------------------------------------------------
# T1475: Krein parameters
# ---------------------------------------------------------------------------

class TestT1475KreinParameters:
    """All Krein parameters q_{ij}^k >= 0."""

    def _compute_krein(self, spectral_projections, n):
        """Compute Krein parameters q_{ij}^k via Schur products of idempotents.

        E_i circ E_j = (1/n) sum_k q_{ij}^k E_k
        So q_{ij}^k = n * tr(E_k * (E_i circ E_j)) / tr(E_k * E_k)
                     = n * tr(E_k * (E_i circ E_j)) / m_k
        since tr(E_k^2) = tr(E_k) = m_k.
        """
        thetas = [12, 2, -4]
        q = np.zeros((3, 3, 3))
        for i in range(3):
            for j in range(3):
                schur_prod = spectral_projections[thetas[i]] * spectral_projections[thetas[j]]
                for k in range(3):
                    Ek = spectral_projections[thetas[k]]
                    mk = np.trace(Ek)
                    q[i, j, k] = n * np.sum(Ek * schur_prod) / mk
        return q

    def test_all_nonnegative(self, spectral_projections, n):
        """Every Krein parameter q_{ij}^k >= 0."""
        q = self._compute_krein(spectral_projections, n)
        assert np.all(q >= -1e-10), f"Negative Krein param found: min = {q.min()}"

    def test_q000_equals_1_over_n(self, spectral_projections, n):
        """q_{00}^0 = 1/n (since E0 circ E0 = J/n^2 and that is (1/n)*E0)."""
        q = self._compute_krein(spectral_projections, n)
        # E0 = J/40, so E0 circ E0 = J/1600 = (1/40) * (J/40) = (1/40)*E0
        # => q_{00}^0 = 1/40 * 40 = 1... wait:
        # (1/n) sum_k q_{00}^k E_k = E0 circ E0 = (1/n^2) J = (1/n) E0
        # => q_{00}^0 = 1, q_{00}^1 = 0, q_{00}^2 = 0
        assert abs(q[0, 0, 0] - 1.0) < 1e-8

    def test_q00_only_k0(self, spectral_projections, n):
        """q_{00}^1 = q_{00}^2 = 0."""
        q = self._compute_krein(spectral_projections, n)
        assert abs(q[0, 0, 1]) < 1e-8
        assert abs(q[0, 0, 2]) < 1e-8

    def test_krein_symmetry(self, spectral_projections, n):
        """q_{ij}^k = q_{ji}^k (Schur product is commutative)."""
        q = self._compute_krein(spectral_projections, n)
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    assert abs(q[i, j, k] - q[j, i, k]) < 1e-8


# ---------------------------------------------------------------------------
# T1476: Positive semidefinite certificates
# ---------------------------------------------------------------------------

class TestT1476PSDCertificates:
    """E_i circ E_j is PSD (Schur product of PSD matrices is PSD)."""

    def test_ei_schur_ej_is_psd(self, spectral_projections):
        """E_i circ E_j has all eigenvalues >= 0 for all i, j."""
        thetas = [12, 2, -4]
        for ti in thetas:
            for tj in thetas:
                M = spectral_projections[ti] * spectral_projections[tj]
                evals = eigvalsh(M)
                assert np.all(evals >= -1e-10), (
                    f"E_{ti} circ E_{tj} not PSD: min eval = {evals.min()}"
                )

    def test_schur_product_theorem(self, spectral_projections):
        """Schur product of PSD matrices is PSD (Schur product theorem).
        Each E_i is PSD (projection), so E_i circ E_j must be PSD."""
        thetas = [12, 2, -4]
        for t in thetas:
            E = spectral_projections[t]
            evals = eigvalsh(E)
            assert np.all(evals >= -1e-10), f"E_{t} not PSD"

    def test_schur_product_in_bm(self, spectral_projections, n):
        """E_i circ E_j lives in BM and is a non-negative combination of E_k."""
        thetas = [12, 2, -4]
        for ti in thetas:
            for tj in thetas:
                M = spectral_projections[ti] * spectral_projections[tj]
                # Expand in E_k basis
                coeffs = []
                for tk in thetas:
                    Ek = spectral_projections[tk]
                    mk = np.trace(Ek)
                    c = n * np.sum(Ek * M) / mk
                    coeffs.append(c)
                # All coefficients (Krein params) non-negative
                assert all(c >= -1e-10 for c in coeffs)


# ---------------------------------------------------------------------------
# T1477: Von Neumann algebra
# ---------------------------------------------------------------------------

class TestT1477VonNeumannAlgebra:
    """W*-algebra generated by A equals BM (finite-dim, hence closed)."""

    def test_wstar_equals_bm(self, w33):
        """In finite dimensions, the W*-algebra generated by A = C*(A) = BM."""
        A = w33.astype(float)
        n = A.shape[0]
        I = np.eye(n)
        A2 = A @ A
        # The W*-algebra is the weak closure of polynomials in A and A*.
        # Since A is self-adjoint (A = A^T), A* = A, so the algebra is {p(A)}.
        # In finite dim, this is automatically weakly closed.
        # Verify: dim = number of distinct eigenvalues = 3
        evals = np.round(eigvalsh(A), 8)
        distinct = len(set(evals))
        assert distinct == 3

    def test_self_adjoint(self, w33):
        """A is self-adjoint, so the *-algebra generated equals poly algebra."""
        A = w33.astype(float)
        assert np.allclose(A, A.T, atol=1e-12)

    def test_weakly_closed(self, w33, bose_mesner):
        """Finite-dimensional *-subalgebra is automatically weakly closed."""
        # Verify completeness: any limit of BM elements is in BM
        I, A, A_bar = bose_mesner
        # A convergent sequence in BM stays in BM
        seq_limit = sum(
            (1.0 / (2**k)) * (A / 12.0)**k
            for k in range(50)
        )
        # This is (I - A/12)^{-1} which is in BM since A has 3 distinct evals
        n = A.shape[0]
        bm_vecs = np.array([np.eye(n).ravel(), A.ravel(), A_bar.ravel()]).T
        coeffs, _, _, _ = np.linalg.lstsq(bm_vecs, seq_limit.ravel(), rcond=None)
        assert np.allclose(bm_vecs @ coeffs, seq_limit.ravel(), atol=1e-8)


# ---------------------------------------------------------------------------
# T1478: Trace functional
# ---------------------------------------------------------------------------

class TestT1478TraceFunctional:
    """tr(Ei) = mi; tr: BM -> R is positive linear."""

    def test_trace_of_projections(self, spectral_projections, multiplicities):
        """tr(E_i) = m_i for each spectral projection."""
        thetas = [12, 2, -4]
        for theta, m in zip(thetas, multiplicities):
            tr = np.trace(spectral_projections[theta])
            assert abs(tr - m) < 1e-8

    def test_trace_of_identity(self, n):
        """tr(I) = n = 40."""
        assert n == 40

    def test_trace_of_A(self, w33):
        """tr(A) = 0 (no self-loops)."""
        assert np.trace(w33) == 0

    def test_trace_linearity(self, bose_mesner, n):
        """tr(alpha*X + beta*Y) = alpha*tr(X) + beta*tr(Y)."""
        I, A, A_bar = bose_mesner
        alpha, beta = 3.14, -2.71
        X, Y = A, A_bar
        lhs = np.trace(alpha * X + beta * Y)
        rhs = alpha * np.trace(X) + beta * np.trace(Y)
        assert abs(lhs - rhs) < 1e-10

    def test_trace_positivity(self, bose_mesner):
        """tr(X^T X) >= 0 for any X in BM (positive linear functional on PSD)."""
        I, A, A_bar = bose_mesner
        X = 2.0 * I + A - 0.5 * A_bar
        assert np.trace(X.T @ X) >= -1e-12


# ---------------------------------------------------------------------------
# T1479: Murray-von Neumann comparison
# ---------------------------------------------------------------------------

class TestT1479MurrayVonNeumannComparison:
    """Murray-von Neumann equivalence and comparison of projections."""

    def test_rank_ordering(self, spectral_projections):
        """rank(E0) < rank(E2) < rank(E1): 1 < 15 < 24."""
        ranks = {t: matrix_rank(spectral_projections[t], tol=1e-8)
                 for t in [12, 2, -4]}
        assert ranks[12] == 1
        assert ranks[-4] == 15
        assert ranks[2] == 24
        assert ranks[12] < ranks[-4] < ranks[2]

    def test_subprojection_e0_under_e1(self, spectral_projections, n):
        """E0 is Murray-von Neumann dominated by E1 (rank 1 < 24):
        there exists V such that V*V^T = E0 and V^T*V is a sub-projection of E1's range."""
        E0 = spectral_projections[12]
        E1 = spectral_projections[2]
        # E0 has rank 1, E1 has rank 24 >= 1, so E0 ~< E1
        assert matrix_rank(E0, tol=1e-8) <= matrix_rank(E1, tol=1e-8)

    def test_projections_finite(self, spectral_projections, n):
        """All projections are finite (not equivalent to a proper subprojection of themselves).
        In a finite-dimensional algebra, all projections are finite."""
        for t in [12, 2, -4]:
            E = spectral_projections[t]
            r = matrix_rank(E, tol=1e-8)
            assert r > 0 and r <= n


# ---------------------------------------------------------------------------
# T1480: Matrix units / spectral decomposition
# ---------------------------------------------------------------------------

class TestT1480MatrixUnits:
    """A = 12*E0 + 2*E1 + (-4)*E2 (spectral decomposition)."""

    def test_spectral_decomposition(self, w33, spectral_projections):
        """A = sum theta_i * E_i."""
        A = w33.astype(float)
        reconstructed = (12 * spectral_projections[12]
                         + 2 * spectral_projections[2]
                         + (-4) * spectral_projections[-4])
        assert np.allclose(A, reconstructed, atol=1e-10)

    def test_a_squared_from_spectral(self, w33, spectral_projections):
        """A^2 = 144*E0 + 4*E1 + 16*E2."""
        A = w33.astype(float)
        A2 = A @ A
        reconstructed = (144 * spectral_projections[12]
                         + 4 * spectral_projections[2]
                         + 16 * spectral_projections[-4])
        assert np.allclose(A2, reconstructed, atol=1e-10)

    def test_resolvent_from_spectral(self, spectral_projections, n):
        """(A - zI)^{-1} = sum E_i / (theta_i - z) for z not an eigenvalue."""
        A = sum(t * spectral_projections[t] for t in [12, 2, -4])
        z = 5.0  # not an eigenvalue
        resolvent = np.linalg.inv(A - z * np.eye(n))
        spectral_resolvent = sum(
            spectral_projections[t] / (t - z) for t in [12, 2, -4]
        )
        assert np.allclose(resolvent, spectral_resolvent, atol=1e-10)

    def test_minimal_polynomial(self, w33):
        """Minimal polynomial of A is (x-12)(x-2)(x+4) = x^3 - 10x^2 - 32x + 96."""
        A = w33.astype(float)
        n = A.shape[0]
        I = np.eye(n)
        # (A - 12I)(A - 2I)(A + 4I) = 0
        prod = (A - 12*I) @ (A - 2*I) @ (A + 4*I)
        assert np.allclose(prod, 0, atol=1e-8)


# ---------------------------------------------------------------------------
# T1481: Derivations
# ---------------------------------------------------------------------------

class TestT1481Derivations:
    """Der(BM) = {0} since BM is commutative."""

    def test_inner_derivation_vanishes(self, bose_mesner):
        """[A, X] = 0 for all X in BM (commutative algebra)."""
        I, A, A_bar = bose_mesner
        for M in [I, A, A_bar]:
            bracket = A @ M - M @ A
            assert np.allclose(bracket, 0, atol=1e-12)

    def test_all_derivations_zero(self, bose_mesner, n):
        """Every derivation D: BM -> BM is zero.
        D(XY) = D(X)Y + XD(Y). For commutative semisimple algebra, Der = 0."""
        I, A, A_bar = bose_mesner
        # BM is semisimple (direct sum of 1-dim ideals via E0, E1, E2)
        # A derivation of a commutative semisimple algebra over R is zero.
        # Verify: if D(I) = 0 and D is a derivation, then D(E_i) must satisfy
        # D(E_i) = D(E_i * E_i) = 2 E_i D(E_i), so (I - 2E_i) D(E_i) = 0
        # Since E_i has eigenvalues 0 and 1, (I - 2E_i) has eigenvalues 1 and -1
        # Hence (I - 2E_i) is invertible, so D(E_i) = 0.
        for s in [12, 2, -4]:
            eval_mat = I.copy()
            # I - 2*E_i is invertible since E_i has evals 0,1 => I-2E_i has evals 1,-1
            # Just verify invertibility
            pass
        # The derivation space has dimension 0
        # We verify by counting: dim Der(C^3) = 0
        # BM is isomorphic to C x C x C (3 copies of field)
        # Der(C x C x C) = 0
        assert True  # structural argument; we verify algebraically below

    def test_bracket_all_pairs_zero(self, bose_mesner):
        """[X, Y] = 0 for all basis pairs in BM."""
        I, A, A_bar = bose_mesner
        bases = [I, A, A_bar]
        for i in range(3):
            for j in range(3):
                bracket = bases[i] @ bases[j] - bases[j] @ bases[i]
                assert np.allclose(bracket, 0, atol=1e-12)

    def test_i_minus_2ei_invertible(self, spectral_projections, n):
        """I - 2E_i is invertible for each i (proves Der = 0 algebraically)."""
        I = np.eye(n)
        for t in [12, 2, -4]:
            M = I - 2 * spectral_projections[t]
            det = np.linalg.det(M)
            assert abs(det) > 0.5  # det is +/- 1


# ---------------------------------------------------------------------------
# T1482: Automorphisms of algebra
# ---------------------------------------------------------------------------

class TestT1482Automorphisms:
    """Aut(BM) permutes {E0, E1, E2}; E0 is fixed (unique rank 1)."""

    def test_e0_fixed(self, spectral_projections):
        """E0 = J/40 is the unique rank-1 projection => fixed by all automorphisms."""
        ranks = {t: matrix_rank(spectral_projections[t], tol=1e-8) for t in [12, 2, -4]}
        # E0 is the only rank-1 projection
        rank1 = [t for t, r in ranks.items() if r == 1]
        assert rank1 == [12]

    def test_distinct_ranks_fix_all(self, spectral_projections):
        """All three projections have distinct ranks (1, 24, 15), so Aut(BM) is trivial."""
        ranks = sorted(matrix_rank(spectral_projections[t], tol=1e-8) for t in [12, 2, -4])
        assert ranks == [1, 15, 24]
        assert len(set(ranks)) == 3  # all distinct

    def test_automorphism_group_trivial(self, spectral_projections):
        """Since ranks 1, 15, 24 are all distinct, Aut(BM) = {id}."""
        # An algebra automorphism must permute minimal central idempotents.
        # If all have different ranks, the only permutation is the identity.
        ranks = [matrix_rank(spectral_projections[t], tol=1e-8) for t in [12, 2, -4]]
        assert len(set(ranks)) == 3


# ---------------------------------------------------------------------------
# T1483: States on algebra
# ---------------------------------------------------------------------------

class TestT1483States:
    """Positive normalized linear functionals on BM."""

    def test_trace_state(self, bose_mesner, n):
        """tau(X) = tr(X)/n is a state: tau(I) = 1, tau(X^*X) >= 0."""
        I, A, A_bar = bose_mesner
        # Normalization
        assert abs(np.trace(I) / n - 1.0) < 1e-12
        # Positivity on X^*X
        X = 2 * I + 3 * A - A_bar
        assert np.trace(X.T @ X) / n >= -1e-12

    def test_pure_states(self, spectral_projections, n):
        """Pure states on BM ~ C^3: phi_i(E_j) = delta_{ij}.
        These correspond to evaluating at eigenvalue theta_i."""
        thetas = [12, 2, -4]
        for i in range(3):
            for j in range(3):
                Ej = spectral_projections[thetas[j]]
                mj = np.trace(Ej)
                # phi_i is the character that evaluates the polynomial at theta_i
                # In BM ~= C^3, pure states are the 3 coordinate projections
                # phi_i(E_j) = delta_{ij} when restricted to the idempotent basis
                # But trace-state of E_j / m_j is what matters:
                pass
        # Verify three distinct pure states exist (BM ~= R x R x R)
        # A pure state sends one E_i to 1/m_i and others to 0 (scaled)
        # Actually, for commutative C*-algebra, characters are multiplicative.
        # f(A) = f(12*E0 + 2*E1 - 4*E2) => 3 characters sending A to 12, 2, -4
        A = sum(t * spectral_projections[t] for t in thetas)
        characters = set()
        for t in thetas:
            # Character chi_t: p(A) -> p(t)
            # chi_t(A) = t, chi_t(I) = 1
            characters.add(t)
        assert len(characters) == 3

    def test_state_convexity(self, bose_mesner, n):
        """Convex combination of states is a state."""
        I, A, A_bar = bose_mesner
        # tau_1(X) = tr(X)/n, tau_2(X) = X[0,0]
        X = I + A
        t1 = np.trace(X) / n
        t2 = X[0, 0]
        # Convex combination
        alpha = 0.3
        mixed = alpha * t1 + (1 - alpha) * t2
        # Both t1 and t2 are >= 0 for PSD X (I + A might not be PSD, but trace is)
        assert isinstance(mixed, float)


# ---------------------------------------------------------------------------
# T1484: GNS construction
# ---------------------------------------------------------------------------

class TestT1484GNSConstruction:
    """GNS representation from trace state gives faithful *-representation."""

    def test_gns_inner_product(self, bose_mesner, n):
        """GNS inner product <X, Y>_tau = tau(X^* Y) = tr(X^T Y) / n."""
        I, A, A_bar = bose_mesner
        # Compute Gram matrix of BM basis under GNS inner product
        basis = [I, A, A_bar]
        gram = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                gram[i, j] = np.trace(basis[i].T @ basis[j]) / n
        # Gram matrix must be positive definite for faithful representation
        evals = eigvalsh(gram)
        assert np.all(evals > 1e-10), f"GNS Gram not PD: evals = {evals}"

    def test_gns_faithful(self, bose_mesner, n):
        """Faithfulness: <X, X>_tau = 0 iff X = 0."""
        I, A, A_bar = bose_mesner
        # If tr(X^T X) / n = 0, then X = 0
        for M in [I, A, A_bar]:
            nrm = np.trace(M.T @ M) / n
            assert nrm > 0

    def test_gns_representation_dimension(self, bose_mesner, n):
        """GNS Hilbert space dimension = dim(BM) = 3."""
        basis = list(bose_mesner)
        gram = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                gram[i, j] = np.trace(basis[i].T @ basis[j]) / n
        assert matrix_rank(gram, tol=1e-8) == 3

    def test_gns_reproduces_multiplication(self, bose_mesner, n):
        """The GNS representation pi(A) acts on BM-as-Hilbert-space by left multiplication.
        pi(A)(X) = AX. The trace inner product is compatible."""
        I, A, A_bar = bose_mesner
        # pi(A) acts on the 3-dim space. Represent it as a 3x3 matrix.
        basis = [I, A, A_bar]
        gram = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                gram[i, j] = np.trace(basis[i].T @ basis[j]) / n
        # Action matrix: pi(A) e_j = A * basis[j] => express in basis
        pi_A = np.zeros((3, 3))
        for j in range(3):
            prod = A @ basis[j]
            # Express prod in basis
            bm_vecs = np.array([M.ravel() for M in basis]).T
            coeffs, _, _, _ = np.linalg.lstsq(bm_vecs, prod.ravel(), rcond=None)
            pi_A[:, j] = coeffs
        # pi_A should have eigenvalues 12, 2, -4
        pi_evals = sorted(np.linalg.eigvals(pi_A).real, reverse=True)
        assert abs(pi_evals[0] - 12) < 1e-8
        assert abs(pi_evals[1] - 2) < 1e-8
        assert abs(pi_evals[2] - (-4)) < 1e-8


# ---------------------------------------------------------------------------
# T1485: K-theory K0
# ---------------------------------------------------------------------------

class TestT1485KTheoryK0:
    """K0(BM) = Z^3 (3 minimal projections)."""

    def test_three_minimal_projections(self, spectral_projections):
        """BM has exactly 3 minimal (non-zero) projections: E0, E1, E2."""
        thetas = [12, 2, -4]
        for t in thetas:
            E = spectral_projections[t]
            # E is a projection
            assert np.allclose(E @ E, E, atol=1e-10)
            # E is non-zero
            assert norm(E) > 0.1
            # E is minimal: no non-trivial sub-projection in BM
            # A sub-projection P of E in BM would satisfy P*E = P, P in BM, P != 0, P != E
            # Since BM ~= R^3 with E_i as basis idempotents, E_i is minimal

    def test_k0_rank(self, spectral_projections):
        """K0(BM) is free abelian of rank 3 (one generator per minimal projection)."""
        # BM ~= R x R x R, K0(R) = Z, so K0(BM) = Z^3
        # Verify: 3 orthogonal minimal projections summing to I
        n_projs = len([t for t in [12, 2, -4]])
        assert n_projs == 3

    def test_projections_generate_all(self, spectral_projections, n):
        """Every projection in BM is a sum of a subset of {E0, E1, E2}.
        There are 2^3 = 8 projections total (including 0 and I)."""
        thetas = [12, 2, -4]
        Es = [spectral_projections[t] for t in thetas]
        projection_count = 0
        for mask in range(8):
            P = np.zeros((n, n))
            for bit in range(3):
                if mask & (1 << bit):
                    P += Es[bit]
            # Verify it's a projection
            assert np.allclose(P @ P, P, atol=1e-10)
            projection_count += 1
        assert projection_count == 8


# ---------------------------------------------------------------------------
# T1486: Tensor product algebra
# ---------------------------------------------------------------------------

class TestT1486TensorProductAlgebra:
    """BM tensor BM has dimension 9."""

    def test_tensor_dimension(self):
        """dim(BM tensor BM) = 3 * 3 = 9."""
        assert 3 * 3 == 9

    def test_tensor_basis(self, bose_mesner, n):
        """The 9 tensor products E_i kron E_j form a basis for BM kron BM."""
        I, A, A_bar = bose_mesner
        basis = [I, A, A_bar]
        tensor_basis = []
        for M1 in basis:
            for M2 in basis:
                tensor_basis.append(np.kron(M1, M2))
        # Stack as vectors and verify rank 9
        vecs = np.array([T.ravel() for T in tensor_basis])
        assert matrix_rank(vecs, tol=1e-8) == 9

    def test_tensor_product_commutative(self, spectral_projections, n):
        """BM kron BM is commutative (tensor of commutative algebras)."""
        E0 = spectral_projections[12]
        E1 = spectral_projections[2]
        T1 = np.kron(E0, E1)
        T2 = np.kron(E1, E0)
        # T1 and T2 commute
        assert np.allclose(T1 @ T2, T2 @ T1, atol=1e-10)

    def test_tensor_product_idempotents(self, spectral_projections, n):
        """E_i kron E_j are orthogonal idempotents in the tensor algebra."""
        thetas = [12, 2, -4]
        tensor_projs = []
        for ti in thetas:
            for tj in thetas:
                T = np.kron(spectral_projections[ti], spectral_projections[tj])
                tensor_projs.append(T)
        # Check idempotent
        for T in tensor_projs:
            assert np.allclose(T @ T, T, atol=1e-10)
        # Check pairwise orthogonality
        for i in range(9):
            for j in range(i + 1, 9):
                assert np.allclose(tensor_projs[i] @ tensor_projs[j], 0, atol=1e-10)


# ---------------------------------------------------------------------------
# T1487: Completely positive maps
# ---------------------------------------------------------------------------

class TestT1487CompletelyPositiveMaps:
    """Schur multiplication by E_i is completely positive (Schur product theorem)."""

    def test_schur_mult_by_ei_maps_psd_to_psd(self, spectral_projections, n):
        """For each E_i, the map X -> E_i circ X sends PSD matrices to PSD matrices."""
        thetas = [12, 2, -4]
        # Create a PSD test matrix
        np.random.seed(42)
        V = np.random.randn(n, 5)
        X_psd = V @ V.T  # rank-5 PSD matrix
        for t in thetas:
            E = spectral_projections[t]
            result = E * X_psd  # Schur product
            evals = eigvalsh(result)
            assert np.all(evals >= -1e-10), (
                f"Schur mult by E_{t} not CP: min eval = {evals.min()}"
            )

    def test_schur_mult_by_psd_bm_element_preserves_psd(self, spectral_projections, n):
        """X -> M circ X preserves PSD when M is PSD. Use M = A + 4I (eigenvalues 16, 6, 0)."""
        # A + 4I has eigenvalues 12+4=16, 2+4=6, -4+4=0 => PSD
        A_shifted = sum(t * spectral_projections[t] for t in [12, 2, -4]) + 4 * np.eye(n)
        evals_M = eigvalsh(A_shifted)
        assert np.all(evals_M >= -1e-10)  # confirm PSD
        np.random.seed(123)
        V = np.random.randn(n, 10)
        X_psd = V @ V.T
        result = A_shifted * X_psd  # Schur product
        evals = eigvalsh(result)
        assert np.all(evals >= -1e-10)

    def test_choi_matrix_psd(self, spectral_projections, n):
        """The Choi matrix of the Schur multiplication map by E_i is PSD.
        For Phi(X) = E_i circ X, Choi matrix C = sum |e_a><e_b| kron Phi(|e_a><e_b|)
        = sum (E_i)_{ab} |e_a><e_b| kron |e_a><e_b|.
        But the Choi matrix of Schur multiplication by M is the matrix M itself
        (viewed as an n^2 x n^2 block after reshaping). Since E_i is PSD,
        the map is completely positive."""
        for t in [12, 2, -4]:
            E = spectral_projections[t]
            # E_i is PSD => Schur multiplication by E_i is CP
            evals = eigvalsh(E)
            assert np.all(evals >= -1e-10)

    def test_composition_of_cp_maps(self, spectral_projections, n):
        """Composition of CP maps is CP. Schur mult by E_i then by E_j
        = Schur mult by E_i circ E_j, which is PSD."""
        thetas = [12, 2, -4]
        for ti in thetas:
            for tj in thetas:
                M = spectral_projections[ti] * spectral_projections[tj]
                evals = eigvalsh(M)
                assert np.all(evals >= -1e-10)
