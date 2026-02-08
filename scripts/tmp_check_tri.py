import json
from e8_embedding_group_theoretic import build_w33, generate_e8_roots

seed = json.load(open("checks/PART_CVII_e8_seed_e6_structural.json"))
mapping = {int(it['edge_index']): int(it['root_index']) for it in seed['seed_edges']}

n, vertices, adj, edges = build_w33()
pair_to_edge = {tuple(sorted(edges[i])): i for i in range(len(edges))}
triangles = []
for a in range(n):
    for b in adj[a]:
        if b <= a: continue
        for c in adj[b]:
            if c <= b: continue
            if a in adj[c]:
                e_ab = pair_to_edge[(a,b)]
                e_bc = pair_to_edge[(b,c)]
                e_ac = pair_to_edge[(a,c)]
                triangles.append((e_ab,e_bc,e_ac))

roots = generate_e8_roots()
tri_ok = 0
for (e1,e2,e3) in triangles:
    r1 = roots[mapping[e1]]
    r2 = roots[mapping[e2]]
    r3 = roots[mapping[e3]]
    ok = all(int(r1[i] + r2[i]) == int(r3[i]) for i in range(8))
    if ok:
        tri_ok += 1

print(f"Triangles satisfied: {tri_ok}/{len(triangles)} ({tri_ok/len(triangles):.3f})")
