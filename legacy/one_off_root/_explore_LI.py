"""Phase LI exploration: Idempotent Algebra & Projection Geometry

The adjacency matrix A of W(3,3) generates a 3-dim matrix algebra.
The three primitive idempotents E_0, E_1, E_2 project onto the
eigenspaces of dimensions 1, F=24, G=15. Their algebraic properties
encode deep geometry.
"""
from fractions import Fraction as Fr

V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V*K//2  # 240
R, S = 2, -4
F, G = 24, 15
N = Q + 2      # 5
THETA = K - R   # 10
ALPHA = V // MU  # 10
OMEGA = MU       # 4
DIM_O = K - MU   # 8
ALBERT = V - (Q**2 + MU)  # 27
PHI3 = Q**2 + Q + 1  # 13
PHI6 = Q**2 - Q + 1  # 7
K_BAR = V - 1 - K     # 27
r_s = R - S            # 6

print("=" * 60)
print("IDEMPOTENT ALGEBRA & PROJECTION GEOMETRY")
print("=" * 60)

# Three primitive idempotents of the Bose-Mesner algebra
# E_0 = J/V (all-ones)
# E_1 = (F/V) * projection onto r-eigenspace (dim F=24)
# E_2 = (G/V) * projection onto s-eigenspace (dim G=15)
#
# In terms of A: E_i = product of (A - theta_j*I)/(theta_i - theta_j) for j != i

print("\n=== PRIMITIVE IDEMPOTENT EXPRESSIONS ===")
# E_0 = (A-R*I)(A-S*I) / ((K-R)(K-S))
# E_1 = (A-K*I)(A-S*I) / ((R-K)(R-S))
# E_2 = (A-K*I)(A-R*I) / ((S-K)(S-R))

# Denominators
d0 = (K - R) * (K - S)  # ALPHA * 2^MU = 10*16 = 160
d1 = (R - K) * (R - S)  # (-ALPHA) * r_s = -60
d2 = (S - K) * (S - R)  # (-2^MU) * (-r_s) = 96

print(f"Denominators:")
print(f"  d0 = (K-R)(K-S) = {K-R}*{K-S} = {d0}")
print(f"     = ALPHA * 2^MU = {ALPHA} * {2**MU} = {ALPHA * 2**MU}: {d0 == ALPHA * 2**MU}")
print(f"  d1 = (R-K)(R-S) = {R-K}*{R-S} = {d1}")
print(f"     = -ALPHA * r_s = {-ALPHA * r_s}: {d1 == -ALPHA * r_s}")
print(f"  d2 = (S-K)(S-R) = {S-K}*{S-R} = {d2}")
print(f"     = -2^MU * (-r_s) = {(-2**MU) * (-r_s)}: {d2 == 2**MU * r_s}")
print(f"     = Q * 2^N = {Q * 2**N}: {d2 == Q * 2**N}")

print(f"\n  d0 = {d0} = V * MU = {V*MU}: {d0 == V*MU}")
print(f"  d1 = {d1} = -V*MU/... hmm")
print(f"  d0 * d1 * d2 = {d0 * d1 * d2}")
print(f"  = -(ALPHA * 2^MU * r_s)^2 wait no")
# d0*d1 = (K-R)(K-S)(R-K)(R-S) = -(K-R)^2 * (K-S) * (R-S)
# d0*d1*d2 = -(K-R)^2 * (K-S)^2 * (R-S)^2 ... that's -disc
print(f"  d0 * d1 * d2 = {d0*d1*d2}")
print(f"  -disc(m) = {-921600}: {d0*d1*d2 == -921600}")
# d0*d1*d2 = (K-R)(K-S) * (R-K)(R-S) * (S-K)(S-R)
# = -(K-R)^2 * -(K-S)^2 * -(R-S)^2 ... no let me be careful
# = [(K-R)(R-K)] * [(K-S)(S-K)] * [(R-S)(S-R)]
# = [-(K-R)^2] * [-(K-S)^2] * [-(R-S)^2]
# = -disc
print(f"  Confirmed: d0*d1*d2 = -disc(m) = -(MU*E)^2")

