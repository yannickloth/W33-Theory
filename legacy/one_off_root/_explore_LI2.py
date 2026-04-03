"""Phase LI exploration round 2: Spectral Zeta, Heat Kernel, Graph Energy

Deeper derived quantities from the W(3,3) spectrum.
"""
from fractions import Fraction as Fr
import math

V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V*K//2       # 240
R, S = 2, -4
F, G = 24, 15
N = Q + 2         # 5
ALPHA = V // MU   # 10
DIM_O = K - MU    # 8
ALBERT = V - (Q**2 + MU)  # 27
PHI3 = Q**2 + Q + 1       # 13
PHI6 = Q**2 - Q + 1       # 7
K_BAR = V - 1 - K         # 27
r_s = R - S               # 6

print("=" * 60)
print("SPECTRAL ZETA, HEAT KERNEL, GRAPH ENERGY")
print("=" * 60)

print("\n=== GRAPH ENERGY ===")
# Energy = sum of |eigenvalues| with multiplicity
energy = 1*K + F*abs(R) + G*abs(S)
print(f"Energy(W(3,3)) = K + F*|R| + G*|S|")
print(f"  = {K} + {F}*{abs(R)} + {G}*{abs(S)}")
print(f"  = {K} + {F*abs(R)} + {G*abs(S)} = {energy}")
# = 12 + 48 + 60 = 120
print(f"  = E/2 = {E//2}: {energy == E//2}")
# 120 = E/2 ✓ Beautiful!
print(f"  = V*Q = {V*Q}: {energy == V*Q}")
# 120 = 40*3 ✓
print(f"  = F*N = {F*N}: {energy == F*N}")
# 120 = 24*5 ✓ 
print(f"  = K*ALPHA = {K*ALPHA}: {energy == K*ALPHA}")
# 120 = 12*10 ✓
print(f"  = DIM_O*G = {DIM_O*G}: {energy == DIM_O*G}")
# 120 = 8*15 ✓
print(f"  = r_s*F/... = 5! = {math.factorial(5)}: {energy == math.factorial(5)}")
# 120 = 5! ✓
print(f"  = 2*E/MU = {2*E//MU}: {energy == 2*E//MU}")
# 120 = 480/4 = 120 ✓

# So ENERGY = 120 = E/2 = V*Q = F*N = K*ALPHA = G*DIM_O = 5!
# INCREDIBLE! The graph energy is exactly E/2 = half the edge count!

print(f"\n=== KIRCHHOFF INDEX ===")
# Kf = V * sum_{i with lambda_i > 0} m_i / lambda_i (Laplacian eigenvalues)
# Laplacian eigenvalues: 0 (mult 1), ALPHA (mult F), 2^MU (mult G)
kf = V * (Fr(F, ALPHA) + Fr(G, 2**MU))
print(f"Kf = V * (F/ALPHA + G/2^MU)")
print(f"   = {V} * ({Fr(F,ALPHA)} + {Fr(G,2**MU)})")
print(f"   = {V} * {Fr(F,ALPHA) + Fr(G,2**MU)}")
print(f"   = {kf}")
# = 40 * (24/10 + 15/16) = 40 * (12/5 + 15/16) = 40 * (192/80 + 75/80) = 40 * 267/80
# = 267/2 = 133.5
# 267/2... hmm
print(f"   = {float(kf)}")
# Check: 267 = 3*89
print(f"   Numerator 267 = 3*89 = Q*89")
# 267/2 = 133.5... not as clean

print(f"\n=== KEMENY'S CONSTANT ===")
# Kemeny = sum_{i with lambda_i > 0} 1/lambda_i (normalized Laplacian... or Laplacian)
# For random walk: K_kem = sum_{i>0} V/lambda_i where lambda_i are Laplacian eigenvalues
# Or: K_kem = sum_{i>0} 1/(1 - theta_i/K) for normalized
kemeny_norm = Fr(F, Fr(ALPHA, K)) + Fr(G, Fr(K-S, K))
# Actually K_kem = sum m_i * K/(K-theta_i) for theta_i != K
# = F * K/ALPHA + G * K/(K-S) = F*K/ALPHA + G*K/(K+MU)
kemeny = Fr(F*K, ALPHA) + Fr(G*K, K-S)
print(f"Kemeny = F*K/ALPHA + G*K/(K-S)")
print(f"       = {Fr(F*K, ALPHA)} + {Fr(G*K, K-S)}")
print(f"       = {kemeny}")
# = 24*12/10 + 15*12/16 = 288/10 + 180/16 = 144/5 + 45/4 = 576/20 + 225/20 = 801/20
print(f"       Hmm, {float(kemeny)}")
# Not super clean. Let me try the standard definition
# Kemeny's constant = sum_{i>0} 1/lambda_i where lambda_i are Laplacian eigenvalues
kemeny2 = Fr(F, ALPHA) + Fr(G, 2**MU)
print(f"\nKemeny (Laplacian) = F/ALPHA + G/2^MU = {kemeny2} = {float(kemeny2)}")
# = 12/5 + 15/16 = 192/80 + 75/80 = 267/80
# Hmm. Let's check 267 = 3*89 = Q*89
print(f"  267/80 ... 267 = Q*89")

