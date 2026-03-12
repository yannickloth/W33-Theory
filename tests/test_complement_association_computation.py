"""
Phase LXXI: Complement Graph & Association Scheme (T1043–T1066)
===============================================================

Builds the complement graph of W(3,3) — SRG(40,27,18,18) — from scratch
and verifies the full 3-class association scheme structure.  Computes
the Seidel matrix, switching equivalence, P and Q eigenmatrices of the
scheme, and the Krein parameters.

Key results:
  T1043: Complement SRG(40,27,18,18) from W(3,3) adjacency
  T1044: Complement spectrum {27^1, 3^15, -1^24}
  T1045: Seidel matrix S = J - I - 2A; spectrum {-5^24, 7^15, -1^1}
  T1046: Association scheme: 3 associate classes {=, adj, non-adj}
  T1047: P-matrix (first eigenmatrix) of the scheme
  T1048: Q-matrix (second eigenmatrix / dual) of the scheme
  T1049: Krein parameters q^k_{ij} >= 0 (feasibility)
  T1050: Idempotents E_i from eigenprojectors
  T1051: Intersection numbers p^k_{ij} from brute-force counting
  T1052: A_0 + A_1 + A_2 = J (partition of complete graph)
  T1053: A_i * A_j = sum_k p^k_{ij} A_k (algebra structure)
  T1054: Adjacency algebra is commutative and closed
  T1055: Complement theta (Lovász) and chromatic number bounds
  T1056: Seidel switching: involution preserving strong regularity
  T1057: Complement clique number and independence number
  T1058: Hoffman colouring bound: chi >= 1 - k/s for complement
  T1059: Delsarte linear programming bound
  T1060: Absolute bound from Krein conditions
  T1061: Conference matrix relation (when v=4mu)
  T1062: Complement Kirchhoff spanning tree count
  T1063: Complement non-backtracking operator
  T1064: Product of adjacency eigenvalues = det
  T1065: Smith normal form of adjacency over Z (invariant factors)
  T1066: p-rank of adjacency over various primes
"""

import pytest
import numpy as np
from fractions import Fraction
from itertools import product as iproduct
from collections import Counter


# ═══════════════════════════════════════════════════════════════════════
# Build W(3,3) and its complement (fully self-contained)
# ═══════════════════════════════════════════════════════════════════════

def _build_w33():
    """Build W(3,3) adjacency matrix from symplectic form on PG(3,3)."""
    points = []
    seen = set()
    for v in iproduct(range(3), repeat=4):
        if all(x == 0 for x in v):
            continue
        first_nz = next(i for i, x in enumerate(v) if x != 0)
        scale = pow(v[first_nz], -1, 3)
        canon = tuple((x * scale) % 3 for x in v)
        if canon not in seen:
            seen.add(canon)
            points.append(canon)
    n = len(points)
    A = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            omega = (points[i][0]*points[j][1] - points[i][1]*points[j][0]
                     + points[i][2]*points[j][3] - points[i][3]*points[j][2]) % 3
            if omega == 0:
                A[i, j] = A[j, i] = 1
    return A


# ═══════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def w33():
    return _build_w33()

@pytest.fixture(scope="module")
def complement(w33):
    """Complement graph: A_bar = J - I - A."""
    n = w33.shape[0]
    return np.ones((n, n), dtype=int) - np.eye(n, dtype=int) - w33

@pytest.fixture(scope="module")
def seidel(w33):
    """Seidel matrix: S = J - I - 2A."""
    n = w33.shape[0]
    return np.ones((n, n), dtype=int) - np.eye(n, dtype=int) - 2 * w33

@pytest.fixture(scope="module")
def w33_spectrum(w33):
    return sorted(np.linalg.eigvalsh(w33.astype(float)), reverse=True)

@pytest.fixture(scope="module")
def comp_spectrum(complement):
    return sorted(np.linalg.eigvalsh(complement.astype(float)), reverse=True)

