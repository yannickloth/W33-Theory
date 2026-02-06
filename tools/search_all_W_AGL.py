"""
Search all 3-dim W subspaces for an affine map (AGL(3,3)) carrying the coset triads
(Hamming=6 triangles) to the E6 affine triads.

This script performs early pruning: for each affine map, it first checks a small sample of
coset triads and only if those map to E6 triads does it check the full set equality.
"""

import json
from itertools import combinations, product

import numpy as np

# Load E6 coords and triads
with open(
    "artifacts/e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8"
) as f:
    e6_heis = json.load(f)

# e6 triads set
e6_triads = set()
for item in e6_heis["affine_u_lines"]:
    for tri in item["triads"]:
        e6_triads.add(tuple(sorted(tri)))

# e6 coords to id
e6_coords_map = {
    tuple(v["u"] + [v["z"]]): int(k) for k, v in e6_heis["e6id_to_heisenberg"].items()
}
assert len(e6_coords_map) == 27

# G and M
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

# find kernel and all 3-dim subspaces (copy from SEARCH_3D...)
kernel = [m for m in messages if (M @ np.array(m) % 3 == 0).all()]

# function to build span
from itertools import product as cart


def span(basis):
    S = set()
    for coeffs in cart(range(3), repeat=len(basis)):
        v = tuple(
            sum((coeffs[i] * basis[i][j]) for i in range(len(basis))) % 3
            for j in range(6)
        )
        S.add(v)
    return S


subspace_list = []
seen = set()
for a, b, c in combinations(kernel, 3):
    sp = span([a, b, c])
    if len(sp) == 27:
        key = tuple(sorted(sp))
        if key not in seen:
            seen.add(key)
            subspace_list.append(sp)

print("found subspaces:", len(subspace_list))

# Precompute GL(3,3) matrices
F = [0, 1, 2]
GL = []
for entries in product(F, repeat=9):
    M3 = np.array(entries, dtype=int).reshape((3, 3))
    a = M3
    det_mod3 = (
        a[0, 0] * (a[1, 1] * a[2, 2] - a[1, 2] * a[2, 1])
        - a[0, 1] * (a[1, 0] * a[2, 2] - a[1, 2] * a[2, 0])
        + a[0, 2] * (a[1, 0] * a[2, 1] - a[1, 1] * a[2, 0])
    ) % 3
    if det_mod3 != 0:
        GL.append(M3 % 3)
print("GL(3,3) size:", len(GL))
translations = list(product(range(3), repeat=3))

# Define a function to test one W
from itertools import islice


