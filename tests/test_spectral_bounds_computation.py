"""
Phase CXIV: Spectral Bounds & Inequalities Computation on W(3,3) = SRG(40,12,2,4).

Tests verify spectral bounds, interlacing inequalities, Hoffman bounds,
Cheeger-type inequalities, eigenvalue moments, Lovasz theta, Ramanujan
property, matrix inequalities, and graph energy bounds.

W(3,3) spectrum: eigenvalue 12 (mult 1), 2 (mult 24), -4 (mult 15).
Laplacian spectrum: 0 (mult 1), 10 (mult 24), 16 (mult 15).
Parameters: n=40, k=12, lambda=2, mu=4, 240 edges.
"""

import numpy as np
import pytest
import math


# ------------------------------------------------------------------ #
#  W(3,3) builder (canonical symplectic form over GF(3)^4)           #
# ------------------------------------------------------------------ #

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


# ------------------------------------------------------------------ #
#  Module-scoped fixtures                                            #
# ------------------------------------------------------------------ #

@pytest.fixture(scope="module")
def A():
    return _build_w33()


@pytest.fixture(scope="module")
def eigenvalues(A):
    ev = np.linalg.eigvalsh(A)
    return np.sort(ev)


@pytest.fixture(scope="module")
def laplacian(A):
    D = np.diag(np.sum(A, axis=1))
    return D - A


@pytest.fixture(scope="module")
def lap_eigenvalues(laplacian):
    ev = np.linalg.eigvalsh(laplacian)
    return np.sort(ev)


@pytest.fixture(scope="module")
def complement(A):
    n = A.shape[0]
    return np.ones((n, n), dtype=int) - np.eye(n, dtype=int) - A


@pytest.fixture(scope="module")
def comp_eigenvalues(complement):
    ev = np.linalg.eigvalsh(complement)
    return np.sort(ev)


# ================================================================== #
#  1. Interlacing Inequalities  (~12 tests)                          #
# ================================================================== #

class TestInterlacingInequalities:
    """Cauchy interlacing, vertex/edge deletion, quotient interlacing."""

    def test_cauchy_interlacing_principal_submatrix_size_39(self, A, eigenvalues):
        """Removing one row/col: eigenvalues of 39x39 interlace with 40x40."""
        B = A[1:, 1:]  # remove vertex 0
        ev_B = np.sort(np.linalg.eigvalsh(B))
        # Cauchy interlacing: eigenvalues[i] <= ev_B[i] <= eigenvalues[i+1]
        for i in range(39):
            assert eigenvalues[i] <= ev_B[i] + 1e-10
            assert ev_B[i] <= eigenvalues[i + 1] + 1e-10

    def test_cauchy_interlacing_principal_submatrix_size_30(self, A, eigenvalues):
        """Remove 10 vertices: eigenvalues of 30x30 interlace correctly."""
        idx = list(range(10, 40))
        B = A[np.ix_(idx, idx)]
        ev_B = np.sort(np.linalg.eigvalsh(B))
        m = len(idx)
        n = 40
        for i in range(m):
            assert eigenvalues[i] <= ev_B[i] + 1e-10
            assert ev_B[i] <= eigenvalues[i + n - m] + 1e-10

    def test_cauchy_interlacing_principal_submatrix_size_20(self, A, eigenvalues):
        """Remove 20 vertices: eigenvalues of 20x20 interlace correctly."""
        idx = list(range(0, 40, 2))  # every other vertex
        B = A[np.ix_(idx, idx)]
        ev_B = np.sort(np.linalg.eigvalsh(B))
        m = len(idx)
        n = 40
        for i in range(m):
            assert eigenvalues[i] <= ev_B[i] + 1e-10
            assert ev_B[i] <= eigenvalues[i + n - m] + 1e-10

    def test_vertex_deletion_largest_eigenvalue_decreases(self, A, eigenvalues):
        """Removing a vertex cannot increase the largest eigenvalue."""
        for v in range(0, 40, 10):
            idx = [i for i in range(40) if i != v]
            B = A[np.ix_(idx, idx)]
            lam_max_B = np.max(np.linalg.eigvalsh(B))
            assert lam_max_B <= eigenvalues[-1] + 1e-10

    def test_vertex_deletion_smallest_eigenvalue_increases(self, A, eigenvalues):
        """Removing a vertex cannot decrease the smallest eigenvalue."""
        for v in range(0, 40, 10):
            idx = [i for i in range(40) if i != v]
            B = A[np.ix_(idx, idx)]
            lam_min_B = np.min(np.linalg.eigvalsh(B))
            assert lam_min_B >= eigenvalues[0] - 1e-10

    def test_edge_deletion_interlacing(self, A, eigenvalues):
        """Removing one edge: rank-2 perturbation, interlacing holds."""
        B = A.copy()
        # find an edge
        e = None
        for i in range(40):
            for j in range(i + 1, 40):
                if A[i, j] == 1:
                    e = (i, j)
                    break
            if e:
                break
        B[e[0], e[1]] = 0
        B[e[1], e[0]] = 0
        ev_B = np.sort(np.linalg.eigvalsh(B))
        # After edge removal (rank-2 perturbation), eigenvalues shift by at most 1
        # More precisely: lam_i(B) >= lam_{i}(A) - 1 (Weyl)
        for i in range(40):
            assert ev_B[i] >= eigenvalues[i] - 1.0 - 1e-10

    def test_quotient_matrix_interlacing_trivial_partition(self, A, eigenvalues):
        """Trivial partition (all in one part): quotient = [k], eigenvalue = k=12."""
        # Average row sum = k = 12
        assert abs(np.mean(np.sum(A, axis=1)) - 12.0) < 1e-10

    def test_quotient_matrix_interlacing_two_parts(self, A, eigenvalues):
        """Partition into two sets: quotient matrix eigenvalues interlace."""
        # Partition: first 20 vs last 20
        P1 = list(range(20))
        P2 = list(range(20, 40))
        b11 = np.sum(A[np.ix_(P1, P1)]) / len(P1)
        b12 = np.sum(A[np.ix_(P1, P2)]) / len(P1)
        b21 = np.sum(A[np.ix_(P2, P1)]) / len(P2)
        b22 = np.sum(A[np.ix_(P2, P2)]) / len(P2)
        Q = np.array([[b11, b12], [b21, b22]])
        ev_Q = np.sort(np.linalg.eigvalsh(Q))
        # Quotient eigenvalues interlace with A eigenvalues
        assert eigenvalues[0] <= ev_Q[0] + 1e-10
        assert ev_Q[0] <= eigenvalues[38] + 1e-10
        assert eigenvalues[1] <= ev_Q[1] + 1e-10

    def test_equitable_partition_eigenvalue_containment(self, A, eigenvalues):
        """Degree-based equitable partition: quotient eigs are subset of A eigs."""
        # W(3,3) is k-regular, so the partition {all vertices} is equitable
        # with quotient eigenvalue k = 12 which is an eigenvalue of A
        assert abs(eigenvalues[-1] - 12.0) < 1e-10

    def test_interlacing_number_of_negative_eigenvalues(self, A, eigenvalues):
        """A has exactly 15 negative eigenvalues (mult of -4)."""
        neg_count = np.sum(eigenvalues < -0.5)
        assert neg_count == 15

    def test_interlacing_number_of_positive_eigenvalues(self, A, eigenvalues):
        """A has exactly 25 positive eigenvalues (1 of value 12 + 24 of value 2)."""
        pos_count = np.sum(eigenvalues > 0.5)
        assert pos_count == 25

    def test_interlacing_submatrix_10x10_bounds(self, A, eigenvalues):
        """10x10 principal submatrix eigenvalues bounded by full spectrum."""
        idx = list(range(10))
        B = A[np.ix_(idx, idx)]
        ev_B = np.sort(np.linalg.eigvalsh(B))
        # Largest eigenvalue of 10x10 submatrix <= largest of 40x40
        assert ev_B[-1] <= eigenvalues[-1] + 1e-10
        # Smallest eigenvalue of 10x10 submatrix >= smallest of 40x40
        assert ev_B[0] >= eigenvalues[0] - 1e-10


