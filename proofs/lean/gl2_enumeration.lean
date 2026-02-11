import gl2_base
import conjugators_generated

/-!
`GL(2,3)` enumerative utilities and a constructive conjugacy bridge.

This module keeps a small, stable surface area:
- the enumerative definitions live in `gl2_base.lean`,
- the large finite-case conjugacy proof is auto-generated in `conjugators_generated.lean`
  by `scripts/generate_conjugators_lean.py`.

We re-export a single user-facing theorem `candidates_conjugate` that delegates to the
generated lemma.
-/

open GL2F3
open GL2F3Enumeration

namespace GL2F3Enumeration

/-- Every involution with `det = 2` is conjugate to `diag(-1,1)` in `GL(2,3)`. -/
theorem candidates_conjugate :
    ∀ M ∈ candidates, ∃ P ∈ invertible_matrices, P ⬝ M ⬝ inv2x2 P = GL2F3.A_diag_mat := by
  simpa using candidates_conjugate_generated

end GL2F3Enumeration
