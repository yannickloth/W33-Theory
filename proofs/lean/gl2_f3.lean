import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
import Mathlib.Data.Matrix.Basic

/-!
Basic GL(2,3) helpers: 2x2 matrices over ZMod 3 and a canonical involution
`diag(-1,1)` used in the reduced-orbit analysis.
-/

namespace GL2F3

open Matrix

/-- The diagonal matrix diag(-1,1) in `M_2(F3)`. -/
def A_diag_mat : Matrix (Fin 2) (Fin 2) (ZMod 3) := fun i j =>
  if i = 0 ∧ j = 0 then (-1 : ZMod 3) else if i = 1 ∧ j = 1 then (1 : ZMod 3) else 0

/-- `A_diag_mat` is an involution (squares to the identity). -/
theorem A_diag_mat_mul_self : A_diag_mat ⬝ A_diag_mat = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [A_diag_mat];
    -- the only nonzero product terms occur on the diagonal
    try simp [Matrix.mul_apply]

/-- `det(A_diag_mat) = (-1)*1 = -1 ≡ 2 (mod 3)`. -/
theorem A_diag_mat_det : A_diag_mat.det = (2 : ZMod 3) := by
  -- compute the determinant directly for the 2x2 matrix
  -- det [[a,b],[c,d]] = a*d - b*c
  have : A_diag_mat 0 0 = (-1 : ZMod 3) := by simp [A_diag_mat]
  have : A_diag_mat 0 1 = 0 := by simp [A_diag_mat]
  have : A_diag_mat 1 0 = 0 := by simp [A_diag_mat]
  have : A_diag_mat 1 1 = (1 : ZMod 3) := by simp [A_diag_mat]
  -- reduce det
  simp [Matrix.det]; -- this reduces to (-1) * 1 - 0 * 0
  -- compute (-1 : ZMod 3) * 1 = -1 = 2
  simp

end GL2F3
