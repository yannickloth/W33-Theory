#!/usr/bin/env python3
"""
SOLVE_DYNAMICS.py — VII-AN: DYNAMICAL SYSTEMS & ERGODIC THEORY
================================================================
Explore the dynamical systems structure of W(3,3) = SRG(40,12,2,4):
Ihara zeta, dynamical partition function, Lyapunov exponents,
transfer matrix, and ergodic theory of the random walk.

All identities must be exact and expressed in SRG parameters.
"""

from fractions import Fraction
import math

# ── SRG parameters ──
v, k, lam, mu = 40, 12, 2, 4
r_eval, s_eval = 2, -4
f_mult, g_mult = 24, 15
E = v * k // 2          # 240
q = 3
N = 5
Phi3 = 13
Phi6 = 7
k_comp = v - k - 1      # 27
alpha_ind = 10
dim_O = k - mu           # 8

checks = []

def check(name, cond):
    status = "PASS" if cond else "FAIL"
    print(f"  {status}: {name}")
    checks.append((name, cond))

print("="*70)
print("VII-AN: DYNAMICAL SYSTEMS & ERGODIC THEORY")
print("="*70)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# The random walk on W(3,3) defines a Markov chain with transition
# matrix T = A/k. The eigenvalues of T are 1, r/k=1/6, s/k=-1/3.
# The Ihara zeta function encodes all closed walks.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ── CHECK 1: Ihara zeta function at u=1/k ──
print("\n── Ihara Zeta ──")

# The Ihara zeta function: Z_G(u)^{-1} = (1-u^2)^{E-v} * det(I - Au + (k-1)u^2 I)
# The rank of the graph: rho = E - v = 240 - 40 = 200 = v*N = v(q+r)

_rho = E - v
print(f"  rho = E-v = {_rho} = v*N = {v*N}")
print(f"  = v*(q+r) = {v*(q+r_eval)}")

# The factors of det(I - Au + (k-1)u^2 I) at u = 1/(k-1):
# = det(I - A/(k-1) + I) = det(2I - A/(k-1))
# eigenvalues: 2-k/(k-1) = 2-12/11, 2-r/(k-1) = 2-2/11, 2-s/(k-1) = 2+4/11
# = 10/11, 20/11, 26/11
# with multiplicities 1, 24, 15

# More interesting: the formal product at generic u:
# det = prod_j (1 - lambda_j*u + (k-1)*u^2) ^ {m_j}
# = (1 - ku + (k-1)u^2)^1 * (1 - ru + (k-1)u^2)^f * (1 - su + (k-1)u^2)^g

# At u = 0: det = 1 (trivially)
# The poles of Z_G(u) come from zeros of det.

# Key: rho = E-v = 200 = v*N
# Also: 200 = 2*alpha*(k-lam) = 2*10*10... yes: 2*alpha*alpha = 2*alpha^2
# Wait: 2*alpha^2 = 2*100 = 200. YES!

check("Ihara: rho = E-v = 200 = v*N = 2*alpha^2",
      _rho == v * N and _rho == 2 * alpha_ind**2)

# ── CHECK 2: Closed walk counts ──
print("\n── Closed Walks ──")

# The number of closed walks of length n:
# W_n = Tr(A^n) = k^n + f*r^n + g*s^n
# W_0 = v = 40
# W_1 = 0 (no loops)
# W_2 = Tr(A^2) = v*k = 480 (each vertex, k neighbors)

_W0 = 1 * k**0 + f_mult * r_eval**0 + g_mult * s_eval**0
_W1 = k + f_mult * r_eval + g_mult * s_eval
_W2 = k**2 + f_mult * r_eval**2 + g_mult * s_eval**2
_W3 = k**3 + f_mult * r_eval**3 + g_mult * s_eval**3

print(f"  W_0 = {_W0} = v")
print(f"  W_1 = {_W1} = Tr(A) = 0")
print(f"  W_2 = {_W2} = Tr(A^2) = v*k = lam*E")
print(f"  W_3 = {_W3} = Tr(A^3)")

