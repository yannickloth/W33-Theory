"""GF(2) helper utilities used by parity pipelines.
Functions:
- is_solvable_and_conflict(tris, d_bits) -> (bool, conflict_indices_or_None)
- minimal_unsat_core(tris, d_bits) -> minimal unsat subset list or None
- solve_parity_pycryptosat(tris, d_bits) -> (sat_bool, signs_dict_or_None)
"""

from typing import Dict, List, Optional, Tuple

# NOTE: pycryptosat is an optional dependency; only used by solve_parity_pycryptosat
try:
    from pycryptosat import Solver
except Exception:  # pragma: no cover - optional
    Solver = None


def is_solvable_and_conflict(
    tris: List[Tuple[int, int, int]], d_bits: Dict[Tuple[int, int, int], int]
) -> Tuple[bool, Optional[List[int]]]:
    """Return (True,None) if system is solvable; if not solvable returns (False, list_of_row_indices_in_conflict)"""
    # build nodes list
    nodes = sorted({v for t in tris for v in t})
    idx = {v: i for i, v in enumerate(nodes)}
    rows = []  # (mask, rhs)
    for t in tris:
        m = 0
        for v in t:
            m |= 1 << idx[v]
        rhs = d_bits.get(tuple(sorted(t)), 0)
        rows.append((m, rhs))
    # elimination with tracking
    pivots = {}
    combs = [1 << i for i in range(len(rows))]
    for i, (mask, rhs) in enumerate(rows):
        m = mask
        r = rhs
        c = combs[i]
        while m:
            p = m.bit_length() - 1
            if p in pivots:
                pm, pr, pc = pivots[p]
                m ^= pm
                r ^= pr
                c ^= pc
            else:
                pivots[p] = (m, r, c)
                break
        if m == 0 and r == 1:
            cert_inds = [j for j in range(len(rows)) if (c >> j) & 1]
            return False, cert_inds
    return True, None


def minimal_unsat_core(
    tris: List[Tuple[int, int, int]], d_bits: Dict[Tuple[int, int, int], int]
) -> Optional[List[Tuple[int, int, int]]]:
    """Return a deletion-minimal unsat core (list of triads) or None if system is solvable."""
    if not tris:
        return None
    solv, _ = is_solvable_and_conflict(tris, d_bits)
    if solv:
        return None
    S = list(tris)
    changed = True
    while changed:
        changed = False
        for t in S.copy():
            S2 = [x for x in S if x != t]
            solv2, _ = is_solvable_and_conflict(S2, d_bits)
            if not solv2:
                S = S2
                changed = True
    return S


def solve_parity_pycryptosat(
    tris: List[Tuple[int, int, int]], d_bits: Dict[Tuple[int, int, int], int]
) -> Tuple[bool, Optional[Dict[int, bool]]]:
    """Attempt to find a sign assignment s_i in {0,1} for nodes 0..26 that satisfies s_i xor s_j xor s_k == d for each tri in tris with d_bits known.
    Returns (True, signs_dict) or (False, None).
    Uses pycryptosat.Solver if available.
    """
    if Solver is None:
        raise RuntimeError("pycryptosat not available")
    s = Solver()
    # use var ids 1..27 for s_0..s_26
    involved_nodes = set(v for t in tris for v in t)
    for t in tris:
        tri = tuple(sorted(t))
        db = d_bits.get(tri, None)
        if db is None:
            continue
        a, b, c = tri
        s.add_xor_clause([a + 1, b + 1, c + 1], bool(db))
    res = s.solve()
    sat = bool(res[0])
    if not sat:
        return False, None
    assignment = res[1]
    # assignment is sequence-like with index == var id
    signs = {}
    for i in range(27):
        if i + 1 < len(assignment):
            signs[i] = bool(assignment[i + 1])
        else:
            signs[i] = False
    return True, signs
