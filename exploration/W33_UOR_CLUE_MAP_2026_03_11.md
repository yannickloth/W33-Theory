# W33 / UOR Clue Map

This note records the strongest clues from the extracted `UOR-Framework-main`
zip and separates them from weaker overlays.

## The Real Clues

The useful parts of the UOR repo are structural:

- `docs/content/concepts/monodromy.md`
- `docs/content/concepts/sheaf-semantics.md`
- `docs/content/concepts/cohomology.md`
- `docs/content/concepts/quantum-spectral-sequence.md`
- `foundation/src/bridge/observable.rs`

Those files point toward:

- coefficient-level cohomology over `Z/2Z`
- nontrivial holonomy / monodromy
- local-to-global gluing and `H^1` language
- lift-obstruction classes in `H^2`
- residual-entropy / curvature observables

These are all conceptually close to the live W33 transport and flavour stack.

## Strongest Exact Bridges

### 1. Binary shadow of nonabelian transport

The live W33 transport graph already has:

- exact local `S3` holonomy
- exact native `A2` local system
- exact old `v14` triangle parity

The right UOR-style match is:

- full holonomy = `Weyl(A2) ~= S3 ~= D3`
- coefficient shadow = sign / determinant map to `Z2`
- the old `v14` triangle parity is exactly that sign shadow

So the correct binary shadow is the holonomy sign, not the raw edge-voltage bit.

### 2. Local-to-global flavour gluing

The live `l6` flavour stack already has:

- exact local `V4` character data
- exact route-by-route closure data
- a canonical global label matrix

The right UOR-style match is:

- local sections = exact route patches from the two minimal `A2` closures
- global section = the canonical matrix `[[AB,I,A],[AB,I,A],[A,B,0]]`
- gluing theorem = those local sections are compatible and glue uniquely

So the open problem is no longer whether the flavour data glues. It is why
those local sections are selected dynamically.

## Useful but Secondary Clues

### 64 x 81 x 10 factorization

`|Sp(4,3)| = 51840 = 64 x 81 x 10` is cleaner than the Monster divisibility
story:

- `64 = 2^6`
- `81 = 3^4`
- small residual factor `10`

This is a real mixed-radix bridge, but it is weaker than the holonomy and
gluing clues.

### Ternary extension

`exploration/uor_ternary_breakthrough.py` is directionally better than the
Monster file because it tries to move UOR out of its binary-only shell and into
the `GF(3)` world where `W(3,3)` actually lives.

That is a better long-term bridge than moonshine numerology.

## Things To Treat Cautiously

### Monster / Landauer overlays

`exploration/w33_uor_landauer_monster_bridge.py` mixes some true statements
with much weaker numerology. The real content there is Landauer plus the
critical identity. The Monster layer is not the strongest clue.

### Quantum-level inconsistency

The extracted UOR repo does not present one stable quantum-level tower.

- `website/content/concepts/quantum-levels.md` uses `Q0 = 1 bit`, `Q1 = 2`,
  `Q2 = 4`, `Q3 = 8`
- `docs/content/concepts/quantum-universality.md` uses a materially different
  scale
- the local Monster bridge scripts use yet another `8/16/24/40/48` ladder

That means the quantum-level numerology is not stable enough to treat as a
theorem source.

## Current Take

The extracted UOR framework really does contain clues, but the best ones are
not the flashy ones.

The real bridge is:

1. `Z2` coefficient shadow above a richer nonabelian transport system
2. local-to-global gluing for the exact flavour label matrix
3. eventually, a ternary / `GF(3)` extension rather than a binary-only UOR

That is where the overlap with the live W33 theorem stack is strongest.
