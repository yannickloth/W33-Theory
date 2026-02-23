#!/usr/bin/env python3
"""
THEORY_PART_CLXXIV_YUKAWA_OPTIMIZATION.py
Pillar 65: Full C^27 Yukawa Tensor Gradient Optimization

========================================================================
CORE INSIGHT
========================================================================

Y(v_H) is a 3x3 complex matrix that depends LINEARLY on the Higgs VEV
v_H ∈ C^27 (by trilinearity of the E6 cubic form c(ψ_a, ψ_b, v_H)).

This means we can:
  1.  Build the full 3×3×27 Yukawa tensor T[a,b,k] = c(ψ_a, ψ_b, e_k)
      in 27 function evaluations.

  2.  Compute Y_up = T · v_up and Y_dn = T · v_dn instantly (matrix-vector
      products), replacing the O(27²×36) loop each time.

  3.  Optimize the CKM error ||abs(V_CKM(v_up,v_dn)) - V_exp||_F over
      the FULL C^27 × C^27 search space (108 real parameters) using
      gradient descent — reaching far below the coarse grid's 0.057.

Key new results:
  * Tensor rank analysis: how many independent Yukawa structures exist?
  * Minimum achievable CKM error over all v_H ∈ C^27?
  * Optimal Higgs VEV direction — is V_ub suppressed?
  * 7-dimensional active subspace (matches Gram rank = 7)
========================================================================
"""

from __future__ import annotations
import json, sys, os, time
import numpy as np
from scipy.optimize import minimize

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
sys.path.insert(0, repo_root)
sys.path.insert(0, os.path.join(repo_root, "scripts"))

from w33_complex_yukawa import (
    build_z3_complex_profiles, build_dominant_profiles,
    ckm_error, pmns_error,
)
from w33_ckm_from_vev import compute_ckm_and_jarlskog, cubic_form_on_h27

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


# ---------------------------------------------------------------------------
# Step 1: Build the Yukawa tensor
# ---------------------------------------------------------------------------

def build_yukawa_tensor(psi_dom, local_tris):
    """Build T[a,b,k] = c(psi_dom[a], psi_dom[b], e_k) for k=0..26.

    T is 3×3×27 (complex). Y(v_H) = einsum('abk,k->ab', T, v_H).
    """
    n27 = len(psi_dom[0])
    T = np.zeros((3, 3, n27), dtype=complex)
    for k in range(n27):
        e_k = np.zeros(n27, dtype=complex)
        e_k[k] = 1.0
        for a in range(3):
            for b in range(a, 3):
                val = cubic_form_on_h27(None, local_tris, psi_dom[a], psi_dom[b], e_k)
                T[a, b, k] = val
                T[b, a, k] = val  # symmetric
    return T


def yukawa_fast(T, v_H):
    """Y(v_H) = sum_k T[:,:,k] * v_H[k].  Fast via einsum."""
    return np.einsum("abk,k->ab", T, v_H)


# ---------------------------------------------------------------------------
# Step 2: Analyse the Yukawa tensor
# ---------------------------------------------------------------------------

def analyse_yukawa_tensor(T):
    """Rank, singular values, and active subspace of the Yukawa map."""
    print("\n" + "="*70)
    print("YUKAWA TENSOR ANALYSIS")
    print("="*70)

    # Reshape T as 9×27 matrix (rows = flattened Y entries, cols = v_H modes)
    T_mat = T.reshape(9, 27)  # complex 9×27
    U, s, Vh = np.linalg.svd(T_mat, full_matrices=False)
    rank = int(np.sum(s > 1e-10))

    print(f"  Tensor shape: 3×3×27 (flattened as 9×27 complex matrix)")
    print(f"  Singular values: {[f'{sv:.4f}' for sv in s]}")
    print(f"  Effective rank: {rank}  (= number of independent Yukawa structures)")
    print(f"  Null space dimension: {27 - rank}  (= flat Higgs directions)")
    print()

    # Active subspace: the right singular vectors (columns of Vh.T)
    # with non-zero singular value
    V_active = Vh[:rank, :].conj().T  # 27×rank (active Higgs directions)
    print(f"  Active subspace: {rank}-dimensional subspace of C^27")
    print(f"  Any v_H outside this subspace gives Y=0 exactly.")
    print()

    # The Frobenius norm of Y(v_H) depends only on the projection of v_H
    # onto the active subspace.  Max Frobenius norm = s[0] (dominant SV of T).
    print(f"  Max ||Y||_F over unit ||v_H|| = {s[0]:.4f}")
    print(f"  (achieved by v_H = right SV of T corresponding to sigma_1)")

    return T_mat, s, Vh, rank, V_active


