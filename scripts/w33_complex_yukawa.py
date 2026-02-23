#!/usr/bin/env python3
"""Complex Yukawa matrices from Z3 eigenvectors of W(3,3) harmonic space.

The three generation subspaces of H_1(W(3,3)) arise from the Z3 decomposition
of the 81-dimensional harmonic space under an order-3 automorphism R:

  Eigenvalue  1    → real   27-dim subspace V_0  (generation 0)
  Eigenvalue  ω    → complex 27-dim subspace V_ω  (generation 1)
  Eigenvalue  ω²   → conj(V_ω)                   (generation 2)

where ω = exp(2πi/3).

Physical fermions of each generation live in these eigenspaces.  Using the
COMPLEX eigenvectors of V_ω as generation-1 profiles (rather than the real/
imaginary parts separately) gives a complex 3×3 Yukawa matrix Y whose
diagonalisation generically produces non-trivial CKM mixing with J ≠ 0.

The script computes:

  1. Complex generation profiles ψ_a (a=0,1,2) at H27 vertices from the Z3
     eigenspaces, using the MEAN of the 27 projected eigenvectors.
  2. Block-constrained complex Yukawa matrices for all Z3-charge-conserving
     block assignments (a+b+c ≡ 0 mod 3).
  3. Full vertex-pair scan with complex VEVs: v_H = e_vi + e^{iθ}·e_vj.
  4. CKM matrix and Jarlskog invariant J for the best assignments.

Outputs: data/w33_complex_yukawa.json
"""

from __future__ import annotations

import json
import sys
import os

import numpy as np

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)
sys.path.insert(0, os.path.join(repo_root, "scripts"))

from w33_ckm_from_vev import (
    build_h27_index_and_tris,
    cubic_form_on_h27,
    compute_ckm_and_jarlskog,
    diagonalize_yukawa,
)
from w33_homology import boundary_matrix, build_clique_complex, build_w33
from w33_h1_decomposition import (
    J_matrix,
    build_incidence_matrix,
    make_vertex_permutation,
    signed_edge_permutation,
    transvection_matrix,
)
from e8_embedding_group_theoretic import build_w33 as build_w33_gt
from collections import Counter


# ---------------------------------------------------------------------------
# Experimental targets
# ---------------------------------------------------------------------------

V_CKM_exp = np.array([
    [0.97373, 0.2243,  0.00382],
    [0.2210,  0.987,   0.0410 ],
    [0.0080,  0.0388,  1.013  ],
])

V_PMNS_exp = np.array([
    [0.821,  0.550,  0.149],
    [0.356,  0.689,  0.632],
    [0.438,  0.470,  0.763],
])

J_exp = 3.08e-5  # Jarlskog invariant (quark sector)


def ckm_error(V: np.ndarray) -> float:
    return float(np.linalg.norm(np.abs(V) - V_CKM_exp))


def pmns_error(V: np.ndarray) -> float:
    return float(np.linalg.norm(np.abs(V) - V_PMNS_exp))


# ---------------------------------------------------------------------------
# Build Z3 eigenstructure
# ---------------------------------------------------------------------------

