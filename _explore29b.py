import math
from math import gcd, comb, factorial

# SRG parameters
v, k, lam, mu, q = 40, 12, 2, 4, 3
E = 240; r, s = 2, -4; delta = 6
f, g = 24, 15; N = 5; phi3, phi6 = 13, 7
albert, theta, dimO = 27, 10, 8

vals = {'v':v,'k':k,'lam':lam,'mu':mu,'q':q,'N':N,'theta':theta,
        'delta':delta,'f':f,'g':g,'phi3':phi3,'phi6':phi6,
        'albert':albert,'dimO':dimO,'E':E}

print('=== MÖBIUS FUNCTION VALUES ===')
def mobius(n):
    if n == 1: return 1
    d = 2
    factors = []
    temp = n
    while d*d <= temp:
        if temp % d == 0:
            factors.append(d)
            temp //= d
            if temp % d == 0:
                return 0
        d += 1
    if temp > 1:
        factors.append(temp)
    return (-1)**len(factors)

# Mertens function M(n) = sum_{k=1}^{n} mu(k)
def mertens(n):
    return sum(mobius(kk) for kk in range(1, n+1))

for name, val in sorted(vals.items(), key=lambda x: x[1]):
    m = mertens(val)
    hits = [nm for nm, vl in vals.items() if abs(m) == vl]
    print(f'  M({name}={val}) = {m}', f'= {hits}' if hits else '')

print()
print('=== LIOUVILLE LAMBDA ===')
def liouville(n):
    if n == 1: return 1
    d = 2
    count = 0
    while d*d <= n:
        while n % d == 0:
            count += 1
            n //= d
        d += 1
    if n > 1: count += 1
    return (-1)**count

# Summatory Liouville L(n) = sum_{k=1}^{n} lambda(k)
for name, val in [('v',v),('k',k),('E',E),('f',f),('albert',albert),('theta',theta)]:
    L = sum(liouville(kk) for kk in range(1, val+1))
    hits = [nm for nm, vl in vals.items() if abs(L) == vl]
    print(f'  L({name}={val}) = {L}', f'= {hits}' if hits else '')

print()
print('=== DIGITAL ROOT / PERSISTENT MULTIPLICATIVE ===')
def multiplicative_persistence(n):
    steps = 0
    while n >= 10:
        prod = 1
        for d in str(n):
            prod *= int(d)
        n = prod
        steps += 1
    return steps, n  # (steps, final digit)

for name, val in vals.items():
    if val < 10: continue
    steps, final = multiplicative_persistence(val)
    hits_s = [nm for nm, vl in vals.items() if steps == vl]
    hits_f = [nm for nm, vl in vals.items() if final == vl]
    if hits_s or hits_f:
        extra = []
        if hits_s: extra.append(f'steps={steps}={hits_s}')
        if hits_f: extra.append(f'final={final}={hits_f}')
        print(f'  MP({name}={val}): {", ".join(extra)}')

print()
print('=== ADDITIVE PERSISTENCE ===')
def additive_persistence(n):
    steps = 0
    while n >= 10:
        n = sum(int(d) for d in str(n))
        steps += 1
    return steps, n

for name, val in vals.items():
    if val < 10: continue
    steps, final = additive_persistence(val)
    hits_s = [nm for nm, vl in vals.items() if steps == vl]
    hits_f = [nm for nm, vl in vals.items() if final == vl]
    if hits_s or hits_f:
        extra = []
        if hits_s: extra.append(f'steps={steps}={hits_s}')
        if hits_f: extra.append(f'final={final}={hits_f}')
        print(f'  AP({name}={val}): {", ".join(extra)}')

print()
print('=== FIBONACCI ENTRY POINT ===')
# alpha(n) = smallest m such that n | F(m)
def fib_entry(n):
    if n <= 0: return None
    a, b = 0, 1
    for m in range(1, 10*n+1):
        a, b = b, a+b
        if a % n == 0:
            return m
    return None

for name, val in sorted(vals.items(), key=lambda x: x[1]):
    if val < 2: continue
    ep = fib_entry(val)
    if ep is not None:
        hits = [nm for nm, vl in vals.items() if ep == vl]
        if hits:
            print(f'  alpha({name}={val}) = {ep} = {hits}')