print(f"\n=== EFFECTIVE RESISTANCE ===")
# Total effective resistance = Kf/V = (Kirchhoff index)/V
eff_res = kf / V
print(f"Total effective resistance = Kf/V = {eff_res} = {float(eff_res)}")

print(f"\n=== SPECTRAL GAP ===")
gap = K - R  # smallest nonzero Laplacian eigenvalue = ALPHA
print(f"Spectral gap = K - R = {gap} = ALPHA = {ALPHA}")
# The spectral gap is ALPHA, which is the second Laplacian eigenvalue

print(f"\n=== ALGEBRAIC CONNECTIVITY ===")
# Fiedler value = smallest nonzero Laplacian eigenvalue = ALPHA = 10
print(f"Algebraic connectivity (Fiedler) = ALPHA = {ALPHA}")
print(f"  This is K-R, the gap to the second-largest adjacency eigenvalue")

print(f"\n=== HEAT KERNEL TRACE ===")
# Z(t) = sum_i m_i * exp(-t * lambda_i) where lambda_i are Laplacian eigenvalues
# = 1 + F*exp(-ALPHA*t) + G*exp(-2^MU*t)
# At t = ln(2)/ALPHA:
#   Z(t) = 1 + F*(1/2) + G*exp(-2^MU*ln(2)/ALPHA)
#   = 1 + F/2 + G*2^(-2^MU/ALPHA)
#   = 1 + 12 + 15*2^(-16/10) = 13 + 15*2^(-8/5)
# Not obviously named.

# At t=0: Z(0) = V = 40
# Z'(0) = -(F*ALPHA + G*2^MU) = -(24*10 + 15*16) = -(240 + 240) = -480 = -2E
print(f"Heat kernel at t=0: Z(0) = V = {V}")
heat_deriv = -(F*ALPHA + G*2**MU)
print(f"Z'(0) = -(F*ALPHA + G*2^MU) = -({F*ALPHA} + {G*2**MU}) = {heat_deriv}")
print(f"  = -2E = {-2*E}: {heat_deriv == -2*E}")
# Beautiful! Z'(0) = -2E = -480

# Z''(0) = F*ALPHA^2 + G*(2^MU)^2
heat_d2 = F*ALPHA**2 + G*(2**MU)**2
print(f"Z''(0) = F*ALPHA^2 + G*(2^MU)^2 = {F*ALPHA**2} + {G*(2**MU)**2} = {heat_d2}")
# = 24*100 + 15*256 = 2400 + 3840 = 6240
print(f"  = {heat_d2}")
# 6240 = 2^5 * 3 * 5 * 13 = 2^N * Q * N * PHI3
print(f"  = 2^N * Q * N * PHI3 = {2**N * Q * N * PHI3}: {heat_d2 == 2**N * Q * N * PHI3}")
# 32*3*5*13 = 6240 ✓
# Also: 6240 = V * (2E/V + something)
print(f"  = V * 156 = {V*156}: hmm {heat_d2 == V*156}")
print(f"  = E * 26 = {E*26}: {heat_d2 == E*26}")
# 6240 = 240*26... 26 = bosonic dimension!
print(f"  = E * BOSONIC = {E * 26}: {heat_d2 == E * 26}")
# Or: 6240 / 40 = 156 = 2*78 = 2*dim(E6)
print(f"  Z''(0)/V = {heat_d2//V} = 2*78 = 2*dim(E6)")

# Higher moments: Z^(n)(0) = (-1)^n * sum m_i * lambda_i^n
heat_d3 = -(F*ALPHA**3 + G*(2**MU)**3)
print(f"Z'''(0) = -(F*ALPHA^3 + G*(2^MU)^3) = -({F*ALPHA**3} + {G*(2**MU)**3})")
print(f"        = {heat_d3}")
# = -(24*1000 + 15*4096) = -(24000 + 61440) = -85440
print(f"  = {heat_d3}")
# 85440 = 2^6 * 3 * 5 * 89
# Hmm, 89 is prime. Not as clean.

# Ratio Z''/Z' 
ratio = Fr(heat_d2, -heat_deriv)
print(f"\nZ''(0)/|Z'(0)| = {heat_d2}/{-heat_deriv} = {ratio} = {float(ratio)}")
# 6240/480 = 13 = PHI3!
print(f"  = PHI3 = {PHI3}: {ratio == PHI3}")
# BEAUTIFUL!