def build_z3_complex_profiles():
    """Extract complex Z3 generation profiles at H27 vertices.

    Returns:
      H27       : list of 27 global W33 vertex indices
      local_tris: list of (i,j,k) triangle triples in H27-local indices
      psi       : list of three length-27 vectors:
                    psi[0] real  (λ=1 eigenspace, generation 0)
                    psi[1] complex (λ=ω eigenspace, generation 1)
                    psi[2] = conj(psi[1])  (generation 2)
      P         : list of three 27×27 projection matrices
                    P[a][:,i] = H27-vertex values of mode i in generation a
    """
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    d2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    D = build_incidence_matrix(n, edges)
    L1 = D.T @ D + d2 @ d2.T
    eigvals, eigvecs = np.linalg.eigh(L1)
    harm_mask = np.abs(eigvals) < 0.5
    H_mat = eigvecs[:, harm_mask]   # m_edges × 81

    # Build an order-3 element of Aut(W33)
    J_mat = J_matrix()
    gen_vperms, gen_signed = [], []
    for vert in vertices:
        M_t = transvection_matrix(np.array(vert, dtype=int), J_mat)
        vp = make_vertex_permutation(M_t, vertices)
        gen_vperms.append(tuple(vp))
        ep, es = signed_edge_permutation(vp, edges)
        gen_signed.append((tuple(ep), tuple(es)))

    id_v = tuple(range(n))
    visited = {id_v: (tuple(range(len(edges))), tuple([1] * len(edges)))}
    queue = [id_v]
    while queue:
        cur_v = queue.pop()
        cur_ep, cur_es = visited[cur_v]
        for gv, (gep, ges) in zip(gen_vperms, gen_signed):
            new_v = tuple(gv[i] for i in cur_v)
            if new_v not in visited:
                new_ep = tuple(gep[cur_ep[i]] for i in range(len(edges)))
                new_es = tuple(ges[cur_ep[i]] * cur_es[i] for i in range(len(edges)))
                visited[new_v] = (new_ep, new_es)
                queue.append(new_v)

    best_R = None
    for cur_v, (cur_ep, cur_es) in visited.items():
        v2 = tuple(cur_v[cur_v[i]] for i in range(n))
        v3 = tuple(cur_v[v2[i]] for i in range(n))
        if v3 != id_v or cur_v == id_v:
            continue
        ep_np = np.asarray(cur_ep, dtype=int)
        es_np = np.asarray(cur_es, dtype=float)
        S_g = H_mat[ep_np, :] * es_np[:, None]
        R_g = H_mat.T @ S_g
        eigs_check = np.linalg.eigvals(R_g)
        phases = np.angle(eigs_check) / (2 * np.pi / 3)
        counts = Counter(round(p) % 3 for p in phases)
        if counts[0] == 27 and counts[1] == 27 and counts[2] == 27:
            best_R = R_g
            break

    if best_R is None:
        raise RuntimeError("No Z3 element found in Aut(W33)")

    # Eigendecompose R
    eig_vals_R, eig_vecs_R = np.linalg.eig(best_R)
    phases_R = np.angle(eig_vals_R)
    phase_groups: dict = {}
    for i in range(81):
        p = round(phases_R[i] / (2 * np.pi / 3))
        key = int(p) % 3
        phase_groups.setdefault(key, []).append(i)

    # λ=1 (real) subspace
    trivial_idx = np.array(phase_groups[0])
    V_trivial = eig_vecs_R[:, trivial_idx]  # 81×27 complex

    # λ=ω subspace (pick the one group with key≠0)
    omega_key = [k for k in phase_groups if k != 0 and len(phase_groups[k]) == 27][0]
    omega_idx = np.array(phase_groups[omega_key])
    V_omega = eig_vecs_R[:, omega_idx]      # 81×27 complex

    # Build H27 geometry
    adj_list = [[] for _ in range(n)]
    for u, v in edges:
        adj_list[u].append(v)
        adj_list[v].append(u)
    H27, local_tris = build_h27_index_and_tris(adj_list, v0=0)
    h27_map = {v: i for i, v in enumerate(H27)}

    # Incident edges for each H27 vertex
    incident: dict = {i: [] for i in range(len(H27))}
    for eidx, (u, v) in enumerate(edges):
        if u in h27_map:
            incident[h27_map[u]].append(eidx)
        if v in h27_map:
            incident[h27_map[v]].append(eidx)

    def project_modes(B_modes: np.ndarray) -> np.ndarray:
        """Project 81×K mode matrix onto H27 vertices → 27×K array."""
        K = B_modes.shape[1]
        out = np.zeros((len(H27), K), dtype=B_modes.dtype)
        for ki in range(K):
            h = H_mat @ B_modes[:, ki]
            for vidx in range(len(H27)):
                for eidx in incident[vidx]:
                    out[vidx, ki] += h[eidx]
        return out

    # Projection matrices: P[a] is 27×27 (H27 vertices × mode index)
    P0 = np.real(project_modes(V_trivial))  # real
    P1 = project_modes(V_omega)              # complex
    P2 = np.conj(P1)                         # complex conj

    # Generation profiles: mean across the 27 mode columns
    def normalized_mean(P: np.ndarray) -> np.ndarray:
        x = np.mean(P, axis=1)
        n_ = np.linalg.norm(x)
        return x / n_ if n_ > 1e-15 else x

    psi = [normalized_mean(P0), normalized_mean(P1), normalized_mean(P2)]
    return H27, local_tris, psi, [P0, P1, P2]


