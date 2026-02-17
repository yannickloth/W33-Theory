"""
Compute entropy-like diagnostics for Leech vs Monster corrections.
"""

import math

leech = 196560
monster = 196883
correction = monster - leech

S_leech = math.log(leech)
S_monster = math.log(monster)

print(f"Leech dim = {leech}")
print(f"Monster smallest rep = {monster} = Leech + {correction}")
print()
print(f"Entropy proxy: ln(dim)")
print(f"  ln(Leech)    = {S_leech:.6f}")
print(f"  ln(Monster)  = {S_monster:.6f}")
print(f"  ΔS = ln(Monster) - ln(Leech) = {S_monster - S_leech:.6e}")
print()
print(f"Relative change: {monster/leech - 1:.6e} (≈ { (monster/leech - 1)*100:.6f}% )")
