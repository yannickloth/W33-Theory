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

end GL2F3Enumeration