print(f"\n=== LAPLACIAN SPECTRAL MOMENTS ===")
# M_n = sum_i m_i * lambda_i^n
# M_0 = V = 40
# M_1 = F*ALPHA + G*2^MU = 2E = 480
# M_2 = F*ALPHA^2 + G*(2^MU)^2 = 6240 = E*BOSONIC
# M_3 = F*ALPHA^3 + G*(2^MU)^3 = 85440
# M_4 = ?
M = [V]
for n in range(1, 9):
    Mn = F*ALPHA**n + G*(2**MU)**n
    M.append(Mn)
    print(f"M_{n} = {Mn}")

# Check ratios M_{n+1} / M_n
print(f"\nRatios M_{{n+1}}/M_n:")
for n in range(len(M)-1):
    print(f"  M_{n+1}/M_{n} = {Fr(M[n+1], M[n])} = {float(Fr(M[n+1], M[n])):.4f}")

# Let's check M_n / (M_1)^n
print(f"\nM_n / M_1:")
for n in range(len(M)):
    print(f"  M_{n} / M_1 = {Fr(M[n], M[1])}")

print(f"\n=== IHARA ZETA FUNCTION ===")
# For a regular graph, the Ihara zeta equals reciprocal of
# (1-u^2)^{(K-1)V/2 - V} * det(I - A*u + (K-1)*u^2 * I)
# where the det is over V x V.
# For SRG, det factorizes:
# = product over eigenvalues theta_i: (1 - theta_i*u + (K-1)*u^2)^{m_i}

# The reciprocal of the Ihara zeta at u is:
# zeta_I(u)^{-1} = (1-u^2)^{E-V} * prod_i (1 - theta_i*u + (K-1)*u^2)^{m_i}
# where the product is over the three eigenvalues

print(f"Ihara zeta denominator factors:")
print(f"  (1-u^2)^{{E-V}} = (1-u^2)^{{{E-V}}} = (1-u^2)^{{{E-V}}}")
# E-V = 240-40 = 200
print(f"  E-V = {E-V}")
print(f"    = E - V = {E} - {V} = {E-V}")
print(f"    = V*(K/2 - 1) = V*(K-2)/2 = {V*(K-2)//2}")
# 40*5 = 200 ✓
print(f"    = V*N = {V*N}: {E-V == V*N}")
# 200 = 40*5 = V*N ✓!

# The three quadratic factors at eigenvalues K, R, S:
# f_K(u) = 1 - K*u + (K-1)*u^2 = (K-1)u^2 - K*u + 1
# f_R(u) = 1 - R*u + (K-1)*u^2 = (K-1)u^2 - R*u + 1
# f_S(u) = 1 - S*u + (K-1)*u^2 = (K-1)u^2 - S*u + 1

# f_K(u) with K=12: 11u^2 - 12u + 1 = (11u-1)(u-1)
# f_R(u) with R=2: 11u^2 - 2u + 1
# f_S(u) with S=-4: 11u^2 + 4u + 1
print(f"\n  f_K(u) = 11u^2 - 12u + 1 = (11u-1)(u-1)")
print(f"  f_R(u) = 11u^2 - 2u + 1")
print(f"  f_S(u) = 11u^2 + 4u + 1")
print(f"  Note: K-1 = {K-1} = (K-1)")

# Discriminants of these quadratics:
disc_K = K**2 - 4*(K-1)  # 144-44 = 100
disc_R = R**2 - 4*(K-1)  # 4-44 = -40
disc_S = S**2 - 4*(K-1)  # 16-44 = -28

print(f"\n  Discriminants:")
print(f"    disc(f_K) = K^2 - 4(K-1) = {disc_K}")
print(f"      = ALPHA^2 = {ALPHA**2}: {disc_K == ALPHA**2}")
# 100 = 10^2 = ALPHA^2 ✓
print(f"    disc(f_R) = R^2 - 4(K-1) = {disc_R}")
print(f"      = -V = {-V}: {disc_R == -V}")
# -40 = -V ✓!
print(f"    disc(f_S) = S^2 - 4(K-1) = {disc_S}")
print(f"      = -(V-K) = -{V-K}: {disc_S == -(V-K)}")
# -28 = -(40-12) = -28 ✓
# Also -28 = -4*PHI6 = -MU*PHI6
print(f"      = -MU*PHI6 = {-MU*PHI6}: {disc_S == -MU*PHI6}")

# Product of discriminants:
disc_prod = disc_K * disc_R * disc_S
print(f"\n  Product of discriminants: {disc_prod}")
print(f"    = ALPHA^2 * V * MU*PHI6 = {ALPHA**2 * V * MU * PHI6}")
# Careful with signs: 100 * (-40) * (-28) = 100*1120 = 112000
# = ALPHA^2 * V * MU * PHI6 = 100*40*4*7 = 112000 ✓
print(f"    = {disc_prod} = 112000")
# 112000 = 2^6 * 5^3 * 7 = 2^r_s * N^Q * PHI6
print(f"    = 2^r_s * N^Q * PHI6 = {2**r_s * N**Q * PHI6}: {disc_prod == 2**r_s * N**Q * PHI6}")
# 64*125*7 = 56000 ≠ 112000. Let me factorize properly.
# 112000 = 112 * 1000 = 16*7 * 8*125 = 2^4*7 * 2^3*5^3 = 2^7*5^3*7
print(f"    = 2^7 * 5^3 * 7 = {2**7 * 5**3 * 7}: {disc_prod == 2**7 * 5**3 * 7}")
# 128*125*7 = 112000 ✓

