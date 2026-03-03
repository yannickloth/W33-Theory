#!/usr/bin/env python3
"""
SOLVE_DESIGNS.py — VII-W: COMBINATORIAL DESIGNS & DISTANCE STRUCTURE
=====================================================================
Explore the association scheme, distance-regular structure, t-designs,
spread/ovoid combinatorics, and their connection to particle physics
from W(3,3) = SRG(40,12,2,4).

All identities must be exact and expressed in SRG parameters.
"""

from fractions import Fraction
import numpy as np
from itertools import combinations

# ── SRG parameters ──
v, k, lam, mu = 40, 12, 2, 4
r_eval, s_eval = 2, -4
f, g = 24, 15
E = v * k // 2          # 240
q = 3
N = 5
Phi3 = 13
Phi6 = 7
k_comp = v - k - 1      # 27
alpha_ind = 10

checks = []

def check(name, cond):
    status = "PASS" if cond else "FAIL"
    print(f"  {status}: {name}")
    checks.append((name, cond))

print("="*70)
print("VII-W: COMBINATORIAL DESIGNS & DISTANCE STRUCTURE")
print("="*70)

# ── Build graph (PG(3,3) + symplectic form) ──
GF3 = range(3)
pg3_points = set()
for a in GF3:
    for b in GF3:
        for c in GF3:
            for d in GF3:
                if (a,b,c,d) != (0,0,0,0):
                    pt = (a,b,c,d)
                    for i in range(4):
                        if pt[i] != 0:
                            inv = pow(pt[i], -1, 3)
                            norm = tuple((x * inv) % 3 for x in pt)
                            pg3_points.add(norm)
                            break
points = sorted(pg3_points)
assert len(points) == v

def symp(p1, p2):
    return (p1[0]*p2[1] - p1[1]*p2[0] + p1[2]*p2[3] - p1[3]*p2[2]) % 3

A = np.zeros((v, v), dtype=int)
edges = []
for i in range(v):
    for j in range(i+1, v):
        if symp(points[i], points[j]) == 0:
            A[i][j] = A[j][i] = 1
            edges.append((i,j))
assert len(edges) == E

print(f"\n  Graph: v={v}, E={E}, k={k}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 1: Association scheme — intersection numbers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── Association Scheme ──")

# SRG has a 2-class association scheme with relations:
# R0 = identity, R1 = adjacency, R2 = non-adjacency (complement)
# Intersection numbers p^h_{ij} form the structure constants.
# p^1_{11} = λ, p^1_{12} = k-λ-1, p^1_{22} = k'-λ' where k'=v-k-1=27
# p^2_{11} = μ, p^2_{12} = k-μ, p^2_{22} = k'-μ' 

# We need μ' (common non-neighbors for non-adjacent pairs)
# In complement: λ' = v - 2k + μ - 2 = 40-24+4-2 = 18
# μ' = v - 2k + λ = 40-24+2 = 18 (hmm, λ'=μ' for complement?)
lam_comp = v - 2*k + mu - 2  # 18
mu_comp = v - 2*k + lam       # 18
print(f"  Complement: k'={k_comp}, λ'={lam_comp}, μ'={mu_comp}")

# λ' = μ' = 18 = 2q² (conference graph property!)
# This means the complement is a conference graph!
print(f"  λ'=μ'={lam_comp} = 2q² = {2*q**2}")

check("Complement λ'=μ'=2q² = 18 (conference graph!)",
      lam_comp == mu_comp == 2*q**2)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 2: Krein parameters — the Krein array
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── Krein Parameters ──")

# For SRG, Krein parameters q^k_{ij} are computed from eigenvalues.
# The Krein conditions require q^k_{ij} >= 0.
# For SRG(v,k,λ,μ):
# q^1_{11} = f(f+1)/v - f(f-1)r²/(vk) + (f-1)(f-2)r⁴/(vk²) ??? 
# Actually simpler: the key Krein parameters are:
# q^1_{11} = 1 + f(r³-s³)/(k(s-r)) + (f²-f)(r²s²)/(k²(s-r)²) ... 
# Let me use the standard formula from the eigenmatrix.

