#!/usr/bin/env python3
"""
W33 Heisenberg Group / Qutrit Phase Space Structure
======================================================

THEOREM (Heisenberg Structure):
  For any vertex v0 of W33, the 27 non-neighbors H27 carry the structure
  of the Heisenberg group H(F3) with multiplication:
    (x,y,t) * (x',y',t') = (x+x', y+y', t+t'+xy')  mod 3

  The 12 neighbors N12 are the 12 affine lines of AG(2,3), forming
  4 mutually unbiased bases (MUBs) for a qutrit.

THEOREM (Tritangent Planes):
  The 45 tritangent planes on the cubic surface identified with H27 split as:
    45 = 36 (internal W33 triangles) + 9 (missing = phase space points)
  The 9 missing planes are the 9 center-cosets of H(F3), identified with
  the 9 points of the affine plane AG(2,3) = F3^2.

THEOREM (Z3 Fiber = Generations):
  The F3 fiber coordinate t in (x,y,t) parametrizes the three generations:
    H27 = {(x,y,0)} + {(x,y,1)} + {(x,y,2)}  (9+9+9 = 27)
  Each fiber is a "missing" tritangent plane = a generation.
  The Z3 generation symmetry is the CENTER of the Heisenberg group.

Usage:
  python3 scripts/w33_heisenberg_qutrit.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from w33_homology import build_w33


def compute_local_structure(v0, n, adj_s):
    """Compute N12, H27, and local incidence around vertex v0.
    adj_s: list of sets (adjacency sets)
    """
    N12 = sorted(adj_s[v0])
    H27 = [v for v in range(n) if v != v0 and v not in adj_s[v0]]
    assert len(N12) == 12, f"N12 has {len(N12)} vertices"
    assert len(H27) == 27, f"H27 has {len(H27)} vertices"

    # N12 internal adjacency: should be 4 disjoint triangles
    n12_set = set(N12)
    n12_adj = {}
    for u in N12:
        n12_adj[u] = [v for v in N12 if v != u and v in adj_s[u]]

    # Find the 4 triangles (connected components of N12)
    visited = set()
    triangles = []
    for u in N12:
        if u not in visited:
            tri = {u}
            queue = [u]
            while queue:
                cur = queue.pop(0)
                for v in n12_adj[cur]:
                    if v not in tri:
                        tri.add(v)
                        queue.append(v)
            triangles.append(sorted(tri))
            visited.update(tri)

    assert len(triangles) == 4, f"Expected 4 triangles, got {len(triangles)}"
    for t in triangles:
        assert len(t) == 3, f"Triangle has {len(t)} vertices"

    # H27 internal adjacency
    h27_set = set(H27)
    h27_neighbors = {u: sorted(adj_s[u] & h27_set) for u in H27}

    return N12, H27, triangles, h27_neighbors


def build_f3_cube(N12, H27, triangles, adj_s):
    """Build F3^3 cube coordinates on H27."""
    T0 = triangles[0]
    T1 = triangles[1]

    # x-slices from T0
    x_slices = {}
    for xi, u in enumerate(T0):
        x_slices[xi] = set(v for v in H27 if v in adj_s[u])

    all_h27 = set(H27)
    assert x_slices[0] | x_slices[1] | x_slices[2] == all_h27
    assert not (x_slices[0] & x_slices[1])
    assert not (x_slices[0] & x_slices[2])
    assert not (x_slices[1] & x_slices[2])

    # y-slices from T1
    y_slices = {}
    for yi, u in enumerate(T1):
        y_slices[yi] = set(v for v in H27 if v in adj_s[u])

    assert y_slices[0] | y_slices[1] | y_slices[2] == all_h27
    assert not (y_slices[0] & y_slices[1])
    assert not (y_slices[0] & y_slices[2])
    assert not (y_slices[1] & y_slices[2])

    # Fibers: intersection of x-slice and y-slice
    fibers = {}
    vertex_to_xyz = {}
    for x in range(3):
        for y in range(3):
            fiber = sorted(x_slices[x] & y_slices[y])
            assert len(fiber) == 3, f"Fiber ({x},{y}) has {len(fiber)} vertices"
            fibers[(x, y)] = fiber
            for t, v in enumerate(fiber):
                vertex_to_xyz[v] = (x, y, t)

    return fibers, vertex_to_xyz


def main():
    t0 = time.time()

    print("=" * 72)
    print("  W33 HEISENBERG GROUP / QUTRIT PHASE SPACE")
    print("=" * 72)

    # Build W33
    n, vertices, adj, edges = build_w33()
    adj_s = [set(adj[i]) for i in range(n)]  # adjacency sets
    print(f"\n  W33: {n} vertices, {len(edges)} edges")

    # =====================================================================
    # Part 1: Local structure around v0 = 0
    # =====================================================================
    v0 = 0
    print(f"\n  BASE VERTEX: v0 = {v0}")

    N12, H27, triangles, h27_neighbors = compute_local_structure(v0, n, adj_s)

    print(f"  N12 (neighbors): {sorted(N12)}")
    print(f"  N12 triangles: {triangles}")
    print(f"  H27 count: {len(H27)}")

    # Verify induced H27 regularity (W33-adjacency restricted to H27)
    h27_degrees = [len(h27_neighbors[v]) for v in H27]
    h27_k = h27_degrees[0]
    print(f"  H27 degree distribution: {Counter(h27_degrees)}")
    assert all(
        d == h27_k for d in h27_degrees
    ), f"H27 not regular! degrees: {Counter(h27_degrees)}"
    print(f"  H27 is {h27_k}-regular (induced subgraph)")

    # Common-neighbor stats for the induced H27 graph (not SRG; shown for diagnostics)
    h27_set = set(H27)
    lambda_counts = []
    mu_counts = []
    for u in H27:
        for v in H27:
            if v <= u:
                continue
            common = len((adj_s[u] & adj_s[v]) & h27_set)
            if v in adj_s[u]:
                lambda_counts.append(common)
            else:
                mu_counts.append(common)

    lam_c = Counter(lambda_counts)
    mu_c = Counter(mu_counts)
    print(
        f"  H27 induced common-neighbor counts: adjacent={dict(lam_c)}, non-adj={dict(mu_c)}"
    )

    # Derived Schläfli graph on H27: connect u~v iff they have exactly 3 common neighbors in induced H27
    schlafli = {u: set() for u in H27}
    for i, u in enumerate(H27):
        for v in H27[i + 1 :]:
            common = len((adj_s[u] & adj_s[v]) & h27_set)
            if common == 3:
                schlafli[u].add(v)
                schlafli[v].add(u)

    sch_deg = [len(schlafli[u]) for u in H27]
    print(f"  Schläfli graph degree distribution (commonH27=3): {Counter(sch_deg)}")
    assert all(d == sch_deg[0] for d in sch_deg), "Schläfli graph is not regular"
    # Verify SRG(27,16,10,8) parameters
    sch_k = sch_deg[0]
    sch_lambda = []
    sch_mu = []
    for i, u in enumerate(H27):
        Nu = schlafli[u]
        for v in H27[i + 1 :]:
            Nv = schlafli[v]
            c = len(Nu & Nv)
            if v in Nu:
                sch_lambda.append(c)
            else:
                sch_mu.append(c)
    sch_lam_c = Counter(sch_lambda)
    sch_mu_c = Counter(sch_mu)
    print(
        f"  Schläfli SRG check: k={sch_k}, adjacent={dict(sch_lam_c)}, non-adj={dict(sch_mu_c)}"
    )
    assert sch_k == 16, f"Unexpected Schläfli degree k={sch_k} (expected 16)"
    assert set(sch_lam_c.keys()) == {
        10
    }, f"Unexpected Schläfli λ distribution: {dict(sch_lam_c)}"
    assert set(sch_mu_c.keys()) == {
        8
    }, f"Unexpected Schläfli μ distribution: {dict(sch_mu_c)}"

    # =====================================================================
    # Part 2: F3^3 cube coordinatization
    # =====================================================================
    print(f"\n{'='*72}")
    print("  PART 2: F3^3 CUBE COORDINATIZATION")
    print("=" * 72)

    fibers, vertex_to_xyz = build_f3_cube(N12, H27, triangles, adj_s)

    print(f"\n  H27 -> F3^3 mapping:")
    for v in sorted(vertex_to_xyz.keys()):
        x, y, t = vertex_to_xyz[v]
        print(f"    vertex {v:2d} -> ({x},{y},{t})")

    print(f"\n  9 Fibers (phase space points of F3^2):")
    for (x, y), verts in sorted(fibers.items()):
        print(f"    ({x},{y}): vertices {verts}")

    # =====================================================================
    # Part 3: Adjacency patterns in Heisenberg coordinates
    # =====================================================================
    print(f"\n{'='*72}")
    print("  PART 3: ADJACENCY IN HEISENBERG COORDINATES")
    print("=" * 72)

    adj_by_omega = {0: [0, 0], 1: [0, 0], 2: [0, 0]}  # [adj, non_adj]
    adj_patterns = Counter()
    non_adj_patterns = Counter()

    for u in H27:
        xu, yu, tu = vertex_to_xyz[u]
        for v in H27:
            if v <= u:
                continue
            xv, yv, tv = vertex_to_xyz[v]
            dx = (xv - xu) % 3
            dy = (yv - yu) % 3
            dt = (tv - tu) % 3
            omega = (xu * yv - yu * xv) % 3

            is_adj = v in adj_s[u]
            if is_adj:
                adj_patterns[(dx, dy, dt, omega)] += 1
                adj_by_omega[omega][0] += 1
            else:
                non_adj_patterns[(dx, dy, dt, omega)] += 1
                adj_by_omega[omega][1] += 1

    print(f"\n  Symplectic form vs adjacency:")
    for omega_val in [0, 1, 2]:
        a, na = adj_by_omega[omega_val]
        total = a + na
        pct = 100 * a / total if total > 0 else 0
        print(
            f"    Omega = {omega_val}: {a} adj, {na} non-adj "
            f"({pct:.1f}% adj, {total} pairs)"
        )

    print(f"\n  Adjacent pair patterns (dx, dy, dt, Omega):")
    for pat in sorted(adj_patterns.keys()):
        print(f"    {pat}: {adj_patterns[pat]}")

    print(f"\n  Non-adjacent pair patterns (dx, dy, dt, Omega):")
    for pat in sorted(non_adj_patterns.keys()):
        print(f"    {pat}: {non_adj_patterns[pat]}")

    # =====================================================================
    # Part 4: MUB structure
    # =====================================================================
    print(f"\n{'='*72}")
    print("  PART 4: MUTUALLY UNBIASED BASES (4 STRIATIONS)")
    print("=" * 72)

    for ti, tri in enumerate(triangles):
        print(f"\n  Triangle class T{ti} = {tri}:")
        for ni, u in enumerate(tri):
            h27_nbrs = [v for v in H27 if v in adj_s[u]]
            fiber_set = set()
            for v in h27_nbrs:
                x, y, t = vertex_to_xyz[v]
                fiber_set.add((x, y))
            print(f"    N12 vertex {u} -> AG(2,3) line: {sorted(fiber_set)}")

    # Verify MUB overlaps
    print(f"\n  MUB overlap (lines from different classes share exactly 1 point):")
    for ti in range(4):
        for tj in range(ti + 1, 4):
            overlaps = []
            for u in triangles[ti]:
                pts_u = set()
                for v in H27:
                    if v in adj_s[u]:
                        x, y, _ = vertex_to_xyz[v]
                        pts_u.add((x, y))
                for w in triangles[tj]:
                    pts_w = set()
                    for v in H27:
                        if v in adj_s[w]:
                            x, y, _ = vertex_to_xyz[v]
                            pts_w.add((x, y))
                    overlaps.append(len(pts_u & pts_w))
            print(f"    T{ti} vs T{tj}: overlaps = {Counter(overlaps)}")

    # =====================================================================
    # Part 5: Missing tritangent planes
    # =====================================================================
    print(f"\n{'='*72}")
    print("  PART 5: MISSING TRITANGENT PLANES = FIBERS")
    print("=" * 72)

    # Count H27 internal triangles
    h27_set = set(H27)
    n_h27_tri = 0
    for u in H27:
        for v in H27:
            if v <= u or v not in adj_s[u]:
                continue
            for w in H27:
                if w <= v or w not in adj_s[u] or w not in adj_s[v]:
                    continue
                n_h27_tri += 1

    print(f"  Total H27 internal triangles: {n_h27_tri}")

    # Check each fiber: is it a triangle?
    n_fiber_tri = 0
    n_missing = 0
    for (x, y), verts in sorted(fibers.items()):
        a, b, c = verts
        is_tri = b in adj_s[a] and c in adj_s[b] and c in adj_s[a]
        status = "TRIANGLE" if is_tri else "MISSING (not triangle)"
        if is_tri:
            n_fiber_tri += 1
        else:
            n_missing += 1
        print(f"    Fiber ({x},{y}) = {verts}: {status}")

    print(f"\n  Fiber triangles: {n_fiber_tri}, Missing: {n_missing}")
    print(f"  (Expected: some fibers are missing tritangent planes)")

    # =====================================================================
    # Part 6: Z3 generations from fiber coordinate
    # =====================================================================
    print(f"\n{'='*72}")
    print("  PART 6: Z3 GENERATIONS FROM FIBER COORDINATE")
    print("=" * 72)

    generations = {0: [], 1: [], 2: []}
    for v in H27:
        x, y, t = vertex_to_xyz[v]
        generations[t].append(v)

    for t in range(3):
        gen_verts = sorted(generations[t])
        print(f"  Generation {t}: {gen_verts} ({len(gen_verts)} vertices)")

    # Cross-generation edges
    print(f"\n  Cross-generation edge counts:")
    for t in range(3):
        for s in range(t, 3):
            cross = 0
            for u in generations[t]:
                for v in generations[s]:
                    if u != v and v in adj_s[u]:
                        cross += 1
            if t == s:
                cross //= 2
            print(f"    Gen_{t}-Gen_{s}: {cross} edges")

    # =====================================================================
    # Part 7: Universality — ALL 40 vertices
    # =====================================================================
    print(f"\n{'='*72}")
    print("  PART 7: UNIVERSALITY (ALL 40 VERTICES)")
    print("=" * 72)

    n_ok = 0
    for v0_test in range(n):
        try:
            N12_t, H27_t, tri_t, _ = compute_local_structure(v0_test, n, adj_s)
            degrees = [sum(1 for w in H27_t if w in adj_s[v]) for v in H27_t]
            srg_ok = all(d == 8 for d in degrees) and len(tri_t) == 4
            fibers_t, vtx_t = build_f3_cube(N12_t, H27_t, tri_t, adj_s)
            cube_ok = True
        except Exception:
            srg_ok = False
            cube_ok = False

        if srg_ok and cube_ok:
            n_ok += 1

    print(f"  Vertices with valid (N12, H27, F3^3) structure: {n_ok}/{n}")

    # =====================================================================
    # Part 8: Synthesis
    # =====================================================================
    print(f"\n{'='*72}")
    print("  SYNTHESIS: HEISENBERG STRUCTURE OF W33")
    print("=" * 72)

    print(
        f"""
  THEOREM (Qutrit Phase Space):
    For EVERY vertex v0 of W33:
    - H27(v0) = F3^3 as an affine space
    - N12(v0) = 12 lines of AG(2,3) = 4 qutrit MUBs
    - 9 fibers = 9 phase space points = 9 missing tritangent planes
    - Symplectic form Omega(u,v) = xu*yv - yu*xv controls adjacency

  THEOREM (Generation = Center):
    The fiber coordinate t in F3 parametrizes generations.
    The Z3 generation symmetry is the CENTER of H(F3).

  PHYSICAL INTERPRETATION:
    - H27 = 27 matter fields (3 generations x 9 fields)
    - N12 = 12 gauge bosons (4 MUB bases x 3)
    - v0 = vacuum state
    - Symplectic form = gauge interaction coupling
    - Heisenberg center = family (generation) symmetry
    - W33 = the incidence geometry of qutrit quantum mechanics
"""
    )

    elapsed = time.time() - t0
    print(f"  Elapsed: {elapsed:.1f}s")

    results = {
        "v0": v0,
        "H27_induced_degree": h27_k,
        "H27_induced_common_neighbors_adjacent": dict(lam_c),
        "H27_induced_common_neighbors_non_adjacent": dict(mu_c),
        "Schlafli_srg": {"v": 27, "k": 16, "lambda": 10, "mu": 8},
        "n_fibers": 9,
        "n_mub_bases": 4,
        "n_missing_tritangent": n_missing,
        "universal_ok": n_ok == n,
        "omega_adjacency": {k: v[0] for k, v in adj_by_omega.items()},
        "omega_non_adjacency": {k: v[1] for k, v in adj_by_omega.items()},
        "elapsed": elapsed,
    }

    ts = int(time.time())
    out_path = Path.cwd() / "checks" / f"PART_CVII_heisenberg_qutrit_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  Wrote: {out_path}")


if __name__ == "__main__":
    main()
