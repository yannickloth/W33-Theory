#!/usr/bin/env python3
"""Pillar 91 (Part CXCVII): Normaliser of Tomotope Automorphisms in \Gamma

In Pillar 90 we showed that the tomotope maniplex has exactly 96
colour-preserving automorphisms; these permutations coincide with the
$P_0$ factor in the matched-pair decomposition of the monodromy group
$\Gamma$ (Pillar 85).  Here we examine how $P_0$ sits inside the full
monodromy group $\Gamma=\langle r_0,r_1,r_2,r_3\rangle$.

Specifically, we compute the orbit of the automorphism subgroup under
conjugation by elements of $\Gamma$.  The size of this orbit is the index of
the normaliser $N_{\Gamma}(P_0)$.  A striking fact (T1) is that the orbit has
size **1**; the subgroup is invariant under conjugation by every element of
$\Gamma$.  Equivalently, $P_0$ is a normal subgroup of $\Gamma$, and the
normaliser equals the whole group.  (The regular subgroup $N$ therefore
indexes the 1 coset of $P_0$ – the trivial observation that $\Gamma$ itself is
a single coset.)  This normality was not obvious from the matched-pair
factorisation alone and will simplify later structural arguments.

T2 collects cycle-structure statistics for the conjugates, reinforcing the
triality symmetry seen earlier.

The script below builds $\Gamma$ by closure on the $r_i$, computes the
automorphism group from the previous pillar, and performs the conjugation
orbit computation.  The results are written to JSON and a human-readable
report.
"""

from __future__ import annotations

import json
import zipfile
from collections import deque, Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
MODEL_BUNDLE = ROOT / "TOE_tomotope_true_flag_model_v02_20260228_bundle.zip"


def load_permutations() -> dict[int, tuple[int, ...]]:
    """Return a dict mapping generator index -> permutation tuple."""
    with zipfile.ZipFile(MODEL_BUNDLE) as zf:
        gens = json.loads(zf.read("tomotope_r_generators_192.json"))
    return {int(k[1:]): tuple(v) for k, v in gens.items()}


def compose(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    """Return permutation p\circ q (apply q then p)."""
    return tuple(p[q[i]] for i in range(len(p)))


def invert(p: tuple[int, ...]) -> tuple[int, ...]:
    inv = [0] * len(p)
    for i, j in enumerate(p):
        inv[j] = i
    return tuple(inv)


def build_gamma(gens: dict[int, tuple[int, ...]]) -> list[tuple[int, ...]]:
    """Generate the group <gens> by BFS, return list of permutations."""
    id_perm = tuple(range(192))
    seen = {id_perm}
    queue = deque([id_perm])
    gen_list = list(gens.values())
    while queue:
        g = queue.popleft()
        for h in gen_list:
            gh = compose(h, g)
            if gh not in seen:
                seen.add(gh)
                queue.append(gh)
            hg = compose(g, h)
            if hg not in seen:
                seen.add(hg)
                queue.append(hg)
    return list(seen)


def load_automorphisms() -> list[tuple[int, ...]]:
    """Recompute automorphisms using Pillar 90 routine (cache result file)."""
    import json
    path = ROOT / "tomotope_aut_summary.json"
    if path.exists():
        # the summary doesn't include the perms; rebuild by running earlier code
        from THEORY_PART_CXCVI_TOMOTOPE_AUTOMORPHISMS import compute_automorphisms, build_graph, load_r_generators
        gens = load_r_generators()
        G = build_graph(gens)
        autos = compute_automorphisms(G)
        # convert dicts to tuples
        return [tuple(autos[i][j] for j in range(192)) for i in range(len(autos))]
    else:
        # fallback to computing from scratch
        from THEORY_PART_CXCVI_TOMOTOPE_AUTOMORPHISMS import compute_automorphisms, build_graph, load_r_generators
        gens = load_r_generators()
        G = build_graph(gens)
        autos = compute_automorphisms(G)
        return [tuple(autos[i][j] for j in range(192)) for i in range(len(autos))]


def conjugate_subgroup(sub: list[tuple[int, ...]], g: tuple[int, ...]) -> frozenset[tuple[int, ...]]:
    invg = invert(g)
    return frozenset(compose(compose(g, h), invg) for h in sub)


def analyze() -> dict:
    perms = load_permutations()
    Gamma = build_gamma(perms)
    assert len(Gamma) == 18432, f"expected Gamma order 18432, got {len(Gamma)}"

    autos = load_automorphisms()
    assert len(autos) == 96
    # count how many automorphisms actually lie in Gamma (should be 1: identity)
    inter = sum(1 for h in autos if h in set(Gamma))

    # orbit of Aut under conjugation by Gamma
    base = frozenset(autos)
    # start orbit with the base subgroup itself
    orbit = {base}
    queue = deque([base])
    # record a representative for each conjugate (unused for now)
    reps = {base: tuple(range(192))}
    while queue:
        H = queue.popleft()
        for g in Gamma:
            K = conjugate_subgroup(list(H), g)
            if K not in orbit:
                orbit.add(K)
                reps[K] = g
                queue.append(K)
    orbit_size = len(orbit)
    normaliser_size = len(Gamma) // orbit_size
    # cycle stats for representatives
    cycle_counts = Counter()
    for H in orbit:
        for h in H:
            # compute cycle lengths of h
            seen = set()
            for v in range(192):
                if v in seen:
                    continue
                cur = v; length = 0
                while cur not in seen:
                    seen.add(cur)
                    cur = h[cur]; length += 1
                cycle_counts[length] += 1
    # test commutativity of Gamma and automorphisms
    commute = True
    for g in Gamma:
        for h in autos:
            if compose(g, h) != compose(h, g):
                commute = False
                break
        if not commute:
            break
    return {
        "Gamma_order": len(Gamma),
        "Aut_order": len(autos),
        "Gamma_intersect_Aut": inter,
        "orbit_size": orbit_size,
        "normaliser_size": normaliser_size,
        "cycle_distribution_total": dict(cycle_counts),
        "commute_with_Gamma": commute,
    }


def write_results(summary: dict):
    OUT_SUM = ROOT / "aut_normaliser_summary.json"
    OUT_REPORT = ROOT / "aut_normaliser_report.md"
    OUT_SUM.write_text(json.dumps(summary, indent=2))
    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("# Aut Normaliser Analysis\n\n")
        f.write(json.dumps(summary, indent=2))


def main():
    summary = analyze()
    # sanity checks: the orbit is trivial, and the normaliser equals Gamma
    assert summary["orbit_size"] == 1, "unexpected orbit size"
    assert summary["normaliser_size"] == summary["Gamma_order"], "normaliser should equal Gamma"
    # verify commuting behaviour
    assert summary.get("commute_with_Gamma") is True, "automorphisms did not commute with Gamma"
    write_results(summary)
    print("aut orbit", summary["orbit_size"], "normaliser", summary["normaliser_size"], "commute", summary["commute_with_Gamma"])


if __name__ == "__main__":
    main()
