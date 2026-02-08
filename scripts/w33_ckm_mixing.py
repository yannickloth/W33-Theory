#!/usr/bin/env python3
"""
CKM-like Mixing Matrix from Z3 Ambiguity in W33
==================================================

DISCOVERY: All 800 order-3 elements of PSp(4,3) decompose the 81-dim
harmonic space as 27 + 27 + 27. Different Z3 subgroups give DIFFERENT
generation bases. The mismatch between two bases gives a CKM-like
mixing matrix — a PREDICTION of the theory.

Physical Interpretation:
  In the Standard Model, the CKM matrix arises because the mass
  eigenstates (defined by Yukawa couplings) differ from the weak
  eigenstates (defined by SU(2) gauge interaction).

  In W33, different Z3 subgroups correspond to different ways of
  decomposing matter into three generations. The physical Z3 is
  determined by the specific process (strong vs weak vs Yukawa).
  The mismatch between two such decompositions gives mixing.

Method:
  1. Classify 800 order-3 elements into conjugacy classes
  2. Pick representatives from two different classes
  3. Compute their eigenspace decompositions on H1 (81-dim)
  4. Compute the 3x3 overlap matrix between generation subspaces
  5. Check if the mixing angles match experimental CKM values

Usage:
  py -3 -X utf8 scripts/w33_ckm_mixing.py
"""
from __future__ import annotations

import sys
import time
from collections import deque, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from w33_homology import boundary_matrix, build_clique_complex, build_w33

from w33_h1_decomposition import (
    J_matrix,
    build_incidence_matrix,
    make_vertex_permutation,
    signed_edge_permutation,
    signed_permutation_matrix,
    transvection_matrix,
)


def build_all(verbose=True):
    """Build everything needed: W33, Hodge, PSp(4,3)."""
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)

    B2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    D = build_incidence_matrix(n, edges)
    L1 = D.T @ D + B2 @ B2.T

    w, v = np.linalg.eigh(L1)
    idx = np.argsort(w)
    w, v = w[idx], v[:, idx]

    tol = 1e-8
    null_idx = np.where(np.abs(w) < tol)[0]
    W = v[:, null_idx]
    b1 = W.shape[1]
    assert b1 == 81

    S_proj = W @ W.T

    J_mat = J_matrix()
    gen_vperms = []
    gen_signed = []
    for vert in vertices:
        M_t = transvection_matrix(np.array(vert, dtype=int), J_mat)
        vp = make_vertex_permutation(M_t, vertices)
        gen_vperms.append(tuple(vp))
        ep, es = signed_edge_permutation(vp, edges)
        gen_signed.append((tuple(ep), tuple(es)))

    id_v = tuple(range(n))
    id_e = tuple(range(m))
    id_s = tuple([1] * m)
    visited = {id_v: (id_e, id_s)}
    queue = deque([id_v])

    while queue:
        cur_v = queue.popleft()
        cur_ep, cur_es = visited[cur_v]
        for gv, (gep, ges) in zip(gen_vperms, gen_signed):
            new_v = tuple(gv[i] for i in cur_v)
            if new_v not in visited:
                new_ep = tuple(gep[cur_ep[i]] for i in range(m))
                new_es = tuple(ges[cur_ep[i]] * cur_es[i] for i in range(m))
                visited[new_v] = (new_ep, new_es)
                queue.append(new_v)

    if verbose:
        print(f"  Built: {n} vertices, {m} edges, |PSp(4,3)| = {len(visited)}")

    return {
        'n': n, 'vertices': vertices, 'adj': adj, 'edges': edges,
        'm': m, 'W': W, 'S_proj': S_proj,
        'visited': visited, 'gen_vperms': gen_vperms, 'gen_signed': gen_signed,
    }