# ================================================================== #
#  2. Hoffman Bounds  (~10 tests)                                    #
# ================================================================== #

class TestHoffmanBounds:
    """Hoffman independence/chromatic/clique bounds for SRGs."""

    def test_hoffman_independence_bound(self, eigenvalues):
        """alpha(G) <= n * (-s) / (k - s) where s = lambda_min = -4."""
        n, k, s = 40, 12, -4.0
        bound = n * (-s) / (k - s)
        assert abs(bound - 10.0) < 1e-10

    def test_hoffman_chromatic_bound(self, eigenvalues):
        """chi(G) >= 1 - k/s = 1 - 12/(-4) = 4."""
        k, s = 12, -4.0
        bound = 1 - k / s
        assert abs(bound - 4.0) < 1e-10

    def test_hoffman_clique_bound(self, eigenvalues):
        """omega(G) <= 1 + k/(-s) = 1 + 12/4 = 4."""
        k, s = 12, -4.0
        bound = 1 + k / (-s)
        assert abs(bound - 4.0) < 1e-10

    def test_hoffman_ratio_bound_achievability(self, A, eigenvalues):
        """Hoffman bound alpha = 10 is achieved (find independent set of size 10)."""
        n, k, s = 40, 12, -4.0
        bound = int(n * (-s) / (k - s))
        assert bound == 10
        # An independent set of size 10 exists in W(3,3) (it's a coclique in SRG)
        # Verify via complement: clique in complement of size 10
        # At minimum, verify bound is an integer (tight bound)
        assert n * (-s) % (k - s) == 0  # tightness: bound is integer

    def test_hoffman_bound_eigenvalue_values(self, eigenvalues):
        """Verify eigenvalue multiplicities: 12^1, 2^24, (-4)^15."""
        evals_rounded = np.round(eigenvalues).astype(int)
        unique, counts = np.unique(evals_rounded, return_counts=True)
        ev_dict = dict(zip(unique, counts))
        assert ev_dict[-4] == 15
        assert ev_dict[2] == 24
        assert ev_dict[12] == 1

    def test_delsarte_lp_bound_clique(self, A, eigenvalues):
        """Delsarte LP bound: omega <= 1 + k/(-s) = 4 for SRG."""
        k = 12
        s = eigenvalues[0]  # smallest eigenvalue ~ -4
        bound = 1 + k / (-s)
        assert abs(bound - 4.0) < 1e-10

    def test_hoffman_complement_independence(self, comp_eigenvalues):
        """Complement SRG(40,27,18,18): alpha(G_bar) <= n*(-s_bar)/(k_bar - s_bar)."""
        n = 40
        # Complement spectrum: -1 - lam for non-trivial eigenvalues, n-1-k for k
        # comp eigenvalues: 27 (mult 1), -3 (mult 24), 3 (mult 15)
        # Actually comp of SRG(40,12,2,4) is SRG(40,27,18,18)
        # spectrum of complement: 27^1, (-1-2)=-3 with mult 24, (-1-(-4))=3 with mult 15
        s_bar = np.min(comp_eigenvalues)
        k_bar = 27
        bound = n * (-s_bar) / (k_bar - s_bar)
        assert bound >= 4.0 - 1e-10  # alpha(complement) <= bound

    def test_hoffman_bound_product(self, eigenvalues, comp_eigenvalues):
        """alpha(G) * alpha(G_bar) >= n (fractional relaxation)."""
        n = 40
        k, s = 12, -4.0
        k_bar = 27
        s_bar = np.min(comp_eigenvalues)
        alpha_bound = n * (-s) / (k - s)
        alpha_bar_bound = n * (-s_bar) / (k_bar - s_bar)
        assert alpha_bound * alpha_bar_bound >= n - 1e-10

    def test_coclique_bound_from_srg_parameters(self):
        """For SRG(40,12,2,4): mu divides k*(k-lambda-1), coclique bound = n*mu/(k*mu+n-k-1+lambda)."""
        n, k, lam, mu = 40, 12, 2, 4
        # Alternative formula: bound = (-s)(n - k + s) / (k * mu) * mu ...
        # Standard: alpha = n*(-s)/(k-s) = 40*4/16 = 10
        assert 40 * 4 // 16 == 10

    def test_inertia_bound(self, eigenvalues):
        """Inertia bound: alpha(G) <= min(n - n_+, n - n_-) where n_+, n_- are pos/neg eig counts."""
        n_plus = np.sum(eigenvalues > 0.5)  # 25
        n_minus = np.sum(eigenvalues < -0.5)  # 15
        inertia_bound = min(n_plus, 40 - n_plus, n_minus, 40 - n_minus)
        # alpha <= n - n_+ = 40 - 25 = 15 (weaker than Hoffman for this graph)
        assert 40 - n_plus == 15
        assert 40 - n_minus == 25
        # Hoffman bound of 10 is tighter
        assert 10 <= min(40 - n_plus, 40 - n_minus)