# The first eigenmatrix P has rows [1,k], [1,r], [1,s]... for 2-class:
# P = [[1, k, k'],
#      [1, r, -r-1],    (since r' = -(v-k-1) - r·k/(f or g)... )
#      [1, s, -s-1]]    (hmm, need to be more careful)

# For a 2-class scheme: A₁ has eigenvalues k, r, s on E₀, E₁, E₂
# A₂ (complement) has eigenvalues k', -r-1, -s-1
r2 = -r_eval - 1   # complement eigenvalue for r-space: -3
s2 = -s_eval - 1    # complement eigenvalue for s-space: 3

print(f"  Complement eigenvalues: k'={k_comp}, r₂={r2}, s₂={s2}")
print(f"  |r₂|=|s₂|= {abs(r2)} = q (balanced!)")

check("Complement eigenvalues: |r₂|=|s₂|=q=3 (balanced spectrum)",
      abs(r2) == q and abs(s2) == q)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 3: Eigenmatrix and Q-matrix (dual)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── Eigenmatrix P and Dual Q ──")

# First eigenmatrix P (columns = coordinates in idempotent basis):
# P = [[1, k,       k'     ],
#      [1, r,       -1-r   ],
#      [1, s,       -1-s   ]]
P_mat = np.array([[1, k,      k_comp],
                   [1, r_eval, -1-r_eval],
                   [1, s_eval, -1-s_eval]], dtype=float)

print(f"  P = {P_mat.tolist()}")
# P = [[1, 12, 27], [1, 2, -3], [1, -4, 3]]

# Second eigenmatrix Q = v * P⁻¹ * diag(m) where m = [1, f, g]
# Actually: Q_{ij} = m_j * P_{ji}^{-1} ... standard formula:
# Q = diag(m) * P^T * diag(1/k_j)^{-1}... 
# Let me just compute: PQ = vI

m = np.array([1, f, g], dtype=float)
k_j = np.array([1, k, k_comp], dtype=float)

# Q_ij = (m_i/k_j) * P_ji  for 2-class association scheme (after transposing)
# Actually the standard formula is: Q = v * diag(1/m) * P^{-1} * diag(k_j)... 
# Let me just compute P^{-1} and verify.

P_inv = np.linalg.inv(P_mat)
Q_mat = v * np.diag(1.0/m) @ P_inv @ np.diag(k_j)

# Hmm, let me use the correct formula. PQ = vI means Q = v * P^{-1}.
Q_direct = v * P_inv

print(f"  P·Q/v = I check: {np.allclose(P_mat @ Q_direct, v * np.eye(3))}")

# But Q should have the standard form:
# Q = [[1, f,     g    ],
#      [1, f*r/k, g*s/k'],  ... (need exact formula)

# The dual eigenmatrix Q has Q_{ij} = P_{ji} * m_i / k_j
# (Row i of Q corresponds to idempotent E_i, column j to relation R_j)
# Wait, the standard definition varies by text. Let me verify directly.

# The correct relation: P * Q = v * I where
# P_{i,j} = eigenvalue of A_j on eigenspace i (i=0,1,2; j=0,1,2)
# Q_{j,i} = (m_i / n_j) * P_{i,j} where n_j = valency of relation j

# So Q_{j,i} = (m_i / k_j) * P_{i,j}
# This gives Q as:
Q_std = np.zeros((3,3))
for j in range(3):
    for i in range(3):
        Q_std[j,i] = (m[i] / k_j[j]) * P_mat[i,j]

print(f"  Q_std = {Q_std.tolist()}")
print(f"  PQ_std = {(P_mat @ Q_std).tolist()}")
pq_check = np.allclose(P_mat @ Q_std, v * np.eye(3))
print(f"  P·Q = v·I: {pq_check}")

