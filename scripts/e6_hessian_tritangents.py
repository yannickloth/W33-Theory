#!/usr/bin/env python3
"""Hessian / Heisenberg decomposition of the 45 E6 cubic (tritangent) triads.

This repo contains an intrinsic, fully-computed model of the E6 27-set as a
3-adic Heisenberg-labelled space:

  H27  ≅  F3^2 × F3   with coordinates (u1,u2,z).

In that model, the 45 tritangent planes (triads) split canonically as:

  - 9  "fiber" triads  (constant-u, z runs over 0/1/2), and
  - 36 "affine-line" triads (u collinear in AG(2,3), constant z).

The same 36+9 split appears in the classical Hessian/Witting literature as
"36 tritangents in 12×(_3{4}_2) plus 9 diameter tritangents". We don't rely on
that literature here; we just verify the finite-geometry structure from our
artifacts.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

ART = ROOT / "artifacts"

U2 = Tuple[int, int]
U3 = Tuple[int, int, int]
Triad = Tuple[int, int, int]
Perm = Tuple[int, ...]
Mat2 = Tuple[Tuple[int, int], Tuple[int, int]]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _norm_triad(tri: Iterable[int]) -> Triad:
    a, b, c = (int(x) for x in tri)
    t = tuple(sorted((a, b, c)))
    if len(t) != 3:
        raise ValueError(f"bad triad: {tri!r}")
    return t  # type: ignore[return-value]


def _mod3(x: int) -> int:
    return int(x) % 3


def _u_add(a: U2, b: U2) -> U2:
    return (_mod3(a[0] + b[0]), _mod3(a[1] + b[1]))


def _u_sub(a: U2, b: U2) -> U2:
    return (_mod3(a[0] - b[0]), _mod3(a[1] - b[1]))


def _u_scale(a: U2, s: int) -> U2:
    return (_mod3(s * a[0]), _mod3(s * a[1]))

def _omega_u(a: U2, b: U2) -> int:
    """Alternating form omega((x,y),(x',y')) = x*y' - y*x' over F3."""
    return _mod3(a[0] * b[1] - a[1] * b[0])


def _psi(a: U2, u: U2) -> int:
    """Heisenberg cocycle psi = (1/2)·omega on F3, with 1/2 = 2 mod 3."""
    return _mod3(2 * _omega_u(a, u))


def _dir_canonical(d: U2) -> U2:
    """Canonicalize direction in F3^2 up to nonzero scalar multiples."""
    if d == (0, 0):
        raise ValueError("zero direction")
    d1 = (_mod3(d[0]), _mod3(d[1]))
    d2 = _u_scale(d1, 2)  # 2 = -1 mod 3
    return min(d1, d2)


@dataclass(frozen=True)
class HessianSplit:
    fiber_triads: List[Triad]
    affine_triads: List[Triad]
    u_lines: List[Tuple[U2, U2, U2]]
    u_line_directions: Dict[U2, List[Tuple[U2, U2, U2]]]
    e6id_to_vec: Dict[int, U3]
    vec_to_e6id: Dict[U3, int]


def load_heisenberg_model() -> Mapping[str, Any]:
    return _load_json(ART / "e6_cubic_affine_heisenberg_model.json")


def load_firewall_bad_triads() -> List[Triad]:
    data = _load_json(ART / "firewall_bad_triads_mapping.json")
    bad = data.get("bad_triangles_Schlafli_e6id", [])
    if not (isinstance(bad, list) and len(bad) == 9):
        raise ValueError("unexpected bad-triad payload")
    return [_norm_triad(t) for t in bad]


def _heisenberg_vec_maps(model: Mapping[str, Any]) -> Tuple[Dict[int, U3], Dict[U3, int]]:
    raw = model.get("e6id_to_heisenberg", {})
    if not isinstance(raw, dict) or len(raw) != 27:
        raise ValueError("missing/invalid e6id_to_heisenberg mapping")
    e6id_to_vec: Dict[int, U3] = {}
    vec_to_e6id: Dict[U3, int] = {}
    for k, payload in raw.items():
        if not isinstance(payload, dict):
            raise ValueError("unexpected heisenberg entry")
        u = payload.get("u")
        z = payload.get("z")
        if not (isinstance(u, list) and len(u) == 2):
            raise ValueError("unexpected heisenberg u")
        vec = (_mod3(int(u[0])), _mod3(int(u[1])), _mod3(int(z)))
        e6id = int(k)
        e6id_to_vec[e6id] = vec
        vec_to_e6id[vec] = e6id
    if len(e6id_to_vec) != 27 or len(vec_to_e6id) != 27:
        raise ValueError("expected 27-point inverse map")
    return e6id_to_vec, vec_to_e6id


def _extract_fiber_triads(model: Mapping[str, Any]) -> List[Triad]:
    fiber = model.get("fiber_triads_e6id", [])
    if not (isinstance(fiber, list) and len(fiber) == 9):
        raise ValueError("unexpected fiber triad list")
    return sorted({_norm_triad(t) for t in fiber})


def _extract_affine_triads(model: Mapping[str, Any]) -> List[Triad]:
    lines = model.get("affine_u_lines", [])
    if not (isinstance(lines, list) and len(lines) == 12):
        raise ValueError("unexpected affine_u_lines payload")
    triads: set[Triad] = set()
    for entry in lines:
        if not isinstance(entry, dict):
            raise ValueError("unexpected affine_u_lines entry")
        for tri in entry.get("triads", []):
            triads.add(_norm_triad(tri))
    if len(triads) != 36:
        raise ValueError(f"expected 36 affine triads, got {len(triads)}")
    return sorted(triads)


def _extract_u_lines(model: Mapping[str, Any]) -> List[Tuple[U2, U2, U2]]:
    lines = model.get("affine_u_lines", [])
    if not (isinstance(lines, list) and len(lines) == 12):
        raise ValueError("unexpected affine_u_lines payload")
    u_lines: list[Tuple[U2, U2, U2]] = []
    for entry in lines:
        if not isinstance(entry, dict):
            raise ValueError("unexpected affine_u_lines entry")
        u_line = entry.get("u_line", [])
        if not (isinstance(u_line, list) and len(u_line) == 3):
            raise ValueError("unexpected u_line payload")
        pts = tuple((int(p[0]) % 3, int(p[1]) % 3) for p in u_line)
        if len(set(pts)) != 3:
            raise ValueError("u_line is not 3 distinct points")
        u_lines.append(tuple(sorted(pts)))  # canonicalize as set-like tuple
    if len(set(u_lines)) != 12:
        raise ValueError("expected 12 distinct u-lines")
    return sorted(set(u_lines))

def _all_ag23_lines() -> List[Tuple[U2, U2, U2]]:
    """All 12 affine lines in AG(2,3) on U=F3^2 (as 3-point subsets)."""
    U = [(i, j) for i in range(3) for j in range(3)]
    # 4 direction classes in F3^2 / {±1}
    dirs = sorted({_dir_canonical((a, b)) for a in range(3) for b in range(3) if not (a == 0 and b == 0)})
    if len(dirs) != 4:
        raise ValueError("expected 4 direction classes in AG(2,3)")

    lines: set[Tuple[U2, U2, U2]] = set()
    for u0 in U:
        for d in dirs:
            pts = tuple(sorted({_u_add(u0, _u_scale(d, t)) for t in (0, 1, 2)}))
            if len(pts) != 3:
                raise ValueError("unexpected line size")
            lines.add(pts)  # duplicates collapse

    if len(lines) != 12:
        raise ValueError(f"expected 12 AG(2,3) lines, got {len(lines)}")
    return sorted(lines)


def _u_line_direction(u_line: Tuple[U2, U2, U2]) -> U2:
    """Return the direction class of a 3-point affine line in AG(2,3)."""
    pts = list(u_line)
    diffs: set[U2] = set()
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            d = _u_sub(pts[j], pts[i])
            if d != (0, 0):
                diffs.add(_dir_canonical(d))
    # A 3-point line should have exactly one direction class.
    if len(diffs) != 1:
        raise ValueError(f"unexpected u-line diffs: {u_line} -> {sorted(diffs)}")
    return next(iter(diffs))


def _apply_matrix(A: Mat2, u: U2) -> U2:
    return (
        _mod3(A[0][0] * u[0] + A[0][1] * u[1]),
        _mod3(A[1][0] * u[0] + A[1][1] * u[1]),
    )


def _perm_compose(p: Perm, q: Perm) -> Perm:
    """Permutation composition p∘q (apply q then p)."""
    return tuple(p[i] for i in q)


def _perm_translation(
    e6id_to_vec: Mapping[int, U3], vec_to_e6id: Mapping[U3, int], a: U2, c: int
) -> Perm:
    """Heisenberg translation (u,z) ↦ (u+a, z+c+psi(a,u))."""
    a = (_mod3(a[0]), _mod3(a[1]))
    c = _mod3(int(c))
    out: list[int] = []
    for i in range(27):
        u1, u2, z = e6id_to_vec[i]
        u = (u1, u2)
        u_new = _u_add(u, a)
        z_new = _mod3(z + c + _psi(a, u))
        out.append(int(vec_to_e6id[(u_new[0], u_new[1], z_new)]))
    return tuple(out)


def _perm_symplectic(
    e6id_to_vec: Mapping[int, U3], vec_to_e6id: Mapping[U3, int], A: Mat2
) -> Perm:
    """Linear Sp(2,3)=SL(2,3) action on u-plane; z unchanged."""
    out: list[int] = []
    for i in range(27):
        u1, u2, z = e6id_to_vec[i]
        u_new = _apply_matrix(A, (u1, u2))
        out.append(int(vec_to_e6id[(u_new[0], u_new[1], z)]))
    return tuple(out)


def analyze_hessian_heisenberg_group(
    triads: Iterable[Triad], e6id_to_vec: Mapping[int, U3], vec_to_e6id: Mapping[U3, int]
) -> Dict[str, Any]:
    """Enumerate Heisenberg⋊SL(2,3) on H27 and verify triad invariance."""
    triad_set = {tuple(sorted(map(int, t))) for t in triads}
    if len(triad_set) != 45:
        raise ValueError("expected 45 triads for group invariance check")

    # Generators: Heisenberg translations (two u-shifts + central z-shift) and SL(2,3) (S,T).
    gen_T10 = _perm_translation(e6id_to_vec, vec_to_e6id, (1, 0), 0)
    gen_T01 = _perm_translation(e6id_to_vec, vec_to_e6id, (0, 1), 0)
    gen_Z = _perm_translation(e6id_to_vec, vec_to_e6id, (0, 0), 1)

    # Standard generators of SL(2,3): S=[[0,-1],[1,0]], T=[[1,1],[0,1]] with -1=2 mod 3.
    S: Mat2 = ((0, 2), (1, 0))
    T: Mat2 = ((1, 1), (0, 1))
    gen_S = _perm_symplectic(e6id_to_vec, vec_to_e6id, S)
    gen_T = _perm_symplectic(e6id_to_vec, vec_to_e6id, T)

    gens = [gen_T10, gen_T01, gen_Z, gen_S, gen_T]
    identity: Perm = tuple(range(27))

    # BFS closure (|G| is expected to be 27*24 = 648).
    from collections import deque

    seen: set[Perm] = {identity}
    q: deque[Perm] = deque([identity])
    while q:
        g = q.popleft()
        for h in gens:
            gh = _perm_compose(h, g)
            if gh not in seen:
                seen.add(gh)
                q.append(gh)

    group = seen
    order = len(group)

    # Orbit size (transitivity) from point 0.
    orbit0 = {g[0] for g in group}

    def _triad_image(p: Perm, tri: Triad) -> Triad:
        a, b, c = tri
        return tuple(sorted((p[a], p[b], p[c])))  # type: ignore[return-value]

    triads_invariant = True
    for g in group:
        for tri in triad_set:
            if _triad_image(g, tri) not in triad_set:
                triads_invariant = False
                break
        if not triads_invariant:
            break

    return {
        "order": order,
        "orbit_size": len(orbit0),
        "transitive": len(orbit0) == 27,
        "triads_invariant": triads_invariant,
    }


def analyze_hessian_tritangent_split() -> Dict[str, Any]:
    model = load_heisenberg_model()
    e6id_to_vec, vec_to_e6id = _heisenberg_vec_maps(model)

    fiber_triads = _extract_fiber_triads(model)
    affine_triads = _extract_affine_triads(model)
    all_triads = sorted(set(fiber_triads) | set(affine_triads))
    if len(all_triads) != 45:
        raise ValueError(f"expected 45 total triads, got {len(all_triads)}")
    if set(fiber_triads) & set(affine_triads):
        raise ValueError("fiber/affine triad sets should be disjoint")

    # Cross-check against the firewall's forbidden 9.
    bad = load_firewall_bad_triads()
    if sorted(bad) != sorted(fiber_triads):
        raise ValueError("firewall bad triads do not match fiber triads")

    # The u-plane is canonically AG(2,3). We compute its 12 lines directly,
    # and only use the artifact's u-lines as a cross-check.
    u_lines = _all_ag23_lines()
    u_lines_art = _extract_u_lines(model)
    if set(u_lines) != set(u_lines_art):
        raise ValueError("artifact u-lines do not match AG(2,3) enumeration")
    dirs: dict[U2, list[Tuple[U2, U2, U2]]] = defaultdict(list)
    for L in u_lines:
        dirs[_u_line_direction(L)].append(L)
    dirs = {k: sorted(v) for k, v in dirs.items()}

    # In AG(2,3) there are 4 direction classes, each with 3 parallel lines.
    direction_sizes = {k: len(v) for k, v in dirs.items()}

    # u-point incidence: each point lies on 4 lines, and each pair determines a line.
    u_points: list[U2] = sorted({p for L in u_lines for p in L})
    if len(u_points) != 9:
        raise ValueError("expected 9 u-points in AG(2,3)")
    through: Counter[U2] = Counter()
    for L in u_lines:
        through.update(L)
    pair_to_count: Counter[Tuple[U2, U2]] = Counter()
    for L in u_lines:
        a, b, c = L
        for x, y in ((a, b), (a, c), (b, c)):
            pair_to_count[tuple(sorted((x, y)))] += 1

    # Fiber triads are constant-u and sweep all z.
    fiber_u: dict[Triad, U2] = {}
    for tri in fiber_triads:
        vecs = [e6id_to_vec[i] for i in tri]
        u_set = {(v[0], v[1]) for v in vecs}
        z_set = {v[2] for v in vecs}
        if len(u_set) != 1 or z_set != {0, 1, 2}:
            raise ValueError(f"fiber triad not (u fixed, z all): {tri} -> {vecs}")
        fiber_u[tri] = next(iter(u_set))

    # Affine triads are the 36 non-fiber tritangent planes. In the Heisenberg
    # model they are exactly the "3 lifts" of each affine u-line in AG(2,3):
    # each triad picks one point from each of the three u-fibers.
    affine_meta: dict[Triad, Dict[str, Any]] = {}
    u_line_sets = {frozenset(L) for L in u_lines}
    for tri in affine_triads:
        vecs = [e6id_to_vec[i] for i in tri]
        u_set = {(v[0], v[1]) for v in vecs}
        if len(u_set) != 3:
            raise ValueError(f"affine triad does not hit 3 distinct u fibers: {tri} -> {vecs}")
        if frozenset(u_set) not in u_line_sets:
            raise ValueError(f"affine triad u-set not a u-line: {tri} -> {sorted(u_set)}")
        affine_meta[tri] = {"u_line": sorted(u_set), "vecs": vecs}

    # Stronger per-line check: each u-line entry carries 3 triads partitioning
    # the 9 points of the three fibers over that line.
    raw_lines = model.get("affine_u_lines", [])
    for entry in raw_lines:
        u_line = tuple(sorted((int(p[0]) % 3, int(p[1]) % 3) for p in entry["u_line"]))
        u_line_set = frozenset(u_line)
        expected_points = {
            vec_to_e6id[(u[0], u[1], z)] for u in u_line for z in (0, 1, 2)
        }
        triads = [_norm_triad(t) for t in entry["triads"]]
        if len(triads) != 3:
            raise ValueError("expected 3 triads per u-line")
        union_points: set[int] = set()
        for tri in triads:
            vecs = [e6id_to_vec[i] for i in tri]
            tri_u = {(v[0], v[1]) for v in vecs}
            if frozenset(tri_u) != u_line_set:
                raise ValueError(f"triad does not project to u-line: {tri} -> {sorted(tri_u)}")
            union_points.update(tri)
        if union_points != expected_points:
            raise ValueError("u-line triads do not partition the 3 fibers")

    # ---------------------------------------------------------------------
    # Canonical reconstruction (no triad lookup):
    # For each u-line L={u0+t d}, define its omega-offset c = omega(u0,d).
    # Then the three affine triads over L are the graphs z = b - c*t.
    # ---------------------------------------------------------------------
    recon_fiber: set[Triad] = set()
    U_pts = [(i, j) for i in range(3) for j in range(3)]
    for u in U_pts:
        tri = tuple(sorted(vec_to_e6id[(u[0], u[1], z)] for z in (0, 1, 2)))
        recon_fiber.add(tri)
    if len(recon_fiber) != 9:
        raise ValueError("expected 9 reconstructed fiber triads")

    recon_affine: set[Triad] = set()
    for L in u_lines:
        u0 = min(L)
        # pick a direction from the line itself (canonical up to ±1)
        other = next(p for p in L if p != u0)
        d = _dir_canonical(_u_sub(other, u0))
        c = int(_omega_u(u0, d)) % 3
        a = (-c) % 3  # z-slope on the lift
        for b in (0, 1, 2):
            tri_pts = []
            for t in (0, 1, 2):
                u = _u_add(u0, _u_scale(d, t))
                z = (b + a * t) % 3
                tri_pts.append(int(vec_to_e6id[(u[0], u[1], z)]))
            recon_affine.add(tuple(sorted(tri_pts)))
    if len(recon_affine) != 36:
        raise ValueError(f"expected 36 reconstructed affine triads, got {len(recon_affine)}")

    if recon_fiber != set(fiber_triads):
        raise ValueError("reconstructed fiber triads mismatch artifact")
    if recon_affine != set(affine_triads):
        raise ValueError("reconstructed affine triads mismatch artifact")

    hessian_group = analyze_hessian_heisenberg_group(all_triads, e6id_to_vec, vec_to_e6id)

    return {
        "counts": {
            "points_total": 27,
            "triads_total": 45,
            "fiber_triads": len(fiber_triads),
            "affine_triads": len(affine_triads),
            "u_points": len(u_points),
            "u_lines": len(u_lines),
            "u_line_directions": len(dirs),
        },
        "reconstruction": {
            "fiber_matches": True,
            "affine_matches": True,
        },
        "hessian_group": hessian_group,
        "ag23_checks": {
            "direction_sizes": direction_sizes,
            "u_point_line_degrees": dict(sorted(through.items())),
            "pair_line_counts": Counter(pair_to_count).most_common(3),
            "pairs_total": len(pair_to_count),
        },
        "fiber_triads": [list(t) for t in fiber_triads],
        "affine_triads": [list(t) for t in affine_triads],
        "u_lines": [[list(p) for p in L] for L in u_lines],
        "u_line_directions": {str(k): [[[a, b], [c, d], [e, f]] for ((a, b), (c, d), (e, f)) in v] for k, v in dirs.items()},
        "fiber_u": {str(list(k)): list(v) for k, v in fiber_u.items()},
        "affine_meta_sample": {str(list(k)): affine_meta[k] for k in sorted(list(affine_meta))[:5]},
        "heisenberg_maps": {
            "e6id_to_vec": {str(k): list(v) for k, v in sorted(e6id_to_vec.items())},
            "vec_to_e6id": {str(list(k)): v for k, v in sorted(vec_to_e6id.items())},
        },
    }


def main() -> None:
    print("=" * 72)
    print("E6 TRITANGENTS: HESSIAN/HEISENBERG 36+9 DECOMPOSITION")
    print("=" * 72)
    res = analyze_hessian_tritangent_split()

    c = res["counts"]
    print("\nCounts")
    print("-" * 30)
    for k in [
        "points_total",
        "triads_total",
        "fiber_triads",
        "affine_triads",
        "u_points",
        "u_lines",
        "u_line_directions",
    ]:
        print(f"  {k:>18}: {c[k]}")

    ag = res["ag23_checks"]
    print("\nAG(2,3) checks (u-plane)")
    print("-" * 30)
    print("  direction sizes:", ag["direction_sizes"])
    print("  u degrees (should all be 4):", sorted(set(ag["u_point_line_degrees"].values())))
    print("  #pairs covered (should be 36):", ag["pairs_total"])

    # Internal asserts (keep these lightweight and structural).
    assert c["triads_total"] == 45
    assert c["fiber_triads"] == 9
    assert c["affine_triads"] == 36
    assert c["u_points"] == 9
    assert c["u_lines"] == 12
    assert c["u_line_directions"] == 4
    assert set(ag["direction_sizes"].values()) == {3}
    assert sorted(set(ag["u_point_line_degrees"].values())) == [4]
    assert ag["pairs_total"] == 36

    hg = res["hessian_group"]
    print("\nHeisenberg⋊SL(2,3) symmetry on H27")
    print("-" * 30)
    print("  order:", hg["order"])
    print("  orbit size:", hg["orbit_size"])
    print("  triads invariant:", hg["triads_invariant"])

    assert hg["order"] == 648
    assert hg["transitive"] is True
    assert hg["triads_invariant"] is True

    print("\nALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()