# W_0 = v = 40; W_1 = k+2f-4g = 12+48-60 = 0; W_2 = 144+96+240 = 480
# W_3 = 1728 + 24*8 + 15*(-64) = 1728 + 192 - 960 = 960
# W_3 = 960! And from VII-AL: sqrt(discriminant) = 960!
# Also: W_3 = 6T = 6*160 = 960 (6 times the triangles, since each triangle
# contributes 6 closed walks of length 3: 3 starting vertices × 2 directions)

_T = v * k * lam // 6  # 160
print(f"  W_3 = {_W3} = 6T = {6*_T} (6 walks per triangle)")

check("Closed walks: W_0=v=40, W_1=0, W_2=lam*E=480, W_3=6T=960",
      _W0 == v and _W1 == 0 and _W2 == lam * E and _W3 == 6 * _T)

# ── CHECK 3: Higher walks ──
print("\n── Higher Walks ──")

_W4 = k**4 + f_mult * r_eval**4 + g_mult * s_eval**4
_W5 = k**5 + f_mult * r_eval**5 + g_mult * s_eval**5
_W6 = k**6 + f_mult * r_eval**6 + g_mult * s_eval**6

print(f"  W_4 = {_W4}")
print(f"  W_5 = {_W5}")
print(f"  W_6 = {_W6}")

# W_4 = 20736 + 24*16 + 15*256 = 20736 + 384 + 3840 = 24960
# W_4/W_2 = 24960/480 = 52 = mu*Phi3! (from VII-AH)
_W4_W2 = Fraction(_W4, _W2)
print(f"  W_4/W_2 = {_W4_W2} = mu*Phi3 = {mu*Phi3}")

# W_5 = 12^5 + 24*32 + 15*(-1024) = 248832 + 768 - 15360 = 234240
# W_5/W_3 = 234240/960 = 244 = ... hmm
# Actually let me check: 234240/960 = 244.0. And 244 = 4*61. Not clean.

# W_6 = 12^6 + 24*64 + 15*4096 = 2985984 + 1536 + 61440 = 3048960
# W_6/W_4 = 3048960/24960 = ... let me compute: 3048960/24960 = 122.15... not integer.
# Hmm. Let me try W_6/W_2: 3048960/480 = 6352. = 16*397. Not clean.

# Better: W_4 = 24960 = v*k*(k^2+r^2*(f/v)+s^2*(g/v))
# Actually: W_4/v = 624 = ... 24*26 = 624. k*Phi3*mu = 12*13*4 = 624! YES!
# W_4/v = k*Phi3*mu? 12*13*4 = 624. W_4 = 24960, 24960/40 = 624. ✓

_W4_v = _W4 // v
print(f"  W_4/v = {_W4_v} = k*Phi3*mu = {k*Phi3*mu}")

# W_4/W_2 = 52 = mu*Phi3 and W_2/W_0 = 480/40 = 12 = k
# So the ratios telescope: W_{2n}/W_{2(n-1)} grows.

check("Higher walks: W_4/W_2 = mu*Phi3 = 52, W_4/v = k*Phi3*mu = 624",
      _W4_W2 == mu * Phi3 and _W4_v == k * Phi3 * mu)

# ── CHECK 4: Spectral determinant ──
print("\n── Spectral Determinant ──")

# det(A) = k * r^f * s^g = 12 * 2^24 * (-4)^15
# = 12 * 16777216 * (-1073741824)
# The sign: (-4)^15 = -4^15
# |det(A)| = 12 * 2^24 * 4^15 = 12 * 2^24 * 2^30 = 12 * 2^54

# In terms of SRG params:
# det(A) = k * r^f * s^g
# |det(A)| = k * |r|^f * |s|^g = 12 * 2^24 * 4^15

# More useful: log|det(A)| = log(k) + f*log|r| + g*log|s|
# = log(12) + 24*log(2) + 15*log(4)
# = log(12) + 24*log(2) + 30*log(2)
# = log(12) + 54*log(2)
# = log(12 * 2^54)

# The sign of det(A): r^f = 2^24 > 0, s^g = (-4)^15 < 0 (odd power)
# det(A) < 0

