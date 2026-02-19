#!/usr/bin/env python3
"""Association-scheme extractor for ATLAS GAP permutation reps (small degrees).

Implements:
 - parse_gap_permrep(file) -> list[perm tuples]
 - build_schreier_stabilizer(generators, base=0) -> stabilizer generators (perms)
 - compute_suborbits_from_generators(generators, base=0) -> list of H-orbits (suborbits)
 - compute_intersection_numbers(suborbits, coset_reps, gens, base=0) -> p_{ij}^k

Designed to run on moderate degrees (He:2058). Not suitable for HN:1,140,000.
"""
from __future__ import annotations

import json
import logging
import math
import re
from collections import Counter, deque
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

logger = logging.getLogger(__name__)  # module logger for diagnostics


def _perm_from_cycle_notation(cycle_text: str, n: int) -> tuple[int, ...]:
    # cycle_text like "(1,2)(3,4,5)" -> 0-indexed tuple mapping
    perm = list(range(n))
    for cyc in re.finditer(r"\(([^)]+)\)", cycle_text):
        nums = [int(x.strip()) - 1 for x in cyc.group(1).split(",") if x.strip()]
        if not nums:
            continue
        for a, b in zip(nums, nums[1:] + nums[:1]):
            perm[a] = b
    return tuple(perm)


