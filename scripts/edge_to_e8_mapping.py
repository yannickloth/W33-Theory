"""Find a global linear transform mapping W33 edge lifts to E8 roots and compute a one-to-one mapping.

Algorithm:
 1. Use anchor matches from HYBRID_BIJECTION_CONSTRUCTION strategies (diff_pad, diff_double, concat)
 2. Compute Procrustes/Kabsch rotation + uniform scale aligning anchor lifts to E8 roots
 3. Apply transform to lifts for all edges (try multiple lift strategies/variants) and compute nearest E8 root
 4. Solve greedy minimal-distance bipartite matching (edge -> root) and report coverage
 5. Save mapping and diagnostics to artifacts/edge_root_mapping.json

This is heuristic but deterministic given the anchor set.
"""

import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

# Ensure repo root is in sys.path so top-level modules are importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import construction helpers from existing module
from HYBRID_BIJECTION_CONSTRUCTION import (
    build_E8_roots,
    build_W33,
    is_E8_root,
    lift_concat,
    lift_diff_double,
    lift_diff_pad,
    lift_diff_pad_right,
    lift_half_int,
    lift_sum_double,
    lift_sum_pad,
)

ARTIFACTS = Path("artifacts")
ARTIFACTS.mkdir(parents=True, exist_ok=True)


def anchors_from_strategies():
    """Return list of anchor pairs (edge_idx, lift_vec (8,), root (8,))"""
    vertices, edges = build_W33()
    e8_roots = build_E8_roots()
    E8_set = set(e8_roots)

    anchors = []
    # expanded set of strategies (including half-int and variant families) to increase anchor coverage
    strategies = [
        lift_diff_pad,
        lift_diff_double,
        lift_concat,
        lift_diff_pad_right,
        lift_sum_pad,
        lift_sum_double,
        lift_half_int,
    ]
    # also try scaled/variant families
    from HYBRID_BIJECTION_CONSTRUCTION import (
        lift_concat_variants,
        lift_diff_scaled_variants,
        lift_half_int_variants,
    )

    for lift_fn in strategies:
        for i in range(len(edges)):
            vec = lift_fn(i)
            is_root, root = is_E8_root(vec)
            if is_root:
                anchors.append(
                    (i, np.array(vec, dtype=float), np.array(root, dtype=float))
                )

    # try family variants (may return multiple vectors per edge)
    for i in range(len(edges)):
        try:
            for vec in lift_diff_scaled_variants(i):
                is_root, root = is_E8_root(vec)
                if is_root:
                    anchors.append(
                        (i, np.array(vec, dtype=float), np.array(root, dtype=float))
                    )
        except Exception:
            pass
        try:
            for vec in lift_concat_variants(i):
                is_root, root = is_E8_root(vec)
                if is_root:
                    anchors.append(
                        (i, np.array(vec, dtype=float), np.array(root, dtype=float))
                    )
        except Exception:
            pass
        try:
            for vec in lift_half_int_variants(i):
                is_root, root = is_E8_root(vec)
                if is_root:
                    anchors.append(
                        (i, np.array(vec, dtype=float), np.array(root, dtype=float))
                    )
        except Exception:
            pass

    # unique anchors by edge (prefer half-integer matches if available)
    anchors_by_edge = {}
    for eidx, vec, root in anchors:
        if eidx not in anchors_by_edge or (
            not all(c == int(c) for c in anchors_by_edge[eidx][1])
            and all(c != int(c) for c in root)
        ):
            # prefer half-int root match for the same edge
            anchors_by_edge[eidx] = (vec, root)
    return [(e, v, r) for e, (v, r) in anchors_by_edge.items()]