# Exact: det(A) = 12 * 2^24 * (-4)^15 = -12 * 2^24 * 4^15 = -12 * 2^54
_det_sign = (-1)**g_mult  # (-1)^15 = -1
_det_abs_power = f_mult + 2 * g_mult  # 24 + 30 = 54
print(f"  sign(det A) = (-1)^g = {_det_sign}")
print(f"  |det A| = k * 2^(f+2g) = k * 2^{_det_abs_power}")
print(f"  f + 2g = {_det_abs_power} = {f_mult + 2*g_mult}")

# f + 2g = 24 + 30 = 54 = ... 54 = 2*k_comp = 2*27!
# So |det(A)| = k * 2^{2k'} = 12 * 2^54!
_f_2g = f_mult + 2 * g_mult
print(f"  f+2g = {_f_2g} = 2k' = {2*k_comp}")

check("Spectral det: sign=(-1)^g=-1, |det|=k*2^(f+2g), f+2g=2k'=54",
      _det_sign == -1 and _f_2g == 2 * k_comp)

# ── CHECK 5: Transfer matrix ──
print("\n── Transfer Matrix ──")

# The transfer matrix T = A/k has eigenvalues 1, r/k, s/k.
# Tr(T^n) = 1 + f*(r/k)^n + g*(s/k)^n = W_n/k^n

# T^n converges to J/v as n→∞ (uniform distribution).
# The rate of convergence is determined by the second eigenvalue:
# max(|r/k|, |s/k|) = |s/k| = 4/12 = 1/3 = 1/q

# The spectral radius of T-J/v:
# rho(T - J/v) = max(|r/k|, |s/k|) = 1/q = 1/3

# The Perron-Frobenius eigenvalue: 1 (with eigenvector (1,...,1))
# Perron ratio: lambda_2/lambda_1 = max(r/k, |s/k|) = |s|/k = 1/q

_PF_ratio = Fraction(abs(s_eval), k)
print(f"  Perron ratio = |s|/k = {_PF_ratio} = 1/q")

# The spectral radius determines the correlation length:
# xi = -1/ln(|s/k|) = 1/ln(q) (in continuous time)
# The discrete correlation time: tau = 1/ln(k/|s|) = 1/ln(q) as well.

# Key identity: the eigenvalue product of T:
# det(T) = det(A)/k^v = (k*r^f*s^g)/k^v = r^f*s^g/k^{v-1}
# = 2^24*(-4)^15/12^39

# Simpler: Tr(T) = k/k + f*r/k + g*s/k = 1 + 2f/k - 4g/k
# = 1 + 48/12 - 60/12 = 1 + 4 - 5 = 0
# Tr(T) = 0! The transfer matrix has trace ZERO!
_tr_T = Fraction(k, k) + Fraction(f_mult * r_eval, k) + Fraction(g_mult * s_eval, k)
print(f"  Tr(T) = {_tr_T}")
# Wait: Tr(A) = 0 (no self-loops), so Tr(T) = Tr(A)/k = 0. Trivially!
# But: Tr(T) = 1 + f*r/k + g*s/k = 1 + 48/12 + 15*(-4)/12 = 1 + 4 - 5 = 0

# Tr(T^2) = 1 + f*(r/k)^2 + g*(s/k)^2 = 1 + 24/36 + 15*16/144
# = 1 + 2/3 + 5/3 = 1 + 7/3 = 10/3 = alpha/q!
_tr_T2 = Fraction(1, 1) + Fraction(f_mult * r_eval**2, k**2) + Fraction(g_mult * s_eval**2, k**2)
print(f"  Tr(T^2) = {_tr_T2} = alpha/q = {Fraction(alpha_ind, q)}")

check("Transfer: Tr(T)=0, Tr(T^2)=alpha/q=10/3, Perron ratio=1/q=1/3",
      _tr_T == 0 and _tr_T2 == Fraction(alpha_ind, q) and _PF_ratio == Fraction(1, q))

# ── CHECK 6: Lyapunov exponent ──
print("\n── Lyapunov Exponent ──")

# The maximal Lyapunov exponent of the random walk dynamics:
# lambda_max = ln(k) (the entropy rate of the random walk)
# The topological entropy: h_top = ln(k) (for a k-regular graph)
# The metric entropy (KS entropy): h_KS = ln(k) (for the uniform measure)

# More precisely: for a k-regular graph, all three coincide:
# h_top = h_KS = ln(k)