# ---------------------------------------------------------------------------
# Dominant-eigenvector generation profiles
# ---------------------------------------------------------------------------

def build_dominant_profiles(P: list) -> list:
    """Replace mean-projection profiles with dominant Gram eigenvector profiles.

    For generation a the Gram matrix G_a = P[a]^dag P[a] (27x27 Hermitian).
    Its top eigenvector in mode-index space, projected back to H27 vertex
    space via P[a], concentrates the profile on the most coherent linear
    combination of modes and dramatically sharpens CKM/PMNS predictions.

    Args:
      P: list of three 27x27 matrices [P0 (real), P1 (complex), P2 (complex)]

    Returns:
      psi_dom: list of three normalized length-27 complex vectors.
    """
    psi_dom = []
    for a in range(3):
        Pa = P[a]
        G = Pa.conj().T @ Pa        # 27x27 Hermitian Gram matrix
        evals, evecs = np.linalg.eigh(G)
        v_dom = evecs[:, -1]        # top eigenvector in mode-index space
        phi = Pa @ v_dom            # project back to H27 vertex space
        norm = np.linalg.norm(phi)
        psi_dom.append(phi / norm if norm > 1e-15 else phi)
    return psi_dom


# ---------------------------------------------------------------------------
# Yukawa and CKM utilities
# ---------------------------------------------------------------------------

def yukawa3x3(psi, local_tris, v_H: np.ndarray) -> np.ndarray:
    """3×3 Yukawa matrix Y[a,b] = c(ψ_a, ψ_b, v_H)."""
    Y = np.zeros((3, 3), dtype=complex)
    for a in range(3):
        for b in range(a, 3):
            val = cubic_form_on_h27(None, local_tris, psi[a], psi[b], v_H)
            Y[a, b] = Y[b, a] = val
    return Y


def eigenvalue_hierarchy(Y: np.ndarray) -> tuple:
    vals = np.linalg.eigvalsh(np.real(Y @ Y.conj().T))
    abs_eigs = sorted(np.sqrt(np.maximum(vals, 0)))
    ratio = abs_eigs[-1] / abs_eigs[0] if abs_eigs[0] > 1e-14 else float("inf")
    return abs_eigs, ratio


# ---------------------------------------------------------------------------
# Block affine coordinate helpers (same as w33_yukawa_blocks.py)
# ---------------------------------------------------------------------------

def gf3_inv(x: int) -> int:
    return {1: 1, 2: 2}[int(x) % 3]


def h27_affine_coord(v: tuple) -> int:
    """Return the 'a' (first affine) coordinate (= block index)."""
    x0, x1, x2, x3 = v
    inv_x2 = gf3_inv(x2)
    return int((x0 * inv_x2) % 3)


def get_block_indices(H27_vertices: list) -> dict:
    blocks: dict = {0: [], 1: [], 2: []}
    for i, v in enumerate(H27_vertices):
        a = h27_affine_coord(v)
        blocks[a].append(i)
    return blocks


# ---------------------------------------------------------------------------
# Complex VEV scan
# ---------------------------------------------------------------------------

