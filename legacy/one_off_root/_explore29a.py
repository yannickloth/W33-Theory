import math
from math import gcd, comb, factorial
from itertools import combinations

# SRG parameters
v, k, lam, mu, q = 40, 12, 2, 4, 3
E = 240; r, s = 2, -4; delta = 6
f, g = 24, 15; N = 5; phi3, phi6 = 13, 7
albert, theta, dimO = 27, 10, 8

vals = {'v':v,'k':k,'lam':lam,'mu':mu,'q':q,'N':N,'theta':theta,
        'delta':delta,'f':f,'g':g,'phi3':phi3,'phi6':phi6,
        'albert':albert,'dimO':dimO,'E':E}

print('=== CONTINUED FRACTION PARTIAL QUOTIENTS ===')
def cf_sqrt(n, terms=10):
    a0 = int(math.isqrt(n))
    if a0*a0 == n: return [a0]
    m, d, a = 0, 1, a0
    result = [a0]
    for _ in range(terms):
        m = d*a - m
        d = (n - m*m)//d
        a = (a0 + m)//d
        result.append(a)
    return result

for name, val in [('v',v),('k',k),('E',E),('f',f),('g',g),('albert',albert),('theta',theta)]:
    cf = cf_sqrt(val)
    print(f'  sqrt({name}={val}) cf = {cf}')
    period = cf[1:] if len(cf) > 1 else []
    plen = 0
    if period:
        for plen in range(1, len(period)+1):
            if period[:plen] == period[plen:2*plen]:
                break
    hits = []
    for nm, vl in vals.items():
        if plen == vl: hits.append(nm)
    if hits:
        print(f'    period length = {plen} = {hits}')

print()
print('=== PERFECT POWER TESTS ===')
for name, val in vals.items():
    for base in range(2, val):
        for exp in range(2, 20):
            if base**exp == val:
                print(f'  {name}={val} = {base}^{exp}')
                break
        if base**2 > val: break

print()
print('=== POLYGONAL NUMBER TESTS ===')
def polygonal(s, n):
    return n * ((s-2)*n - (s-4)) // 2

for s_val in range(3, 15):
    hits = {}
    for n in range(1, 100):
        p = polygonal(s_val, n)
        for name, val in vals.items():
            if p == val:
                hits[name] = (n, val)
    if hits:
        parts = ', '.join(f'{nm}: P({h[0]})={h[1]}' for nm, h in hits.items())
        print(f'  {s_val}-gonal: {parts}')

print()
print('=== CENTERED POLYGONAL NUMBERS ===')
def centered_polygonal(s_val, n):
    return s_val*n*(n-1)//2 + 1

for s_val in range(3, 20):
    hits = {}
    for n in range(1, 50):
        c = centered_polygonal(s_val, n)
        for name, val in vals.items():
            if c == val:
                hits[name] = (n, val)
    if hits:
        parts = ', '.join(f'{nm}: C({h[0]})={h[1]}' for nm, h in hits.items())
        print(f'  Centered {s_val}-gonal: {parts}')

print()
print('=== STAR / STELLATED / HEX NUMBERS ===')
for n in range(1, 30):
    star = 6*n*(n-1)+1
    for name, val in vals.items():
        if star == val:
            print(f'  Star({n}) = {star} = {name}')

for n in range(1, 30):
    h = 2*n*n - 2*n + 1
    for name, val in vals.items():
        if h == val:
            print(f'  Hex({n}) = {h} = {name}')

print()
print('=== PRONIC / OBLONG NUMBERS ===')
for n in range(1, 30):
    pronic = n*(n+1)
    for name, val in vals.items():
        if pronic == val:
            print(f'  Pronic({n}) = {pronic} = {name}')

print()
print('=== FACTORIZATION PROPERTIES ===')
def factorize(n):
    factors = {}
    d = 2
    while d*d <= n:
        while n % d == 0:
            factors[d] = factors.get(d,0) + 1
            n //= d
        d += 1
    if n > 1: factors[n] = factors.get(n,0) + 1
    return factors