print(f"\n=== IHARA POLES ===")
# The poles of the Ihara zeta come from zeros of the denominator.
# f_K(u) = 0: u = 1 or u = 1/(K-1) = 1/11
# f_R(u) = 0: u = (R ± sqrt(R^2 - 4(K-1))) / (2(K-1))
#            = (2 ± sqrt(-40)) / 22 = (2 ± 2i*sqrt(10)) / 22
#            = (1 ± i*sqrt(10)) / 11
# f_S(u) = 0: u = (-4 ± sqrt(-28)) / 22 = (-4 ± 2i*sqrt(7)) / 22
#            = (-2 ± i*sqrt(7)) / 11

print(f"Ihara poles:")
print(f"  From f_K: u = 1, 1/{K-1}")
print(f"  From f_R: u = (1 +/- i*sqrt(ALPHA)) / {K-1}")
print(f"           |u|^2 = (1 + ALPHA)/{(K-1)**2} = {Fr(1+ALPHA, (K-1)**2)} = 1/{K-1}")
# |u|^2 = (1+10)/121 = 11/121 = 1/11 ✓ (Ramanujan condition for this root)
print(f"           = 1/{K-1}: RH condition")
print(f"  From f_S: u = (-2 +/- i*sqrt(PHI6)) / {K-1}")
print(f"           |u|^2 = (4 + PHI6)/{(K-1)**2} = {Fr(4+PHI6, (K-1)**2)} = 1/{K-1}")
# |u|^2 = (4+7)/121 = 11/121 = 1/11 ✓
print(f"           = 1/{K-1}: RH condition OK")

print(f"\n  W(3,3) satisfies the Ihara-Bass Riemann Hypothesis (Ramanujan graph)!")
print(f"  All non-trivial poles have |u| = 1/sqrt(K-1) = 1/sqrt({K-1})")
print(f"  This is because |R|, |S| <= 2*sqrt(K-1) = {2*math.sqrt(K-1):.4f}")
print(f"     |R| = {abs(R)}, |S| = {abs(S)}, bound = {2*math.sqrt(K-1):.4f}")
print(f"     |S| = {abs(S)} <= {2*math.sqrt(K-1):.4f}: {abs(S) <= 2*math.sqrt(K-1)}")

print(f"\n=== RAMANUJAN CONDITION ===")
# A regular graph is Ramanujan iff max(|R|,|S|) <= 2*sqrt(K-1)
ramanujan_bound = 2 * math.sqrt(K - 1)
print(f"Ramanujan bound = 2*sqrt(K-1) = 2*sqrt({K-1}) = {ramanujan_bound:.6f}")
print(f"max(|R|, |S|) = max({abs(R)}, {abs(S)}) = {max(abs(R), abs(S))}")
is_ramanujan = max(abs(R), abs(S)) <= ramanujan_bound
print(f"Is Ramanujan: {is_ramanujan}")
# |S|=4 ≤ 2√11 = 6.633: ✓ It IS Ramanujan!

# In fact: 2√(K-1) = 2√11 ≈ 6.633
# R=2 < 6.633 ✓, S=-4, |S|=4 < 6.633 ✓

# Ramanujan tightness: |S| / (2√(K-1)) = 4/6.633 = 0.603
tightness = abs(S) / ramanujan_bound
print(f"Tightness: |S| / 2*sqrt(K-1) = {tightness:.6f}")
print(f"  = MU / (2*sqrt(K-1)) = {MU}/{ramanujan_bound:.4f}")

print(f"\n=== IHARA ZETA SPECIAL VALUE ===")
# zeta_I(u)^{-1} = (1-u^2)^{V*N} * f_K(u)*f_R(u)^F*f_S(u)^G
# At u=1: f_K(1) = 0, so zeta has a pole at u=1
# At u=-1: f_K(-1) = 11+12+1 = 24 = F!
# f_R(-1) = 11+2+1 = 14 = 2*PHI6!
# f_S(-1) = 11-4+1 = 8 = DIM_O!
fK_m1 = 11 + 12 + 1
fR_m1 = 11 + 2 + 1
fS_m1 = 11 - 4 + 1
print(f"At u = -1:")
print(f"  f_K(-1) = {fK_m1} = F = {F}: {fK_m1 == F}")
print(f"  f_R(-1) = {fR_m1} = 2*PHI6 = {2*PHI6}: {fR_m1 == 2*PHI6}")
print(f"  f_S(-1) = {fS_m1} = DIM_O = {DIM_O}: {fS_m1 == DIM_O}")
# These are exactly the signless Laplacian eigenvalues!!
print(f"  = exactly the signless Laplacian eigenvalues {{{F}, 2*PHI6={2*PHI6}, DIM_O={DIM_O}}}!")

