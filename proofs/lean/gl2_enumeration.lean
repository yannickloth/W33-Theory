import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
import Mathlib.Data.Matrix.Basic
import Mathlib.Init.Data.List
import Mathlib.Data.List.Basic

/-!
Enumerative GL(2,3) utilities: build all 2x2 matrices over F3 and select the
involutions with determinant `2`. This sets up the brute-force conjugacy proof
strategy in a small finite domain.
-/

open GL2F3

namespace GL2F3Enumeration

/-- All elements of `ZMod 3` expressed as a list literal. -/
def all_vals : List (ZMod 3) := [0, 1, 2]

/-- Construct a 2x2 matrix from four entries (row-major): [[a,b],[c,d]]. -/
def mk2x2 (a b c d : ZMod 3) : Matrix (Fin 2) (Fin 2) (ZMod 3) :=
  fun i j =>
    if i = 0 ∧ j = 0 then a
    else if i = 0 ∧ j = 1 then b
    else if i = 1 ∧ j = 0 then c
    else d

/-- All 2x2 matrices over F3 (there are 3^4 = 81 of them). -/
def all_matrices : List (Matrix (Fin 2) (Fin 2) (ZMod 3)) :=
  all_vals.bind fun a =>
    all_vals.bind fun b =>
      all_vals.bind fun c =>
        all_vals.map fun d => mk2x2 a b c d

/-- Predicate: matrix is an involution (A^2 = I). -/
def is_involution (M : Matrix (Fin 2) (Fin 2) (ZMod 3)) : Prop :=
  M ⬝ M = 1

/-- Predicate: determinant equals 2 (i.e., `-1` mod 3). -/
def det_is_two (M : Matrix (Fin 2) (Fin 2) (ZMod 3)) : Prop :=
  M.det = (2 : ZMod 3)

/-- Candidates for conjugacy: involutions with determinant 2. -/
def candidates : List (Matrix (Fin 2) (Fin 2) (ZMod 3)) :=
  all_matrices.filter fun M => is_involution M && det_is_two M

/-- Sanity: the diagonal `diag(-1,1)` is one such candidate. -/
theorem A_diag_in_candidates : GL2F3.A_diag_mat ∈ candidates := by
  simp [candidates, candidates.filter, is_involution, det_is_two]
  -- The checks reduce to the previously proved facts
  simp [GL2F3.A_diag_mat_mul_self, GL2F3.A_diag_mat_det]

/-- Adjugate for a 2×2 matrix: [[a,b],[c,d]]^# = [[d,-b],[-c,a]]. -/
def adj2x2 (M : Matrix (Fin 2) (Fin 2) (ZMod 3)) : Matrix (Fin 2) (Fin 2) (ZMod 3) :=
  fun i j =>
    if i = 0 ∧ j = 0 then M 1 1
    else if i = 0 ∧ j = 1 then -M 0 1
    else if i = 1 ∧ j = 0 then -M 1 0
    else M 0 0

/-- Explicit 2×2 inverse formula in F3: inv(M) = det(M) * adj(M).
    In F3 every nonzero determinant is self-inverse (1^-1 = 1, 2^-1 = 2), so
    multiplying the adjugate by `M.det` yields the inverse when `M.det ≠ 0`. -/
def inv2x2 (M : Matrix (Fin 2) (Fin 2) (ZMod 3)) : Matrix (Fin 2) (Fin 2) (ZMod 3) :=
  (M.det) • (adj2x2 M)

/-- For 2×2 matrices the adjugate satisfies `M * adj(M) = det(M) * I`. -/
theorem mul_adj2x2_eq_det_mul_one (M : Matrix (Fin 2) (Fin 2) (ZMod 3)) :
    M ⬝ adj2x2 M = (M.det) • 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [adj2x2, Matrix.mul_apply]

