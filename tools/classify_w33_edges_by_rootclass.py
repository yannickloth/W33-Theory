#!/usr/bin/env python3
"""Tag W33 edges with their E8 root-class labels.

Reads the explicit bijection decomposition artifact (root coords + class
keys) and the edge->root index map.  Outputs CSV and counts JSON in artifacts.
"""
from pathlib import Path
import json
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]

u1 = (1,1,1,1,1,1,1,1)
u2 = (1,1,1,1,1,1,-1,-1)
def dot(r,u): return sum(int(r[i])*int(u[i]) for i in range(8))


def main():
    art = json.loads((ROOT / "artifacts" / "explicit_bijection_decomposition.json").read_text(encoding="utf-8"))
    roots = art["root_coords"]
    edge_to_root = {int(k): int(v) for k,v in art["edge_to_root_index"].items()}

    class72_key = tuple(art["class72_key"])
    class1_keys = set(tuple(x) for x in art["class1_keys"])
    class27_keys = set(tuple(x) for x in art["class27_keys"])

    root_class = {}
    for i,r in enumerate(roots):
        k = (dot(r,u1), dot(r,u2))
        if k == class72_key:
            root_class[i] = "E6_72"
        elif k in class1_keys:
            root_class[i] = "A2_6"
        elif k in class27_keys:
            root_class[i] = "MIXED_162"
        else:
            root_class[i] = "OTHER"

    counts = defaultdict(int)
    rows = []
    for eidx,ridx in sorted(edge_to_root.items()):
        c = root_class[ridx]
        counts[c]+=1
        rows.append((eidx,ridx,c))

    out_csv = ROOT / "artifacts" / "w33_edges_by_rootclass.csv"
    out_csv.parent.mkdir(exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        f.write("edge_index,root_index,root_class\n")
        for eidx,ridx,c in rows:
            f.write(f"{eidx},{ridx},{c}\n")

    out_json = ROOT / "artifacts" / "w33_edges_by_rootclass_counts.json"
    out_json.write_text(json.dumps(dict(counts), indent=2), encoding="utf-8")

    print("=== W33 edges by root class ===")
    for k in sorted(counts):
        print(k, counts[k])
    print("Wrote:", out_csv)
    print("Wrote:", out_json)


if __name__ == "__main__":
    main()