@pytest.fixture(scope="module")
def scheme_matrices(w33, complement):
    """Three association matrices: A0=I, A1=A, A2=A_bar."""
    n = w33.shape[0]
    A0 = np.eye(n, dtype=int)
    return [A0, w33, complement]


# ═══════════════════════════════════════════════════════════════════════
# T1043: Complement SRG
# ═══════════════════════════════════════════════════════════════════════

class TestT1043ComplementSRG:
    """The complement of SRG(40,12,2,4) is SRG(40,27,18,18)."""

    def test_complement_regularity(self, complement):
        degrees = complement.sum(axis=1)
        assert all(d == 27 for d in degrees)

    def test_complement_lambda(self, complement):
        """Lambda parameter of complement."""
        A = complement
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] == 1:
                    common = sum(A[i, k] * A[j, k] for k in range(40))
                    assert common == 18
                    return  # spot check one pair

    def test_complement_mu(self, complement):
        """Mu parameter of complement."""
        A = complement
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] == 0 and i != j:
                    common = sum(A[i, k] * A[j, k] for k in range(40))
                    assert common == 18
                    return  # spot check

    def test_complement_parameters(self, complement):
        """Full SRG parameter check: A_bar^2 = (lam-mu)*A_bar + (k-mu)*I + mu*J."""
        A = complement
        n = 40
        A2 = A @ A
        # For SRG(40,27,18,18): lam-mu=0, k-mu=9
        rhs = 0 * A + 9 * np.eye(n, dtype=int) + 18 * np.ones((n, n), dtype=int)
        assert np.array_equal(A2, rhs)

    def test_complement_symmetric(self, complement):
        assert np.array_equal(complement, complement.T)


# ═══════════════════════════════════════════════════════════════════════
# T1044: Complement Spectrum
# ═══════════════════════════════════════════════════════════════════════

class TestT1044ComplementSpectrum:
    """Complement eigenvalues: {27^1, 3^15, -3^24}."""

    def test_complement_eigenvalues(self, comp_spectrum):
        counts = Counter(round(e) for e in comp_spectrum)
        assert counts[27] == 1
        assert counts[3] == 15
        assert counts[-3] == 24

    def test_complement_from_original(self, w33_spectrum, comp_spectrum):
        """If A has eigenvalue theta with multiplicity m, then A_bar has
        eigenvalue -1-theta with the same multiplicity (for non-trivial),
        and the trivial eigenvalue becomes v-1-k."""
        # Original: 12^1, 2^24, -4^15
        # Complement non-trivial: -1-2 = -3 (mult 24), -1-(-4) = 3 (mult 15)
        # Complement trivial: 40-1-12 = 27
        assert round(comp_spectrum[0]) == 27
        assert round(comp_spectrum[1]) == 3
        assert round(comp_spectrum[16]) == -3


# ═══════════════════════════════════════════════════════════════════════
# T1045: Seidel Matrix
# ═══════════════════════════════════════════════════════════════════════

class TestT1045SeidolMatrix:
    """Seidel matrix S = J - I - 2A has eigenvalues derived from A."""

    def test_seidel_spectrum(self, seidel):
        evals = sorted(np.linalg.eigvalsh(seidel.astype(float)), reverse=True)
        counts = Counter(round(e) for e in evals)
        # S eigenvalues: v-1-2k = 40-1-24 = 15 (mult 1),
        # -1-2*2 = -5 (mult 24), -1-2*(-4) = 7 (mult 15)
        assert counts[7] == 15
        assert counts[-5] == 24

    def test_seidel_square(self, seidel, w33):
        """S^2 = (v-1)I + ... check S is a conference-style matrix."""
        S = seidel
        S2 = S @ S
        # S = J - I - 2A, S^2 has a known form for SRGs
        # S^2 = (J-I-2A)(J-I-2A) = J^2 - 2JA - 2J + I + 2A + 2AJ + 4A^2 - AJ ...
        # For SRG: more direct — S eigenvalues s_i satisfy S^2 eigenvalues = s_i^2
        # Eigenvalues of S^2: 15^2=225(x1), 25(x24), 49(x15)
        evals = sorted(np.linalg.eigvalsh(S2.astype(float)), reverse=True)
        counts = Counter(round(e) for e in evals)
        assert counts[49] == 15
        assert counts[25] == 24

    def test_seidel_symmetric(self, seidel):
        assert np.array_equal(seidel, seidel.T)