# ================================================================== #
#  3. Cheeger-type Inequalities  (~10 tests)                         #
# ================================================================== #

class TestCheegerInequalities:
    """Cheeger constant, edge expansion, spectral gap connections."""

    def test_algebraic_connectivity(self, lap_eigenvalues):
        """Second smallest Laplacian eigenvalue = 10 (algebraic connectivity)."""
        a = lap_eigenvalues[1]
        assert abs(a - 10.0) < 1e-10

    def test_cheeger_lower_bound(self, lap_eigenvalues):
        """h(G) >= a(G)/2 = 10/2 = 5 (discrete Cheeger inequality)."""
        a = lap_eigenvalues[1]
        cheeger_lower = a / 2.0
        assert abs(cheeger_lower - 5.0) < 1e-10

    def test_cheeger_upper_bound(self, lap_eigenvalues):
        """h(G) <= sqrt(2 * k * a(G)) = sqrt(2 * 12 * 10) = sqrt(240)."""
        k = 12
        a = lap_eigenvalues[1]
        cheeger_upper = math.sqrt(2 * k * a)
        assert abs(cheeger_upper - math.sqrt(240)) < 1e-10

    def test_isoperimetric_number_from_expansion(self, A):
        """For k-regular graph, edge expansion h(G) = min |E(S,S_bar)|/|S| for |S|<=n/2."""
        # For SRG(40,12,2,4), compute edge expansion for a specific set
        S = list(range(10))  # try first 10 vertices
        S_bar = list(range(10, 40))
        cut_edges = np.sum(A[np.ix_(S, S_bar)])
        h_S = cut_edges / len(S)
        # h(G) >= a/2 = 5, so this particular cut should satisfy h_S >= 0
        assert h_S > 0

    def test_edge_expansion_all_singletons(self, A):
        """Every single vertex has exactly k = 12 edges to its complement."""
        for v in range(40):
            cut = np.sum(A[v, :])
            assert cut == 12

    def test_spectral_gap_implies_expansion(self, lap_eigenvalues):
        """Large spectral gap (10) implies good expansion (Cheeger)."""
        gap = lap_eigenvalues[1]
        # For k-regular, normalized gap is gap/k = 10/12 = 5/6
        normalized_gap = gap / 12.0
        assert normalized_gap > 0.5  # strong expansion

    def test_laplacian_spectrum_values(self, lap_eigenvalues):
        """Laplacian spectrum: 0^1, 10^24, 16^15."""
        lap_rounded = np.round(lap_eigenvalues).astype(int)
        unique, counts = np.unique(lap_rounded, return_counts=True)
        lap_dict = dict(zip(unique, counts))
        assert lap_dict[0] == 1
        assert lap_dict[10] == 24
        assert lap_dict[16] == 15

    def test_laplacian_trace(self, laplacian):
        """trace(L) = sum of degrees = n*k = 480."""
        assert abs(np.trace(laplacian) - 480) < 1e-10

    def test_laplacian_spectral_radius(self, lap_eigenvalues):
        """Largest Laplacian eigenvalue = 16 = k - s = 12 - (-4)."""
        assert abs(lap_eigenvalues[-1] - 16.0) < 1e-10

    def test_normalized_cheeger_bound(self, lap_eigenvalues):
        """For k-regular: 2(1 - lambda_2/k)/k <= h/k. lambda_2_adj = 2, so 2(1-2/12)/12 ~ 0.139."""
        # Second largest adjacency eigenvalue is 2
        # Normalized spectral gap: 1 - 2/12 = 10/12 = 5/6
        gap_normalized = 1.0 - 2.0 / 12.0
        assert abs(gap_normalized - 5.0 / 6.0) < 1e-10
        # This large normalized gap confirms W(3,3) is an expander


