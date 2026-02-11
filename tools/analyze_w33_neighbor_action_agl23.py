#!/usr/bin/env python3
"""Analyze the W33 neighborhood action that realizes AGL(2,3).

This is a concrete bridge between:
  - the 40-vertex symplectic polar graph W33 (aka the point graph of W(3,3)),
  - its full automorphism group of order 51,840 (PSp extended by an
    anti-symplectic similitude),
  - and the induced action on the 12-neighborhood of a vertex, which factors
    through a 3-element kernel to a 432-element group isomorphic to AGL(2,3).

Key computed facts:
  - The 12 neighbors split as 4 disjoint triangles (the 4 parallel classes /
    striations of the affine plane AG(2,3) line graph).
  - The induced neighbor action has size 432 and acts as full S4 on the 4
    triangles (PGL(2,3) ≅ S4).
  - The 45 involutions in AGL(2,3) split as:
      * 36 "reflections" (det=2 in the affine model): fix an entire triangle
        (a striation) pointwise.
      * 9 "half-turns" (det=1): fix exactly one vertex in each triangle.
    Reflection centralizers have size 12 (D12 fingerprint), matching the
    det=2 involution class computed in `tools/analyze_agl23_det2_involution_class.py`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.analyze_balanced_orbit_stabilizer as w33


def _repo_rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT.resolve()))
    except ValueError:
        return str(resolved)


def _compose_perm(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    """Return p∘q (apply q, then p)."""

    n = len(p)
    return tuple(p[q[i]] for i in range(n))


def _is_involution(p: tuple[int, ...]) -> bool:
    n = len(p)
    return all(p[p[i]] == i for i in range(n))


def _invert_perm(p: tuple[int, ...]) -> tuple[int, ...]:
    inv = [0] * len(p)
    for i, v in enumerate(p):
        inv[int(v)] = int(i)
    return tuple(inv)


def _perm_order(p: tuple[int, ...]) -> int:
    n = len(p)
    seen = [False] * n
    out = 1
    for i in range(n):
        if seen[i]:
            continue
        cur = i
        count = 0
        while not seen[cur]:
            seen[cur] = True
            cur = int(p[cur])
            count += 1
        out = math.lcm(out, int(count))
    return int(out)


def _connected_components(adj: list[list[int]]) -> list[list[int]]:
    n = len(adj)
    seen: set[int] = set()
    comps: list[list[int]] = []
    for i in range(n):
        if i in seen:
            continue
        q: deque[int] = deque([i])
        comp: list[int] = []
        while q:
            u = q.popleft()
            if u in seen:
                continue
            seen.add(u)
            comp.append(u)
            for v in range(n):
                if adj[u][v] and v not in seen:
                    q.append(v)
        comps.append(sorted(comp))
    return sorted(comps)


def _fixed_points(p: tuple[int, ...]) -> set[int]:
    return {i for i, v in enumerate(p) if i == v}


def _triangle_perm(
    p: tuple[int, ...], triangles: list[set[int]], tri_of: dict[int, int]
) -> tuple[int, ...] | None:
    img: list[int] = []
    for tri in triangles:
        mapped = {tri_of[int(p[v])] for v in tri}
        if len(mapped) != 1:
            return None
        img.append(int(next(iter(mapped))))
    return tuple(img)


def build_report(base_vertex: int = 0) -> dict[str, Any]:
    points, adj40, _edges = w33.build_w33()

    symp_gens = w33.get_generators(points)
    antisymp_mat = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 2, 0],
        [0, 0, 0, 2],
    ]  # diag(1,1,2,2) with multiplier 2
    antisymp = w33.matrix_to_vertex_perm(antisymp_mat, points)
    if antisymp is None:
        raise RuntimeError("Failed to build antisymplectic generator permutation")

    group40 = w33.enumerate_group(symp_gens + [antisymp])

    if not (0 <= int(base_vertex) < len(points)):
        raise ValueError(f"base_vertex must be in [0,{len(points)-1}]")
    v0 = int(base_vertex)

    stabilizer40 = [p for p in group40 if int(p[v0]) == v0]

    neighbors = [i for i in range(len(points)) if int(adj40[v0][i]) == 1]
    neighbors.sort()

    nbr_idx = {v: i for i, v in enumerate(neighbors)}
    induced12: set[tuple[int, ...]] = set()
    for p in stabilizer40:
        induced12.add(tuple(nbr_idx[int(p[v])] for v in neighbors))
    induced12_list = sorted(induced12)

    kernel_size = int(len(stabilizer40) // len(induced12_list))

    # Induced adjacency on the 12 neighbors: for W33 this is 4 disjoint K3's.
    adj12 = [
        [int(adj40[neighbors[i]][neighbors[j]]) for j in range(len(neighbors))]
        for i in range(len(neighbors))
    ]
    comps = _connected_components(adj12)

    # Validate the "4 triangles" structure.
    tri_sizes = Counter(len(c) for c in comps)
    deg_hist = Counter(sum(adj12[i][j] for j in range(12) if j != i) for i in range(12))
    triangles_ok = bool(
        len(comps) == 4
        and tri_sizes == Counter({3: 4})
        and deg_hist == Counter({2: 12})
    )

    triangles = [set(c) for c in comps]
    tri_of: dict[int, int] = {v: idx for idx, tri in enumerate(triangles) for v in tri}

    # Induced action on the 4 triangles (striations).
    tri_action: set[tuple[int, ...]] = set()
    tri_perm_map: dict[tuple[int, ...], tuple[int, ...]] = {}
    for p in induced12_list:
        img = _triangle_perm(p, triangles, tri_of)
        if img is None:
            raise RuntimeError("Induced element does not preserve triangle partition")
        tri_perm_map[p] = img
        tri_action.add(img)

    id_tri = tuple(range(4))
    tri_kernel = [p for p, img in tri_perm_map.items() if img == id_tri]
    tri_kernel_order_hist = Counter(_perm_order(p) for p in tri_kernel)

    # Within the triangle-kernel (size 18), the order-3 subgroup of size 9 is the
    # translation group (Z3)^2, and the extra involution is the scalar -I.
    translations = [p for p in tri_kernel if _perm_order(p) in {1, 3}]
    translations_set = set(translations)
    translations_is_subgroup = bool(
        translations
        and all(
            _compose_perm(a, b) in translations_set
            for a in translations
            for b in translations
        )
    )
    translations_is_abelian = bool(
        translations
        and all(
            _compose_perm(a, b) == _compose_perm(b, a)
            for a in translations
            for b in translations
        )
    )
    translations_normal = True
    if translations:
        for g in induced12_list:
            gin = _invert_perm(g)
            for t in translations:
                conj = _compose_perm(_compose_perm(g, t), gin)
                if conj not in translations_set:
                    translations_normal = False
                    break
            if not translations_normal:
                break

    id12 = tuple(range(12))
    involutions = [p for p in induced12_list if p != id12 and _is_involution(p)]

    # Classify involutions by fixed structure relative to the 4 triangles.
    reflection_count = 0
    rotation_count = 0
    refl_fixed_triangle_hist: Counter[int] = Counter()
    refl_axis_triangle_hist: Counter[int] = Counter()
    cent_hist_by_type: dict[str, Counter[int]] = {
        "reflection": Counter(),
        "rotation": Counter(),
    }
    reflections: list[tuple[int, ...]] = []
    rotations: list[tuple[int, ...]] = []

    for x in involutions:
        fixed = _fixed_points(x)
        full_tris = [i for i, tri in enumerate(triangles) if tri.issubset(fixed)]

        # Centralizer size in the induced neighbor group.
        cent = sum(
            1 for g in induced12_list if _compose_perm(g, x) == _compose_perm(x, g)
        )

        if len(fixed) != 4:
            raise RuntimeError(f"Unexpected involution fixed count {len(fixed)}")

        if len(full_tris) == 1:
            reflection_count += 1
            reflections.append(x)
            cent_hist_by_type["reflection"][int(cent)] += 1
            t_fix = int(full_tris[0])
            refl_fixed_triangle_hist[t_fix] += 1

            # Axis is the unique fixed vertex outside the fully fixed triangle.
            axis_candidates = sorted(fixed - triangles[t_fix])
            if len(axis_candidates) != 1:
                raise RuntimeError("Expected unique axis vertex outside fixed triangle")
            refl_axis_triangle_hist[tri_of[int(axis_candidates[0])]] += 1
        elif len(full_tris) == 0:
            rotation_count += 1
            rotations.append(x)
            cent_hist_by_type["rotation"][int(cent)] += 1
        else:
            raise RuntimeError("Unexpected involution fixed-triangle count")

    # Conjugacy + D12 fingerprint for reflections inside the induced neighbor action.
    reflection_conj_class_size = 0
    reflection_conj_class_is_single = False
    reflection_centralizer_order_hist: dict[str, int] | None = None
    reflection_centralizer_matches_d12 = False
    if reflections:
        r0 = reflections[0]
        conj = set()
        for g in induced12_list:
            gin = _invert_perm(g)
            conj.add(_compose_perm(_compose_perm(g, r0), gin))
        reflection_conj_class_size = int(len(conj))
        reflection_conj_class_is_single = bool(conj == set(reflections))

        cent = [
            g for g in induced12_list if _compose_perm(g, r0) == _compose_perm(r0, g)
        ]
        reflection_centralizer_order_hist = {
            str(k): int(v)
            for k, v in sorted(Counter(_perm_order(g) for g in cent).items())
        }
        reflection_centralizer_matches_d12 = bool(
            len(cent) == 12
            and reflection_centralizer_order_hist == {"1": 1, "2": 7, "3": 2, "6": 2}
        )

    return {
        "status": "ok",
        "generated_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "base_vertex": int(v0),
        "paths": {
            "w33_builder": _repo_rel(
                Path("tools/analyze_balanced_orbit_stabilizer.py")
            ),
        },
        "group": {
            "point_count": int(len(points)),
            "aut_group_order": int(len(group40)),
            "vertex_stabilizer_order": int(len(stabilizer40)),
        },
        "neighborhood": {
            "neighbor_count": int(len(neighbors)),
            "induced_subgraph_degree_histogram": {
                str(k): int(v) for k, v in sorted(deg_hist.items())
            },
            "triangle_components": [sorted(list(c)) for c in comps],
            "triangles_ok": bool(triangles_ok),
        },
        "neighbor_action": {
            "induced_group_order": int(len(induced12_list)),
            "kernel_order": int(kernel_size),
            "triangle_action_order": int(len(tri_action)),
            "triangle_action_is_S4": bool(len(tri_action) == 24),
            "triangle_kernel_order": int(len(tri_kernel)),
            "triangle_kernel_order_histogram": {
                str(k): int(v) for k, v in sorted(tri_kernel_order_hist.items())
            },
            "translations": {
                "order": int(len(translations)),
                "order_histogram": {
                    str(k): int(v)
                    for k, v in sorted(
                        Counter(_perm_order(p) for p in translations).items()
                    )
                },
                "is_subgroup": bool(translations_is_subgroup),
                "is_abelian": bool(translations_is_abelian),
                "is_normal": bool(translations_normal),
            },
        },
        "involutions": {
            "count": int(len(involutions)),
            "reflection_count": int(reflection_count),
            "rotation_count": int(rotation_count),
            "reflection_conjugacy_class_count": int(
                1 if reflection_conj_class_is_single else 0
            ),
            "reflection_conjugacy_class_size": int(reflection_conj_class_size),
            "reflection_centralizer_order_histogram": reflection_centralizer_order_hist,
            "reflection_centralizer_matches_d12_fingerprint": bool(
                reflection_centralizer_matches_d12
            ),
            "reflection_fixed_triangle_histogram": {
                str(k): int(v) for k, v in sorted(refl_fixed_triangle_hist.items())
            },
            "reflection_axis_triangle_histogram": {
                str(k): int(v) for k, v in sorted(refl_axis_triangle_hist.items())
            },
            "centralizer_size_histogram_by_type": {
                "reflection": {
                    str(k): int(v)
                    for k, v in sorted(cent_hist_by_type["reflection"].items())
                },
                "rotation": {
                    str(k): int(v)
                    for k, v in sorted(cent_hist_by_type["rotation"].items())
                },
            },
        },
        "claim_checks": {
            "aut_group_order_is_51840": bool(len(group40) == 51840),
            "vertex_stabilizer_order_is_1296": bool(len(stabilizer40) == 1296),
            "neighbor_count_is_12": bool(len(neighbors) == 12),
            "induced_neighbor_group_order_is_432": bool(len(induced12_list) == 432),
            "kernel_order_is_3": bool(kernel_size == 3),
            "triangles_ok": bool(triangles_ok),
            "triangle_action_is_S4": bool(len(tri_action) == 24),
            "triangle_kernel_order_is_18": bool(len(tri_kernel) == 18),
            "translation_subgroup_order_is_9": bool(len(translations) == 9),
            "translation_subgroup_is_normal_abelian": bool(
                translations_is_subgroup
                and translations_is_abelian
                and translations_normal
            ),
            "involutions_split_36_9": bool(
                len(involutions) == 45
                and reflection_count == 36
                and rotation_count == 9
            ),
            "reflection_centralizer_is_12": bool(
                cent_hist_by_type["reflection"] == Counter({12: 36})
            ),
            "reflections_form_single_conjugacy_class": bool(
                reflection_conj_class_is_single
            ),
            "reflection_centralizer_matches_d12_fingerprint": bool(
                reflection_centralizer_matches_d12
            ),
        },
        "claim_holds": bool(
            len(group40) == 51840
            and len(stabilizer40) == 1296
            and len(neighbors) == 12
            and len(induced12_list) == 432
            and kernel_size == 3
            and triangles_ok
            and len(tri_action) == 24
            and len(tri_kernel) == 18
            and len(translations) == 9
            and translations_is_subgroup
            and translations_is_abelian
            and translations_normal
            and len(involutions) == 45
            and reflection_count == 36
            and rotation_count == 9
            and cent_hist_by_type["reflection"] == Counter({12: 36})
            and reflection_conj_class_is_single
            and reflection_centralizer_matches_d12
        ),
    }


def render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# W33 Neighbor Action Realizes AGL(2,3) (2026-02-11)")
    lines.append("")
    lines.append(f"- base vertex: `{report['base_vertex']}`")
    lines.append(f"- claim holds: `{report['claim_holds']}`")
    lines.append("")
    lines.append("## Group Orders")
    lines.append("")
    g = report["group"]
    lines.append(f"- point count: `{g['point_count']}`")
    lines.append(f"- |Aut(W33)|: `{g['aut_group_order']}`")
    lines.append(f"- |Stab(v)|: `{g['vertex_stabilizer_order']}`")
    lines.append("")
    lines.append("## Neighborhood Geometry")
    lines.append("")
    nb = report["neighborhood"]
    lines.append(f"- neighbor count: `{nb['neighbor_count']}`")
    lines.append(
        f"- induced degree histogram: `{nb['induced_subgraph_degree_histogram']}`"
    )
    lines.append(
        f"- triangle components (parallel classes): `{nb['triangle_components']}`"
    )
    lines.append(f"- triangles OK: `{nb['triangles_ok']}`")
    lines.append("")
    lines.append("## Induced Neighbor Action")
    lines.append("")
    act = report["neighbor_action"]
    lines.append(f"- induced group order: `{act['induced_group_order']}`")
    lines.append(f"- kernel order: `{act['kernel_order']}`")
    lines.append(
        f"- action on 4 triangles: `{act['triangle_action_order']}` (S4: `{act['triangle_action_is_S4']}`)"
    )
    lines.append(f"- triangle-kernel order: `{act.get('triangle_kernel_order')}`")
    translations = act.get("translations", {})
    if translations:
        lines.append(
            "- translations (Z3^2) inside kernel: "
            f"`{translations.get('order')}` (normal+abelian: `{bool(translations.get('is_normal')) and bool(translations.get('is_abelian'))}`)"
        )
    lines.append("")
    lines.append("## Involutions (Reflections vs Half-Turns)")
    lines.append("")
    inv = report["involutions"]
    lines.append(f"- total involutions: `{inv['count']}`")
    lines.append(f"- reflections (fix a full triangle): `{inv['reflection_count']}`")
    lines.append(f"- half-turns (no full triangle fixed): `{inv['rotation_count']}`")
    lines.append(
        "- reflections form one conjugacy class: "
        f"`{bool(inv.get('reflection_conjugacy_class_count') == 1)}`"
    )
    if inv.get("reflection_centralizer_order_histogram") is not None:
        lines.append(
            "- reflection centralizer order histogram (D12): "
            f"`{inv['reflection_centralizer_order_histogram']}`"
        )
    lines.append(
        f"- reflection fixed-triangle histogram: `{inv['reflection_fixed_triangle_histogram']}`"
    )
    lines.append(
        f"- reflection axis-triangle histogram: `{inv['reflection_axis_triangle_histogram']}`"
    )
    lines.append(
        "- centralizer size histograms: "
        f"`{inv['centralizer_size_histogram_by_type']}`"
    )
    lines.append("")
    lines.append("## Cross-Reference")
    lines.append("")
    lines.append(
        "- The reflection centralizer fingerprint (`12`) matches the det=2 involution "
        "class computation in `docs/AGL23_DET2_INVOLUTION_CLASS_2026_02_11.md`."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-vertex", type=int, default=0)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "w33_neighbor_action_agl23_2026_02_11.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "docs" / "W33_NEIGHBOR_ACTION_AGL23_2026_02_11.md",
    )
    args = parser.parse_args()

    report = build_report(base_vertex=args.base_vertex)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_md(report), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