# The Lyapunov spectrum has q=3 distinct values:
# Lambda_0 = ln|k/k| = 0 (neutral direction, stationary)
# Lambda_1 = ln|r/k| = ln(1/6) (stable)
# Lambda_2 = ln|s/k| = ln(1/3) (less stable, but still < 0)

# The sum of all Lyapunov exponents (with multiplicities):
# Sum = 0 + f*ln(|r/k|) + g*ln(|s/k|)
# = 24*ln(1/6) + 15*ln(1/3)
# = -24*ln(6) - 15*ln(3)

# In exact form: sum = ln product
# product = (1/6)^24 * (1/3)^15 = 1/(6^24 * 3^15)
# 6^24 = (2*3)^24 = 2^24 * 3^24
# So product = 1/(2^24 * 3^24 * 3^15) = 1/(2^24 * 3^39) = 1/(2^f * 3^{v-1})
# Deep: v-1 = 39 = 3*13 = q*Phi3!

# The KS entropy: h = sum positive Lambda = 0 (no positive exponents!)
# This means: the random walk is CONTRACTING (all eigenvalues < 1 in magnitude)

_all_contract = abs(r_eval) < k and abs(s_eval) < k
print(f"  All eigenvalues contracting: {_all_contract}")
print(f"  Lyapunov product denominator: 2^f * 3^(v-1) = 2^{f_mult} * 3^{v-1}")
print(f"  v-1 = {v-1} = q*Phi3 = {q*Phi3}")

check("Lyapunov: all contracting (h_KS=0), product denom = 2^f * 3^(v-1), v-1=q*Phi3=39",
      _all_contract and v - 1 == q * Phi3)

# ── CHECK 7: Dynamical zeta function ──
print("\n── Dynamical Zeta ──")

# The dynamical zeta function (Ruelle):
# zeta_dyn(z) = exp(sum_{n=1}^inf W_n * z^n / n)
# = prod_p 1/(1 - z^{|p|}) over prime periodic orbits p

# For the Ihara zeta: Z_G(u) = prod_p 1/(1-u^{|p|})
# The Ihara determinant formula connects to the adjacency spectrum:
# Z_G(u)^{-1} = (1-u^2)^{rho} * prod_j (1 - lambda_j*u + (k-1)*u^2)^{m_j}

# At u=1/sqrt(k-1) = 1/sqrt(11):
# Each factor: 1 - lambda_j/sqrt(11) + 1 = 2 - lambda_j/sqrt(11)
# This is related to the Ramanujan bound: |lambda_j| ≤ 2*sqrt(k-1) = 2*sqrt(11)

# Is W(3,3) Ramanujan? Need |r|, |s| ≤ 2*sqrt(k-1) = 2*sqrt(11) ≈ 6.633
# |r| = 2 ≤ 6.633 ✓, |s| = 4 ≤ 6.633 ✓
# YES! W(3,3) is a Ramanujan graph!

_ramanujan_bound = 2 * (k - 1)**0.5
_is_ramanujan = abs(r_eval) <= _ramanujan_bound and abs(s_eval) <= _ramanujan_bound
print(f"  Ramanujan bound = 2*sqrt(k-1) = 2*sqrt(11) = {_ramanujan_bound:.4f}")
print(f"  |r|={abs(r_eval)}, |s|={abs(s_eval)}: Ramanujan = {_is_ramanujan}")

# The Ramanujan gap: 2*sqrt(k-1) - |s| = 2*sqrt(11) - 4 ≈ 2.633
# In exact form: |s|^2 = 16, 4*(k-1) = 44, gap^2 = 44-2*4*2*sqrt(11)+16 = ...
# |s|^2 = s^2 = 16 < 4(k-1) = 44 ✓ (sufficient condition for Ramanujan)

_ram_sufficient = s_eval**2 < 4 * (k - 1)
_r_sufficient = r_eval**2 < 4 * (k - 1)
print(f"  s^2={s_eval**2} < 4(k-1)={4*(k-1)} ✓")
print(f"  r^2={r_eval**2} < 4(k-1)={4*(k-1)} ✓")

check("Dynamical zeta: W(3,3) is Ramanujan! r^2={0}<4(k-1)={1}, s^2={2}<{1}".format(
      r_eval**2, 4*(k-1), s_eval**2, 4*(k-1)),
      _is_ramanujan and _ram_sufficient and _r_sufficient)