for name, val in vals.items():
    if val < 2: continue
    facs = factorize(val)
    omega = len(facs)
    bigomega = sum(facs.values())
    rad = 1
    for p in facs: rad *= p
    hits_o = [nm for nm, vl in vals.items() if omega == vl]
    hits_bo = [nm for nm, vl in vals.items() if bigomega == vl]
    hits_r = [nm for nm, vl in vals.items() if rad == vl]
    if hits_o or hits_bo or hits_r:
        extra = []
        if hits_o: extra.append(f'omega={omega}={hits_o}')
        if hits_bo: extra.append(f'Omega={bigomega}={hits_bo}')
        if hits_r: extra.append(f'rad={rad}={hits_r}')
        print(f'  {name}={val}={dict(facs)}: {", ".join(extra)}')

print()
print('=== ALIQUOT SEQUENCES ===')
def aliquot_step(n):
    return sum(d for d in range(1,n) if n%d==0)

for name, val in [('v',v),('k',k),('f',f),('albert',albert),('theta',theta),('E',E)]:
    seq = [val]
    n = val
    for _ in range(15):
        n = aliquot_step(n)
        if n == 0: break
        seq.append(n)
        if n == 1: break
        if n in seq[:-1]:
            break
    hit_vals = []
    for i, sv in enumerate(seq):
        for nm, vl in vals.items():
            if sv == vl: hit_vals.append(f'step{i}={nm}')
    print(f'  aliquot({name}={val}): {seq[:10]}')
    if hit_vals: print(f'    SRG hits: {hit_vals}')

print()
print('=== HAPPY NUMBERS ===')
def digit_sq_sum(n):
    return sum(int(d)**2 for d in str(n))

for name, val in vals.items():
    if val < 2: continue
    n = val
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = digit_sq_sum(n)
    if n == 1:
        steps = 0
        n2 = val
        while n2 != 1:
            n2 = digit_sq_sum(n2)
            steps += 1
        hits = [nm for nm, vl in vals.items() if steps == vl]
        x = f' = {hits}' if hits else ''
        print(f'  {name}={val} is HAPPY in {steps} steps{x}')

print()
print('=== SOPFR (SUM OF PRIME FACTORS WITH REPETITION) ===')
for name, val in vals.items():
    if val < 2: continue
    facs = factorize(val)
    sopfr_val = sum(p*e for p,e in facs.items())
    hits = [nm for nm, vl in vals.items() if sopfr_val == vl]
    if hits:
        print(f'  sopfr({name}={val}) = {sopfr_val} = {hits}')

print()
print('=== ARITHMETIC DERIVATIVE ===')
def arith_deriv(n):
    if n <= 1: return 0
    facs = factorize(n)
    result = 0
    for p, e in facs.items():
        result += n * e // p
    return result

for name, val in vals.items():
    if val < 2: continue
    ad = arith_deriv(val)
    hits = [nm for nm, vl in vals.items() if ad == vl]
    if hits:
        print(f'  D({name}={val}) = {ad} = {hits}')

print()
print('=== JACOBI SYMBOL / LEGENDRE SYMBOL ===')
def jacobi(a, n):
    if n <= 0 or n % 2 == 0: return None
    a = a % n
    t = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5): t = -t
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3: t = -t
        a = a % n
    return t if n == 1 else 0