def _compose(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    # (p o q)(i) = p[q[i]] ; permutations as 0-indexed image tuples
    return tuple(p[q[i]] for i in range(len(p)))


def _inv(p: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * len(p)
    for i, a in enumerate(p):
        out[a] = i
    return tuple(out)


def parse_gap_permrep(gap_path: Path) -> List[tuple[int, ...]]:
    text = gap_path.read_text(encoding="utf-8")
    # detect degree by searching for highest integer in cycles
    nums = [int(x) for x in re.findall(r"\b(\d+)\b", text)]
    if not nums:
        raise RuntimeError("no integers found in GAP file")
    n = max(nums)
    # find lines like b11 := (1,374)(2,708)... or gens := [ ... ]
    perms: List[tuple[int, ...]] = []
    for m in re.finditer(r"([a-zA-Z0-9_]+)\s*:=\s*((?:\([^)]*\))+)", text):
        cycle_text = m.group(2)
        perms.append(_perm_from_cycle_notation(cycle_text, n))
    # fallback: look for PermList / gens := [ (...) , (...) ] style
    if not perms:
        m = re.search(
            r"gens\s*:=\s*\[\s*((?:\([^)]*\)\s*,?\s*)+)\]", text, flags=re.DOTALL
        )
        if m:
            inner = m.group(1)
            # split by '),(' or '), ' conservatively
            cycles = re.findall(r"\([^)]*\)", inner)
            if cycles:
                cycle_text = "".join(cycles)
                perms.append(_perm_from_cycle_notation(cycle_text, n))
    return perms


def _point_bfs_coset_reps(
    gens: Iterable[tuple[int, ...]], n: int, base: int = 0
) -> Dict[int, tuple[int, ...]]:
    # return map point -> permutation p with p(base)=point
    gens = list(gens)
    idperm = tuple(range(n))
    rep: Dict[int, tuple[int, ...]] = {base: idperm}
    q = deque([base])
    while q:
        u = q.popleft()
        p_u = rep[u]
        for g in gens:
            v = g[u]
            if v not in rep:
                # rep[v] = g o p_u
                rep[v] = _compose(g, p_u)
                q.append(v)
    return rep


def schreier_stabilizer_from_coset_reps(
    gens: Iterable[tuple[int, ...]],
    coset_reps: Dict[int, tuple[int, ...]],
    base: int = 0,
) -> List[tuple[int, ...]]:
    # Schreier generators s = t_u * g * inv(t_{g(u)}) which fix base
    gens = list(gens)
    Hgens: Set[tuple[int, ...]] = set()
    for u, t_u in coset_reps.items():
        for g in gens:
            gu = g[u]
            t_gu = coset_reps[gu]
            s = _compose(t_u, _compose(g, _inv(t_gu)))
            # sanity: s[base] should be base
            if s[base] != base:
                # numerical noise or cycle notation mismatch
                continue
            Hgens.add(s)
    return list(Hgens)


def orbit_of_group_on_points(
    generators: Iterable[tuple[int, ...]], start: int
) -> List[int]:
    gens = list(generators)
    seen = {start}
    q = deque([start])
    while q:
        u = q.popleft()
        for g in gens:
            v = g[u]
            if v not in seen:
                seen.add(v)
                q.append(v)
    return sorted(seen)


def compute_suborbits_from_generators(
    gens: Iterable[tuple[int, ...]], base: int = 0
) -> List[List[int]]:
    gens = list(gens)
    n = len(gens[0])
    # coset reps mapping base->point
    coset_reps = _point_bfs_coset_reps(gens, n, base)
    # compute stabilizer generators (Schreier)
    Hgens = schreier_stabilizer_from_coset_reps(gens, coset_reps, base)
    # compute H-orbits on points (these are the suborbits)
    assigned = [False] * n
    suborbits: List[List[int]] = []
    for v in range(n):
        if assigned[v]:
            continue
        orb = orbit_of_group_on_points(Hgens, v)
        for w in orb:
            assigned[w] = True
        suborbits.append(orb)
    # ensure base is in first orbit (index 0)
    suborbits_sorted = sorted(suborbits, key=lambda s: (0 not in s, len(s)))
    return suborbits_sorted


def compute_intersection_numbers(
    suborbits: List[List[int]],
    coset_reps: Dict[int, tuple[int, ...]],
    gens: Iterable[tuple[int, ...]],
    base: int = 0,
) -> Tuple[List[List[List[int]]], List[tuple[int, ...]]]:
    # p_{ij}^k via representative mapping
    r = len(suborbits)
    # build quick membership index
    which = {}
    for idx, S in enumerate(suborbits):
        for v in S:
            which[v] = idx
    # prepare coset rep permutations for base->x
    # coset_reps provided externally (from _point_bfs_coset_reps)
    pijk = [[[0 for _ in range(r)] for __ in range(r)] for ___ in range(r)]
    for i, S_i in enumerate(suborbits):
        # pick representative x in S_i
        x = S_i[0]
        t_x = coset_reps[x]
        inv_t_x = _inv(t_x)
        for j, S_j in enumerate(suborbits):
            # compute image of S_j under t_x: t_x(S_j)
            img = {t_x[y] for y in S_j}
            # count intersections with each S_k
            cnts = Counter(which[z] for z in img)
            for k in range(r):
                pijk[i][j][k] = cnts.get(k, 0)
    return pijk


def build_matrices_from_pijk(pijk: List[List[List[int]]]) -> List[List[List[int]]]:
    # M_i matrices where (M_i)_{j,k}=p_{ij}^k
    r = len(pijk)
    Ms = []
    for i in range(r):
        M = [[pijk[i][j][k] for k in range(r)] for j in range(r)]
        Ms.append(M)
    return Ms


def analyze_gap_permrep_association(gap_file: str | Path, base: int = 1) -> dict:
    """Parse one ATLAS GAP permrep file or a group of companion .g* files and
    return the association-scheme data for the point-stabilizer of `base`.

    Behavioural notes:
    - If `gap_file` is a single file like `Foo-gN.g1` but there are companion
      files `Foo-gN.g2`, `Foo-gN.g3` etc., all matching `Foo-gN.g*` will be
      parsed and their generators combined (this mirrors ATLAS split files).
    - If parsing yields an incomplete orbit (coset reps < degree) we raise a
      clear error rather than silently producing many singleton suborbits.
    """
    gap_file = Path(gap_file)

    # if the file is part of an ATLAS multi-file permrep (e.g. .g1/.g2), try to
    # collect all siblings with the same base name (Foo-gN.g*) so callers may
    # pass a single .g1 file and still get the full generating set.
    siblings: List[Path] = []
    stem_match = re.match(r"^(.*)(\.g\d+)$", gap_file.name)
    if stem_match:
        prefix = stem_match.group(1)
        for p in gap_file.parent.glob(prefix + ".g*"):
            siblings.append(p)
    else:
        siblings = [gap_file]

    # parse every sibling we found (or the single file)
    perms: List[tuple[int, ...]] = []
    for p in siblings:
        perms.extend(parse_gap_permrep(p))

    if not perms:
        raise RuntimeError("no permutations parsed from %s" % gap_file)

    # degree is length of permutation tuple
    n = len(perms[0])
    # convert base to 0-index
    base0 = base - 1
    # compute coset reps for G acting on points (rep mapping base->point)
    coset_reps = _point_bfs_coset_reps(perms, n, base0)
    if len(coset_reps) != n:
        # Try to recover by searching for another base that yields a full orbit.
        # Some GAP/ATLAS split files may place the transitive block on a point
        # other than the canonical `base` (rare), so attempt alternate bases
        # before failing the operation.
        found_full = False
        for alt in range(n):
            if alt == base0:
                continue
            alt_coset = _point_bfs_coset_reps(perms, n, alt)
            if len(alt_coset) == n:
                coset_reps = alt_coset
                base0 = alt
                found_full = True
                logger.info(
                    "analyze_gap_permrep_association: recovered full orbit using alternate base %d (original base %d produced %d of %d points)",
                    base0,
                    base,
                    len(coset_reps),
                    n,
                )
                break
        if not found_full:
            raise RuntimeError(
                f"incomplete orbit for base={base}; reached {len(coset_reps)} of {n} points - "
                "did you pass all companion .g* files?"
            )
        # continue using the recovered full orbit (base0 updated)

    suborbits = compute_suborbits_from_generators(perms, base0)
    sizes = [len(s) for s in suborbits]
    # verify base orbit present
    assert any(base0 in s for s in suborbits)
    pijk = compute_intersection_numbers(suborbits, coset_reps, perms, base0)
    Ms = build_matrices_from_pijk(pijk)
    # compute eigenvalues of the r x r matrices (small)
    import numpy as _np

    eigs = [_np.linalg.eigvals(_np.array(M, dtype=float)).tolist() for M in Ms]
    return {
        "degree": n,
        "rank": len(suborbits),
        "suborbit_lengths": sizes,
        "pijk": pijk,
        "Ms": Ms,
        "eigs": eigs,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: w33_permrep_association.py <gap-file> [base=1]")
        raise SystemExit(1)
    out = analyze_gap_permrep_association(
        sys.argv[1], base=int(sys.argv[2]) if len(sys.argv) > 2 else 1
    )
    print(json.dumps(out, indent=2))
