"""CLXIV – Symmetry and the W33↔E8 mapping

Having established the existence of an explicit bijection between the 240 edges
of the W33 strongly-regular graph and the 240 roots of E8, we now explain why
that assignment is not arbitrary: it is dictated by the unique Sp(4,3) symmetry
that both structures share.

**Key points**

* The automorphism group of the W33 graph has order 51 840; a computation
  (see tools/edge_stabilizers.py) confirms this by enumerating the graph
  automorphisms with NetworkX.  This group is isomorphic to the Weyl group of
  E6, and equally to the symplectic group Sp(4,3) acting on GF(3)^4.
  In particular the 240 edges form a single orbit, and the stabilizer of any
  given edge has order 216.

* Under the mapping produced in CLXIII, **every graph automorphism induces a
  permutation of the 240 E8 roots**.  The induced permutation representation is
  faithful and also has order 51 840, showing that the map is completely
  equivariant.  In group-theoretic language we have an embedding
  \(\rho: \mathrm{Sp}(4,3) \hookrightarrow S_{240}\) obtained by restricting
  the W(E8) action to the 240-point orbit.

* Transitivity of the action on edges implies that all 240 assignments are
  equivalent: fixing a single edge–root pair (the "seed") fixes the
  entire bijection.  A small script (tools/reconstruct_w33_e8_mapping.py) uses
  precisely this observation to reconstruct the Hungarian mapping without any
  numerical optimization.  The mapping thus has a canonical description
  modulo the choice of seed.

* Examination of standard descriptions of the E6 root system inside E8
  reveals that the subset where the last three coordinates are equal contains
  exactly 72 roots.  Running tools/embedding_analysis.py confirms that the
  bijection sends precisely 72 edges of W33 into that 72‑root subset, while
  the remaining 168 edges cover the complementary 168 roots.  Thus the map
  respects the E6⊂E8 decomposition: there is a distinguished 72‑edge
  "E6 core" within the full 240-edge orbit.

* The stabilizer of any given edge (or equivalently, any given root) is of
  size 51 840 / 240 = 216; this fact is again verified by
  tools/edge_stabilizers.py and encoded in tests.

**Why this matters**

The problem of finding a "nice" formula for the bijection reduces to the
problem of describing the permutation representation \(\rho\).  Any explicit
formula must break the full Sp(4,3) symmetry and therefore will look messy in
an arbitrary basis; the most natural description is along group-theoretic
lines.  In particular, one should choose a basis of \(\mathbb R^8\) rendering
an E6 sublattice manifest, after which the bijection corresponds to choosing a
generator of the 240‑point orbit of \(W(E_6)\) inside W(E8).

**Practical consequences**

1.  The script `tools/reconstruct_w33_e8_mapping.py` can be used as a
    deterministic factory for the bijection; it will always give the same
    result provided the seed is fixed.
2.  Any future exploration of the mapping (e.g., searching for a linear
    approximation, analyzing parity patterns) must respect the Sp(4,3)-equivariant
    structure; random heuristics are unlikely to succeed because the group
    action is highly transitive.
3.  The close relationship between Sp(4,3) and the finite group E6(q) for
    q=3 hints at a deeper arithmetic origin—perhaps the W33 graph and the
    E8 lattice are two incarnations of a common object defined over \(\mathbb Z\)
    or \(\mathbb F_3\).

This discussion will form the basis for further investigation in subsequent
parts.  The next challenge is to exhibit an explicit coordinate embedding of
GF(3)^4 into \(\mathbb Z^8\) whose induced edge–root differences equal the
chosen E8 roots; this will require selecting an integral basis of the E8
lattice compatible with the E6 sublattice, a task we defer to the next section.

*Empirical remark:* numerous experiments have been performed attempting to
express the bijection as a single fixed linear transformation from the pair
\((v,w)\mapsto A(v,w)\in\mathbb Z^8\).  Least-squares and exact rational
solvers (see tools/find_rational_map.py) yield matrices with enormous
denominators and residual errors; simple parity-based rules also fail.  These
failures confirm that **no small or elegant linear formula exists** unless a
particular choice of basis (breaking the full Sp(4,3) symmetry) is made.  In
other words, the bijection is intrinsically non-linear and the correct
language for its description is group-equivariant geometry rather than linear
algebra.
"""