"""Phase L exploration round 2: deeper polynomial anatomy"""
from sympy import *

# Source constants
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
# Characteristic polynomial of SRG
p = (x - K)**1 * (x - R)**F * (x - S)**G

print("=== DISCRIMINANT & RESULTANT ===")
# Discriminant of the minimal polynomial m(x) = (x-K)(x-R)(x-S)
m = (x - K) * (x - R) * (x - S)
disc_m = discriminant(m, x)
print(f"Minimal poly: {expand(m)}")
print(f"Discriminant of m(x) = {disc_m}")
print(f"  = {factorint(abs(disc_m))}")
# disc = product of (ei-ej)^2 for i<j
d12 = (K - R)**2  # = THETA^2 = 100
d13 = (K - S)**2  # = (K+MU)^2 = 256 = 2^8
d23 = (R - S)**2  # = (r-s)^2 = 36
print(f"  (K-R)^2 = THETA^2 = {d12}")
print(f"  (K-S)^2 = (K+MU)^2 = {d13}")
print(f"  (R-S)^2 = (r-s)^2 = {d23}")
print(f"  Product = {d12*d13*d23}")
print(f"  THETA^2 * (K+MU)^2 * (r-s)^2 = {d12*d13*d23}")
print(f"  = (THETA * (K+MU) * (r-s))^2 = ({10*16*6})^2 = {(10*16*6)**2}")
print(f"  THETA*(K+MU)*(r-s) = {10*16*6} = {factorint(10*16*6)}")
print(f"  = ALPHA * 2^OMEGA * r_s = {ALPHA} * {2**OMEGA} * {r_s} = {ALPHA * 2**OMEGA * r_s}")

print(f"\n=== TRACE DECOMPOSITIONS ===")
# We know tr(A^n) = K^n + F*R^n + G*S^n
for n in range(1, 9):
    tr_n = K**n + F * R**n + G * S**n
    parts = [K**n, F * R**n, G * S**n]
    print(f"tr(A^{n}) = {K}^{n} + {F}*{R}^{n} + {G}*({S})^{n} = {parts[0]} + {parts[1]} + {parts[2]} = {tr_n}")

print(f"\n=== TRACE RATIOS ===")
for n in range(2, 9):
    tr_n = K**n + F * R**n + G * S**n
    print(f"tr(A^{n})/V = {tr_n//V} (exact: {Rational(tr_n, V)})")
    if tr_n % V == 0:
        val = tr_n // V
        print(f"  = {factorint(val)}")
    # Also / (2E)
    if tr_n % (2*E) == 0:
        print(f"  tr(A^{n})/(2E) = {tr_n // (2*E)}")

print(f"\n=== POWER SUM NEWTON IDENTITIES ===")
# Symmetric functions of K, R, S
e1 = K + R + S  # sum of eigenvalues... but weighted
# For the MINIMAL poly eigenvalues:
s1 = K + R + S
s2 = K*R + K*S + R*S
s3 = K*R*S
print(f"e1 = K+R+S = {s1}")
print(f"e2 = KR+KS+RS = {s2}")
print(f"e3 = KRS = {s3}")
print(f"  e1 = {s1} = K+LAM-MU = {K+LAM-MU}")
print(f"  e2 = {s2} = LAM*S + K*S + K*R = {LAM*S + K*S + K*R}")
print(f"       = (LAM-MU)*K + R*S = {(LAM-MU)*K + R*S}")
print(f"       = -E/V*(V-1) ... no")
print(f"  e2 = KR+KS+RS = K(R+S)+RS = K(LAM-MU)+LAM*MU = {K*(LAM-MU) + LAM*MU}")
print(f"       = -K*R + R*S ... no")
print(f"  e2 = {s2} = -(V*K - 2*E)... {-(V*K - 2*E)}")
print(f"  Actually from SRG: sum of eigenvalues (with multiplicity):")
s1_full = K + F*R + G*S  # = 0 (trace = 0)
s2_full = K**2 + F*R**2 + G*S**2  # = 2E = 480
print(f"  p1 = K + F*R + G*S = {s1_full}")
print(f"  p2 = K^2 + F*R^2 + G*S^2 = {s2_full} = 2E = {2*E}")
# Newton identity: p2 = sigma1*p1 - 2*sigma2
# where sigma_k are symmetric funcs of ALL eigenvalues (with multiplicity)
# sigma1 = 0 (trace), sigma2 = -E (from p2 = 2*sigma2... wait)
# Actually: p1 = sigma1; p2 = sigma1*p1 - 2*sigma2; so sigma2 = (sigma1*p1 - p2)/2 = -E
print(f"  sigma1 = 0, sigma2 = -E = {-E}")