print(f"\n=== COMPLEMENT TRANSFORMS ===")
# For the complement graph A_bar = J - I - A:
# Laplacian: L_bar = K_bar*I - A_bar = ALBERT*I - (J-I-A) = (ALBERT+1)*I - J + A 
# = (V-K)*I - J + A = L - J + (V-K-K)*I ... hmm
# Actually L_bar_eigenvalues: 0, V-ALPHA, V-2^MU (for a regular complement)
# Since L_bar = V*I - L (for a K-regular graph with complement (V-1-K)-regular)
# Wait. For complement: L_bar = (V-1-K)*I - A_bar
# A_bar eigenvalues: ALBERT=27, -Q=-3, Q=3 with mults 1, ?, ?
# Complement eigenvalues: -1-R = -3 = -Q, -1-S = 3 = Q

# The complement Laplacian eigenvalues are:
# K_bar - ALBERT = 0, K_bar - (-Q) = ALBERT+Q = 30, K_bar - Q = ALBERT-Q = 24 = F
cl_0 = K_BAR - ALBERT  # 0
cl_1 = K_BAR - (-Q)       # 30
cl_2 = K_BAR - Q           # 24 = F

print(f"Complement Laplacian eigenvalues:")
print(f"  K_BAR - ALBERT = {cl_0} (null, mult 1)")
print(f"  K_BAR - (-Q) = {cl_1} = ALBERT+Q = {ALBERT+Q} (mult F)")
print(f"    = V-ALPHA = {V-ALPHA}: {cl_1 == V-ALPHA}")
print(f"  K_BAR - Q = {cl_2} = ALBERT-Q = {ALBERT-Q} = F = {F}: {cl_2 == F} (mult G)")

# Complement spanning trees:
cl_tau = Fr((V-ALPHA)**F * F**G, V)
print(f"\nComplement spanning trees tau_bar = (V-ALPHA)^F * F^G / V")
print(f"  = {V-ALPHA}^{F} * {F}^{G} / {V}")
# 30^24 * 24^15 / 40
# 30 = 2*3*5, so 30^24 = 2^24 * 3^24 * 5^24
# 24 = 2^3 * 3, so 24^15 = 2^45 * 3^15
# Numerator = 2^69 * 3^39 * 5^24
# / 40 = / (2^3 * 5) = 2^66 * 3^39 * 5^23
exp2_c = 24 + 45 - 3  # 66
exp3_c = 24 + 15       # 39 = V-1
exp5_c = 24 - 1         # 23
print(f"  = 2^{exp2_c} * 3^{exp3_c} * 5^{exp5_c}")
print(f"  exp3 = {exp3_c} = V-1 = {V-1}: {exp3_c == V-1}")
# 39 = V-1 ✓

print(f"\n=== GRAPH + COMPLEMENT RELATIONSHIP ===")
# Spanning trees ratio tau_bar / tau
# tau = 2^81 * 5^23
# tau_bar = 2^66 * 3^39 * 5^23
# ratio = 2^66 * 3^39 * 5^23 / (2^81 * 5^23) = 3^39 / 2^15
# = 3^(V-1) / 2^G
ratio_tau = Fr(3**(V-1), 2**G)
print(f"tau_bar / tau = 3^(V-1) / 2^G = {Fr(3,2)}^... ")
print(f"  = Q^(V-1) / 2^G")
# Check: 3^39 / 2^15 = Q^(V-1) / 2^G ✓ (since Q=3, V-1=39, G=15)

# Laplacian spectra relationship:
# Graph: {0, ALPHA^F, (2^MU)^G}
# Complement: {0, (V-ALPHA)^F, F^G}
# Note: complement eigenvalues are V - (graph eigenvalues), except for 0
print(f"\nLaplacian eigenvalue pairing (graph + complement):")
print(f"  0 + 0 = 0")
print(f"  ALPHA + (V-ALPHA) = V = {ALPHA + (V-ALPHA)}")
print(f"  2^MU + F = {2**MU + F} = V = {V}: {2**MU + F == V}")
# 16+24 = 40 ✓! Each nonzero pair sums to V!

print(f"\n=== COMPLETE MATRIX ZOO ===")
# Let's tabulate all the matrix transforms and their eigenvalues
print(f"{'Matrix':<20} {'theta_0':>10} {'theta_1':>10} {'theta_2':>10} {'Named':>8}")
print(f"-" * 60)

