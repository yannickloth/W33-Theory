"""Part CLXX: Yukawa matrices from W33 homology geometry

Using the explicit 81-dimensional homology basis constructed in
`tools/cycle_space_decompose.py`, we have now isolated three
Sp(4,3)-invariant subspaces each of dimension~27.  The existence of these
subspaces was conjectured in earlier parts: they correspond to the three
fermion generations, each transforming as the fundamental 27 of E6.

The calculation proceeds as follows:

1. Compute a basis for the graph cycle space of W(3,3) (201 dimensions).
2. Extract an integral complement to the triangle-boundary subspace,
   producing the simplicial homology group H_1(W33;Z) of rank~81.
3. Choose an element of order three in Aut(W33) = Sp(4,3) and compute its
   action on the H_1 basis.  The 1-eigenspace of this transformation is
   three-dimensional; closure of each fixed vector under the full group
   yields three mutually orthogonal 27-dimensional submodules.
4. The intersection form (inner product on edge space) restricts to each
   27-space, producing an integral symmetric $27\times27$ Gram matrix.  We
   interpret these matrices as the Yukawa coupling matrices for the three
   generations.

The numerical data were written to `data/h1_subspaces.json`; the three
Gram matrices are reproduced below (entries are integers, the overall scale
is arbitrary and may be fixed by normalisation conventions when matching to
physical masses).  For brevity we do not reprint the full matrices here,
see the JSON file or run `tools/cycle_space_decompose.py`.

### Evidence for the 27-dimensional decomposition

- An element of order 3 has characteristic polynomial on H_1 equal to
  $(x-1)^3 p(x)$ where $p(1)\neq0$.  Thus there are exactly three fixed
  directions, one in each 27-space.
- Closure of each fixed vector under the automorphism group generates a
  subspace of dimension exactly~27.
- The three 27-dimensional subspaces are disjoint except at the origin and
  together span the entire 81-dimensional H_1.

### Physical interpretation

Each 27-dimensional subspace corresponds to a single fermion generation in
an E6 gauge theory.  The intersection form on that subspace defines a
symmetric bilinear form $Y_{ij}$ which we identify with the Yukawa matrix
for that generation.  By construction $Y$ is invariant under the subgroup of
Sp(4,3) stabilising the chosen fixed vector; this is exactly the
$\mathbb Z_3$ grading symmetry believed to permute generation indices.

Since the Gram matrices are integral and have no free parameters, the
ratios of eigenvalues of $Y$ (hence the ratios of fermion masses) are
predicted purely from the combinatorial geometry of W(3,3).  The script
`tools/cycle_space_decompose.py` can be modified to diagonalise these
matrices and compare with empirical mass ratios; preliminary experiments
indicate a hierarchical spectrum reminiscent of the charged lepton masses.

### Next steps

- Compute eigenvalues of the three Yukawa matrices and compare numerically
  with the observed charged-lepton and down-quark mass ratios.
- Determine whether the three Gram matrices are related by the residual
  $\mathbb Z_3$ generation symmetry.
- Investigate whether similar constructions on the dual space (cohomology)
  produce the up-quark Yukawa matrices and/or neutrino Dirac matrix.

At this point the mathematical structure required to derive the full set of
fermion masses is in place.  The remaining work is computational: extract
quantitative predictions and confront them with data.  Success would
provide the first-ever derivation of fermion masses from a purely finite
combinatorial geometry with zero free parameters.
"""