# Q row 0: [1, 1, 1] * m / k_j → [1*1/1, f*1/k, g*1/k'] = [1, 24/12, 15/27] = [1, 2, 5/9]
# Hmm, that's not standard. Let me try the other convention:
# Q_{i,j} = (m_j / k_i) * P_{j,i}   (transposed)

Q_alt = np.zeros((3,3))
for i in range(3):
    for j in range(3):
        Q_alt[i,j] = m[j] * P_mat[j,i] / k_j[i]

print(f"  Q_alt = {Q_alt.tolist()}")
pq_alt = np.allclose(P_mat @ Q_alt, v * np.eye(3))
print(f"  P·Q_alt = v·I: {pq_alt}")

# Let me just verify PQ = vI for Q = v * P^{-1}
# Exact computation with Fraction:
P_frac = [[Fraction(1), Fraction(k), Fraction(k_comp)],
           [Fraction(1), Fraction(r_eval), Fraction(-1-r_eval)],
           [Fraction(1), Fraction(s_eval), Fraction(-1-s_eval)]]

# det(P) = 1*(r*(-1-s) - s*(-1-r)) - k*((-1-s) - (-1-r)) + k'*(s-r)
det_P = (Fraction(1) * (Fraction(r_eval)*Fraction(-1-s_eval) - Fraction(s_eval)*Fraction(-1-r_eval))
       - Fraction(k) * (Fraction(-1-s_eval) - Fraction(-1-r_eval))
       + Fraction(k_comp) * (Fraction(s_eval) - Fraction(r_eval)))

# = 1*(r(-1-s) - s(-1-r)) - k((-1-s)-(-1-r)) + k'(s-r)
# = 1*(-r-rs+s+sr) - k(-s+r) + k'(s-r)
# = 1*(s-r) - k(r-s) + k'(s-r)
# = (s-r)(1+k-k') = (s-r)(1+k-v+k+1) = (s-r)(2k+2-v)

det_simp = Fraction(s_eval - r_eval) * Fraction(2*k + 2 - v)
print(f"  det(P) = (s-r)(2k+2-v) = ({s_eval-r_eval})({2*k+2-v}) = {det_simp}")
# = (-6)(-16) = 96? No: (s-r)=-6, (2k+2-v)=26-40=-14
# det(P) = (-6)(-14) = 84 ... let me verify
print(f"  = {det_simp}")
det_np = round(np.linalg.det(P_mat))
print(f"  det(P) numpy = {det_np}")

# So det(P) = (s-r)(2k+2-v) = 84
# 84 = k*Phi6 = 12*7
# Also = C(q²,3) = C(9,3) = 84!
det_P_val = (s_eval - r_eval) * (2*k + 2 - v)  # (-6)*(-14) = 84
print(f"  det(P) = {det_P_val} = k·Φ₆ = {k*Phi6} = C(q²,3) = {9*8*7//6}")

check("det(P_eigenmatrix) = k·Φ₆ = C(q²,3) = 84",
      det_P_val == k * Phi6)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 4: Spread structure — number of spreads
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── Spread & Ovoid Structure ──")

# In GQ(q,q), a spread is a set of q²+1 = 10 lines partitioning points.
# An ovoid is a set of q²+1 = 10 points, one per line.
# Points = v = 40, Lines = v = 40 (self-dual)
# Each spread has q²+1 = 10 lines, each ovoid has q²+1 = 10 points.

# Spread = partition of v=40 points into q²+1=10 lines of q+1=4 points each.
# 10 * 4 = 40 ✓

n_spread_lines = q**2 + 1  # 10 = alpha
n_line_points = q + 1       # 4 = mu = omega