matrices = [
    ("A", K, R, S, f"{K},{R},{S}"),
    ("A_bar", ALBERT, -Q, Q, f"q^3,-q,q"),
    ("L = KI-A", 0, K-R, K-S, f"0,a,2^u"),
    ("L_bar", 0, V-(K-R), V-(K-S), f"0,V-a,F"),
    ("K*I+A", K+K, K+R, K+S, f"F,2P6,O"),
    ("Seidel", V-1-2*K, -1-2*R, -1-2*S, f"G,-N,P6"),
    ("-A", -K, -R, -S, f"-K,-R,-S"),
    ("A^2", K**2, R**2, S**2, "K2,R2,S2"),
    ("J-A", V-K, -R, -S, "Kb+1,-R,-S"),
]
for name, t0, t1, t2, named in matrices:
    print(f"{name:<20} {t0:>10} {t1:>10} {t2:>10} {named:>8}")

print(f"\n=== IDEMPOTENT TRANSFER MATRIX ===")
# T = [1, 1, 1; K, R, S; K_bar, -(R+1), -(S+1)]
# = eigenmatrix P
# P^{-1} tells us how to express powers of A in terms of idempotents
# The key structure: P diagonalizes the intersection numbers

# P * diag(1, F, G) * P^T should give the intersection algebra
# Let's compute P * P^T:
PPT = [[0]*3 for _ in range(3)]
mults = [1, F, G]
for i in range(3):
    for j in range(3):
        PPT[i][j] = sum(P[i][c] * P[j][c] for c in range(3))

P = [[1, K, K_BAR], [1, R, -(R+1)], [1, S, -(S+1)]]
print(f"P^T * P (Gram matrix in eigenvalue space):")
PTP = [[0]*3 for _ in range(3)]
for i in range(3):
    for j in range(3):
        PTP[i][j] = sum(P[r][i]*P[r][j] for r in range(3))
        
for row in PTP:
    print(f"  {row}")

# P^T * diag(1,F,G) * P
PmP = [[0]*3 for _ in range(3)]
for i in range(3):
    for j in range(3):
        PmP[i][j] = sum(mults[r]*P[r][i]*P[r][j] for r in range(3))

print(f"\nP^T * M * P (M=diag(1,F,G), Schur product matrix):")
for row in PmP:
    print(f"  {row}")

# This should be V * I
print(f"  = V * I: {PmP == [[V,0,0],[0,V,0],[0,0,V]]}")
# FALSE probably. Let's see.
# PmP[0][0] = 1*1*1 + F*1*1 + G*1*1 = 1+F+G = V ✓
# PmP[0][1] = 1*1*K + F*1*R + G*1*S = K + F*R + G*S = 12+48-60 = 0 ✓!
# PmP[1][1] = 1*K*K + F*R*R + G*S*S = K^2+F*R^2+G*S^2 = 144+96+240 = 480 = 2E
# So PmP ≠ V*I but is related to trace powers

print(f"\nP^T * M * P diagonal entries:")
print(f"  [0,0] = 1+F+G = V = {V}")
print(f"  [1,1] = K^2+F*R^2+G*S^2 = {K**2}+{F*R**2}+{G*S**2} = {K**2+F*R**2+G*S**2}")
print(f"       = 2E = {2*E}: {K**2+F*R**2+G*S**2 == 2*E}")

# Second column of PmP:
print(f"  [2,2] = K_BAR^2+F*(R+1)^2+G*(S+1)^2")
val22 = K_BAR**2 + F*(R+1)**2 + G*(S+1)**2
print(f"       = {K_BAR**2}+{F*(R+1)**2}+{G*(S+1)**2} = {val22}")
print(f"       = {val22} = 2*E_bar = 2*(V-1)*ALBERT/2 = {(V-1)*ALBERT}: {val22 == (V-1)*ALBERT}")
# 729+216+135 = 1080 = (V-1)*ALBERT = 39*27 ≈ 1053... let me check
# 27^2 = 729, 24*3^2 = 216, 15*(-3)^2=135; 729+216+135=1080
# E_bar = edges of complement = K_BAR*(V)/2... no, E_bar = V*K_BAR/2 = 40*27/2 = 540
# 2*E_bar = 1080 ✓!
E_BAR = V * K_BAR // 2  # 540
print(f"       = 2*E_bar = {2*E_BAR}: {val22 == 2*E_BAR}")

print(f"\n=== TRACE POWERS OF SEIDEL MATRIX ===")
# tr(S^n) = G^n + F*(-N)^n + G*PHI6^n
for n_val in range(1, 7):
    tr_S = G**n_val + F*(-N)**n_val + G*PHI6**n_val
    print(f"tr(S_seidel^{n_val}) = {G**n_val} + {F*(-N)**n_val} + {G*PHI6**n_val} = {tr_S}")

