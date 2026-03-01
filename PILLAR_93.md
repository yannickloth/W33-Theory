# Pillar 93: Constructing the Regular Subgroup N

With the direct‑product structure of the tomotope symmetry fully established
(Pillars 90–92), the only remaining piece of the matched‑pair combinatorics
is an explicit description of the regular subgroup \(N\subset\Gamma\).
For the reader this completes the picture:

* \(\Gamma\) acts transitively on the 192 flags.
* \(P_0\cong H\) is the external automorphism set of order 96 which
  commutes with \(\Gamma\).
* \(N\) is the unique subgroup of \(\Gamma\) of order 192 which acts
  sharply transitively on the flags (a regular subgroup).

The script `THEORY_PART_CXCIII_FIND_N.py` performs a random search inside
\(\Gamma\) to locate such a subgroup.  It then verifies closure, computes
its element‑order distribution, and writes two data files:

* `N_subgroup.json` – list of the 192 permutations comprising \(N\).
* `N_flag_map.json` – a bijection between flags and elements of \(N\);
  the element associated to flag \(k\) is the unique \(n\in N\) with
  \(n(0)=k\).

The order distribution of \(N\) is
```
Counter({4:84, 2:43, 3:32, 6:32, 1:1})
```
confirming the Sylow‑2 subgroups of order 64 and the presence of exactly one
identity element.  This matches Pillar 85 T5 and provides an explicit model
for the triality action in the normal‑Sylow picture.

The follow‑up tests verify that the found subgroup is indeed regular and a
subgroup, and that the bijection to flags is complete.

## Consequences and applications

- The element of \(N\) corresponding to a flag gives a canonical labelling
  of flags by group elements; this labelling was tacitly used in earlier
  arguments but is now explicit.
- Computations on \(\Gamma\) that depend only on the image of a single
  flag (e.g. checking connectivity, transport laws) can be reduced to
  running over \(N\) rather than the full 18 432 elements, a factor‑96
  reduction in brute‑force search.
- When constructing explicit isomorphisms between \(\Gamma\) and other
  groups, one may now identify the normal‑Sylow‑2 structure concretely.

## Further directions

The direct‑product structure proved in Pillar 92 tells us that any future
bundle whose analysis involves both monodromy and automorphism data can be
split: one may first analyse the \(\Gamma\)-part (e.g. transported edges) and
then append the commuting \(H\)-action afterwards.  This is particularly
helpful in the `S3_sheet` and `axis_block_twist` analyses, where the presence
of a triality phase could have interleaved with monodromy; knowing that the
phase generator commutes with every \(\Gamma\)-element allows us to treat it
as an independent gauge factor.

The explicit description of \(N\) also invites comparison with classical
maniplex theory.  Regular subgroups of transitive permutation groups are the
subject of much study; the web of conjugacy classes (65 classes in \(\Gamma\))
provides a rich dataset for exploring automorphism towers and triality
phenomena.  Extra literature on maniplexes (e.g. the works of Monson,
Pellicer, Schulte) often emphasises the role of regular subgroups; our
concretes offer a test case.

Finally, the bijection `N_flag_map.json` may be used to correlate the
Heisenberg quotient coordinates (Pillar 89) with group‑theoretic operations in
\(N\).  This sets the stage for embedding the whole package into larger
algebraic constructions such as Clifford algebras or Heisenberg extensions,
with \(N\) playing the role of a translation group and \(P_0\) the role of
outer automorphisms.
