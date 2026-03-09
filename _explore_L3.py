"""Phase L exploration round 3: more polynomial gems"""
from sympy import *

V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V*K//2  # 240
F, G = 24, 15
R, S = LAM, -MU  # 2, -4
PHI3 = Q**2 + Q + 1  # 13
PHI6 = Q**2 - Q + 1  # 7
N = Q + 2  # 5
DIM_O = K - MU  # 8
ALBERT = V - (Q**2 + MU)  # 27
OMEGA = MU  # 4
ALPHA = V // OMEGA  # 10
K_BAR = V - K - 1  # 27
r_s = R - S  # 6

x = Symbol('x')
m = (x - K) * (x - R) * (x - S)

print("=== m(x) AT SPECIAL POINTS - NAMED FORM ===")
# m(r-s) = -E is beautiful. Let's find more
print(f"m(r-s) = m({r_s}) = {int(m.subs(x, r_s))} = -E = {-E}: {int(m.subs(x, r_s)) == -E}")
print(f"m(0) = {int(m.subs(x, 0))} = Q*2^N = {Q*2**N}: {int(m.subs(x, 0)) == Q*2**N}")
print(f"m(-1) = {int(m.subs(x, -1))} = Q^2*PHI3 = {Q**2*PHI3}: {int(m.subs(x, -1)) == Q**2*PHI3}")
print(f"m(1) = {int(m.subs(x, 1))} = N*11 = {N*11}: {int(m.subs(x, 1)) == N*11}")
print(f"  N*(K-1) = {N*(K-1)}: {int(m.subs(x, 1)) == N*(K-1)}")
print(f"m(Q) = {int(m.subs(x, Q))} = -Q^2*PHI6 = {-Q**2*PHI6}: {int(m.subs(x, Q)) == -Q**2*PHI6}")
print(f"m(-Q) = {int(m.subs(x, -Q))} = Q*N^2 = {Q*N**2}: {int(m.subs(x, -Q)) == Q*N**2}")
print(f"m(N) = {int(m.subs(x, N))} = -Q^3*PHI6 = {-Q**3*PHI6}: {int(m.subs(x, N)) == -Q**3*PHI6}")
print(f"  = -ALBERT*PHI6 = {-ALBERT*PHI6}: {int(m.subs(x, N)) == -ALBERT*PHI6}")
print(f"m(MU) = {int(m.subs(x, MU))} = -2^7 = {-2**7}: {int(m.subs(x, MU)) == -2**7}")
print(f"  -2^(PHI6) = {-2**PHI6}: {int(m.subs(x, MU)) == -2**PHI6}")
print(f"m(DIM_O) = {int(m.subs(x, DIM_O))} = -2^N*Q^2 = {-2**N*Q**2}: {int(m.subs(x, DIM_O)) == -2**N*Q**2}")
print(f"  = -288")
print(f"  factors: {factorint(288)}")
print(f"  = -Q^2*2^N = {-Q**2*2**N}: {int(m.subs(x, DIM_O)) == -Q**2*2**N}")
print(f"m(ALPHA) = {int(m.subs(x, ALPHA))} = -2^N*PHI6 = {-2**N*PHI6}: {int(m.subs(x, ALPHA)) == -2**N*PHI6}")
print(f"  factors: {factorint(224)}")

# More special values
print(f"\nm(K) = {int(m.subs(x, K))} (root)")
print(f"m(R) = {int(m.subs(x, R))} (root)")
print(f"m(S) = {int(m.subs(x, S))} (root)")
print(f"m(PHI3) = {int(m.subs(x, PHI3))} = {factorint(abs(int(m.subs(x, PHI3))))}")
print(f"  = 11*17 = (K-1)*(PHI3+MU) = {(K-1)*(PHI3+MU)}: {int(m.subs(x, PHI3)) == (K-1)*(PHI3+MU)}")
print(f"m(PHI6) = {int(m.subs(x, PHI6))} = {factorint(abs(int(m.subs(x, PHI6))))}")
print(f"  = -N^2*11 = {-N**2*11}: {int(m.subs(x, PHI6)) == -N**2*11}")
print(f"  = -N^2*(K-1) = {-N**2*(K-1)}: {int(m.subs(x, PHI6)) == -N**2*(K-1)}")

