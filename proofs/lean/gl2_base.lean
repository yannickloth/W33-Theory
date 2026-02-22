import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
import Mathlib.Data.Matrix.Basic
import Mathlib.Init.Data.List
import Mathlib.Data.List.Basic
import gl2_f3
import gl2_f3

/-!
GL(2,3) base definitions extracted so generated and hand-written proofs can share a
single canonical foundation. This file contains small, fully-decidable enumerative
utilities and the adjugate/inverse helpers used in proofs.
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

/-- Adjugate for a 2×2 matrix: [[a,b],[c,d]]^# = [[d,-b],[-c,a]]. -/
def adj2x2 (M : Matrix (Fin 2) (Fin 2) (ZMod 3)) : Matrix (Fin 2) (Fin 2) (ZMod 3) :=
  fun i j =>
    if i = 0 ∧ j = 0 then M 1 1
    else if i = 0 ∧ j = 1 then -M 0 1
    else if i = 1 ∧ j = 0 then -M 1 0
    else M 0 0

/-- Explicit 2×2 inverse formula in F3: inv(M) = det(M) * adj(M). -/
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

end GL2F3Enumeration