print(f"\n=== IDEMPOTENT NUMERATOR POLYNOMIALS ===")
# N_0(x) = (x-R)(x-S) = x^2 - (R+S)x + RS = x^2 + LAM*x - DIM_O
# N_1(x) = (x-K)(x-S) = x^2 - (K+S)x + KS = x^2 - DIM_O*x - V_something
# N_2(x) = (x-K)(x-R) = x^2 - (K+R)x + KR = x^2 - 2*PHI6*x + F
print(f"N_0(x) = (x-R)(x-S) = x^2 + {LAM}x - {DIM_O}")
print(f"N_1(x) = (x-K)(x-S) = x^2 - {K+S}x + {K*S}")
print(f"       = x^2 - DIM_O*x - {abs(K*S)}")
print(f"       K*S = {K*S} = -{V+DIM_O} = -48: {K*S == -(V+DIM_O)}")
# Actually K*S = 12*(-4) = -48
print(f"       = -MU*K = {-MU*K}: {K*S == -MU*K}")
# -48 = -4*12 = -MU*K ✓
print(f"N_2(x) = (x-K)(x-R) = x^2 - {K+R}x + {K*R}")
print(f"       = x^2 - 2*PHI6*x + F")

print(f"\n=== IDEMPOTENT TRACES ===")
# tr(E_i) = dim of eigenspace = {1, F, G}
# But also tr(E_i) = sum over eigenvalues of E_i at each eigenvalue
# E_0 at eigenvalue K: N_0(K)/d0 = (K-R)(K-S)/d0 = d0/d0 = 1
# E_0 at eigenvalue R: N_0(R)/d0 = 0 (since R is a root)
# E_0 at eigenvalue S: N_0(S)/d0 = 0
# So tr(E_0) = 1*1 + F*0 + G*0 = 1 ✓

# E_1 at eigenvalue K: N_1(K)/d1 = (K-K)(K-S)/d1 = 0
# E_1 at eigenvalue R: N_1(R)/d1 = (R-K)(R-S)/d1 = d1/d1 = 1
# E_1 at eigenvalue S: N_1(S)/d1 = (S-K)(S-S)/d1 = 0
# So tr(E_1) = 0 + F*1 + 0 = F = 24 ✓

print(f"tr(E_0) = 1")
print(f"tr(E_1) = F = {F}")
print(f"tr(E_2) = G = {G}")
print(f"Sum = 1 + F + G = {1+F+G} = V = {V}: {1+F+G == V}")

print(f"\n=== HADAMARD (ENTRYWISE) PRODUCTS OF IDEMPOTENTS ===")
# Krein parameters: E_i ∘ E_j = (1/V) * sum_k q^k_{ij} E_k
# From Phase XLIX, all 6 non-trivial Krein params have denominator Q

# q^k_{ij} values from the eigenmatrix and dual eigenmatrix
# Using the first eigenmatrix P:
# P = [[1, K, K_BAR],  where K_BAR = ALBERT = 27 (complement eigenvalue)
#      [1, R, -(R+1)],
#      [1, S, -(S+1)]]
# = [[1, 12, 27], [1, 2, -3], [1, -4, 3]]

# The dual matrix Q = V * P^(-1) (not to be confused with q=3)
# Q has columns that give the Krein parameters

# From Phase XLIX we verified:
# q^1_{11} = MU*(K-1)/Q = 44/3
# q^2_{11} = V/Q = 40/3
# q^1_{22} = MU*N/Q = 20/3
# q^2_{22} = ALPHA/Q = 10/3
# q^1_{12} = N^2/Q = 25/3
# q^2_{12} = DIM_O*MU/Q = 32/3

print(f"Krein parameters (all with denominator Q={Q}):")
q1_11 = Fr(MU * (K-1), Q)
q2_11 = Fr(V, Q)
q1_22 = Fr(MU * N, Q)
q2_22 = Fr(ALPHA, Q)
q1_12 = Fr(N**2, Q)
q2_12 = Fr(DIM_O * MU, Q)

print(f"  q^1_{{11}} = {q1_11}")
print(f"  q^2_{{11}} = {q2_11}")
print(f"  q^1_{{22}} = {q1_22}")
print(f"  q^2_{{22}} = {q2_22}")
print(f"  q^1_{{12}} = {q1_12}")
print(f"  q^2_{{12}} = {q2_12}")

