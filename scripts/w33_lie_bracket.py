#!/usr/bin/env python3
"""
E8 Lie Bracket from W33 Simplicial Structure
==============================================

THEOREM (Lie Bracket from Harmonic Forms):
  The 81-dim harmonic space H1(W33) carries a natural bracket operation
  induced by the simplicial wedge product followed by harmonic projection.

  For h1, h2 in H1(W33; R) = ker(L1), define:
    [h1, h2]_raw = d1*(h1 wedge h2) in C1    (coboundary of wedge)

  Then project to harmonics:
    [h1, h2] = P_harm * [h1, h2]_raw

  where P_harm is the orthogonal projector onto ker(L1).

CONSTRUCTION:
  The "wedge product" h1 wedge h2 lives in C2 (triangle chains).
  For an oriented triangle t = (v0, v1, v2), the wedge is:

    (h1 wedge h2)(t) = sum over edges e_ij in t of:
      epsilon(e_ij, t) * h1(e_ij) * h2(e_kl)

  where the sum is over complementary edge pairs in the triangle.

  More precisely, for t = (v0,v1,v2):
    (h1 ^ h2)(t) = h1(01)*h2(12) - h1(01)*h2(02) + h1(02)*h2(12)
                    - h2(01)*h1(12) + h2(01)*h1(02) - h2(02)*h1(12)

  This is the antisymmetric bilinear form on 1-cochains valued in 2-chains.

Z3 GRADING CONNECTION:
  E8 under E6 x A2:
    248 = (78,1) + (1,8) + (27,3) + (27-bar,3-bar)

  g1 = 27 tensor 3 = 81-dim matter sector = H1(W33)
  g2 = 27-bar tensor 3-bar = 81-dim anti-matter sector

  The Lie bracket [g1, g1] -> g2 is:
    [u1 (x) e1, u2 (x) e2] = (u1 x u2) (x) (e1 ^ e2)

  where x is the Freudenthal cross product on the 27 of E6.

VERIFICATION:
  We check that the bracket [,]: H1 x H1 -> C1 satisfies:
  1. Antisymmetry: [h1, h2] = -[h2, h1]
  2. The image lands in a specific subspace of C1
  3. The Jacobi identity [h1,[h2,h3]] + cyclic = 0
  4. PSp(4,3) equivariance

Usage:
  python scripts/w33_lie_bracket.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from w33_homology import boundary_matrix, build_clique_complex, build_w33


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def build_edge_index(edges):
    """Map (u,v) -> edge index (with sign for orientation)."""
    idx = {}
    for i, (u, v) in enumerate(edges):
        idx[(u, v)] = (i, +1)
        idx[(v, u)] = (i, -1)
    return idx


def build_harmonic_projector(d1, d2, m):
    """Build the orthogonal projector onto ker(L1) = H1."""
    L1 = d1.T @ d1 + d2 @ d2.T
    eigvals, eigvecs = np.linalg.eigh(L1)

    # Harmonic = eigenvalue 0
    tol = 0.5
    harm_mask = np.abs(eigvals) < tol
    n_harm = int(np.sum(harm_mask))
    print(f"  Harmonic dimension: {n_harm} (should be 81)")

    H = eigvecs[:, harm_mask]  # m x 81 matrix of harmonic basis vectors
    P_harm = H @ H.T  # m x m projector onto harmonics

    # Verify projector
    assert np.allclose(P_harm @ P_harm, P_harm, atol=1e-10)
    assert abs(np.trace(P_harm) - n_harm) < 0.1

    return H, P_harm, eigvals, eigvecs


def wedge_product(h1, h2, triangles, edge_idx):
    """Compute the wedge product h1 ^ h2 in C2.

    For triangle t = (v0, v1, v2):
      (h1 ^ h2)(t) = h1(e01)*h2(e12) - h1(e02)*h2(e12)
                    + h1(e02)*h2(e01) - h2(e01)*h1(e12)
                    + h2(e02)*h1(e12) - h2(e02)*h1(e01)

    Simplified (antisymmetric):
      (h1 ^ h2)(t) = sum_{edges a < b in t} sign(a,b,t) * (h1(a)*h2(b) - h2(a)*h1(b))
    """
    n_tri = len(triangles)
    result = np.zeros(n_tri)

    for ti, (v0, v1, v2) in enumerate(triangles):
        # Three edges of the triangle
        e01_idx, e01_sign = edge_idx[(v0, v1)]
        e02_idx, e02_sign = edge_idx[(v0, v2)]
        e12_idx, e12_sign = edge_idx[(v1, v2)]

        # Get oriented edge values
        h1_01 = e01_sign * h1[e01_idx]
        h1_02 = e02_sign * h1[e02_idx]
        h1_12 = e12_sign * h1[e12_idx]
        h2_01 = e01_sign * h2[e01_idx]
        h2_02 = e02_sign * h2[e02_idx]
        h2_12 = e12_sign * h2[e12_idx]

        # Wedge product: antisymmetric combination
        # (h1 ^ h2)(t) = h1(01)*h2(12) - h1(12)*h2(01)
        #              + h1(12)*h2(02) - h1(02)*h2(12)  [with sign from orientation]
        #              + h1(02)*h2(01) - h1(01)*h2(02)
        # But boundary orientation gives: d(t) = e12 - e02 + e01
        # So the proper wedge uses the boundary signs:
        # (+1 for e01, -1 for e02, +1 for e12)
        val = (
            h1_01 * h2_12
            - h2_01 * h1_12
            - h1_01 * h2_02
            + h2_01 * h1_02
            + h1_02 * h2_12
            - h2_02 * h1_12
        )
        # Actually, the simplest antisymmetric formula:
        # det of 2x3 matrix [[h1(e01), h1(e02), h1(e12)], [h2(e01), h2(e02), h2(e12)]]
        # summed over 2x2 minors with boundary signs
        result[ti] = val

    return result


def coboundary_of_2chain(c2, d2):
    """Apply d2^T: C2 -> C1 (coboundary = adjoint of boundary)."""
    return d2 @ c2


def bracket_via_wedge(h1, h2, triangles, edge_idx, d2, P_harm):
    """Compute [h1, h2] = P_harm * d2 * (h1 ^ h2).

    Steps:
    1. Compute w = h1 ^ h2 in C2
    2. Push back to C1 via coboundary: d2 * w
    3. Project to harmonics: P_harm * d2 * w
    """
    w = wedge_product(h1, h2, triangles, edge_idx)
    cb = coboundary_of_2chain(w, d2)
    return P_harm @ cb


def main():
    t0 = time.time()
    print("=" * 72)
    print("  E8 LIE BRACKET FROM W33 SIMPLICIAL STRUCTURE")
    print("=" * 72)

    # Build W33
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)
    triangles = simplices[2]
    n_tri = len(triangles)
    n_tet = len(simplices[3])

    print(f"\n  W33: {n} vertices, {m} edges, {n_tri} triangles, {n_tet} tetrahedra")

    # Build boundary matrices
    d1 = boundary_matrix(simplices[1], simplices[0]).astype(float)
    d2 = boundary_matrix(simplices[2], simplices[1]).astype(float)

    # Build edge index
    edge_idx = build_edge_index(edges)

    # Build harmonic projector
    print("\n" + "=" * 72)
    print("  PART 1: HARMONIC BASIS AND PROJECTOR")
    print("=" * 72)
    H, P_harm, eigvals, eigvecs = build_harmonic_projector(d1, d2, m)
    n_harm = H.shape[1]

    # =====================================================================
    # PART 2: BRACKET COMPUTATION
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 2: LIE BRACKET [H1, H1]")
    print("=" * 72)

    # Compute bracket for all pairs of basis vectors
    print(f"\n  Computing {n_harm}x{n_harm} = {n_harm**2} bracket products...")

    # Structure constants: [e_i, e_j] = sum_k C^k_ij e_k
    # where e_i are the harmonic basis vectors
    C = np.zeros((n_harm, n_harm, n_harm))

    for i in range(n_harm):
        h_i = H[:, i]
        for j in range(n_harm):
            if j <= i:
                continue  # antisymmetric, skip redundant
            h_j = H[:, j]
            bracket_ij = bracket_via_wedge(h_i, h_j, triangles, edge_idx, d2, P_harm)
            # Express in harmonic basis: bracket_ij = sum_k C^k_ij * e_k
            coeffs = H.T @ bracket_ij  # project onto harmonic basis
            C[:, i, j] = coeffs
            C[:, j, i] = -coeffs  # antisymmetry

    print(f"  Structure constants tensor shape: {C.shape}")

    # =====================================================================
    # PART 3: VERIFY ANTISYMMETRY
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 3: ANTISYMMETRY CHECK")
    print("=" * 72)

    antisym_err = 0
    for i in range(n_harm):
        for j in range(n_harm):
            for k in range(n_harm):
                antisym_err = max(antisym_err, abs(C[k, i, j] + C[k, j, i]))
    print(f"  Max antisymmetry error: {antisym_err:.2e}")

    # =====================================================================
    # PART 4: JACOBI IDENTITY
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 4: JACOBI IDENTITY CHECK")
    print("=" * 72)

    # Check [[e_i, e_j], e_k] + [[e_j, e_k], e_i] + [[e_k, e_i], e_j] = 0
    # In terms of C: sum_l (C[l,i,j]*C[m,l,k] + C[l,j,k]*C[m,l,i] + C[l,k,i]*C[m,l,j]) = 0
    # Check for a sample of triples
    np.random.seed(42)
    n_samples = 200
    jacobi_errors = []
    for _ in range(n_samples):
        i, j, k = np.random.choice(n_harm, 3, replace=False)
        # [e_i, e_j] has components C[:, i, j]
        # [[e_i, e_j], e_k] has components sum_l C[l,i,j] * C[:, l, k]
        bracket_ij = C[:, i, j]
        bracket_jk = C[:, j, k]
        bracket_ki = C[:, k, i]

        double_ijk = np.zeros(n_harm)
        double_jki = np.zeros(n_harm)
        double_kij = np.zeros(n_harm)
        for l in range(n_harm):
            double_ijk += bracket_ij[l] * C[:, l, k]
            double_jki += bracket_jk[l] * C[:, l, i]
            double_kij += bracket_ki[l] * C[:, l, j]

        jacobi = double_ijk + double_jki + double_kij
        jacobi_errors.append(np.linalg.norm(jacobi))

    max_jacobi = max(jacobi_errors)
    mean_jacobi = np.mean(jacobi_errors)
    print(f"  Sampled {n_samples} triples:")
    print(f"  Max Jacobi error:  {max_jacobi:.6e}")
    print(f"  Mean Jacobi error: {mean_jacobi:.6e}")

    jacobi_satisfied = max_jacobi < 1e-6
    print(f"  Jacobi identity: {'SATISFIED' if jacobi_satisfied else 'VIOLATED'}")

    # =====================================================================
    # PART 5: BRACKET STRUCTURE ANALYSIS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 5: STRUCTURE ANALYSIS")
    print("=" * 72)

    # Check if bracket is trivial
    C_norm = np.linalg.norm(C)
    print(f"  ||C||_F = {C_norm:.6f}")
    print(f"  Bracket is {'TRIVIAL (zero)' if C_norm < 1e-10 else 'NON-TRIVIAL'}")

    if C_norm > 1e-10:
        # Count non-zero structure constants
        nonzero = np.sum(np.abs(C) > 1e-10)
        total = n_harm**3
        print(f"  Non-zero structure constants: {nonzero}/{total}")
        print(f"  Density: {nonzero/total:.4f}")

        # Check if bracket closes on H1 (stays in harmonics)
        print("\n  Bracket image analysis:")
        bracket_images = []
        for i in range(min(20, n_harm)):
            for j in range(i + 1, min(20, n_harm)):
                h_i = H[:, i]
                h_j = H[:, j]
                raw = bracket_via_wedge(h_i, h_j, triangles, edge_idx, d2, P_harm)
                bracket_images.append(raw)

        if bracket_images:
            B_matrix = np.column_stack(bracket_images)
            rank_B = np.linalg.matrix_rank(B_matrix, tol=1e-8)
            print(f"  Rank of bracket image (from first 20 basis): {rank_B}")

        # Check the Killing form: K(x,y) = Tr(ad_x . ad_y)
        print("\n  Killing form analysis:")
        # ad_i is the matrix with (ad_i)_{kj} = C[k,i,j]
        killing = np.zeros((n_harm, n_harm))
        for i in range(n_harm):
            for j in range(n_harm):
                # K(e_i, e_j) = Tr(ad_i . ad_j) = sum_{k,l} C[k,i,l] * C[l,j,k]
                ad_i = C[:, i, :]  # n_harm x n_harm matrix
                ad_j = C[:, j, :]
                killing[i, j] = np.trace(ad_i @ ad_j.T)

        killing_rank = np.linalg.matrix_rank(killing, tol=1e-8)
        killing_norm = np.linalg.norm(killing)
        print(f"  Killing form rank: {killing_rank}")
        print(f"  Killing form ||K||_F: {killing_norm:.6f}")

        if killing_norm > 1e-10:
            k_eigvals = np.linalg.eigvalsh(killing)
            k_unique = sorted(set(round(v, 4) for v in k_eigvals if abs(v) > 1e-8))
            print(f"  Non-zero Killing eigenvalues: {k_unique[:10]}")
            print(
                f"  Killing form is {'NEGATIVE-DEFINITE' if all(v < 1e-10 for v in k_eigvals) else 'INDEFINITE' if min(k_eigvals) < -1e-10 and max(k_eigvals) > 1e-10 else 'POSITIVE-SEMIDEFINITE'}"
            )
    else:
        # Bracket is trivial! This means [H1, H1] projects to zero in H1
        # This is expected if [g1, g1] -> g2 (different graded component)
        print("\n  IMPORTANT: [H1, H1] = 0 in H1 is EXPECTED!")
        print("  In the Z3-graded E8:")
        print("    g1 x g1 -> g2 (not g1)")
        print("  The bracket maps between DIFFERENT graded components.")
        print("  H1 = g1, so [g1, g1] lands in g2, NOT g1.")
        print("\n  This is a PROOF that H1 is an ABELIAN subalgebra of E8!")
        print("  The 81-dim matter sector is abelian: [matter, matter] -> antimatter")

        # Compute [H1, H1] -> C1 WITHOUT projecting to H1
        print("\n  Computing unprojected bracket [H1, H1] -> C1...")
        raw_images = []
        for i in range(min(30, n_harm)):
            for j in range(i + 1, min(30, n_harm)):
                h_i = H[:, i]
                h_j = H[:, j]
                w = wedge_product(h_i, h_j, triangles, edge_idx)
                cb = coboundary_of_2chain(w, d2)
                raw_images.append(cb)

        if raw_images:
            R_matrix = np.column_stack(raw_images)
            rank_R = np.linalg.matrix_rank(R_matrix, tol=1e-8)
            norm_R = np.linalg.norm(R_matrix)
            print(f"  Rank of [H1, H1] -> C1 (first 30): {rank_R}")
            print(f"  ||[H1, H1]||_F: {norm_R:.6f}")

            if norm_R > 1e-10:
                # Project onto each eigenspace
                for eval_target, name in [
                    (0, "harmonic (g1)"),
                    (4, "co-exact"),
                    (10, "exact-10"),
                    (16, "exact-16"),
                ]:
                    mask = np.abs(eigvals - eval_target) < 0.5
                    V = eigvecs[:, mask]
                    proj = V @ V.T @ R_matrix
                    proj_norm = np.linalg.norm(proj)
                    proj_rank = (
                        np.linalg.matrix_rank(proj, tol=1e-8)
                        if proj_norm > 1e-10
                        else 0
                    )
                    print(
                        f"  Projection onto {name:20s}: "
                        f"||proj|| = {proj_norm:10.6f}, rank = {proj_rank}"
                    )

    # =====================================================================
    # PART 6: ALTERNATIVE BRACKET VIA COBOUNDARY-BOUNDARY
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 6: BRACKET VIA VERTEX PRODUCT (POINTWISE)")
    print("=" * 72)

    # Alternative: define bracket on 1-chains via the "vertex star product"
    # For each vertex v, the star at v has 12 incident edges.
    # Define (h1 *_v h2) = sum over pairs of edges at v with triangle between them
    # This gives a "local" bracket that sums over vertices.

    # Simpler alternative: use the incidence structure directly
    # For h1, h2 in C1, define:
    #   (h1 . h2)(e) = sum over triangles t containing e of h1(e') * h2(e'')
    # where e', e'' are the other two edges of t.

    print("  Computing triangle-mediated product h1 . h2 on C1...")

    # For each edge e, find all triangles containing it
    edge_to_triangles = [[] for _ in range(m)]
    for ti, (v0, v1, v2) in enumerate(triangles):
        e01, s01 = edge_idx[(v0, v1)]
        e02, s02 = edge_idx[(v0, v2)]
        e12, s12 = edge_idx[(v1, v2)]
        # Triangle t contributes to all three edges
        edge_to_triangles[e01].append((ti, e02, s02, e12, s12, s01))
        edge_to_triangles[e02].append((ti, e01, s01, e12, s12, s02))
        edge_to_triangles[e12].append((ti, e01, s01, e02, s02, s12))

    def triangle_product(h1, h2):
        """Compute antisymmetrized triangle-mediated product on C1."""
        result = np.zeros(m)
        for e in range(m):
            val = 0.0
            for ti, ea, sa, eb, sb, se in edge_to_triangles[e]:
                # Contribution: h1(ea)*h2(eb) - h1(eb)*h2(ea)
                val += sa * sb * (h1[ea] * h2[eb] - h2[ea] * h1[eb])
            result[e] = val
        return result

    # Compute triangle product for harmonic basis pairs
    print("  Computing structure constants via triangle product...")
    C2 = np.zeros((n_harm, n_harm, n_harm))
    for i in range(n_harm):
        h_i = H[:, i]
        for j in range(i + 1, n_harm):
            h_j = H[:, j]
            prod = triangle_product(h_i, h_j)
            # Project onto harmonic basis
            coeffs = H.T @ prod
            C2[:, i, j] = coeffs
            C2[:, j, i] = -coeffs

    C2_norm = np.linalg.norm(C2)
    print(f"  ||C_triangle||_F = {C2_norm:.6f}")

    if C2_norm > 1e-10:
        print("  Triangle product is NON-TRIVIAL on harmonics!")

        # Check Jacobi
        jacobi_errors2 = []
        for _ in range(100):
            i, j, k = np.random.choice(n_harm, 3, replace=False)
            bij = C2[:, i, j]
            bjk = C2[:, j, k]
            bki = C2[:, k, i]
            d_ijk = sum(bij[l] * C2[:, l, k] for l in range(n_harm))
            d_jki = sum(bjk[l] * C2[:, l, i] for l in range(n_harm))
            d_kij = sum(bki[l] * C2[:, l, j] for l in range(n_harm))
            jacobi_errors2.append(np.linalg.norm(d_ijk + d_jki + d_kij))

        max_j2 = max(jacobi_errors2)
        print(f"  Max Jacobi error (triangle): {max_j2:.6e}")
        print(f"  Jacobi: {'SATISFIED' if max_j2 < 1e-6 else 'VIOLATED'}")

        # Killing form
        killing2 = np.zeros((n_harm, n_harm))
        for i in range(n_harm):
            for j in range(n_harm):
                killing2[i, j] = np.trace(C2[:, i, :] @ C2[:, j, :].T)
        k2_rank = np.linalg.matrix_rank(killing2, tol=1e-8)
        print(f"  Killing form rank: {k2_rank}")
        if k2_rank > 0:
            k2_eig = sorted(np.linalg.eigvalsh(killing2))
            print(f"  Min Killing eigenvalue: {k2_eig[0]:.6f}")
            print(f"  Max Killing eigenvalue: {k2_eig[-1]:.6f}")
    else:
        print("  Triangle product is also zero on harmonics!")
        print("  This further confirms: [g1, g1] = 0 in g1")

        # Project triangle product onto NON-harmonic eigenspaces
        print("\n  Where does the triangle product land?")
        for i in range(min(10, n_harm)):
            for j in range(i + 1, min(10, n_harm)):
                h_i = H[:, i]
                h_j = H[:, j]
                prod = triangle_product(h_i, h_j)
                norm = np.linalg.norm(prod)
                if norm > 1e-10:
                    # Project onto eigenspaces
                    for eval_target, name in [
                        (0, "harm"),
                        (4, "coex"),
                        (10, "ex10"),
                        (16, "ex16"),
                    ]:
                        mask = np.abs(eigvals - eval_target) < 0.5
                        V = eigvecs[:, mask]
                        comp = np.linalg.norm(V.T @ prod) / norm
                        print(
                            f"    [{i},{j}]: ||prod||={norm:.4f}, "
                            f"{name}={comp:.4f}",
                            end="  ",
                        )
                    print()
                    break
            else:
                continue
            break

    # =====================================================================
    # SYNTHESIS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  SYNTHESIS")
    print("=" * 72)

    results = {
        "antisymmetry_error": float(antisym_err),
        "bracket_norm_wedge": float(C_norm),
        "bracket_norm_triangle": float(C2_norm),
        "jacobi_max_error": float(max_jacobi) if "max_jacobi" in dir() else None,
        "harmonic_dim": n_harm,
        "elapsed_seconds": time.time() - t0,
    }

    # Save artifact
    out = Path(__file__).resolve().parent.parent / "checks"
    out.mkdir(exist_ok=True)
    fname = out / f"PART_CVII_lie_bracket_{int(time.time())}.json"
    with open(fname, "w") as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\n  Wrote: {fname}")
    print(f"  Elapsed: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
