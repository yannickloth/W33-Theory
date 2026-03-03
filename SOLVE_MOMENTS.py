#!/usr/bin/env python3
"""
THE MOMENT CHAIN AND THE EXCEPTIONAL CASCADE

Discovery: Tr(A^4)/Tr(A^2) = 52 = dim(F4).

Question: Does the full moment chain Tr(A^{2n})/Tr(A^{2n-2}) give 
ALL exceptional group dimensions?

Also: The non-neighbor subgraph eigenvalue structure with 
multiplicities {1, 12, 8, 6} and the partition 27 = 1+12+8+6
may encode the E6 decomposition.
"""

import numpy as np
from fractions import Fraction
import math

q = 3
v, k, lam, mu = 40, 12, 2, 4
r_eval, s_eval = 2, -4
f_mult, g_mult = 24, 15
E = 240

print("="*80)
print("  THE MOMENT CHAIN")
print("="*80)

# Spectral moments: M_n = Tr(A^n) = k^n + f*r^n + g*s^n
moments = {}
for n in range(1, 13):
    m = k**n + f_mult * r_eval**n + g_mult * s_eval**n
    moments[n] = m

print(f"\n  Tr(A^n) for n = 1..12:")
for n in range(1, 13):
    print(f"    M_{n:2d} = {moments[n]:>20d}")

print(f"\n  Ratios M_n / M_{'{n-2}'}:")
for n in range(3, 13):
    if moments[n-2] != 0:
        ratio = Fraction(moments[n], moments[n-2])
        print(f"    M_{n}/M_{n-2} = {float(ratio):>15.4f} = {ratio}")

print(f"\n  Even moment ratios M_{'{2n}'}/M_{'{2n-2}'}:")
for n in range(2, 7):
    ratio = Fraction(moments[2*n], moments[2*n-2])
    print(f"    M_{2*n}/M_{2*n-2} = {float(ratio):>15.4f} = {ratio}")

# M2/M0 (M0 = Tr(I) = 40 = v)
M0 = v
ratio_2_0 = Fraction(moments[2], M0)
print(f"\n  M_2/M_0 = {moments[2]}/{M0} = {ratio_2_0} = {float(ratio_2_0)}")

# Let's also look at M_n/v
print(f"\n  M_n / v (moments per vertex):")
for n in range(1, 13):
    ratio = Fraction(moments[n], v)
    print(f"    M_{n:2d}/v = {float(ratio):>15.4f} = {ratio}")

# Key: M2/M0 = 12 = k, M4/M2 = 52
print(f"\n  MOMENT RATIO CHAIN:")
print(f"    M_0 = v = {v}")
print(f"    M_2/M_0 = {Fraction(moments[2], v)} = k = {k}")
print(f"    M_4/M_2 = {Fraction(moments[4], moments[2])} = dim(F4) = v+k = {v+k}")

M6_M4 = Fraction(moments[6], moments[4])
print(f"    M_6/M_4 = {M6_M4} = {float(M6_M4):.4f}")

# Is M6/M4 a known quantity?
# M6 = k^6 + 24*64 + 15*4096 = 2985984 + 1536 + 61440 = 3048960
# M4 = 24960
# M6/M4 = 3048960/24960 = 122.18... hmm
# Not an integer. Let's see: 3048960/24960 = 480*6352/24960 ... let me compute

print(f"\n  M_6/M_4 = {moments[6]}/{moments[4]} = {float(M6_M4):.6f}")
print(f"  Not an integer. Let's try other combinations...")

# What about weighted moments?
# The "proper" ratios might use different normalization
# Try: (M_n - k^n) / (M_{n-2} - k^{n-2})
# This removes the trivial eigenvalue contribution

for n in range(4, 13, 2):
    num = moments[n] - k**n
    den = moments[n-2] - k**(n-2)
    if den != 0:
        ratio = Fraction(num, den)
        print(f"    (M_{n}-k^{n})/(M_{n-2}-k^{n-2}) = {float(ratio):.4f} = {ratio}")

# ══════════════════════════════════════════════════════
# THE POWER SUM SYMMETRIC FUNCTIONS
# ══════════════════════════════════════════════════════
print("\n" + "="*80)
print("  NEWTON'S IDENTITIES: CONNECTING MOMENTS TO EIGENVALUES")
print("="*80)

# The two non-trivial eigenvalues are r = 2, s = -4
# Their elementary symmetric functions:
e1 = r_eval + s_eval  # = -2
e2 = r_eval * s_eval  # = -8

