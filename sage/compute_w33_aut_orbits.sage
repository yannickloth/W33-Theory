# Sage script to compute automorphism group orbits of W33 (SymplecticPolarGraph(4,3))
# Run with: sage -python sage/compute_w33_aut_orbits.sage

from sage.all import *

# Build PG(3,3) points (1D subspaces of GF(3)^4)
F = GF(3)
V = MatrixSpace(F, 4)
pts = []
rep = []
for a0 in F:
    for a1 in F:
        for a2 in F:
            for a3 in F:
                v = vector(F, [a0, a1, a2, a3])
                if v != 0:
                    pts.append(v)
# take representatives of projective points (first nonzero coordinate == 1)
proj = []
seen = set()
for v in pts:
    # normalized representative
    for i in range(4):
        if v[i] != 0:
            inv = 1 / v[i]
            nv = tuple([(inv * c) for c in v])
            break
    if nv not in seen:
        seen.add(nv)
        proj.append(vector(F, nv))

assert len(proj) == 40

# symplectic form J (4x4)
J = matrix(F, [[0,0,0,1],[0,0,1,0],[0,-1,0,0],[-1,0,0,0]])

# adjacency: u~v if u^T J v == 0 in F
G = Graph()
G.add_vertices(range(40))
for i in range(40):
    for j in range(i+1, 40):
        if (proj[i].transpose() * J * proj[j])[0] == 0:
            G.add_edge(i, j)

print('n_vertices', G.num_verts(), 'n_edges', G.num_edges())

# compute automorphism group and orbits
Aut = G.automorphism_group()
orbits = Aut.orbits()
print('automorphism group size:', Aut.order())
print('orbits:', orbits)

# Compare to proposed partition (V1-V16, V17-V26, V27, V28-V39, V40)
fermions = set(range(0,16))
exotics = set(range(16,26))
e6_sing = set([26])
gauge = set(range(27, 27+12))
dark = set([39])

part = [fermions, exotics, e6_sing, gauge, dark]

for i, orbit in enumerate(orbits):
    print('orbit', i, 'size', len(orbit), 'intersection sizes with partition:', [len(set(orbit) & grp) for grp in part])

# Save orbits to a file
import json
with open('checks/PART_CXI_aut_orbits_sage.json', 'w') as f:
    json.dump({'aut_order': Aut.order(), 'orbits': [sorted(list(o)) for o in orbits]}, f, indent=2)
print('Wrote checks/PART_CXI_aut_orbits_sage.json')