# Sum of Krein parameters for each pair (i,j)
# sum_k q^k_{ij} = F*G/V for i != j (from Krein conditions)
# sum_k q^k_{11} = F*(F+1)/(2V) ... no
# Actually: sum_k q^k_{ij} * dim(E_k) = dim(E_i) * dim(E_j/V)
# The Krein condition is: E_i ∘ E_j = (1/V) sum_k q^k_{ij} E_k
# Trace both sides: dim(E_j)/V * [j==i] = (1/V)(q^0_{ij}*1 + q^1_{ij}*F + q^2_{ij}*G)
# Wait, that's not quite right either.

# Sum identity: q^0_{ij} + q^1_{ij} + q^2_{ij} = some known thing
# For self-dual graphs with 3 classes, sum_k q^k_{ij} depends on structure
# Actually q^0_{ij} = delta_{ij} * dim(E_i) for the trivial Krein param

print(f"\n=== IDEMPOTENT DIMENSIONS AS FRACTIONS ===")
print(f"F/V = {Fr(F,V)} = {float(Fr(F,V)):.6f}")
print(f"G/V = {Fr(G,V)} = {float(Fr(G,V)):.6f}")
print(f"F/G = {Fr(F,G)} = {float(Fr(F,G)):.6f}")
print(f"  = 8/5 = DIM_O/N: {Fr(F,G) == Fr(DIM_O, N)}")
print(f"F*G = {F*G} = 360 = E + 2*E/2 ... = {E+E//2}")
print(f"F*G = {F*G} = {E}+{F*G-E} = E+120")
print(f"  = V*Q^2 = {V*Q**2}: {F*G == V*Q**2}")
# 360 = 40*9 = V*Q^2 ✓
print(f"  = 2*E*Q/MU = {2*E*Q//MU}: {F*G == 2*E*Q//MU}")
# 360 = 2*240*3/4 = 360 ✓
print(f"F*G/V = Q^2 = {Q**2}: {F*G//V == Q**2}")
print(f"(F-1)*(G-1) = {(F-1)*(G-1)} = {23*14}")
print(f"  = 322 = 2*7*23")

print(f"\n=== EIGENMATRIX P (FIRST KIND) ===")
# Standard SRG eigenmatrix
P = [[1, K, K_BAR], [1, R, -(R+1)], [1, S, -(S+1)]]
print(f"P = [[1, K, K_BAR], [1, R, -(R+1)], [1, S, -(S+1)]]")
print(f"  = [[1, {K}, {K_BAR}], [1, {R}, {-(R+1)}], [1, {S}, {-(S+1)}]]")

# Column sums
cs = [sum(P[i][j] for i in range(3)) for j in range(3)]
print(f"Column sums: {cs}")
print(f"  = [3, K+R+S, K_BAR-(R+1)-(S+1)] = [3, ALPHA, ALBERT-R+S-2]")
KRS_cs = K_BAR - (R+1) - (S+1)
print(f"  Third col sum = {KRS_cs} = K_BAR - (R+S+2) = {K_BAR} - {R+S+2} = {K_BAR-R-S-2}")
print(f"  = ALBERT + LAM = {ALBERT + LAM}: {KRS_cs == ALBERT + LAM}")
# 27 - 2 + 4 - 2 = 27... check: 27 - (2+1) - (-4+1) = 27 - 3 + 3 = 27
print(f"  Actually: {K_BAR} - {R+1} - {S+1} = {K_BAR - (R+1) - (S+1)}")

# Row sums
rs_sum = [sum(P[i]) for i in range(3)]
print(f"Row sums: {rs_sum}")
print(f"  = [1+K+K_BAR, 1+R-(R+1), 1+S-(S+1)]")
print(f"  = [V, 0, 0]")
# Row 0: 1 + K + K_BAR = 1 + K + (V-1-K) = V ✓
# Row 1: 1 + R - R - 1 = 0 ✓
# Row 2: 1 + S - S - 1 = 0 ✓
assert rs_sum == [V, 0, 0]
print(f"  Non-trivial rows sum to 0 ✓")

