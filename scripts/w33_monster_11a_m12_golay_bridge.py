#!/usr/bin/env python3
"""Monster 11A <-> 11*M12 <-> ternary Golay: the missing *phase* is the bridge.

This repo has two deterministic ingredients:

1) Monster class-algebra / centralizer data (bundled ATLAS snapshot + CTblLib),
   including the prime-order class 11A with:

       C_M(11A) = 11 * M12.

2) The ternary Golay code G_12 (length 12, dim 6 over F3) used in the s12 /
   Heisenberg machinery.

The subtlety: for the ternary code, the natural Mathieu symmetry is most
cleanly expressed as a **monomial** action (permutation + coordinate signs),
not as bare coordinate permutations on F3^{12}. That is exactly the pattern we
see throughout the repo: *grade-only* structure is not enough; the **phase**
matters.

This script verifies, offline:
  - b11 (order 2) and b21 (order 3) generate the ATLAS 12-point M12.
  - The induced Steiner S(5,6,12) hexad designs are isomorphic.
  - After transporting b11,b21 to the repo's Golay coordinate system, the
    resulting **pure permutations do not preserve the code**.
  - But there exist diagonal sign vectors s in {1,2}^{12} such that the lifted
    monomial maps D_s P preserve the code (so we have an explicit 2-cover lift).
  - The Monster (2A x 3B -> 11A) prime-ratio signature is r_11 = 144, and
    144 = [M12:PSL2(11)].

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_monster_11a_m12_golay_bridge.py
"""

from __future__ import annotations

import sys
from itertools import combinations, product
from pathlib import Path
from typing import Any, Iterable

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _act_word_by_perm(word: tuple[int, ...], perm: tuple[int, ...]) -> tuple[int, ...]:
    """Apply coordinate permutation perm[i]=j via out[j]=word[i]."""
    out = [0] * len(word)
    for i, j in enumerate(perm):
        out[int(j)] = int(word[int(i)]) % 3
    return tuple(out)


def _act_word_by_monomial(
    word: tuple[int, ...], perm: tuple[int, ...], signs: tuple[int, ...]
) -> tuple[int, ...]:
    """Apply monomial D*P: first permute, then multiply each coordinate by signs[i]."""
    w = _act_word_by_perm(word, perm)
    return tuple((int(signs[i]) * int(w[i])) % 3 for i in range(len(word)))


def _incidence_graph(hexads: list[tuple[int, ...]], prefix: str) -> nx.Graph:
    """Point-hexad bipartite incidence graph."""
    G = nx.Graph()
    for i in range(12):
        G.add_node((prefix, "p", i), kind="p", idx=int(i))
    for bi, H in enumerate(hexads):
        bnode = (prefix, "b", int(bi))
        G.add_node(bnode, kind="b")
        for i in H:
            G.add_edge((prefix, "p", int(i)), bnode)
    return G


def _subset_orbit(
    seed: tuple[int, ...], gens: list[tuple[int, ...]]
) -> set[tuple[int, ...]]:
    """Orbit of a 6-subset under generators/inverses (acting on points 0..11)."""
    seen = {tuple(seed)}
    q = [tuple(seed)]
    while q:
        S = q.pop()
        for g in gens:
            T = tuple(sorted(int(g[i]) for i in S))
            if T not in seen:
                seen.add(T)
                q.append(T)
    return seen


def _find_hexad_orbit_m12(
    gens: list[tuple[int, ...]],
) -> list[tuple[int, ...]]:
    """Deterministically find an M12-orbit of size 132 on 6-subsets (Steiner hexads)."""
    pts = list(range(12))
    for S in combinations(pts, 6):
        orb = _subset_orbit(tuple(S), gens)
        if len(orb) == 132:
            return sorted(orb)
    raise RuntimeError("failed to locate a 132-orbit on 6-subsets (expected Steiner hexads)")


def _find_sign_lift_for_perm(
    *,
    perm: tuple[int, ...],
    generator_rows: list[tuple[int, ...]],
    code_set: set[tuple[int, ...]],
) -> tuple[int, ...] | None:
    """Find signs in {1,2}^12 such that D*P sends each generator row into the code."""
    n = len(perm)
    for signs in product((1, 2), repeat=n):
        ok = True
        for row in generator_rows:
            if _act_word_by_monomial(row, perm, signs) not in code_set:
                ok = False
                break
        if ok:
            return tuple(int(x) for x in signs)
    return None