/-- Dually, `adj(M) * M = det(M) * I`. -/
theorem adj2x2_mul_eq_det_mul_one (M : Matrix (Fin 2) (Fin 2) (ZMod 3)) :
    adj2x2 M ⬝ M = (M.det) • 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [adj2x2, Matrix.mul_apply]

/-- Nonzero elements of `ZMod 3` square to `1`. -/
theorem nonzero_square_one (m : ZMod 3) (h : m ≠ 0) : m * m = 1 := by
  fin_cases m <;> simp at *
  have : (m : Int) ≠ 0 := by simp_all
  -- the two remaining cases (1 and 2) square to 1 in ZMod 3
  fin_cases m <;> decide

/-- Left inverse property for `inv2x2` on invertible matrices. -/
theorem left_inv2x2 (M : Matrix (Fin 2) (Fin 2) (ZMod 3)) (h : M.det ≠ 0) :
    M ⬝ inv2x2 M = 1 := by
  calc
    M ⬝ inv2x2 M = M ⬝ ((M.det) • adj2x2 M) := by simp [inv2x2]
    _ = (M.det) • (M ⬝ adj2x2 M) := by simp [Matrix.mul_smul]
    _ = (M.det) • ((M.det) • 1) := by simp [mul_adj2x2_eq_det_mul_one]
    _ = ((M.det * M.det : ZMod 3)) • 1 := by simp [ZMod.smul_smul]
  have d2 : M.det * M.det = 1 := nonzero_square_one M.det h
  simpa [d2] using (by simp [ZMod.smul_eq_mul])

/-- Right inverse property for `inv2x2` on invertible matrices. -/
theorem right_inv2x2 (M : Matrix (Fin 2) (Fin 2) (ZMod 3)) (h : M.det ≠ 0) :
    inv2x2 M ⬝ M = 1 := by
  calc
    inv2x2 M ⬝ M = ((M.det) • adj2x2 M) ⬝ M := by simp [inv2x2]
    _ = (M.det) • (adj2x2 M ⬝ M) := by simp [Matrix.smul_mul]
    _ = (M.det) • ((M.det) • 1) := by simp [adj2x2_mul_eq_det_mul_one]
    _ = ((M.det * M.det : ZMod 3)) • 1 := by simp [ZMod.smul_smul]
  have d2 : M.det * M.det = 1 := nonzero_square_one M.det h
  simpa [d2] using (by simp [ZMod.smul_eq_mul])

/-- List of invertible matrices (GL(2,3) concrete list). -/
def invertible_matrices : List (Matrix (Fin 2) (Fin 2) (ZMod 3)) :=
  all_matrices.filter fun M => M.det ≠ 0

/-- Enumerative conjugacy result: every involution with det = 2 is conjugate to
    `diag(-1,1)` by some invertible matrix in `GL(2,3)`. We provide explicit
    constructive witnesses (conjugator `P`) for each finite case discovered
    by enumeration. -/