print(f"\n=== EIGENMATRIX DETERMINANT ===")
# det(P) = -E from Phase XLIX
# Let's verify by expanding
d = (1*(R*(-(S+1)) - (-(R+1))*S) - K*(1*(-(S+1)) - (-(R+1))*1) + K_BAR*(1*S - R*1))
print(f"det(P) = {d}")
print(f"  = -E = {-E}: {d == -E}")

print(f"\n=== DUAL EIGENMATRIX Q_MAT ===")
# Q_mat = V * P^{-1}
# Q_mat[i][j] = V * (cofactor of P[j][i]) / det(P)
# Since P @ Q_mat.T = V * I, we have Q_mat = V * P^{-1} ... actually PQ = VI
# In standard notation: Q = V * P^(-1)

# Elements of Q (from Phase XLIX):
# Q = [[1, F, G], [1, MU, -N], [1, -DIM_O/Q, N/Q]]
# Hmm wait, that was rows of Q.

print(f"Q eigenmatrix rows:")
print(f"  Row 0: [1, {F}, {G}]")
print(f"  Row 1: [1, {Fr(MU*F, K)}, {Fr(-N*G, K)}]")
# Actually let me compute Q = V * P^(-1) properly
# Q[0] = [1, f, g] (multiplicities)
# This is standard for association scheme

print(f"\n=== IDEMPOTENT ALGEBRA STRUCTURE CONSTANTS ===")
# A * E_i = theta_i * E_i (by definition)
# A = K*E_0 + R*E_1 + S*E_2 (spectral decomposition)
# I = E_0 + E_1 + E_2
# J = V*E_0

print(f"A = K*E_0 + R*E_1 + S*E_2 = {K}*E_0 + {R}*E_1 + ({S})*E_2")
print(f"I = E_0 + E_1 + E_2")
print(f"J = V*E_0 = {V}*E_0")

# A^2 = K^2*E_0 + R^2*E_1 + S^2*E_2
# tr(A^2) = K^2*1 + R^2*F + S^2*G = 2E
print(f"A^2 = {K**2}*E_0 + {R**2}*E_1 + {S**2}*E_2")

# KEY: the Hoffman polynomial H(x) such that H(A) = J
# J = V*E_0, so we need H(K) = V, H(R) = 0, H(S) = 0
# H(x) = V * (x-R)(x-S) / ((K-R)(K-S))
# = V * N_0(x) / d0
# = (V / d0) * (x-R)(x-S)
print(f"\n=== HOFFMAN POLYNOMIAL ===")
vd0 = Fr(V, d0)
print(f"H(x) = (V/d0) * (x-R)(x-S) = {vd0} * (x-{R})(x-({S}))")
print(f"V/d0 = {vd0} = V/(ALPHA*2^MU) = {Fr(V, ALPHA*2**MU)}")
print(f"  = 1/MU = {Fr(1,MU)}: {vd0 == Fr(1,MU)}")
# V/d0 = 40/160 = 1/4 = 1/MU ✓!

print(f"\nH(x) = (1/MU) * (x-R)(x-S)")
print(f"     = (1/{MU}) * (x^2 + {LAM}x - {DIM_O})")
print(f"H(K) = (1/{MU}) * (K-R)(K-S) = {K-R}*{K-S}/{MU} = {(K-R)*(K-S)//MU}")
print(f"     = ALPHA*2^MU/MU = {ALPHA*2**MU//MU} = V = {V}: {(K-R)*(K-S)//MU == V}")
print(f"H(0) = (1/{MU}) * (-R)(-S) = RS/MU = {R*S}/{MU} = {Fr(R*S, MU)}")
print(f"     = -DIM_O/MU = {Fr(-DIM_O, MU)} = -LAM = {-LAM}: {Fr(R*S, MU) == -LAM}")
print(f"H(1) = (1/{MU}) * (1-R)(1-S) = {(1-R)*(1-S)}/{MU} = {Fr((1-R)*(1-S), MU)}")
print(f"     = (-1)*N/MU = {Fr(-N, MU)}: {Fr((1-R)*(1-S), MU) == Fr(-N, MU)}")
# (1-2)(1+4)/4 = (-1)(5)/4 = -5/4 ✓

