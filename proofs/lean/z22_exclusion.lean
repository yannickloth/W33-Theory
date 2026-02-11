/-!
Lean 4 skeleton for the short symbolic exclusion of `z -> 2*z + 2`.

This captures the same `x=0` contradiction used in:
- `tools/formal_z22_proof.py`
- `tests/test_formal_proof_z22.py`

It is intentionally compact so it can be extended to the full reduced-orbit
formalization.
-/

import Mathlib.Data.ZMod.Basic

namespace Z22Exclusion

/-- Vertical line `L : x = 0` in `F3^2`. -/
def L : List (Prod (ZMod 3) (ZMod 3)) := [(0, 0), (0, 1), (0, 2)]

/-- Product-sign rule encoded as `+/- 1` in `Int`. -/
def PLine (a b c : ZMod 3) : Int :=
  if b * c = 0 then 1 else -1

/-- `PLine = +1` iff `b*c = 0`. -/
theorem PLine_eq_iff (a b c : ZMod 3) : (PLine a b c = 1) ↔ (b * c = 0) := by
  by_cases h0 : b * c = 0
  · simp [PLine, h0]
  · simp [PLine, h0]

/-- Closed-form full-sign rule for the `(a,b)=(1,0)` branch. -/
def SLine (a b c : ZMod 3) (z : ZMod 3) : Int :=
  if (c * c + 2 * c + z : ZMod 3) = 2 then 1 else -1

/-- In the `(1,0)` slice, `SLine = +1` iff the polynomial equals `2`. -/
theorem SLine_for_1_0_eq_iff (c z : ZMod 3) :
    (SLine (1 : ZMod 3) 0 c z = 1) ↔ ((c * c + 2 * c + z : ZMod 3) = 2) := by
  by_cases h0 : (c * c + 2 * c + z : ZMod 3) = 2
  · simp [SLine, h0]
  · simp [SLine, h0]

/-- For `x=0`, product sign is `+1`. -/
@[simp] theorem PLine_vertical : PLine (1 : ZMod 3) 0 0 = 1 := by
  simp [PLine]

/-- For `x=0` and `z=1`, closed-form sign is `-1`. -/
@[simp] theorem SLine_vertical_z1 : SLine (1 : ZMod 3) 0 0 1 = -1 := by
  simp [SLine]

/-- Core contradiction used to exclude `z=(2,2)`: `+1 != -1`. -/
theorem z22_contradiction :
    Ne (PLine (1 : ZMod 3) 0 0) (SLine (1 : ZMod 3) 0 0 1) := by
  simp [PLine_vertical, SLine_vertical_z1]

end Z22Exclusion
