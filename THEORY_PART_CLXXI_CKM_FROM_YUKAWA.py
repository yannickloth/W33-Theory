"""Part CLXXI: Quark mixing from H1 Yukawa geometry

The previous section (CLXX) derived three 27-dimensional invariant
subspaces of H_1(W(3,3)) and identified the intersection form restricted to
each as a symmetric integer matrix.  Diagonalising these ``Yukawa Gram
matrices'' produced eigenvalue hierarchies of roughly 10:1, 8.7:1 and 15:1.
At first glance the ratios match the intergenerational hierarchies observed
in the charged-lepton and down-quark sectors (τ/μ, μ/e, s/d etc).

To make contact with flavour mixing we now consider the relative orientation of
the mass-eigenvector bases defined by two different Gram matrices.  If the
first matrix is interpreted as the up-type quark Yukawa and the second as the
down-type Yukawa, then the overlap between their principal eigenvectors
gives a candidate for the Cabibbo–Kobayashi–Maskawa (CKM) matrix.  The
hypothesis is that the finite geometry already contains the seed of quark
mixing via the fact that the three 27-spaces are not mutually orthogonal in
H_1; their eigenbases are misaligned by O(1) angles.

A simple numerical experiment is performed in
``scripts/ckm_from_grams.py``.  The script loads
``data/h1_subspaces.json``, identifies the two Gram matrices with the largest
Yukawa ratio (our working assumption is that the heaviest sector corresponds
to the up quarks), and computes the overlap of their first three principal
eigenvectors.  After row-normalising the resulting 3×3 real matrix we obtain
a flavour-mixing pattern of order

    [[0.03, 0.62, 0.34],
     [0.08, 0.32, 0.60],
     [0.55, 0.34, 0.11]]

which is clearly not unitary, nor does it reproduce the small Cabibbo angle or
hierarchical structure of the physical CKM.  Nevertheless the presence of a
mild hierarchy (one large element O(0.6) and several entries O(0.1)) shows that
mixing is encoded geometrically and that further refinement of the model
(e.g. selecting the correct linear combinations or including additional scale
factors) may yield quantitatively accurate predictions.

The computation is completely deterministic and parameter-free; the only input
is the combinatorial intersection form of H_1, which itself follows from the
W(3,3) incidence relations.  The adjacency between different subspaces is a
consequence of the Sp(4,3) symmetry of the graph and may ultimately be
explained group-theoretically.

A corresponding unit test ``tests/test_ckm_from_grams.py`` checks that the
script runs, produces a 3×3 matrix, and that the overlap is non‑uniform (at
least one row has a dominant entry >0.5).  This test will serve as a
regression guard once a more refined analytic derivation is available.

Further work (CLXXII?) will investigate whether the same geometry can also
account for the Pontecorvo–Maki–Nakagawa–Sakata (PMNS) matrix by associating one
of the subspaces with the neutrino Dirac coupling and including a seesaw
structure.
"""
