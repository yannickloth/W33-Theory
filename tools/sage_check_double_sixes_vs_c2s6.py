#!/usr/bin/env sage
"""Check whether the C2 x S6 subgroup (order 1440) of the line-action stabilizes any unordered double-six.
Writes artifacts/sage_c2s6_double_six_stabilized.json with any stabilized examples.
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
    double_file = ROOT / "artifacts" / "w33_double_sixes_full.json"
    if not double_file.exists():
        print("Double-sixes file missing; run tools/emit_w33_double_sixes.py first")
        raise SystemExit(2)
    doubles = json.loads(double_file.read_text(encoding="utf-8"))["double_sixes"]

    # build group on lines (as before)
    line_perms = []
    line_index = {tuple(sorted(l)): i for i, l in enumerate(lines)}
    for perm in point_perms:
        images_idx = [
            line_index[tuple(sorted(perm[i] for i in line))] + 1 for line in lines
        ]
        line_perms.append(images_idx)
    perm_exprs = ["PermList([%s])" % ",".join(str(x) for x in p) for p in line_perms]
    group_expr = "Group(" + ",".join(perm_exprs) + ")"
    Ggap = gap(group_expr)

    # find class of subgroups order 1440
    classes = gap("ConjugacyClassesSubgroups(%s)" % group_expr)
    nclasses = int(classes.Length())

    res = []
    for i in range(1, nclasses + 1):
        H = classes[i].Representative()
        if int(H.Order()) != 1440:
            continue
        print("Analyzing class index", i, "structure", H.StructureDescription())
        # check each double-six: whether H stablizes its union set
        for idx, ds in enumerate(doubles):
            S = ds["A"] + ds["B"]
            S1 = "Set([" + ",".join(str(x + 1) for x in S) + "])"
            # compute set stabilizer of H acting on 1..40
            stab = gap(f"Stabilizer({H}, {S1}, OnSets)")
            sz = int(stab.Order())
            if sz == 1440:
                print("Found double-six stabilized by H at index", idx)
                res.append({"index": idx, "A": ds["A"], "B": ds["B"]})
                # stop after first found
                break
        if res:
            break

    out = {"found": len(res) > 0, "examples": res}
    (ART / "sage_c2s6_double_six_stabilized.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print("Wrote", ART / "sage_c2s6_double_six_stabilized.json")


if __name__ == "__main__":
    main()
