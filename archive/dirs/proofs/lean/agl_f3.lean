import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
import Mathlib.Data.Matrix.Basic
import affine_f3
import gl2_f3
import gl2_base

/-!
Affine group helpers on AG(2,3).

This file is intentionally ASCII-only (see tests/test_lean_agl_smoke.py).
It provides a minimal affine-element type, its action on points, composition,
and an involution criterion.
-/

namespace AffineF3

open GL2F3
open GL2F3Enumeration

/-- Point addition in F3^2. -/
def point_add (p q : Point) : Point := (p.fst + q.fst, p.snd + q.snd)

/-- Point negation. -/
def point_neg (p : Point) : Point := (-p.fst, -p.snd)

/-- Affine element represented as a (linear, shift) pair. -/
def AffineElem : Type := Prod (Matrix (Fin 2) (Fin 2) (ZMod 3)) Point

/-- Action of an affine element on a point. -/
def act (e : AffineElem) (p : Point) : Point :=
  point_add (GL2F3.act e.fst p) e.snd

/-- Composition in the affine group:
(M1,s1) * (M2,s2) = (M1*M2, M1*s2 + s1). -/
def compose (e1 e2 : AffineElem) : AffineElem :=
  (e1.fst * e2.fst, point_add (GL2F3.act e1.fst e2.snd) e1.snd)

/-- Identity affine element. -/
def id_elem : AffineElem := (1, (0, 0))

/-- Composition respects action. -/
theorem act_compose (e1 e2 : AffineElem) (p : Point) :
    act (compose e1 e2) p = act e1 (act e2 p) := by
  simp [compose, act, point_add, GL2F3.act_mul, GL2F3.act]
  cases p with
  | mk x y =>
    simp [compose, act, point_add, GL2F3.act_mul, GL2F3.act]
    apply Prod.ext <;>
      simp [add_assoc, add_left_comm, add_comm, mul_assoc, mul_comm, mul_add, add_mul]
    ring

/-- Predicate: affine element is an involution (order 2). -/
def is_involution (e : AffineElem) : Prop :=
  compose e e = id_elem

/-- Characterize affine involutions: e^2 = id iff M^2 = I and M*s + s = 0. -/
theorem is_involution_iff (e : AffineElem) :
    Iff
      (is_involution e)
      (And (e.fst * e.fst = 1)
        (point_add (GL2F3.act e.fst e.snd) e.snd = (0, 0))) := by
  have forward :
      is_involution e ->
        And (e.fst * e.fst = 1)
          (point_add (GL2F3.act e.fst e.snd) e.snd = (0, 0)) := by
    intro h
    have hm : e.fst * e.fst = 1 := by
      have := congrArg Prod.fst h
      simpa [is_involution, compose, id_elem] using this
    have hs : point_add (GL2F3.act e.fst e.snd) e.snd = (0, 0) := by
      have := congrArg Prod.snd h
      simpa [is_involution, compose, id_elem] using this
    exact And.intro hm hs

  have backward :
      And (e.fst * e.fst = 1)
          (point_add (GL2F3.act e.fst e.snd) e.snd = (0, 0)) ->
        is_involution e := by
    intro h
    rcases h with And.intro hm hs
    apply Prod.ext <;> simp [is_involution, compose, id_elem, hm, hs]

  exact Iff.intro forward backward

end AffineF3