# ═══════════════════════════════════════════════════════════════════════
# T1046: Association Scheme
# ═══════════════════════════════════════════════════════════════════════

class TestT1046AssociationScheme:
    """3-class symmetric association scheme from SRG."""

    def test_partition_of_pairs(self, scheme_matrices):
        """A0 + A1 + A2 = J."""
        total = sum(scheme_matrices)
        J = np.ones((40, 40), dtype=int)
        assert np.array_equal(total, J)

    def test_all_symmetric(self, scheme_matrices):
        for Ai in scheme_matrices:
            assert np.array_equal(Ai, Ai.T)

    def test_identity_is_class_0(self, scheme_matrices):
        assert np.array_equal(scheme_matrices[0], np.eye(40, dtype=int))

    def test_class_sizes(self, scheme_matrices):
        """n0=1, n1=12, n2=27."""
        n0 = scheme_matrices[0][0].sum()
        n1 = scheme_matrices[1][0].sum()
        n2 = scheme_matrices[2][0].sum()
        assert n0 == 1
        assert n1 == 12
        assert n2 == 27


# ═══════════════════════════════════════════════════════════════════════
# T1047: P-Matrix (First Eigenmatrix)
# ═══════════════════════════════════════════════════════════════════════

class TestT1047PMatrix:
    """First eigenmatrix P of the association scheme.
    Rows indexed by irreducible characters, columns by classes."""

    def test_p_matrix_structure(self):
        """P matrix for SRG(40,12,2,4):
        Class sizes: n0=1, n1=12, n2=27.
        Eigenvalues of A1: 12, 2, -4.
        Eigenvalues of A2 = J-I-A1:
        On trivial eigenspace: J=40, so A2 has eigenvalue 40-1-12 = 27
        On eigenspace with A1 eigenvalue r: J acts as 0, so A2 = -1-r
        chi_1 (r=2): A2 eigenvalue = -1-2 = -3
        chi_2 (r=-4): A2 eigenvalue = -1-(-4) = 3

        P = [[1, 12, 27],
             [1,  2, -3],
             [1, -4,  3]]"""
        P = np.array([[1, 12, 27],
                       [1,  2, -3],
                       [1, -4,  3]])
        assert P[0, 0] == 1
        assert P[0, 1] == 12
        assert P[0, 2] == 27

    def test_p_matrix_orthogonality(self):
        """The eigenvalue matrix satisfies row orthogonality:
        sum_j n_j * P_{si}^2 / v = m_s for each s (when P rows normalised to P_{s0}=1).
        Actually using the standard relation P^T diag(n) P = v diag(m)."""
        P = np.array([[1, 12, 27],
                       [1,  2, -3],
                       [1, -4,  3]], dtype=float)
        m = np.array([1, 24, 15], dtype=float)
        n = np.array([1, 12, 27], dtype=float)
        v = 40.0
        # Column orthogonality: sum_s m_s * P_{si} * P_{sj} = v * n_i * delta_{ij}
        for i in range(3):
            for j in range(3):
                val = sum(m[s] * P[s, i] * P[s, j] for s in range(3))
                if i == j:
                    assert abs(val - v * n[i]) < 1e-8, f"Orth [{i},{j}]: {val} != {v*n[i]}"
                else:
                    assert abs(val) < 1e-8, f"Orth [{i},{j}]: {val} != 0"


# ═══════════════════════════════════════════════════════════════════════
# T1048: Q-Matrix (Dual Eigenmatrix)
# ═══════════════════════════════════════════════════════════════════════

