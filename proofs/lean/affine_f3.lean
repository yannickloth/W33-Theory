import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic

/-!
Affine plane over F3 (AG(2,3)) helper definitions.
This file intentionally keeps a minimal surface area: definitions for points,
`all_points`, `on_line` and `line_from_abc` are provided so we can begin
machine-checking statements about lines in `z22_exclusion.lean`.
-/

namespace AffineF3

/-- Points in `F3^2` as pairs `(x,y)`. -/
def Point := Prod (ZMod 3) (ZMod 3)

/-- All 9 affine points in a canonical order. -/
def all_points : List Point :=
  [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]

/-- Predicate for a point `(x,y)` to lie on the line `a*x + b*y = c`. -/
def on_line (a b c : ZMod 3) (p : Point) : Prop :=
  a * p.fst + b * p.snd = c

/-- The list of points satisfying `a*x + b*y = c` (computed by filtering the
canonical `all_points` list). -/
def line_from_abc (a b c : ZMod 3) : List Point :=
  all_points.filter fun p => a * p.fst + b * p.snd = c

/-- Vertical line `x = 0` as `line_from_abc 1 0 0`. -/
def vertical_line : List Point := line_from_abc (1 : ZMod 3) 0 0

/-- `vertical_line` expands to the three canonical vertical points. -/
theorem vertical_line_eq : vertical_line = [(0, 0), (0, 1), (0, 2)] := by
  simp [vertical_line, line_from_abc, all_points]

end AffineF3
