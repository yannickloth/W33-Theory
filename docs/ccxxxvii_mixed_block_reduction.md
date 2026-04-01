# Phase CCXXXVII - Mixed-Block Reduction

This note sharpens the chiral-Clifford gap from Phase CCXXXV.

The previous phase identified two continuum-facing quadratic packets at q = 3:

- 55 = 15 + 25 + 15
- 39 = 15 + 9 + 15.

The new point is that these are the same chiral quadratic architecture with two
different choices for the mixed block.

## A4 packet

For the quadratic Weyl packet,

- 15 = dim Sym^2(W+)
- 25 = dim(W+ tensor W-)
- 15 = dim Sym^2(W-)

so

- 55 = 15 + 25 + 15.

## c6 packet

For the chiral packet identified in Phase CCXXXV,

- 15 = dim Sym^2(W+)
-  9 = dim(Lambda^2_+ tensor Lambda^2_-)
- 15 = dim Sym^2(W-)

so

- 39 = 15 + 9 + 15.

## Exact q = 3 gap

The gap is entirely in the mixed block:

- 25 - 9 = 16.

At q = 3 this is exactly the Clifford packet

- 16 = 2^4 = mu^2.

The family selector is

- (q+2)^2 - q^2 - mu^2 = -(q-3)(q+1).

So q = 3 is the unique positive integer point where the mixed-block reduction

- dim(W+ tensor W-) -> dim(Lambda^2_+ tensor Lambda^2_-)

loses exactly one 4D Clifford packet.

## Best current reading

The continuum-facing hierarchy now has a precise block-level interpretation:

- A4 packet 55 = Sym^2(W+) + (W+ tensor W-) + Sym^2(W-)
- c6 packet 39 = Sym^2(W+) + (Lambda^2_+ tensor Lambda^2_-) + Sym^2(W-)
- gap 16 = Clifford_4.

So the difference between the full quadratic Weyl lift and the c6 packet is not
spread across the whole architecture. It sits entirely in the mixed chiral
block, and at q = 3 that lost mixed block is exactly one Clifford packet.