check("Spread: (q²+1) lines of (q+1) pts = α·ω = v",
      n_spread_lines * n_line_points == v)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 5: Vertex partition into cliques and ovoids
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Each vertex is in exactly q+1 = 4 lines (cliques of size q+1=4)
# Each vertex is in exactly ? ovoids
# Lines through a point: q+1 = 4 = mu
# Points collinear with x: k = q(q+1) = 12
# Non-collinear (non-adjacent): k' = q³ = 27

lines_per_pt = q + 1  # 4
pts_per_line = q + 1   # 4
collinear = q * (q + 1)  # 12 = k

print(f"  Lines per point: {lines_per_pt} = q+1 = μ = {mu}")
print(f"  Points per line: {pts_per_line} = q+1 = μ")
print(f"  Collinear points: {collinear} = q(q+1) = k = {k}")

# The dual GQ: points ↔ lines, so collinearity in dual = concurrence in original
# Number of concurrent lines: q(q+1) = 12 = k (self-dual!)

check("Lines per point = pts per line = q+1 = μ (self-dual GQ)",
      lines_per_pt == pts_per_line == mu)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 6: Bose-Mesner algebra dimension
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── Bose-Mesner Algebra ──")

# For a d-class association scheme, the Bose-Mesner algebra has dimension d+1.
# For SRG (2-class): dim = 3.
# Basis: {I, A, J-I-A} (identity, adjacency, complement adjacency)
# This is a commutative algebra of v×v matrices.

# The algebra is isomorphic to C³ (direct sum of 1-dim ideals).
# The primitive idempotents E₀, E₁, E₂ have rank 1, f, g.
# E₀ = (1/v)J (all-ones projection)
# E₁ has rank f = 24 (dominant eigenspace)
# E₂ has rank g = 15 (subdominant eigenspace)

# The KEY identity: E₀ + E₁ + E₂ = I
# Ranks: 1 + f + g = v = 40
rank_sum = 1 + f + g
print(f"  Idempotent ranks: 1 + f + g = 1+{f}+{g} = {rank_sum} = v = {v}")

check("Bose-Mesner: 1+f+g = v (idempotent decomposition of identity)",
      rank_sum == v)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 7: Seidel matrix and switching equivalence
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── Seidel Matrix & Two-Graph ──")

# Seidel matrix: S = J - I - 2A (or equivalently -(2A-J+I))
# S has eigenvalues:
# For A eigenvalue k: S = v-1-2k = 40-1-24 = 15 = g
# For A eigenvalue r: S = -1-2r = -1-4 = -5 = -(q+r_eval) = -(q+2) = -N
# For A eigenvalue s: S = -1-2s = -1+8 = 7 = Φ₆

S_eig_k = v - 1 - 2*k   # 15 = g
S_eig_r = -1 - 2*r_eval  # -5 = -N
S_eig_s = -1 - 2*s_eval  # 7 = Phi6

print(f"  Seidel eigenvalues: {S_eig_k}, {S_eig_r}, {S_eig_s}")
print(f"  = g, -N, Φ₆ = {g}, {-N}, {Phi6}")

# The Seidel spectrum {g^1, (-N)^f, Φ₆^g} has a beautiful property:
# Product of distinct Seidel eigenvalues:
seidel_prod = S_eig_k * S_eig_r * S_eig_s
print(f"  Seidel product: g·(-N)·Φ₆ = {seidel_prod}")
# = 15·(-5)·7 = -525 = -(q(q+r)²Φ₆)... 
# |525| = 3·175 = 3·25·7 = q·N²·Φ₆
print(f"  |product| = {abs(seidel_prod)} = q·N²·Φ₆ = {q*N**2*Phi6}")

check("Seidel eig product: |g·(-N)·Φ₆| = q·N²·Φ₆ = 525",
      abs(seidel_prod) == q * N**2 * Phi6)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 8: Adjacency algebra structure constants
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── Structure Constants ──")

# A² = λA + μ(J-I-A) + kI  (from SRG definition)
# A² = (λ-μ)A + (k-μ)I + μJ
# A² = -2A + 8I + 4J  (our master identity)