print(f"\n=== HOFFMAN CLIQUE BOUND REVISITED ===")
# Hoffman bound: omega(G) <= V * (-S) / (K - S) = V*MU / (K+MU) = 40*4/16 = 10
# = V/2^MU_half... = V*MU/2^MU
hoff = Fr(V * (-S), K - S)
print(f"Hoffman bound = V*|S|/(K-S) = V*MU/(K+MU) = {hoff}")
print(f"  = V*MU/2^MU = {Fr(V*MU, 2**MU)} = ALPHA = {ALPHA}: {hoff == ALPHA}")
# 40*4/16 = 160/16 = 10 = ALPHA ✓

# Hoffman independence number bound: alpha(G) <= V * (-R) / (K - R)... wait
# alpha(G) <= V * (1 - K/(-S)) = V * (1 + K/MU) = V * (MU+K)/MU = V*(K+MU)/MU
# Actually, Lovász bound: alpha(G) <= V * (-S)/(K-S) too? No.
# Hoffman bound for independence: alpha <= V * (-R)/(K-(-R)... 
# No: for independent set, alpha <= V - V*K/(K-S) = ... let me look this up

# Actually for SRG: omega = V/(1 - K/S) and alpha = V/(1 - K/R)
# omega = V / (1 + K/MU) = V*MU/(MU+K) = 40*4/16 = 10 = ALPHA
# alpha = V / (1 - K/R) = V*R/(R-K) = 40*2/(2-12) = 80/(-10) = -8
# That's negative, wrong formula. 
# Correct: alpha = V * (1 + K/|S|)... no.
# From Hoffman: alpha <= -V*S/(K-S) = V*MU/(K+MU) = 10. Same as omega!

print(f"\n=== PROJECTION DIMENSIONS ===")
# Dim of each eigenspace
# 1-dim: trivial (all-ones direction) 
# F-dim: 24 = dim of the r=2 eigenspace
# G-dim: 15 = dim of the s=-4 eigenspace
# F + G = V - 1 = 39

print(f"Eigenspace dimensions: 1, F={F}, G={G}")
print(f"F + G = {F+G} = V-1 = {V-1}")
print(f"F - G = {F-G} = Q^2 = {Q**2}: {F-G == Q**2}")
print(f"F * G = {F*G} = V*Q^2 = {V*Q**2}: {F*G == V*Q**2}")
print(f"F / G = DIM_O/N = {DIM_O}/{N} = {Fr(DIM_O,N)}: {Fr(F,G) == Fr(DIM_O,N)}")

# The three idempotent ranks are 1, F, G and satisfy:
# 1*F*G = F*G = V*Q^2 = 360
# 1+F+G = V = 40
# These are the elementary symmetric functions of {1, F, G}:
# sigma1 = V, sigma2 = F+G+F*G = (V-1)+V*Q^2 = 39+360 = 399
# sigma3 = F*G = V*Q^2

s1 = 1 + F + G  # V
s2 = 1*F + 1*G + F*G  # F+G+F*G = 39+360 = 399
s3 = 1 * F * G  # V*Q^2 = 360
print(f"\nSymmetric functions of {{1, F, G}}:")
print(f"  sigma1 = {s1} = V")
print(f"  sigma2 = {s2} = {F+G}+{F*G} = (V-1)+V*Q^2")
print(f"  sigma3 = {s3} = V*Q^2 = F*G")
print(f"  sigma2 = {s2}")
print(f"  = F + G + F*G = {F+G} + {F*G}")
# sigma2/V = (V-1+V*Q^2)/V
print(f"  sigma2/sigma1 = {Fr(s2,s1)} = {float(Fr(s2,s1)):.6f}")

print(f"\n=== PROJECTION ENTROPY ===")
# Shannon entropy of the spectral measure
import math
w0, w1, w2 = Fr(1,V), Fr(F,V), Fr(G,V)
H = -(float(w0)*math.log2(float(w0)) + float(w1)*math.log2(float(w1)) + float(w2)*math.log2(float(w2)))
print(f"Spectral entropy H = -{float(w0):.4f}*log2({float(w0):.4f}) - {float(w1):.4f}*log2({float(w1):.4f}) - {float(w2):.4f}*log2({float(w2):.4f})")
print(f"  = {H:.6f}")
print(f"  Max entropy = log2(3) = {math.log2(3):.6f}")
print(f"  Normalized = {H/math.log2(3):.6f}")

