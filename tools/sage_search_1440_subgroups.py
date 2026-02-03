#!/usr/bin/env sage
"""Search Aut(W(3,3)) for subgroups of order 1440 and report orbit sizes on 40 points.

This script:
- imports the permutation generators built by `tools.w33_aut_group_construct` (permutation form)
- constructs a Sage `PermutationGroup` from those generators
- uses GAP via Sage to get conjugacy classes of subgroups and filters those of order 1440
- for each candidate subgroup, computes orbit sizes on the 40 points and records structure
- writes `artifacts/sage_1440_subgroup_search.json` summarizing candidates

Run inside Sage (Docker) for best results.
"""
import json
import sys
from pathlib import Path

# ensure local tools are importable
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from tools.w33_aut_group_construct import build_points, generate_group, matrix_to_perm

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

# Only import the GAP interface from Sage; we'll construct GAP permutations directly
try:
    from sage.interfaces.gap import gap
except Exception as e:
    print("This script must be run inside Sage: missing GAP interface:", e)
    raise SystemExit(1)


def perms_from_matrices(points):
    # generate permutation images from generator matrices
    _, gens_matrices = generate_group(points)
    perms = []
    for M in gens_matrices:
        perm = matrix_to_perm(M, points)
        # convert to 1-based image list for Sage Permutation
        perm1 = [p + 1 for p in perm]
        perms.append(Permutation(perm1))
    return perms


def main():
    pts = build_points()
    n = len(pts)
    assert n == 40

    # Build GAP group directly from permutation image lists to avoid Sage permutation class issues
    G, perm_gens = generate_group(pts)
    # perm_gens is a list of generator permutations represented as tuples mapping 0..39 -> 0..39
    perm_exprs = []
    for perm in perm_gens:
        images = ",".join(str(p + 1) for p in perm)  # GAP wants 1-based images
        perm_exprs.append(f"PermList([{images}])")
    group_expr = "Group(" + ",".join(perm_exprs) + ")"
    Ggap = gap(group_expr)
    print("Built GAP group. GAP order:", int(Ggap.Order()))

    print("Starting GAP ConjugacyClassesSubgroups (this can take a while)...")
    sys.stdout.flush()
    classes = Ggap.ConjugacyClassesSubgroups()
    print("Done computing conjugacy classes; total classes:", int(classes.Length()))
    sys.stdout.flush()

    candidates = []
    for c in classes:
        H = c.Representative()
        sz = int(H.Order())
        if sz == 1440:
            # compute structure description
            sdesc = str(H.StructureDescription())
            # Compute orbits on 1..40 under H action using GAP list
            points_list_expr = "[" + ",".join(str(i) for i in range(1, n + 1)) + "]"
            gap_points = gap(points_list_expr)
            orbits = H.Orbits(gap_points)
            orb_sizes = [int(o.Length()) for o in orbits]
            orb_sizes_sorted = sorted(orb_sizes, reverse=True)
            candidates.append({"structure": sdesc, "orb_sizes": orb_sizes_sorted})

    out = {
        "group_order": int(Ggap.Order()),
        "n_candidates_1440": len(candidates),
        "candidates": candidates,
    }
    (ART / "sage_1440_subgroup_search.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print("Wrote", ART / "sage_1440_subgroup_search.json")


if __name__ == "__main__":
    main()
