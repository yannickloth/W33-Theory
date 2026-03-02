# Pillar 98: Connecting N to the 270-Edge Transport

This pillar establishes the precise relationship between the regular
subgroup N (acting on 192 flags) and the 270-edge transport law (acting
on 27 QIDs).

## Key Discoveries

**T1 — QID Interaction:**  N is *not* fully QID-separating. There are
exactly 54 instances where a non-identity element of N maps a flag to
another flag with the same QID.  This means the N-action partially
respects the QID partition.

**T2 — Block Structure:**  The 192 flags decompose into 48 blocks of
size 4, giving a ratio of 192/48 = 4 flags per block.

**T3 — Non-Uniform Projection:**  The ratio of blocks to QIDs is
48/27 = 16/9, which is *not* an integer.  This means the projection
from blocks to QIDs is non-uniform: some QIDs correspond to more
blocks than others.

**T4 — Derived Subgroup Transitivity:**  The derived subgroup [N,N]
(order 48) acts *transitively* on all 48 blocks — a single orbit.
This is a powerful structural constraint showing [N,N] already
captures the full block dynamics.

## Consequences

The factorisation 192 → 48 → 27 is not a simple tower of uniform
coverings.  The intermediate level (blocks) relates to flags by a
clean factor of 4, but the passage from blocks to QIDs involves a
non-trivial partition.  The derived subgroup's transitivity on blocks
means that the abelianisation N/[N,N] ≅ Z₂² acts as a "colour"
symmetry permuting the 4 flags within each block.
