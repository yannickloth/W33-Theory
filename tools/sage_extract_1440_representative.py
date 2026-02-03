#!/usr/bin/env sage
"""Extract representative generators for the GAP conjugacy class of order 1440.
Writes artifacts/sage_c2_s6_representative.json with generator images (0-based).
"""
import json
import sys
from pathlib import Path

# ensure local tools importable (add workspace root)
sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.path.append(str(Path(__file__).resolve().parent))

try:
    from sage.interfaces.gap import gap
except Exception as e:
    print("This script must be run inside Sage: missing GAP interface:", e)
    raise SystemExit(1)

from tools.w33_aut_group_construct import build_points, generate_group, matrix_to_perm

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)


def main():
    pts = build_points()
    _, perm_gens = generate_group(pts)
    # build GAP group expression from perms
    perm_exprs = []
    for perm in perm_gens:
        images = ",".join(str(p + 1) for p in perm)
        perm_exprs.append(f"PermList([{images}])")
    group_expr = "Group(" + ",".join(perm_exprs) + ")"
    # assign to GAP variable G for later references
    gap(f"G := {group_expr}")
    Ggap = gap("G")
    print("GAP group order:", int(Ggap.Order()))

    classes = gap("ConjugacyClassesSubgroups(G)")
    nclasses = int(classes.Length())
    print("Conjugacy classes of subgroups:", nclasses)

    rep_info = None
    for i in range(1, nclasses + 1):
        c = classes[i]
        H = c.Representative()
        sz = int(H.Order())
        if sz == 1440:
            sdesc = str(H.StructureDescription())
            print("Found class index", i, "structure", sdesc)
            # extract generators of H by evaluating gen(k) for k in 1..40
            # ask GAP to compute the permutation lists for the generators of this representative
            perm_lists = gap(
                f"List(GeneratorsOfGroup(classes[{i}].Representative()), g -> PermList(g))"
            )
            gens_list = []
            for idxp in range(1, int(perm_lists.Length()) + 1):
                perm = perm_lists[idxp]
                img = [int(perm[j]) - 1 for j in range(1, len(pts) + 1)]
                gens_list.append(img)
            rep_info = {"structure": sdesc, "order": sz, "generators": gens_list}
            break

    if rep_info is None:
        print("No subgroup of order 1440 found")
        sys.exit(2)

    (ART / "sage_c2_s6_representative.json").write_text(
        json.dumps(rep_info, indent=2), encoding="utf-8"
    )
    print("Wrote", ART / "sage_c2_s6_representative.json")


if __name__ == "__main__":
    main()
