# TOE: Holonomy-induced line polarization and hidden A5 (Feb 27, 2026)

This bundle is a **novel structural extraction** from the SRG(36) face-triangle decomposition and the canonical
“back-edge” Z2 holonomy cochain (as in `compute_srg36_holonomy.py`).

## Inputs used (from your existing bundles)

- `TOE_E6pair_SRG_triangle_decomp_v01_20260227`
  - `e6pair_srg_adj_36x36.npy`
  - `triangle_decomposition_120_blocks.json`
  - `w33_line_to_e6pair_triangles.json`
- `TOE_edge_to_oriented_rootpairs_v01_20260227`
  - `edge_to_oriented_rootpair_triple.json`

## Construction (canonical; no hand choices)

1. Each chosen face triangle (one of the 120 blocks) has **two oriented lifts** coming from the W33-edge → oriented-rootpair triple map.
2. We choose a canonical orientation per face by **lexicographically minimal cyclic rotation** of its lift.
3. This induces a global directed “tail” on each SRG edge and a Z2 1-cochain `c(e)`.
4. For every SRG triangle, define holonomy `hol(tri) = (# back-edges) mod 2`.

This reproduces the known counts:

- total SRG triangles: 1200  
- chosen faces: 120 (all have hol=1)  
- non-face triangles with hol=1: **240**  
- non-face triangles with hol=0: 840  

## New object 1: the **40 special faces** (one per W33 line)

For any SRG triangle `t=(i,j,k)`, define its **image face**:

`f(t) := { third(i,j), third(i,k), third(j,k) }`

where `third(u,v)` is the unique third vertex of the chosen face containing edge `{u,v}`.

Now count, for each chosen face F, how many **odd non-face** triangles t satisfy `f(t)=F`.

Result:

- Exactly **40** faces get **6** odd preimages.
- The other **80** faces get **0** odd preimages.

Using `w33_line_to_e6pair_triangles.json`, those 40 faces are **exactly one triangle block per W33 line**.

## New object 2: a **6-regular directed graph on the 40 W33 lines**

Let the vertices be the 40 W33 lines (line_id 0..39).

For each odd non-face SRG triangle `t`, define:

- `tail_line := line_id( f(t) )`  (the special face chosen for that line)
- Among the three edge-faces `{i,j,third(i,j)}`, `{i,k,third(i,k)}`, `{j,k,third(j,k)}`, **exactly one** is special.
  Let that special face be `F_edge`.
- `head_line := line_id(F_edge)`.

This yields a directed edge `tail_line -> head_line`.

**Result:**
- Directed edges: **240**
- Every line has outdegree = indegree = **6**
- The underlying undirected graph has 120 edges and splits into **two connected components**:
  - a 30-vertex component
  - a 10-vertex component

## New object 3: the 10-component is **L(K5)**, and the stabilizer is **A5**

The 10-vertex component is isomorphic to the **line graph of K5** (equivalently, the complement of the Petersen graph).

Inside the PSp(4,3) action on W33 lines induced from your Sp(4,3) matrices, the subgroup preserving the full
holonomy-induced line-digraph has order **60**, and via the L(K5) identification its action is by **even permutations**
on the 5 underlying vertices — i.e. **A5**.

This is a clean “icosahedral/A5” symmetry **appearing canonically** from the holonomy construction.

## Files in this bundle

- `line_digraph_edges_240.csv`  
  The 240 odd non-face triangles as directed edges between W33 lines.
- `line_undirected_edges_120.csv`  
  Undirected version of the line adjacency.
- `line_components.json`  
  Component split (30 + 10) with the explicit line_id lists.
- `comp10_isomorphism_to_LK5.json`  
  Explicit isomorphism from the 10 component’s line_ids to edges of K5.
- `stabilizer_A5_generators.json`  
  Two permutations on 40 line_ids generating the order-60 stabilizer inside PSp(4,3).
- `stabilizer_A5_induced_on_K5_vertices.json`  
  The induced even permutations on the 5 K5 vertices.

## Why this matters for the TOE weld

This gives a **brand new, sharply-structured “A5 spine”** living inside your SRG36 ↔ W33 ↔ (Sp/PSp) transport story:

- It is extracted from the same holonomy/cocycle machinery that produces the central Z2 extension (Sp vs PSp).
- It produces a rigid, canonical 40-object structure with a nontrivial stabilizer (A5) and a recognizable K5 shadow.
- A5/icosahedral symmetry is a well-known portal into E8 via icosians — this looks like the finite-combinatorial
  “projection” of that mechanism inside your W33 transport data.

Next obvious step: use this A5/K5 structure to **seed a canonical labeling** on the octonion 480 orbit (and then weld the 480s
by conjugating the corresponding permutation representations).

## Octonion-side search (new)

A companion script has been added to this bundle which searches the full
signed-permutation group on seven imaginary units for subgroups isomorphic
to **A₅** whose action on the 480 octonion multiplication tables produces
an orbit fingerprint of \(6\times60 + 6\times20\).  This mirrors the
holonomy-induced A₅ discovered on the W33 line graph and provides the
necessary conjugacy candidate for the 480‑weld.

Run the search with:

```sh
python recompute_line_polarization_A5.py --search-octonion \
    [--max-g N] [--max-h M] [--seed S] [--verbose]
```

The script will write `octonion_A5_search_results.json` and package the
findings into a new bundle `TOE_octonion_A5_search_v01_20260227_bundle.zip`.

The bundle contains the search results, the script itself, and a short
README describing the output.