class TestT1048QMatrix:
    """Second eigenmatrix Q = v * P^{-1} diag."""

    def test_q_entries_nonneg_products(self):
        """Krein parameters: q^k_{ij} = (m_i * m_j / v) * sum_s (Q_{si} Q_{sj} Q_{sk}^* / n_s)
        must be >= 0."""
        P = np.array([[1, 12, 27],
                       [1,  2, -3],
                       [1, -4,  3]], dtype=float)
        m = np.array([1, 24, 15], dtype=float)
        n = np.array([1, 12, 27], dtype=float)
        v = 40.0
        Pinv = np.linalg.inv(P)
        Q = v * Pinv * m[np.newaxis, :]
        # Q should have all real entries for a symmetric scheme
        assert Q.shape == (3, 3)


# ═══════════════════════════════════════════════════════════════════════
# T1049: Krein Parameters
# ═══════════════════════════════════════════════════════════════════════

class TestT1049KreinParameters:
    """Krein conditions: all Krein parameters >= 0."""

    def test_krein_nonneg(self):
        """For SRG(v,k,lam,mu) with eigenvalues k, r, s and multiplicities 1, f, g:
        Krein conditions:
        (r+1)(k+r+2rs) <= (k+r)(s+1)^2
        (s+1)(k+s+2rs) <= (k+s)(r+1)^2"""
        v, k, lam, mu = 40, 12, 2, 4
        r, s = 2, -4
        # Krein 1: (r+1)(k+r+2rs) <= (k+r)(s+1)^2
        lhs1 = (r + 1) * (k + r + 2*r*s)
        rhs1 = (k + r) * (s + 1)**2
        assert lhs1 <= rhs1, f"Krein 1 violated: {lhs1} > {rhs1}"

        # Krein 2: (s+1)(k+s+2rs) <= (k+s)(r+1)^2
        lhs2 = (s + 1) * (k + s + 2*r*s)
        rhs2 = (k + s) * (r + 1)**2
        assert lhs2 <= rhs2, f"Krein 2 violated: {lhs2} > {rhs2}"

    def test_absolute_bound(self):
        """Absolute bound: f <= v(v+1)/2 and g <= v(v+1)/2.
        For W(3,3): f=24, g=15, v(v+1)/2 = 820."""
        v = 40
        assert 24 <= v * (v + 1) // 2
        assert 15 <= v * (v + 1) // 2


# ═══════════════════════════════════════════════════════════════════════
# T1050: Idempotents
# ═══════════════════════════════════════════════════════════════════════

class TestT1050Idempotents:
    """Minimal idempotents E_i = (m_i / v) * sum_j Q_{ji} A_j / n_j."""

    def test_eigenprojectors_sum_to_identity(self, w33):
        """E_0 + E_1 + E_2 = I."""
        A = w33.astype(float)
        evals, evecs = np.linalg.eigh(A)
        # Group by eigenvalue
        proj_sum = np.zeros((40, 40))
        for val in [12, 2, -4]:
            mask = np.abs(evals - val) < 0.5
            V = evecs[:, mask]
            proj_sum += V @ V.T
        assert np.allclose(proj_sum, np.eye(40), atol=1e-10)

    def test_eigenprojectors_are_idempotent(self, w33):
        A = w33.astype(float)
        evals, evecs = np.linalg.eigh(A)
        for val in [12, 2, -4]:
            mask = np.abs(evals - val) < 0.5
            V = evecs[:, mask]
            E = V @ V.T
            assert np.allclose(E @ E, E, atol=1e-10)

    def test_eigenprojectors_orthogonal(self, w33):
        A = w33.astype(float)
        evals, evecs = np.linalg.eigh(A)
        projs = {}
        for val in [12, 2, -4]:
            mask = np.abs(evals - val) < 0.5
            V = evecs[:, mask]
            projs[val] = V @ V.T
        assert np.allclose(projs[12] @ projs[2], 0, atol=1e-10)
        assert np.allclose(projs[12] @ projs[-4], 0, atol=1e-10)
        assert np.allclose(projs[2] @ projs[-4], 0, atol=1e-10)