print(f"  Non-trivial eigenvalues: r = {r_eval}, s = {s_eval}")
print(f"  e1 = r + s = {e1}")
print(f"  e2 = r * s = {e2}")
print(f"  |e2| = {abs(e2)} = k - mu = dim(O)")
print(f"  e1 = {e1} = -lam = -({lam})")

# The characteristic polynomial of the non-trivial part:
# t^2 - e1*t + e2 = t^2 + 2t - 8 = (t+4)(t-2) ✓
print(f"\n  Char poly: t^2 - ({e1})t + ({e2}) = t^2 + {-e1}t - {-e2}")
print(f"           = (t - {r_eval})(t - {s_eval}) = (t-2)(t+4) ✓")

# The discriminant
disc = e1**2 - 4*e2
print(f"\n  Discriminant = e1^2 - 4*e2 = {e1**2} - 4*({e2}) = {disc}")
print(f"  = {disc} = 36 = 6^2 = (k/lam)^2")
print(f"  sqrt(disc) = 6 = r - s = mass gap")

# ══════════════════════════════════════════════════════
# THE EXCEPTIONAL CASCADE IN THE EIGENVALUE PRODUCTS
# ══════════════════════════════════════════════════════
print("\n" + "="*80)
print("  THE EXCEPTIONAL CASCADE")
print("="*80)

# The key insight: the SRG eigenvalue PRODUCTS give exceptional dims
# We already know: sums and products of eigenvalues with f,g multiplicities
# give exceptional groups. Let me be systematic.

print(f"\n  From eigenvalues r={r_eval}, s={s_eval}, k={k}:")
print(f"    k - r = {k - r_eval} = {10} = alpha = dim sp(4)")
print(f"    r - s = {r_eval - s_eval} = {6} = k/lam")
print(f"    k - s = {k - s_eval} = {16} = s^2")
print(f"    k + r = {k + r_eval} = {14} = dim G_2")
print(f"    k + |s| = {k + abs(s_eval)} = {16} = s^2")
print(f"    f*r = {f_mult*r_eval} = {48} = |binary octahedral| = |O*|")
print(f"    g*|s| = {g_mult*abs(s_eval)} = {60} = |A_5| = |icosahedr|")

# Products with multiplicities
print(f"\n  Weighted products:")
print(f"    f*r^2 = {f_mult*r_eval**2} = {96}")
print(f"    g*s^2 = {g_mult*s_eval**2} = {240} = E!")
print(f"    k^2 = {k**2} = {144}")
print(f"    Tr(A^2) = {moments[2]} = 480 = 2E")

# The g*s^2 = E discovery is HUGE!
print(f"\n  *** g * s^2 = {g_mult} * {s_eval**2} = {g_mult*s_eval**2} = E = {E} ***")
print(f"  The 'heavy' modes carry EXACTLY the edge energy!")

# What about f*r^2 = 96?
# 96 = 2^5 * 3 = 4! * 4 = v - k + f + g + ...
# 96 = 2*48 = 2*|O*|
# 96 = 4*24 = mu*f
print(f"  f*r^2 = {96} = mu*f = {mu}*{f_mult}")
print(f"  k^2 = {144} = v*mu - k = {v*mu - k}? No, {v*mu-k} != 144")
print(f"  k^2 = {144} = 12^2 = (k/lam * lam)^2")

# ══════════════════════════════════════════════════════
# THE PARTITION OF Tr(A^2)
# ══════════════════════════════════════════════════════
print("\n" + "="*80)
print("  THE PARTITION OF Tr(A^2) = 480")
print("="*80)

print(f"""
  Tr(A^2) = k^2 + f*r^2 + g*s^2
          = {k**2} + {f_mult*r_eval**2} + {g_mult*s_eval**2}
          = {k**2} + {f_mult*r_eval**2} + {g_mult*s_eval**2}
          = 144 + 96 + 240
  
  The three contributions:
    k^2      = 144 = 12^2 (vacuum/gravity)
    f*r^2    =  96 = mu*f (matter-gauge coupling)  
    g*s^2    = 240 = E (heavy/edge sector)
  
  Note: g*s^2 = E exactly! This means:
    The contribution of the g = 15 "heavy" eigenspace
    to Tr(A^2) equals the number of edges.
    
  Also: Tr(A^2) = k^2 + mu*f + E
                 = k^2 + mu*f + vk/2
                 = 144 + 96 + 240 = 480
  
  Simplification: 480 = 2E = 2*240 = vk
  Check: vk = 40*12 = 480 ✓ (of course: Tr(A^2) = Σ_i d_i = vk for k-regular)
""")

