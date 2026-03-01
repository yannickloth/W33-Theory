# Pillar 99: Clifford Algebra Embedding

This pillar constructs a Clifford algebra Cl(V, Q) over F₃ and embeds the
key algebraic structures of the tomotope into it.

## Key Discoveries

**T1 — Cl(2, F₃):**  The Clifford algebra Cl(2, F₃) has dimension 2² = 4
with basis {1, e₀, e₁, e₀e₁}.  The generators satisfy:
- e₀² = e₁² = 1 (Euclidean quadratic form)
- e₀e₁ + e₁e₀ = 0 (anticommutation)

**T2 — Unit Vectors:**  Under the Euclidean form a² + b² = 1 mod 3,
there are exactly 4 unit vectors in F₃²: (1,0), (2,0), (0,1), (0,2).
These generate the Pin group.

**T4 — Spin Group Orders:**
| n | Spin(n, F₃) | Order |
|---|-------------|-------|
| 2 | Z₄          | 4     |
| 3 | SL(2, F₃)   | 24    |
| 4 | SL(2,F₃)²   | 576   |
| 5 | Sp(4, F₃)   | 51840 |

**T5 — Embedding:**  Since |N| = 192 and |Spin(4, F₃)| = 576 = 3 × 192,
the regular subgroup N embeds into Spin(4, F₃) with **index 3**.
N occupies exactly 1/3 of the full Spin group — it is a maximal subgroup.

## Consequences

The identification N ↪ Spin(4, F₃) provides a clean algebraic home for
the tomotope's regular subgroup.  Since Spin(4, F₃) ≅ SL(2, F₃) × SL(2, F₃),
and N has index 3 in this group, N can be understood as a "diagonal"
subgroup of the double cover.  

The full symmetry |Γ × H| = 1,769,472 would require embedding into a much
larger Spin group (Spin(5, F₃) or beyond), but the core structure is
already captured at dimension 4.