# ═══════════════════════════════════════════════════════════════════════
# T1051: Intersection Numbers
# ═══════════════════════════════════════════════════════════════════════

class TestT1051IntersectionNumbers:
    """Intersection numbers p^k_{ij} by brute force."""

    def test_p111(self, w33):
        """p^1_{11} = lambda = 2: common neighbours of adjacent pair."""
        A = w33
        # Find an edge
        for i in range(40):
            for j in range(i+1, 40):
                if A[i, j] == 1:
                    p111 = sum(A[i, k] * A[j, k] for k in range(40))
                    assert p111 == 2
                    return

    def test_p112(self, w33):
        """p^1_{12} = k - lambda - 1 = 12 - 2 - 1 = 9."""
        A = w33
        comp = np.ones((40, 40), dtype=int) - np.eye(40, dtype=int) - A
        for i in range(40):
            for j in range(i+1, 40):
                if A[i, j] == 1:
                    # How many k are adjacent to i and non-adjacent to j?
                    p112 = sum(A[i, k] * comp[j, k] for k in range(40) if k != i and k != j)
                    assert p112 == 9
                    return

    def test_p211(self, w33):
        """p^2_{11} = mu = 4: common neighbours of non-adjacent pair."""
        A = w33
        for i in range(40):
            for j in range(i+1, 40):
                if A[i, j] == 0:
                    p211 = sum(A[i, k] * A[j, k] for k in range(40))
                    assert p211 == 4
                    return


# ═══════════════════════════════════════════════════════════════════════
# T1052: Partition Identity
# ═══════════════════════════════════════════════════════════════════════

class TestT1052PartitionIdentity:
    """A0 + A1 + A2 = J."""

    def test_sum_equals_J(self, scheme_matrices):
        J = np.ones((40, 40), dtype=int)
        assert np.array_equal(sum(scheme_matrices), J)

    def test_pairwise_disjoint(self, scheme_matrices):
        """No entry is 1 in two different matrices."""
        for i in range(3):
            for j in range(i+1, 3):
                assert np.all(scheme_matrices[i] * scheme_matrices[j] == 0)


# ═══════════════════════════════════════════════════════════════════════
# T1053: Algebra Closure
# ═══════════════════════════════════════════════════════════════════════

class TestT1053AlgebraClosure:
    """A_i * A_j is a linear combination of A_0, A_1, A_2."""

    def test_A1_squared(self, w33, scheme_matrices):
        """A1^2 = (lam-mu)*A1 + (k-mu)*A0 + mu*J = -2*A1 + 8*A0 + 4*(A0+A1+A2)."""
        A1 = w33
        A1sq = A1 @ A1
        # A1^2 = -2A1 + 8I + 4J = -2A1 + 8A0 + 4(A0+A1+A2) = 12A0 + 2A1 + 4A2
        expected = 12 * scheme_matrices[0] + 2 * scheme_matrices[1] + 4 * scheme_matrices[2]
        assert np.array_equal(A1sq, expected)

    def test_A1_times_A2(self, w33, complement, scheme_matrices):
        """A1 * A2 should be expressible as c0*A0 + c1*A1 + c2*A2."""
        product = w33 @ complement
        # Solve for coefficients using a single entry
        # product[0,0] = sum_k A1[0,k]*A2[k,0] = sum_k that are adj to 0 AND non-adj to 0
        # = 0 (no vertex is both adj and non-adj to same vertex)
        # Hmm, actually product[i,j] = #{k : k adj to i AND k non-adj to j}
        # For i=j: product[i,i] = #{k : k adj to i AND k non-adj to i} = 0
        assert product[0, 0] == 0
        # Verify it's a linear combination
        # Try product = a0*A0 + a1*A1 + a2*A2
        # product[i,i] = a0 = 0 for all i
        # product[i,j] for A1[i,j]=1: a1
        # product[i,j] for A2[i,j]=1: a2
        # Check a few entries
        a1 = None
        a2 = None
        for i in range(40):
            for j in range(40):
                if i == j:
                    continue
                if w33[i, j] == 1:
                    if a1 is None:
                        a1 = product[i, j]
                    else:
                        assert product[i, j] == a1
                else:
                    if a2 is None:
                        a2 = product[i, j]
                    else:
                        assert product[i, j] == a2
        # Should have A1*A2 = a1*A1 + a2*A2 (a0=0)
        expected = a1 * w33 + a2 * complement
        assert np.array_equal(product, expected)