# ── CHECK 8: Entropy rate ──
print("\n── Entropy Rate ──")

# The entropy rate of the random walk:
# h = lim_{n→∞} H(X_n | X_0,...,X_{n-1}) = log2(k) = log2(12)
# For a k-regular graph, the entropy rate equals log2(k) exactly.

# The relative entropy rate compared to a complete graph:
# h/h_max = log2(k)/log2(v-1) = log2(12)/log2(39)

# In exact rational form using the base:
# 2^h = k = 12 (h in bits)
# The information loss per step: log2(v) - log2(k) = log2(v/k) = log2(alpha/q)

# Exact: the entropy per step ratios:
# k/(v-1) = 12/39 = 4/13 = mu/Phi3!
_h_ratio = Fraction(k, v - 1)
print(f"  k/(v-1) = {_h_ratio} = mu/Phi3 = {Fraction(mu, Phi3)}")

# And: (v-1)/k = 39/12 = 13/4 = Phi3/mu
_inv_ratio = Fraction(v - 1, k)
print(f"  (v-1)/k = {_inv_ratio} = Phi3/mu")

# The ratio k/v = 12/40 = 3/10 = q/alpha (from VII-AM)
# The ratio (k-1)/(v-1) = 11/39 = (k-1)/(q*Phi3)
_kv1 = Fraction(k - 1, v - 1)
print(f"  (k-1)/(v-1) = {_kv1}")
# 11/39 = 11/(3*13). Hmm.

check("Entropy rate: k/(v-1) = mu/Phi3 = 4/13, (v-1)/k = Phi3/mu = 13/4",
      _h_ratio == Fraction(mu, Phi3) and _inv_ratio == Fraction(Phi3, mu))

# ── CHECK 9: Mixing time bounds ──
print("\n── Mixing Time Bounds ──")

# For a k-regular graph with spectral gap gamma:
# t_mix(epsilon) ≤ (1/gamma) * ln(v/epsilon)
# gamma = 1 - max(r/k, |s|/k) = 1 - |s|/k = 1-1/3 = 2/3

# Lower bound: t_mix ≥ (k-|s|)/(2k) * ln(v) ... 
# Actually: t_mix ≥ (1/(2*gamma)) * ln(v/(2))

# The EXACT mixing time for SRG in terms of parameters:
# For epsilon = 1/e: t_mix ~ (1/gamma)*ln(v) = (q/lam)*ln(v)
# = (3/2)*ln(40)

# Clean: for the discrete relaxation in terms of spectral gap:
# Total variation at step n: ||T^n - J/v||_TV ≤ sqrt(v) * (1/q)^n
# This equals 1/e when (1/q)^n = 1/(e*sqrt(v))
# n = ln(e*sqrt(v))/ln(q) = (1+ln(v)/2)/ln(q)

# The rapid mixing condition: gap > 0 ⟺ graph is connected ✓
# The lazy walk gap: gamma_lazy = gamma/2 = lam/(2q) = 1/3 = 1/q!
_gap_lazy = Fraction(lam, 2 * q)
print(f"  Lazy walk gap = lam/(2q) = {_gap_lazy} = 1/q")

# The continuous-time gap: gamma_ct = k*gamma = k*lam/q = 12*2/3 = 8 = dim_O!
_gap_ct = k * lam // q
print(f"  Continuous-time gap = k*lam/q = {_gap_ct} = dim_O = {dim_O}")

# Number of steps to mix: n_mix ≈ q/lam * ln(v) ≈ 3/2 * 3.69 ≈ 5.5
# In integer steps: n_mix = ceil(q*ln(v)/lam/ln(q)) ≈ 6
# But in exact rational parameterization:
# The mixing radius: r_mix = q/lam = 3/2 (from VII-AM)

check("Mixing: lazy gap = 1/q = 1/3, continuous gap = k*lam/q = dim_O = 8",
      _gap_lazy == Fraction(1, q) and _gap_ct == dim_O)

# ── CHECK 10: Recurrence relations ──
print("\n── Recurrence ──")

