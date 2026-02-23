#!/usr/bin/env python3
"""Yukawa matrices from SU(3)^3 block decomposition of H27.

The 27 non-neighbours of a vertex in W(3,3) decompose under the affine
coordinate parameterisation as three 9-element blocks:

  Block 0 (a=0): (a,b,c) with a=0 in GF(3)^3
  Block 1 (a=1): (a,b,c) with a=1
  Block 2 (a=2): (a,b,c) with a=2

These correspond to the three SU(3)^3 representations in the E6 27-plet:
  27 = (3,3-bar,1) + (3-bar,1,3) + (1,3,3-bar)

Physical Yukawa matrices arise from contracting the E6 cubic invariant with
one factor from each block (for cross-block / (0,1,2) triangles):

  Y_up[a,b]   = C(X_a^{block1}, X_b^{block2}, v_Higgs^{block0})
  Y_down[a,b] = C(X_a^{block1}, X_b^{block0}, v_Higgs^{block2})

where X_a is the harmonic generation profile of generation a restricted to
the specified block, and v_Higgs is a uniform (or eigenvector) VEV in the
Higgs block.

This script computes these matrices, their eigenvalue spectra, Koide
parameters, and the resulting CKM mixing matrix.
"""

from __future__ import annotations

import json
import sys
import os
import itertools

import numpy as np

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)
sys.path.insert(0, os.path.join(repo_root, "scripts"))

from w33_ckm_from_vev import (
    _build_hodge_and_generations,
    build_h27_index_and_tris,
    build_generation_profiles,
    cubic_form_on_h27,
    compute_ckm_and_jarlskog,
)
from e8_embedding_group_theoretic import build_w33


# --------------------------------------------------------------------------
# GF(3) helpers
# --------------------------------------------------------------------------

def gf3_inv(x: int) -> int:
    return {1: 1, 2: 2}[int(x) % 3]


def h27_affine_coord(v: tuple) -> tuple:
    """Convert PG(3,3) homogeneous coord to affine (a,b,c) with x2=1."""
    # H27 vertices satisfy x2 != 0; normalize by dividing by x2
    x0, x1, x2, x3 = v
    inv_x2 = gf3_inv(x2)
    a = (x0 * inv_x2) % 3
    b = (x1 * inv_x2) % 3
    c = (x3 * inv_x2) % 3
    return a, b, c


def get_block_indices(H27_vertices: list) -> dict:
    """Return {0: [...], 1: [...], 2: [...]} mapping block -> H27 indices."""
    blocks: dict = {0: [], 1: [], 2: []}
    for i, v in enumerate(H27_vertices):
        a, b, c = h27_affine_coord(v)
        blocks[a].append(i)
    return blocks


# --------------------------------------------------------------------------
# Yukawa computation
# --------------------------------------------------------------------------

def restrict_to_block(X: np.ndarray, block: list) -> np.ndarray:
    """Return X with all entries zeroed out except those in `block`."""
    r = np.zeros(27)
    for i in block:
        r[i] = X[i]
    return r


def uniform_vev(block: list) -> np.ndarray:
    """Uniform unit vector supported on a block."""
    v = np.zeros(27)
    for i in block:
        v[i] = 1.0 / np.sqrt(len(block))
    return v


def yukawa_matrix(X_profiles, block_row, block_col, v_higgs, local_tris):
    """Compute 3x3 Yukawa matrix Y[a,b] = C(X_a^block_row, X_b^block_col, v_higgs)."""
    Y = np.zeros((3, 3), dtype=complex)
    for a in range(3):
        xa = restrict_to_block(X_profiles[a], block_row)
        for b in range(a, 3):
            xb = restrict_to_block(X_profiles[b], block_col)
            val = cubic_form_on_h27(None, local_tris, xa, xb, v_higgs)
            Y[a, b] = Y[b, a] = val
    return Y


