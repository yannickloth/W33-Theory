# Pillar 97: The 270-Edge Transport Law

This pillar analyses the 270-edge transport data and derives the algebraic
transport law governing transitions between the 27 QID vertices.

## Key Discoveries

**T1 — Edge Decomposition:**  The 270 edges decompose as 5 generators ×
54 edges each.  Every generator produces a valence-2 graph on 27 vertices
(each QID sends to exactly 2 targets).

**T2 — Involution Generators:**  Generators g8 and g9 are true involutions:
every edge reverses (q→t implies t→q).  Each has exactly 3 fixed points
among the 27 QIDs.

**T3 — Order-3 Generators:**  Generators g2, g3, g5 have no self-inverse
edges — they act as order-3 permutations on the QID set.

**T4 — Affine Matrices:**  All 270 edges carry an affine matrix
L ∈ GL(2, F₃) with **determinant 1**.  Only 3 distinct matrices appear:
the identity I, the scalar 2I, and a shear matrix.  This shows the transport
preserves orientation in the Heisenberg quotient.

**T5 — Z₃ Cocycle:**  The cocycle exponent distribution is {0: 201, 1: 33,
2: 36}.  Most edges (74.4%) are cocycle-trivial; the non-trivial edges
concentrate on specific generators.

**T6 — Orient Strata:**  The orient_index field partitions the 270 edges
into exactly 10 strata of 27 edges each — one per generator×twin_bit
combination.

## Consequences

The transport law takes the explicit form

$$
(x', y', z') = L \cdot (x, y) + (t_x, t_y) + \omega \cdot z
$$

where L is one of the three det-1 matrices, (tₓ, tᵧ) is the z-shift, and ω
is the cocycle correction.  This affine structure over F₃ is exactly what one
expects from a Heisenberg bundle.