# Quadratic residues mod small SRG primes
for p in [q, N, phi6, phi3]:
    qr = [x for x in range(1, p) if pow(x, (p-1)//2, p) == 1]
    qnr = [x for x in range(1, p) if pow(x, (p-1)//2, p) == p-1]
    print(f'  QR mod {p}: {qr}, QNR: {qnr}')
    # count QRs
    num_qr = len(qr)
    hits = [nm for nm, vl in vals.items() if num_qr == vl]
    if hits:
        print(f'    #QR mod {p} = {num_qr} = {hits}')

print()
print('=== TETRAHEDRAL / PYRAMIDAL NUMBERS ===')
# Tetrahedral T(n) = n(n+1)(n+2)/6
for n in range(1, 30):
    tet = n*(n+1)*(n+2)//6
    for name, val in vals.items():
        if tet == val:
            print(f'  Tetra({n}) = {tet} = {name}')

# Square pyramidal P(n) = n(n+1)(2n+1)/6
for n in range(1, 30):
    pyr = n*(n+1)*(2*n+1)//6
    for name, val in vals.items():
        if pyr == val:
            print(f'  Pyramid({n}) = {pyr} = {name}')

print()
print('=== EULER NUMBER (ZIGZAG/TANGENT/SECANT) ===')
# E_0=1, E_1=0, E_2=-1, E_3=0, E_4=5, etc. (secant/tangent numbers)
# Tangent numbers: T(1)=1, T(2)=2, T(3)=16, T(4)=272
# Up/down numbers: 1,1,1,2,5,16,61,272,...
def euler_zigzag(nmax):
    # A000111
    a = [0]*(nmax+1)
    a[0] = 1
    for nn in range(1, nmax+1):
        a[nn] = 0
        for kk in range(nn):
            a[nn] += comb(nn-1, kk) * a[kk] * a[nn-1-kk] // (2 if nn > 1 else 1)
    # Actually use a different approach
    T = [0]*(nmax+2)
    T[0] = 1
    for nn in range(1, nmax+1):
        T[nn] = nn * T[nn-1]
    # Use explicit recurrence for A000111
    E_arr = [0]*(nmax+1)
    E_arr[0] = 1
    if nmax >= 1: E_arr[1] = 1
    for nn in range(2, nmax+1):
        # Use the alternating permutation count
        pass
    # Simpler: direct computation
    result = [1, 1]
    for nn in range(2, nmax+1):
        # Boustrophedon transform
        row = [0]*(nn+1)
        row[0] = 0
        for jj in range(nn):
            if nn % 2 == 0:
                row[jj+1] = row[jj] + result[jj]
            else:
                row[nn-jj] = row[nn-jj-1+1] if nn-jj < nn else 0
        # Actually let me just use the standard algorithm
        pass
    return result

# Simple zigzag computation
def zigzag_numbers(nmax):
    T = [[0]*(nmax+1) for _ in range(nmax+1)]
    T[0][0] = 1
    for nn in range(1, nmax+1):
        if nn % 2 == 1:  # odd
            T[nn][0] = 0
            for kk in range(1, nn+1):
                T[nn][kk] = T[nn][kk-1] + T[nn-1][kk-1]
        else:  # even
            T[nn][nn] = 0
            for kk in range(nn-1, -1, -1):
                T[nn][kk] = T[nn][kk+1] + T[nn-1][kk]
    return [T[nn][0] if nn%2==0 else T[nn][nn] for nn in range(nmax+1)]

zz = zigzag_numbers(15)
print(f'  Zigzag numbers: {zz}')
for i, z in enumerate(zz):
    for name, val in vals.items():
        if z == val:
            print(f'  Zigzag({i}) = {z} = {name}')

print()
print('=== DOUBLE FACTORIAL ===')
# n!! = n*(n-2)*(n-4)*...
def double_factorial(n):
    result = 1
    while n > 1:
        result *= n
        n -= 2
    return result

for n in range(1, 20):
    df = double_factorial(n)
    for name, val in vals.items():
        if df == val:
            print(f'  {n}!! = {df} = {name}')

print()
print('=== SUBFACTORIAL (DERANGEMENTS) ===')
def subfactorial(n):
    if n == 0: return 1
    if n == 1: return 0
    return (n-1) * (subfactorial(n-1) + subfactorial(n-2))

for n in range(0, 15):
    sf = subfactorial(n)
    for name, val in vals.items():
        if sf == val:
            print(f'  !{n} = {sf} = {name}')

print()
print('=== PRIMORIAL / COMPOSITORIAL ===')
def primorial(n):
    result = 1
    for i in range(2, n+1):
        if all(i%j != 0 for j in range(2, int(i**0.5)+1)):
            result *= i
    return result

for n in range(2, 20):
    pm = primorial(n)
    for name, val in vals.items():
        if pm == val:
            print(f'  primorial({n}) = {pm} = {name}')
