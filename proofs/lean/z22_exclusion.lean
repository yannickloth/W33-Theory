/-!
Lean 4 skeleton for the short symbolic exclusion of `z -> 2*z + 2`.

This captures the same `x=0` contradiction used in:
- `tools/formal_z22_proof.py`
- `tests/test_formal_proof_z22.py`

It is intentionally compact so it can be extended to the full reduced-orbit
formalization.
-/

import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
import affine_f3
import gl2_f3

namespace Z22Exclusion

open AffineF3

/-- Vertical line `L : x = 0` in `F3^2` (delegated to `AffineF3.vertical_line`). -/
def L : List (Prod (ZMod 3) (ZMod 3)) := vertical_line

/-- Product-sign rule encoded as `+/- 1` in `Int`. -/
def PLine (a b c : ZMod 3) : Int :=
  if b * c = 0 then 1 else -1

/-- `PLine = +1` iff `b*c = 0`. -/
theorem PLine_eq_iff (a b c : ZMod 3) : Iff (PLine a b c = 1) (b * c = 0) := by
  by_cases h0 : b * c = 0 <;> simp [PLine, h0]

/-- Closed-form full-sign rule for the `(a,b)=(1,0)` branch. -/
def SLine (a b c : ZMod 3) (z : ZMod 3) : Int :=
  if (c * c + 2 * c + z : ZMod 3) = 2 then 1 else -1

/-- In the `(1,0)` slice, `SLine = +1` iff the polynomial equals `2`. -/
theorem SLine_for_1_0_eq_iff (c z : ZMod 3) :
    Iff (SLine (1 : ZMod 3) 0 c z = 1) ((c * c + 2 * c + z : ZMod 3) = 2) := by
  by_cases h0 : (c * c + 2 * c + z : ZMod 3) = 2 <;> simp [SLine, h0]

/-- Affine z-map used in the corollary, `z -> 2*z + 2`. -/
def zMap (z : ZMod 3) : ZMod 3 :=
  2 * z + 2

/-- `z=1` is fixed by `zMap`. -/
@[simp] theorem zMap_one : zMap 1 = 1 := by
  simp [zMap]

/-- `z=0` is sent to `2`. -/
@[simp] theorem zMap_zero : zMap 0 = 2 := by
  simp [zMap]

/-- `z=2` is sent to `0`. -/
@[simp] theorem zMap_two : zMap 2 = 0 := by
  simp [zMap]

/-- Explicit table for `zMap` on `ZMod 3`. -/
theorem zMap_table : And (zMap 0 = 2) (And (zMap 1 = 1) (zMap 2 = 0)) := by
  simp [zMap]

/-- The affine map `z -> 2*z+2` is an involution on `ZMod 3`. -/
@[simp] theorem zMap_involution (z : ZMod 3) : zMap (zMap z) = z := by
  fin_cases z <;> simp [zMap]

/-- `z=1` is the unique fixed point of `zMap` in `ZMod 3`. -/
theorem zMap_fixed_iff (z : ZMod 3) : Iff (zMap z = z) (z = 1) := by
  fin_cases z <;> simp [zMap]

/-- Any fixed point of `zMap` must be `z=1`. -/
theorem zMap_fixed_point_unique (z : ZMod 3) (hz : zMap z = z) : z = 1 := by
  exact (zMap_fixed_iff z).1 hz

/-- For `x=0`, product sign is `+1`. -/
@[simp] theorem PLine_vertical : PLine (1 : ZMod 3) 0 0 = 1 := by
  simp [PLine]

/-- For `x=0` and `z=1`, closed-form sign is `-1`. -/
@[simp] theorem SLine_vertical_z1 : SLine (1 : ZMod 3) 0 0 1 = -1 := by
  simp [SLine]

/-- Same sign value after inserting `zMap 1 = 1`. -/
@[simp] theorem SLine_vertical_zMap_one : SLine (1 : ZMod 3) 0 0 (zMap 1) = -1 := by
  simp [zMap, SLine]

/-- Explicit full-sign table for the vertical line `x=0` across all `z`. -/
theorem SLine_vertical_table :
    And (SLine (1 : ZMod 3) 0 0 0 = -1)
      (And (SLine (1 : ZMod 3) 0 0 1 = -1) (SLine (1 : ZMod 3) 0 0 2 = 1)) := by
  simp [SLine]

/-- `SLine` when `c = 0` for `z=1` is always `-1` (works for any a,b). -/
theorem SLine_c0_z1 (a b : ZMod 3) : SLine a b 0 1 = -1 := by
  simp [SLine]

/-- For any line through the origin (`c = 0`) the product sign is `+1`. -/
theorem PLine_c0_eq_one (a b : ZMod 3) : PLine a b 0 = 1 := by
  simp [PLine]

open GL2F3

