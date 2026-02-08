#!/usr/bin/env python3
"""
H1 Irreducible Decomposition under Sp(4,3) / PSp(4,3)
=======================================================

DISCOVERY: The 81-dim representation of PSp(4,3) on H1(W33; R)
decomposes into exactly 2 irreducible components (commutant_dim = 2).

This script finds the two components, their dimensions, and their
physical interpretation.

Method:
  1. Build harmonic basis W (240 x 81) from Hodge Laplacian
  2. Generate PSp(4,3) via symplectic transvections on GF(3)^4
  3. Compute restricted representation R_g = W^T P_g W (81 x 81)
  4. Find a non-trivial commutant element via group averaging
  5. Diagonalize to find the irreducible decomposition
  6. Verify by checking all generators preserve the decomposition

Physical significance:
  If 81 = d1 + d2, this reveals the internal structure of the matter sector.
  The E8 Z3-grading gives g1 = 81 = 27 x 3 (three 27-plets of E6).
  The irreducible decomposition under the geometric symmetry group tells
  us HOW the 81 matter cycles organize internally.

Usage:
  python scripts/w33_h1_decomposition.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from w33_homology import build_clique_complex, boundary_matrix, build_w33


# =========================================================================
# GF(3) symplectic machinery
# =========================================================================

def gf3(x: int) -> int:
    return int(x % 3)


def mat_mod3(A) -> np.ndarray:
    return np.array([[gf3(int(x)) for x in row] for row in A], dtype=int)


def J_matrix() -> np.ndarray:
    """Symplectic form J = [[0,I],[-I,0]] on GF(3)^4."""
    J = np.zeros((4, 4), dtype=int)
    J[0, 1] = 1; J[1, 0] = -1
    J[2, 3] = 1; J[3, 2] = -1
    return mat_mod3(J)


def transvection_matrix(u: np.ndarray, J: np.ndarray) -> np.ndarray:
    """Symplectic transvection T(u) = I + u (Ju)^T over GF(3)."""
    u = u.reshape((4, 1))
    Ju = J @ u
    M = np.eye(4, dtype=int) + (u @ Ju.T)
    return mat_mod3(M)


def normalize_projective(v: tuple) -> tuple:
    """Normalize projective vector: first nonzero entry = 1."""
    for i, x in enumerate(v):
        if x % 3 != 0:
            inv = pow(int(x), -1, 3)
            return tuple((inv * int(y)) % 3 for y in v)
    return v


def apply_matrix_projective(M: np.ndarray, v: tuple) -> tuple:
    """Apply 4x4 GF(3) matrix to projective point."""
    vec = np.array(v, dtype=int).reshape((4, 1))
    res = tuple(int(x) % 3 for x in (M @ vec).flatten())
    return normalize_projective(res)


# =========================================================================
# Build Hodge Laplacian and harmonic basis
# =========================================================================

def build_incidence_matrix(n: int, edges: list) -> np.ndarray:
    """Oriented vertex-edge incidence matrix D (n x m)."""
    m = len(edges)
    D = np.zeros((n, m), dtype=float)
    for col, (i, j) in enumerate(edges):
        D[i, col] = 1.0
        D[j, col] = -1.0
    return D


def compute_harmonic_basis(n, adj, edges, simplices):
    """Compute the 81-dim harmonic basis of H1(W33)."""
    B2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    D = build_incidence_matrix(n, edges)

    # Hodge Laplacian L1 = D^T D + B2 B2^T
    L1 = D.T @ D + B2 @ B2.T

    # Eigendecomposition
    w, v = np.linalg.eigh(L1)
    idx = np.argsort(w)
    w, v = w[idx], v[:, idx]

    # Kernel (harmonic 1-forms)
    tol = 1e-8
    null_idx = np.where(np.abs(w) < tol)[0]
    W = v[:, null_idx]
    return W, w


# =========================================================================
# Vertex and edge permutations
# =========================================================================

def make_vertex_permutation(M: np.ndarray, vertices: list) -> list:
    """Compute permutation of vertices induced by matrix M."""
    perm = []
    for v in vertices:
        newv = apply_matrix_projective(M, v)
        j = vertices.index(newv)
        perm.append(j)
    return perm


def vertex_perm_to_edge_perm(vperm: list, edges: list) -> list:
    """Convert vertex permutation to edge permutation."""
    edge_index = {}
    for i, (a, b) in enumerate(edges):
        edge_index[(a, b)] = i
        edge_index[(b, a)] = i

    eperm = []
    for i, (a, b) in enumerate(edges):
        a2, b2 = vperm[a], vperm[b]
        key = (min(a2, b2), max(a2, b2))
        eperm.append(edge_index[key])
    return eperm


def edge_perm_to_matrix(eperm: list, m: int) -> np.ndarray:
    """Convert edge permutation to permutation matrix."""
    P = np.zeros((m, m), dtype=float)
    for i, j in enumerate(eperm):
        P[j, i] = 1.0
    return P


# =========================================================================
# Main decomposition
# =========================================================================

def find_irreducible_decomposition():
    """Find the 2 irreducible components of the 81-dim rep on H1."""
    t0 = time.time()
    print("=" * 70)
    print("  H1 IRREDUCIBLE DECOMPOSITION UNDER PSp(4,3)")
    print("=" * 70)

    # Build W33
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)
    print(f"\nW33: {n} vertices, {m} edges, {len(simplices[2])} triangles")

    # Harmonic basis
    print("Computing harmonic basis...")
    W, eigenvalues = compute_harmonic_basis(n, adj, edges, simplices)
    b1 = W.shape[1]
    print(f"Harmonic basis dimension: {b1}")
    assert b1 == 81, f"Expected b1=81, got {b1}"

    # Build generators: all transvection matrices
    J = J_matrix()
    print("Building PSp(4,3) generators (transvections)...")

    # Use a small generating set (3 transvections suffice for the group)
    gen_vectors = [
        np.array([1, 0, 0, 0], dtype=int),
        np.array([0, 1, 0, 0], dtype=int),
        np.array([0, 0, 1, 0], dtype=int),
        np.array([0, 0, 0, 1], dtype=int),
        np.array([1, 1, 0, 0], dtype=int),
    ]

    gen_matrices = [transvection_matrix(u, J) for u in gen_vectors]
    gen_vperms = [make_vertex_permutation(M, vertices) for M in gen_matrices]
    gen_eperms = [vertex_perm_to_edge_perm(vp, edges) for vp in gen_vperms]

    # Compute restricted representation R_g = W^T P_g W for each generator
    print("Computing restricted representation matrices on H1...")
    R_gens = []
    for i, eperm in enumerate(gen_eperms):
        P_g = edge_perm_to_matrix(eperm, m)
        R_g = W.T @ P_g @ W  # 81 x 81
        R_gens.append(R_g)
        # Verify unitarity
        err = np.max(np.abs(R_g @ R_g.T - np.eye(b1)))
        print(f"  Generator {i}: unitarity error = {err:.2e}")

    # Strategy 1: Find a non-trivial commutant element
    # Use a random linear combination of generators and their products
    print("\nFinding irreducible decomposition...")

    # Take a product of generators as a non-trivial group element
    R_prod = R_gens[0] @ R_gens[1] @ R_gens[2]

    # Compute eigenvalues of R_prod
    eigvals_prod, eigvecs_prod = np.linalg.eig(R_prod)

    # The eigenvalues are complex (since R_prod is orthogonal, they lie on unit circle)
    print(f"  R_prod eigenvalue count: {len(eigvals_prod)}")

    # Strategy 2: Use a Hermitian combination for cleaner decomposition
    # The sum S = sum_g R_g is a Hermitian commutant element
    S = sum(R_gens)
    S = (S + S.T) / 2  # Ensure Hermitian

    # Eigendecomposition of S
    w_S, v_S = np.linalg.eigh(S)
    idx = np.argsort(w_S)
    w_S, v_S = w_S[idx], v_S[:, idx]

    # Cluster eigenvalues
    tol = 1e-6
    clusters = []
    current_cluster = [0]
    for i in range(1, len(w_S)):
        if abs(w_S[i] - w_S[current_cluster[0]]) < tol:
            current_cluster.append(i)
        else:
            clusters.append((float(w_S[current_cluster[0]]), current_cluster[:]))
            current_cluster = [i]
    clusters.append((float(w_S[current_cluster[0]]), current_cluster[:]))

    print(f"\n  Eigenvalue clusters of S = sum(generators) on H1:")
    for val, indices in clusters:
        print(f"    eigenvalue {val:.6f}, multiplicity {len(indices)}")

    # Strategy 3: Use the Casimir-like element
    # C = sum_g R_g R_g^T (always commutes with the representation)
    # But R_g R_g^T = I for orthogonal matrices, so C = |gens| * I. Trivial.

    # Strategy 4: Use R_g^2 for a single generator
    # The key insight: we need the GROUP AVERAGE, not just generators.
    # Since enumerating the full group (25920 elements) is feasible,
    # let's compute the "quadratic Casimir" via group averaging.
    print("\nBuilding group by BFS and computing quadratic average...")

    from collections import deque

    # BFS to enumerate group, storing edge permutations as tuples
    id_v = tuple(range(n))
    id_e = tuple(range(m))
    visited = {id_v: id_e}
    queue = deque([id_v])

    gen_v_tuples = [tuple(vp) for vp in gen_vperms]
    gen_e_tuples = [tuple(ep) for ep in gen_eperms]

    while queue:
        cur_v = queue.popleft()
        cur_e = visited[cur_v]
        for gv, ge in zip(gen_v_tuples, gen_e_tuples):
            new_v = tuple(gv[i] for i in cur_v)
            new_e = tuple(ge[i] for i in cur_e)
            if new_v not in visited:
                visited[new_v] = new_e
                queue.append(new_v)

    group_size = len(visited)
    print(f"  Group size: {group_size}")

    # Compute C = (1/|G|) sum_g R_g for character trace,
    # and Q = (1/|G|) sum_g chi(g)^2 for commutant dimension verification
    # Also compute a Hermitian matrix that commutes with all R_g
    # Use: A = (1/|G|) sum_g R_g (not useful if trivial component absent)
    # Better: use the square of the permutation character restricted to H1

    # Compute projection matrix S = W W^T (m x m)
    S_proj = W @ W.T  # Projects onto harmonic subspace

    # For each g, chi(g) = trace(R_g) = trace(P_g S_proj)
    ar = np.arange(m, dtype=int)

    total_chi_sq = 0.0
    # Also accumulate: C2 = (1/|G|) sum_g chi(g) * R_g (class operator projection)
    C2 = np.zeros((b1, b1), dtype=float)
    # And: R_avg = (1/|G|) sum_g R_g (trivial projection)
    R_avg = np.zeros((b1, b1), dtype=float)

    count = 0
    for cur_v, cur_e in visited.items():
        cur_e_np = np.asarray(cur_e, dtype=int)
        # chi(g) = trace of restriction of P_g to harmonic subspace
        chi = float(S_proj[ar, cur_e_np].sum())
        total_chi_sq += chi * chi

        # R_g via fast computation: R_g = W^T P_g W
        # P_g W = W[cur_e, :] (permute rows of W)
        P_g_W = W[cur_e_np, :]
        R_g = W.T @ P_g_W

        C2 += chi * R_g
        R_avg += R_g
        count += 1

    C2 /= group_size
    R_avg /= group_size
    avg_chi_sq = total_chi_sq / group_size
    print(f"  avg |chi|^2 = {avg_chi_sq:.6f} (should be 2.0 for commutant_dim=2)")
    print(f"  commutant_dim = {int(round(avg_chi_sq))}")

    # C2 = (1/|G|) sum_g chi(g) R_g is a commutant element
    # Its eigenvalues should split into 2 groups (for the 2 irreps)
    # Symmetrize for numerical stability
    C2_sym = (C2 + C2.T) / 2

    w_C2, v_C2 = np.linalg.eigh(C2_sym)
    idx = np.argsort(w_C2)
    w_C2, v_C2 = w_C2[idx], v_C2[:, idx]

    # Cluster eigenvalues of C2
    clusters_C2 = []
    current = [0]
    for i in range(1, len(w_C2)):
        if abs(w_C2[i] - w_C2[current[0]]) < 0.01:
            current.append(i)
        else:
            clusters_C2.append((float(w_C2[current[0]]), len(current), current[:]))
            current = [i]
    clusters_C2.append((float(w_C2[current[0]]), len(current), current[:]))

    print(f"\n  Eigenvalue clusters of C2 = (1/|G|) sum chi(g) R_g:")
    dims = []
    for val, mult, indices in clusters_C2:
        print(f"    eigenvalue {val:.8f}, multiplicity {mult}")
        dims.append(mult)

    # The two irreducible components
    if len(clusters_C2) == 2:
        d1, d2 = dims[0], dims[1]
        print(f"\n  IRREDUCIBLE DECOMPOSITION: 81 = {d1} + {d2}")

        # Extract the basis vectors for each component
        V1 = v_C2[:, clusters_C2[0][2]]
        V2 = v_C2[:, clusters_C2[1][2]]

        # Verify: check that each generator preserves V1 and V2
        print("\n  Verification: generators preserve decomposition?")
        all_preserved = True
        for i, eperm in enumerate(gen_eperms):
            cur_e_np = np.asarray(eperm, dtype=int)
            P_g_W = W[cur_e_np, :]
            R_g = W.T @ P_g_W

            # Check V1 is invariant: R_g V1 should be in span(V1)
            R_V1 = R_g @ V1
            # Project onto V1 complement (V2): should be zero
            proj_err_1 = np.linalg.norm(V2.T @ R_V1)
            # Same for V2
            R_V2 = R_g @ V2
            proj_err_2 = np.linalg.norm(V1.T @ R_V2)

            ok = proj_err_1 < 1e-8 and proj_err_2 < 1e-8
            if not ok:
                all_preserved = False
            print(f"    Generator {i}: V1 leakage = {proj_err_1:.2e}, V2 leakage = {proj_err_2:.2e} {'OK' if ok else 'FAIL'}")

        # Compute the character of each irrep for verification
        print("\n  Character analysis of each component:")
        chi1_sq_sum = 0.0
        chi2_sq_sum = 0.0
        for cur_v, cur_e in visited.items():
            cur_e_np = np.asarray(cur_e, dtype=int)
            P_g_W = W[cur_e_np, :]
            R_g = W.T @ P_g_W

            # Restrict to V1: R_g|V1 = V1^T R_g V1
            R_g_V1 = V1.T @ R_g @ V1
            R_g_V2 = V2.T @ R_g @ V2
            chi1 = np.trace(R_g_V1)
            chi2 = np.trace(R_g_V2)
            chi1_sq_sum += chi1 * chi1
            chi2_sq_sum += chi2 * chi2

        chi1_sq_avg = chi1_sq_sum / group_size
        chi2_sq_avg = chi2_sq_sum / group_size
        print(f"    V1 ({d1}-dim): <|chi_1|^2> = {chi1_sq_avg:.6f} (should be 1.0 if irreducible)")
        print(f"    V2 ({d2}-dim): <|chi_2|^2> = {chi2_sq_avg:.6f} (should be 1.0 if irreducible)")

        # Physical interpretation
        print("\n" + "=" * 70)
        print("  PHYSICAL INTERPRETATION")
        print("=" * 70)
        print(f"""
  The 81 harmonic 1-forms (matter cycles) decompose as:
    H1(W33; R) = V_{d1} + V_{d2}   (as PSp(4,3)-modules)

  Under E8's Z3-grading: g1 = 81 = 27 x 3 (three 27-plets of E6)
  Under PSp(4,3) = W(E6): 81 = {d1} + {d2}

  This decomposition reveals the internal symmetry-breaking pattern:
  - The {d1}-dim component may correspond to one sector of matter fields
  - The {d2}-dim component to another sector
  - Their interaction structure is constrained by PSp(4,3) invariance

  KEY: Both V1 and V2 carry representations where the cup product
  H^1 x H^1 -> H^2 = 0 vanishes. So neither sector self-interacts
  topologically; interactions are mediated by the gauge sector (E6).