# ---------------------------------------------------------------------------
# Step 3: Gradient-based CKM optimization
# ---------------------------------------------------------------------------

def params_to_vevs(params):
    """Split 108-real parameter vector into (v_up, v_dn) ∈ C^27 × C^27."""
    v_up = params[:27] + 1j * params[27:54]
    v_dn = params[54:81] + 1j * params[81:108]
    return v_up, v_dn


def vevs_to_params(v_up, v_dn):
    """Pack (v_up, v_dn) into 108-real parameter vector."""
    return np.concatenate([
        np.real(v_up), np.imag(v_up),
        np.real(v_dn), np.imag(v_dn)
    ])


def ckm_objective(params, T, target=V_CKM_exp):
    """CKM Frobenius error as function of 108-real parameters."""
    v_up, v_dn = params_to_vevs(params)
    # Normalize
    nu = np.linalg.norm(v_up)
    nd = np.linalg.norm(v_dn)
    if nu < 1e-15 or nd < 1e-15:
        return 1e6
    v_up = v_up / nu
    v_dn = v_dn / nd
    Y_u = yukawa_fast(T, v_up)
    Y_d = yukawa_fast(T, v_dn)
    if np.allclose(Y_u, 0, atol=1e-14) or np.allclose(Y_d, 0, atol=1e-14):
        return 1e6
    try:
        V, _ = compute_ckm_and_jarlskog(Y_u, Y_d)
        return float(np.linalg.norm(np.abs(V) - target, "fro"))
    except Exception:
        return 1e6


def pmns_objective(params, T, target=V_PMNS_exp):
    """PMNS Frobenius error as function of 108-real parameters."""
    v_nu, v_e = params_to_vevs(params)
    nn = np.linalg.norm(v_nu)
    ne = np.linalg.norm(v_e)
    if nn < 1e-15 or ne < 1e-15:
        return 1e6
    v_nu = v_nu / nn
    v_e  = v_e  / ne
    Y_nu = yukawa_fast(T, v_nu)
    Y_e  = yukawa_fast(T, v_e)
    if np.allclose(Y_nu, 0, atol=1e-14) or np.allclose(Y_e, 0, atol=1e-14):
        return 1e6
    try:
        V, _ = compute_ckm_and_jarlskog(Y_nu, Y_e)
        return float(np.linalg.norm(np.abs(V) - target, "fro"))
    except Exception:
        return 1e6


def run_optimization(T, objective, init_params, label="CKM", n_restarts=5,
                     maxiter=2000):
    """Run L-BFGS-B optimization from init_params plus random restarts."""
    print(f"\n  Optimizing {label} error (L-BFGS-B, {n_restarts} restarts) ...")
    best_val = float("inf")
    best_params = init_params.copy()

    starts = [init_params.copy()]
    rng = np.random.default_rng(42)
    for _ in range(n_restarts - 1):
        # Random start: small perturbation of init + random direction
        noise = rng.normal(0, 0.3, size=len(init_params))
        starts.append(init_params + noise)

    for i, p0 in enumerate(starts):
        t0 = time.time()
        res = minimize(
            objective, p0, args=(T,),
            method="L-BFGS-B",
            options={"maxiter": maxiter, "ftol": 1e-14, "gtol": 1e-8},
        )
        elapsed = time.time() - t0
        val = float(res.fun)
        status = "IMPROVED" if val < best_val else "worse"
        print(f"    Restart {i+1}/{n_restarts}: {label} err = {val:.6f} "
              f"({elapsed:.1f}s) [{status}]")
        if val < best_val:
            best_val = val
            best_params = res.x.copy()

    return best_val, best_params


