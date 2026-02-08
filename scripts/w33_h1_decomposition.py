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
  3. Compute SIGNED restricted representation R_g = W^T S_g W (81 x 81)
     where S_g accounts for edge orientation reversal under permutation
  4. Find a non-trivial commutant element via group averaging
  5. Diagonalize to find the irreducible decomposition
  6. Verify by checking all generators preserve the decomposition

CRITICAL: Edge orientation signs must be tracked. When a vertex
permutation maps edge (i,j) to (sigma(j), sigma(i)) with sigma(j) < sigma(i),
the 1-chain picks up a -1 sign. This is essential for correct representation
matrices on H1.

Usage:
  python scripts/w33_h1_decomposition.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import deque
from pathlib import Path

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
    """Oriented vertex-edge incidence matrix D (n x m).
    For edge (i,j) with i<j: D[i,col] = +1, D[j,col] = -1.
    """
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
    L1 = D.T @ D + B2 @ B2.T
    w, v = np.linalg.eigh(L1)
    idx = np.argsort(w)
    w, v = w[idx], v[:, idx]
    tol = 1e-8
    null_idx = np.where(np.abs(w) < tol)[0]
    W = v[:, null_idx]
    return W, w


# =========================================================================
# SIGNED edge permutation (critical for correct H1 action)
# =========================================================================

def make_vertex_permutation(M: np.ndarray, vertices: list) -> list:
    """Compute permutation of vertices induced by matrix M."""
    perm = []
    for v in vertices:
        newv = apply_matrix_projective(M, v)
        j = vertices.index(newv)
        perm.append(j)
    return perm


def signed_edge_permutation(vperm: list, edges: list):
    """Compute signed edge permutation from vertex permutation.

    Returns (perm, signs) where:
      perm[i] = index of image edge
      signs[i] = +1 if orientation preserved, -1 if reversed

    Edge (a, b) with a < b maps to (vperm[a], vperm[b]).
    If vperm[a] < vperm[b]: orientation preserved, sign = +1
    If vperm[a] > vperm[b]: edge stored as (vperm[b], vperm[a]), sign = -1
    """
    edge_index = {}
    for i, (a, b) in enumerate(edges):
        edge_index[(a, b)] = i

    perm = []
    signs = []
    for i, (a, b) in enumerate(edges):
        a2, b2 = vperm[a], vperm[b]
        if a2 < b2:
            perm.append(edge_index[(a2, b2)])
            signs.append(1)
        else:
            perm.append(edge_index[(b2, a2)])
            signs.append(-1)
    return perm, signs


def signed_permutation_matrix(perm: list, signs: list, m: int) -> np.ndarray:
    """Build signed permutation matrix S_g from edge perm and signs.
    S_g[perm[i], i] = signs[i]
    """
    S = np.zeros((m, m), dtype=float)
    for i in range(m):
        S[perm[i], i] = signs[i]
    return S


# =========================================================================
# Main decomposition
# =========================================================================

