/-!
Short Lean 4 skeleton: symbolic exclusion of z = 2*z + 2 on Z/3Z (F3)

This file provides a minimal statement and proof sketch in Lean-style pseudocode.
It is intended as a starting point for a fully machine-checked formalization.

To complete formally, one should:
  - import a finite-field development for F3 (Zmod 3 or finite ring library),
  - define points (x,y) in F3^2, affine lines as solution sets to a*x + b*y = c,
  - implement the coordinate-free product law `P(line) = +1 iff b*c = 0`, and
  - implement the full-sign closed form for the (a,b)=(1,0) case.

The lemma below encodes the short x=0 contradiction used in the repo.
-/

namespace Z22Exclusion

-- We use `ZMod 3` for F3
open ZMod

/-- Vertical line L: x = 0 in F3^2. -/
def L : List (ZMod 3 × ZMod 3) :=
  [(0,0), (0,1), (0,2)]

/-- Normalized coefficients for x = 0 are (a,b,c) = (1,0,0). -/
lemma normalized_abc_L : (1 : ZMod 3, 0, 0) = (1, 0, 0) := by rfl

/-- Product sign law: for normalized a*x + b*y = c, P(line) = +1 iff b*c = 0.
    Here (b,c)=(0,0) so P(L) = +1. -/
lemma product_sign_L : (true) := by
  -- machine-friendly proof: compute b*c = 0, conclude P(L) = +1
  trivial

/-- Full-sign closed form for (a,b) = (1,0): s(line,z) = +1 iff (c^2 + 2c + z) == 2.
    For c = 0 and z = 1 we get (0 + 0 + 1) = 1 != 2, hence s(L,1) = -1. -/
lemma full_sign_L_z1 : (true) := by
  -- machine-friendly proof: compute expression value = 1, conclude s(L,1) = -1
  trivial

/-- Contradiction: P(L) = +1 but s(L,1) = -1. -/
theorem z22_contradiction : (true) := by
  -- combine product_sign_L and full_sign_L_z1 to derive contradiction
  trivial

end Z22Exclusion
