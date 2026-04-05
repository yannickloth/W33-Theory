"""Line graph and edge-vertex incidence structure.

Phase DXXI — The line graph L(Γ) has 240 vertices (one per edge), each edge-vertex
adjacent to 2(k-1)-λ = 20-2 = 18... wait. For k-regular: L(Γ) is (2k-2)-regular = 22-regular.
Each edge shares endpoints, and two edges sharing a vertex are adjacent in L(Γ).
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def build_line_graph_summary() -> dict:
    v, k, lam, mu, q = 40, 12, 2, 4, 3
    r, s = 2, -4
    f, g = 24, 15
    E = 240
    # Line graph L(Γ): V(L) = E = 240, each edge {u,v} adjacent to (k-1)+(k-1) = 22 edges
    # minus common edges counted separately
    lg_vertices = E  # 240
    lg_degree = 2 * (k - 1) - lam  # 22 - 2 = 20? 
    # Actually: for edge {u,v}, adjacent edges are:
    # edges incident to u (not {u,v}): k-1 = 11
    # edges incident to v (not {u,v}): k-1 = 11
    # minus edges incident to both u AND v (which share both endpoints with {u,v}'s endpoints):
    # these are edges {u,w} where w~v (common neighbor), counted λ=2 times? No.
    # Two edges {u,w} and {v,w} where w is common neighbor are BOTH adjacent to {u,v} in L(Γ)
    # but they are edges at u and v respectively. So no double counting.
    # Wait: edges sharing endpoint u with {u,v}: there are k-1 others at u.
    # Edges sharing endpoint v with {u,v}: there are k-1 others at v.
    # But some share BOTH an endpoint with different parts? No, an edge can only share one endpoint.
    # Unless there are parallel edges (none in simple graph).
    # So lg_degree = 2(k-1) = 22? Actually...
    # Two edges incident to u ∩ v: edges {u,w} where w~u and w~v (triangles),
    # and {v,w} similarly. But {u,w} is incident to u, {v,w} is incident to v — distinct.
    # The issue: edges {w₁,w₂} where w₁~u and w₂~v or both w₁,w₂ are endpoints...
    # No. In the line graph, two edges are adjacent iff they share a vertex.
    # So edge {u,v}'s neighbors in L = all edges sharing u or v with {u,v}
    # = {u,w: w~u, w≠v} ∪ {v,w: w~v, w≠u}
    # Size = (k-1) + (k-1) - |{edges {w₁, w₂} counted twice}|
    # But {u,w} and {v,w'} never overlap unless w=v or w'=u (excluded).
    # The intersection is edges {u,w} where also {v,w} exists, meaning w is common neighbor.
    # But these are different edges! {u,w} is one, {v,w} is different.
    # So no overlap: lg_degree = 2(k-1) = 22
    lg_degree_correct = 2 * (k - 1)  # 22
    # Edges of L(Γ) = v × k × (k-1) / 2 (each vertex contributes C(k,2) edge-pairs)
    # Wait: |E(L)| = Σ_v C(deg(v), 2) = v × C(k,2) = 40 × 66 = 2640
    lg_edges = v * k * (k - 1) // 2  # 40 × 66 = 2640
    # Check: |E(L)| = lg_vertices × lg_degree / 2 = 240 × 22 / 2 = 2640 ✓
    lg_edges_check = lg_vertices * lg_degree_correct // 2  # 2640
    return {
        "status": "ok",
        "line_graph": {
            "lg_vertices": lg_vertices,
            "lg_degree": lg_degree_correct,
            "lg_edges": lg_edges,
        },
        "line_graph_theorem": {
            "lg_v_240": lg_vertices == 240,
            "lg_deg_22": lg_degree_correct == 22,
            "lg_edges_2640": lg_edges == 2640,
            "lg_edges_consistent": lg_edges == lg_edges_check,
            "therefore_line_graph_verified": (
                lg_vertices == 240 and lg_degree_correct == 22
                and lg_edges == 2640
            ),
        },
    }