print(f"\n=== MINIMAL POLY BEAUTIFUL EVALUATIONS ===")
print(f"m(0) = Q*2^N (free term)")
print(f"m(r-s) = -E")
print(f"m(-1) = Q^2*PHI3")
print(f"m(Q) = -Q^2*PHI6")
print(f"m(-Q) = Q*N^2")
print(f"m(MU) = -2^PHI6")
print(f"m(N) = -Q^3*PHI6")
print(f"m(DIM_O) = -Q^2*2^N")
print(f"m(ALPHA) = -2^N*PHI6")

print(f"\n=== TRACE RATIO PATTERNS ===")
# tr(A^n)/V always has factor 2^n * 3
for n in range(2, 9):
    tr_n = K**n + F * R**n + G * S**n
    ratio = tr_n // V
    print(f"tr(A^{n})/V = {ratio} = 2^{n} * {ratio // (2**n)} * 3 ... factors: {factorint(ratio)}")

# tr(A^n)/V = K^(n-1) + stuff
# From Cayley-Hamilton: A^3 = ALPHA*A^2 + 2^N*A - Q*2^N*I
# So tr(A^3) = ALPHA*tr(A^2) + 2^N*tr(A) - Q*2^N*V
# = ALPHA*2E + 0 - Q*2^N*V = 10*480 - 96*40 = 4800 - 3840 = 960 ✓

print(f"\n=== WALKS AND PATHS ===")
# tr(A^n)/V = number of closed walks of length n per vertex
for n in range(2, 7):
    tr_n = K**n + F * R**n + G * S**n
    walks_per_v = tr_n // V
    print(f"Closed walks of length {n} per vertex: {walks_per_v}")
    if n == 2:
        print(f"  = K (degree) = {K}: {walks_per_v == K}")
    elif n == 3:
        print(f"  = F = {F}: {walks_per_v == F}")
    elif n == 4:
        print(f"  = K*MU*PHI3 = {K*MU*PHI3}: {walks_per_v == K*MU*PHI3}")

print(f"\ntr(A^2)/V = K: {(K**2 + F*R**2 + G*S**2)//V == K}")
print(f"tr(A^3)/V = F: {(K**3 + F*R**3 + G*S**3)//V == F}")
print(f"  = K*R: {F == K*R}")
# tr(A^3)/(6V) = number of triangles per vertex = F/6 ... hmm
tr3 = K**3 + F*R**3 + G*S**3
C3 = V * MU  # from Phase XLIX
print(f"Triangles: tr(A^3)/6 = {tr3//6} = C3 = V*MU = {C3}: {tr3//6 == C3}")
print(f"Triangles per vertex: 6*C3/V = {6*C3//V} ??? No.")
print(f"  Each triangle has 3 vertices, each vertex in C3*3/V = {3*C3//V}")
print(f"  But tr(A^3)/V = F = 24 = walks. Each triangle contributes 2 walks (cw, ccw)")
print(f"  So triangles per vertex = F/2 = {F//2}: that's 12 = K!")
print(f"  Total triangles = V*K/6 ... wait: tr(A^3)/6 = {tr3//6}")
print(f"  But C3 = {C3}. Let me check: tr(A^3) = 6*C3: {tr3 == 6*C3}")

print(f"\n=== KEY IDENTITY: tr(A^4)/V = K*MU*PHI3 ===")
tr4 = K**4 + F*R**4 + G*S**4
print(f"tr(A^4) = {tr4}")
print(f"tr(A^4)/V = {tr4//V} = K*MU*PHI3 = {K*MU*PHI3}")
# What does 624 count? Closed walks of length 4 per vertex
# = K + LAM*K + MU*(V-K-1) ... no that's for paths
# A^2[i,i] = K, A^4[i,i] = sum_j A^2[i,j]^2