/-- `A_diag_mat` fixes each vertical point `(0,b)` (matrix action version). -/
@[simp] theorem A_diag_fix_elem (b : ZMod 3) : GL2F3.act GL2F3.A_diag_mat (0, b) = (0, b) := by
  simp [GL2F3.act, GL2F3.A_diag_mat]

/-- `A_diag_mat` preserves the vertical line `L` (matrix action version). -/
theorem A_diag_on_L : L.map (GL2F3.act GL2F3.A_diag_mat) = L := by
  simp [L, GL2F3.act, GL2F3.A_diag_mat]

/-- Corollary: if a `z` is fixed by `zMap`, `diag(-1,1)` cannot simultaneously
    preserve the vertical line and make the product sign equal to the full sign.
-/
theorem diag_no_z_stabilizer (z : ZMod 3) (hz : zMap z = z) :
    Ne (PLine (1 : ZMod 3) 0 0) (SLine (1 : ZMod 3) 0 0 z) := by
  exact z22_contradiction_of_fixed_point z hz

/-- Core contradiction used to exclude `z=(2,2)`: `+1 != -1`. -/
theorem z22_contradiction :
    Ne (PLine (1 : ZMod 3) 0 0) (SLine (1 : ZMod 3) 0 0 1) := by
  simp [PLine_vertical, SLine_vertical_z1]

/-- Equivalent contradiction in the explicit `zMap` form. -/
theorem z22_contradiction_via_zMap :
    Ne (PLine (1 : ZMod 3) 0 0) (SLine (1 : ZMod 3) 0 0 (zMap 1)) := by
  simp [PLine_vertical, SLine_vertical_zMap_one]

/--
If one assumes a fixed point `z` of `zMap`, the same vertical-line contradiction
follows after reducing to the unique fixed value `z=1`.
-/
theorem z22_contradiction_of_fixed_point
    (z : ZMod 3) (hz : zMap z = z) :
    Ne (PLine (1 : ZMod 3) 0 0) (SLine (1 : ZMod 3) 0 0 z) := by
  have hz1 : z = 1 := zMap_fixed_point_unique z hz
  simpa [hz1] using z22_contradiction

/--
Same fixed-point contradiction written in the explicit `zMap` target form.
-/
theorem z22_contradiction_of_fixed_point_via_zMap
    (z : ZMod 3) (hz : zMap z = z) :
    Ne (PLine (1 : ZMod 3) 0 0) (SLine (1 : ZMod 3) 0 0 (zMap z)) := by
  have hz1 : z = 1 := zMap_fixed_point_unique z hz
  simpa [hz1] using z22_contradiction_via_zMap

/--
There is no fixed point of `zMap` for which the vertical-line sign could be
preserved (`PLine = SLine`), i.e. the exclusion can be stated existentially.
-/
theorem z22_no_fixed_point_stabilizer :
    Not (Exists fun z : ZMod 3 =>
      zMap z = z /\ PLine (1 : ZMod 3) 0 0 = SLine (1 : ZMod 3) 0 0 z) := by
  intro h
  rcases h with Exists.intro z hrest
  rcases hrest with And.intro hz heq
  exact (z22_contradiction_of_fixed_point z hz) heq

/--
Same existential exclusion but written with the explicit `zMap` target.
-/
theorem z22_no_fixed_point_stabilizer_via_zMap :
    Not (Exists fun z : ZMod 3 =>
      zMap z = z /\ PLine (1 : ZMod 3) 0 0 = SLine (1 : ZMod 3) 0 0 (zMap z)) := by
  intro h
  rcases h with Exists.intro z hrest
  rcases hrest with And.intro hz heq
  exact (z22_contradiction_of_fixed_point_via_zMap z hz) heq

/--
No fixed-point stabilizer exists for any candidate involution that preserves
some line through the origin (`c = 0`). This generalizes the vertical-line
contradiction to all such linear stabilizers.
-/
theorem z22_no_fixed_point_stabilizer_for_candidate_line_through_origin
    (M : Matrix (Fin 2) (Fin 2) (ZMod 3))
    (hM : List.Mem M GL2F3Enumeration.candidates) :
    Not (Exists fun z : ZMod 3 =>
      zMap z = z /
        Exists fun a b : ZMod 3 =>
          (line_from_abc a b 0).map (GL2F3.act M) = line_from_abc a b 0 /
            PLine a b 0 = SLine a b 0 z) := by
  intro h
  rcases h with Exists.intro z hrest
  rcases hrest with And.intro hz hline
  rcases hline with Exists.intro a hline2
  rcases hline2 with Exists.intro b hrest2
  rcases hrest2 with And.intro _ heq
  have p := PLine_c0_eq_one a b
  have z1 := zMap_fixed_point_unique z hz
  have s := by simpa [z1] using SLine_c0_z1 a b
  have : 1 = -1 := by simp [p, heq, s]
  contradiction

end Z22Exclusion
