Lean 4 skeleton proofs for the Reduced Orbit corollary

This folder contains a starting point (`z22_exclusion.lean`) for a formal
Lean 4 development showing the short symbolic exclusion of `z=(2,2)`.

To proceed locally:
- Install Lean 4 and lake (https://leanprover.github.io/)
- Create a `lakefile.lean` and add appropriate `mathlib` or `mathlib4` dependencies
- Flesh out the provided lemmas with explicit finite-field arithmetic on `ZMod 3`

This file is intentionally minimal: it encodes the statements and a proof
strategy but not the fully detailed formal tactics. Contributions welcome.