print(f"\n=== SEIDEL MATRIX ===")
# S_seidel = J - I - 2A
# Eigenvalues: V-1-2K = 39-24 = 15 = G (mult 1)
#              -1-2R = -1-4 = -5 = -N (mult F)
#              -1-2S = -1+8 = 7 = PHI6 (mult G)
s_k = V - 1 - 2*K
s_r = -1 - 2*R
s_s = -1 - 2*S
print(f"Seidel eigenvalues:")
print(f"  V-1-2K = {s_k} = G = {G}: {s_k == G}")
print(f"  -1-2R = {s_r} = -N = {-N}: {s_r == -N}")
print(f"  -1-2S = {s_s} = PHI6 = {PHI6}: {s_s == PHI6}")

# Seidel spectrum: {G, -N, PHI6} with mults {1, F, G}
print(f"\nSeidel spectrum: {{{G}^1, {-N}^{F}, {PHI6}^{G}}}")
print(f"  {G}, {-N}, {PHI6} — sorted: {sorted([G, -N, PHI6])}")

# Seidel polynomial det(xI - S_seidel)
print(f"\nSeidel char poly: (x-G)(x+N)^F(x-PHI6)^G")
print(f"Seidel minimal poly: (x-G)(x+N)(x-PHI6)")
print(f"  = x^3 - (G-N+PHI6)x^2 + ...")
sm_sum = G + (-N) + PHI6
sm_prod = G * (-N) * PHI6
sm_sig2 = G*(-N) + G*PHI6 + (-N)*PHI6
print(f"  Sum of Seidel eigenvalues: G-N+PHI6 = {sm_sum}")
print(f"    = G+PHI6-N = {G}+{PHI6}-{N} = {G+PHI6-N}")
# 15-5+7 = 17 = PHI3+MU = 13+4 = 17
print(f"    = PHI3+MU = {PHI3+MU}: {sm_sum == PHI3+MU}")
print(f"    = ALBERT-ALPHA = {ALBERT-ALPHA}: {sm_sum == ALBERT-ALPHA}")
# 27-10=17 ✓

print(f"  Pairwise sum: {sm_sig2}")
print(f"    = G*(-N) + G*PHI6 + (-N)*PHI6 = {G*(-N)} + {G*PHI6} + {(-N)*PHI6}")
print(f"    = {sm_sig2}")
# -75+105-35 = -5
print(f"    = -N = {-N}: {sm_sig2 == -N}")

print(f"  Product: G*(-N)*PHI6 = {sm_prod}")
print(f"    = -N*G*PHI6 = {-N*G*PHI6}")
print(f"    = -{N*G*PHI6}")
# -5*15*7 = -525
print(f"    = -Q*N^2*(V-1) ... ")
print(f"    525 = {525} = {3*5*5*7} = Q*N^2*PHI6 = {Q*N**2*PHI6}: {525 == Q*N**2*PHI6}")
print(f"    So product = -Q*N^2*PHI6 = {-Q*N**2*PHI6}: {sm_prod == -Q*N**2*PHI6}")

# Seidel minimal poly: x^3 - 17x^2 - 5x + 525
x_coeff = -sm_sig2
const = -sm_prod
print(f"\nSeidel min poly: x^3 - {sm_sum}x^2 + ({sm_sig2})x - ({sm_prod})")
print(f"  = x^3 - (ALBERT-ALPHA)x^2 - N*x + Q*N^2*PHI6")

print(f"\n=== SEIDEL DETERMINANT ===")
seidel_det = s_k * s_r**F * s_s**G
print(f"det(S_seidel) = G * (-N)^F * PHI6^G")
print(f"  = {G} * ({-N})^{F} * {PHI6}^{G}")
print(f"  sign: G>0, (-N)^F = N^F (F=24 even), PHI6^G>0")
print(f"  = G * N^F * PHI6^G")
print(f"  = {G} * {N**F} * {PHI6**G}")
print(f"  = {seidel_det}")