def koide_parameter(m1: float, m2: float, m3: float) -> float:
    """Koide sum rule: Q = (m1+m2+m3)/(sqrt(m1)+sqrt(m2)+sqrt(m3))^2."""
    s = m1**0.5 + m2**0.5 + m3**0.5
    if abs(s) < 1e-15:
        return float("nan")
    return (m1 + m2 + m3) / s**2


# Experimental CKM magnitudes (PDG 2024)
V_CKM_exp = np.array([
    [0.97373, 0.2243, 0.00382],
    [0.2210, 0.987, 0.0410],
    [0.0080, 0.0388, 1.013],
])

# Experimental fermion masses at M_Z (GeV)
masses_GeV = {
    "u": 0.00216, "c": 1.27, "t": 172.4,
    "d": 0.00467, "s": 0.093, "b": 4.18,
    "e": 0.000511, "mu": 0.1057, "tau": 1.777,
}


def ckm_error(V: np.ndarray) -> float:
    """Frobenius norm of |V_CKM| - V_exp."""
    return float(np.linalg.norm(np.abs(V) - V_CKM_exp))


def eigenvalue_hierarchy(Y: np.ndarray) -> tuple:
    """Return sorted |eigenvalues| and max/min ratio of Y (real symmetric)."""
    eigs = np.linalg.eigvalsh(np.real(Y))
    abs_eigs = sorted(np.abs(eigs))
    if abs_eigs[0] < 1e-14:
        ratio = float("inf")
    else:
        ratio = abs_eigs[-1] / abs_eigs[0]
    return abs_eigs, ratio