def compute_procrustes(A, B, allow_scale=True):
    """Compute linear transform (s,R,t) minimizing ||s*A*R + t - B||_F.

    Returns scale s (float), rotation R (8x8 ndarray), translation t (1x8 ndarray)
    """
    assert A.shape == B.shape
    n, d = A.shape
    # centroids
    muA = A.mean(axis=0)
    muB = B.mean(axis=0)
    A0 = A - muA
    B0 = B - muB

    # covariance matrix
    H = A0.T.dot(B0)
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T.dot(U.T)
    # Handle reflection
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T.dot(U.T)
    if allow_scale:
        scale = np.trace(np.diag(S)) / np.sum(A0**2)
    else:
        scale = 1.0

    t = muB - scale * (muA.dot(R))
    return scale, R, t


def all_lift_variants(edge_idx):
    """Return a list of candidate lift vectors for the given edge index."""
    from HYBRID_BIJECTION_CONSTRUCTION import (
        lift_concat,
        lift_concat_variants,
        lift_diff_double,
        lift_diff_pad,
        lift_diff_pad_right,
        lift_diff_scaled_variants,
        lift_half_int,
        lift_half_int_variants,
        lift_sum_double,
        lift_sum_pad,
    )

    vecs = []
    for fn in [
        lift_diff_pad,
        lift_diff_double,
        lift_concat,
        lift_diff_pad_right,
        lift_sum_pad,
        lift_sum_double,
        lift_half_int,
    ]:
        try:
            v = fn(edge_idx)
            vecs.append(np.array(v, dtype=float))
        except Exception:
            pass

    # add variants
    try:
        for vv in lift_diff_scaled_variants(edge_idx):
            vecs.append(np.array(vv, dtype=float))
    except Exception:
        pass
    try:
        for vv in lift_concat_variants(edge_idx):
            vecs.append(np.array(vv, dtype=float))
    except Exception:
        pass
    try:
        for vv in lift_half_int_variants(edge_idx):
            vecs.append(np.array(vv, dtype=float))
    except Exception:
        pass

    # Deduplicate
    uniq = []
    seen = set()
    for v in vecs:
        key = tuple(np.round(v, 8))
        if key not in seen:
            seen.add(key)
            uniq.append(v)
    return uniq


def nearest_root(vec, roots):
    """Return (root, dist) nearest to vec from roots (ndarray list)."""
    arr = np.vstack(roots)
    dists = np.linalg.norm(arr - vec.reshape(1, -1), axis=1)
    idx = int(np.argmin(dists))
    return tuple(arr[idx]), float(dists[idx])


def greedy_bipartite_match(candidate_triples, n_edges, n_roots):
    """Greedy assignment from sorted candidate triples (edge, root, dist).
    candidate_triples should be sorted by dist ascending.
    Returns dict edge->root and stats.
    """
    assigned_edges = set()
    assigned_roots = set()
    mapping = {}
    for eidx, rtuple, dist in candidate_triples:
        if eidx in assigned_edges or rtuple in assigned_roots:
            continue
        mapping[eidx] = rtuple
        assigned_edges.add(eidx)
        assigned_roots.add(rtuple)
        if len(assigned_edges) == n_edges or len(assigned_roots) == n_roots:
            break
    return mapping


def compute_line_graph_embedding(k=16):
    """Compute spectral embedding of the line graph of W33 edges."""
    # Build line graph adjacency directly (avoid external dependency on networkx)
    vertices, edges = build_W33()
    n = len(edges)
    A = np.zeros((n, n), dtype=float)
    for i in range(n):
        u, v = edges[i]
        for j in range(i + 1, n):
            a, b = edges[j]
            # line graph adjacency: edges share a vertex
            if u == a or u == b or v == a or v == b:
                A[i, j] = A[j, i] = 1.0

    # spectral embedding via eigenvectors of adjacency
    vals, vecs = np.linalg.eigh(A)
    idx = np.argsort(vals)[::-1]
    vecs = vecs[:, idx]
    k = min(k, vecs.shape[1])
    emb = vecs[:, :k]
    # normalize rows
    norms = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12
    emb = emb / norms
    return emb


