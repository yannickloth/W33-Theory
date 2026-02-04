#!/usr/bin/env sage
"""
Compute the automorphism group of the W33 graph (SRG(40,12,2,4)) via its symplectic model,
and extract the stabilizer of a point.

Goal: independently verify the ubiquitous number
  |Aut(W33)| = 51840  and  |Stab(point)| = 1296 = 51840/40.

Writes:
  artifacts/sage_w33_point_stabilizer_structure.json
"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "sage_w33_point_stabilizer_structure.json"


def normalize(v):
    # normalize projective point so first nonzero coordinate becomes 1
    for i in range(4):
        if v[i] != 0:
            return tuple((v[j] / v[i]) for j in range(4))
    raise ValueError("zero vector")


def symp(u, v):
    # standard symplectic form on F3^4, in block form (x1,x2,y1,y2)
    # <(x,y),(x',y')> = x·y' - y·x'
    return u[0] * v[2] + u[1] * v[3] - u[2] * v[0] - u[3] * v[1]


def main():
    F = GF(3)
    # projective points in PG(3,3): (3^4-1)/(3-1)=40
    pts = {}
    for a in F:
        for b in F:
            for c in F:
                for d in F:
                    if (a, b, c, d) == (0, 0, 0, 0):
                        continue
                    v = normalize((a, b, c, d))
                    pts[v] = 1
    pts = sorted(pts.keys())
    if len(pts) != 40:
        raise RuntimeError("Expected 40 projective points")

    idx = {p: i for i, p in enumerate(pts)}

    # W33 adjacency: orthogonality w.r.t. symplectic form (collinear in W(3,3))
    G = Graph()
    G.add_vertices(range(40))
    for i in range(40):
        for j in range(i + 1, 40):
            if symp(pts[i], pts[j]) == 0:
                G.add_edge(i, j)

    # Check SRG parameters quickly.
    degs = sorted(set(G.degree()))
    if degs != [12]:
        raise RuntimeError("Expected regular degree 12")

    aut = G.automorphism_group()
    order = int(aut.order())

    # Pick the first point (projectively (1,0,0,0)).
    v0 = idx[normalize((F(1), F(0), F(0), F(0)))]
    stab = aut.stabilizer(v0)

    out = {
        "status": "ok",
        "counts": {"vertices": int(40), "degree": int(12)},
        "orders": {
            "aut_w33": int(order),
            "stab_point": int(stab.order()),
            "index": int(int(order) // int(stab.order())),
        },
        "structure": {
            "aut_w33": str(aut.structure_description()),
            "stab_point": str(stab.structure_description()),
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("status=ok wrote", OUT)


if __name__ == "__main__":
    main()