def extract_results(T, best_params_ckm, best_params_pmns):
    """Extract physical CKM/PMNS predictions from optimized parameters."""
    print("\n" + "="*70)
    print("OPTIMIZED PREDICTIONS")
    print("="*70)

    results = {}

    for label, params, target, exp_label in [
        ("CKM", best_params_ckm, V_CKM_exp, "V_CKM"),
        ("PMNS", best_params_pmns, V_PMNS_exp, "V_PMNS"),
    ]:
        v1, v2 = params_to_vevs(params)
        v1 /= np.linalg.norm(v1)
        v2 /= np.linalg.norm(v2)
        Y1 = yukawa_fast(T, v1)
        Y2 = yukawa_fast(T, v2)
        try:
            V, J = compute_ckm_and_jarlskog(Y1, Y2)
            absV = np.abs(V)
            err = float(np.linalg.norm(absV - target, "fro"))
        except Exception:
            print(f"  {label}: SVD failed")
            continue

        print(f"\n  {label} optimized error: {err:.6f}")
        print(f"  {exp_label} |matrix|:")
        for row in absV:
            print("    " + "  ".join(f"{x:.4f}" for x in row))

        if label == "CKM":
            print(f"\n  |V_ud| = {absV[0,0]:.4f}  (exp: 0.9737)")
            print(f"  |V_us| = {absV[0,1]:.4f}  (exp: 0.2243)  Cabibbo")
            print(f"  |V_ub| = {absV[0,2]:.4f}  (exp: 0.0038)  ** TARGET")
            print(f"  Jarlskog J = {J:.4e}")
        elif label == "PMNS":
            print(f"\n  |V_e1| = {absV[0,0]:.4f}  (exp: 0.821)")
            print(f"  |V_e2| = {absV[0,1]:.4f}  (exp: 0.550)")
            print(f"  |V_e3| = {absV[0,2]:.4f}  (exp: 0.149)  ** reactor angle")
            print(f"  Jarlskog J_lepton = {J:.4e}")

        results[label.lower()] = {
            "error": err,
            "V": absV.tolist(),
            "Jarlskog": float(J),
            "v1_re": np.real(v1).tolist(),
            "v1_im": np.imag(v1).tolist(),
            "v2_re": np.real(v2).tolist(),
            "v2_im": np.imag(v2).tolist(),
        }

    return results


# ---------------------------------------------------------------------------
# Step 4: Active-subspace optimization (7-dimensional)
# ---------------------------------------------------------------------------