def main(do_full_scan: bool = True, optimize: bool = False):
    print("Building W33 Hodge decomposition ...")
    H, triangles, edges, gens = _build_hodge_and_generations()

    n_w33, vertices_w33, adj_w33, _ = build_w33()
    v0_idx = 0
    neighbors_v0 = set(adj_w33[v0_idx])
    H27_idx_global = [i for i in range(n_w33) if i != v0_idx and i not in neighbors_v0]
    H27_vertices = [vertices_w33[i] for i in H27_idx_global]

    H27, local_tris, X_profiles = build_generation_profiles(H, edges, gens, v0=0)
    print(f"H27 size = {len(H27)}, triangles = {len(local_tris)}")

    # Identify blocks by affine first coordinate
    blocks = get_block_indices(H27_vertices)
    print("Block sizes:", {k: len(v) for k, v in blocks.items()})

    # Report generation profile norms per block
    print("\nGeneration profile norms per block:")
    for a in range(3):
        row = []
        for k in range(3):
            xr = restrict_to_block(X_profiles[a], blocks[k])
            row.append(f"||X{a}^B{k}||={np.linalg.norm(xr):.4f}")
        print(" ".join(row))

    # Compute block-projected Yukawa matrices for all assignments
    # Physical up-type:   C(X^B_row, X^B_col, v^B_vev)
    # Try all permutations of (row_block, col_block, vev_block)
    print("\n=== Scanning all (row, col, vev) block assignments ===")
    best_score = float("inf")
    best = None
    results = []

    for row_b, col_b, vev_b in itertools.permutations([0, 1, 2]):
        v_higgs = uniform_vev(blocks[vev_b])
        Y_up = yukawa_matrix(X_profiles, blocks[row_b], blocks[col_b], v_higgs, local_tris)
        # down-type uses the complementary block assignment (swap col and vev)
        v_higgs_d = uniform_vev(blocks[col_b])
        Y_down = yukawa_matrix(X_profiles, blocks[row_b], blocks[vev_b], v_higgs_d, local_tris)

        if np.allclose(Y_up, 0, atol=1e-12) or np.allclose(Y_down, 0, atol=1e-12):
            continue

        V, J = compute_ckm_and_jarlskog(Y_up, Y_down)
        err = ckm_error(V)

        abs_eigs_up, ratio_up = eigenvalue_hierarchy(Y_up)
        abs_eigs_down, ratio_dn = eigenvalue_hierarchy(Y_down)

        # Koide of down-sector (third, as charged-lepton proxy)
        if abs_eigs_down[0] > 1e-14:
            Q = koide_parameter(*abs_eigs_down)
        else:
            Q = float("nan")

        score = err + abs(Q - 2 / 3) if not np.isnan(Q) else err
        results.append({
            "blocks": (row_b, col_b, vev_b),
            "ckm_error": err,
            "koide_Q": Q,
            "score": score,
            "eigenvalues_up": abs_eigs_up,
            "eigenvalues_down": abs_eigs_down,
            "ratio_up": ratio_up,
            "ratio_down": ratio_dn,
            "V_CKM": np.abs(V).tolist(),
            "Jarlskog": J,
        })

        if score < best_score:
            best_score = score
            best = results[-1]
        print(f"  (B{row_b},B{col_b},v_B{vev_b}): CKM_err={err:.4f}, Q={Q:.4f}, "
              f"ratios=({ratio_up:.1f},{ratio_dn:.1f})")

    print("\n=== Best assignment ===")
    if best:
        print(f"Blocks: {best['blocks']}")
        print(f"CKM error: {best['ckm_error']:.6f}")
        print(f"Koide Q: {best['koide_Q']:.6f}")
        print(f"Eigenvalue hierarchies: up={[f'{e:.4f}' for e in best['eigenvalues_up']]}")
        print(f"                       down={[f'{e:.4f}' for e in best['eigenvalues_down']]}")
        print("|V_CKM|:")
        for row in best["V_CKM"]:
            print("  " + "  ".join(f"{x:.4f}" for x in row))
        print("Jarlskog J:", best["Jarlskog"])

    if do_full_scan:
        # Scan ALL pairs (vi, vj) of H27 vertex VEVs using full generation profiles.
        print("\n=== Full vertex-pair VEV scan (27x26 pairs, full X profiles) ===")
        best_ckm_err = float("inf")
        best_vertex_result = None

        def yukawa_full(v):
            """Yukawa using FULL (un-restricted) generation profiles."""
            Y = np.zeros((3, 3), dtype=complex)
            for a in range(3):
                for b in range(a, 3):
                    val = cubic_form_on_h27(None, local_tris, X_profiles[a], X_profiles[b], v)
                    Y[a, b] = Y[b, a] = val
            return Y

        for vi in range(27):
            e_vi = np.zeros(27)
            e_vi[vi] = 1.0
            Y_u = yukawa_full(e_vi)
            if np.allclose(Y_u, 0, atol=1e-12):
                continue
            for vj in range(27):
                if vj == vi:
                    continue
                e_vj = np.zeros(27)
                e_vj[vj] = 1.0
                Y_d = yukawa_full(e_vj)
                if np.allclose(Y_d, 0, atol=1e-12):
                    continue

                V, J = compute_ckm_and_jarlskog(Y_u, Y_d)
                err = ckm_error(V)
                if err < best_ckm_err:
                    abs_eigs_u, ratio_u = eigenvalue_hierarchy(Y_u)
                    abs_eigs_d, ratio_d = eigenvalue_hierarchy(Y_d)
                    a_vi, b_vi, c_vi = h27_affine_coord(H27_vertices[vi])
                    a_vj, b_vj, c_vj = h27_affine_coord(H27_vertices[vj])
                    best_ckm_err = err
                    best_vertex_result = {
                        "vi_up": vi,
                        "vj_down": vj,
                        "v_up_pg": list(H27_vertices[vi]),
                        "v_dn_pg": list(H27_vertices[vj]),
                        "v_up_affine": (a_vi, b_vi, c_vi),
                        "v_dn_affine": (a_vj, b_vj, c_vj),
                        "v_up_block": a_vi,
                        "v_dn_block": a_vj,
                        "ckm_error": err,
                        "Jarlskog": float(J),
                        "ratio_up": float(ratio_u),
                        "ratio_down": float(ratio_d),
                        "eigenvalues_up": [float(x) for x in abs_eigs_u],
                        "eigenvalues_down": [float(x) for x in abs_eigs_d],
                        "V_CKM": np.abs(V).tolist(),
                    }

        if best_vertex_result:
            r = best_vertex_result
            print(f"Best pair: H27[{r['vi_up']}]={r['v_up_pg']} (up) vs "
                  f"H27[{r['vj_down']}]={r['v_dn_pg']} (down)")
            print(f"  Affine: up={r['v_up_affine']} (Block {r['v_up_block']}), "
                  f"dn={r['v_dn_affine']} (Block {r['v_dn_block']})")
            print(f"  CKM error = {r['ckm_error']:.6f}  (identity baseline ~0.32)")
            print(f"  Eigenvalue hierarchy (up): 1 : "
                  f"{r['eigenvalues_up'][1]/r['eigenvalues_up'][0]:.1f} : "
                  f"{r['eigenvalues_up'][2]/r['eigenvalues_up'][0]:.1f}")
            print(f"  Eigenvalue hierarchy (dn): 1 : "
                  f"{r['eigenvalues_down'][1]/r['eigenvalues_down'][0]:.1f} : "
                  f"{r['eigenvalues_down'][2]/r['eigenvalues_down'][0]:.1f}")
            print("  |V_CKM|:")
            for row in r["V_CKM"]:
                print("    " + "  ".join(f"{x:.4f}" for x in row))
            print(f"  Jarlskog J = {r['Jarlskog']:.6f}")

        if optimize and best_vertex_result:
            # try random perturbations mixing the best up/down vertices with others
            print("\n=== Perturbation optimization around best pair ===")
            vi0 = best_vertex_result['vi_up']
            vj0 = best_vertex_result['vj_down']
            base_err = best_vertex_result['ckm_error']
            # perform a few random linear combinations of two vertices
            for trial in range(200):
                # choose neighbor vertex within same block for up or down
                vi1 = np.random.choice([i for i in range(27) if i != vi0])
                vj1 = np.random.choice([j for j in range(27) if j != vj0])
                alpha = np.random.rand()
                v_up = np.zeros(27); v_up[vi0] = alpha; v_up[vi1] = 1 - alpha
                v_dn = np.zeros(27); v_dn[vj0] = alpha; v_dn[vj1] = 1 - alpha
                Yu = yukawa_full(v_up); Yd = yukawa_full(v_dn)
                if np.allclose(Yu,0) or np.allclose(Yd,0):
                    continue
                V, J = compute_ckm_and_jarlskog(Yu, Yd)
                err = ckm_error(V)
                if err < base_err:
                    base_err = err
                    best_vertex_result.update({
                        'vi_up': vi0, 'vj_down': vj0,
                        'ckm_error': err,
                        'V_CKM': np.abs(V).tolist(),
                    })
            print(f"Optimized CKM error: {base_err:.6f} (was {best_ckm_err:.6f})")

    # Save results
    os.makedirs("data", exist_ok=True)
    out = {
        "block_scan": [
            {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in r.items()}
            for r in results
        ],
        "best_block": {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in best.items()} if best else None,
        "vertex_scan_best": {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in best_vertex_result.items()} if best_vertex_result else None,
    }
    with open("data/w33_yukawa_blocks.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nSaved data/w33_yukawa_blocks.json")


if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser(description="Compute Yukawa/CKM data from W33 H27 profiles")
        parser.add_argument("--full-vertex-scan", action="store_true",
                            help="Perform the full 27x26 vertex-pair scan (default).")
        parser.add_argument("--quick-optimize", action="store_true",
                            help="After finding best pair, try random 2-vertex mixtures to improve CKM.")
        parser.add_argument("--no-scan", action="store_true",
                            help="Skip the full vertex-pair scan (for quick tests).")
        args = parser.parse_args()

        # run main but control scanning behaviour via flags
        # we patch global variables inside main for simplicity
        # call main with appropriate options
        main(do_full_scan=not args.no_scan, optimize=args.quick_optimize)
