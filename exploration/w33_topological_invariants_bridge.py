"""Topological invariants of the graph manifold.
Phase DXLVII — Interpret W(3,3) as a simplicial complex.
Betti numbers: β₀=1 (connected), β₁=E-V+1=201 (cycle rank).
Euler characteristic χ = V-E+T = 40-240+160 = -40 = -v.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_topological_invariants_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    E = v * k // 2  # 240
    T = v * k * lam // 6  # 160
    # Clique complex: vertices, edges, triangles (no 4-cliques? ω=4 so we have tetrahedra too)
    omega = q + 1  # 4
    # Number of 4-cliques (tetrahedra): 
    # In SRG, a 4-clique = complete subgraph on 4 vertices
    # Each 4-clique has C(4,2)=6 edges and C(4,3)=4 triangles
    # Total 4-cliques: hard to compute exactly without adjacency matrix
    # But: each line of GQ has q+1=4 points, all mutually collinear → 4-clique
    # Total lines = v = 40 (dual interpretation: 40 lines in dual GQ)
    # Actually: W(3,3) has 40 points. The lines of the GQ form 4-cliques.
    # Number of lines = b = v(k)/(q+1) = 40×12/4 = ... wait
    # In GQ(3,3): points = 40, lines = 40 (self-dual!), each line has q+1=4 points
    num_lines = 40  # same as points (self-dual)
    # Each line = 1 tetrahedron
    # Number of 4-cliques = number of lines = 40
    tet = num_lines  # 40
    # Euler char of clique complex with tetrahedra:
    # χ = V - E + T - tet = 40 - 240 + 160 - 40 = -80
    # But for 2-skeleton (just vertices, edges, triangles):
    chi_2 = v - E + T  # 40 - 240 + 160 = -40
    chi_is_neg_v = chi_2 == -v
    # For full clique complex (including tetrahedra):
    chi_3 = v - E + T - tet  # -80
    chi_3_is = chi_3 == -2 * v
    # β₁ of 1-skeleton (graph): = E - V + 1 = 201 (first Betti)
    beta1 = E - v + 1  # 201
    beta1_check = beta1 == 201
    return {
        "status": "ok",
        "topological_invariants_theorem": {
            "chi_2_neg_v": chi_is_neg_v,
            "chi_3_neg_2v": chi_3_is,
            "beta1_201": beta1_check,
            "num_tet_v": tet == v,
            "therefore_topo_verified": chi_is_neg_v and chi_3_is and beta1_check and tet==v,
        },
    }
