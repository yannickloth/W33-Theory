import importlib.util
import random

spec = importlib.util.spec_from_file_location("the_exact_map", "..\\THE_EXACT_MAP.py")
# load by path
spec = importlib.util.spec_from_file_location("the_exact_map", "THE_EXACT_MAP.py")
exact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exact)
print(
    "line_rep == expected?",
    exact.line_rep
    == [
        (0, 0),
        (1, 0),
        (0, 0),
        (1, 2),
        (2, 2),
        (1, 1),
        (2, 0),
        (2, 1),
        (1, 1),
        (2, 2),
        (1, 2),
        (2, 1),
    ],
)
random.seed(42)
sample = random.sample(exact.weight_6, 50)
passc = 0
failc = 0
zero = tuple([0] * 12)
for a in sample[:15]:
    for b in sample[:15]:
        for c in sample[:15]:
            if a != b and b != c and a != c:
                bc = tuple((b[i] + c[i]) % 3 for i in range(12))
                ca = tuple((c[i] + a[i]) % 3 for i in range(12))
                ab = tuple((a[i] + b[i]) % 3 for i in range(12))
                if bc != zero and ca != zero and ab != zero:
                    s1 = exact.symplectic_sign(a, bc) * exact.symplectic_sign(b, c)
                    s2 = exact.symplectic_sign(b, ca) * exact.symplectic_sign(c, a)
                    s3 = exact.symplectic_sign(c, ab) * exact.symplectic_sign(a, b)
                    if s1 == s2 == s3:
                        passc += 1
                    else:
                        failc += 1
print("pass,fail,total=", passc, failc, passc + failc)