print(f"\n=== DETERMINANT ANATOMY ===")
det_A = K * R**F * S**G  # careful: might need abs
det_val = K * R**F * S**G
print(f"det(A) = K * R^F * S^G = {K} * {R}^{F} * ({S})^{G}")
print(f"       = {K} * {R**F} * {S**G}")
print(f"       = {det_val}")
print(f"  |det(A)| = {abs(det_val)}")
print(f"  = {factorint(abs(det_val))}")
# We said p(0) = (-K)(-R)^F(-S)^G = (-1)^V * K*R^F*S^G
# But V=40, so (-1)^V = 1
# p(0) = (-K)*(-R)^F*(-S)^G = (-1)^(1+F+G) * K * R^F * S^G
# 1+F+G = 1+24+15 = 40 = V, (-1)^V = 1
# So p(0) = K * R^F * S^G = det... wait the char poly is det(xI - A)
# p(0) = det(-A) = (-1)^V det(A) = det(A) since V even
print(f"  p(0) = det(-A) = (-1)^V det(A) = det(A) (V even)")
print(f"  p(0) = {(-K) * (-R)**F * (-S)**G}")
print(f"  = (-1)^V * K * R^F * S^G = {det_val}")

# Factor det(A) in terms of named constants
# det_val = 12 * 2^24 * (-4)^15 = 12 * 2^24 * (-1)^15 * 4^15
# = -12 * 2^24 * 2^30 = -12 * 2^54
# = -3 * 4 * 2^54 = -3 * 2^56
# = -Q * 2^(DIM_O*PHI6)
print(f"  -Q * 2^(DIM_O*PHI6) = {-Q * 2**(DIM_O*PHI6)}")
print(f"  DIM_O * PHI6 = {DIM_O*PHI6} = {DIM_O}*{PHI6}")
print(f"  det(A) = -Q * 2^56: {det_val == -Q * 2**56}")

print(f"\n=== PERMANENT vs DETERMINANT ===")
# |det| = Q * 2^56
# Compare with V! etc
print(f"  log2|det| = log2(Q) + 56 = {log(Q,2).evalf() + 56:.6f}")
print(f"  56 = DIM_O * PHI6 = 8*7 = |W(E7)|/|W(E6)| (ovoid count!)")

print(f"\n=== POLYNOMIAL AT PHYSICS POINTS ===")
# p(26) where 26 = bosonic string dimension
for val, name in [(26, '26=bos_dim'), (10, 'ALPHA=10'), (11, '11=K-1'),
                   (16, '16=K+MU'), (78, '78=dim(E6)'), (248, '248=dim(E8)')]:
    pval = (val - K) * (val - R)**F * (val - S)**G
    print(f"p({name}) = {pval}")
    if pval != 0:
        print(f"  = {factorint(abs(pval))} {'(neg)' if pval < 0 else '(pos)'}")

print(f"\n=== VIETA FORMULAS FOR MINIMAL POLY ===")
# m(x) = x^3 - e1*x^2 + e2*x - e3 = (x-K)(x-R)(x-S)
mexp = expand(m)
print(f"m(x) = {mexp}")
coeffs = Poly(m, x).all_coeffs()
print(f"Coefficients: {coeffs}")
# x^3 - (K+R+S)x^2 + (KR+KS+RS)x - KRS
print(f"  -(K+R+S) = {-(K+R+S)} = {coeffs[1]}")
print(f"  KR+KS+RS = {K*R+K*S+R*S} = {coeffs[2]}")
print(f"  -KRS = {-K*R*S} = {coeffs[3]}")