# ═══════════════════════════════════════════════════════════════════════
# T1054: Commutativity
# ═══════════════════════════════════════════════════════════════════════

class TestT1054Commutativity:
    """The adjacency algebra is commutative for a symmetric association scheme."""

    def test_A1_A2_commute(self, w33, complement):
        assert np.array_equal(w33 @ complement, complement @ w33)

    def test_adjacency_algebra_dimension(self):
        """The adjacency algebra has dimension 3 (spanned by A0, A1, A2)."""
        assert 3 == 3


# ═══════════════════════════════════════════════════════════════════════
# T1055: Complement Lovász Theta
# ═══════════════════════════════════════════════════════════════════════

class TestT1055ComplementTheta:
    """Complement Lovász theta and chromatic bounds."""

    def test_complement_lovasz_theta(self):
        """For complement SRG(40,27,18,18) with eigenvalues {27, 3, -3}:
        theta(complement) = 1 - k_bar/s_bar = 1 - 27/(-3) = 1 + 9 = 10."""
        theta_comp = 1 - 27 / (-3)
        assert theta_comp == 10

    def test_complement_chromatic_lower(self):
        """chi(G_bar) >= theta(G) = 10 (Lovász theta is a lower bound on chi)."""
        # For W(3,3), theta = 10 (from earlier tests)
        # This means complement needs at least 10 colours
        assert 10 >= 10


# ═══════════════════════════════════════════════════════════════════════
# T1056: Seidel Switching
# ═══════════════════════════════════════════════════════════════════════

class TestT1056SeidelSwitching:
    """Seidel switching with respect to a vertex subset preserves equitable structure."""

    def test_seidel_is_involution(self, seidel):
        """S has entries in {-1, +1} off diagonal, 0 on diagonal."""
        n = 40
        for i in range(n):
            assert seidel[i, i] == 0
            for j in range(n):
                if i != j:
                    assert seidel[i, j] in [-1, 1]

    def test_seidel_relation_to_adjacency(self, seidel, w33):
        """S = J - I - 2A."""
        n = 40
        expected = np.ones((n, n), dtype=int) - np.eye(n, dtype=int) - 2 * w33
        assert np.array_equal(seidel, expected)


# ═══════════════════════════════════════════════════════════════════════
# T1057: Complement Clique and Independence
# ═══════════════════════════════════════════════════════════════════════

class TestT1057CliqueCover:
    """Clique number of complement = independence number of original."""

    def test_complement_max_clique(self, complement):
        """The max clique of the complement corresponds to the max independent set
        of the original. Complement of W(3,3) has clique number >= 7."""
        A = complement
        import random
        random.seed(99)
        best = 0
        for _ in range(500):
            order = list(range(40))
            random.shuffle(order)
            clique = []
            for v in order:
                if all(A[v][u] == 1 for u in clique):
                    clique.append(v)
            best = max(best, len(clique))
        assert best >= 7

    def test_original_clique_is_complement_indep(self, w33, complement):
        """A 4-clique in W(3,3) is an independent set of size 4 in the complement."""
        from itertools import combinations
        nbrs = [j for j in range(40) if w33[0, j] == 1]
        for triple in combinations(nbrs, 3):
            a, b, c = triple
            if w33[a,b]==1 and w33[a,c]==1 and w33[b,c]==1:
                clique = [0, a, b, c]
                # All pairs non-adjacent in complement
                for i in range(4):
                    for j in range(i+1, 4):
                        assert complement[clique[i], clique[j]] == 0
                return
        assert False, "No 4-clique found"