def test_W(W, idx=None):
    # build coset reps
    used = set()
    cosets = []
    for m in messages:
        if m in used:
            continue
        cosets.append(m)
        for w in W:
            used.add(tuple((m[i] + w[i]) % 3 for i in range(6)))
    if len(cosets) != 27:
        return None
    # coset coords
    # We need to produce 3D coordinates for cosets via an M' whose kernel equals W.
    # Find a basis for W (3 independent vectors)
    W_list = list(W)
    basisW = []
    for v in W_list:
        if len(basisW) == 0:
            basisW.append(v)
            continue
        # check linear independence over F3 wrt current basis
        # attempt to express v as linear combination of basisW
        in_span = False
        if len(basisW) == 1:
            for a in range(3):
                if tuple((a * basisW[0][i]) % 3 for i in range(6)) == v:
                    in_span = True
                    break
        elif len(basisW) == 2:
            for a in range(3):
                for b in range(3):
                    test = tuple(
                        (a * basisW[0][i] + b * basisW[1][i]) % 3 for i in range(6)
                    )
                    if test == v:
                        in_span = True
                        break
                if in_span:
                    break
        if not in_span:
            basisW.append(v)
        if len(basisW) == 3:
            break

    if len(basisW) != 3:
        return None

    # Solve for annihilator: r in F3^6 with r·w = 0 for all w in basisW
    annihilators = []
    for r in product(range(3), repeat=6):
        if all(sum((r[i] * basisW[j][i]) for i in range(6)) % 3 == 0 for j in range(3)):
            annihilators.append(r)

    # Choose three independent rows from annihilators to form M' (3x6)
    Mprime_rows = []
    for r in annihilators:
        # test independence relative to rows chosen so far
        if len(Mprime_rows) == 0:
            Mprime_rows.append(r)
            continue
        in_span = False
        if len(Mprime_rows) == 1:
            for a in range(3):
                if tuple((a * np.array(Mprime_rows[0]) % 3).tolist()) == r:
                    in_span = True
                    break
        elif len(Mprime_rows) == 2:
            for a in range(3):
                for b in range(3):
                    test = tuple(
                        (a * np.array(Mprime_rows[0]) + b * np.array(Mprime_rows[1]))
                        % 3
                    )
                    if test == r:
                        in_span = True
                        break
                if in_span:
                    break
        if not in_span:
            Mprime_rows.append(r)
        if len(Mprime_rows) == 3:
            break

    if len(Mprime_rows) != 3:
        return None

    Mprime = np.array(Mprime_rows, dtype=int) % 3
    # coset 3D coords via Mprime
    coset_coords = [tuple((Mprime @ np.array(m) % 3).tolist()) for m in cosets]

    # build coset triads indices (Hamming=6 condition on codewords still relevant)
    cw27 = [tuple((np.array(m) @ G_matrix % 3).tolist()) for m in cosets]
    coset_triads = []
    for i, j, k in combinations(range(27), 3):
        if (
            sum(x != y for x, y in zip(cw27[i], cw27[j])) == 6
            and sum(x != y for x, y in zip(cw27[i], cw27[k])) == 6
            and sum(x != y for x, y in zip(cw27[j], cw27[k])) == 6
        ):
            coset_triads.append((i, j, k))
    if len(coset_triads) != 36:
        return None

    # For speed, pick sample of triads to test early
    sample_triads = list(islice(coset_triads, 0, 3))

    # precompute mapped coords for each GL
    for L_idx, L in enumerate(GL):
        if idx is not None and L_idx % 1000 == 0:
            print(f"  testing L {L_idx}/{len(GL)} for W {idx}")
        mapped_no_t = [tuple((L @ np.array(c)) % 3) for c in coset_coords]
        # for each translation, check sample first
        for t in translations:
            mapped_with_t = [
                tuple((np.array(m) + np.array(t)) % 3) for m in mapped_no_t
            ]
            # quick check: all mapped coords must be present in e6_coords_map
            try:
                mapped_ids = [e6_coords_map[c] for c in mapped_with_t]
            except KeyError:
                continue
            # sample triads
            ok = True
            for tri in sample_triads:
                mapped_tri = tuple(
                    sorted((mapped_ids[tri[0]], mapped_ids[tri[1]], mapped_ids[tri[2]]))
                )
                if mapped_tri not in e6_triads:
                    ok = False
                    break
            if not ok:
                continue
            # full check
            mapped_triads = set(
                tuple(sorted((mapped_ids[a], mapped_ids[b], mapped_ids[c])))
                for (a, b, c) in coset_triads
            )
            if mapped_triads == e6_triads:
                return {"L": L.tolist(), "t": t, "cosets": cosets}
    return None


# Run over all W and stop early if found
found = None
for i, W in enumerate(subspace_list):
    print(f"testing W {i+1}/{len(subspace_list)} (idx={i})")
    try:
        res = test_W(W, i)
    except Exception as e:
        print("ERROR while testing W idx", i, e)
        raise
    if res:
        print("Found mapping for W idx", i)
        found = (i, res)
        break
    else:
        print("  no mapping for W idx", i)

print("done, found?", found is not None)
if found:
    with open("artifacts/found_W_mapping.json", "w") as f:
        json.dump({"idx": found[0], "res": found[1]}, f, indent=2)
    print("wrote artifacts/found_W_mapping.json")
else:
    print("no affine mapping found for any W")