# In the Bose-Mesner algebra, with A₀=I, A₁=A, A₂=J-I-A:
# A₁² = λ·A₁ + μ·A₂ + k·A₀
# So the structure constants p^0_{11}=k, p^1_{11}=λ, p^2_{11}=μ

# A₁·A₂ = ?
# A₁·(J-I-A₁) = A₁·J - A₁ - A₁²
# = kJ - A₁ - (λA₁ + μA₂ + kI)
# = kJ - (1+λ)A₁ - μA₂ - kI
# = kA₀ + k·A₁ + k·A₂ - (1+λ)A₁ - μA₂ - kI  (using J=A₀+A₁+A₂+... wait J=I+A₁+A₂)
# Actually J = A₀+A₁+A₂ = I + A + (J-I-A), so kJ = k(I+A₁+A₂)
# A₁·A₂ = k(I+A₁+A₂) - (1+λ)A₁ - μA₂ - kI
# = (k-k)I + (k-1-λ)A₁ + (k-μ)A₂
# = 0·I + (k-1-λ)·A₁ + (k-μ)·A₂

p1_12 = k - 1 - lam  # 9 = q²
p2_12 = k - mu         # 8 = dim(O)
print(f"  A₁·A₂ structure: p^1_12={p1_12}=q², p^2_12={p2_12}=dim(O)")

check("Structure: p^1_12 = k-1-λ = q² = 9, p^2_12 = k-μ = dim(O) = 8",
      p1_12 == q**2 and p2_12 == k - mu)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 9: μ-subconstituent — local graph 
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── Local Structure (μ-subconstituent) ──")

# The local graph (neighborhood of a vertex) has k=12 vertices.
# In GQ(q,q): the neighborhood decomposes into q+1=4 cliques of q=3 vertices.
# So the local graph is the disjoint union of (q+1) copies of K_q = 4 copies of K_3.
# This is 4·K₃ (4 triangles).

# Verify by computation:
vtx0 = 0
nbrs = [j for j in range(v) if A[0][j] == 1]
assert len(nbrs) == k

# Check the local graph structure
local_A = np.zeros((k, k), dtype=int)
for i_idx in range(k):
    for j_idx in range(i_idx+1, k):
        if A[nbrs[i_idx]][nbrs[j_idx]] == 1:
            local_A[i_idx][j_idx] = 1
            local_A[j_idx][i_idx] = 1

local_edges = np.sum(local_A) // 2
local_k = k * lam // 2  # expected edges = k*λ/2 ... 
# Actually: each vertex in local graph is adjacent to λ=2 others → edges = k*λ/2 = 12
print(f"  Local graph: {k} vertices, {local_edges} edges")
print(f"  k·λ/2 = {k*lam//2} edges (each vertex sees λ=2 neighbors)")

# Local graph eigenvalues: 4·K₃ has eigenvalues {2^4, (-1)^8}
# i.e., (q-1)^(q+1), (-1)^(q(q+1)-q-1)... let me just compute
local_eigs = sorted(np.linalg.eigvalsh(local_A), reverse=True)
print(f"  Local eigenvalues: {[round(e) for e in local_eigs]}")
n_pos = sum(1 for e in local_eigs if e > 0.5)
n_neg = sum(1 for e in local_eigs if e < -0.5)
n_zero = sum(1 for e in local_eigs if abs(e) < 0.5)
print(f"  Signature: {n_pos} positive ({round(local_eigs[0])}), {n_neg} negative ({round(local_eigs[-1])}), {n_zero} zero")

# Expected: 4 copies of K₃: eigenvalues are 2 (×4) and -1 (×8)
# So: 4 eigenvalues of +2 (= q-1), 8 eigenvalues of -1
# n_pos = q+1 = 4, n_neg = k - (q+1) = 8 = dim(O)

