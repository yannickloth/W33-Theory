# TOE Holonomy Report (Z3 flat / Z2 nontrivial)

This report is computed **purely from the repo artifacts**:

- W33 edge ↔ oriented E6-root-pair triple mapping (`edge_to_oriented_rootpair_triple.csv`)
- PSp(4,3) action on 240 W33 edges (10 generators, orders 3/4/2)
- Induced action on 120 edgepairs (= SRG triangles)

## Key algebraic finding

### 1) The 120 SRG triangles (edgepairs) carry a **pure Z2 transport** — Z3 collapses
For the induced action on 120 edgepairs, the transport labels lie in the triangle symmetry group D6.
Empirically:

- **rot_Z3 is identically 0** for every generator move on edgepairs.
- **flip_Z2 is nonzero on 184/1200 generator moves**.

So the Z3 rotation degree of freedom is **pure gauge at triangle-block level**, while a Z2 reflection cocycle survives.

See: `edgepair_transport_D6.csv`.

### 2) Generator-cycle holonomy is flat on edgepairs
For each generator, every edgepair cycle has holonomy (flip,rot)=(0,0).
See: `holonomy_cycles_edgepairs_by_generator.csv`.

### 3) First nontrivial holonomy appears in commutators (Z2 reflections)
Among commutators [g_i,g_j], the smallest clear nontrivial case is:

- **[g4,g5]** has fixed edgepairs which pick up **flip=1** (a reflection holonomy).

See: `commutator_cycle_holonomy_edgepairs.csv`.

### 4) Edge vs edgepair: the opposite edge always reflects the oriented triple
Inside each edgepair {e, e_opposite}:

- oriented triple on e_opposite is always **reflection** of the triple on e
- i.e. (flip,rot)=(1,0) for all 120 pairs.

See: `edgepair_internal_flip_stats.json`.

## Files

- `edgepair_transport_D6.csv` — edgepair-level transport (image, flip_Z2, rot_Z3)
- `holonomy_cycles_edges_by_generator.csv` — edge-level cycle holonomy stats
- `holonomy_cycles_edgepairs_by_generator.csv` — edgepair-level cycle holonomy stats
- `commutator_cycle_holonomy_edgepairs.csv` — commutator element cycle holonomies
- `sample_nontrivial_holonomy_elements.json` — short words with nontrivial Z2 holonomy on cycles