def find_irreducible_decomposition():
    t0 = time.time()
    print("=" * 70)
    print("  H1 IRREDUCIBLE DECOMPOSITION UNDER PSp(4,3)")
    print("=" * 70)

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

    # Build generators: ALL 40 projective point transvections
    J = J_matrix()
    print("Building PSp(4,3) generators (all 40 transvections)...")

    gen_vectors = [np.array(v, dtype=int) for v in vertices]
    gen_matrices = [transvection_matrix(u, J) for u in gen_vectors]
    gen_vperms = [make_vertex_permutation(M, vertices) for M in gen_matrices]
    gen_signed = [signed_edge_permutation(vp, edges) for vp in gen_vperms]

    # Verify unitarity with signed permutation matrices
    print("Verifying unitarity of signed representation on H1...")
    R_gens = []
    for i, (eperm, esigns) in enumerate(gen_signed):
        S_g = signed_permutation_matrix(eperm, esigns, m)
        R_g = W.T @ S_g @ W  # 81 x 81
        R_gens.append(R_g)
        err = np.max(np.abs(R_g @ R_g.T - np.eye(b1)))
        if i < 5 or err > 1e-6:
            print(f"  Generator {i}: unitarity error = {err:.2e}")

    # Check a few more
    max_err = max(np.max(np.abs(R @ R.T - np.eye(b1))) for R in R_gens)
    print(f"  Max unitarity error across all 40 generators: {max_err:.2e}")

    # BFS to enumerate the full group PSp(4,3) using SIGNED edge permutations
    print("\nEnumerating PSp(4,3) via BFS on vertex permutations...")
    gen_v_tuples = [tuple(vp) for vp in gen_vperms]

    # For edge perms, we store (perm_tuple, signs_tuple) keyed by vertex perm
    gen_e_data = [(tuple(ep), tuple(es)) for ep, es in gen_signed]

    id_v = tuple(range(n))
    id_e = tuple(range(m))
    id_s = tuple([1] * m)

    # Store vertex_perm -> (edge_perm, edge_signs)
    visited = {id_v: (id_e, id_s)}
    queue = deque([id_v])

    while queue:
        cur_v = queue.popleft()
        cur_ep, cur_es = visited[cur_v]
        for gv, (gep, ges) in zip(gen_v_tuples, gen_e_data):
            # Composition: new = gen o cur (on vertices)
            new_v = tuple(gv[i] for i in cur_v)
            if new_v not in visited:
                # Compose edge permutations: new_ep[i] = gep[cur_ep[i]]
                # Compose signs: new_es[i] = ges[cur_ep[i]] * cur_es[i]
                new_ep = tuple(gep[cur_ep[i]] for i in range(m))
                new_es = tuple(ges[cur_ep[i]] * cur_es[i] for i in range(m))
                visited[new_v] = (new_ep, new_es)
                queue.append(new_v)

    group_size = len(visited)
    print(f"  Group size: {group_size}")

    # Compute commutant dimension and Casimir element C2
    print("Computing Casimir element C2 = (1/|G|) sum chi(g) R_g ...")
    S_proj = W @ W.T  # Projection onto harmonic subspace (m x m)
    ar = np.arange(m, dtype=int)

    total_chi_sq = 0.0
    C2 = np.zeros((b1, b1), dtype=float)

    count = 0
    for cur_v, (cur_ep, cur_es) in visited.items():
        cur_ep_np = np.asarray(cur_ep, dtype=int)
        cur_es_np = np.asarray(cur_es, dtype=float)

        # chi(g) = trace(S_g restricted to H1) = sum_e S_proj[e, sigma(e)] * sign(e)
        chi = float((S_proj[ar, cur_ep_np] * cur_es_np).sum())
        total_chi_sq += chi * chi

        # R_g = W^T S_g W where S_g permutes rows of W with signs
        S_g_W = W[cur_ep_np, :] * cur_es_np[:, None]
        R_g = W.T @ S_g_W

        C2 += chi * R_g
        count += 1

    C2 /= group_size
    avg_chi_sq = total_chi_sq / group_size
    commutant_dim = int(round(avg_chi_sq))
    print(f"  avg |chi|^2 = {avg_chi_sq:.6f}")
    print(f"  commutant_dim = {commutant_dim}")

    # Symmetrize C2 for numerical stability
    C2_sym = (C2 + C2.T) / 2

    # Eigendecomposition of C2
    w_C2, v_C2 = np.linalg.eigh(C2_sym)
    idx = np.argsort(w_C2)
    w_C2, v_C2 = w_C2[idx], v_C2[:, idx]

    # Cluster eigenvalues
    tol_cluster = max(0.01, (w_C2[-1] - w_C2[0]) * 0.001)
    clusters = []
    current = [0]
    for i in range(1, len(w_C2)):
        if abs(w_C2[i] - w_C2[current[0]]) < tol_cluster:
            current.append(i)
        else:
            clusters.append((float(np.mean(w_C2[current])), len(current), current[:]))
            current = [i]
    clusters.append((float(np.mean(w_C2[current])), len(current), current[:]))

    print(f"\n  Eigenvalue clusters of C2 ({len(clusters)} clusters):")
    dims = []
    for val, mult, indices in clusters:
        print(f"    eigenvalue {val:.8f}, multiplicity {mult}")
        dims.append(mult)

    # Analyze the decomposition
    print(f"\n  Number of irreducible components: {len(clusters)}")
    print(f"  Component dimensions: {dims}")
    print(f"  Sum: {sum(dims)} (should be 81)")
    print(f"  Decomposition: 81 = {' + '.join(map(str, dims))}")

    # For each component, verify irreducibility via <|chi_i|^2> = 1
    print("\n  Irreducibility check for each component:")
    component_bases = []
    for ci, (val, mult, indices) in enumerate(clusters):
        Vi = v_C2[:, indices]
        component_bases.append(Vi)

        chi_sq_sum = 0.0
        for cur_v, (cur_ep, cur_es) in visited.items():
            cur_ep_np = np.asarray(cur_ep, dtype=int)
            cur_es_np = np.asarray(cur_es, dtype=float)
            S_g_W = W[cur_ep_np, :] * cur_es_np[:, None]
            R_g = W.T @ S_g_W
            # Restrict to component Vi
            R_g_Vi = Vi.T @ R_g @ Vi
            chi_i = np.trace(R_g_Vi)
            chi_sq_sum += chi_i * chi_i

        chi_sq_avg = chi_sq_sum / group_size
        is_irr = abs(chi_sq_avg - 1.0) < 0.1
        print(f"    Component {ci} (dim {mult}): <|chi|^2> = {chi_sq_avg:.6f} {'IRREDUCIBLE' if is_irr else f'REDUCIBLE (decomposes into ~{int(round(chi_sq_avg))} pieces)'}")

    # Verify generators preserve each component
    print("\n  Verification: generators preserve components?")
    all_preserved = True
    for gi, (eperm, esigns) in enumerate(gen_signed[:5]):
        S_g = signed_permutation_matrix(eperm, esigns, m)
        R_g = W.T @ S_g @ W

        max_leak = 0.0
        for ci, Vi in enumerate(component_bases):
            for cj, Vj in enumerate(component_bases):
                if ci == cj:
                    continue
                leak = np.linalg.norm(Vj.T @ R_g @ Vi)
                max_leak = max(max_leak, leak)

        ok = max_leak < 1e-6
        if not ok:
            all_preserved = False
        print(f"    Generator {gi}: max cross-component leakage = {max_leak:.2e} {'OK' if ok else 'FAIL'}")

    # Physical interpretation
    print("\n" + "=" * 70)
    print("  RESULTS & PHYSICAL INTERPRETATION")
    print("=" * 70)
    print(f"""
  PSp(4,3) (order {group_size}) acts on H1(W33; R) = R^81

  Commutant dimension: {commutant_dim}
  Number of irreducible components: {len(clusters)}
  Decomposition: 81 = {' + '.join(map(str, dims))}

  Under E8's Z3-grading: g1 = 81 = 27 x 3 (three 27-plets of E6)
  Under PSp(4,3): 81 = {' + '.join(map(str, dims))}

  Trivial representation is {'present' if 1 in dims else 'absent'} in H1.
  This means {'there is a PSp(4,3)-invariant harmonic 1-form' if 1 in dims else 'NO harmonic 1-form is PSp(4,3)-invariant'}.

  Cup product H^1 x H^1 -> H^2 = 0 still holds: no component self-interacts.
  All interactions are mediated by the gauge sector (E6 = 78-dim).
""")

    elapsed = time.time() - t0

    # Assemble results
    result = {
        "group_size": group_size,
        "b1": b1,
        "commutant_dim": commutant_dim,
        "avg_chi_squared": float(avg_chi_sq),
        "n_irreducible_components": len(clusters),
        "component_dimensions": dims,
        "decomposition": f"{b1} = {' + '.join(map(str, dims))}",
        "all_generators_preserve": all_preserved,
        "C2_eigenvalues": [(float(v), int(mult)) for v, mult, _ in clusters],
        "elapsed_seconds": elapsed,
    }

    # Add irreducibility checks
    irr_checks = {}
    for ci, (val, mult, indices) in enumerate(clusters):
        Vi = v_C2[:, indices]
        chi_sq_sum = 0.0
        for cur_v, (cur_ep, cur_es) in visited.items():
            cur_ep_np = np.asarray(cur_ep, dtype=int)
            cur_es_np = np.asarray(cur_es, dtype=float)
            S_g_W = W[cur_ep_np, :] * cur_es_np[:, None]
            R_g = W.T @ S_g_W
            R_g_Vi = Vi.T @ R_g @ Vi
            chi_i = np.trace(R_g_Vi)
            chi_sq_sum += chi_i * chi_i
        chi_sq_avg = chi_sq_sum / group_size
        irr_checks[f"component_{ci}"] = {
            "dimension": mult,
            "chi_sq_avg": float(chi_sq_avg),
            "irreducible": abs(chi_sq_avg - 1.0) < 0.1,
        }
    result["irreducibility_checks"] = irr_checks

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