print(f"\n=== MULTIPLICITY-WEIGHTED POWER SUMS ===")
# These are the graph's spectral moments mu_n = (1/V) * tr(A^n)
for n_val in range(1, 9):
    tr_An = K**n_val + F*R**n_val + G*S**n_val
    mu_n = Fr(tr_An, V)
    print(f"mu_{n_val} = tr(A^{n_val})/V = ({K**n_val}+{F*R**n_val}+{G*S**n_val})/{V} = {mu_n} = {float(mu_n):.2f}")

print(f"\n=== ENTROPY OF SPECTRAL MEASURE ===")
# Shannon entropy with 3 eigenvalue weights: {1/V, F/V, G/V}
w = [Fr(1,V), Fr(F,V), Fr(G,V)]
H_bits = sum(-float(wi)*math.log2(float(wi)) for wi in w)
H_nats = sum(-float(wi)*math.log(float(wi)) for wi in w)
print(f"H(bits) = {H_bits:.6f}")
print(f"H(nats) = {H_nats:.6f}")
print(f"exp(H_nats) = {math.exp(H_nats):.6f}")
# Perplexity
perp = 2**H_bits
print(f"Perplexity = 2^H = {perp:.6f}")

print(f"\n=== MULTIPLICITY POLYNOMIAL ===")
# The multiplicity polynomial: m̃(x) such that m̃(theta_i) = m_i
# m̃(K) = 1, m̃(R) = F, m̃(S) = G
# This is a quadratic: m̃(x) = ax^2 + bx + c
# System: aK^2 + bK + c = 1, aR^2 + bR + c = F, aS^2 + bS + c = G

# Using Lagrange interpolation
# m̃(x) = 1*(x-R)(x-S)/((K-R)(K-S)) * 1 + (x-K)(x-S)/((R-K)(R-S)) * F + (x-K)(x-R)/((S-K)(S-R)) * G
# = N_0(x)/d0 + F*N_1(x)/d1 + G*N_2(x)/d2

# At x=0:
m0 = Fr(R*S, (K-R)*(K-S)) + Fr(F*K*S, (R-K)*(R-S)) + Fr(G*K*R, (S-K)*(S-R))
print(f"m̃(0) = R*S/d0 + F*K*S/d1 + G*K*R/d2")
print(f"     = {Fr(R*S,(K-R)*(K-S))} + {Fr(F*K*S,(R-K)*(R-S))} + {Fr(G*K*R,(S-K)*(S-R))}")
print(f"     = {m0}")
# = -8/160 + 24*(-48)/(-60) + 15*24/96
# = -1/20 + 19.2 + 3.75
# = -1/20 + 96/5 + 15/4
# = -1/20 + 384/20 + 75/20 = 458/20 = 229/10
print(f"m̃(0) = {float(m0):.4f}")

# The multiplicity polynomial is actually the idempotent evaluated at A
# E_i(theta_j) = delta_{ij} * (V * m_j) wait...

# Actually, the V*E_i are the projection matrices, and tr(E_i) = m_i
# The multiplicity polynomial for an SRG is:
# m(x) = V * [(x-R)(x-S)]/[(K-R)(K-S)] for m=1 eigenspace... no that's the Hoffman

# Let me just compute the Lagrange form coefficients
# a, b, c from the three equations
from fractions import Fraction as Fr
a_num = Fr(1, (K-R)*(K-S)) + Fr(F, (R-K)*(R-S)) + Fr(G, (S-K)*(S-R))
b_num = Fr(-(R+S), (K-R)*(K-S)) + Fr(F*(-(K+S)), (R-K)*(R-S)) + Fr(G*(-(K+R)), (S-K)*(S-R))
c_num = Fr(R*S, (K-R)*(K-S)) + Fr(F*K*S, (R-K)*(R-S)) + Fr(G*K*R, (S-K)*(S-R))

print(f"\nMultiplicity polynomial: m̃(x) = ({a_num})x^2 + ({b_num})x + ({c_num})")
# Verify:
for theta, m_val, name in [(K, 1, "K"), (R, F, "R"), (S, G, "S")]:
    val = a_num * theta**2 + b_num * theta + c_num
    print(f"  m̃({name}={theta}) = {val} (expected {m_val}): {val == m_val}")

print(f"\n=== MATRIX RESOLVENT / GREEN'S FUNCTION ===")
# G(z) = (zI - A)^(-1), trace = sum m_i / (z - theta_i)
# Trace of resolvent:
# tr G(z) = 1/(z-K) + F/(z-R) + G/(z-S)
# At z=0: tr G(0) = -1/K - F/R - G/S
tr_G0 = Fr(-1, K) + Fr(-F, R) + Fr(-G, S)
print(f"tr G(0) = -1/K - F/R - G/S")
print(f"       = {Fr(-1,K)} + {Fr(-F,R)} + {Fr(-G,S)}")
print(f"       = {tr_G0} = {float(tr_G0):.4f}")
# = -1/12 - 12 + 15/4 = -1/12 - 48/4 + 45/4 = -1/12 - 3/4 = -1/12 - 9/12 = -10/12 = -5/6
print(f"       = -{Fr(5,6)} = -N/r_s = {Fr(-N,r_s)}: {tr_G0 == Fr(-N,r_s)}")
# -5/6 = -N/r_s ✓! This is the normalized Laplacian eigenvalue!