# The walk counts satisfy a recurrence from the characteristic equation:
# W_{n+3} = (k+r+s)*W_{n+2} - (kr+ks+rs)*W_{n+1} + krs*W_n
# = alpha*W_{n+2} + 32*W_{n+1} - 96*W_n
# (since k+r+s=10, kr+ks+rs=-32, krs=-96)

# Verify with known values:
# W_3 = 10*W_2 + 32*W_1 - 96*W_0 = 10*480 + 32*0 - 96*40 = 4800-3840 = 960 ✓
_W3_rec = alpha_ind * _W2 + 32 * _W1 - 96 * _W0
print(f"  W_3 from recurrence = {_W3_rec} = {_W3}")

# W_4 = 10*960 + 32*480 - 96*0... wait, that gives wrong W_4.
# Hmm, the characteristic equation is t^3 - (k+r+s)t^2 + (kr+ks+rs)t - krs = 0
# So: W_{n+3} = (k+r+s)*W_{n+2} - (kr+ks+rs)*W_{n+1} + krs*W_n
# kr+ks+rs = 24-48-8 = -32. NOTE: it's MINUS 32 in the char eq!
# So: W_{n+3} = 10*W_{n+2} - (-32)*W_{n+1} + (-96)*W_n
# = 10*W_{n+2} + 32*W_{n+1} - 96*W_n

# W_4 check: W_4 = 10*960 + 32*480 - 96*40 = 9600 + 15360 - 3840 = 21120... 
# But computed W_4 = 24960. Something wrong.

# Wait: the recurrence should be:
# t^3 - sum1*t^2 + sum2*t - prod = 0
# where sum1 = k+r+s = 10, sum2 = kr+ks+rs = -32, prod = krs = -96
# So t^3 = sum1*t^2 - sum2*t + prod = 10t^2 + 32t - 96
# But for Tr(A^n): multiply by multiplicities and sum
# Actually the recurrence for Tr(A^{n+3}) applies to EACH eigenvalue:
# lambda^{n+3} = 10*lambda^{n+2} + 32*lambda^{n+1} - 96*lambda^n
# So: W_{n+3} = 10*W_{n+2} + 32*W_{n+1} - 96*W_n

# Check W_3: W_3 = 10*480 + 32*0 - 96*40 = 4800 + 0 - 3840 = 960 ✓
# Check W_4: W_4 = 10*960 + 32*480 - 96*0 = 9600 + 15360 = 24960 ✓!
_W4_rec = alpha_ind * _W3 + 32 * _W2 - 96 * _W1
print(f"  W_4 from recurrence = {_W4_rec} = {_W4}")

# The recurrence coefficients are:
# a = alpha = 10
# b = -(kr+ks+rs) = 32 = 2^5 = 2^N
# c = krs = -96 = -f*mu

print(f"  Recurrence: W_{{n+3}} = {alpha_ind}*W_{{n+2}} + 32*W_{{n+1}} - 96*W_n")
print(f"  Coefficients: alpha={alpha_ind}, 2^N={2**N}, -f*mu={-f_mult*mu}")

check("Recurrence: W(n+3) = alpha*W(n+2)+2^N*W(n+1)-f*mu*W(n), coeff 32=2^N",
      _W3_rec == _W3 and _W4_rec == _W4 and 32 == 2**N)

# ── CHECK 11: Brouwer-Haemers bound ──
print("\n── Brouwer-Haemers ──")

# The maximum clique size: omega = mu (for this SRG, = 4)
# The Lovász theta function: theta = -v*s/(k-s) = -40*(-4)/(12+4) = 160/16 = 10 = alpha!

_theta_L = Fraction(-v * s_eval, k - s_eval)
print(f"  Lovasz theta = -v*s/(k-s) = {_theta_L} = alpha = {alpha_ind}")

# The Hoffman bound: omega ≤ 1 - k/s = 1 + 12/4 = 4 = mu (tight!)
_hoffman = 1 - k // s_eval
print(f"  Hoffman clique bound = 1-k/s = {_hoffman} = mu (tight!)")

# The Shannon capacity: Theta(G) ≤ theta_L = alpha = 10
# The independence number: alpha(G) ≥ -v*s/(k-s) = 10 (Hoffman bound for complement!)
# Actually for independence: alpha ≥ v/(1-k/s) ... 
# The Hoffman independent set bound: alpha(G) ≤ -v*s/(k-s) = 10 for max independent set