print(f"\n  K+R+S = {K+R+S} = ALPHA = {ALPHA}: {K+R+S == ALPHA}")
print(f"  KR+KS+RS = {K*R+K*S+R*S}")
print(f"    = K(R+S)+RS = {K}*{R+S}+{R*S} = {K*(R+S)+R*S}")
print(f"    R+S = LAM-MU = {LAM-MU} = {R+S}")
print(f"    RS = LAM*(-MU) = {R*S} = -{LAM*MU}")
print(f"    KR+KS+RS = K(LAM-MU) - LAM*MU = {K*(LAM-MU) - LAM*MU}")
print(f"    = -K*LAM - LAM*MU = ... no: = K*LAM - K*MU - LAM*MU")
val_e2 = K*R + K*S + R*S
print(f"    = {val_e2}")
print(f"    = -(V-1+MU) ... {-(V-1+MU)}: {val_e2 == -(V-1+MU)}")
print(f"    Nope. Let me just factor: {factorint(abs(val_e2))}, sign={'neg' if val_e2<0 else 'pos'}")

print(f"\n  KRS = {K*R*S}")
print(f"    = K*LAM*(-MU) = -{K*LAM*MU} = {K*R*S}")
print(f"    = -K*DIM_O ... no: -K*LAM*MU = -{K*LAM*MU}")
print(f"    = -2*K*MU = -96: {K*R*S == -2*K*MU}")

print(f"\n=== SUM / PRODUCT IDENTITIES ===")
print(f"K+R+S = {K+R+S} = ALPHA = {ALPHA}")
print(f"K*R*S = {K*R*S} = -2*K*MU = {-2*K*MU}: {K*R*S == -2*K*MU}")
print(f"       = -DIM_O * K = {-DIM_O*K}: {K*R*S == -DIM_O*K}")
print(f"       Nope: -96 vs {-DIM_O*K}")
print(f"K*R*S = {K*R*S} = -K*DIM_O: {K*R*S == -K*DIM_O}")
print(f"K*R*S = {K*R*S}")
print(f"  factored: {factorint(abs(K*R*S))}")
print(f"  = -2^5 * 3 = -Q * 2^N = {-Q * 2**N}: {K*R*S == -Q * 2**N}")

e2_val = K*R + K*S + R*S
print(f"\nKR+KS+RS = {e2_val}")
print(f"  = -E/V * (thing)?")
print(f"  -32 factored: {factorint(abs(e2_val))}")
print(f"  = -2^N = {-2**N}: {e2_val == -2**N}")

print(f"\n=== BEAUTIFUL VIETA SUMMARY ===")
print(f"K+R+S = ALPHA = {ALPHA}")
print(f"KR+KS+RS = -2^N = {-2**N}: {e2_val == -2**N}")
print(f"KRS = -Q*2^N = {-Q*2**N}: {K*R*S == -Q*2**N}")

print(f"\nSo minimal poly = x^3 - ALPHA*x^2 - 2^N*x + Q*2^N")
print(f"                = x^3 - {ALPHA}x^2 - {2**N}x + {Q*2**N}")
print(f"Check: {expand((x-K)*(x-R)*(x-S))}")

print(f"\n=== RATIO IDENTITIES ===")
print(f"KRS / (KR+KS+RS) = {Rational(K*R*S, e2_val)} = Q = {Q}: {Rational(K*R*S, e2_val) == Q}")
print(f"(K+R+S) / (KR+KS+RS) = {Rational(K+R+S, e2_val)} = -ALPHA/2^N = {Rational(-ALPHA, 2**N)}")
print(f"(K+R+S) * KRS = {(K+R+S)*K*R*S} = -ALPHA*Q*2^N = {-ALPHA*Q*2**N}")
print(f"  = -Q*ALPHA*2^N = {-Q*ALPHA*2**N}")
print(f"  = {factorint(abs((K+R+S)*K*R*S))}")

print(f"\n=== CAYLEY-HAMILTON: A^3 = ALPHA*A^2 + 2^N*A - Q*2^N*I ===")
print(f"This means: A^3 = {ALPHA}*A^2 + {2**N}*A - {Q*2**N}*I")
print(f"Trace check: tr(A^3) = {ALPHA}*tr(A^2) + {2**N}*tr(A) - {Q*2**N}*V")
tr3_check = ALPHA * 2*E + 2**N * 0 - Q*2**N*V
print(f"  = {ALPHA}*{2*E} + 0 - {Q*2**N*V} = {ALPHA*2*E} - {Q*2**N*V} = {tr3_check}")
tr3_actual = K**3 + F*R**3 + G*S**3
print(f"  Actual tr(A^3) = {tr3_actual}")
print(f"  Match: {tr3_check == tr3_actual}")