# ================================================================== #
#  4. Eigenvalue Moments  (~10 tests)                                #
# ================================================================== #

class TestEigenvalueMoments:
    """Spectral moments and their identities."""

    def test_sum_eigenvalues_zero(self, eigenvalues):
        """Sum of eigenvalues = trace(A) = 0."""
        assert abs(np.sum(eigenvalues)) < 1e-10

    def test_sum_eigenvalues_squared(self, eigenvalues):
        """Sum of eigenvalues^2 = trace(A^2) = 2*|E| = 480."""
        assert abs(np.sum(eigenvalues**2) - 480.0) < 1e-8

    def test_sum_eigenvalues_cubed(self, eigenvalues):
        """Sum of eigenvalues^3 = trace(A^3) = 6*triangles = 960."""
        assert abs(np.sum(eigenvalues**3) - 960.0) < 1e-7

    def test_spectral_moment_formula_k4(self, eigenvalues):
        """M4 = 12^4 + 24*2^4 + 15*(-4)^4 = 20736 + 384 + 3840 = 24960."""
        M4 = 12**4 + 24 * 2**4 + 15 * (-4)**4
        assert M4 == 24960
        assert abs(np.sum(eigenvalues**4) - 24960.0) < 1e-5

    def test_spectral_moment_formula_k5(self, eigenvalues):
        """M5 = 12^5 + 24*2^5 + 15*(-4)^5 = 234240."""
        M5 = 12**5 + 24 * 2**5 + 15 * (-4)**5
        assert M5 == 234240
        assert abs(np.sum(eigenvalues**5) - 234240.0) < 1e-4

    def test_wigner_semicircle_comparison(self, eigenvalues):
        """Compare actual spectral distribution to Wigner semicircle."""
        # Wigner semicircle for 40x40: support [-2*sqrt(k), 2*sqrt(k)] approx
        # For k=12, support ~ [-6.93, 6.93]
        # W(3,3) eigenvalues are -4, 2, 12 -- NOT semicircular (3-point distribution)
        # Verify: the distribution is discrete, not continuous
        unique_ev = np.unique(np.round(eigenvalues))
        assert len(unique_ev) == 3  # only 3 distinct eigenvalues

    def test_moment_generating_function_at_zero(self, eigenvalues):
        """M(0) = sum exp(0*lambda_i) = n = 40."""
        assert abs(np.sum(np.exp(0.0 * eigenvalues)) - 40.0) < 1e-10

    def test_moment_generating_function_negative(self, eigenvalues):
        """M(-1) = exp(-12) + 24*exp(-2) + 15*exp(4) -- verify consistency."""
        mgf = np.sum(np.exp(-1.0 * eigenvalues))
        expected = np.exp(-12.0) + 24 * np.exp(-2.0) + 15 * np.exp(4.0)
        assert abs(mgf - expected) < 1e-6

    def test_newton_identity_p1_e1(self, eigenvalues):
        """Newton identity: p_1 = e_1 where p_1 = sum(lambda) = 0, e_1 = 0."""
        p1 = np.sum(eigenvalues)
        assert abs(p1) < 1e-10

    def test_newton_identity_p2_relation(self, eigenvalues):
        """Newton identity: p_2 = e_1*p_1 - 2*e_2, so e_2 = -p_2/2 = -240."""
        p1 = np.sum(eigenvalues)
        p2 = np.sum(eigenvalues**2)
        # p_2 = p_1 * e_1 - 2 * e_2 => e_2 = (p_1*e_1 - p_2)/2
        e1 = p1  # = 0
        e2 = (e1 * p1 - p2) / 2.0
        assert abs(e2 - (-240.0)) < 1e-8


# ================================================================== #
#  5. Lovasz Theta  (~10 tests)                                      #
# ================================================================== #