print()
print('=== PISANO PERIOD ===')
# pi(n) = Pisano period = period of Fibonacci sequence mod n
def pisano_period(n):
    a, b = 0, 1
    for i in range(1, 6*n+10):
        a, b = b, (a+b) % n
        if a == 0 and b == 1:
            return i
    return None

for name, val in sorted(vals.items(), key=lambda x: x[1]):
    if val < 2: continue
    pp = pisano_period(val)
    if pp is not None:
        hits = [nm for nm, vl in vals.items() if pp == vl]
        if hits:
            print(f'  pi({name}={val}) = {pp} = {hits}')

print()
print('=== MÖBIUS FUNCTION AT SRG VALUES ===')
for name, val in sorted(vals.items(), key=lambda x: x[1]):
    m = mobius(val)
    print(f'  mu({name}={val}) = {m}')

print()
print('=== PARTITION INTO DISTINCT PARTS ===')
def partitions_distinct(n):
    # Q(n) = number of partitions of n into distinct parts
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(n, i - 1, -1):
            dp[j] += dp[j - i]
    return dp[n]

for name, val in vals.items():
    if val > 100: continue
    pd = partitions_distinct(val)
    hits = [nm for nm, vl in vals.items() if pd == vl]
    if hits:
        print(f'  Q({name}={val}) = {pd} = {hits}')

print()
print('=== HIGHLY COMPOSITE / ANTI-PRIME ===')
# Check if SRG values are highly composite
def count_divisors(n):
    return sum(1 for d in range(1, n+1) if n%d==0)

max_divs = 0
hc = []
for n in range(1, 250):
    d = count_divisors(n)
    if d > max_divs:
        max_divs = d
        hc.append(n)

for name, val in vals.items():
    if val in hc:
        print(f'  {name}={val} is highly composite (rank {hc.index(val)+1})')

print()
print('=== PRONIC CHAIN ===')
# Pronic(n) = n*(n+1). Key finding: Pronic(g) = g*(g+1) = 15*16 = 240 = E!
for name, val in vals.items():
    p = val * (val + 1)
    hits = [nm for nm, vl in vals.items() if p == vl]
    if hits:
        print(f'  Pronic at {name}={val}: {val}*{val+1} = {p} = {hits}')

print()
print('=== ARITHMETIC DERIVATIVE CHAIN ===')
def arith_deriv(n):
    if n <= 1: return 0
    d = 2
    temp = n
    result = 0
    while d*d <= temp:
        while temp % d == 0:
            result += n // d
            temp //= d
        d += 1
    if temp > 1:
        result += n // temp
    return result

# Chain: D(D(...(n)...))
for name, val in [('v',v),('k',k),('f',f),('albert',albert),('theta',theta),('dimO',dimO),('delta',delta),('g',g)]:
    chain = [val]
    x = val
    for _ in range(6):
        x = arith_deriv(x)
        if x == 0 or x in chain: break
        chain.append(x)
    srg_hits = []
    for i, c in enumerate(chain):
        for nm, vl in vals.items():
            if c == vl:
                srg_hits.append(f'{nm}={vl}')
    print(f'  D-chain({name}={val}): {chain}  SRG: {srg_hits}')

print()
print('=== SOPFR CHAIN ===')
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

def sopfr(n):
    return sum(p*e for p, e in factorize(n).items())

for name, val in [('v',v),('k',k),('f',f),('albert',albert),('E',E),('theta',theta)]:
    chain = [val]
    x = val
    for _ in range(8):
        x = sopfr(x)
        if x <= 1 or x in chain: break
        chain.append(x)
    srg_hits = []
    for i, c in enumerate(chain):
        for nm, vl in vals.items():
            if c == vl:
                srg_hits.append(f'step{i}={nm}')
    print(f'  sopfr-chain({name}={val}): {chain}  SRG: {srg_hits}')

print()
print('=== STERN-BROCOT / CALKIN-WILF ===')
# Position in Calkin-Wilf tree: fusc sequence
def fusc(n):
    if n <= 1: return n
    if n % 2 == 0:
        return fusc(n // 2)
    else:
        return fusc((n-1) // 2) + fusc((n+1) // 2)

for i in range(1, 50):
    f = fusc(i)
    for name, val in vals.items():
        if f == val and val > 3:
            print(f'  fusc({i}) = {f} = {name}')
