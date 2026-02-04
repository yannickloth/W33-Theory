#!/usr/bin/env sage
"""Compute line-orbits of the C2xS6 subgroup in the induced line action and write them out.
"""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from tools.find_schlafli_embedding_in_w33 import compute_w33_lines
from tools.w33_aut_group_construct import build_points, generate_group

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

try:
    from sage.interfaces.gap import gap
except Exception as e:
    print("This script must be run inside Sage: missing GAP interface:", e)
    raise SystemExit(1)


def main():
    pts = build_points()
    _, point_perms = generate_group(pts)
    lines = compute_w33_lines(pts)
    line_index = {tuple(sorted(l)): i for i, l in enumerate(lines)}
    line_perms = []
    for perm in point_perms:
        images_idx = [
            line_index[tuple(sorted(perm[i] for i in line))] + 1 for line in lines
        ]
        line_perms.append(images_idx)
    perm_exprs = ["PermList([%s])" % ",".join(str(x) for x in p) for p in line_perms]
    group_expr = "Group(" + ",".join(perm_exprs) + ")"

    classes = gap("ConjugacyClassesSubgroups(%s)" % group_expr)
    idx = None
    for i in range(1, int(classes.Length()) + 1):
        H = classes[i].Representative()
        if int(H.Order()) == 1440:
            idx = i
            break
    if idx is None:
        print("No class index found")
        return
    H = classes[idx].Representative()
    pts_list_expr = "[" + ",".join(str(i) for i in range(1, len(lines) + 1)) + "]"
    gap_pts = gap(pts_list_expr)
    orbs = H.Orbits(gap_pts)
    orb_lists = []
    for j in range(1, int(orbs.Length()) + 1):
        L = orbs[j]
        orb_lists.append([int(L[k]) - 1 for k in range(1, int(L.Length()) + 1)])
    out = {"class_index": idx, "orbits": orb_lists}
    (ART / "sage_c2s6_line_orbits.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print("Wrote", ART / "sage_c2s6_line_orbits.json")


if __name__ == "__main__":
    main()