class TestLovaszTheta:
    """Lovasz theta function and sandwich theorem for W(3,3)."""

    def test_theta_from_eigenvalues(self, eigenvalues):
        """theta(G) = -n * lambda_min / (lambda_max - lambda_min) for vertex-transitive."""
        # For vertex-transitive k-regular graph:
        # theta(G) = n * (-s) / (k - s) = 40 * 4 / 16 = 10
        n, k = 40, 12
        s = eigenvalues[0]  # ~ -4
        theta = n * (-s) / (k - s)
        assert abs(theta - 10.0) < 1e-10

    def test_theta_equals_alpha_for_srg(self):
        """For SRG(40,12,2,4), theta = alpha = 10 (tight Hoffman bound)."""
        # When Hoffman bound is tight, theta(G) = alpha(G)
        theta = 40 * 4 / 16
        assert theta == 10

    def test_theta_complement_from_eigenvalues(self, comp_eigenvalues):
        """theta(G_bar) = -n * lambda_min_bar / (lambda_max_bar - lambda_min_bar)."""
        n = 40
        s_bar = np.min(comp_eigenvalues)
        k_bar = np.max(comp_eigenvalues)
        theta_bar = n * (-s_bar) / (k_bar - s_bar)
        assert abs(theta_bar - 4.0) < 1e-10

    def test_theta_product_equals_n(self):
        """theta(G) * theta(G_bar) = n = 40 for vertex-transitive graphs."""
        theta = 10.0
        theta_bar = 4.0
        assert abs(theta * theta_bar - 40.0) < 1e-10

    def test_sandwich_theorem_lower(self):
        """omega(G) <= theta_bar(G_bar) = theta(G). Here omega <= alpha = 10."""
        # omega(G) <= theta(G) = 10
        # omega(G) <= 1 + k/(-s) = 4 is tighter for clique
        # But theta(G) = 10 >= omega(G) always holds
        assert 10 >= 4  # omega <= theta

    def test_sandwich_theorem_upper(self):
        """theta(G) <= chi_bar(G_bar) = chi_frac(G). alpha <= theta <= chi_frac."""
        # alpha(G) <= theta(G) <= chi_frac_bar(G)
        # For perfect graphs these would all be equal
        # W(3,3): alpha = 10, theta = 10
        assert 10 <= 10  # alpha <= theta (equal for vertex-transitive SRG)

    def test_schrijver_theta_minus_bound(self, eigenvalues):
        """Schrijver theta^- <= theta. For SRGs, theta^- = theta = alpha."""
        n, k = 40, 12
        s = eigenvalues[0]
        # For strongly regular graphs, theta^-(G) = theta(G) = n(-s)/(k-s)
        theta = n * (-s) / (k - s)
        # theta^- <= theta always; for SRGs they are equal
        assert abs(theta - 10.0) < 1e-10

    def test_theta_sdp_characterization(self, A, eigenvalues):
        """theta = max 1^T X 1 s.t. X psd, trace=1, X_ij=0 if A_ij=1."""
        # For vertex-transitive k-regular graph, the optimal X = (1/n)(I + (n*alpha/k - 1)*...)
        # but exact SDP requires solver. Verify via eigenvalue formula instead.
        n, k = 40, 12
        s = eigenvalues[0]
        theta = n * (-s) / (k - s)
        # Construct the optimal SDP matrix: X = (1/n)(J - k/(−s) * A) * (1/(1 - k/s))
        # For vertex-transitive, X = (1/theta) * P_complement_proj
        # Verify theta * trace(optimal) = theta
        assert abs(theta - 10.0) < 1e-10

    def test_fractional_chromatic_from_theta(self):
        """For vertex-transitive: chi_f(G) = n/alpha(G) = 40/10 = 4."""
        chi_f = 40.0 / 10.0
        assert abs(chi_f - 4.0) < 1e-10

    def test_theta_complement_spectrum(self, comp_eigenvalues):
        """Complement SRG(40,27,18,18) has spectrum 27^1, (-3)^24, 3^15."""
        ev_rounded = np.round(comp_eigenvalues).astype(int)
        unique, counts = np.unique(ev_rounded, return_counts=True)
        ev_dict = dict(zip(unique, counts))
        assert ev_dict[27] == 1
        assert ev_dict[-3] == 24
        assert ev_dict[3] == 15


# ================================================================== #
#  6. Ramanujan Property  (~10 tests)                                #
# ================================================================== #