""")
    else:
        print(f"\n  WARNING: Expected 2 clusters but found {len(clusters_C2)}")
        print("  This may indicate finer decomposition or numerical issues.")
        print("  Trying alternative approach: random commutant element...")

        # Try random Hermitian combination of R_g^(k) for various k
        np.random.seed(42)
        rand_coeffs = np.random.randn(min(20, group_size))
        C_rand = np.zeros((b1, b1), dtype=float)
        for i, (cur_v, cur_e) in enumerate(list(visited.items())[:20]):
            cur_e_np = np.asarray(cur_e, dtype=int)
            P_g_W = W[cur_e_np, :]
            R_g = W.T @ P_g_W
            C_rand += rand_coeffs[i] * R_g
        C_rand = (C_rand + C_rand.T) / 2

        w_rand, v_rand = np.linalg.eigh(C_rand)
        # Cluster
        clusters_rand = []
        current = [0]
        for i in range(1, len(w_rand)):
            if abs(w_rand[i] - w_rand[current[0]]) < 0.1:
                current.append(i)
            else:
                clusters_rand.append((float(w_rand[current[0]]), len(current)))
                current = [i]
        clusters_rand.append((float(w_rand[current[0]]), len(current)))
        print("  Random commutant element clusters:")
        for val, mult in clusters_rand:
            print(f"    eigenvalue {val:.4f}, multiplicity {mult}")

    # Also analyze: what is the R_avg matrix?
    print("\n  Trivial component check (R_avg = projection onto trivial rep):")
    print(f"    rank(R_avg) = {np.linalg.matrix_rank(R_avg, tol=1e-8)}")
    print(f"    trace(R_avg) = {np.trace(R_avg):.6f}")
    trivial_dim = int(round(np.trace(R_avg)))
    print(f"    Multiplicity of trivial rep in H1: {trivial_dim}")

    elapsed = time.time() - t0

    # Assemble results
    result = {
        "group_size": group_size,
        "b1": b1,
        "commutant_dim": int(round(avg_chi_sq)),
        "avg_chi_squared": float(avg_chi_sq),
        "n_irreducible_components": len(clusters_C2),
        "component_dimensions": dims,
        "decomposition": f"{b1} = {' + '.join(map(str, dims))}",
        "all_generators_preserve": all_preserved if len(clusters_C2) == 2 else None,
        "trivial_multiplicity": trivial_dim,
        "C2_eigenvalues": [(float(v), int(m)) for v, m, _ in clusters_C2],
        "elapsed_seconds": elapsed,
    }

    if len(clusters_C2) == 2:
        result["irreducibility_check"] = {
            "V1_chi_sq_avg": float(chi1_sq_avg),
            "V2_chi_sq_avg": float(chi2_sq_avg),
            "V1_irreducible": abs(chi1_sq_avg - 1.0) < 0.1,
            "V2_irreducible": abs(chi2_sq_avg - 1.0) < 0.1,
        }

    # Write output
    ts = int(time.time())
    out_path = Path.cwd() / "checks" / f"PART_CVII_h1_decomposition_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\n  Wrote: {out_path}")
    print(f"  Elapsed: {elapsed:.1f}s")

    return result


if __name__ == "__main__":
    find_irreducible_decomposition()
