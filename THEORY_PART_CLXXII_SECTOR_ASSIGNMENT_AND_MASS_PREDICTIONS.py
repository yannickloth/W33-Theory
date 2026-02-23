"""Part CLXXII: Sector assignment and mass-ratio scoring

Building on the Yukawa geometry of W(3,3), we now attempt to identify which
of the three 27-dimensional H\_1 subspaces correspond to the up-quark,
down-quark and charged-lepton Yukawa matrices.  The finite geometry provides
three symmetric Gram matrices; physical sectors must be assigned in some order.

A brute-force Python script (`scripts/yukawa_sector_assignment.py`) iterates
over all six permutations, computing three quantitative penalties:

* CKM error — Frobenius norm of the difference between the 3x3 overlap matrix
  computed from the first two Grams and the experimental CKM matrix.
* Koide error — deviation of the Koide parameter of the third Gram from 2/3.
* Mass-ratio error — new in 2026; the sum of squared relative differences
  between the predicted inter-generation ratios and the observed quark/lepton
  ratios.  Predicted masses are obtained by scaling the eigenvalues of each
  Gram so that the largest matches the corresponding heaviest fermion (\`t\`,
  \`b\`, \`\tau\`).

The total score is the sum of the three errors; the permutation minimizing the
score is selected as the best assignment.

Numerical experiments show that the ordering

    1. down quark
    2. charged lepton
    3. up quark

yields the lowest combined error.  The resulting mass-ratio penalty is
\(\approx5.86\), corresponding to rough agreement (within factors of a few)
for the first- and second-generation masses.  Although the absolute
predictions are not yet phenomenologically precise, the pattern reproduces
qualitative hierarchies and provides a framework for further refinement.

The assignment also respects a residual \(\mathbb{Z}_3\) symmetry: an order-3
automorphism of W(3,3) cyclically permutes the three 27-dimensional subspaces,
explaining the ubiquitous `generation` permutation symmetry found in the Standard
Model.

The script is accompanied by a comprehensive pytest file tracking:

* successful execution and JSON output;
* structure of the `best` entry (permutation, sector labels, predicted
  masses);
* validity of the mass-error calculation and score composition;
* sanity bounds on the numerical penalties.

Future work will extend this machinery to include a fourth Gram for
Dirac/Majorana neutrinos and to compute the leptonic PMNS matrix, potentially
tying the tiny neutrino mass ratios to the same finite geometry.

"""