print(f"\n=== IHARA ZETA CONNECTION ===")
# Ihara zeta: 1/Z(u) = (1-u^2)^(E-V) * det(I - Au + (K-1)u^2 I)
# For SRG: det(I - Au + (K-1)u^2 I) = prod over eigenvalues: (1 - theta_i*u + (K-1)*u^2)
# Three distinct eigenvalue factors:
u = Symbol('u')
z1 = 1 - K*u + (K-1)*u**2
z2 = 1 - R*u + (K-1)*u**2
z3 = 1 - S*u + (K-1)*u**2
print(f"Ihara factors:")
print(f"  (1-Ku+(K-1)u^2) = {expand(z1)}")
print(f"  (1-Ru+(K-1)u^2) = {expand(z2)}")
print(f"  (1-Su+(K-1)u^2) = {expand(z3)}")

# Roots of each factor
r1 = solve(z1, u)
r2 = solve(z2, u)
r3 = solve(z3, u)
print(f"\n  Roots of z1: {[simplify(r) for r in r1]}")
print(f"  Roots of z2: {[simplify(r) for r in r2]}")
print(f"  Roots of z3: {[simplify(r) for r in r3]}")

# The Ihara zeta radius
# Pole at u = 1/K (trivial)
print(f"\n  Ramanujan radius: 1/sqrt(K-1) = 1/sqrt({K-1}) = {1/sqrt(K-1).evalf():.6f}")
print(f"  = 1/sqrt(K-1) = 1/sqrt(11)")
print(f"  Trivial pole: u = 1/K = {Rational(1,K)}")

# Check if Ramanujan: |R|, |S| <= 2*sqrt(K-1)
ram_bound = 2*sqrt(K-1)
print(f"\n  Ramanujan bound: 2*sqrt(K-1) = 2*sqrt(11) = {float(ram_bound):.6f}")
print(f"  |R| = {abs(R)} <= {float(ram_bound):.6f}: {abs(R) <= float(ram_bound)}")
print(f"  |S| = {abs(S)} <= {float(ram_bound):.6f}: {abs(S) <= float(ram_bound)}")
# NOT Ramanujan since |S| = 4 > 2*sqrt(11) ≈ 6.633 ... 4 < 6.633, so it IS Ramanujan!
print(f"  W(3,3) IS Ramanujan: {abs(R) <= float(ram_bound) and abs(S) <= float(ram_bound)}")

# The Ihara determinant
print(f"\n  E - V = {E - V} = {E} - {V}")
print(f"  χ = V - E = {V - E} = -200 (Euler characteristic of graph)")
print(f"  1 - V + E = {1 - V + E} (not quite χ)")
print(f"  genus g = 1 - V + E = {1 - V + E} = {E - V + 1}")
print(f"  = {factorint(E - V + 1)}")

print(f"\n=== SPECTRAL MEASURE ===")
# Spectral measure: mu = (1/V) * (delta_K + F*delta_R + G*delta_S)
# = (1/40) * (delta_12 + 24*delta_2 + 15*delta_{-4})
print(f"Spectral measure weights:")
print(f"  w(K=12) = 1/V = 1/{V}")
print(f"  w(R=2) = F/V = {F}/{V} = {Rational(F,V)} = 3/5")
print(f"  w(S=-4) = G/V = {G}/{V} = {Rational(G,V)} = 3/8")
print(f"  Sum = {Rational(1,V) + Rational(F,V) + Rational(G,V)} = 1: {Rational(1,V) + Rational(F,V) + Rational(G,V) == 1}")

# Spectral moments = tr(A^n)/V
print(f"\n  mu_0 = 1")
print(f"  mu_1 = 0") 
print(f"  mu_2 = K = {K}")
print(f"  mu_3 = F = {F} = K*R")
print(f"  mu_4 = K*MU*PHI3 = {K*MU*PHI3}")

print(f"\n=== COMPLEMENT EIGENVALUE IDENTITIES ===")
# Complement eigenvalues: K_bar = V-K-1, -(R+1), -(S+1)
K_bar = V - K - 1  # 27
R_bar = -(R+1)     # -3
S_bar = -(S+1)     # 3