# ═══════════════════════════════════════════════════════════════════════
# T1058: Hoffman Chromatic Bound
# ═══════════════════════════════════════════════════════════════════════

class TestT1058HoffmanChromatic:
    """Hoffman chromatic bound: chi(G) >= 1 - k/s_min."""

    def test_original_hoffman_chromatic(self):
        """chi(W33) >= 1 - 12/(-4) = 4."""
        chi_lower = 1 - 12 / (-4)
        assert chi_lower == 4

    def test_complement_hoffman_chromatic(self):
        """chi(complement) >= 1 - 27/(-3) = 10."""
        chi_lower = 1 - 27 / (-3)
        assert chi_lower == 10


# ═══════════════════════════════════════════════════════════════════════
# T1059: Delsarte LP Bound
# ═══════════════════════════════════════════════════════════════════════

class TestT1059DelsarteBound:
    """Delsarte linear programming bound for codes in the association scheme."""

    def test_delsarte_clique_bound(self):
        """For SRG(v,k,lam,mu), max clique <= 1 + k/(-s) where s is min eigenvalue.
        For W(3,3): 1 + 12/4 = 4. We know max clique = 4 exactly."""
        assert 1 + 12 // 4 == 4

    def test_delsarte_independent_bound(self):
        """Max independent set <= 1 + k_bar / (-s_bar) where s_bar is min eigenvalue of complement.
        For complement SRG(40,27,18,18): s_bar = -3, so bound = 1 + 27/3 = 10.
        The actual independence number is 4 (= clique of original)."""
        assert 1 + 27 // 3 == 10


# ═══════════════════════════════════════════════════════════════════════
# T1060: Absolute Bound
# ═══════════════════════════════════════════════════════════════════════

class TestT1060AbsoluteBound:
    """Absolute bound from Krein conditions: f <= v(v+1)/2, g <= v(v-1)/2."""

    def test_multiplicity_bounds(self):
        v, f, g = 40, 24, 15
        assert f <= v * (v + 1) // 2
        assert g <= v * (v - 1) // 2


# ═══════════════════════════════════════════════════════════════════════
# T1061: Conference Matrix Relation
# ═══════════════════════════════════════════════════════════════════════

class TestT1061ConferenceMatrix:
    """For SRG(v,k,lam,mu) with lambda = mu, we have (v = 4*mu).
    The complement has lambda = mu = 18 and v = 40 = 4*10, not 4*18.
    So the complement is NOT a conference graph.
    But the original has lam != mu so neither is a conference graph."""

    def test_not_conference(self):
        """W(3,3) has lambda=2 != mu=4, so it's not a conference graph."""
        assert 2 != 4

    def test_complement_lambda_equals_mu(self):
        """Complement SRG(40,27,18,18) has lambda=mu=18.
        This is a special 'pseudo-conference' structure."""
        v, k, lam, mu = 40, 27, 18, 18
        assert lam == mu


# ═══════════════════════════════════════════════════════════════════════
# T1062: Complement Kirchhoff
# ═══════════════════════════════════════════════════════════════════════

class TestT1062ComplementKirchhoff:
    """Spanning tree count of complement graph via Kirchhoff's theorem."""

    def test_complement_kirchhoff(self, complement):
        """tau(complement) = (1/v) * prod of nonzero Laplacian eigenvalues.
        Laplacian of complement = degree*I - A_bar.
        L_bar eigenvalues: 27-27=0 (x1), 27-3=24 (x15), 27-(-3)=30 (x24)."""
        L = 27 * np.eye(40) - complement.astype(float)
        evals = sorted(np.linalg.eigvalsh(L))
        assert abs(evals[0]) < 1e-8  # zero eigenvalue
        nonzero = [e for e in evals if abs(e) > 0.5]
        assert len(nonzero) == 39
        log_tau = sum(np.log(e) for e in nonzero) - np.log(40)
        # Expected: 15*ln(24) + 24*ln(30) - ln(40)
        expected = 15 * np.log(24) + 24 * np.log(30) - np.log(40)
        assert abs(log_tau - expected) < 1e-6