# S_seidel = J - I - 2A, so det(S) = det(-I-2A+J)
# This relates to det evaluated at shifted eigenvalues

print(f"\n=== LAPLACIAN MATRIX ===")
# L = K*I - A
# Eigenvalues: K-K=0, K-R=ALPHA=10, K-S=K+MU=2^MU=16
# Multiplicities: 1, F=24, G=15
l_k = K - K  # 0
l_r = K - R  # ALPHA = 10
l_s = K - S  # 2^MU = 16
print(f"Laplacian eigenvalues:")
print(f"  K-K = {l_k} (null, mult 1)")
print(f"  K-R = {l_r} = ALPHA = {ALPHA} (mult F={F})")
print(f"  K-S = {l_s} = 2^MU = {2**MU} (mult G={G})")

# Number of spanning trees (Matrix-Tree theorem)
# tau = (1/V) * prod of nonzero Laplacian eigenvalues
# = (1/V) * ALPHA^F * (2^MU)^G
tau = Fr(ALPHA**F * (2**MU)**G, V)
print(f"\nSpanning trees tau = ALPHA^F * (2^MU)^G / V")
print(f"  = {ALPHA}^{F} * {2**MU}^{G} / {V}")
print(f"  = {ALPHA**F} * {(2**MU)**G} / {V}")
# This is a huge number. Let me express it in terms of prime factorization
# ALPHA = 2*5, so ALPHA^F = 2^24 * 5^24
# (2^MU)^G = 2^(MU*G) = 2^60
# Total: 2^(24+60) * 5^24 / (2^3 * 5) = 2^81 * 5^23
print(f"  Prime factorization of numerator: 2^{24}*5^{24} * 2^{MU*G}")
print(f"    = 2^{24+MU*G} * 5^{F}")
print(f"    = 2^{24+MU*G} * 5^{F}")
# V = 40 = 2^3 * 5
print(f"    / (2^3 * 5) = 2^{24+MU*G-3} * 5^{F-1}")
print(f"    = 2^{24+MU*G-3} * 5^{F-1}")
exp2 = 24 + MU*G - 3  # 24+60-3 = 81
exp5 = F - 1  # 23
print(f"    = 2^{exp2} * 5^{exp5}")
print(f"  tau = 2^{exp2} * 5^{exp5}")
# Check: 24 + MU*G - 3 = 24+60-3 = 81
# F - 1 = 23
print(f"  MU*G = {MU*G} = 60")
print(f"  exp2 = F + MU*G - 3 = {F + MU*G - 3}")

print(f"\n=== SIGNLESS LAPLACIAN ===")
# Q_mat = K*I + A (signless Laplacian... or L+ = D + A)
# Eigenvalues: K+K=2K=F=24, K+R=14=2*PHI6, K+S=DIM_O=8
# Wait, those are 2K, K+R, K+S = F, 2*PHI6, DIM_O
q_k = K + K  # 24 = F
q_r = K + R  # 14 = 2*PHI6  
q_s = K + S  # 8 = DIM_O
print(f"Signless Laplacian eigenvalues:")
print(f"  K+K = {q_k} = F = {F} (mult 1)")
print(f"  K+R = {q_r} = 2*PHI6 = {2*PHI6} (mult F={F})")
print(f"  K+S = {q_s} = DIM_O = {DIM_O} (mult G={G})")
print(f"  = {{F, 2*PHI6, DIM_O}}")

# Signless Laplacian determinant
sl_det_num = q_k * q_r**F * q_s**G
print(f"\ndet(K*I+A) = F * (2*PHI6)^F * DIM_O^G")
print(f"  = {F} * {2*PHI6}^{F} * {DIM_O}^{G}")
# = 24 * 14^24 * 8^15
# = 2^3*3 * (2*7)^24 * 2^(3*15)
# = 2^3*3 * 2^24*7^24 * 2^45
# = 2^72 * 3 * 7^24
print(f"  = 2^72 * 3 * 7^{F} = 2^72 * Q * PHI6^{F}")
print(f"  72 = 2*(r-s)^2 = |Delta(E6)| = {2*r_s**2}")
# Check: 3+24+45 = 72 ✓