def compute_root_graph_embedding(k=16, relation="abs1"):
    """Compute spectral embedding for E8 root graph using a relation on inner products.
    relation: 'abs1' -> |dot| == 1, '1' -> dot == 1, '-1' -> dot == -1
    """
    roots = [np.array(r, dtype=float) for r in build_E8_roots()]
    n = len(roots)
    A = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            ip = int(np.dot(roots[i], roots[j]))
            ok = False
            if relation == "abs1":
                ok = abs(ip) == 1
            elif relation == "1":
                ok = ip == 1
            elif relation == "-1":
                ok = ip == -1
            if ok:
                A[i, j] = A[j, i] = 1.0

    vals, vecs = np.linalg.eigh(A)
    idx = np.argsort(vals)[::-1]
    vecs = vecs[:, idx]
    k = min(k, vecs.shape[1])
    emb = vecs[:, :k]
    norms = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12
    emb = emb / norms
    return emb


def run_graph_embedding_mapping(k=16):
    """Compute embeddings of edge-line graph and root graph, align via anchors and assign.
    Returns mapping, candidate distances and transform used.
    """
    print("Computing line-graph embedding for edges...")
    edge_emb = compute_line_graph_embedding(k=k)
    print("Computing root-graph embedding (abs1 relation) ...")
    root_emb = compute_root_graph_embedding(k=k, relation="abs1")

    # Use anchor correspondences to compute Procrustes on embeddings
    anchors = anchors_from_strategies()
    if len(anchors) < 10:
        print("Not enough anchors for embedding alignment; returning empty")
        return {}, [], None

    # anchor indices
    edge_idx_to_root = {e: tuple(r) for (e, _, r) in anchors}
    anchor_edges = []
    anchor_roots = []
    roots = [tuple(r) for r in build_E8_roots()]
    root_index = {tuple(r): i for i, r in enumerate(roots)}
    for eidx, _, r in anchors:
        anchor_edges.append(eidx)
        anchor_roots.append(root_index[tuple(r)])

    A = edge_emb[np.array(anchor_edges)]
    B = root_emb[np.array(anchor_roots)]

    s_emb, R_emb, t_emb = compute_procrustes(A, B, allow_scale=True)
    print(f"Embedding transform: scale={s_emb:.6f}, det(R)={np.linalg.det(R_emb):.6f}")

    # transform edge embeddings
    edge_emb_t = (edge_emb.dot(R_emb)) * s_emb + t_emb

    # Compute cost matrix in embedding space
    n_edges = edge_emb_t.shape[0]
    n_roots = root_emb.shape[0]
    cost = np.linalg.norm(edge_emb_t[:, None, :] - root_emb[None, :, :], axis=2)

    # Hungarian assignment
    mapping = {}
    try:
        from scipy.optimize import linear_sum_assignment

        row_ind, col_ind = linear_sum_assignment(cost)
        for r, c in zip(row_ind, col_ind):
            mapping[r] = tuple(np.array(build_E8_roots())[c])
        method_used = "hungarian_emb"
    except Exception:
        # greedy fallback on embedding nearest
        candidate_triples = []
        for i in range(n_edges):
            j = int(np.argmin(cost[i]))
            candidate_triples.append(
                (i, tuple(np.array(build_E8_roots())[j]), float(cost[i, j]))
            )
        mapping = greedy_bipartite_match(
            sorted(candidate_triples, key=lambda x: x[2]), n_edges, n_roots
        )
        method_used = "greedy_emb"

    # Stats
    matched = len(mapping)
    out = ARTIFACTS / "edge_root_mapping_embedding.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump({"method": method_used, "matched": matched}, f, indent=2)

    print("Embedding mapping matched:", matched)
    return mapping, cost, (s_emb, R_emb, t_emb)