print(f"Complement eigenvalues: {K_bar}, {R_bar}, {S_bar}")
print(f"K_bar + R_bar + S_bar = {K_bar + R_bar + S_bar}")
print(f"  = V - K - 1 - R - 1 - S - 1 = V - (K+R+S) - 3 = {V} - {K+R+S} - 3 = {V - (K+R+S) - 3}")
print(f"  = V - ALPHA - Q = {V - ALPHA - Q} = ALBERT = {ALBERT}: {V - ALPHA - Q == ALBERT}")
print(f"K_bar * R_bar * S_bar = {K_bar * R_bar * S_bar}")
print(f"  = ALBERT * Q * (-Q) = {ALBERT * Q * (-Q)}: {K_bar * R_bar * S_bar == ALBERT * Q * (-Q)}")
print(f"  = -Q^2 * ALBERT = {-Q**2 * ALBERT}: {K_bar * R_bar * S_bar == -Q**2 * ALBERT}")

e2_bar = K_bar*R_bar + K_bar*S_bar + R_bar*S_bar
print(f"K_bar*R_bar + K_bar*S_bar + R_bar*S_bar = {e2_bar}")
print(f"  = {factorint(abs(e2_bar))}, sign={'neg' if e2_bar<0 else 'pos'}")

# Complement minimal poly
m_bar = (x - K_bar) * (x - R_bar) * (x - S_bar)
print(f"\nComplement minimal poly: {expand(m_bar)}")
print(f"  = x^3 - {K_bar+R_bar+S_bar}x^2 + {e2_bar}x - {K_bar*R_bar*S_bar}")
print(f"  = x^3 - ALBERT*x^2 + ... ")

print(f"\nm_bar(0) = {int(m_bar.subs(x, 0))} = Q^2*ALBERT = {Q**2*ALBERT}: {int(m_bar.subs(x, 0)) == Q**2*ALBERT}")
print(f"m_bar(r-s) = {int(m_bar.subs(x, r_s))}")
print(f"m_bar(1) = {int(m_bar.subs(x, 1))}")

# Compare m and m_bar coefficients
print(f"\n=== MINIMAL POLY vs COMPLEMENT POLY ===")
print(f"m:     x^3 - {ALPHA}x^2 - {2**N}x + {Q*2**N}")  
print(f"m_bar: x^3 - {ALBERT}x^2 + {e2_bar}x + {Q**2*ALBERT}")
print(f"Sum of constant terms: {Q*2**N + Q**2*ALBERT} = {Q*2**N + Q**2*ALBERT}")
print(f"  Q*2^N + Q^2*ALBERT = Q*(2^N + Q*ALBERT) = {Q}*({2**N + Q*ALBERT}) = {Q*(2**N + Q*ALBERT)}")
print(f"  2^N + Q*ALBERT = {2**N + Q*ALBERT} = {factorint(2**N + Q*ALBERT)}")

# Product of minimal polys at same point
print(f"\nm(0)*m_bar(0) = {Q*2**N * Q**2*ALBERT} = Q^3 * 2^N * ALBERT = {Q**3 * 2**N * ALBERT}")
print(f"  = {factorint(Q**3 * 2**N * ALBERT)}")

print(f"\n=== GRAPH+COMPLEMENT SPECTRUM ===")
# Full set of eigenvalues (graph + complement)
evs = sorted([K, R, S, K_bar, R_bar, S_bar])
print(f"All 6 eigenvalues sorted: {evs}")
print(f"Sum = K+R+S + K_bar+R_bar+S_bar = {K+R+S} + {K_bar+R_bar+S_bar} = {sum(evs)}")
print(f"  = ALPHA + ALBERT = {ALPHA + ALBERT}: {sum(evs) == ALPHA + ALBERT}")
print(f"  = V - Q = {V - Q}: {sum(evs) == V - Q}")