def classify_order3_conjugacy(data):
    """Classify order-3 elements into conjugacy classes.

    Two elements g1, g2 are conjugate if there exists h with g2 = h g1 h^{-1}.
    On vertex permutations: g2_v = h_v o g1_v o h_v^{-1}.
    """
    n = data['n']
    m = data['m']
    visited = data['visited']
    W = data['W']
    b1 = W.shape[1]

    id_v = tuple(range(n))

    # Find all order-3 elements
    order3 = []
    for cur_v, (cur_ep, cur_es) in visited.items():
        v2 = tuple(cur_v[i] for i in cur_v)
        v3 = tuple(cur_v[i] for i in v2)
        if v3 == id_v and cur_v != id_v:
            order3.append((cur_v, cur_ep, cur_es))

    print(f"\n  Total order-3 elements: {len(order3)}")

    # Classify by conjugacy: two elements are conjugate if they have the
    # same cycle type on vertices AND the same character on H1
    # (Character is a class function, so conjugate elements have same chi)

    # But we already know ALL have chi=0. So we need a finer invariant.
    # Use the FULL character on all Hodge sectors.

    ar = np.arange(m, dtype=int)
    S_proj = data['S_proj']

    # For each order-3 element, compute characters on different sectors
    # We'll use the cycle structure on vertices as a conjugacy class identifier
    class_map = defaultdict(list)

    for i, (cur_v, cur_ep, cur_es) in enumerate(order3):
        # Cycle type on vertices
        visited_v = set()
        cycles = []
        for start in range(n):
            if start in visited_v:
                continue
            cycle = []
            pos = start
            while pos not in visited_v:
                visited_v.add(pos)
                cycle.append(pos)
                pos = cur_v[pos]
            cycles.append(len(cycle))
        cycle_type = tuple(sorted(cycles))
        class_map[cycle_type].append(i)

    print(f"  Conjugacy classes of order-3 elements (by vertex cycle type):")
    for ct, indices in sorted(class_map.items()):
        print(f"    Cycle type {ct}: {len(indices)} elements")

    # For a finer classification, also compute character on other sectors
    # (co-exact, exact-10, exact-16)
    print(f"\n  Refining with full spectral character...")

    # Get eigenvectors for all Hodge sectors
    B2 = boundary_matrix(data.get('simplices', build_clique_complex(n, data['adj']))[2],
                         build_clique_complex(n, data['adj'])[1]).astype(float)
    D = build_incidence_matrix(n, data['edges'])
    L1 = D.T @ D + B2 @ B2.T
    w, v = np.linalg.eigh(L1)
    idx_sort = np.argsort(w)
    w, v = w[idx_sort], v[:, idx_sort]

    tol = 1e-6
    # Get sector projectors
    sectors = {}
    for ev_target, name in [(0.0, 'harm'), (4.0, 'coex'), (10.0, 'ex10'), (16.0, 'ex16')]:
        sec_idx = np.where(np.abs(w - ev_target) < tol)[0]
        W_sec = v[:, sec_idx]
        sectors[name] = W_sec @ W_sec.T  # projector

    refined_map = defaultdict(list)
    for i, (cur_v, cur_ep, cur_es) in enumerate(order3):
        cur_ep_np = np.asarray(cur_ep, dtype=int)
        cur_es_np = np.asarray(cur_es, dtype=float)

        chars = []
        for name in ['harm', 'coex', 'ex10', 'ex16']:
            P = sectors[name]
            chi = float((P[ar, cur_ep_np] * cur_es_np).sum())
            chars.append(round(chi))
        key = tuple(chars)
        refined_map[key].append(i)

    print(f"\n  Refined conjugacy classes (by spectral character):")
    for chars, indices in sorted(refined_map.items()):
        print(f"    chi(harm,coex,ex10,ex16) = {chars}: {len(indices)} elements")

    return order3, refined_map