# ══════════════════════════════════════════════════════
# THE M4 STRUCTURE
# ══════════════════════════════════════════════════════
print("="*80)
print("  THE PARTITION OF Tr(A^4) = 24960")
print("="*80)

m4_k = k**4
m4_f = f_mult * r_eval**4
m4_g = g_mult * s_eval**4

print(f"  k^4 = {m4_k}")
print(f"  f*r^4 = {m4_f}")
print(f"  g*s^4 = {m4_g}")
print(f"  Sum = {m4_k + m4_f + m4_g}")
print(f"\n  k^4 = {m4_k} = (k^2)^2 = 144^2 = 20736")
print(f"  f*r^4 = {m4_f} = {f_mult}*{r_eval**4}")
print(f"  g*s^4 = {m4_g} = {g_mult}*{s_eval**4} = 15*256")
print(f"  g*s^4 = {m4_g} = E * s^2 = {E}*{s_eval**2}")
print(f"  f*r^4 = {m4_f} = mu*f*r^2 = {mu}*{f_mult}*{r_eval**2}")

# So M4 = k^4 + mu*f*r^2 + E*s^2
# M4/M2 = (k^4 + mu*f*r^2 + E*s^2) / (k^2 + mu*f + E)
# = (k^4 + mu*f*r^2 + E*s^2) / vk

# Let me try a different decomposition of M4
# M4 = Tr(A^4) = Tr(A^2 * A^2) = sum_{i,j} A^2_{ij}^2
# For SRG: A^2 = kI + lam*A + mu*(J-I-A) = (k-mu)I + (lam-mu)A + mu*J
# So A^2 = (k-mu)I + (lam-mu)A + mu*J
#        = 8I - 2A + 4J

A2_check = (k-mu) * np.eye(1) + (lam-mu) * np.array([[0]]) + mu * np.ones((1,1))
print(f"\n  A^2 = (k-mu)I + (lam-mu)A + mu*J")
print(f"      = {k-mu}I + ({lam-mu})A + {mu}J")
print(f"      = 8I - 2A + 4J")

# A^2 = 8I - 2A + 4J
# Tr(A^4) = Tr((8I - 2A + 4J)^2)
# But J^2 = vJ, JA = AJ = kJ, A^2 = 8I - 2A + 4J
# (8I - 2A + 4J)^2 = 64I + 4A^2 + 16J^2 - 32A - 64J*I + 16J*... 
# This is getting complicated but we can verify:

# A^4 = (A^2)^2 = (8I - 2A + 4J)^2
# = 64I + 4A^2 + 16J^2 - 32A + 64J - 16AJ
# Hmm, let me be more careful:
# (8I - 2A + 4J)^2 
# = 64I^2 + 4A^2 + 16J^2 - 32IA + 64IJ - 16AJ
# Hmm no, cross terms are weird. Let me use eigenvalues instead.

# ══════════════════════════════════════════════════════
# THE SRG QUADRATIC: A^2 = (k-mu)I + (lam-mu)A + mu*J
# ══════════════════════════════════════════════════════
print("\n" + "="*80)
print("  THE ADJACENCY ALGEBRA RELATION: A^2 = 8I - 2A + 4J")
print("="*80)

print(f"""
  The fundamental algebraic identity of the SRG:
  
    A^2 = (k-mu)*I + (lam-mu)*A + mu*J
    A^2 = {k-mu}*I + ({lam-mu})*A + {mu}*J
    A^2 = 8I - 2A + 4J
  
  This is the DEFINING RELATION of the Bose-Mesner algebra!
  It means A satisfies a degree-2 polynomial over the algebra 
  generated by I, A, J.
  
  In terms of physics:
  - I = identity = free propagation (mass term)
  - A = adjacency = interaction (gauge coupling)
  - J = all-ones = universal coupling (gravity)
  
  The relation says:
    (interaction)^2 = 8*(free) - 2*(interaction) + 4*(gravity)
  
  Or rearranged:
    A^2 + 2A - 8I = 4J
    (A + 4)(A - 2) = 4(J - I)   [since A^2 + 2A - 8 = (A+4)(A-2)]
                                 [and 4J - 8I = ... hmm not exactly]
  
  Actually: A^2 + 2A - 8I = 4J
  Check on eigenvalues:
    k: 144 + 24 - 8 = 160 = 4*40 = 4v ✓ (J has eigenvalue v=40)
    r: 4 + 4 - 8 = 0 ✓ (J has eigenvalue 0 on orthogonal complement)
    s: 16 - 8 - 8 = 0 ✓
  
  So: A^2 + 2A - 8I = 4J
  
  The coefficients: +2 = lam, -8 = -k+mu = -(k-mu), 4 = mu
  Or: A^2 + lam*A - (k-mu)*I = mu*J
  
  This is the MASTER EQUATION of the theory:
    A^2 + lam*A - (k-mu)*I = mu*J
    
  In division algebra terms: 
    A^2 + dim(C)*A - dim(O)*I = dim(H)*J
""")