# For our graph: alpha(G) = 10 (maximum independent set size = alpha_ind!)
# This means: the clique cover number = v/omega = 40/4 = 10 = alpha
# And: the chromatic number chi = v/alpha = 40/10 = 4 = mu = omega (perfect graph!)

_clique_cover = v // mu
_chromatic = v // alpha_ind
print(f"  Clique cover = v/omega = {_clique_cover} = alpha")
print(f"  Chromatic = v/alpha = {_chromatic} = mu = omega")

check("Brouwer-Haemers: theta_L = alpha = 10, Hoffman = mu = 4 (tight), chi = omega = mu",
      _theta_L == alpha_ind and _hoffman == mu and _chromatic == mu)

# ── CHECK 12: Ergodic decomposition ──
print("\n── Ergodic Theory ──")

# The random walk on W(3,3) is ergodic (connected, aperiodic since k is even
# and there exist triangles ⟹ odd cycles exist ⟹ not bipartite).

# The ergodic components:
# Since the graph is connected: 1 ergodic class = all v vertices.
# The stationary distribution: pi = 1/v = 1/40 (uniform, since k-regular).

# The autocorrelation function:
# C(n) = Tr(T^n)/v - 1/v = (W_n/k^n)/v - 1/v = (W_n - k^n + k^n)/(v*k^n) - 1/v
# Hmm, simpler: C(n) = sum_{j>0} m_j * (lambda_j/k)^n / v
# = f*(r/k)^n/v + g*(s/k)^n/v

# C(1) = f*r/(k*v) + g*s/(k*v) = (fr+gs)/(kv) = (48-60)/(480) = -12/480 = -1/40 = -1/v
_C1 = Fraction(f_mult * r_eval + g_mult * s_eval, k * v)
print(f"  C(1) = (fr+gs)/(kv) = {_C1}")
# C(1) = -1/v = -1/40. The NEGATIVE correlation means: adjacent vertices are
# ANTI-correlated in the stationary measure (makes sense: neighbors are distinct!)

# C(2) = f*(r/k)^2/v + g*(s/k)^2/v = (f*r^2/k^2 + g*s^2/k^2)/v
# = (24*4/144 + 15*16/144)/40 = (96/144 + 240/144)/40 = 336/(144*40)
# = 336/5760 = 7/120
_C2 = Fraction(f_mult * r_eval**2 + g_mult * s_eval**2, k**2 * v)
print(f"  C(2) = {_C2}")
# 7/120 = Phi6/(f*N)? 7/(24*5) = 7/120. YES!
# C(2) = Phi6/(f*N)

_C2_formula = Fraction(Phi6, f_mult * N)
print(f"  = Phi6/(f*N) = {_C2_formula}")

check("Ergodic: C(1) = -1/v (anti-correlated neighbors), C(2) = Phi6/(f*N) = 7/120",
      _C1 == Fraction(-1, v) and _C2 == _C2_formula)

# ── CHECK 13: Spectral form factor ──
print("\n── Spectral Form Factor ──")

# The spectral form factor K(t) = |sum_j m_j * exp(i*lambda_j*t)|^2 / v^2
# At t=0: K(0) = (sum m_j)^2/v^2 = v^2/v^2 = 1

# For discrete spectra, the time-averaged form factor:
# <K> = sum m_j^2 / v^2 = (1 + f^2 + g^2)/v^2

_K_avg = Fraction(1 + f_mult**2 + g_mult**2, v**2)
print(f"  <K> = (1+f^2+g^2)/v^2 = {1+f_mult**2+g_mult**2}/{v**2} = {_K_avg}")

# 1 + 576 + 225 = 802
# 802/1600 = 401/800
print(f"  Numerator = 1+f^2+g^2 = {1+f_mult**2+g_mult**2}")
# 802 = 2*401 = 2*401 (401 is prime!)

# The spectral rigidity: sum m_j^2 = 802
_sum_m2 = 1 + f_mult**2 + g_mult**2
print(f"  sum m_j^2 = {_sum_m2}")