def run_geometry_mapping(tol=1e-8):
    """Geometric anchor-based Procrustes mapping (original method).
    Returns (mapping, candidate_triples, (s,R,t))
    """
    vertices, edges = build_W33()
    E8_roots = [np.array(r, dtype=float) for r in build_E8_roots()]

    anchors = anchors_from_strategies()
    print(f"Anchors available: {len(anchors)}")
    assert len(anchors) >= 4, "Not enough anchors to compute stable transform"

    A = np.vstack([v for (_, v, _) in anchors])
    B = np.vstack([r for (_, _, r) in anchors])

    s, R, t = compute_procrustes(A, B, allow_scale=True)
    print(f"Computed transform: scale={s:.6f}, det(R)={np.linalg.det(R):.6f}")

    # Generate candidate assignments (and full cost matrix for global assignment)
    candidate_triples = []  # (edge_idx, root_tuple, dist)
    n_edges = len(edges)
    n_roots = len(E8_roots)
    cost = np.full((n_edges, n_roots), fill_value=np.inf)

    for eidx in range(n_edges):
        vec_candidates = all_lift_variants(eidx)
        best = None
        for v in vec_candidates:
            v_trans = s * (v.dot(R)) + t
            arr = np.vstack(E8_roots)
            dists = np.linalg.norm(arr - v_trans.reshape(1, -1), axis=1)
            cost[eidx] = np.minimum(cost[eidx], dists)
            j = int(np.argmin(dists))
            dist = float(dists[j])
            root = tuple(arr[j])
            if best is None or dist < best[0]:
                best = (dist, root, v, v_trans)
        if best is not None:
            candidate_triples.append((eidx, best[1], best[0]))

    candidate_triples.sort(key=lambda x: x[2])

    # Try Hungarian assignment
    mapping = {}
    try:
        from scipy.optimize import linear_sum_assignment

        row_ind, col_ind = linear_sum_assignment(cost)
        for r, c in zip(row_ind, col_ind):
            mapping[r] = tuple(E8_roots[c])
        method_used = "hungarian"
    except Exception:
        mapping = greedy_bipartite_match(candidate_triples, n_edges, n_roots)
        method_used = "greedy"

    # Stats
    matched = len(mapping)
    close_matches = sum(1 for (_, _, d) in candidate_triples if d < tol)

    result = {
        "n_edges": n_edges,
        "n_roots": n_roots,
        "anchors": len(anchors),
        "matched": matched,
        "close_matches": close_matches,
        "assignment_method": method_used,
    }

    outp = ARTIFACTS / "edge_root_mapping_geom.json"
    with outp.open("w", encoding="utf-8") as f:
        json.dump({"result": result, "sample": list(mapping.items())[:20]}, f, indent=2)

    print("Geometric mapping summary:", result)
    return mapping, candidate_triples, (s, R, t)