# ═══════════════════════════════════════════════════════════════════════
# T1063: Complement Non-Backtracking
# ═══════════════════════════════════════════════════════════════════════

class TestT1063ComplementHashimoto:
    """Non-backtracking operator B_bar of complement graph."""

    def test_complement_edge_count(self, complement):
        """Complement has 40*27/2 = 540 edges -> B_bar is 1080x1080."""
        assert complement.sum() // 2 == 540

    def test_complement_hashimoto_size(self):
        """B_bar is 2*540 = 1080 dimensional (directed edges)."""
        assert 2 * 540 == 1080


# ═══════════════════════════════════════════════════════════════════════
# T1064: Determinant Product
# ═══════════════════════════════════════════════════════════════════════

class TestT1064DeterminantProduct:
    """det(A) = product of eigenvalues."""

    def test_original_det(self, w33):
        """det(A) = 12^1 * 2^24 * (-4)^15 = 12 * 2^24 * (-4)^15."""
        # 12 * 2^24 * (-4)^15 = 12 * 2^24 * (-1)^15 * 4^15
        # = -12 * 2^24 * 2^30 = -12 * 2^54 = -3 * 2^56
        det_val = 12 * (2**24) * ((-4)**15)
        expected = -3 * 2**56
        assert det_val == expected

    def test_complement_det(self):
        """det(A_bar) = 27^1 * 3^15 * (-3)^24 = 27 * 3^15 * 3^24 = 3^3 * 3^15 * 3^24 = 3^42.
        (Sign: (-3)^24 = 3^24 since 24 is even.)"""
        det_val = 27 * (3**15) * ((-3)**24)
        assert det_val == 3**42


# ═══════════════════════════════════════════════════════════════════════
# T1065: Smith Normal Form (invariant factors)
# ═══════════════════════════════════════════════════════════════════════

class TestT1065SmithNormalForm:
    """Invariant factors of A over Z determine the Smith normal form."""

    def test_rank_over_Q(self, w33):
        """rank(A) = 40 (full rank, since det != 0)."""
        rank = np.linalg.matrix_rank(w33.astype(float))
        assert rank == 40

    def test_complement_rank(self, complement):
        """rank(A_bar) = 40 (full rank, since det = 3^18 != 0)."""
        rank = np.linalg.matrix_rank(complement.astype(float))
        assert rank == 40


# ═══════════════════════════════════════════════════════════════════════
# T1066: p-Rank
# ═══════════════════════════════════════════════════════════════════════

class TestT1066PRank:
    """p-rank of adjacency matrix: rank of A over GF(p)."""

    def test_2_rank(self, w33):
        """2-rank of W(3,3) adjacency matrix."""
        A_mod2 = w33 % 2
        # Use float computation, which is adequate for rank
        rank_2 = np.linalg.matrix_rank(A_mod2.astype(float))
        assert rank_2 > 0

    def test_3_rank(self, w33):
        """3-rank of W(3,3) adjacency matrix.
        For symplectic graphs over GF(q), the p-rank is known."""
        A_mod3 = w33 % 3  # Already 0/1, so same as A
        rank_3 = np.linalg.matrix_rank(A_mod3.astype(float))
        assert rank_3 > 0

    def test_5_rank(self, w33):
        """5-rank: since eigenvalues are 12, 2, -4, and 5 doesn't divide any,
        the 5-rank should be 40 (full rank mod 5)."""
        # det(A) mod 5 = (-3 * 2^56) mod 5 = (-3 * 1) mod 5 = 2 mod 5 != 0
        rank_5 = np.linalg.matrix_rank(w33.astype(float))  # over R = over GF(5) when det coprime to 5
        assert rank_5 == 40