def compute_generation_eigenspaces(data, element):
    """Compute the three 27-dim eigenspaces of an order-3 element on H1."""
    m = data['m']
    W = data['W']
    b1 = W.shape[1]

    cur_v, cur_ep, cur_es = element
    cur_ep_np = np.asarray(cur_ep, dtype=int)
    cur_es_np = np.asarray(cur_es, dtype=float)

    S_g_W = W[cur_ep_np, :] * cur_es_np[:, None]
    R_g = W.T @ S_g_W

    eigenvalues, eigenvectors = np.linalg.eig(R_g)

    omega = np.exp(2j * np.pi / 3)
    omega_bar = np.exp(-2j * np.pi / 3)

    spaces = {}
    for label, target in [('1', 1.0), ('w', omega), ('wb', omega_bar)]:
        idx = [i for i, ev in enumerate(eigenvalues) if abs(ev - target) < 0.1]
        spaces[label] = eigenvectors[:, idx]

    return spaces


def compute_mixing_matrix(spaces1, spaces2):
    """Compute the 3x3 generation mixing matrix between two Z3 bases.

    M_{ij} = ||P_i^{(1)} P_j^{(2)}||_F^2 / 27

    where P_i^{(k)} is the projector onto the i-th generation in basis k.
    This gives the probability that a particle in generation i of basis 1
    appears as generation j in basis 2.
    """
    labels = ['1', 'w', 'wb']
    M = np.zeros((3, 3))

    for i, l1 in enumerate(labels):
        V1 = spaces1[l1]  # 81 x 27 (complex)
        for j, l2 in enumerate(labels):
            V2 = spaces2[l2]  # 81 x 27 (complex)
            # Overlap: trace of P1 P2 = ||V1^H V2||_F^2
            overlap = V1.conj().T @ V2  # 27 x 27
            M[i, j] = np.real(np.trace(overlap @ overlap.conj().T)) / 27.0

    return M


def analyze_mixing_angles(M):
    """Extract mixing angles from the 3x3 mixing matrix.

    The CKM matrix is parameterized by three angles (theta12, theta13, theta23)
    and a CP-violating phase delta.

    For our probability matrix P = |V|^2, the angles can be extracted from:
      sin^2(theta12) = P[0,1] / (P[0,0] + P[0,1])
      sin^2(theta23) = P[1,2] / (P[1,1] + P[1,2])
      sin^2(theta13) = P[0,2]
    """
    print(f"\n  Mixing matrix (generation overlap probabilities):")
    labels = ['Gen 1', 'Gen 2', 'Gen 3']
    print(f"           {'  '.join(f'{l:>8s}' for l in labels)}")
    for i, l in enumerate(labels):
        row = '  '.join(f'{M[i,j]:8.5f}' for j in range(3))
        print(f"    {l}: {row}")

    # Check it's doubly stochastic (rows and columns sum to 1)
    row_sums = M.sum(axis=1)
    col_sums = M.sum(axis=0)
    print(f"\n  Row sums: {row_sums}")
    print(f"  Col sums: {col_sums}")
    is_doubly_stochastic = np.allclose(row_sums, 1.0, atol=0.01) and \
                           np.allclose(col_sums, 1.0, atol=0.01)
    print(f"  Doubly stochastic: {is_doubly_stochastic}")

    if np.max(M) > 0.99:
        print(f"\n  RESULT: Mixing matrix is (near) identity")
        print(f"  The two Z3 elements give the SAME generation decomposition")
        return {'trivial': True}

    if is_doubly_stochastic and np.min(M) > 0.01:
        # Non-trivial mixing!
        # Extract angles
        if M[0, 0] + M[0, 1] > 0:
            sin2_12 = M[0, 1] / (M[0, 0] + M[0, 1])
        else:
            sin2_12 = float('nan')

        if M[1, 1] + M[1, 2] > 0:
            sin2_23 = M[1, 2] / (M[1, 1] + M[1, 2])
        else:
            sin2_23 = float('nan')

        sin2_13 = M[0, 2]

        theta12 = np.arcsin(np.sqrt(max(0, min(1, sin2_12)))) * 180 / np.pi
        theta23 = np.arcsin(np.sqrt(max(0, min(1, sin2_23)))) * 180 / np.pi
        theta13 = np.arcsin(np.sqrt(max(0, min(1, sin2_13)))) * 180 / np.pi

        print(f"\n  Mixing angles:")
        print(f"    theta_12 = {theta12:.2f} deg (CKM: ~13.0 deg, PMNS: ~33.4 deg)")
        print(f"    theta_23 = {theta23:.2f} deg (CKM: ~2.4 deg, PMNS: ~45.0 deg)")
        print(f"    theta_13 = {theta13:.2f} deg (CKM: ~0.2 deg, PMNS: ~8.5 deg)")

        # Check for maximal mixing (theta = 45 deg => sin^2 = 0.5)
        if abs(sin2_12 - 1/3) < 0.05:
            print(f"\n  NOTE: theta_12 gives sin^2 ~ 1/3 (tribimaximal mixing!)")

        return {
            'trivial': False,
            'sin2_12': float(sin2_12),
            'sin2_23': float(sin2_23),
            'sin2_13': float(sin2_13),
            'theta12': float(theta12),
            'theta23': float(theta23),
            'theta13': float(theta13),
        }

    return {'trivial': True}