def run_iterative_refinement(max_iter=10, add_tol=1e-8, tol=1e-6):
    """Iterative EM-style refinement: grow anchors from high-confidence matches and recompute transforms."""
    vertices, edges = build_W33()
    E8_roots = [np.array(r, dtype=float) for r in build_E8_roots()]

    anchors = {e: (v, r) for (e, v, r) in anchors_from_strategies()}
    print(f"Starting anchors: {len(anchors)}")

    prev_best = None
    best_mapping = {}
    best_metrics = None

    for it in range(max_iter):
        # partition anchors
        anchors_list = [(e, v, r) for e, (v, r) in anchors.items()]
        anchors_int = [
            (e, v, r) for (e, v, r) in anchors_list if all(c == int(c) for c in r)
        ]
        anchors_half = [
            (e, v, r) for (e, v, r) in anchors_list if not all(c == int(c) for c in r)
        ]

        transforms = []
        if len(anchors_int) >= 3:
            A = np.vstack([v for (_, v, _) in anchors_int])
            B = np.vstack([r for (_, _, r) in anchors_int])
            s, R, t = compute_procrustes(A, B, allow_scale=True)
            transforms.append(("int", s, R, t))
        if len(anchors_half) >= 3:
            A = np.vstack([v for (_, v, _) in anchors_half])
            B = np.vstack([r for (_, _, r) in anchors_half])
            s, R, t = compute_procrustes(A, B, allow_scale=True)
            transforms.append(("half", s, R, t))
        if not transforms and len(anchors_list) >= 3:
            A = np.vstack([v for (_, v, _) in anchors_list])
            B = np.vstack([r for (_, _, r) in anchors_list])
            s, R, t = compute_procrustes(A, B, allow_scale=True)
            transforms.append(("all", s, R, t))

        # candidate best distances per edge across transforms
        n_edges = len(edges)
        n_roots = len(E8_roots)
        cost = np.full((n_edges, n_roots), fill_value=np.inf)
        best_info = {}
        for eidx in range(n_edges):
            vec_candidates = all_lift_variants(eidx)
            for v in vec_candidates:
                for name, s, R, t in transforms:
                    v_trans = s * (v.dot(R)) + t
                    arr = np.vstack(E8_roots)
                    dists = np.linalg.norm(arr - v_trans.reshape(1, -1), axis=1)
                    cost[eidx] = np.minimum(cost[eidx], dists)
                    j = int(np.argmin(dists))
                    dist = float(dists[j])
                    if (eidx not in best_info) or (dist < best_info[eidx][0]):
                        best_info[eidx] = (dist, tuple(arr[j]), name)

        # Solve assignment
        try:
            from scipy.optimize import linear_sum_assignment

            row_ind, col_ind = linear_sum_assignment(cost)
            mapping = {
                int(r): tuple(E8_roots[int(c)]) for r, c in zip(row_ind, col_ind)
            }
            method_used = "hungarian"
        except Exception:
            candidate_triples = [
                (e, best_info[e][1], best_info[e][0])
                for e in range(n_edges)
                if e in best_info
            ]
            candidate_triples.sort(key=lambda x: x[2])
            mapping = greedy_bipartite_match(candidate_triples, n_edges, n_roots)
            method_used = "greedy"

        # compute high-confidence matches (dist < add_tol)
        added = 0
        for e, r in mapping.items():
            dist = best_info.get(e, (math.inf, None, None))[0]
            if dist < add_tol and e not in anchors:
                # need the corresponding lift vector
                # find the lift that produced this root in best_info
                anchors[e] = (None, np.array(r, dtype=float))
                added += 1

        print(
            f"Iteration {it}: method={method_used} mapped={len(mapping)} added_anchors={added}"
        )

        # stop if nothing new added
        if added == 0:
            # fallback: try more lenient add_tol and break
            if add_tol < 1e-3:
                add_tol *= 10
                print(f"No anchors added — increasing add_tol to {add_tol}")
                continue
            break

        # keep best mapping
        if best_metrics is None or len(mapping) > best_metrics:
            best_mapping = mapping
            best_metrics = len(mapping)

    out = ARTIFACTS / "edge_root_mapping_iterative.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(
            {"best_matched": best_metrics, "final_anchors": len(anchors)}, f, indent=2
        )

    print("Iterative best matched:", best_metrics, "final anchors:", len(anchors))
    return best_mapping, anchors, transforms


