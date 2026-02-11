import json

from e8_embedding_group_theoretic import generate_e8_roots

roots = generate_e8_roots()
open("checks/_tmp_root_vectors.json", "w", encoding="utf-8").write(
    json.dumps({str(i): roots[i] for i in range(10)}, indent=2)
)
print("wrote checks/_tmp_root_vectors.json")