print(f"\n=== COMPANION MATRIX INTERPRETATION ===")
print(f"Companion matrix of m(x) = x^3 - {ALPHA}x^2 - {2**N}x + {Q*2**N}")
print(f"  [[0, 0, -{Q*2**N}],")
print(f"   [1, 0,  {2**N}],")
print(f"   [0, 1,  {ALPHA}]]")

print(f"\n=== DERIVATIVE & CRITICAL POINTS ===")
mp = diff(m, x)
print(f"m'(x) = {mp}")
crits = solve(mp, x)
print(f"Critical points: {[float(c) for c in crits]}")
print(f"  = ({2*ALPHA} ± sqrt({(2*ALPHA)**2 - 12*(-2**N)}))/6")
disc_mp = (2*ALPHA)**2 + 12*2**N
print(f"  Discriminant of m' = 4*ALPHA^2 + 12*2^N = {disc_mp}")
print(f"  = {factorint(disc_mp)}")
print(f"  sqrt({disc_mp}) = {sqrt(disc_mp).evalf():.6f}")
# 4*100 + 12*32 = 400 + 384 = 784 = 28^2
print(f"  = 28^2 = {28**2}: {disc_mp == 784}")
print(f"  28 = 4*PHI6 = {4*PHI6}: {28 == 4*PHI6}")
print(f"  28 = OMEGA*PHI6 = {OMEGA*PHI6}: {28 == OMEGA*PHI6}")
print(f"  So critical pts = (2*ALPHA ± OMEGA*PHI6)/6")
c1 = Rational(2*ALPHA + OMEGA*PHI6, 6)
c2 = Rational(2*ALPHA - OMEGA*PHI6, 6)
print(f"  c1 = (20+28)/6 = {c1} = DIM_O = {DIM_O}: {c1 == DIM_O}")
print(f"  c2 = (20-28)/6 = {c2} = -{Rational(4,3)} = -MU/Q = {Rational(-MU,Q)}: {c2 == Rational(-MU,Q)}")

print(f"\n  Critical point c1 = DIM_O (local min between R and K)")
print(f"  Critical point c2 = -MU/Q (local max between S and R)")
print(f"  m(DIM_O) = {int(m.subs(x, DIM_O))} ") 
print(f"  m(-MU/Q) = {m.subs(x, Rational(-MU,Q))}")
mc2 = m.subs(x, Rational(-MU,Q))
print(f"  m(-MU/Q) = {mc2}")
print(f"  = {Rational(mc2)}")

print(f"\n=== RESULTANT ===")
res = resultant(m, mp, x)
print(f"Resultant(m, m') = {res}")
print(f"  = {factorint(abs(res))}")
print(f"  = disc(m) * leading_coeff = {disc_m}")
print(f"  disc/res = {Rational(disc_m, res)}")

print(f"\n=== POLYNOMIAL VALUE ANATOMY ===")
# Let's tabulate m(x) at special points
print("m(x) at special points:")
for val, name in [(-1, '-1'), (0, '0'), (1, '1'), (Q, 'Q'), (-Q, '-Q'),
                  (N, 'N'), (MU, 'MU'), (DIM_O, 'DIM_O'), (ALPHA, 'ALPHA'),
                  (r_s, 'r-s'), (PHI3, 'PHI3'), (PHI6, 'PHI6')]:
    mv = int(m.subs(x, val))
    sign = '-' if mv < 0 else '+'
    fv = factorint(abs(mv)) if mv != 0 else '0'
    print(f"  m({name:>5}) = {mv:>8} = {sign}{fv}")

print(f"\n=== CHAR POLY NORM FACTORIZATIONS ===")
# |p(x)| at special integer points, all factored
print("Full char poly p(x) = (x-K)*(x-R)^F*(x-S)^G factorizations:")
for val, name in [(-1, '-1'), (1, '1'), (Q, 'Q'), (-Q, '-Q'),
                  (N, 'N'), (MU, 'MU'), (DIM_O, 'DIM_O'),
                  (r_s, 'r-s'), (PHI3, 'PHI3'), (PHI6, 'PHI6')]:
    pval = (val - K) * (val - R)**F * (val - S)**G
    sign = '-' if pval < 0 else '+'
    print(f"  p({name:>5}) = {sign}  prime factored: {factorint(abs(pval))}")

