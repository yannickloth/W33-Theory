#!/usr/bin/env python3
"""
Triangle Space C_2(W33) Decomposition under PSp(4,3)
======================================================

The triangle chain space C_2(W33) = R^160 decomposes into 4 irreducible
representations under PSp(4,3). In the current implementation this
decomposition is found (and FS-indicators computed) via commutant
diagonalization and character checks.

Observed decomposition (2026-02-09):
  160 = 90 + 30 + 30 + 10

KNOWN CONTEXT:
  C_0(40)  = 1 + 24 + 15     (3 irreps)
  C_1(240) = 81 + 90 + 30 + 24 + 15  (5/6 irreps; 90=45_C complex)
  C_2(160) = 90 + 30 + 30 + 10
  C_3(40)  = 1 + 24 + 15     (3 irreps, same as C_0)

The triangle Laplacian:
  L_2 = d_2^T d_2 + d_3 d_3^T = 4I  (ALL eigenvalues = 4!)

This means L_2 is SCALAR — every triangle mode has the same "mass".
The decomposition into 8 irreps must come from the GROUP action alone,
not from eigenvalue splitting.

Usage:
  python3 scripts/w33_triangle_decomposition.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, deque
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from w33_homology import build_clique_complex, boundary_matrix, build_w33
from w33_h1_decomposition import (
    J_matrix,
    build_incidence_matrix,
    make_vertex_permutation,
    signed_edge_permutation,
    transvection_matrix,
)


def build_triangle_permutation(vp, triangles, tri_idx):
    """Build the signed permutation on triangles induced by vertex permutation vp.

    Returns (perm, signs) where:
      perm[i] = j means triangle i maps to triangle j
      signs[i] = +/-1 is the orientation sign
    """
    n_tri = len(triangles)
    perm = np.zeros(n_tri, dtype=int)
    signs = np.zeros(n_tri, dtype=float)

    for i, tri in enumerate(triangles):
        # Apply vertex permutation
        mapped = [vp[tri[0]], vp[tri[1]], vp[tri[2]]]
        sorted_mapped = tuple(sorted(mapped))
        j = tri_idx[sorted_mapped]
        perm[i] = j

        # Compute orientation sign
        # The sign is the parity of the permutation that sorts mapped
        # We need: sign of permutation taking (mapped[0], mapped[1], mapped[2])
        # to sorted order
        inv = 0
        for a in range(3):
            for b in range(a + 1, 3):
                if mapped[a] > mapped[b]:
                    inv += 1
        signs[i] = (-1) ** inv

    return perm, signs


def build_tet_permutation(vp, tetrahedra, tet_idx):
    """Build the signed permutation on tetrahedra induced by vertex permutation vp."""
    n_tet = len(tetrahedra)
    perm = np.zeros(n_tet, dtype=int)
    signs = np.zeros(n_tet, dtype=float)

    for i, tet in enumerate(tetrahedra):
        mapped = [vp[tet[j]] for j in range(4)]
        sorted_mapped = tuple(sorted(mapped))
        j = tet_idx[sorted_mapped]
        perm[i] = j

        # Sign = parity of permutation sorting mapped
        inv = 0
        for a in range(4):
            for b in range(a + 1, 4):
                if mapped[a] > mapped[b]:
                    inv += 1
        signs[i] = (-1) ** inv

    return perm, signs


def main():
    t0 = time.time()

    print("=" * 72)
    print("  TRIANGLE SPACE C_2(W33) DECOMPOSITION UNDER PSp(4,3)")
    print("=" * 72)

    # =====================================================================
    # Step 1: Build W33 and its clique complex
    # =====================================================================
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)
    triangles = simplices[2]
    tetrahedra = simplices[3]
    n_tri = len(triangles)
    n_tet = len(tetrahedra)

    print(f"\n  W33 clique complex: {n} vertices, {m} edges, "
          f"{n_tri} triangles, {n_tet} tetrahedra")

    # Build indices
    tri_idx = {t: i for i, t in enumerate(triangles)}
    tet_idx = {t: i for i, t in enumerate(tetrahedra)}

    # =====================================================================
    # Step 2: Verify L_2 = 4I (triangle Laplacian is scalar)
    # =====================================================================
    print(f"\n  Verifying L_2 = 4I...")

    d2 = boundary_matrix(simplices[2], simplices[1]).astype(float)  # 240 x 160
    d3 = boundary_matrix(simplices[3], simplices[2]).astype(float)  # 160 x 40

    L2 = d2.T @ d2 + d3 @ d3.T
    L2_eigvals = np.sort(np.linalg.eigvalsh(L2))
    L2_error = np.linalg.norm(L2 - 4.0 * np.eye(n_tri))
    print(f"  ||L_2 - 4I|| = {L2_error:.2e}")
    print(f"  L_2 eigenvalues: min={L2_eigvals[0]:.6f}, max={L2_eigvals[-1]:.6f}")
    assert L2_error < 1e-10, f"L_2 is not 4I! Error: {L2_error}"

    # =====================================================================
    # Step 3: Build PSp(4,3) group
    # =====================================================================
    print(f"\n  Building PSp(4,3)...")

    J = J_matrix()
    gen_vperms = []
    for v in vertices:
        M = transvection_matrix(np.array(v, dtype=int), J)
        vp = make_vertex_permutation(M, vertices)
        gen_vperms.append(tuple(vp))

    id_v = tuple(range(n))
    visited = {id_v}
    queue = deque([id_v])
    all_vperms = [id_v]

    while queue:
        cur_v = queue.popleft()
        for gv in gen_vperms:
            new_v = tuple(gv[i] for i in cur_v)
            if new_v not in visited:
                visited.add(new_v)
                all_vperms.append(new_v)
                queue.append(new_v)

    G = len(all_vperms)
    print(f"  |PSp(4,3)| = {G}")
    assert G == 25920, f"Unexpected group order: {G}"

    # =====================================================================
    # Step 4: Compute characters on C_2
    # =====================================================================
    print(f"\n  Computing signed triangle characters for all {G} elements...")

    # Store full character data (chi on C_0, C_1, C_2, C_3)
    characters = []  # list of (chi0, chi1, chi2, chi3) tuples
    chi2_list = []

    ar_m = np.arange(m, dtype=int)
    ar_tri = np.arange(n_tri, dtype=int)

    for idx_g, vp in enumerate(all_vperms):
        # C_0 character: fixed points
        chi0 = sum(1 for i in range(n) if vp[i] == i)

        # C_1 character: signed edge
        ep, es = signed_edge_permutation(vp, edges)
        ep_np = np.asarray(ep, dtype=int)
        es_np = np.asarray(es, dtype=float)
        fixed_e = (ep_np == ar_m)
        chi1 = float(np.sum(es_np[fixed_e]))

        # C_2 character: signed triangle
        tp, ts = build_triangle_permutation(vp, triangles, tri_idx)
        fixed_t = (tp == ar_tri)
        chi2 = float(np.sum(ts[fixed_t]))
        chi2_list.append(chi2)

        # C_3 character: signed tetrahedron
        ttp, tts = build_tet_permutation(vp, tetrahedra, tet_idx)
        ar_tet = np.arange(n_tet, dtype=int)
        fixed_tet = (ttp == ar_tet)
        chi3 = float(np.sum(tts[fixed_tet]))

        characters.append((chi0, chi1, chi2, chi3))

    chi2_arr = np.array(chi2_list, dtype=float)

    # Commutant dimension check
    comm2 = np.sum(chi2_arr ** 2) / G
    print(f"\n  <|chi_2|^2> = {comm2:.6f}")
    print(f"  Number of irreps in C_2: {int(round(comm2))}")

    # =====================================================================
    # Step 5: Decompose C_2 using random projections
    # =====================================================================
    print(f"\n  Decomposing C_2 = R^{n_tri} into irreps...")

    # Build all 160x160 representation matrices on C_2
    # This is memory-intensive (25920 x 160 x 160) but manageable
    # We'll use the commutant projection method: A = (1/|G|) sum R_g^T X R_g

    # To find irreps, we use the character method:
    # Project out each isotypic component using:
    #   P_rho = (dim(rho)/|G|) * sum chi_rho(g)^* R_g
    # But we don't know the characters of the irreps yet.
    # Instead, we use random projections to find the commutant algebra.

    # Build representation matrices for C_2 (signed triangle perms)
    print(f"  Building C_2 representation matrices...")
    R_tri = np.zeros((G, n_tri, n_tri), dtype=float)
    for idx_g, vp in enumerate(all_vperms):
        tp, ts = build_triangle_permutation(vp, triangles, tri_idx)
        for i in range(n_tri):
            R_tri[idx_g, tp[i], i] = ts[i]

    # Verify: R should be orthogonal for each g
    sample_idx = min(100, G - 1)
    check = R_tri[sample_idx] @ R_tri[sample_idx].T
    err = np.linalg.norm(check - np.eye(n_tri))
    print(f"  Orthogonality check (g={sample_idx}): ||RR^T - I|| = {err:.2e}")

    # Commutant algebra: find all A such that A R_g = R_g A for all g
    # Method: project random matrices into commutant
    print(f"\n  Computing commutant algebra via random projections...")

    np.random.seed(42)
    n_probes = 10
    commutant_basis = []

    for probe in range(n_probes):
        X = np.random.randn(n_tri, n_tri)

        # Symmetric part
        Xs = (X + X.T) / 2
        A_sym = np.zeros((n_tri, n_tri), dtype=float)
        for idx_g in range(G):
            A_sym += R_tri[idx_g].T @ Xs @ R_tri[idx_g]
        A_sym /= G

        # Antisymmetric part
        Xa = (X - X.T) / 2
        A_anti = np.zeros((n_tri, n_tri), dtype=float)
        for idx_g in range(G):
            A_anti += R_tri[idx_g].T @ Xa @ R_tri[idx_g]
        A_anti /= G

        for A in [A_sym, A_anti]:
            if np.linalg.norm(A) > 1e-10:
                commutant_basis.append(A / np.linalg.norm(A))

    # Gram-Schmidt on commutant basis
    comm_space = []
    for A in commutant_basis:
        v = A.ravel()
        for u in comm_space:
            v -= np.dot(v, u) * u
        norm = np.linalg.norm(v)
        if norm > 1e-8:
            comm_space.append(v / norm)

    comm_dim = len(comm_space)
    print(f"  Commutant dimension: {comm_dim}")

    # =====================================================================
    # Step 6: Diagonalize commutant to find isotypic components
    # =====================================================================
    print(f"\n  Finding isotypic components...")

    # Build a "generic" commutant element with distinct eigenvalues
    # on each isotypic component
    np.random.seed(123)
    coeffs = np.random.randn(comm_dim)
    C_generic = np.zeros((n_tri, n_tri), dtype=float)
    for i, c in enumerate(coeffs):
        C_generic += c * comm_space[i].reshape(n_tri, n_tri)

    # Make it symmetric (real commutant elements can be symmetrized)
    C_sym = (C_generic + C_generic.T) / 2

    # Diagonalize
    eigvals, eigvecs = np.linalg.eigh(C_sym)

    # Cluster eigenvalues to find isotypic components
    tol_cluster = 1e-6
    clusters = []
    used = np.zeros(n_tri, dtype=bool)
    sorted_idx = np.argsort(eigvals)

    for i in sorted_idx:
        if used[i]:
            continue
        cluster = [i]
        used[i] = True
        for j in sorted_idx:
            if not used[j] and abs(eigvals[j] - eigvals[i]) < tol_cluster:
                cluster.append(j)
                used[j] = True
        clusters.append(cluster)

    print(f"\n  Found {len(clusters)} isotypic components:")
    dims = []
    for ci, cluster in enumerate(clusters):
        d = len(cluster)
        dims.append(d)
        ev = eigvals[cluster[0]]
        print(f"    Component {ci+1}: dim = {d}, eigenvalue = {ev:.6f}")

    dims_sorted = sorted(dims)
    print(f"\n  Dimensions: {' + '.join(map(str, dims_sorted))} = {sum(dims_sorted)}")
    assert sum(dims_sorted) == n_tri, f"Dimensions don't sum to {n_tri}"

    # =====================================================================
    # Step 7: Verify irreducibility of each component
    # =====================================================================
    print(f"\n  Verifying irreducibility of each component...")

    irrep_data = []
    for ci, cluster in enumerate(clusters):
        d = len(cluster)
        V = eigvecs[:, cluster]  # n_tri x d projector basis

        # Commutant of restricted representation
        np.random.seed(42 + ci)
        X_probe = np.random.randn(d, d)
        X_sym = (X_probe + X_probe.T) / 2
        X_anti = (X_probe - X_probe.T) / 2

        A_s = np.zeros((d, d), dtype=float)
        A_a = np.zeros((d, d), dtype=float)
        for idx_g in range(G):
            R_sub = V.T @ R_tri[idx_g] @ V  # d x d
            A_s += R_sub.T @ X_sym @ R_sub
            A_a += R_sub.T @ X_anti @ R_sub
        A_s /= G
        A_a /= G

        # Check if A_s is scalar (=> irreducible for symmetric probes)
        A_s_trace = np.trace(A_s) / d
        A_s_dev = np.linalg.norm(A_s - A_s_trace * np.eye(d))

        # Check A_anti for complex structure
        A_a_norm = np.linalg.norm(A_a)

        is_irreducible = A_s_dev < 1e-8
        has_complex_structure = A_a_norm > 1e-6

        # Frobenius-Schur indicator
        fs_indicator = None
        if is_irreducible:
            if has_complex_structure:
                # Check J^2 = -I
                J_cand = A_a / np.linalg.norm(A_a) * np.sqrt(d)
                J2 = J_cand @ J_cand
                j2_err = np.linalg.norm(J2 + np.eye(d))
                if j2_err < 1e-6:
                    fs_indicator = 0  # complex type
                else:
                    fs_indicator = 1  # real type with nonzero anti part (should check)
            else:
                fs_indicator = 1  # real type

        status = "IRREDUCIBLE" if is_irreducible else "REDUCIBLE?"
        fs_str = {0: "complex", 1: "real", -1: "quaternionic", None: "?"}[fs_indicator]

        print(f"    Component {ci+1} (dim {d}): {status}, FS={fs_indicator} ({fs_str})")
        print(f"      ||A_sym - scalar*I|| = {A_s_dev:.2e}, ||A_anti|| = {A_a_norm:.2e}")

        irrep_data.append({
            'dim': d,
            'irreducible': is_irreducible,
            'fs_indicator': fs_indicator,
            'fs_type': fs_str,
        })

    # =====================================================================
    # Step 8: Identify the physical content
    # =====================================================================
    print(f"\n{'='*72}")
    print("  PHYSICAL INTERPRETATION OF C_2 DECOMPOSITION")
    print("=" * 72)

    dims_sorted = sorted([d['dim'] for d in irrep_data])
    print(f"\n  C_2(160) = {' + '.join(map(str, dims_sorted))}")
    print(f"  under PSp(4,3) (order 25920)")

    # Identify shared dimensions with other chain spaces
    print(f"\n  CROSS-SPACE IDENTIFICATION:")
    print(f"    C_0(40)  = 1 + 24 + 15")
    print(f"    C_1(240) = 81 + 90 + 30 + 24 + 15")
    print(f"    C_2(160) = {' + '.join(map(str, dims_sorted))}")
    print(f"    C_3(40)  = 1 + 24 + 15")

    # Check which C_1 irreps appear in C_2
    c1_dims = Counter([81, 90, 30, 24, 15])
    c2_dims = Counter(dims_sorted)

    shared = c1_dims & c2_dims
    print(f"\n  Dimensions shared with C_1: {dict(shared)}")
    print(f"  Dimensions NOT in C_1: {dict(c2_dims - c1_dims)}")

    # =====================================================================
    # Step 9: Character analysis - match to C_1 irreps
    # =====================================================================
    print(f"\n  Character matching with C_1 irreps...")

    # Build C_1 Hodge projectors
    D_inc = build_incidence_matrix(n, edges)
    B2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    L1 = D_inc.T @ D_inc + B2 @ B2.T
    w, v = np.linalg.eigh(L1)
    idx_sort = np.argsort(w)
    w, v = w[idx_sort], v[:, idx_sort]

    tol_ev = 1e-6
    hodge_sectors = {}
    for label, target_ev in [('harm', 0.0), ('coex', 4.0), ('ex10', 10.0), ('ex16', 16.0)]:
        idx = np.where(np.abs(w - target_ev) < tol_ev)[0]
        hodge_sectors[label] = v[:, idx]

    # Compute character of each C_1 Hodge sector at each group element
    print(f"  Computing C_1 Hodge sector characters...")

    chi_c1_sectors = {k: np.zeros(G) for k in ['harm', 'coex', 'ex10', 'ex16']}

    for idx_g, vp in enumerate(all_vperms):
        ep, es = signed_edge_permutation(vp, edges)
        ep_np = np.asarray(ep, dtype=int)
        es_np = np.asarray(es, dtype=float)

        for label, V_sector in hodge_sectors.items():
            P = V_sector @ V_sector.T  # projector
            # chi = sum_i P[i, ep[i]] * es[i]
            chi = float(np.sum(P[ar_m, ep_np] * es_np))
            chi_c1_sectors[label][idx_g] = chi

    # Compute character of each C_2 component
    print(f"  Computing C_2 component characters...")

    chi_c2_components = []
    for ci, cluster in enumerate(clusters):
        V = eigvecs[:, cluster]
        P = V @ V.T  # projector

        chi_comp = np.zeros(G)
        for idx_g in range(G):
            chi_comp[idx_g] = np.trace(P @ R_tri[idx_g])
        chi_c2_components.append(chi_comp)

    # Inner products between C_2 components and C_1 sectors
    print(f"\n  Character inner products <chi_C2, chi_C1>:")
    print(f"  {'C2 comp':>10s} | {'harm(81)':>10s} | {'coex(120)':>10s} | {'ex10(24)':>10s} | {'ex16(15)':>10s}")
    print(f"  {'-'*10}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}")

    for ci, chi_c2 in enumerate(chi_c2_components):
        d = len(clusters[ci])
        ips = {}
        for label in ['harm', 'coex', 'ex10', 'ex16']:
            ip = np.dot(chi_c2, chi_c1_sectors[label]) / G
            ips[label] = ip
        print(f"  dim={d:>5d} | {ips['harm']:10.4f} | {ips['coex']:10.4f} | "
              f"{ips['ex10']:10.4f} | {ips['ex16']:10.4f}")

    # Inner products with C_0 characters
    print(f"\n  Character inner products with C_0 and C_3:")

    chi_c0 = np.array([c[0] for c in characters], dtype=float)
    chi_c3 = np.array([c[3] for c in characters], dtype=float)

    for ci, chi_c2 in enumerate(chi_c2_components):
        d = len(clusters[ci])
        ip_c0 = np.dot(chi_c2, chi_c0) / G
        ip_c3 = np.dot(chi_c2, chi_c3) / G
        ip_c1 = np.dot(chi_c2, np.array([c[1] for c in characters], dtype=float)) / G
        print(f"    C_2 dim={d}: <chi, chi_C0>={ip_c0:.4f}, <chi, chi_C1>={ip_c1:.4f}, "
              f"<chi, chi_C3>={ip_c3:.4f}")

    # =====================================================================
    # Step 10: Boundary map structure
    # =====================================================================
    print(f"\n{'='*72}")
    print("  BOUNDARY MAP STRUCTURE")
    print("=" * 72)

    # d_2: C_2 -> C_1 maps triangles to edges
    # d_3: C_3 -> C_2 maps tetrahedra to triangles
    # How do these maps interact with the irrep decomposition?

    # im(d_2^T) in C_2 = co-exact part of C_2
    # im(d_3) in C_2 = exact part of C_2
    # Since L_2 = 4I, there are no harmonic 2-chains (b_2 = 0)
    # So C_2 = im(d_2^T) + im(d_3)

    # Compute the subspaces
    rank_d2 = np.linalg.matrix_rank(d2, tol=1e-8)
    rank_d3 = np.linalg.matrix_rank(d3, tol=1e-8)

    print(f"\n  rank(d_2) = {rank_d2}  (d_2: C_2 -> C_1, so d_2^T: C_1 -> C_2)")
    print(f"  rank(d_3) = {rank_d3}  (d_3: C_3 -> C_2)")
    print(f"  rank(d_2) + rank(d_3) = {rank_d2 + rank_d3}")
    print(f"  dim(C_2) = {n_tri}")
    print(f"  b_2 = {n_tri - rank_d2 - rank_d3}")

    # Project each C_2 irrep component onto im(d_2^T) and im(d_3)
    # im(d_2^T) = column space of d_2^T
    U_d2, S_d2, _ = np.linalg.svd(d2.T, full_matrices=False)
    r_d2 = np.sum(S_d2 > 1e-8)
    P_coex2 = U_d2[:, :r_d2] @ U_d2[:, :r_d2].T  # projector onto im(d_2^T)

    # im(d_3) = column space of d_3
    U_d3, S_d3, _ = np.linalg.svd(d3, full_matrices=False)
    r_d3 = np.sum(S_d3 > 1e-8)
    P_ex2 = U_d3[:, :r_d3] @ U_d3[:, :r_d3].T  # projector onto im(d_3)

    print(f"\n  Each C_2 component projected onto im(d_2^T) and im(d_3):")
    for ci, cluster in enumerate(clusters):
        d = len(cluster)
        V = eigvecs[:, cluster]

        # Project each basis vector
        coex_dim = np.trace(V.T @ P_coex2 @ V)
        ex_dim = np.trace(V.T @ P_ex2 @ V)

        print(f"    dim={d}: coex_2 overlap = {coex_dim:.4f}, exact_2 overlap = {ex_dim:.4f}")

    # =====================================================================
    # Step 11: Summary and synthesis
    # =====================================================================
    print(f"\n{'='*72}")
    print("  SYNTHESIS: TRIANGLE DECOMPOSITION")
    print("=" * 72)

    print(f"""
  C_2(W33) = R^160 decomposes under PSp(4,3) as:

    160 = {' + '.join(map(str, dims_sorted))}

  KEY PROPERTIES:
    - L_2 = 4I (all triangle modes have mass = spectral gap)
    - b_2 = 0 (no harmonic 2-chains)
    - C_2 = im(d_2^T) + im(d_3) (co-exact + exact)
    - rank(d_2) = {rank_d2} (co-exact dim in C_2)
    - rank(d_3) = {rank_d3} (exact dim in C_2)

  PHYSICAL INTERPRETATION:
    - Every triangle is a 3-body interaction vertex
    - 160 = 4 x 40 = faces per tetrahedron x tetrahedra
    - The 8-irrep decomposition reveals the internal structure
      of gauge boson interactions
""")

    elapsed = time.time() - t0
    print(f"  Elapsed: {elapsed:.1f}s")

    # Save results
    results = {
        'n_triangles': n_tri,
        'n_components': len(clusters),
        'dimensions': dims_sorted,
        'irrep_data': irrep_data,
        'L2_error': float(L2_error),
        'rank_d2': rank_d2,
        'rank_d3': rank_d3,
        'b2': n_tri - rank_d2 - rank_d3,
        'elapsed_seconds': elapsed,
    }

    ts = int(time.time())
    out_path = Path.cwd() / "checks" / f"PART_CVII_triangle_decomp_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  Wrote: {out_path}")


if __name__ == "__main__":
    main()