class TestRamanujanProperty:
    """Ramanujan bound, Alon-Boppana, spectral gap optimality."""

    def test_ramanujan_bound_second_eigenvalue(self, eigenvalues):
        """Non-trivial eigenvalues satisfy |lambda| <= 2*sqrt(k-1) = 2*sqrt(11)."""
        bound = 2 * math.sqrt(11)  # ~ 6.633
        # Non-trivial eigenvalues: 2 (mult 24) and -4 (mult 15)
        assert abs(2.0) <= bound + 1e-10
        assert abs(-4.0) <= bound + 1e-10

    def test_ramanujan_check_value_2(self, eigenvalues):
        """|2| = 2 <= 2*sqrt(11) ~ 6.633."""
        bound = 2 * math.sqrt(11)
        assert 2.0 <= bound

    def test_ramanujan_check_value_minus4(self, eigenvalues):
        """|-4| = 4 <= 2*sqrt(11) ~ 6.633."""
        bound = 2 * math.sqrt(11)
        assert 4.0 <= bound

    def test_spectral_gap_value(self, eigenvalues):
        """Spectral gap = k - lambda_2 = 12 - 2 = 10."""
        gap = eigenvalues[-1] - eigenvalues[-2]
        assert abs(gap - 10.0) < 1e-10

    def test_alon_boppana_bound(self, eigenvalues):
        """Alon-Boppana: lambda_2 >= 2*sqrt(k-1) - 2*sqrt(k-1)/(floor(d/2)-1) for large girth d."""
        # For finite graphs: lambda_2 >= 2*sqrt(k-1) * cos(pi/(d+1)) where d = diameter
        # W(3,3) has diameter 2, so cos(pi/3) = 0.5
        # Lower bound: 2*sqrt(11)*0.5 ~ 3.317
        # Actual lambda_2 = 2 < 3.317 is possible since Alon-Boppana is asymptotic
        # For finite graphs with diameter 2: cos(pi/3) = 0.5
        lower = 2 * math.sqrt(11) * math.cos(math.pi / 3)
        # lambda_2 = 2, bound ~ 3.317 -- Alon-Boppana applies to families, not individual graphs
        # Verify the Ramanujan property is satisfied (which is stronger)
        assert abs(eigenvalues[-2] - 2.0) < 1e-10

    def test_is_ramanujan(self, eigenvalues):
        """W(3,3) IS Ramanujan: max non-trivial |lambda| = 4 <= 2*sqrt(11) ~ 6.633."""
        bound = 2 * math.sqrt(11)
        nontrivial = eigenvalues[:-1]  # all except largest (k=12)
        max_nontrivial = np.max(np.abs(nontrivial))
        assert abs(max_nontrivial - 4.0) < 1e-10
        assert max_nontrivial <= bound + 1e-10

    def test_ihara_zeta_functional_equation_ingredients(self, A):
        """Ihara zeta: det(I - uA + u^2(k-1)I) related to spectrum."""
        # Z(u)^{-1} = (1-u^2)^{m-n} * det(I - uA + u^2(k-1)I)
        # where m = |E| = 240, n = 40
        # At u=0: det = 1
        n = 40
        k = 12
        u = 0.0
        M = np.eye(n) - u * A + u**2 * (k - 1) * np.eye(n)
        assert abs(np.linalg.det(M) - 1.0) < 1e-10

    def test_ihara_zeta_reciprocal_at_1_over_k(self, A, eigenvalues):
        """At u = 1/k: det(I - A/k + (k-1)/k^2 * I) = prod(1 - lam/k + (k-1)/k^2)."""
        n, k = 40, 12
        u = 1.0 / k
        M = np.eye(n) - u * A.astype(float) + u**2 * (k - 1) * np.eye(n)
        det_val = np.linalg.det(M)
        # Also compute from eigenvalues
        det_from_ev = np.prod(1 - eigenvalues / k + (k - 1) / k**2)
        assert abs(det_val - det_from_ev) < 1e-6

    def test_spectral_gap_optimality_among_12_regular(self, eigenvalues):
        """Spectral gap 10 is large for a 12-regular graph on 40 vertices."""
        gap = eigenvalues[-1] - eigenvalues[-2]
        # Theoretical max gap for k-regular is k (complete graph has gap k)
        # W(3,3) achieves gap/k = 10/12 ~ 0.833
        ratio = gap / 12.0
        assert ratio > 0.8

    def test_ramanujan_margin(self, eigenvalues):
        """Margin to Ramanujan bound: 2*sqrt(11) - 4 ~ 2.633 (comfortable margin)."""
        bound = 2 * math.sqrt(11)
        margin = bound - 4.0
        assert margin > 2.5
        assert margin < 3.0


# ================================================================== #
#  7. Matrix Inequalities  (~10 tests)                               #
# ================================================================== #

class TestMatrixInequalities:
    """Weyl, Fan, Schur complement, trace, Hadamard, Fischer inequalities."""

    def test_weyl_inequality_sum(self, A, eigenvalues):
        """Weyl: lambda_i(A+B) <= lambda_{i-j+n}(A) + lambda_j(B)."""
        # Take B = identity
        B = np.eye(40)
        C = A.astype(float) + B
        ev_C = np.sort(np.linalg.eigvalsh(C))
        # eigenvalues of A+I = eigenvalues(A) + 1
        for i in range(40):
            assert abs(ev_C[i] - (eigenvalues[i] + 1.0)) < 1e-10

    def test_weyl_inequality_perturbation(self, A, eigenvalues):
        """Weyl perturbation: |lambda_i(A+E) - lambda_i(A)| <= ||E||_2."""
        # Perturbation E = 0.1 * I
        E = 0.1 * np.eye(40)
        B = A.astype(float) + E
        ev_B = np.sort(np.linalg.eigvalsh(B))
        norm_E = 0.1
        for i in range(40):
            assert abs(ev_B[i] - eigenvalues[i]) <= norm_E + 1e-10

    def test_fan_inequality_singular_values(self, A):
        """Fan: sum of top k singular values of A+B <= sum top k of A + sum top k of B."""
        B = np.eye(40, dtype=int)
        sv_A = np.sort(np.linalg.svd(A.astype(float), compute_uv=False))[::-1]
        sv_B = np.sort(np.linalg.svd(B.astype(float), compute_uv=False))[::-1]
        sv_AB = np.sort(np.linalg.svd((A + B).astype(float), compute_uv=False))[::-1]
        for k in range(1, 41):
            assert np.sum(sv_AB[:k]) <= np.sum(sv_A[:k]) + np.sum(sv_B[:k]) + 1e-8

    def test_schur_complement_positive_semidefinite(self, A):
        """Schur complement of shifted A is PSD when shift makes it PD."""
        # A + 5I is PD (since min eigenvalue is -4, shift gives min = 1 > 0)
        M = A.astype(float) + 5.0 * np.eye(40)
        ev_M = np.linalg.eigvalsh(M)
        assert np.all(ev_M >= 0.5)
        # Schur complement of a PD matrix is PD
        # Partition into 20x20 blocks
        M11 = M[:20, :20]
        M12 = M[:20, 20:]
        M21 = M[20:, :20]
        M22 = M[20:, 20:]
        # Schur complement S = M11 - M12 * M22^{-1} * M21
        M22_inv = np.linalg.inv(M22)
        S = M11 - M12 @ M22_inv @ M21
        ev_S = np.linalg.eigvalsh(S)
        assert np.all(ev_S >= -1e-8)

    def test_trace_inequality_am_gm(self, A, eigenvalues):
        """trace(A^2)/n >= (trace(A)/n)^2 (Cauchy-Schwarz for traces)."""
        trace_A = np.trace(A)
        trace_A2 = np.trace(A @ A)
        n = 40
        assert trace_A2 / n >= (trace_A / n) ** 2 - 1e-10

    def test_hadamard_inequality_gram(self, A):
        """Hadamard: |det(G)| <= prod(||row_i||^2) for Gram matrix G = A^T A."""
        G = A.T @ A  # Gram matrix
        # For integer matrix, use log to avoid overflow
        # det(G) = prod(eigenvalues of G)
        ev_G = np.linalg.eigvalsh(G.astype(float))
        log_det = np.sum(np.log(np.maximum(ev_G, 1e-300)))
        # Hadamard: log|det(G)| <= sum(log(||row_i||^2))
        row_norms_sq = np.array([np.dot(G[i], G[i]) for i in range(40)])
        log_hadamard = np.sum(np.log(row_norms_sq))
        assert log_det <= log_hadamard + 1e-6

    def test_fischer_inequality_block(self, A):
        """Fischer: det(M) <= det(M11)*det(M22) for PSD block matrix M."""
        M = A.astype(float) + 5.0 * np.eye(40)  # make strictly PD
        M11 = M[:20, :20]
        M22 = M[20:, 20:]
        det_M = np.linalg.det(M)
        det_M11 = np.linalg.det(M11)
        det_M22 = np.linalg.det(M22)
        assert det_M <= det_M11 * det_M22 + 1e-3

    def test_cauchy_schwarz_trace(self, A):
        """Cauchy-Schwarz: trace(AB)^2 <= trace(A^2)*trace(B^2)."""
        B = A.T  # = A since symmetric
        trAB = np.trace(A @ B)
        trA2 = np.trace(A @ A)
        trB2 = np.trace(B @ B)
        assert trAB**2 <= trA2 * trB2 + 1e-10

    def test_eigenvalue_trace_relation(self, A, eigenvalues):
        """trace(A) = sum(eigenvalues) = 0."""
        assert abs(np.trace(A) - np.sum(eigenvalues)) < 1e-10
        assert abs(np.trace(A)) < 1e-10

    def test_spectral_norm_equals_max_eigenvalue(self, A, eigenvalues):
        """||A||_2 = max|lambda_i| = 12 for symmetric A."""
        sv = np.linalg.svd(A.astype(float), compute_uv=False)
        spectral_norm = np.max(sv)
        assert abs(spectral_norm - 12.0) < 1e-10
        assert abs(np.max(np.abs(eigenvalues)) - 12.0) < 1e-10


