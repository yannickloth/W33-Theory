#!/usr/bin/env python3
"""End-to-end mass synthesis from W33 geometry.

- computes Dirac / Hodge spectral data
- derives Yukawa weights from the 45-triad counting model (lambda = 9/40)
- computes charged-fermion mass estimates (GUT-scale proxy)
- computes neutrino seesaw estimates using the W33 Dirac coupling matrix

Produces a JSON artifact and returns a dict for programmatic use.
"""
from __future__ import annotations

import json
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

# local imports (existing utilities)
from scripts.w33_h1_decomposition import build_incidence_matrix, compute_harmonic_basis
from scripts.w33_hodge import compute_hodge_laplacians, eigen_decomp_sorted
from scripts.w33_neutrino_seesaw import (  # reuse to construct sectors if needed (lightweight import)
    build_full_group,
)

ROOT = Path(__file__).resolve().parents[1]


def derive_yukawas_from_triads(lambda_val=Fraction(9, 40)):
    """Return Yukawa weight estimates following the 36/9 triad split model.

    Returns dictionary of Yukawa (dimensionless) for SM fermions.
    """
    # Using the same empirical mapping used elsewhere in the repo
    ratio_affine = 36 / 45
    ratio_fiber = 9 / 45

    Y_t = 1.0
    Y_b = float(ratio_affine) * float(lambda_val)
    Y_c = float(ratio_fiber) * float(lambda_val) ** 2
    Y_s = float(ratio_fiber) * float(lambda_val) ** 2
    Y_u = float(lambda_val) ** 3
    Y_d = float(lambda_val) ** 3

    # charged leptons (parallel assignment used in repo)
    Y_tau = float(ratio_affine) * float(lambda_val)
    Y_mu = float(ratio_fiber) * float(lambda_val) ** 2
    Y_e = float(lambda_val) ** 3

    return {
        "Y_t": Y_t,
        "Y_b": Y_b,
        "Y_c": Y_c,
        "Y_s": Y_s,
        "Y_u": Y_u,
        "Y_d": Y_d,
        "Y_tau": Y_tau,
        "Y_mu": Y_mu,
        "Y_e": Y_e,
    }


def compute_neutrino_seesaw_masses(H, simplices, edges, M_R_GeV: float = 3**20):
    """Recompute the Dirac coupling m_D (48×3) and estimate light neutrino masses.

    Uses the same wedge-norm coupling used in `w33_neutrino_seesaw.py` and
    applies the seesaw formula m_nu ~ m_D^2 / M_R with an assumed M_R scale.
    Returns singular values of m_D (dimensionless relative couplings) and
    light neutrino masses in eV using an electroweak-scale normalization.
    """
    # Map harmonic sectors to fermion(48)/singlet(3) subspaces by reusing
    # compute_harmonic_basis and the sector extraction logic from the
    # neutrino seesaw pipeline. For simplicity, re-run the minimal coupling
    # computation: project H onto sectors by clustering as in existing script.

    # --- Reuse the approach in w33_neutrino_seesaw: find harmonic basis and
    #     then build fermion / singlet projectors. We'll call compute_harmonic_basis
    #     upstream so H is already the harmonic basis (240 x 81).

    # For brevity we will reuse the wedge-based coupling but pick an
    # approximate partitioning consistent with repository conventions.
    # Practical approach: use SVD on a sampled coupling tensor to locate
    # the 3-dim singlet directions and 48-dim fermion space.

    # Build wedge-coupling matrix between harmonic basis columns to find a
    # small 3-dim singlet subspace: compute pairwise self-wedge norms and
    # take principal components.
    n_harm = H.shape[1]

    # quick singular-value-based probe for singlet directions
    # build a small 81x81 symmetric matrix from triple-wedge statistics
    W = np.zeros((n_harm, n_harm))
    triangles = simplices[2]
    edge_idx = {(u, v): (i, +1) for i, (u, v) in enumerate(edges)}
    edge_idx.update({(v, u): (i, -1) for i, (u, v) in enumerate(edges)})

    # pairwise coupling via triangle contractions (cheap proxy)
    for i in range(n_harm):
        hi = H[:, i]
        for j in range(i, n_harm):
            hj = H[:, j]
            s = 0.0
            for v0, v1, v2 in triangles:
                e01_i, e01_s = edge_idx[(v0, v1)]
                e02_i, e02_s = edge_idx[(v0, v2)]
                e12_i, e12_s = edge_idx[(v1, v2)]
                hi01 = e01_s * hi[e01_i]
                hi02 = e02_s * hi[e02_i]
                hi12 = e12_s * hi[e12_i]
                hj01 = e01_s * hj[e01_i]
                hj02 = e02_s * hj[e02_i]
                hj12 = e12_s * hj[e12_i]
                # antisymmetric wedge-like contraction (proxy)
                w = (
                    hi01 * hj12
                    - hj01 * hi12
                    - hi01 * hj02
                    + hj01 * hi02
                    + hi02 * hj12
                    - hj02 * hi12
                )
                s += w * w
            W[i, j] = s
            W[j, i] = s

    # SVD on W to find dominant 3 singlet directions
    u, svals, vt = np.linalg.svd(W)
    singlet_vecs = u[:, :3]  # mixing in H-basis (81×3)

    # Fermion subspace: take next 48 principal components (approx)
    fermion_vecs = u[:, 3 : 3 + 48]

    # Project harmonic basis H (240×81) into edge representation for coupling
    H_singlet = H @ singlet_vecs  # 240 × 3
    H_fermion = H @ fermion_vecs  # 240 × 48

    # Compute wedge-based Dirac coupling m_D (48 × 3)
    m_D = np.zeros((48, 3))
    for fi in range(48):
        for sj in range(3):
            h1 = H_fermion[:, fi]
            h2 = H_singlet[:, sj]
            wedge_sq = 0.0
            for v0, v1, v2 in triangles:
                e01_i, e01_s = edge_idx[(v0, v1)]
                e02_i, e02_s = edge_idx[(v0, v2)]
                e12_i, e12_s = edge_idx[(v1, v2)]
                h1_01 = e01_s * h1[e01_i]
                h1_02 = e02_s * h1[e02_i]
                h1_12 = e12_s * h1[e12_i]
                h2_01 = e01_s * h2[e01_i]
                h2_02 = e02_s * h2[e02_i]
                h2_12 = e12_s * h2[e12_i]
                w = (
                    h1_01 * h2_12
                    - h2_01 * h1_12
                    - h1_01 * h2_02
                    + h2_01 * h1_02
                    + h1_02 * h2_12
                    - h2_02 * h1_12
                )
                wedge_sq += w * w
            m_D[fi, sj] = np.sqrt(wedge_sq)

    # singular values (dimensionless relative couplings)
    sigma = np.linalg.svd(m_D, compute_uv=False)

    # Map dimensionless couplings to GeV scale for seesaw estimate.
    # Use electroweak v = 246 GeV as representative scale for Dirac-type
    # masses: m_D_GeV ≈ sigma * v (order-of-magnitude mapping).
    v_EW = 246.22
    m_D_GeV = sigma * v_EW

    # Light neutrino masses (approx) via type-I seesaw: m_ν ≈ m_D^2 / M_R
    m_nu_GeV = (m_D_GeV**2) / M_R_GeV
    # convert to eV
    m_nu_eV = m_nu_GeV * 1e9

    return {
        "m_D_singular_values": [float(x) for x in sigma.tolist()],
        "m_D_GeV": [float(x) for x in m_D_GeV.tolist()],
        "m_nu_eV": [float(x) for x in m_nu_eV.tolist()],
        "sum_m_nu_eV": float(m_nu_eV.sum()),
    }