def local_search_refine_mapping(
    initial_mapping, relation="abs1", iterations=20000, temp=0.01
):
    """Local swap-based refinement to maximize adjacency-preservation score.

    initial_mapping: dict edge_idx -> root_tuple
    relation: root adjacency rule (abs1, 1, -1)
    """
    # Build line-graph adjacency for edges
    vertices, edges = build_W33()
    n_edges = len(edges)
    L_adj = [set() for _ in range(n_edges)]
    for i in range(n_edges):
        u, v = edges[i]
        for j in range(i + 1, n_edges):
            a, b = edges[j]
            if u == a or u == b or v == a or v == b:
                L_adj[i].add(j)
                L_adj[j].add(i)

    # Build root index map and root adjacency
    roots = [tuple(r) for r in build_E8_roots()]
    root_index = {r: i for i, r in enumerate(roots)}
    n_roots = len(roots)
    R_adj = [set() for _ in range(n_roots)]
    for i in range(n_roots):
        ri = np.array(roots[i], dtype=float)
        for j in range(i + 1, n_roots):
            rj = np.array(roots[j], dtype=float)
            ip = int(np.dot(ri, rj))
            ok = False
            if relation == "abs1":
                ok = abs(ip) == 1
            elif relation == "1":
                ok = ip == 1
            elif relation == "-1":
                ok = ip == -1
            if ok:
                R_adj[i].add(j)
                R_adj[j].add(i)

    # Convert initial mapping to arrays of indices
    edge_to_root = {}
    for e, rtuple in initial_mapping.items():
        edge_to_root[e] = root_index[tuple(rtuple)]

    # fill unassigned edges randomly with unused roots
    unused_roots = set(range(n_roots)) - set(edge_to_root.values())
    for e in range(n_edges):
        if e not in edge_to_root:
            if unused_roots:
                edge_to_root[e] = unused_roots.pop()
            else:
                edge_to_root[e] = e % n_roots

    # compute initial score
    def compute_score(mapping):
        score = 0
        for i in range(n_edges):
            ri = mapping[i]
            for j in L_adj[i]:
                if j <= i:
                    continue
                rj = mapping[j]
                if rj in R_adj[ri]:
                    score += 1
        return score

    current_score = compute_score(edge_to_root)
    best_score = current_score
    best_map = edge_to_root.copy()

    import random

    for it in range(iterations):
        # pick two random edges to swap roots
        e1, e2 = random.sample(range(n_edges), 2)
        r1 = edge_to_root[e1]
        r2 = edge_to_root[e2]

        # compute delta score efficiently by looking at neighbors
        def local_contrib(e, mapping):
            ri = mapping[e]
            s = 0
            for j in L_adj[e]:
                if j == e:
                    continue
                rj = mapping[j]
                if rj in R_adj[ri]:
                    s += 1
            return s

        before = local_contrib(e1, edge_to_root) + local_contrib(e2, edge_to_root)
        # perform swap
        edge_to_root[e1], edge_to_root[e2] = r2, r1
        after = local_contrib(e1, edge_to_root) + local_contrib(e2, edge_to_root)
        delta = after - before
        accept = False
        if delta >= 0:
            accept = True
        else:
            # Metropolis criterion
            if random.random() < math.exp(delta / (temp + 1e-12)):
                accept = True
        if not accept:
            # revert
            edge_to_root[e1], edge_to_root[e2] = r1, r2
        else:
            current_score += delta
            if current_score > best_score:
                best_score = current_score
                best_map = edge_to_root.copy()

    print(
        f"Local search best score: {best_score} (initial {compute_score(edge_to_root)})"
    )
    # Convert best_map back to edge->root tuples
    final_mapping = {e: tuple(roots[idx]) for e, idx in best_map.items()}
    return final_mapping, best_score


def run_mapping(tol=1e-8):
    """Run the three mapping strategies and summarize results."""
    mapping_geom, candidate_triples, geom_transform = run_geometry_mapping(tol=tol)
    mapping_emb, cost_emb, emb_transform = run_graph_embedding_mapping(k=16)
    mapping_iter, final_anchors, transforms_iter = run_iterative_refinement()

    # Write a summary
    out = ARTIFACTS / "edge_root_mapping_summary.json"
    summary = {
        "geom_matched": len(mapping_geom) if mapping_geom else 0,
        "embedding_matched": len(mapping_emb) if mapping_emb else 0,
        "iterated_matched": len(mapping_iter) if mapping_iter else 0,
    }
    with out.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Final summary:", summary)
    return (
        mapping_geom,
        mapping_emb,
        mapping_iter,
        (geom_transform, emb_transform, transforms_iter),
    )


if __name__ == "__main__":
    run_mapping()