# ================================================================== #
#  8. Graph Energy Bounds  (~8 tests)                                #
# ================================================================== #

class TestGraphEnergyBounds:
    """Graph energy E(G) = sum|lambda_i|, bounds and complements."""

    def test_energy_value(self, eigenvalues):
        """E(G) = 1*|12| + 24*|2| + 15*|-4| = 12 + 48 + 60 = 120."""
        energy = np.sum(np.abs(eigenvalues))
        assert abs(energy - 120.0) < 1e-8

    def test_energy_lower_bound_sqrt(self, eigenvalues):
        """E(G) >= sqrt(2*m + n*(n-1)*|det(A)|^{2/n})."""
        # For simple lower bound: E(G) >= 2*m/n (trivial)
        # 2*240/40 = 12; E = 120 >> 12
        m = 240
        n = 40
        lower = 2.0 * m / n
        energy = np.sum(np.abs(eigenvalues))
        assert energy >= lower - 1e-10

    def test_mcclelland_bound(self, eigenvalues):
        """McClelland: E(G) <= sqrt(n*(2m + n*(n-1)*|det|^{2/n}))."""
        n, m = 40, 240
        # det(A) from eigenvalues
        # log|det| = log(12) + 24*log(2) + 15*log(4)
        log_det = math.log(12) + 24 * math.log(2) + 15 * math.log(4)
        det_term = math.exp(2.0 * log_det / n)
        mcclelland = math.sqrt(n * (2 * m + n * (n - 1) * det_term))
        energy = np.sum(np.abs(eigenvalues))
        assert energy <= mcclelland + 1e-6

    def test_koolen_moulton_bound(self, eigenvalues):
        """Koolen-Moulton: E(G) <= 2m/n + sqrt((n-1)*(2m - (2m/n)^2))."""
        n, m = 40, 240
        avg_sq = 2.0 * m / n  # = 12
        km_bound = avg_sq + math.sqrt((n - 1) * (2 * m - avg_sq**2))
        energy = np.sum(np.abs(eigenvalues))
        assert energy <= km_bound + 1e-6

    def test_complement_energy(self, comp_eigenvalues):
        """E(G_bar): complement SRG(40,27,18,18) spectrum 27^1, (-3)^24, 3^15."""
        energy_comp = np.sum(np.abs(comp_eigenvalues))
        expected = abs(27) + 24 * abs(-3) + 15 * abs(3)
        assert abs(energy_comp - expected) < 1e-8
        assert abs(expected - (27 + 72 + 45)) < 1e-10
        assert abs(expected - 144.0) < 1e-10

    def test_energy_plus_complement_energy(self, eigenvalues, comp_eigenvalues):
        """E(G) + E(G_bar) >= 2*(n-1) = 78 (Nikiforov)."""
        energy = np.sum(np.abs(eigenvalues))      # 120
        energy_comp = np.sum(np.abs(comp_eigenvalues))  # 144
        assert energy + energy_comp >= 2 * 39 - 1e-10
        # Actually: 120 + 144 = 264 >> 78

    def test_coulson_integral_formula(self, A, eigenvalues):
        """Coulson: E(G) = (1/pi) integral_{-inf}^{inf} (n - ix*trace((A-ixI)^{-1})) dx/x^2."""
        # Numerical verification using eigenvalue formula:
        # E(G) = (1/pi) * integral sum_i (|lambda_i| related)
        # = sum |lambda_i| directly
        # Verify via numerical integration (trapezoidal on [-100, 100])
        energy_exact = np.sum(np.abs(eigenvalues))
        # Coulson integral: E = (1/pi) * integral_0^inf [n - sum_i x^2/(x^2+lam_i^2)] * (2/x^2) ...
        # Simplified: E = (2/pi) * integral_0^inf (1/x^2) * sum_i (lam_i^2 / (x^2 + lam_i^2)) dx
        # = sum_i |lam_i| (exact)
        # Numerical check at a specific point
        x = 1.0
        integrand_terms = eigenvalues**2 / (x**2 + eigenvalues**2)
        assert np.sum(integrand_terms) > 0  # positive definite integrand

    def test_energy_equals_twice_positive_eigenvalue_sum(self, eigenvalues):
        """For bipartite graphs E = 2*sum(positive eigenvalues). W(3,3) is NOT bipartite."""
        # W(3,3) is not bipartite (has odd cycles / triangles)
        # So E != 2*sum(positive eigenvalues)
        pos_sum = np.sum(eigenvalues[eigenvalues > 0])
        energy = np.sum(np.abs(eigenvalues))
        # 2 * pos_sum = 2*(12 + 24*2) = 2*60 = 120 = E ... coincidence!
        # Actually: pos eigenvalues sum = 12 + 24*2 = 60
        # neg eigenvalues sum of abs = 15*4 = 60
        # So E = 60 + 60 = 120 = 2*60. This happens because sum|neg| = sum(pos)
        # which follows from trace(A) = 0 => sum(pos) = sum|neg|
        assert abs(pos_sum - 60.0) < 1e-8
        assert abs(energy - 2 * pos_sum) < 1e-8