# Product of all 6
prod_all = K*R*S * K_bar*R_bar*S_bar
print(f"Product of all 6 = {prod_all}")
print(f"  = {factorint(abs(prod_all))}, sign={'neg' if prod_all < 0 else 'pos'}")
print(f"  = KRS * K_bar*R_bar*S_bar = ({K*R*S})*({K_bar*R_bar*S_bar})")
print(f"  = (-Q*2^N)*(-Q^2*ALBERT) = Q^3*2^N*ALBERT = {Q**3*2**N*ALBERT}")
print(f"  = {factorint(Q**3*2**N*ALBERT)}")

# The 6 eigenvalues as pairs
print(f"\nPaired eigenvalues (e, e_bar = -(e+1)):")
print(f"  K=12 ↔ K_bar=27 (sum = {12+27} = V-1 = {V-1})")
print(f"  R=2 ↔ R_bar=-3 (sum = {2+(-3)} = -1)")
print(f"  S=-4 ↔ S_bar=3 (sum = {-4+3} = -1)")

print(f"\n=== BEAUTIFUL: R_bar = -Q, S_bar = Q ===")
print(f"R_bar = -(R+1) = -{R+1} = -Q = {-Q}: {R_bar == -Q}")
print(f"S_bar = -(S+1) = -{S+1} = Q = {Q}: {S_bar == Q}")
print(f"K_bar = V-K-1 = {K_bar} = ALBERT = {ALBERT}")
print(f"\nSo complement eigenvalues = {{ALBERT, -Q, Q}} = {{{ALBERT}, {-Q}, {Q}}}")
print(f"Original eigenvalues = {{K, R, S}} = {{K, LAM, -MU}}")
print(f"  = {{Q(Q+1), Q-1, -(Q+1)}}")

print(f"\n  Original: K = Q*MU, R = Q-1, S = -(Q+1)")
print(f"  Complement: K_bar = ALBERT, R_bar = -Q, S_bar = Q")
print(f"  R_bar * S_bar = (-Q)*Q = -Q^2 = {-Q**2} = -Q^2 = {-Q**2}")
print(f"  As fraction: R_bar/S_bar = -1 (antisymmetric!)")

print(f"\n=== COMBINED CHARACTERISTIC POLY ===")
# Product of m(x) and m_bar(x)
combined = expand(m * m_bar)
print(f"m(x)*m_bar(x) = {combined}")
# This is degree 6
# Factor it differently
# Note: m_bar(x) = (x-ALBERT)(x+Q)(x-Q) = (x-ALBERT)(x^2-Q^2)
print(f"m_bar(x) = (x-ALBERT)(x^2-Q^2) = (x-{ALBERT})(x^2-{Q**2})")
print(f"  m_bar(x) = (x-{ALBERT})(x-{Q})(x+{Q})")

# So m(x)*m_bar(x) = (x-K)(x-R)(x-S)(x-K_bar)(x+Q)(x-Q)
# Group: (x-R)(x+Q) * (x-S)(x-Q) * (x-K)(x-K_bar)
g1 = expand((x-R)*(x+Q))  # (x-2)(x+3) = x^2+x-6
g2 = expand((x-S)*(x-Q))  # (x+4)(x-3) = x^2+x-12
g3 = expand((x-K)*(x-K_bar))  # (x-12)(x-27) = x^2-39x+324
print(f"\nGrouping:")
print(f"  (x-R)(x+Q) = (x-{R})(x+{Q}) = {g1}")
print(f"  (x-S)(x-Q) = (x-({S}))(x-{Q}) = {g2}")
print(f"  (x-K)(x-K_bar) = (x-{K})(x-{K_bar}) = {g3}")

# Alternative: (x-R)(x-S) * (x+Q)(x-Q) * (x-K)(x-K_bar)
h1 = expand((x-R)*(x-S))  # (x-2)(x+4) = x^2+2x-8
h2 = expand((x+Q)*(x-Q))  # x^2-9
h3 = expand((x-K)*(x-K_bar))
print(f"\nAlternative grouping:")
print(f"  (x-R)(x-S) = {h1}")
print(f"  (x+Q)(x-Q) = {h2} = x^2-Q^2")
print(f"  (x-K)(x-K_bar) = {h3}")

