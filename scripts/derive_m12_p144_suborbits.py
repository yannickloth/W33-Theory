#!/usr/bin/env python3
"""Derive M12 degree-144 coset-action suborbit structure (PSL2(11) stabilizer).

This repo stores some sporadic permutation-degree metadata (rank + suborbits) in
`data/*_permutation_degrees.json` for offline verification of the Monster r_p
"prime ratio signature" pipeline.

For M12, the primitive coset action on a maximal subgroup PSL2(11) has index 144.
To keep tests and analyses offline, we compute the suborbit lengths
deterministically from the standard 12-point generators (ATLAS v3 permrep
`M12G1-p12aB0`):

  b11 := (1,4)(3,10)(5,11)(6,12)
  b21 := (1,8,9)(2,3,4)(5,12,11)(6,10,7)

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\derive_m12_p144_suborbits.py
"""

from __future__ import annotations

import math
from collections import Counter, deque
from dataclasses import dataclass
from typing import Iterable


def perm_from_cycles(n: int, cycles: list[list[int]]) -> tuple[int, ...]:
    perm = list(range(n))
    for cyc in cycles:
        if not cyc:
            continue
        z = [c - 1 for c in cyc]
        for a, b in zip(z, z[1:] + z[:1]):
            perm[a] = b
    return tuple(perm)