def compute_mass_predictions():
    t0 = time.time()

    # Build harmonic basis and simplices
    # (compute_harmonic_basis returns H (240×81), eigenvalues)
    from w33_homology import build_clique_complex, build_w33

    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    H, eigs = compute_harmonic_basis(n, adj, edges, simplices)

    # Dirac / Hodge spectra (samples)
    Ls = compute_hodge_laplacians()
    w0, _ = eigen_decomp_sorted(Ls["L0"])
    w1, _ = eigen_decomp_sorted(Ls["L1"])

    # Yukawa predictions (triad model)
    yukawas = derive_yukawas_from_triads()

    # Charged-fermion mass estimates (GUT-scale proxy)
    # follow normalization used in derive_yukawa_from_45_triads.py
    m_t_exp_GeV = 100.0  # proxy top at GUT-scale (order-of-magnitude)
    masses = {
        "top_GeV": m_t_exp_GeV * (yukawas["Y_t"] ** 2),
        "bottom_GeV": m_t_exp_GeV * (yukawas["Y_b"] ** 2),
        "charm_GeV": m_t_exp_GeV * (yukawas["Y_c"] ** 2),
        "strange_GeV": m_t_exp_GeV * (yukawas["Y_s"] ** 2),
        "up_GeV": m_t_exp_GeV * (yukawas["Y_u"] ** 2),
        "down_GeV": m_t_exp_GeV * (yukawas["Y_d"] ** 2),
        "tau_GeV": m_t_exp_GeV * (yukawas["Y_tau"] ** 2),
        "mu_GeV": m_t_exp_GeV * (yukawas["Y_mu"] ** 2),
        "electron_GeV": m_t_exp_GeV * (yukawas["Y_e"] ** 2),
    }

    # Neutrino seesaw estimates
    neutrino = compute_neutrino_seesaw_masses(H, simplices, edges)

    out = {
        "timestamp": int(time.time()),
        "hodge_sqrt_vertex_sample": [
            float(x) for x in np.sqrt(np.clip(w0, 0.0, None))[:8]
        ],
        "hodge_sqrt_edge_sample": [
            float(x) for x in np.sqrt(np.clip(w1, 0.0, None))[:12]
        ],
        "yukawas": yukawas,
        "masses_GeV": masses,
        "neutrino_seesaw": neutrino,
    }

    # write artifact
    out_path = ROOT / "artifacts" / f"w33_mass_synthesis_{int(time.time())}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("Wrote mass synthesis artifact:", out_path)
    print(
        "Summary: top Y~{:.2f}, m_t(GUT)~{:.1f} GeV, Σm_ν~{:.3e} eV".format(
            out["yukawas"]["Y_t"],
            out["masses_GeV"]["top_GeV"],
            out["neutrino_seesaw"]["sum_m_nu_eV"],
        )
    )

    return out


if __name__ == "__main__":
    compute_mass_predictions()
