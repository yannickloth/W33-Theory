# TOE duad algebra v05 (PSp(4,3) / rank-5 Gelfand pair)

This bundle is **fully self-contained**: it reconstructs the symplectic generalized quadrangle **W(3,3)** over **F3**, builds the 40 lines, the **120 duads** (perfect matchings per line), constructs **PSp(4,3)** as the induced projective symplectic action, and then **solves the full Bose–Mesner algebra** of the resulting rank-5 association scheme.

## Objects
- 40 points = projective points of F3^4 (canonical reps in `W33_points_projective_reps.json`)
- 40 lines = 2D totally isotropic subspaces (each gives a K4) in `W33_lines_40.json`
- 120 duads = 3 perfect matchings per line in `W33_duads_120.json`

## Group
Two explicit symplectic generators (4×4 matrices mod 3) are in:
- `sp43_symplectic_generators_matrices_mod3.json`

These generate **Sp(4,3)**; the induced projective permutation group on points has order **25920**, i.e. **PSp(4,3)**.

## Rank-5 association scheme on 120 duads
Stabilizer of a base duad has order 216 and its orbits on duads have sizes:

> 1, 2, 27, 36, 54

The full pair-relation matrix R (values 0..4) is stored as:
- `relation_matrix_R_120x120.npy`

## Solved algebra
Intersection numbers p_{ij}^k (A_i A_j = Σ_k p_{ij}^k A_k) are in:
- `intersection_numbers_pijk.json`

Eigenmatrices:
- `eigenmatrix_P.json` (common eigenvalues of A_i)
- `dual_eigenmatrix_Q.json`

Primitive idempotents E_r expressed in the adjacency basis are in:
- `primitive_idempotents_coeffs.json`

## Conjugacy classes + 5 spherical irreps
We compute the conjugacy classes of PSp(4,3) (20 classes total) and output the
character values for the **five multiplicity-free constituents** of the 120-duad permutation module (dims 1,20,15,24,60):

- `conjugacy_classes_spherical_characters.csv`

These five characters come from traces tr(E_r P(g)) using only relation-counts
c_i(g)=|{x : R(x,gx)=i}| and the dual eigenmatrix Q.

## Reproduce
Run `rebuild_all.py` to regenerate everything from scratch.