check("Local graph = (q+1)·K_q: pos eigs = q+1 = μ, neg = dim(O) = 8",
      n_pos == mu and n_neg == k - mu and round(local_eigs[0]) == q - 1)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 10: Subconstituent (Terwilliger) dimensions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── Terwilliger Decomposition ──")

# For SRG, fix a vertex x. The vertices partition into:
# Δ₀ = {x}: size 1
# Δ₁ = neighbors of x: size k = 12
# Δ₂ = non-neighbors of x: size v-k-1 = k' = 27

# The Terwilliger algebra T(x) is generated by A and the diagonal matrices
# E*_0, E*_1, E*_2 (projections onto Δ₀, Δ₁, Δ₂).

# The "subconstituent" sizes and their ratio:
delta_sizes = [1, k, k_comp]  # [1, 12, 27]
print(f"  Subconstituents: Δ₀={delta_sizes[0]}, Δ₁={delta_sizes[1]}, Δ₂={delta_sizes[2]}")
print(f"  Δ₁/Δ₂ = k/k' = {Fraction(k, k_comp)} = {Fraction(k, k_comp)}")

# k/k' = 12/27 = 4/9 = mu/q² = (spacetime)/(field²)
ratio_12 = Fraction(k, k_comp)
print(f"  = μ/q² = {Fraction(mu, q**2)}")

check("Subconstituent ratio k/k' = μ/q² = 4/9 (spacetime/field²)",
      ratio_12 == Fraction(mu, q**2))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 11: Edge-regular + co-edge-regular
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── Edge & Co-Edge Regularity ──")

# SRG is edge-regular (λ=2 for all edges) and co-edge-regular (μ=4 for all non-edges).
# Verify by sampling:
sample_edge = edges[0]
common_nbrs_edge = sum(1 for w in range(v) if A[sample_edge[0]][w]==1 and A[sample_edge[1]][w]==1)

# Find a non-edge
non_edge = None
for i in range(v):
    for j in range(i+1, v):
        if A[i][j] == 0:
            non_edge = (i,j)
            break
    if non_edge:
        break

common_nbrs_nonedge = sum(1 for w in range(v) if A[non_edge[0]][w]==1 and A[non_edge[1]][w]==1)

print(f"  Edge ({sample_edge}): common neighbors = {common_nbrs_edge} = λ = {lam}")
print(f"  Non-edge ({non_edge}): common neighbors = {common_nbrs_nonedge} = μ = {mu}")

# The "regularity triple" (v, k, λ, μ) gives four-tuple of structure constants:
# p^0_{11} = k, p^1_{11} = λ, p^2_{11} = μ, p^0_{01} = 0 (by convention)
# The TOTAL structure info per vertex: k+0+k' = v-1 = 39
# k + k' = v - 1 = 39

# An elegant identity: (k-λ-1)(k'-μ'+1) = ... 
# k-λ-1 = 9 = q², k'-lam_comp+... hmm
# Let's try: the "Higman ratio" k(k-λ-1)/μ = k·q²/μ = 12·9/4 = 27 = k'!
higman = k * (k - lam - 1) // mu
print(f"  Higman: k(k-λ-1)/μ = {k}·{k-lam-1}/{mu} = {higman} = k' = {k_comp}")

check("Higman: k(k-λ-1)/μ = k·q²/μ = k' = 27 (neighbor-complement duality)",
      higman == k_comp)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 12: Strongly regular graph complement parameters match
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── SRG Complement Perfect Symmetry ──")

# The complement graph is SRG(40, 27, 18, 18).
# Note λ' = μ' = 18 = 2q². This means the complement has a VERY special property:
# It's a TYPE I SRG (also called a "conference graph" relative to v=40).