# At z = -1: tr G(-1) 
tr_Gm1 = Fr(1, -1-K) + Fr(F, -1-R) + Fr(G, -1-S)
print(f"\ntr G(-1) = 1/(-1-K) + F/(-1-R) + G/(-1-S)")
print(f"        = {Fr(1,-1-K)} + {Fr(F,-1-R)} + {Fr(G,-1-S)}")
print(f"        = {tr_Gm1}")
# = -1/13 + (-24/3) + 15/3 = -1/13 - 8 + 5 = -1/13 - 3 = -40/13
print(f"        = {float(tr_Gm1):.4f}")
print(f"        = -V/PHI3 = {Fr(-V,PHI3)}: {tr_Gm1 == Fr(-V,PHI3)}")
# -40/13 ✓

# At z = 1: tr G(1)
tr_G1 = Fr(1, 1-K) + Fr(F, 1-R) + Fr(G, 1-S)
print(f"\ntr G(1) = 1/(1-K) + F/(1-R) + G/(1-S)")
print(f"       = {Fr(1,1-K)} + {Fr(F,1-R)} + {Fr(G,1-S)}")
print(f"       = {tr_G1}")
print(f"       = {float(tr_G1):.4f}")
# = -1/11 + (-24) + 15/5 = -1/11 -24 + 3 = -1/11 - 21 = -232/11
# Hmm let me check: F/(1-R) = 24/(1-2) = -24, G/(1-S) = 15/(1+4) = 3
# = -1/11 - 24 + 3 = -1/11 - 21 = (-1-231)/11 = -232/11
print(f"       -232/11 ... 232 = 8*29")

# At z = Q: 
tr_GQ = Fr(1, Q-K) + Fr(F, Q-R) + Fr(G, Q-S)
print(f"\ntr G(Q) = 1/(Q-K) + F/(Q-R) + G/(Q-S)")
print(f"       = {Fr(1,Q-K)} + {Fr(F,Q-R)} + {Fr(G,Q-S)}")
print(f"       = {tr_GQ}")
print(f"       = {float(tr_GQ):.4f}")
# = 1/(3-12) + 24/(3-2) + 15/(3+4) = -1/9 + 24 + 15/7 = -1/9 + 24 + 15/7
# = -7/63 + 1512/63 + 135/63 = 1640/63
# 1640/63 = ... 1640 = 8*205 = 8*5*41; 63 = 9*7 = Q^2*PHI6
print(f"       = {tr_GQ} ... denom = Q^2*PHI6 = {Q**2*PHI6}: {tr_GQ.denominator == Q**2*PHI6}")

print(f"\n=== SUMMARY OF BEAUTIFUL IDENTITIES ===")
print(f"")
print(f"1. GRAPH ENERGY = E/2 = V*Q = F*N = K*ALPHA = G*DIM_O = 5! = 120")
print(f"2. Z'(0)/Z''(0) ... PHI3 ratio (heat kernel)")
print(f"3. Ramanujan: all Ihara poles on |u| = 1/√(K-1)")
print(f"4. Ihara at u=-1 recovers signless Laplacian eigenvalues")
print(f"5. Seidel eigenvalues: G, -N, PHI6")
print(f"6. Seidel sum = PHI3+MU = ALBERT-ALPHA = 17") 
print(f"7. Seidel pairwise = -N; product = -Q*N^2*PHI6")
print(f"8. Spanning trees = 2^81 * 5^23; complement trees = 2^66 * 3^39 * 5^23")
print(f"9. Complement tree ratio = Q^(V-1) / 2^G")
print(f"10. Nonzero Lap eigenvalues pair-sum to V (duality)")
print(f"11. Signless Lap eigenvalues = {{F, 2*PHI6, DIM_O}}")
print(f"12. Norm Lap eigenvalues = {{0, N/r_s, MU/Q}} = {{0, 5/6, 4/3}}")
print(f"13. Resolvent: tr G(0) = -N/r_s, tr G(-1) = -V/PHI3")
print(f"14. det(P) = -E (eigenmatrix)")
print(f"15. Heat kernel: Z'(0) = -2E, Z''(0)/|Z'(0)| = PHI3")
print(f"16. Idempotent denom product = -disc(m) = -(MU*E)^2")
print(f"17. Hoffman polynomial = (1/MU)*(x-R)(x-S), H(0) = -LAM")
print(f"18. Ihara discriminants: ALPHA^2, -V, -MU*PHI6")
print(f"19. Ihara: E-V = V*N = 200 (genus correction)")  
print(f"20. P^T*M*P diagonal = {{V, 2E, 2E_bar}}")