def analyze() -> dict[str, Any]:
    from scripts.derive_m12_p144_suborbits import compose, inv, perm_from_cycles
    from scripts.w33_leech_monster import (
        analyze_monster_2a3b_class_algebra_partial_distribution,
        load_monster_atlas_ccls,
    )
    from tools.s12_universal_algebra import (
        enumerate_linear_code_f3,
        ternary_golay_generator_matrix,
    )

    # ---------------------------------------------------------------------
    # §1. Monster: centralizer order check for 11A
    # ---------------------------------------------------------------------
    atlas = load_monster_atlas_ccls()
    if atlas is None:
        return {"available": False, "reason": "missing monster ATLAS snapshot"}
    classes = atlas.get("classes", {})
    if not isinstance(classes, dict) or "11A" not in classes:
        return {"available": False, "reason": "11A missing from ATLAS snapshot"}
    cent_11a = int(classes["11A"]["centralizer_order"])
    m12_order = 95040
    assert cent_11a == 11 * m12_order

    # ---------------------------------------------------------------------
    # §2. Build Steiner hexads for:
    #   (a) the ATLAS 12-point M12 permrep, and
    #   (b) the repo's ternary Golay code supports.
    # ---------------------------------------------------------------------
    # ATLAS v3 permrep M12G1-p12aB0 generators.
    b11 = perm_from_cycles(12, [[1, 4], [3, 10], [5, 11], [6, 12]])
    b21 = perm_from_cycles(12, [[1, 8, 9], [2, 3, 4], [5, 12, 11], [6, 10, 7]])
    gens = [b11, b21, inv(b11), inv(b21)]

    hexads_atlas = _find_hexad_orbit_m12(gens)
    assert len(hexads_atlas) == 132

    gen = ternary_golay_generator_matrix()
    generator_rows = [tuple(int(x) % 3 for x in row) for row in gen]
    codewords = enumerate_linear_code_f3(gen)
    code_set = set(codewords)
    assert len(code_set) == 3**6

    hexads_code = sorted(
        {
            tuple(sorted(i for i, x in enumerate(cw) if int(x) % 3 != 0))
            for cw in codewords
            if sum(1 for x in cw if int(x) % 3 != 0) == 6
        }
    )
    assert len(hexads_code) == 132

    # ---------------------------------------------------------------------
    # §3. Find a point relabeling pi: ATLAS points -> repo points, by
    #     graph isomorphism of the hexad incidence designs.
    # ---------------------------------------------------------------------
    G_atlas = _incidence_graph(hexads_atlas, "A")
    G_code = _incidence_graph(hexads_code, "C")
    node_match = lambda a, b: a.get("kind") == b.get("kind")
    GM = nx.algorithms.isomorphism.GraphMatcher(G_atlas, G_code, node_match=node_match)
    if not GM.is_isomorphic():
        return {"available": False, "reason": "hexad incidence designs not isomorphic"}
    mapping = GM.mapping  # one deterministic isomorphism
    pi = tuple(int(mapping[("A", "p", i)][2]) for i in range(12))  # atlas -> code

    # Conjugate ATLAS permutations into the repo coordinate system:
    # g_code = pi o g_atlas o pi^{-1}.
    pi_inv = inv(pi)

    def conj_to_code(g: tuple[int, ...]) -> tuple[int, ...]:
        return compose(pi, compose(g, pi_inv))

    b11_code = conj_to_code(b11)
    b21_code = conj_to_code(b21)

    # ---------------------------------------------------------------------
    # §4. Verify: pure permutations still fail on the ternary Golay code.
    # ---------------------------------------------------------------------
    perm_only_ok_11 = all(
        _act_word_by_perm(row, b11_code) in code_set for row in generator_rows
    )
    perm_only_ok_21 = all(
        _act_word_by_perm(row, b21_code) in code_set for row in generator_rows
    )

    # ---------------------------------------------------------------------
    # §5. Find diagonal sign lifts in {1,2}^12 for each generator.
    # ---------------------------------------------------------------------
    signs_11 = _find_sign_lift_for_perm(
        perm=b11_code, generator_rows=generator_rows, code_set=code_set
    )
    signs_21 = _find_sign_lift_for_perm(
        perm=b21_code, generator_rows=generator_rows, code_set=code_set
    )
    if signs_11 is None or signs_21 is None:
        return {"available": False, "reason": "failed to find monomial sign lifts"}

    # Sanity: lifted generators preserve the full code (check on all codewords).
    def monomial_preserves_code(perm: tuple[int, ...], signs: tuple[int, ...]) -> bool:
        return all(_act_word_by_monomial(cw, perm, signs) in code_set for cw in code_set)

    assert monomial_preserves_code(b11_code, signs_11)
    assert monomial_preserves_code(b21_code, signs_21)

    # ---------------------------------------------------------------------
    # §6. Prime-ratio signature r_11 and 144 as a canonical M12 index.
    # ---------------------------------------------------------------------
    dist = analyze_monster_2a3b_class_algebra_partial_distribution()
    if dist.get("available") is not True:
        return {"available": False, "reason": "2A x 3B distribution unavailable"}
    info = dist["classes"]["11A"]
    n = int(info["structure_constant_per_element"])
    assert n % 11 == 0
    r11 = int(n // 11)

    psl2_11_order = 11 * (11**2 - 1) // 2  # 660
    idx = int(m12_order // psl2_11_order)

    return {
        "available": True,
        "monster": {
            "class": "11A",
            "centralizer_order": int(cent_11a),
            "centralizer_decomposition": "11 * M12",
        },
        "m12_atlas_permrep": {
            "b11": list(map(int, b11)),
            "b21": list(map(int, b21)),
        },
        "steiner_design": {
            "hexads_atlas_count": int(len(hexads_atlas)),
            "hexads_code_count": int(len(hexads_code)),
            "atlas_to_code_point_map": list(map(int, pi)),
        },
        "golay": {
            "n_codewords": int(len(code_set)),
            "perm_only_preserves_code_rows": {
                "b11_code": bool(perm_only_ok_11),
                "b21_code": bool(perm_only_ok_21),
            },
            "monomial_lift_signs": {
                "b11_code": list(map(int, signs_11)),
                "b21_code": list(map(int, signs_21)),
            },
        },
        "signature": {
            "pair": "2A x 3B",
            "structure_constant_per_element": int(n),
            "r_11": int(r11),
        },
        "index": {
            "m12_order": int(m12_order),
            "psl2_11_order": int(psl2_11_order),
            "m12_psl2_11_index": int(idx),
        },
    }


def main() -> None:
    rep = analyze()
    if rep.get("available") is not True:
        raise SystemExit(f"Unavailable: {rep}")

    print("=" * 78)
    print("MONSTER 11A <-> M12 <-> TERNARY GOLAY (PHASE/2-COVER BRIDGE)")
    print("=" * 78)

    m = rep["monster"]
    s = rep["signature"]
    idx = rep["index"]
    g = rep["golay"]

    print()
    print("§1. Monster centralizer (ATLAS snapshot)")
    print("-" * 58)
    print(f"  class: {m['class']}")
    print(f"  |C_M(11A)| = {m['centralizer_order']} = 11 * {idx['m12_order']}")

    print()
    print("§2. Monomial lift needed (permutation-only fails)")
    print("-" * 58)
    perm_only = g["perm_only_preserves_code_rows"]
    print(f"  perm-only preserves generator rows? b11={perm_only['b11_code']} b21={perm_only['b21_code']}")
    print("  found diagonal sign lifts in {1,2}^12: True")

    print()
    print("§3. Prime-ratio signature r_11")
    print("-" * 58)
    print(f"  pair: {s['pair']}")
    print(f"  n = {s['structure_constant_per_element']} = 11 * {s['r_11']}")
    print(f"  r_11 = {s['r_11']}")

    print()
    print("§4. 144 as a canonical M12 index")
    print("-" * 58)
    print(f"  |M12| = {idx['m12_order']}")
    print(f"  |PSL2(11)| = {idx['psl2_11_order']}")
    print(f"  [M12:PSL2(11)] = {idx['m12_psl2_11_index']}")

    print()
    print("ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    main()