# Verify the factored form
print(f"  Factored form of the master equation:")
print(f"  A^2 + {lam}A - {k-mu}I = {mu}J")
print(f"  Left side at eigenvalue k={k}: {k**2 + lam*k - (k-mu)}")
print(f"  Right side at k: mu*v = {mu*v}")
print(f"  Match: {k**2 + lam*k - (k-mu) == mu*v}")

print(f"\n  The division algebra form:")
print(f"  A^2 + dim(C)*A - dim(O)*I = dim(H)*J")
print(f"  where C=complex, H=quaternion, O=octonion, J=universal")

# ══════════════════════════════════════════════════════
# THE 27-VERTEX SUBCONSTITUENT DEEP ANALYSIS
# ══════════════════════════════════════════════════════
print("\n" + "="*80)
print("  THE 27-VERTEX SUBCONSTITUENT: E6 DECOMPOSITION")
print("="*80)

# The non-neighbor subgraph has eigenvalues {8, 2, -1, -4}
# with multiplicities {1, 12, 8, 6}

# The 27 of E6 decomposes under various subgroups:
# Under SU(3) x SU(3) x SU(3): 27 = (3,3,1) + (1,3,3) + (3,1,3)
# That gives 9 + 9 + 9 = 27

# Under SU(3) x SU(2) x U(1) (Standard Model):
# 27 = (3,2) + (3-bar,1) + (3-bar,1) + (1,2) + (1,1) + (1,1)
# = 6 + 3 + 3 + 2 + 1 + 1 ... various decompositions

# But OUR decomposition is 27 = 1 + 12 + 8 + 6
# This corresponds to eigenspaces of the subconstituent

print(f"  27 = 1 + 12 + 8 + 6")
print(f"     = 1 + k + (k-mu) + (k/lam)")
print(f"\n  Possible group-theoretic interpretation:")
print(f"    1 = singlet")
print(f"    12 = adjoint of SU(3)xSU(2)xU(1) = dim(gauge)")  
print(f"     8 = adjoint of SU(3) or dim(O)")
print(f"     6 = fundamental of SU(4) ~ SO(6) or real of SU(3)")
print(f"\n  Alternative: under SO(8) (k-mu = 8):")
print(f"    27 = 1 + 8_v + 8_s + 8_c + 1 + 1")
print(f"    (triality of SO(8)! Three 8-dim reps)")
print(f"    But our decomp is 1+12+8+6, not 1+8+8+8+1+1")

# The SRG-native interpretation:
# 12 = k modes: connections to v0's neighbors that "go through" non-neighbors
# 8 = k-mu modes: octonion-like independent directions
# 6 = k/lam modes: paired/complementary to the lambda structure
# 1 = trivial

# Check: is the 12-dim eigenspace related to the k neighbors of v0?
# The 27 non-neighbors each connect to exactly mu = 4 of v0's 12 neighbors.
# Total nn-to-nbr edges: 27 * 4 = 108 = number of edges in the 27-graph!
# Wait, that's a coincidence? Let me check.

nn_edges_internal = 27 * (k - mu) // 2  # = 27*8/2 = 108
nn_edges_to_nbrs = 27 * mu   # = 27*4 = 108

print(f"\n  REMARKABLE COINCIDENCE:")
print(f"  Internal edges of 27-graph: {nn_edges_internal}")
print(f"  Edges from 27 non-nbrs to 12 neighbors: {nn_edges_to_nbrs}")
print(f"  EQUAL! Both = {nn_edges_internal} = {nn_edges_to_nbrs}")
print(f"  = k' * mu = k' * (k-mu) / 2")

# They're equal because k-mu = 2*mu, i.e., 8 = 2*4
print(f"  Why: k-mu = {k-mu}, 2*mu = {2*mu}")
print(f"  k - mu = 2*mu iff k = 3*mu, i.e., {k} = 3*{mu} ✓")
print(f"  This holds because k/mu = q = 3!")

# So k/mu = q = 3 means the non-neighbor graph has equal internal
# and external edge counts. This is a BALANCE condition.

# ══════════════════════════════════════════════════════
# DEEPER: THE TRIALITY OF THE NON-NEIGHBOR GRAPH
# ══════════════════════════════════════════════════════
print("\n" + "="*80)
print("  THE k/mu = q BALANCE AND ITS CONSEQUENCES")
print("="*80)

