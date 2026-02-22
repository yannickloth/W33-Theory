#!/usr/bin/env python3
"""
Higgs VEV selection & PMNS (leptonic mixing) diagnostics — Pillar 47

Demonstrates PMNS mixing from mismatched Z3 generation decompositions
(similar pipeline to CKM-from-VEV, applied to charged‑lepton vs neutrino
Yukawa constructions).  This is *not* a physical seesaw calculation; it
shows that the same group-theoretic / VEV‑alignment mechanism that
produces CKM mixing also produces a PMNS matrix when the neutrino and
charged‑lepton VEV directions differ.

Usage:
    python scripts/w33_higgs_pmns.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from w33_ckm_from_vev import (
    _build_hodge_and_generations,
    build_generation_profiles,
    build_h27_index_and_tris,
    compute_ckm_and_jarlskog,
    yukawa_from_vev_with_tris,
)


def compute_pmns_from_vevs(X_profiles, local_tris, v_e, v_n):
    """Return (V_PMNS, J_pmns, s12, s13, s23) computed from Yukawas.

    V_PMNS = U_e^dagger U_n where U_e/U_n diagonalize Y_e/Y_n respectively.
    """
    Y_e = yukawa_from_vev_with_tris(X_profiles, v_e, local_tris)
    Y_n = yukawa_from_vev_with_tris(X_profiles, v_n, local_tris)
    V, J = compute_ckm_and_jarlskog(Y_e, Y_n)  # same routine used for CKM

    s12 = abs(V[0, 1])
    s23 = abs(V[1, 2])
    s13 = abs(V[0, 2])
    return V, float(J), float(s12), float(s13), float(s23)


def main():
    t0 = time.time()
    H, triangles, edges, gens = _build_hodge_and_generations()
    n = max(max(u, v) for u, v in edges) + 1
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    H27, local_tris = build_h27_index_and_tris(adj, v0=0)
    _, _, X_profiles = build_generation_profiles(H, edges, gens, v0=0)

    # charged-lepton VEV (real) and neutrino VEV (misaligned complex)
    v_e = X_profiles[0].astype(complex)
    v_n = v_e.copy()
    # pick index 3 (couples in cubic contraction) and add complex phase
    v_n[3] *= np.exp(1j * 0.9)

    V, J, s12, s13, s23 = compute_pmns_from_vevs(X_profiles, local_tris, v_e, v_n)

    print("PMNS |V|:\n", np.round(np.abs(V), 6))
    print(f"Jarlskog (PMNS) = {J:.6e}")
    print(f"s12={s12:.6f}, s13={s13:.6f}, s23={s23:.6f}")

    out = {
        "V_abs": np.abs(V).tolist(),
        "J": J,
        "s12": s12,
        "s13": s13,
        "s23": s23,
        "elapsed_seconds": time.time() - t0,
    }
    out_dir = Path(__file__).resolve().parent.parent / "checks"
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"PART_CXVII_higgs_pmns_{int(time.time())}.json"
    with open(fname, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Wrote: {fname}")
    return out


if __name__ == "__main__":
    main()
