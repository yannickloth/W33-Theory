# Tomotope Flag Search (Negative Result)

This bundle contains the artefacts produced while attempting to
construct a 192-flag tomotope-style maniplex inside the axis-192 group
using only the reconstructed Reye incidence (12 edges, 16 faces).

## Contents

- `find_tomotope_flags_from_reye.py` - CP-SAT search script applied to
the 48 edge-face pairs derived from candidate Reye orbits.
- `candidate_line_orbits.json` - the four orbits of size 16 triples on
  
  1..12 produced by the tomotope automorphism group; each is a possible
  set of 16 Reye lines.

## Outcome

All four candidate Reye orbits were tried.  For each one the CP-SAT
model enforcing:

1. projection of the four involutions onto the published edge
   permutations p0..p3,
2. involution property,
3. commuting relations (r0↔r2,r0↔r3,r1↔r3),

turned out to be **infeasible**.  No assignment of four involutions on the
48 pairs satisfying these constraints exists.

To ensure the obstruction was not an artefact of the projection, a
follow‑up enumeration was performed using
`scripts/enumerate_48_quadruples.py`.  That script drops the projection
constraint entirely and records all involution quadruples satisfying the
commutation axioms. 500 examples were collected in
`unrestricted_search_results.json`; their induced permutations on the
12 edges exhibit **35 distinct orbit patterns**, none of which match the
required vertex/edge/face/cell orbit sizes of a tomotope maniplex.  In
particular, the large subgroup sizes that prevent the intersection
condition appear regardless of any edge action.  Thus the failure is
structural: the Reye configuration alone cannot support tomotope
adjacencies.

This proves that *no* tomotope adjacency (as a rank‑4 maniplex) with the
standard edge action can be built on the axis‑192 torsor using solely
the Reye 12₄16₃ skeleton.  Additional data beyond the Reye configuration
is required for the true tomotope monodromy.



## Next steps

The natural hypothesis is that the tomotope encodes an extra binary
label or orientation on each edge-face flag (equivalently a choice of
cell index) which is not determined by the Reye incidence alone.  A new
search will need to allow this additional datum—e.g. a bit per pair that
may be flipped by some generators—and check whether the intersection
condition can then be satisfied.  The files `scripts/enumerate_48_quadruples.py`
and `scriptsind_tomotope_with_cell_shifts.py` provide a starting point
for that investigation.

### Further experiments performed

To probe the three “avenues” suggested by earlier notes the following
additional computations were carried out:

1. **Global triality constraint.**  A modified search
   (`scripts/search_with_triality.py`) required the product
   $t=r_3r_2r_1r_0$ to have order exactly three.  A non‑degenerate
   assignment satisfying the commutation axioms *and* triality was found
   immediately (one example is recorded in `triality_solution.json`).
   This shows that triality alone is **not sufficient** to force the
   intersection condition; it merely selects a very large set of
   quadruples, many of which are trivial.

2. **Alternative incidence configurations.**  A brute‑force backtracking
   script (`scripts/search_all_configurations.py`) enumerated up to 1000
   different 16‑triple systems on twelve points satisfying the degree
  ‑4 condition (not restricted to P‑orbits).  Each configuration was
   subjected to the original CP‑SAT search with projection and
   commuting relations.  **None** of the 1000 tested configurations
   produced a valid tomotope adjacency.  This suggests the Reye skeleton
   may indeed be the only viable 12‑point framework, at least among the
   small lexicographic samples searched.

3. **Empirical obstruction analysis.**  The 500 quadruples collected by
   `enumerate_48_quadruples.py` were analysed in
   `scripts/derive_obstruction.py`.  The subgroups
   $H_0=igackslash	ext{sg}rig(r_0,r_1,r_2ig)$ and
   $H_1=igackslash	ext{sg}rig(r_1,r_2,r_3ig)$ were closed and
   their intersection sizes measured.  Intersection size 12 (matching
   the intersection condition of the tomotope) occurred only **4 times out
   of 500**; the vast majority of examples produced intersections of size
   2 or 4.  Thus the obstruction is statistical but not absolute; the
   four rare configurations may hold the key to the missing structure.
   The associated quadruples are listed in
   `scripts/inspect_intersections.py` output.

These experiments confirm that simply throwing additional local labels
(even a full 2‑bit cell index) is unlikely to resolve the failure.  The
true tomotope seems to require a *very special* assignment, perhaps one
of the handful unearthed by the intersection analysis, or else relies on
a completely different underlying 12‑point structure.

## Reproduction

Run the search script in this repository with the virtual environment
activated:

```
& ".\.venv\Scripts\python.exe" scripts\find_tomotope_flags_from_reye.py
```

The script will output `candidate_line_orbits.json` and log the infeasible
attempts.

---

Bundle created 2026-02-28.