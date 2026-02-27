#!/usr/bin/env python3
"""Classify E8 roots by dot‑pair with two fixed vectors u1,u2.

Produces a summary JSON in artifacts/e8_dotpair_class_summary.json and
prints statistics.  Uses explicit_bijection_decomposition.json for the root
coordinates and class keys.
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

    classes = defaultdict(list)
    for i,r in enumerate(roots):
        classes[(dot(r,u1), dot(r,u2))].append(i)

    sizes = sorted([(k,len(v)) for k,v in classes.items()], key=lambda kv: (-kv[1], kv[0]))
    print("=== DOT-PAIR CLASSES (u1,u2) ===")
    for k,sz in sizes[:20]:
        print(k, "size", sz)
    print("total classes:", len(sizes))
    total = sum(sz for _,sz in sizes)
    print("total roots:", total)

    class72_key = tuple(art["class72_key"])
    class1_keys = [tuple(x) for x in art["class1_keys"]]
    class27_keys = [tuple(x) for x in art["class27_keys"]]

    print("\n=== CHECK AGAINST ENCODED KEYS ===")
    print("class72_key", class72_key, "size", len(classes[class72_key]))
    c1 = sum(len(classes[k]) for k in class1_keys)
    c27 = sum(len(classes[k]) for k in class27_keys)
    print("sum class1_keys sizes:", c1, "(expect 6)")
    print("sum class27_keys sizes:", c27, "(expect 162)")
    print("remaining:", total - len(classes[class72_key]) - c1 - c27)

    out = {
        "class72_key": list(class72_key),
        "class72_size": len(classes[class72_key]),
        "class1_keys": [list(k) for k in class1_keys],
        "class1_sizes": {str(k): len(classes[k]) for k in class1_keys},
        "class27_keys": [list(k) for k in class27_keys],
        "class27_sizes": {str(k): len(classes[k]) for k in class27_keys},
    }
    (ROOT / "artifacts" / "e8_dotpair_class_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote artifacts/e8_dotpair_class_summary.json")


if __name__ == "__main__":
    main()