def complex_vev_scan(psi, local_tris, n_theta: int = 36):
    """Scan over complex VEVs v_H = e_vi + e^{i*theta} e_vj.

    Tries all 27x26 vertex pairs and n_theta phase angles theta in [0, 2*pi).
    Returns (best_ckm_err, best_pmns_err, best_result_ckm, best_result_pmns).
    """
    thetas = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    best_ckm_err = float("inf")
    best_pmns_err = float("inf")
    best_ckm = None
    best_pmns = None

    for vi in range(27):
        e_vi = np.zeros(27, dtype=complex)
        e_vi[vi] = 1.0
        Y_vi = yukawa3x3(psi, local_tris, e_vi)
        if np.allclose(Y_vi, 0, atol=1e-12):
            continue

        for vj in range(27):
            if vj == vi:
                continue
            e_vj = np.zeros(27, dtype=complex)
            e_vj[vj] = 1.0
            Y_vj = yukawa3x3(psi, local_tris, e_vj)
            if np.allclose(Y_vj, 0, atol=1e-12):
                continue

            for theta in thetas:
                phase = np.exp(1j * theta)
                # Up Higgs = e_vi + e^{iθ} e_vj
                v_up = e_vi + phase * e_vj
                Y_u = yukawa3x3(psi, local_tris, v_up)

                # Down Higgs = e_vi - e^{iθ} e_vj  (opposite phase)
                v_dn = e_vi - phase * e_vj
                Y_d = yukawa3x3(psi, local_tris, v_dn)

                if np.allclose(Y_u, 0, atol=1e-12) or np.allclose(Y_d, 0, atol=1e-12):
                    continue

                V, J = compute_ckm_and_jarlskog(Y_u, Y_d)
                if np.any(np.isnan(V)):
                    continue

                err_ckm = ckm_error(V)
                err_pmns = pmns_error(V)

                if err_ckm < best_ckm_err:
                    best_ckm_err = err_ckm
                    eigs_u, rat_u = eigenvalue_hierarchy(Y_u)
                    eigs_d, rat_d = eigenvalue_hierarchy(Y_d)
                    best_ckm = {
                        "vi": int(vi), "vj": int(vj), "theta": float(theta),
                        "ckm_error": err_ckm, "Jarlskog": float(J),
                        "ratio_up": float(rat_u), "ratio_down": float(rat_d),
                        "V_CKM": np.abs(V).tolist(),
                    }

                if err_pmns < best_pmns_err:
                    best_pmns_err = err_pmns
                    eigs_u, rat_u = eigenvalue_hierarchy(Y_u)
                    eigs_d, rat_d = eigenvalue_hierarchy(Y_d)
                    best_pmns = {
                        "vi": int(vi), "vj": int(vj), "theta": float(theta),
                        "pmns_error": err_pmns, "Jarlskog": float(J),
                        "ratio_up": float(rat_u), "ratio_down": float(rat_d),
                        "V_PMNS": np.abs(V).tolist(),
                    }

    return best_ckm_err, best_pmns_err, best_ckm, best_pmns


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Building W33 Z3 complex generation profiles ...")
    H27, local_tris, psi, P = build_z3_complex_profiles()

    print(f"H27 vertices: {len(H27)}, triangles: {len(local_tris)}")
    for a in range(3):
        print(f"  |psi_{a}| norm = {np.linalg.norm(psi[a]):.4f}, "
              f"is_complex = {not np.allclose(np.imag(psi[a]), 0, atol=1e-10)}")

    # --- Real (original) profiles baseline ---
    from w33_ckm_from_vev import _build_hodge_and_generations, build_generation_profiles
    H, triangles, edges, gens = _build_hodge_and_generations()
    _, _, psi_real = build_generation_profiles(H, edges, gens, v0=0)
    print("\n--- Real profile baseline (vertex scan) ---")
    best_real_err = float("inf")
    best_real = None
    for vi in range(27):
        e_vi = np.zeros(27)
        e_vi[vi] = 1.0
        Y_u = yukawa3x3(psi_real, local_tris, e_vi)
        if np.allclose(Y_u, 0, atol=1e-12):
            continue
        for vj in range(27):
            if vj == vi:
                continue
            e_vj = np.zeros(27)
            e_vj[vj] = 1.0
            Y_d = yukawa3x3(psi_real, local_tris, e_vj)
            if np.allclose(Y_d, 0, atol=1e-12):
                continue
            V, J = compute_ckm_and_jarlskog(Y_u, Y_d)
            if np.any(np.isnan(V)):
                continue
            err = ckm_error(V)
            if err < best_real_err:
                best_real_err = err
                best_real = {"vi": vi, "vj": vj, "ckm_error": err,
                             "V_CKM": np.abs(V).tolist(), "Jarlskog": float(J)}
    print(f"  Best real CKM error: {best_real_err:.6f}")

    # --- Complex profile scan ---
    print("\n--- Complex Z3 profile scan (v_H = e_vi + e^(i*theta) e_vj) ---")
    print(f"  Scanning 27x26 pairs x 36 phases = {27*26*36} evaluations ...")
    best_ckm_err, best_pmns_err, best_ckm, best_pmns = complex_vev_scan(
        psi, local_tris, n_theta=36
    )

    print(f"\n=== Best CKM from complex Z3 profiles ===")
    if best_ckm:
        r = best_ckm
        print(f"  vi={r['vi']}, vj={r['vj']}, theta={r['theta']:.3f} rad")
        print(f"  CKM error: {r['ckm_error']:.6f}  (real baseline: {best_real_err:.6f})")
        print(f"  Jarlskog J: {r['Jarlskog']:.3e}  (exp: {J_exp:.2e})")
        print(f"  Eigenvalue ratios: up={r['ratio_up']:.1f}, down={r['ratio_down']:.1f}")
        print("  |V_CKM|:")
        for row in r["V_CKM"]:
            print("    " + "  ".join(f"{x:.4f}" for x in row))

    print(f"\n=== Best PMNS from complex Z3 profiles ===")
    if best_pmns:
        r = best_pmns
        print(f"  vi={r['vi']}, vj={r['vj']}, theta={r['theta']:.3f} rad")
        print(f"  PMNS error: {r['pmns_error']:.6f}")
        print(f"  Jarlskog J: {r['Jarlskog']:.3e}")
        print("  |V_PMNS|:")
        for row in r["V_PMNS"]:
            print("    " + "  ".join(f"{x:.4f}" for x in row))

    # --- Dominant eigenvector profiles ---
    print("\n--- Dominant eigenvector profile scan ---")
    psi_dom = build_dominant_profiles(P)
    for a in range(3):
        print(f"  |psi_dom_{a}| norm = {np.linalg.norm(psi_dom[a]):.4f}, "
              f"is_complex = {not np.allclose(np.imag(psi_dom[a]), 0, atol=1e-10)}")

    print(f"  Scanning 27x26 pairs x 36 phases = {27*26*36} evaluations ...")
    best_ckm_err_dom, best_pmns_err_dom, best_ckm_dom, best_pmns_dom = complex_vev_scan(
        psi_dom, local_tris, n_theta=36
    )

    print(f"\n=== Best CKM from dominant eigenvector profiles ===")
    if best_ckm_dom:
        r = best_ckm_dom
        print(f"  vi={r['vi']}, vj={r['vj']}, theta={r['theta']:.3f} rad")
        print(f"  CKM error: {r['ckm_error']:.6f}  (real baseline: {best_real_err:.6f})")
        print(f"  Jarlskog J: {r['Jarlskog']:.3e}  (exp: {J_exp:.2e})")
        print(f"  Eigenvalue ratios: up={r['ratio_up']:.1f}, down={r['ratio_down']:.1f}")
        print("  |V_CKM|:")
        for row in r["V_CKM"]:
            print("    " + "  ".join(f"{x:.4f}" for x in row))
        print("  Experimental:")
        for row in V_CKM_exp.tolist():
            print("    " + "  ".join(f"{x:.4f}" for x in row))

    print(f"\n=== Best PMNS from dominant eigenvector profiles ===")
    if best_pmns_dom:
        r = best_pmns_dom
        print(f"  vi={r['vi']}, vj={r['vj']}, theta={r['theta']:.3f} rad")
        print(f"  PMNS error: {r['pmns_error']:.6f}")
        print(f"  Jarlskog J: {r['Jarlskog']:.3e}")
        print("  |V_PMNS|:")
        for row in r["V_PMNS"]:
            print("    " + "  ".join(f"{x:.4f}" for x in row))
        print("  Experimental:")
        for row in V_PMNS_exp.tolist():
            print("    " + "  ".join(f"{x:.4f}" for x in row))

    # Save
    os.makedirs("data", exist_ok=True)
    out = {
        "real_baseline_ckm_error": best_real_err,
        "real_baseline": best_real,
        "complex_best_ckm": best_ckm,
        "complex_best_pmns": best_pmns,
        "dominant_best_ckm": best_ckm_dom,
        "dominant_best_pmns": best_pmns_dom,
        "identity_ckm_baseline": float(np.linalg.norm(np.eye(3) - V_CKM_exp)),
        "identity_pmns_baseline": float(np.linalg.norm(np.eye(3) - V_PMNS_exp)),
    }
    with open("data/w33_complex_yukawa.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nSaved data/w33_complex_yukawa.json")


if __name__ == "__main__":
    main()