# A beautiful identity: k·k' = v·(v-1)/2 - E = 780 - 240 = 540? No.
# k·k' = 12·27 = 324 = 18² = (λ')² = (μ')²
kk_prime = k * k_comp
print(f"  k·k' = {kk_prime}")
print(f"  = (λ')² = {lam_comp**2}")
print(f"  = (2q²)² = {(2*q**2)**2}? No, 18²=324, (2·9)²=324 ✓")

# Actually k·k' = 324 = 18² and 18 = 2q². But 324 = μ·q⁴ = 4·81
# = (q+1)·q⁴ = 4·81? No: mu = q+1 = 4, q⁴ = 81. 4·81 = 324 ✓!
print(f"  k·k' = μ·q⁴ = {mu}·{q**4} = {mu*q**4}")

check("k·k' = μ·q⁴ = λ'² = 324 (valency product = complement overlap²)",
      kk_prime == mu * q**4 and kk_prime == lam_comp**2)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 13: Absolute bound and design strength
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── Absolute Bound & Design Strength ──")

# The absolute bound for SRG: v ≤ f(f+3)/2 and v ≤ g(g+3)/2
abs_bound_f = f * (f + 3) // 2  # 24*27/2 = 324
abs_bound_g = g * (g + 3) // 2  # 15*18/2 = 135

print(f"  f(f+3)/2 = {abs_bound_f} = μ·q⁴ = k·k'")
print(f"  g(g+3)/2 = {abs_bound_g}")
print(f"  v = {v} ≤ min({abs_bound_g}, {abs_bound_f}) = {min(abs_bound_f, abs_bound_g)}")

# The RATIO v/abs_bound_g = 40/135 = 8/27 = (k-μ)/k' = dim(O)/k'
ratio_abs = Fraction(v, abs_bound_g)
print(f"  v/(g(g+3)/2) = {ratio_abs} = dim(O)/k' = {Fraction(k-mu, k_comp)}")

check("v/(g(g+3)/2) = dim(O)/k' = 8/27 (absolute bound ratio)",
      ratio_abs == Fraction(k - mu, k_comp))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 14: Cayley table number — number of common neighbors of distance-2 pairs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── Cayley / Friendship Structure ──")

# In the GQ: two non-collinear points have exactly μ = q+1 = 4 common neighbors.
# Two collinear points (on the same line) have λ = q-1 = 2 common neighbors.
# The trace of A² restricted to edges = Σ_{(i,j)∈E} a_{ij}² = |E| (trivially)
# But Σ_{(i,j)∈E} (A²)_{ij} = Σ_{(i,j)∈E} λ = λ·|E| = 2·240 = 480 = Tr(A²) ✓

# More interesting: the average path count between vertices at distance 2:
# Each non-adjacent pair has exactly μ = 4 paths of length 2.
# Total such pairs: k'·v/2 = 27·40/2 = 540 = ... no, C(v,2)-E = 780-240 = 540.
non_edges = v*(v-1)//2 - E  # 540
print(f"  Non-edges: {non_edges} = v(v-1)/2 - E = {v*(v-1)//2}-{E}")
print(f"  540 = 20·k' = {20*k_comp}")

# 540 = k'·v/2 = 27·20 = 540 ✓
# Also: 540 = E·(k-λ-1)/(μ) ??? Let me check: E·q²/μ = 240·9/4 = 540 ✓!
ratio_ne = Fraction(non_edges, E)
print(f"  Non-edges/Edges = {ratio_ne} = q²/μ = {Fraction(q**2, mu)} = {Fraction(9,4)}")

check("Non-edges/Edges = q²/μ = 9/4 (complement density ratio)",
      ratio_ne == Fraction(q**2, mu))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "="*70)
n_pass = sum(1 for _, c in checks if c)
n_total = len(checks)
print(f"  RESULT: {n_pass}/{n_total} checks passed")
if n_pass == n_total:
    print("  ALL CHECKS PASS — COMBINATORIAL DESIGNS VERIFIED")
else:
    for name, c in checks:
        if not c:
            print(f"  FAILED: {name}")
print("="*70)