print(f"\n=== NORMALIZED LAPLACIAN ===")
# L_norm = I - D^(-1/2) A D^(-1/2) = I - A/K (since regular)
# Eigenvalues: 1 - theta/K for each theta
nl_k = Fr(K - K, K)  # 0
nl_r = Fr(K - R, K)  # ALPHA/K = 10/12 = 5/6
nl_s = Fr(K - S, K)  # (K+MU)/K = 16/12 = 4/3

print(f"Normalized Laplacian eigenvalues:")
print(f"  1-K/K = {nl_k}")
print(f"  1-R/K = {nl_r} = ALPHA/K = N/(r-s) = {Fr(N,r_s)}: {nl_r == Fr(N,r_s)}")
print(f"  1-S/K = {nl_s} = (K+MU)/K = MU/Q = {Fr(MU,Q)}: {nl_s == Fr(MU,Q)}")
# 1-2/12 = 10/12 = 5/6; N/r_s = 5/6 ✓
# 1-(-4)/12 = 16/12 = 4/3; MU/Q = 4/3 ✓

print(f"  1 - R/K = N/r_s = {Fr(N,r_s)}")
print(f"  1 - S/K = MU/Q = {Fr(MU,Q)}")
# Beautiful! The normalized Laplacian eigenvalues are N/r_s and MU/Q

print(f"\n  Sum of normalized Lap eigenvalues:")
sum_nl = nl_k + F*nl_r + G*nl_s
print(f"    0 + F*N/r_s + G*MU/Q = {F}*{Fr(N,r_s)} + {G}*{Fr(MU,Q)}")
print(f"    = {Fr(F*N,r_s)} + {Fr(G*MU,Q)} = {Fr(F*N,r_s) + Fr(G*MU,Q)}")
print(f"    = {sum_nl}")
# 24*5/6 + 15*4/3 = 20 + 20 = 40 = V
print(f"    = V = {V}: {sum_nl == V}")

# Product of nonzero normalized Lap eigenvalues
# = (N/r_s)^F * (MU/Q)^G
prod_nl = Fr(N,r_s)**F * Fr(MU,Q)**G
print(f"\n  Product of nonzero norm Lap eigenvalues:")
print(f"    = (N/r_s)^F * (MU/Q)^G")
print(f"    = ({N}/{r_s})^{F} * ({MU}/{Q})^{G}")
# = (5/6)^24 * (4/3)^15

print(f"\n=== CHARACTERISTIC POLYNOMIAL OF kI + A ===")
# det(xI - (kI+A)) at x=0 gives -det(kI+A)
# Actually p_{kI+A}(x) = (x-2k)(x-(k+r))^F(x-(k+s))^G
# = (x-F)(x-14)^F(x-8)^G since 2k=F=24, k+r=14=2Φ6, k+s=DIM_O=8
print(f"char poly of K*I+A at x=0: (-F)*(-14)^F*(-8)^G")
print(f"  = ({-F})*({-(2*PHI6)})^{F}*({-DIM_O})^{G}")
print(f"  = F*(2*PHI6)^F*DIM_O^G * (-1)^(1+F+G)")
print(f"  (-1)^(1+F+G) = (-1)^V = 1 (V even)")
print(f"  So det(K*I+A) = F*(2*PHI6)^F*DIM_O^G ✓")

print(f"\n=== MATRIX FUNCTION EVALUATIONS SUMMARY ===")
print(f"Matrix:    Eigenvalues:              Named constants:")
print(f"A          K, R, S                    Q*MU, LAM, -MU")
print(f"A_bar      ALBERT, -Q, Q             q^3, -q, q")
print(f"L = KI-A   0, ALPHA, 2^MU            0, K-R, K+MU")
print(f"K*I+A      F, 2*PHI6, DIM_O          2K, K+R, K+S")
print(f"S_seidel   G, -N, PHI6               V-1-2K, -1-2R, -1-2S")
print(f"L_norm     0, N/r_s, MU/Q            0, 5/6, 4/3")