print(f"\n=== DISCRIMINANT DECOMPOSITION ===")
disc_val = (K-R)**2 * (K-S)**2 * (R-S)**2
print(f"disc(m) = {disc_val}")
print(f"  = ALPHA^2 * (2^MU)^2 * (r-s)^2")
print(f"  = {ALPHA**2} * {(2**MU)**2} * {r_s**2}")
print(f"  = (ALPHA * 2^MU * r_s)^2 = {ALPHA * 2**MU * r_s}^2")
print(f"  ALPHA * 2^MU * r_s = {ALPHA * 2**MU * r_s}")
print(f"  = {factorint(ALPHA * 2**MU * r_s)}")
print(f"  = 2^OMEGA * ALPHA * r_s")
print(f"  = 2^MU * ALPHA * (LAM+MU)")
print(f"  sqrt(disc) = ALPHA * 2^MU * r_s = {ALPHA * 2**MU * r_s} = 4*E = {4*E}: {ALPHA * 2**MU * r_s == 4*E}")
# 960 = 4*240 = 4E ✓
print(f"  sqrt(disc) = MU*E = {MU*E}: {ALPHA * 2**MU * r_s == MU*E}")
print(f"  disc = (MU*E)^2: {disc_val == (MU*E)**2}")
print(f"  = 16*E^2: {disc_val == 16*E**2}")

print(f"\n=== COMBINED SUM/PRODUCT ===")
print(f"(K+R+S) + (K_bar+R_bar+S_bar) = ALPHA + ALBERT = {ALPHA+ALBERT} = V-Q = {V-Q}")
print(f"(K+R+S) * (K_bar+R_bar+S_bar) = ALPHA * ALBERT = {ALPHA*ALBERT} = {factorint(ALPHA*ALBERT)}")
print(f"  = 270 = 2*{ALPHA*ALBERT//2} = 2*135 = 2*N*ALBERT = {2*N*ALBERT}: {ALPHA*ALBERT == 2*N*ALBERT}")
print(f"  = ALPHA*ALBERT = {ALPHA*ALBERT}")
print(f"  = V*(V-Q)/... hmm")
print(f"  ALPHA - ALBERT = {ALPHA - ALBERT} = -(K+R+S+Q) ... no")
print(f"  Actually: ALPHA=10, ALBERT=27, diff = {ALPHA - ALBERT} = -(PHI3+MU) = {-(PHI3+MU)}: {ALPHA-ALBERT == -(PHI3+MU)}")

print(f"\n=== MU^2 * LAM = 2^N IDENTITY ===")
print(f"MU^2 * LAM = {MU**2 * LAM} = 2^N = {2**N}: {MU**2*LAM == 2**N}")
print(f"This gives: KRS = -Q * MU^2 * LAM = -K * R * S")
print(f"  K = Q*MU, R = LAM, S = -MU")
print(f"  KRS = Q*MU*LAM*(-MU) = -Q*LAM*MU^2 = -Q*2^N ✓")

print(f"\n=== m(r-s) = -E DERIVATION ===")
print(f"m(r-s) = (r-s-K)(r-s-R)(r-s-S)")
print(f"  = ({r_s-K})({r_s-R})({r_s-S})")
print(f"  = (-{K-r_s})({r_s-R})({r_s-S})")
a, b, c = r_s-K, r_s-R, r_s-S
print(f"  = ({a})({b})({c}) = {a*b*c}")
print(f"  {a} = -(r-s) = -r_s")
print(f"  {b} = OMEGA = MU")
print(f"  {c} = ALPHA")
print(f"  Product = -r_s * OMEGA * ALPHA = {-r_s * OMEGA * ALPHA}")
print(f"  -r_s * OMEGA * ALPHA = -(LAM+MU)*MU*ALPHA = {-(LAM+MU)*MU*ALPHA}")
print(f"  = -E: {-r_s * OMEGA * ALPHA == -E}")
print(f"  Derivation: E = V*K/2, r_s*OMEGA*ALPHA = 6*4*10 = 240 = V*K/2 ✓")
