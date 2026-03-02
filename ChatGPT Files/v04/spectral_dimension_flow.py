#!/usr/bin/env python3
"""
spectral_dimension_flow.py

Computes the diffusion-based *spectral dimension* on the W33 "spacetime" using
the 0-form Laplacian L0 = B1 B1^T (vertex Laplacian of the collinearity graph).

We report d_s(t) = -2 d(log p(t)) / d(log t), where p(t) = (1/n) Tr exp(-t L0).

On a finite complex, UV (t->0) and IR (t->∞) limits degenerate; the useful signal
is the *intermediate-scale plateau*.

Outputs:
- spectral_dimension_report.json (t-grid, p(t), d_s(t), plateau estimate)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

HERE = Path(__file__).resolve().parent


def build_L0() -> np.ndarray:
    core = json.loads((HERE / "w33_core.json").read_text())
    nv = len(core["points"])
    edges = [tuple(e) for e in core["edges"]]
    triangles = [tuple(t) for t in core["triangles"]]  # unused but present

    ne = len(edges)
    B1 = np.zeros((nv, ne), dtype=int)
    for e_idx, (u, v) in enumerate(edges):
        B1[u, e_idx] = -1
        B1[v, e_idx] = 1
    return B1 @ B1.T


def spectral_dimension(eigs: np.ndarray, ts: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    n = len(eigs)
    p = np.array([np.mean(np.exp(-t * eigs)) for t in ts])
    d = -2.0 * np.gradient(np.log(p), np.log(ts))
    return p, d


def plateau(ts: np.ndarray, p: np.ndarray, d: np.ndarray, low: float = 1e-3, high: float = 0.8) -> Dict:
    # pick maximum d in a stable band to avoid finite-size IR/UV artifacts
    m = (p > low) & (p < high)
    if not np.any(m):
        return {"found": False}
    idx = np.where(m)[0]
    j = idx[np.argmax(d[m])]
    return {"found": True, "t": float(ts[j]), "d": float(d[j]), "p": float(p[j])}


def main() -> None:
    L0 = build_L0()
    eigs = np.linalg.eigvalsh(L0.astype(float))

    ts = np.logspace(-3, 2, 600)
    p, d = spectral_dimension(eigs, ts)
    plat = plateau(ts, p, d)

    out = {
        "n": int(len(eigs)),
        "trace_L0": int(np.round(float(np.sum(eigs)))),
        "plateau_estimate": plat,
        "ts": ts.tolist(),
        "p": p.tolist(),
        "d_s": d.tolist(),
    }
    (HERE / "spectral_dimension_report.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote spectral_dimension_report.json")
    if plat.get("found"):
        print(f"Plateau: d_s ≈ {plat['d']:.6f} at t ≈ {plat['t']:.6f} (p≈{plat['p']:.4f})")


if __name__ == "__main__":
    main()
