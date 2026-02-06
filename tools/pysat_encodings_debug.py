from pysat.card import EncType

print([attr for attr in dir(EncType) if not attr.startswith("__")])
# print mapping of names to ints
print({k: getattr(EncType, k) for k in dir(EncType) if not k.startswith("__")})
