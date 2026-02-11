import json

m = json.loads(open("artifacts/edge_to_e8_root.json").read())
for key in ["(8, 25)", "(7, 8)", "(8,25)", "(25, 8)", "(19, 16)", "(16, 19)"]:
    print(key, key in m)
print("len", len(m))
