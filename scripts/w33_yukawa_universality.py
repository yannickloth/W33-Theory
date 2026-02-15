#!/usr/bin/env python3
"""
Yukawa Eigenvalue Universality Check
======================================

Check whether the inter-generation Yukawa eigenvalue ratios are the same
for ALL 800 order-3 elements of PSp(4,3), or depend on the choice.

Usage:
  python scripts/w33_yukawa_universality.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from w33_homology import boundary_matrix, build_clique_complex, build_w33

from w33_h1_decomposition import (
    J_matrix,
    build_incidence_matrix,
    make_vertex_permutation,
    signed_edge_permutation,
    transvection_matrix,
)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def main():
    t0 = time.time()
    print("=" * 72)
    print("  YUKAWA EIGENVALUE UNIVERSALITY CHECK")
    print("=" * 72)

    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)
    triangles = simplices[2]

    d2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    D = build_incidence_matrix(n, edges)
    L1 = D.T @ D + d2 @ d2.T
    eigvals, eigvecs = np.linalg.eigh(L1)

    harm_mask = np.abs(eigvals) < 0.5
    H = eigvecs[:, harm_mask]

    edge_idx = {}
    for i, (u, v) in enumerate(edges):
        edge_idx[(u, v)] = (i, +1)
        edge_idx[(v, u)] = (i, -1)

    def wedge_product(h1, h2):
        result = np.zeros(len(triangles))
        for ti, (v0, v1, v2) in enumerate(triangles):
            e01_idx, e01_s = edge_idx[(v0, v1)]
            e02_idx, e02_s = edge_idx[(v0, v2)]
            e12_idx, e12_s = edge_idx[(v1, v2)]
            h1_01, h1_02, h1_12 = (
                e01_s * h1[e01_idx],
                e02_s * h1[e02_idx],
                e12_s * h1[e12_idx],
            )
            h2_01, h2_02, h2_12 = (
                e01_s * h2[e01_idx],
                e02_s * h2[e02_idx],
                e12_s * h2[e12_idx],
            )
            result[ti] = (
                h1_01 * h2_12
                - h2_01 * h1_12
                - h1_01 * h2_02
                + h2_01 * h1_02
                + h1_02 * h2_12
                - h2_02 * h1_12
            )
        return result

    # Build PSp(4,3)
    print("  Enumerating PSp(4,3)...")
    J_mat = J_matrix()
    gen_vperms, gen_signed = [], []
    for vert in vertices:
        M_t = transvection_matrix(np.array(vert, dtype=int), J_mat)
        vp = make_vertex_permutation(M_t, vertices)
        gen_vperms.append(tuple(vp))
        ep, es = signed_edge_permutation(vp, edges)
        gen_signed.append((tuple(ep), tuple(es)))

    id_v = tuple(range(n))
    visited = {id_v: (tuple(range(m)), tuple([1] * m))}
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

    group_list = list(visited.items())
    print(f"  |PSp(4,3)| = {len(visited)}")

    # Find ALL order-3 elements
    print("  Finding order-3 elements...")
    order3_elements = []
    for cur_v, (cur_ep, cur_es) in group_list:
        v2 = tuple(cur_v[cur_v[i]] for i in range(n))
        v3 = tuple(cur_v[v2[i]] for i in range(n))
        if v3 == id_v and cur_v != id_v:
            order3_elements.append((cur_v, cur_ep, cur_es))

    print(f"  Found {len(order3_elements)} order-3 elements")

    # For each order-3 element, decompose H1 and compute Y eigenvalues
    # Sample a subset if there are too many
    omega = np.exp(2j * np.pi / 3)
    I81 = np.eye(81)

    sample_size = min(50, len(order3_elements))
    np.random.seed(42)
    sample_idx = np.random.choice(len(order3_elements), sample_size, replace=False)
    sample = [order3_elements[i] for i in sample_idx]

    print(f"\n  Sampling {sample_size} order-3 elements...")

    all_eigenvalue_ratios = []
    all_y_traces = []

    for idx, (cur_v, cur_ep, cur_es) in enumerate(sample):
        if idx % 10 == 0:
            print(f"    Processing {idx}/{sample_size}...")

        ep_np = np.asarray(cur_ep, dtype=int)
        es_np = np.asarray(cur_es, dtype=float)
        S_g = H[ep_np, :] * es_np[:, None]
        R_g = H.T @ S_g

        # Check 27+27+27 decomposition
        eigs = np.linalg.eigvals(R_g)
        phases = np.angle(eigs) / (2 * np.pi / 3)
        counts = Counter(round(p) % 3 for p in phases)
        if counts[0] != 27 or counts[1] != 27 or counts[2] != 27:
            continue

        # Extract orthogonal generation bases
        P0 = np.real((I81 + R_g + R_g @ R_g) / 3.0)
        U0, S0, _ = np.linalg.svd(P0)
        B0 = U0[:, :27]

        eig_vals_g, eig_vecs_g = np.linalg.eig(R_g)
        ph = np.angle(eig_vals_g)

        # Find omega eigenvectors (phase near +2pi/3 or -2pi/3)
        omega_idx = np.where(np.abs(np.abs(ph) - 2 * np.pi / 3) < 0.3)[0]
        if len(omega_idx) != 54:
            continue

        # Split into omega and omega^2 by sign of phase
        pos_phase = omega_idx[ph[omega_idx] > 0]
        neg_phase = omega_idx[ph[omega_idx] < 0]
        if len(pos_phase) != 27 or len(neg_phase) != 27:
            continue

        V_omega = eig_vecs_g[:, pos_phase]
        B1_raw = np.real(V_omega)
        B2_raw = np.imag(V_omega)

        # Orthogonalize
        proj0 = B0 @ B0.T
        B1_comp = B1_raw - proj0 @ B1_raw
        Q1, R1 = np.linalg.qr(B1_comp)
        B1 = Q1[:, :27]

        proj01 = np.hstack([B0, B1])
        proj01 = proj01 @ proj01.T
        B2_comp = B2_raw - proj01 @ B2_raw
        Q2, R2 = np.linalg.qr(B2_comp)
        if Q2.shape[1] < 27:
            continue
        B2 = Q2[:, :27]

        # Verify dimensions
        if B0.shape[1] != 27 or B1.shape[1] != 27 or B2.shape[1] != 27:
            continue

        # Compute Y matrix (use subset of pairs for speed)
        gens = [B0, B1, B2]
        Y = np.zeros((3, 3))
        n_sample_pairs = 10  # sample pairs for speed

        for a in range(3):
            for b in range(a, 3):
                total = 0.0
                count = 0
                for i in range(n_sample_pairs):
                    h_a = H @ gens[a][:, i]
                    start_j = i + 1 if a == b else 0
                    for j in range(start_j, n_sample_pairs):
                        h_b = H @ gens[b][:, j]
                        w = wedge_product(h_a, h_b)
                        bracket = d2 @ w
                        total += np.dot(bracket, bracket)
                        count += 1
                Y[a, b] = total / count if count > 0 else 0
                Y[b, a] = Y[a, b]

        y_eigs = np.sort(np.linalg.eigvalsh(Y))
        if y_eigs[0] > 1e-12:
            ratios = y_eigs / y_eigs[0]
            all_eigenvalue_ratios.append(tuple(round(r, 1) for r in ratios))
            all_y_traces.append(round(np.trace(Y), 8))

    print(f"\n  Processed {len(all_eigenvalue_ratios)} valid decompositions")

    # Analyze universality
    ratio_counts = Counter(all_eigenvalue_ratios)
    print(f"\n  Unique eigenvalue ratio patterns: {len(ratio_counts)}")
    for ratios, count in sorted(ratio_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"    {ratios}: {count} times")

    trace_counts = Counter(all_y_traces)
    print(f"\n  Y trace values: {len(trace_counts)} unique")
    for trace, count in sorted(trace_counts.items(), key=lambda x: -x[1])[:5]:
        print(f"    Tr(Y) = {trace}: {count} times")

    # Check: is there a UNIVERSAL eigenvalue pattern?
    if len(ratio_counts) == 1:
        print(f"\n  UNIVERSAL: All order-3 elements give the SAME eigenvalue ratios!")
        print(f"  Ratios: {list(ratio_counts.keys())[0]}")
    else:
        print(
            f"\n  NON-UNIVERSAL: eigenvalue ratios depend on the choice of Z3 element"
        )
        # But check if the trace is universal
        if len(trace_counts) == 1:
            print(f"  But Tr(Y) IS universal: {list(trace_counts.keys())[0]}")

    # Also compute the FULL Y matrix for ALL 27 pairs, for 3 sample elements
    print(f"\n  Computing full Y matrices for 3 samples...")
    for s_idx in range(min(3, len(sample))):
        cur_v, cur_ep, cur_es = sample[s_idx]
        ep_np = np.asarray(cur_ep, dtype=int)
        es_np = np.asarray(cur_es, dtype=float)
        S_g = H[ep_np, :] * es_np[:, None]
        R_g = H.T @ S_g

        eigs = np.linalg.eigvals(R_g)
        phases = np.angle(eigs) / (2 * np.pi / 3)
        counts = Counter(round(p) % 3 for p in phases)
        if counts[0] != 27 or counts[1] != 27 or counts[2] != 27:
            continue

        P0 = np.real((I81 + R_g + R_g @ R_g) / 3.0)
        U0, S0, _ = np.linalg.svd(P0)
        B0 = U0[:, :27]

        eig_vals_g, eig_vecs_g = np.linalg.eig(R_g)
        ph = np.angle(eig_vals_g)
        pos_phase = np.where((np.abs(ph) - 2 * np.pi / 3 < 0.3) & (ph > 0))[0]
        neg_phase = np.where((np.abs(ph) - 2 * np.pi / 3 < 0.3) & (ph < 0))[0]
        if len(pos_phase) != 27:
            continue

        V_omega = eig_vecs_g[:, pos_phase]
        B1_raw = np.real(V_omega)
        B2_raw = np.imag(V_omega)

        proj0 = B0 @ B0.T
        B1_comp = B1_raw - proj0 @ B1_raw
        Q1, _ = np.linalg.qr(B1_comp)
        B1 = Q1[:, :27]

        proj01 = np.hstack([B0, B1]) @ np.hstack([B0, B1]).T
        B2_comp = B2_raw - proj01 @ B2_raw
        Q2, _ = np.linalg.qr(B2_comp)
        if Q2.shape[1] < 27:
            continue
        B2 = Q2[:, :27]

        gens_full = [B0, B1, B2]
        Y_full = np.zeros((3, 3))
        for a in range(3):
            for b in range(a, 3):
                total = 0.0
                count = 0
                for i in range(27):
                    h_a = H @ gens_full[a][:, i]
                    start_j = i + 1 if a == b else 0
                    for j in range(start_j, 27):
                        h_b = H @ gens_full[b][:, j]
                        w = wedge_product(h_a, h_b)
                        bracket = d2 @ w
                        total += np.dot(bracket, bracket)
                        count += 1
                Y_full[a, b] = total / count if count > 0 else 0
                Y_full[b, a] = Y_full[a, b]

        y_eigs_full = np.sort(np.linalg.eigvalsh(Y_full))
        print(f"\n  Sample {s_idx}: Y eigenvalues = {y_eigs_full}")
        if y_eigs_full[0] > 1e-12:
            print(f"    Ratios: {y_eigs_full / y_eigs_full[0]}")
        print(f"    Tr(Y) = {np.trace(Y_full):.10f}")

    elapsed = time.time() - t0
    print(f"\n  Elapsed: {elapsed:.1f}s")

    results = {
        "n_order3_elements": len(order3_elements),
        "n_sampled": sample_size,
        "n_valid": len(all_eigenvalue_ratios),
        "n_unique_ratio_patterns": len(ratio_counts),
        "top_patterns": {
            str(k): v for k, v in sorted(ratio_counts.items(), key=lambda x: -x[1])[:5]
        },
        "elapsed_seconds": elapsed,
    }

    out = Path(__file__).resolve().parent.parent / "checks"
    out.mkdir(exist_ok=True)
    fname = out / f"PART_CVII_yukawa_universality_{int(time.time())}.json"
    with open(fname, "w") as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"  Wrote: {fname}")


if __name__ == "__main__":
    main()
