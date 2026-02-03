#!/usr/bin/env sage
"""Build the GAP group induced on the 40 W33 lines and search for order-1440 subgroups.
Writes artifacts/sage_1440_line_action.json summarizing candidate subgroup orbit sizes on the 40 lines.
"""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from tools.find_schlafli_embedding_in_w33 import compute_w33_lines
from tools.w33_aut_group_construct import build_points, generate_group, matrix_to_perm

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

    # compute induced permutations on line indices for each generator
    line_perms = []
    line_index = {tuple(sorted(l)): i for i, l in enumerate(lines)}
    for perm in point_perms:
        images = []
        for line in lines:
            new_line = tuple(sorted(perm[i] for i in line))
            images.append(new_line)
        # map to indices (1-based for GAP)
        images_idx = [line_index[new_line] + 1 for new_line in images]
        line_perms.append(images_idx)

    # build GAP group expression on 1..40 using PermList
    perm_exprs = ["PermList([%s])" % ",".join(str(x) for x in p) for p in line_perms]
    group_expr = "Group(" + ",".join(perm_exprs) + ")"

    Ggap = gap(group_expr)
    print("Built GAP group on lines; order:", int(Ggap.Order()))

    classes = gap("ConjugacyClassesSubgroups(%s)" % group_expr)
    nclasses = int(classes.Length())
    print("Found conjugacy classes:", nclasses)

    candidates = []
    for i in range(1, nclasses + 1):
        H = classes[i].Representative()
        if int(H.Order()) == 1440:
            sdesc = str(H.StructureDescription())
            # compute orbits on 1..40
            points_list_expr = (
                "[" + ",".join(str(i) for i in range(1, len(lines) + 1)) + "]"
            )
            gap_points = gap(points_list_expr)
            orbits = H.Orbits(gap_points)
            orb_sizes = [int(o.Length()) for o in orbits]
            candidates.append(
                {"structure": sdesc, "orb_sizes": sorted(orb_sizes, reverse=True)}
            )

    out = {
        "group_order": int(Ggap.Order()),
        "n_candidates_1440": len(candidates),
        "candidates": candidates,
    }
    (ART / "sage_1440_line_action.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print("Wrote", ART / "sage_1440_line_action.json")


if __name__ == "__main__":
    main()
