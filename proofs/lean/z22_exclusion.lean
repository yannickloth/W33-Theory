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

namespace Z22Exclusion

/-- Vertical line `L : x = 0` in `F3^2`. -/
def L : List (Prod (ZMod 3) (ZMod 3)) := [(0, 0), (0, 1), (0, 2)]

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

/-- For `x=0`, product sign is `+1`. -/
@[simp] theorem PLine_vertical : PLine (1 : ZMod 3) 0 0 = 1 := by
  simp [PLine]

/-- For `x=0` and `z=1`, closed-form sign is `-1`. -/
@[simp] theorem SLine_vertical_z1 : SLine (1 : ZMod 3) 0 0 1 = -1 := by
  simp [SLine]

/-- Same sign value after inserting `zMap 1 = 1`. -/
@[simp] theorem SLine_vertical_zMap_one : SLine (1 : ZMod 3) 0 0 (zMap 1) = -1 := by
  simp [zMap, SLine]

/-- Core contradiction used to exclude `z=(2,2)`: `+1 != -1`. -/
theorem z22_contradiction :
    Ne (PLine (1 : ZMod 3) 0 0) (SLine (1 : ZMod 3) 0 0 1) := by
  simp [PLine_vertical, SLine_vertical_z1]

/-- Equivalent contradiction in the explicit `zMap` form. -/
theorem z22_contradiction_via_zMap :
    Ne (PLine (1 : ZMod 3) 0 0) (SLine (1 : ZMod 3) 0 0 (zMap 1)) := by
  simp [PLine_vertical, SLine_vertical_zMap_one]

end Z22Exclusion