print(f"""
  k/mu = q = 3 means:
  1. Each vertex has k = q*mu = 3*4 = 12 neighbors
  2. Any non-neighbor shares mu = k/q = 4 neighbors with it
  3. Each non-neighbor has degree k-mu = (q-1)*mu = 2*4 = 8 
     within the non-neighbor cloud
  4. Total nn-internal edges = k'*(k-mu)/2 = 27*8/2 = 108
     = k'*mu = nn-to-nbr edges
  
  This BALANCE means:
    Each non-neighbor vertex distributes its k = 12 edges as:
    - mu = 4 edges to v0's neighbors
    - k-mu = 8 edges to other non-neighbors  
    - 0 edges to v0 itself
    Total: 4 + 8 + 0 = 12 = k ✓
  
  The edge distribution is:
    nn-to-nbr : nn-internal : nn-to-v0 = mu : k-mu : 0
                                        = 4  :  8   : 0
                                        = 1  :  2   : 0
    
  In the language of division algebras:
    mu = dim(H) : k-mu = dim(O) : 0
    
  The quaternions mediate the connection to the observed sector,
  while the octonions govern the internal (hidden) dynamics!
""")

# ══════════════════════════════════════════════════════
# GRAND SYNTHESIS
# ══════════════════════════════════════════════════════
print("\n" + "="*80)
print("  THE MASTER EQUATION AND ITS PHYSICAL MEANING")
print("="*80)

print(f"""
  ╔══════════════════════════════════════════════════════════════════╗
  ║  THE MASTER EQUATION OF W(3,3) PHYSICS:                        ║
  ║                                                                 ║
  ║    A^2 + dim(C)*A - dim(O)*I = dim(H)*J                       ║
  ║    A^2 +    2   *A -    8  *I =    4  *J                       ║
  ║                                                                 ║
  ║  On eigenspaces:                                                ║
  ║    Vacuum (k=12):  144 + 24 - 8 = 160 = 4*40 = dim(H)*v      ║
  ║    Matter (r=2):   4 + 4 - 8 = 0   (massless!)                ║
  ║    Heavy  (s=-4):  16 - 8 - 8 = 0   (massless!)               ║
  ║                                                                 ║
  ║  The non-trivial eigenspaces BOTH satisfy:                      ║
  ║    eigenval^2 + dim(C)*eigenval - dim(O) = 0                   ║
  ║                                                                 ║
  ║  This is the MASS-SHELL CONDITION: r and s are roots of         ║
  ║    t^2 + 2t - 8 = 0                                            ║
  ║    (t + 4)(t - 2) = 0                                          ║
  ║    t = 2 (matter) or t = -4 (heavy)                            ║
  ║                                                                 ║
  ║  In physics: particles sit on the mass shell defined by the     ║
  ║  division algebra dimensions!                                   ║
  ╚══════════════════════════════════════════════════════════════════╝
""")

# ══════════════════════════════════════════════════════
# CHECKS
# ══════════════════════════════════════════════════════
print("="*80)
print("  VERIFICATION")
print("="*80)

checks = []
def chk(name, cond):
    checks.append((name, cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

chk("M2/M0 = k = 12", Fraction(moments[2], v) == Fraction(k))
chk("M4/M2 = 52 = dim(F4)", Fraction(moments[4], moments[2]) == Fraction(52))
chk("g*s^2 = E = 240", g_mult * s_eval**2 == E)
chk("f*r^2 = mu*f = 96", f_mult * r_eval**2 == mu * f_mult)
chk("Tr(A^2) = vk = 480", moments[2] == v * k)
chk("Master: r^2 + lam*r - (k-mu) = 0", r_eval**2 + lam*r_eval - (k-mu) == 0)
chk("Master: s^2 + lam*s - (k-mu) = 0", s_eval**2 + lam*s_eval - (k-mu) == 0)
chk("Master: k^2 + lam*k - (k-mu) = mu*v", k**2 + lam*k - (k-mu) == mu*v)
chk("Discriminant = (k/lam)^2 = 36", (lam**2 + 4*(k-mu)) == (k//lam)**2)
chk("k/mu = q = 3 (balance)", k == q * mu)
chk("nn internal = nn external = 108", nn_edges_internal == nn_edges_to_nbrs)
chk("lam = dim(C), mu = dim(H), k-mu = dim(O)", lam == 2 and mu == 4 and k-mu == 8)

n_pass = sum(1 for _,c in checks if c)
print(f"\n  SOLVE_MOMENTS: {n_pass}/{len(checks)} checks pass")