theorem candidates_conjugate :
    ∀ M ∈ candidates, ∃ P ∈ invertible_matrices, P ⬝ M ⬝ inv2x2 P = GL2F3.A_diag_mat := by
  intro M hM
  -- The list of candidate matrices is finite; case-split on the concrete shape
  -- (these are the twelve involutions with determinant 2 found by enumeration).
  have cases :
      M = mk2x2 0 1 1 0
        ∨ M = mk2x2 0 2 2 0
        ∨ M = mk2x2 1 0 0 2
        ∨ M = mk2x2 1 0 1 2
        ∨ M = mk2x2 1 0 2 2
        ∨ M = mk2x2 1 1 0 2
        ∨ M = mk2x2 1 2 0 2
        ∨ M = mk2x2 2 0 0 1
        ∨ M = mk2x2 2 0 1 1
        ∨ M = mk2x2 2 0 2 1
        ∨ M = mk2x2 2 1 0 1
        ∨ M = mk2x2 2 2 0 1 := by
    dec_trivial
  rcases cases with
  | Or.inl h =>
    let P := mk2x2 1 2 1 1
    refine Exists.intro P (And.intro (by simp [invertible_matrices, all_matrices]; simp [P]; dec_trivial) ?_)
    -- check conjugacy by computation
    simp [P, h, inv2x2, adj2x2, Matrix.mul_apply]; dec_trivial
  | Or.inr (Or.inl h) =>
    let P := mk2x2 1 1 1 2
    refine Exists.intro P (And.intro (by simp [invertible_matrices, all_matrices]; simp [P]; dec_trivial) ?_)
    simp [P, h, inv2x2, adj2x2, Matrix.mul_apply]; dec_trivial
  | Or.inr (Or.inr (Or.inl h)) =>
    let P := mk2x2 0 1 1 0
    refine Exists.intro P (And.intro (by simp [invertible_matrices, all_matrices]; simp [P]; dec_trivial) ?_)
    simp [P, h, inv2x2, adj2x2, Matrix.mul_apply]; dec_trivial
  | Or.inr (Or.inr (Or.inr (Or.inl h))) =>
    let P := mk2x2 1 1 1 0
    refine Exists.intro P (And.intro (by simp [invertible_matrices, all_matrices]; simp [P]; dec_trivial) ?_)
    simp [P, h, inv2x2, adj2x2, Matrix.mul_apply]; dec_trivial
  | Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))) =>
    let P := mk2x2 1 2 1 0
    refine Exists.intro P (And.intro (by simp [invertible_matrices, all_matrices]; simp [P]; dec_trivial) ?_)
    simp [P, h, inv2x2, adj2x2, Matrix.mul_apply]; dec_trivial
  | Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h)))))) =>
    let P := mk2x2 0 1 1 2
    refine Exists.intro P (And.intro (by simp [invertible_matrices, all_matrices]; simp [P]; dec_trivial) ?_)
    simp [P, h, inv2x2, adj2x2, Matrix.mul_apply]; dec_trivial
  | Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))))) =>
    let P := mk2x2 0 1 1 1
    refine Exists.intro P (And.intro (by simp [invertible_matrices, all_matrices]; simp [P]; dec_trivial) ?_)
    simp [P, h, inv2x2, adj2x2, Matrix.mul_apply]; dec_trivial
  | Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))))))) =>
    let P := mk2x2 1 0 0 1
    refine Exists.intro P (And.intro (by simp [invertible_matrices, all_matrices]; simp [P]; dec_trivial) ?_)
    simp [P, h, inv2x2, adj2x2, Matrix.mul_apply]; dec_trivial
  | Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h)))))))))) =>
    let P := mk2x2 1 0 1 2
    refine Exists.intro P (And.intro (by simp [invertible_matrices, all_matrices]; simp [P]; dec_trivial) ?_)
    simp [P, h, inv2x2, adj2x2, Matrix.mul_apply]; dec_trivial
  | Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))))))))) =>
    let P := mk2x2 1 0 1 1
    refine Exists.intro P (And.intro (by simp [invertible_matrices, all_matrices]; simp [P]; dec_trivial) ?_)
    simp [P, h, inv2x2, adj2x2, Matrix.mul_apply]; dec_trivial
  | Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr h)))))))))))) =>
    let P := mk2x2 1 1 0 1
    refine Exists.intro P (And.intro (by simp [invertible_matrices, all_matrices]; simp [P]; dec_trivial) ?_)
    simp [P, h, inv2x2, adj2x2, Matrix.mul_apply]; dec_trivial
  | Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))))))))))) =>
    let P := mk2x2 1 2 0 1
    refine Exists.intro P (And.intro (by simp [invertible_matrices, all_matrices]; simp [P]; dec_trivial) ?_)
    simp [P, h, inv2x2, adj2x2, Matrix.mul_apply]; dec_trivial

end GL2F3Enumeration
