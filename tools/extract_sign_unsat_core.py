#!/usr/bin/env python3
"""
Find minimal GF(2) unsat-cores for sign parity inconsistencies in existing mapping outputs.
Writes results to artifacts/sign_unsat_cores.json
"""
import json
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

# load e6 triads and d_bits
with open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8") as f:
    heis = json.load(f)
E6_TRIADS = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]
with open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8") as f:
    sdata = json.load(f)
d_map_sign = {
    tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
}
D_BITS = {t: (0 if sgn == 1 else 1) for t, sgn in d_map_sign.items()}

# reconstruct kernel -> subspaces
import numpy as np

G_matrix = np.array(
    [
        [1, 0, 0, 0, 0, 0, 1, 1, 2, 2, 1, 2],
        [0, 1, 0, 0, 0, 0, 1, 2, 1, 2, 2, 1],
        [0, 0, 1, 0, 0, 0, 2, 1, 1, 1, 2, 2],
        [0, 0, 0, 1, 0, 0, 2, 2, 1, 1, 1, 2],
        [0, 0, 0, 0, 1, 0, 1, 2, 2, 1, 1, 2],
        [0, 0, 0, 0, 0, 1, 2, 1, 2, 2, 1, 1],
    ]
)
M = np.array([[2, 2, 1, 2, 1, 2], [0, 2, 2, 0, 2, 1]], dtype=int)
messages = list(product(range(3), repeat=6))
kernel = [m for m in messages if (M @ np.array(m) % 3 == 0).all()]

subspaces = set()
subspace_list = []
for a, b, c in combinations(kernel, 3):
    S = set()
    for coeffs in product(range(3), repeat=3):
        v = tuple(
            (coeffs[0] * a[i] + coeffs[1] * b[i] + coeffs[2] * c[i]) % 3
            for i in range(6)
        )
        S.add(v)
    if len(S) == 27:
        key = tuple(sorted(S))
        if key not in subspaces:
            subspaces.add(key)
            subspace_list.append(S)

# helpers


def compute_coset_triads(W):
    used = set()
    cosets = []
    for m in messages:
        if m in used:
            continue
        cosets.append(m)
        for w in W:
            used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
    cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
    triads = []
    for i in range(27):
        for j in range(i + 1, 27):
            for k in range(j + 1, 27):
                if (
                    sum(x != y for x, y in zip(cw27[i], cw27[j])) == 6
                    and sum(x != y for x, y in zip(cw27[i], cw27[k])) == 6
                    and sum(x != y for x, y in zip(cw27[j], cw27[k])) == 6
                ):
                    triads.append((i, j, k))
    return set(tuple(sorted(t)) for t in triads), cosets, cw27


# GF(2) solvability + conflict certificate (tracks row combinations)


def is_solvable_and_conflict(tris):
    # tris: list of E6 tri tuples (unordered)
    nodes = sorted({v for t in tris for v in t})
    idx = {v: i for i, v in enumerate(nodes)}
    rows = []
    for t in tris:
        m = 0
        for v in t:
            m |= 1 << idx[v]
        rhs = D_BITS.get(t, 0)
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
            # found certificate: c is bitmask of original rows
            cert_inds = [j for j in range(len(rows)) if (c >> j) & 1]
            return False, cert_inds
    return True, None


# minimal unsat core via deletion-based reduction


def minimal_unsat_core(tris):
    if not tris:
        return []
    solv, _ = is_solvable_and_conflict(tris)
    if solv:
        return None
    S = list(tris)
    changed = True
    while changed:
        changed = False
        for t in S.copy():
            S2 = [x for x in S if x != t]
            solv2, _ = is_solvable_and_conflict(S2)
            if not solv2:
                S = S2
                changed = True
    return S


# process mapping files
import glob

files = sorted(
    list(ART.glob("opt_mapping_W*_status_*.json"))
    + list(ART.glob("anchor_core_cpsat_W*_status_*.json"))
    + list(ART.glob("anchor_specific_cpsat_W*_status_*.json"))
)
# deduplicate and sort by filename for stable processing order
files = sorted(set(files), key=lambda p: p.name)
print("Found mapping files:", [p.name for p in files])
results = []
for f in files:
    data = json.load(open(f, "r", encoding="utf-8"))
    W_idx = data["W_idx"]
    W = subspace_list[W_idx]
    coset_triads_set, cosets, cw27 = compute_coset_triads(W)
    mapping = data["mapping"]
    matched = []
    for t in E6_TRIADS:
        u = tuple(sorted((mapping[t[0]], mapping[t[1]], mapping[t[2]])))
        if u in coset_triads_set:
            matched.append(t)
    matched = sorted(set(matched))
    m_count = len(matched)
    solv, conf = is_solvable_and_conflict(matched)
    print(f"Processing {f.name} W{W_idx} matched {m_count} solvable {solv}")
    entry = {"file": f.name, "W_idx": W_idx, "matched": m_count, "solvable": bool(solv)}
    if solv:
        results.append(entry)
        continue
    # find minimal core
    core = minimal_unsat_core(matched)
    # get certificate for core
    solv2, conf2 = is_solvable_and_conflict(core)
    assert solv2 == False and conf2 is not None
    core_inds = conf2
    core_tris = [list(core[i]) for i in range(len(core))]
    # certificate rows: which of the core rows combine to contradiction
    cert_rows = [core[i] for i in core_inds]
    entry.update(
        {
            "unsat_core": core_tris,
            "core_size": len(core_tris),
            "certificate_core_indices": core_inds,
            "certificate_rows": [list(t) for t in cert_rows],
        }
    )
    results.append(entry)

(Path(ART) / "sign_unsat_cores.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print("Wrote artifacts/sign_unsat_cores.json")