def compose(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    # Function composition: (p∘q)(i) = p(q(i)).
    return tuple(p[i] for i in q)


def inv(p: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * len(p)
    for i, j in enumerate(p):
        out[j] = i
    return tuple(out)


def order(p: tuple[int, ...]) -> int:
    n = len(p)
    seen = [False] * n
    lcm = 1
    for i in range(n):
        if seen[i]:
            continue
        j = i
        cyc_len = 0
        while not seen[j]:
            seen[j] = True
            j = p[j]
            cyc_len += 1
        if cyc_len:
            lcm = (lcm // math.gcd(lcm, cyc_len)) * cyc_len
    return int(lcm)


def generate_group(generators: Iterable[tuple[int, ...]]) -> list[tuple[int, ...]]:
    gens = list(generators)
    if not gens:
        raise ValueError("No generators")
    n = len(gens[0])
    ident = tuple(range(n))
    seen = {ident}
    q: deque[tuple[int, ...]] = deque([ident])
    while q:
        g = q.popleft()
        for s in gens:
            h = compose(g, s)
            if h not in seen:
                seen.add(h)
                q.append(h)
    return list(seen)


def generate_subgroup(
    a: tuple[int, ...],
    b: tuple[int, ...],
    *,
    size_limit: int | None = None,
) -> set[tuple[int, ...]]:
    n = len(a)
    ident = tuple(range(n))
    gens = [a, b, inv(a), inv(b)]
    seen: set[tuple[int, ...]] = {ident}
    q: deque[tuple[int, ...]] = deque([ident])
    while q:
        g = q.popleft()
        for s in gens:
            h = compose(g, s)
            if h not in seen:
                seen.add(h)
                if size_limit is not None and len(seen) > size_limit:
                    return seen
                q.append(h)
    return seen


@dataclass(frozen=True)
class FoundPSL2_11:
    a2: tuple[int, ...]
    b3: tuple[int, ...]
    subgroup: set[tuple[int, ...]]


def find_psl2_11_subgroup(g_elems: list[tuple[int, ...]]) -> FoundPSL2_11:
    """Deterministically find PSL2(11) ⊂ M12 via a (2,3,11) generating pair."""

    elems = sorted(g_elems)
    orders = {g: order(g) for g in elems}
    involutions = [g for g in elems if orders[g] == 2]
    order3 = [g for g in elems if orders[g] == 3]
    if not involutions or not order3:
        raise RuntimeError("Failed to find order-2/order-3 elements in M12")

    # Search in a bounded deterministic window first (usually succeeds fast).
    search_invol = involutions[:500]
    search_o3 = order3[:500]
    for a in search_invol:
        for b in search_o3:
            if orders[compose(a, b)] != 11:
                continue
            sub = generate_subgroup(a, b, size_limit=660)
            if len(sub) == 660:
                return FoundPSL2_11(a, b, sub)

    # Fallback: widen search (still deterministic).
    for a in involutions:
        for b in order3:
            if order(compose(a, b)) != 11:
                continue
            sub = generate_subgroup(a, b, size_limit=660)
            if len(sub) == 660:
                return FoundPSL2_11(a, b, sub)

    raise RuntimeError("Failed to locate PSL2(11) subgroup inside M12")


def cosets_right(
    g_elems: list[tuple[int, ...]], h_elems: set[tuple[int, ...]]
) -> tuple[list[tuple[int, ...]], dict[tuple[int, ...], int]]:
    elems = sorted(g_elems)
    h_sorted = sorted(h_elems)
    n = len(elems[0])
    ident = tuple(range(n))

    reps: list[tuple[int, ...]] = []
    coset_of: dict[tuple[int, ...], int] = {}

    def add_coset(rep: tuple[int, ...]) -> None:
        idx = len(reps)
        reps.append(rep)
        for h in h_sorted:
            coset_of[compose(h, rep)] = idx

    # Ensure coset 0 is H itself.
    add_coset(ident)
    for g in elems:
        if g in coset_of:
            continue
        add_coset(g)

    return reps, coset_of


def orbit_sizes_on_cosets(
    coset_reps: list[tuple[int, ...]],
    coset_of: dict[tuple[int, ...], int],
    gens: list[tuple[int, ...]],
) -> list[int]:
    n_cosets = len(coset_reps)
    visited = [False] * n_cosets
    sizes: list[int] = []
    for start in range(n_cosets):
        if visited[start]:
            continue
        q: deque[int] = deque([start])
        visited[start] = True
        size = 0
        while q:
            i = q.popleft()
            size += 1
            rep = coset_reps[i]
            for s in gens:
                j = coset_of[compose(rep, s)]
                if not visited[j]:
                    visited[j] = True
                    q.append(j)
        sizes.append(size)
    return sizes


def compress_suborbits(suborbits: list[int]) -> str:
    counts = Counter(int(x) for x in suborbits)
    parts: list[str] = []
    for k in sorted(counts.keys()):
        exp = int(counts[k])
        parts.append(f"{k}^{exp}" if exp > 1 else f"{k}")
    return ", ".join(parts)


def main() -> None:
    # ATLAS v3 M12G1-p12aB0 GAP generators.
    b11 = perm_from_cycles(12, [[1, 4], [3, 10], [5, 11], [6, 12]])
    b21 = perm_from_cycles(12, [[1, 8, 9], [2, 3, 4], [5, 12, 11], [6, 10, 7]])
    gens = [b11, b21, inv(b11), inv(b21)]

    g_elems = generate_group(gens)
    assert len(g_elems) == 95040, f"M12 order mismatch: {len(g_elems)}"

    found = find_psl2_11_subgroup(g_elems)
    h = found.subgroup
    assert len(h) == 660
    a = found.a2
    b = found.b3
    assert order(a) == 2
    assert order(b) == 3
    assert order(compose(a, b)) == 11

    # Normalizer order: check g^{-1} a g, g^{-1} b g ∈ H (generators suffice).
    h_set = set(h)
    norm = 0
    for g in g_elems:
        gi = inv(g)
        if compose(compose(gi, a), g) in h_set and compose(compose(gi, b), g) in h_set:
            norm += 1
    # Accept either self-normalizing PSL2(11) (660) or PGL2(11) normalizer (1320).
    if norm not in (660, 1320):
        raise AssertionError(f"Unexpected normalizer size for PSL2(11) in M12: {norm}")
    if norm == 660:
        print("Note: found PSL2(11) with self-normalizer (660) — proceeding.")
    else:
        print("Normalizer matches expected PGL2(11) (1320).")

    coset_reps, coset_of = cosets_right(g_elems, h)
    assert len(coset_reps) == 144
    assert len(coset_of) == 95040

    suborbits = sorted(
        orbit_sizes_on_cosets(coset_reps, coset_of, [a, b, inv(a), inv(b)])
    )
    assert sum(suborbits) == 144
    rank = len(suborbits)
    compressed = compress_suborbits(suborbits)

    print("=" * 78)
    print("M12 degree-144 coset action (stabilizer PSL2(11))")
    print("=" * 78)
    print(f"|M12| = {len(g_elems)}")
    print(f"|H|   = {len(h)}")
    print(f"[M12:H] = {len(coset_reps)}")
    print(f"|N_M12(H)| = {norm} (expected 1320 = PGL2(11))")
    print()
    print(f"rank = {rank}")
    print(f"suborbit_lengths_compressed = {compressed}")
    print(f"suborbit_lengths = {suborbits}")
    print()
    print("JSON snippet:")
    print('  "144": {')
    print(f'    "rank": {rank},')
    print(f'    "suborbit_lengths_compressed": "{compressed}",')
    print(f'    "suborbit_lengths": {suborbits},')
    print('    "stabilizer_order": 660,')
    print('    "stabilizer_group_recognized": "PSL2(11)",')
    outer_name = "PGL2(11)" if norm == 1320 else "PSL2(11) (self-normalizer)"
    print(f'    "outer_stabilizer_order": {norm},')
    print(f'    "outer_stabilizer_group_recognized": "{outer_name}",')
    print(
        '    "derived_from": '
        '"Coset action on PSL2(11) ⊂ M12 '
        '(found inside the 12-point permrep generators from M12G1-p12aB0)."'
    )
    print("  }")


if __name__ == "__main__":
    main()