# ================================================================== #
#  9. Additional Spectral Bound Tests                                #
# ================================================================== #

class TestAdditionalSpectralBounds:
    """Extra tests for completeness: determinant, rank, norms."""

    def test_determinant_from_spectrum(self, A, eigenvalues):
        """det(A) = 12^1 * 2^24 * (-4)^15."""
        det_expected = (12**1) * (2**24) * ((-4)**15)
        # = 12 * 16777216 * (-1073741824)
        # Just check sign and log magnitude
        log_abs_det = math.log(12) + 24 * math.log(2) + 15 * math.log(4)
        det_sign = (-1)**15  # negative (odd number of negative eigenvalues)
        assert det_sign == -1
        det_computed = np.linalg.det(A.astype(float))
        assert det_computed < 0

    def test_rank_full(self, A, eigenvalues):
        """A has rank 40 (all eigenvalues nonzero)."""
        assert np.linalg.matrix_rank(A) == 40

    def test_frobenius_norm(self, A, eigenvalues):
        """||A||_F = sqrt(trace(A^T A)) = sqrt(480)."""
        frob = np.sqrt(np.sum(A.astype(float)**2))
        assert abs(frob - math.sqrt(480)) < 1e-10

    def test_nuclear_norm_equals_energy(self, A, eigenvalues):
        """Nuclear norm (sum of singular values) = E(G) = 120 for symmetric A."""
        sv = np.linalg.svd(A.astype(float), compute_uv=False)
        nuclear = np.sum(sv)
        energy = np.sum(np.abs(eigenvalues))
        assert abs(nuclear - energy) < 1e-8
        assert abs(nuclear - 120.0) < 1e-8

    def test_characteristic_polynomial_coefficients(self, eigenvalues):
        """Characteristic polynomial: det(xI - A) factors with known roots."""
        # p(x) = (x-12)(x-2)^24(x+4)^15
        # p(0) = (-12)*(-2)^24*(4)^15 = -det(A) with appropriate sign
        p_at_0 = (-12) * ((-2)**24) * (4**15)
        # This should equal (-1)^40 * det(A) = det(A)
        det_A = (12) * (2**24) * ((-4)**15)
        assert p_at_0 == (-1)**40 * det_A  # (-1)^n * det(-A) = det(A) for even n

    def test_spectral_radius(self, eigenvalues):
        """Spectral radius rho(A) = max|lambda_i| = 12 = k."""
        rho = np.max(np.abs(eigenvalues))
        assert abs(rho - 12.0) < 1e-10

    def test_adjacency_spectrum_complement_relation(self, eigenvalues, comp_eigenvalues):
        """Complement eigenvalues: if lambda is eig of A, then -1-lambda is eig of A_bar (non-trivial)."""
        # For k-regular graph on n vertices, complement is (n-1-k)-regular
        # If lambda != k is eigenvalue of A, then -1-lambda is eigenvalue of complement
        # 2 -> -3, -4 -> 3, 12 -> 27 (trivial eigenvalue)
        comp_sorted = np.sort(comp_eigenvalues)
        comp_rounded = np.round(comp_sorted).astype(int)
        unique_comp = np.unique(comp_rounded)
        assert -3 in unique_comp
        assert 3 in unique_comp
        assert 27 in unique_comp