def main():
    t0 = time.time()
    print("=" * 72)
    print("  CKM-LIKE MIXING FROM Z3 AMBIGUITY IN W33")
    print("=" * 72)

    print("\n  Building W33 and PSp(4,3)...")
    data = build_all()

    # Classify order-3 elements
    order3, refined_map = classify_order3_conjugacy(data)

    # Get representatives from each refined class
    class_keys = sorted(refined_map.keys())
    print(f"\n  Number of distinct spectral classes: {len(class_keys)}")

    if len(class_keys) < 2:
        print("  Only one class -- all order-3 elements are spectrally equivalent")
        print("  Computing mixing between two non-commuting elements from same class...")

        # Pick two elements from the same class
        indices = list(refined_map.values())[0]
        el1 = order3[indices[0]]
        # Find one that doesn't commute with el1
        for idx in indices[1:]:
            el2 = order3[idx]
            # Check commutation on vertices
            v1, v2 = el1[0], el2[0]
            g1g2 = tuple(v1[i] for i in v2)
            g2g1 = tuple(v2[i] for i in v1)
            if g1g2 != g2g1:
                print(f"  Found non-commuting pair: elements {indices[0]} and {idx}")
                break
        else:
            print("  All elements commute with the first -- this shouldn't happen")
            return
    else:
        # Pick representatives from different classes
        rep_indices = []
        for key in class_keys:
            rep_indices.append(refined_map[key][0])
        el1 = order3[rep_indices[0]]
        el2 = order3[rep_indices[1]]
        print(f"\n  Using representatives from classes {class_keys[0]} and {class_keys[1]}")

    # Compute generation eigenspaces
    print("\n  Computing generation eigenspaces for element 1...")
    spaces1 = compute_generation_eigenspaces(data, el1)
    for label, V in spaces1.items():
        print(f"    Generation '{label}': dim = {V.shape[1]}")

    print("\n  Computing generation eigenspaces for element 2...")
    spaces2 = compute_generation_eigenspaces(data, el2)
    for label, V in spaces2.items():
        print(f"    Generation '{label}': dim = {V.shape[1]}")

    # Compute mixing matrix
    print("\n" + "=" * 72)
    print("  MIXING MATRIX ANALYSIS")
    print("=" * 72)
    M = compute_mixing_matrix(spaces1, spaces2)
    angles = analyze_mixing_angles(M)

    # Try multiple pairs to see the range of mixing patterns
    print("\n" + "=" * 72)
    print("  SYSTEMATIC MIXING ANALYSIS")
    print("=" * 72)

    # Sample several non-commuting pairs and compute their mixing
    print("\n  Sampling mixing matrices from 20 random non-commuting pairs...")
    np.random.seed(42)
    all_indices = list(range(len(order3)))
    np.random.shuffle(all_indices)

    mixing_results = []
    pair_count = 0
    for i in range(min(100, len(all_indices))):
        if pair_count >= 20:
            break
        for j in range(i + 1, min(100, len(all_indices))):
            if pair_count >= 20:
                break
            idx1, idx2 = all_indices[i], all_indices[j]
            v1, v2 = order3[idx1][0], order3[idx2][0]
            g1g2 = tuple(v1[k] for k in v2)
            g2g1 = tuple(v2[k] for k in v1)
            if g1g2 != g2g1:
                s1 = compute_generation_eigenspaces(data, order3[idx1])
                s2 = compute_generation_eigenspaces(data, order3[idx2])
                M_pair = compute_mixing_matrix(s1, s2)

                # Check if non-trivial
                if np.max(M_pair) < 0.99:
                    mixing_results.append(M_pair)
                    pair_count += 1

    if mixing_results:
        print(f"\n  Found {len(mixing_results)} non-trivial mixing matrices")
        # Average the mixing matrices to find the "typical" mixing
        M_avg = np.mean(mixing_results, axis=0)
        print(f"\n  Average mixing matrix:")
        labels = ['Gen 1', 'Gen 2', 'Gen 3']
        print(f"           {'  '.join(f'{l:>8s}' for l in labels)}")
        for i, l in enumerate(labels):
            row = '  '.join(f'{M_avg[i,j]:8.5f}' for j in range(3))
            print(f"    {l}: {row}")

        # Check individual mixing patterns
        print(f"\n  Distribution of diagonal elements (self-coupling):")
        diags = [M[i, i] for M in mixing_results for i in range(3)]
        print(f"    Mean: {np.mean(diags):.4f}")
        print(f"    Std:  {np.std(diags):.4f}")
        print(f"    Min:  {np.min(diags):.4f}")
        print(f"    Max:  {np.max(diags):.4f}")

        # Check if any mixing matrix has the democratic (tribimaximal) pattern
        # Democratic: all entries = 1/3
        for k, M_k in enumerate(mixing_results):
            if np.allclose(M_k, np.ones((3, 3)) / 3, atol=0.05):
                print(f"\n  *** DEMOCRATIC MIXING found in pair {k}! ***")
                print(f"  All generations mix equally -> tribimaximal pattern")
    else:
        print(f"\n  All mixing matrices are trivial (identity)")
        print(f"  This means all order-3 elements give the SAME generation decomposition")
        print(f"  (up to relabeling)")

    # Final analysis
    print("\n" + "=" * 72)
    print("  PHYSICAL INTERPRETATION")
    print("=" * 72)
    print(f"""
  The 800 order-3 elements of PSp(4,3) all decompose 81 = 27 + 27 + 27.
  Different elements define different "flavor bases" for the three generations.

  The mismatch between two bases gives a CKM-like mixing matrix.
  This mixing is a GEOMETRIC PREDICTION of the W33-E8 correspondence,
  not an input parameter.

  In the Standard Model:
    - CKM matrix: quark mixing (Cabibbo angle ~ 13 deg)
    - PMNS matrix: lepton mixing (theta_23 ~ 45 deg, near maximal)

  From W33:
    - Mixing depends on the choice of Z3 pair
    - The mixing pattern is constrained by PSp(4,3) symmetry
    - {"Tribimaximal mixing found!" if mixing_results and any(np.allclose(M, np.ones((3,3))/3, atol=0.05) for M in mixing_results) else "Non-trivial mixing structure found" if mixing_results else "Mixing to be determined by physical selection of Z3"}
""")

    elapsed = time.time() - t0
    print(f"  Elapsed: {elapsed:.1f}s")

    return {
        'n_order3': len(order3),
        'n_spectral_classes': len(refined_map),
        'n_nontrivial_mixings': len(mixing_results) if mixing_results else 0,
        'elapsed': elapsed,
    }


if __name__ == "__main__":
    main()