def active_subspace_optimize(T, rank, Vh, objective, label="CKM",
                              n_restarts=10, maxiter=3000):
    """Optimize within the rank-dimensional active subspace.

    v_H = V_active @ alpha where alpha ∈ C^rank (= 2*rank real DOFs).
    This is much faster than the full 108-parameter search.
    """
    V_active = Vh[:rank, :].conj().T  # 27×rank

    def pack(alpha1, alpha2):
        return np.concatenate([np.real(alpha1), np.imag(alpha1),
                                np.real(alpha2), np.imag(alpha2)])

    def unpack(x):
        alpha1 = x[:rank] + 1j * x[rank:2*rank]
        alpha2 = x[2*rank:3*rank] + 1j * x[3*rank:]
        return alpha1, alpha2

    def obj_active(x):
        a1, a2 = unpack(x)
        v1 = V_active @ a1
        v2 = V_active @ a2
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 < 1e-15 or n2 < 1e-15:
            return 1e6
        params = vevs_to_params(v1 / n1, v2 / n2)
        return objective(params, T)

    print(f"\n  Active-subspace optimization: {label}, rank={rank}, "
          f"params={4*rank}, {n_restarts} restarts ...")
    best_val = float("inf")
    best_x = None
    rng = np.random.default_rng(7)

    for i in range(n_restarts):
        x0 = rng.normal(0, 1, size=4 * rank)
        res = minimize(obj_active, x0, method="L-BFGS-B",
                       options={"maxiter": maxiter, "ftol": 1e-15, "gtol": 1e-9})
        val = float(res.fun)
        if val < best_val:
            best_val = val
            best_x = res.x.copy()
        print(f"    Restart {i+1}: err={val:.6f}")

    # Reconstruct best v_up, v_dn
    a1, a2 = unpack(best_x)
    v1 = V_active @ a1
    v2 = V_active @ a2
    v1 /= np.linalg.norm(v1)
    v2 /= np.linalg.norm(v2)
    best_params = vevs_to_params(v1, v2)
    return best_val, best_params


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Building W33 Z3 complex generation profiles ...")
    H27, local_tris, _, P = build_z3_complex_profiles()
    psi_dom = build_dominant_profiles(P)
    print(f"H27 vertices: {len(H27)}, triangles: {len(local_tris)}")

    # ---- Build Yukawa tensor ----
    print("\nBuilding Yukawa tensor T[a,b,k] ...")
    t0 = time.time()
    T = build_yukawa_tensor(psi_dom, local_tris)
    print(f"  T built in {time.time()-t0:.2f}s,  shape: {T.shape}")

    # ---- Verify tensor against direct computation ----
    v_test = np.zeros(27, dtype=complex)
    v_test[25] = 1.0; v_test[17] = np.exp(1j * np.pi)
    Y_direct = np.einsum("abk,k->ab", T, v_test)
    from w33_complex_yukawa import yukawa3x3
    Y_old = yukawa3x3(psi_dom, local_tris, v_test)
    diff = np.linalg.norm(Y_direct - Y_old)
    print(f"  Tensor vs direct Yukawa check: ||diff|| = {diff:.2e}  ({'OK' if diff < 1e-12 else 'FAIL'})")

    # ---- Analyse tensor ----
    T_mat, s, Vh, rank, V_active = analyse_yukawa_tensor(T)

    # ---- Grid-scan baseline (from prior result) ----
    print("\n" + "="*70)
    print("BASELINE (prior grid scan)")
    print("="*70)
    v_up0 = np.zeros(27, dtype=complex); v_up0[25] = 1.0; v_up0[17] = np.exp(1j*np.pi)
    v_dn0 = np.zeros(27, dtype=complex); v_dn0[25] = 1.0; v_dn0[17] = -np.exp(1j*np.pi)
    Y_u0 = yukawa_fast(T, v_up0 / np.linalg.norm(v_up0))
    Y_d0 = yukawa_fast(T, v_dn0 / np.linalg.norm(v_dn0))
    V0, J0 = compute_ckm_and_jarlskog(Y_u0, Y_d0)
    base_err = float(np.linalg.norm(np.abs(V0) - V_CKM_exp, "fro"))
    print(f"  Baseline CKM error: {base_err:.6f}")
    print(f"  |V_ub| baseline: {np.abs(V0[0,2]):.4f}  (exp: 0.0038)")

    v_lep_nu0 = np.zeros(27, dtype=complex); v_lep_nu0[3] = 1.0; v_lep_nu0[6] = np.exp(1j*2.793)
    v_lep_e0  = np.zeros(27, dtype=complex); v_lep_e0[3]  = 1.0; v_lep_e0[6]  = -np.exp(1j*2.793)
    Y_nu0 = yukawa_fast(T, v_lep_nu0 / np.linalg.norm(v_lep_nu0))
    Y_e0  = yukawa_fast(T, v_lep_e0  / np.linalg.norm(v_lep_e0))
    V_lep0, J_lep0 = compute_ckm_and_jarlskog(Y_nu0, Y_e0)
    base_pmns_err = float(np.linalg.norm(np.abs(V_lep0) - V_PMNS_exp, "fro"))
    print(f"  Baseline PMNS error: {base_pmns_err:.6f}")

    # ---- Full gradient optimization (CKM) ----
    print("\n" + "="*70)
    print("FULL GRADIENT OPTIMIZATION")
    print("="*70)
    init_ckm  = vevs_to_params(v_up0 / np.linalg.norm(v_up0),
                                v_dn0 / np.linalg.norm(v_dn0))
    init_pmns = vevs_to_params(v_lep_nu0 / np.linalg.norm(v_lep_nu0),
                                v_lep_e0  / np.linalg.norm(v_lep_e0))

    best_ckm_full, params_ckm_full = run_optimization(
        T, ckm_objective, init_ckm, label="CKM", n_restarts=5, maxiter=2000)
    best_pmns_full, params_pmns_full = run_optimization(
        T, pmns_objective, init_pmns, label="PMNS", n_restarts=5, maxiter=2000)

    # ---- Active-subspace optimization ----
    print("\n" + "="*70)
    print("ACTIVE-SUBSPACE OPTIMIZATION (7-dimensional)")
    print("="*70)
    best_ckm_as, params_ckm_as = active_subspace_optimize(
        T, rank, Vh, ckm_objective, label="CKM", n_restarts=20, maxiter=5000)
    best_pmns_as, params_pmns_as = active_subspace_optimize(
        T, rank, Vh, pmns_objective, label="PMNS", n_restarts=20, maxiter=5000)

    # Use best of full and active-subspace
    params_ckm_best  = params_ckm_as  if best_ckm_as  < best_ckm_full  else params_ckm_full
    params_pmns_best = params_pmns_as if best_pmns_as < best_pmns_full else params_pmns_full
    best_ckm  = min(best_ckm_full,  best_ckm_as)
    best_pmns = min(best_pmns_full, best_pmns_as)

    # ---- Extract results ----
    results = extract_results(T, params_ckm_best, params_pmns_best)

    # ---- Summary ----
    print("\n" + "="*70)
    print("PILLAR 65 SUMMARY: YUKAWA TENSOR OPTIMIZATION")
    print("="*70)
    print(f"  Prior grid CKM error:      {base_err:.6f}")
    print(f"  Prior grid PMNS error:     {base_pmns_err:.6f}")
    print(f"  Gradient CKM  error:       {best_ckm:.6f}  "
          f"({'IMPROVED' if best_ckm < base_err else 'same'})")
    print(f"  Gradient PMNS error:       {best_pmns:.6f}  "
          f"({'IMPROVED' if best_pmns < base_pmns_err else 'same'})")
    print()
    print(f"  Yukawa tensor rank:        {rank} / 27")
    print(f"  Active subspace dim:       {rank}")
    print(f"  Null space dim:            {27 - rank}")
    print()

    # Save
    output = {
        "pillar": 65,
        "title": "Yukawa Tensor Gradient Optimization",
        "tensor_rank": int(rank),
        "active_subspace_dim": int(rank),
        "null_space_dim": int(27 - rank),
        "tensor_singular_values": s.tolist(),
        "grid_scan_ckm_error": float(base_err),
        "grid_scan_pmns_error": float(base_pmns_err),
        "gradient_ckm_error": float(best_ckm),
        "gradient_pmns_error": float(best_pmns),
        "improved_ckm": best_ckm < base_err,
        "improved_pmns": best_pmns < base_pmns_err,
        "ckm": results.get("ckm", {}),
        "pmns": results.get("pmns", {}),
    }
    os.makedirs("data", exist_ok=True)
    with open("data/w33_yukawa_optimization.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Saved data/w33_yukawa_optimization.json")


if __name__ == "__main__":
    main()