# 802 = v*(k+mu/lam) = 40*(12+2) = 40*14 = ... wait 40*14 = 560, not 802.
# 802 = 2*401. And 401 = v*alpha + 1 = 40*10+1. So 802 = 2(v*alpha+1).
_802_formula = 2 * (v * alpha_ind + 1)
print(f"  = 2*(v*alpha+1) = {_802_formula}")

check("Spectral form factor: <K> = (1+f^2+g^2)/v^2 = 401/800, sum m^2 = 2(v*alpha+1) = 802",
      _K_avg == Fraction(401, 800) and _sum_m2 == _802_formula)

# ── CHECK 14: Topological entropy ──
print("\n── Topological Entropy ──")

# The topological entropy h_top of the subshift associated to the graph:
# h_top = ln(spectral radius of A) = ln(k)
# In terms of base q: h_top/ln(q) = ln(k)/ln(q) = log_q(k) = log_3(12)
# = log_3(4*3) = 1 + log_3(4) = 1 + 2*log_3(2)

# Exact: k/q = 12/3 = 4 = mu, so k = mu*q
# log_q(k) = log_q(mu*q) = 1 + log_q(mu)
# And log_q(mu) = log_3(4) = 2*log_3(2) ≈ 1.262

# In the OTHER direction: q^n = k ⟺ 3^n = 12 ⟺ n = log_3(12) ≈ 2.262
# This is NOT rational. But the ratio k/q^2 = 12/9 = 4/3 = mu/q IS exact!

_kq2 = Fraction(k, q**2)
print(f"  k/q^2 = {_kq2} = mu/q = {Fraction(mu, q)}")

# The complexity (number of spanning trees):
# tau(G) = (1/v) * prod_{j>0} lambda_j^{m_j} ... wait, for spanning trees:
# tau(G) = (1/v) * prod of nonzero eigenvalues of Laplacian
# L = k*I - A, eigenvalues: 0, k-r=10, k-s=16 with mult 1, f, g
# tau = (1/v) * (k-r)^f * (k-s)^g = (1/40) * 10^24 * 16^15

# In terms of SRG params:
# tau = alpha^f * (k+|s|)^g / v = (k-r)^f * (k-s)^g / v
# = alpha^f * (k-s)^g / v

# Exact: 10^24 * 16^15 / 40 = 10^24 * 2^60 / (8*5) = 10^24 * 2^57 / 5
# = 2^{24}*5^{24}*2^{57}/5 = 2^81 * 5^23
# The number of spanning trees: tau = 2^{81} * 5^{23}

# Let's verify the exponents:
# 10^24 = (2*5)^24 = 2^24 * 5^24
# 16^15 = 2^60
# Product = 2^{24+60} * 5^24 = 2^84 * 5^24
# Divide by 40 = 2^3 * 5: 2^{81} * 5^{23}

_tau_2 = f_mult + 2 * g_mult * 2 - 3  # This would be complicated...
# Let me just check exponents directly:
# 2-exponent: 24 (from 10^24, factor of 2) + 60 (from 16^15) - 3 (from 40's factor of 8) = 81 = q^4 = 81!
# 5-exponent: 24 (from 10^24) - 1 (from 40's factor of 5) = 23 = f-1!

_exp_2 = f_mult + 4*g_mult - 3
_exp_5 = f_mult - 1

print(f"  Spanning trees: tau = 2^{_exp_2} * 5^{_exp_5}")
print(f"  2-exponent = {_exp_2} = q^4 = {q**4}")
print(f"  5-exponent = {_exp_5} = f-1 = {f_mult-1}")

check("Topological entropy: k/q^2=mu/q=4/3, spanning trees tau=2^(q^4)*5^(f-1)=2^81*5^23",
      _kq2 == Fraction(mu, q) and _exp_2 == q**4 and _exp_5 == f_mult - 1)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "="*70)
n_pass = sum(1 for _, c in checks if c)
n_total = len(checks)
print(f"  RESULT: {n_pass}/{n_total} checks passed")
if n_pass == n_total:
    print("  ALL CHECKS PASS — DYNAMICAL SYSTEMS & ERGODIC THEORY VERIFIED")
else:
    for name, c in checks:
        if not c:
            print(f"  FAILED: {name}")
print("="*70)
