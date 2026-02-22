from e8_embedding_group_theoretic import (
    generate_e8_roots,
    vec_add,
    vec_dot,
    vec_neg,
    vec_sub,
)

roots = generate_e8_roots()

r37 = roots[22]
r38 = roots[188]

print("Root index 22:", r37, "norm2=", vec_dot(r37, r37))
print("Root index 188:", r38, "norm2=", vec_dot(r38, r38))
print("Dot product:", vec_dot(r37, r38))
print("r37 + r38:", vec_add(r37, r38))
print(
    "Is r37 + r38 a root?",
    vec_add(r37, r38) in roots or vec_neg(vec_add(r37, r38)) in roots,
)
print("r37 - r38:", vec_sub(r37, r38))
print(
    "Is r37 - r38 a root?",
    vec_sub(r37, r38) in roots or vec_neg(vec_sub(r37, r38)) in roots,
)
