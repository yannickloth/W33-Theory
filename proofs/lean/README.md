Lean 4 starter project for the Reduced Orbit corollary

This folder contains a compact Lean formalization skeleton in
`z22_exclusion.lean` for the short symbolic exclusion of `z=(2,2)`.

Project files included:
- `lakefile.lean` (declares the local package + `mathlib` dependency)
- `lean-toolchain` (pins the Lean toolchain used for this folder)
- `proofs.lean` (library entry importing local proof files)
- `z22_exclusion.lean` (current proof skeleton)

Local usage:
```bash
cd proofs/lean
lake update
lake build
```

The current Lean file proves the core contradiction (`PLine = +1` but
`SLine = -1` for the vertical line at `z=1`) and is intended as a base for
extending to a fuller machine-checked reduced-orbit formalization.