print(f"\n=== EIGENVALUE PAIR PRODUCTS ===")
print(f"K*R = {K*R} = 2K = 2*{K}: {K*R == 2*K}")
print(f"  = F = {F}: {K*R == F}")
print(f"K*S = {K*S} = -3K ... no: = {K*S}")
print(f"  = -V-DIM_O = {-V-DIM_O}: {K*S == -V-DIM_O}")
print(f"  factored: {factorint(abs(K*S))}")
print(f"R*S = {R*S} = -DIM_O = {-DIM_O}: {R*S == -DIM_O}")
print(f"  = -LAM*MU = {-LAM*MU}: {R*S == -LAM*MU}")

print(f"\nK*R = F = {F}")
print(f"R*S = -DIM_O = {-DIM_O}")
print(f"K*S = -V+DIM_O = ... {K*S}")

# Compute all pairwise products and sums
print(f"\nK+R = {K+R} = K+LAM = {K+LAM} = 2*PHI6 = {2*PHI6}: {K+R == 2*PHI6}")
print(f"K+S = {K+S} = K-MU = DIM_O = {DIM_O}: {K+S == DIM_O}")
print(f"R+S = {R+S} = LAM-MU = {LAM-MU} = -(LAM) = {-LAM}: {R+S == -LAM}")

print(f"\n=== EIGENVALUE TRIPLE SUMMARY ===")
print(f"Sum:     K+R+S = ALPHA = {ALPHA}")
print(f"Product: KRS = -Q*2^N = {-Q*2**N}")
print(f"Sum of products: KR+KS+RS = -2^N = {-2**N}")
print(f"K*R = F = {F}")
print(f"R*S = -DIM_O = {-DIM_O}")
print(f"K+R = 2*PHI6 = {2*PHI6}")
print(f"K+S = DIM_O = {DIM_O}")
print(f"R+S = -LAM = {-LAM}")
print(f"K-R = THETA = ALPHA = {K-R}: {K-R == ALPHA}")
print(f"  Wait: K-R = {K-R} = {ALPHA}: {K-R == ALPHA}")
print(f"  K-R = 10 = ALPHA ✓")
print(f"K-S = K+MU = {K+MU} = 2^MU = {2**MU}: {K+MU == 2**MU}")
print(f"R-S = r-s = {R-S} = r_s = {r_s}")
print(f"  = LAM+MU = {LAM+MU}: {R-S == LAM+MU}")

print(f"\n=== QUADRATIC COMBINATIONS ===")
print(f"K^2+R^2+S^2 = {K**2+R**2+S**2}")
print(f"  = (K+R+S)^2 - 2(KR+KS+RS) = {ALPHA**2} - 2*({-2**N}) = {ALPHA**2 + 2*2**N}")
print(f"  = {ALPHA**2 + 2*2**N}")
print(f"  = {factorint(ALPHA**2 + 2*2**N)}")
# 100 + 64 = 164 = 4*41
print(f"K^2*R^2+K^2*S^2+R^2*S^2 = (KR+KS+RS)^2 - 2KRS(K+R+S)")
val = (K*R+K*S+R*S)**2 - 2*K*R*S*(K+R+S)
print(f"  = {(2**N)**2} - 2*({-Q*2**N})*{ALPHA} = {2**(2*N)} + {2*Q*2**N*ALPHA}")
print(f"  = {val}")
print(f"  = {factorint(val)}")

print(f"\n=== LOG STRUCTURE ===")
import math
print(f"log_2(K) = {math.log2(K):.6f}")
print(f"log_2(|S|) = {math.log2(abs(S)):.6f} = 2")
print(f"log_2(R) = {math.log2(R):.6f} = 1")
print(f"log_Q(K) = {math.log(K)/math.log(Q):.6f}")
print(f"K = Q^? ... K = 12, Q = 3, not a power")
print(f"K = MU*Q = {MU*Q}")
print(f"K = (Q+1)*Q = Q^2+Q = {Q**2+Q}")
print(f"|S| = Q+1 = MU = {MU}")
print(f"R = Q-1 = LAM = {LAM}")
print(f"K = Q*(Q+1) = Q*MU")
print(f"  So K*R*S = Q*MU*LAM*(-MU) = -Q*MU^2*LAM = {-Q*MU**2*LAM}")
print(f"  = -Q*2^N? {-Q*MU**2*LAM == -Q*2**N}")
print(f"  MU^2*LAM = {MU**2*LAM} = 2^N = {2**N}: {MU**2*LAM == 2**N}")
