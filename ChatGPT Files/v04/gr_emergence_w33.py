#!/usr/bin/env python3
"""
gr_emergence_w33.py

A concrete GR-emergence package for the W33 spacetime model.

We do three things:

(1) Compute Ollivier–Ricci curvature κ(x,y) on *all edges* using optimal transport
    (same method as the earlier bundle: linear programming via scipy.optimize.linprog).
    Verify κ is constant and equals 2/k = 1/6.

(2) Compute the discrete Gauss–Bonnet total:
      Σ_edges κ(e)  = 40
    and show how the project’s "480 Einstein–Hilbert action" arises canonically:

    - Vertex Laplacian L0 has Tr(L0) = Σ_v deg(v) = 40*12 = 480 exactly.
    - With constant κ = 1/6, scalar curvature per vertex can be defined as
          R(v) := Σ_{u~v} κ(v,u) = deg(v)*κ = 12*(1/6)=2
      hence Σ_v R(v) = 80 and Tr(L0) = (1/κ) * Σ_v R(v) = 6*80 = 480.

    This gives a clean normalization story: "EH = Tr(L0)" is equivalent to
    "EH = (1/κ) * ∑ scalar curvature".

(3) Provide a *dynamics* toy model:
    Define a weighted graph metric by edge-weights w_e and use Forman-Ricci curvature
    (closed-form) as a surrogate curvature to demonstrate an "Einstein fixed point"
    under a Ricci-flow-like update on weights.

Outputs:
- gr_emergence_report.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple, Dict

import numpy as np
from scipy.optimize import linprog
import networkx as nx

HERE = Path(__file__).resolve().parent


def load_core() -> tuple[np.ndarray, List[Tuple[int,int]]]:
    core = json.loads((HERE / "w33_core.json").read_text())
    A = np.array(core["adjacency"], dtype=int)
    edges = [tuple(e) for e in core["edges"]]
    return A, edges


def all_pairs_shortest_paths(A: np.ndarray) -> np.ndarray:
    n = A.shape[0]
    dist = np.full((n, n), fill_value=10**9, dtype=int)
    for i in range(n):
        dist[i, i] = 0
        q = [i]
        head = 0
        while head < len(q):
            u = q[head]; head += 1
            for v in np.where(A[u] == 1)[0]:
                v = int(v)
                if dist[i, v] > dist[i, u] + 1:
                    dist[i, v] = dist[i, u] + 1
                    q.append(v)
    return dist


def wasserstein_uniform(cost: np.ndarray) -> float:
    m, n = cost.shape
    a = np.full(m, 1.0 / m)
    b = np.full(n, 1.0 / n)

    c = cost.reshape(-1).astype(float)

    A_eq = []
    b_eq = []

    # row sums
    for i in range(m):
        row = np.zeros(m * n)
        row[i * n:(i + 1) * n] = 1.0
        A_eq.append(row)
        b_eq.append(a[i])

    # col sums
    for j in range(n):
        col = np.zeros(m * n)
        col[j::n] = 1.0
        A_eq.append(col)
        b_eq.append(b[j])

    A_eq = np.vstack(A_eq)
    b_eq = np.array(b_eq)

    bounds = [(0.0, None) for _ in range(m * n)]
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError("linprog failed: " + res.message)
    return float(res.fun)


def ollivier_ricci_edge(A: np.ndarray, dist: np.ndarray, x: int, y: int) -> float:
    Nx = np.where(A[x] == 1)[0].astype(int)
    Ny = np.where(A[y] == 1)[0].astype(int)
    C = dist[np.ix_(Nx, Ny)].astype(float)
    W1 = wasserstein_uniform(C)
    return 1.0 - W1  # since d(x,y)=1


# ---- Forman curvature toy (graph-only version) ----
def forman_edge_curvature(G: nx.Graph, u: int, v: int, w_v: np.ndarray, w_e: Dict[Tuple[int,int], float]) -> float:
    """
    Simple Forman curvature for a weighted graph:
      F(u,v) = w_e(u,v) * (1/w_v(u) + 1/w_v(v))
               - sum_{u~u',u'!=v} w_v(u) / sqrt(w_e(u,v) w_e(u,u'))
               - sum_{v~v',v'!=u} w_v(v) / sqrt(w_e(u,v) w_e(v,v'))
    """
    e = (min(u,v), max(u,v))
    we = w_e[e]
    term = we * (1.0 / w_v[u] + 1.0 / w_v[v])
    for u2 in G.neighbors(u):
        if u2 == v: continue
        e2 = (min(u,u2), max(u,u2))
        term -= w_v[u] / np.sqrt(we * w_e[e2])
    for v2 in G.neighbors(v):
        if v2 == u: continue
        e2 = (min(v,v2), max(v,v2))
        term -= w_v[v] / np.sqrt(we * w_e[e2])
    return float(term)


def forman_flow_demo(A: np.ndarray, steps: int = 30, eta: float = 0.02) -> Dict:
    """
    Demonstrate a Ricci-flow-like relaxation on edge weights using Forman curvature.
    We start with small random perturbations of weights and relax toward constant curvature.
    """
    n = A.shape[0]
    G = nx.from_numpy_array(A)

    # vertex weights all 1
    w_v = np.ones(n)

    # edge weights perturbed
    rng = np.random.default_rng(0)
    w_e = {}
    for u, v in G.edges():
        e = (min(u,v), max(u,v))
        w_e[e] = float(1.0 + 0.05 * rng.normal())

    history = []
    for t in range(steps):
        curvs = []
        for u, v in G.edges():
            curvs.append(forman_edge_curvature(G, u, v, w_v, w_e))
        curvs = np.array(curvs, dtype=float)
        mean = float(curvs.mean())
        var = float(curvs.var())
        history.append({"step": t, "mean": mean, "var": var})

        # update: w_e <- w_e * exp(-eta*(F-mean))  (drives curvature toward constant)
        i = 0
        for u, v in G.edges():
            e = (min(u,v), max(u,v))
            F = float(curvs[i]); i += 1
            w_e[e] *= float(np.exp(-eta * (F - mean)))
        # renormalize to avoid blowup
        avg_w = sum(w_e.values()) / len(w_e)
        for e in list(w_e.keys()):
            w_e[e] /= avg_w

    return {"history": history}


def main() -> None:
    A, edges = load_core()
    n = A.shape[0]
    k = int(A[0].sum())
    assert all(int(A[i].sum()) == k for i in range(n))

    # OT-based curvature
    dist = all_pairs_shortest_paths(A)

    kappas = []
    for (x, y) in edges:
        kappas.append(ollivier_ricci_edge(A, dist, x, y))
    kappas = np.array(kappas, dtype=float)

    kappa_mean = float(kappas.mean())
    kappa_min = float(kappas.min())
    kappa_max = float(kappas.max())

    # Gauss–Bonnet sum over edges (as in the page's claim)
    gb_sum = float(kappas.sum())

    # EH normalization via Tr(L0)
    # L0 trace = sum degrees = n*k
    trace_L0 = int(n * k)

    # scalar curvature per vertex R(v) = sum_{u~v} kappa(v,u)
    # since constant kappa, R(v)=k*kappa
    R_v = float(k * kappa_mean)
    total_scalar = float(n * R_v)

    report = {
        "n": n,
        "k": k,
        "kappa": {"mean": kappa_mean, "min": kappa_min, "max": kappa_max, "expected_2_over_k": 2.0/k},
        "gauss_bonnet_edge_sum": gb_sum,
        "trace_L0": trace_L0,
        "scalar_curvature_per_vertex": R_v,
        "total_scalar_curvature": total_scalar,
        "identity_traceL0_equals_totalScalar_over_kappa": float(total_scalar / kappa_mean) if kappa_mean != 0 else None,
        "forman_flow_demo": forman_flow_demo(A),
    }

    (HERE / "gr_emergence_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Wrote gr_emergence_report.json")
    print(f"κ mean={kappa_mean:.12f} (expected {2.0/k:.12f}), Σ_e κ(e)={gb_sum:.6f}, Tr(L0)={trace_L0}")


if __name__ == "__main__":
    main()
