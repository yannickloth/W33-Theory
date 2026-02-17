"""Fetch CTblLib and export minimal Monster character columns to JSON.

This script downloads a pinned CTblLib source archive (used by GAP's CTblLib
package), extracts the Monster ordinary character table `M` from
`ctomonst.tbl`, and exports a small subset of integer columns needed for
offline, deterministic tests and analyses:

  - 1A (degree)
  - 2A
  - 2B
  - 3A
  - 3B
  - 3C
  - 29A
  - 41A
  - 31A, 31B (trace only)
  - 47A, 47B (trace only)
  - 59A, 59B (trace only)
  - 71A, 71B (trace only)
  - 5A, 5B, 7A, 7B, 11A, 13A, 13B, 17A, 19A (integers)
  - 23A, 23B (trace only)

The resulting file is written to `data/monster_ctbllib_charcols.json`.

Run:
  .venv\\Scripts\\python.exe -X utf8 scripts\\fetch_monster_ctbllib_charcols.py
"""

from __future__ import annotations

import ast
import json
import re
import tarfile
import urllib.request
from pathlib import Path

CTBLLIB_VERSION = "1.3.11"
CTBLLIB_URL = (
    "https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/"
    "gap-ctbllib/1.3.11-1/gap-ctbllib_1.3.11.orig.tar.xz"
)


def _download(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_size > 0:
        return
    with urllib.request.urlopen(url, timeout=60) as r:  # nosec - pinned URL
        dst.write_bytes(r.read())


def _extract_member(archive: Path, member: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, mode="r:xz") as tf:
        m = tf.getmember(member)
        tf.extract(m, path=out_dir)  # nosec - member path is fixed
    return out_dir / member


def _parse_mot_args(tbl_text: str, table_id: str) -> list[str]:
    start = tbl_text.find(f'MOT("{table_id}"')
    if start < 0:
        raise ValueError(f'MOT("{table_id}") not found')

    j = tbl_text.find(f'"{table_id}"', tbl_text.find("(", start))
    j = tbl_text.find(",", j)
    pos = j + 1

    args: list[str] = []
    while len(args) < 5:
        while pos < len(tbl_text) and tbl_text[pos].isspace():
            pos += 1
        if pos >= len(tbl_text) or tbl_text[pos] != "[":
            raise ValueError(f"Unexpected token at {pos}: {tbl_text[pos:pos+20]!r}")

        depth = 0
        buf: list[str] = []
        in_str = False
        escape = False
        while pos < len(tbl_text):
            ch = tbl_text[pos]
            buf.append(ch)
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "[":
                    depth += 1
                elif ch == "]":
                    depth -= 1
                    if depth == 0:
                        pos += 1
                        break
            pos += 1

        args.append("".join(buf))
        while pos < len(tbl_text) and tbl_text[pos].isspace():
            pos += 1
        if pos < len(tbl_text) and tbl_text[pos] == ",":
            pos += 1

    return args


def _split_top_level_list_items(list_text: str) -> list[str]:
    """Split a GAP list string into top-level items (handles empty items)."""
    if not list_text.startswith("["):
        raise ValueError("expected list")

    depth = 1
    items: list[str] = []
    buf: list[str] = []
    in_str = False
    escape = False
    for ch in list_text[1:]:
        if in_str:
            buf.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue

        if ch == '"':
            in_str = True
            buf.append(ch)
            continue

        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1

        if ch == "," and depth == 1:
            items.append("".join(buf).strip())
            buf = []
            continue

        if depth == 0:
            items.append("".join(buf).strip())
            break

        buf.append(ch)

    return items


def _extract_cols(row_str: str, cols: list[int]) -> dict:
    if row_str.startswith("[GALOIS"):
        m = re.match(r"\[GALOIS,\[(\d+),(\d+)\]\]$", row_str)
        if not m:
            raise ValueError("bad GALOIS row")
        return {"GALOIS": (int(m.group(1)), int(m.group(2)))}

    if not (row_str.startswith("[") and row_str.endswith("]")):
        raise ValueError("bad row")

    cols_set = set(cols)
    out: dict[int, str] = {}
    col = 1
    token: list[str] = []
    paren = 0
    for ch in row_str[1:-1]:
        if ch == "(":
            paren += 1
        elif ch == ")":
            paren -= 1
        if ch == "," and paren == 0:
            if col in cols_set:
                out[col] = "".join(token).strip()
            token = []
            col += 1
            continue
        token.append(ch)
    if col in cols_set:
        out[col] = "".join(token).strip()
    return out


def _prime_cyclotomic_trace(token: str, *, p: int) -> int:
    """Compute Tr_{Q(zeta_p)/Q}(token) for a prime p cyclotomic expression.

    Supported token grammar (as produced by CTblLib for many prime-order columns):
      - integers (e.g. '0', '1', '-2')
      - sums of terms like 'E(p)', 'E(p)^k', 'c*E(p)^k' with integer c

    For prime p:
      Tr(1) = p-1
      Tr(zeta_p^k) = -1 for k not divisible by p
    """
    import re

    tok = str(token).strip()
    if tok == "0":
        return 0
    tok = tok.replace("\n", "").replace(" ", "")
    if not tok:
        raise ValueError("empty token")

    # Split into signed terms at top level.
    if tok[0] not in "+-":
        tok = "+" + tok

    term_re = re.compile(r"(?:(\d+)\*)?E\((\d+)\)\^?(\d+)?$")
    parts: list[tuple[int, str]] = []
    i = 0
    while i < len(tok):
        sign = 1
        if tok[i] == "+":
            sign = 1
        elif tok[i] == "-":
            sign = -1
        else:
            raise ValueError(f"unexpected sign at {i}: {tok[i]!r}")
        i += 1
        j = i
        while j < len(tok) and tok[j] not in "+-":
            j += 1
        parts.append((sign, tok[i:j]))
        i = j

    const = 0
    nonzero = 0
    for sign, body in parts:
        if not body:
            continue
        if re.fullmatch(r"\d+", body):
            const += sign * int(body)
            continue
        m = term_re.fullmatch(body)
        if not m:
            raise ValueError(f"cannot parse term {body!r} from {tok!r}")
        coeff = int(m.group(1) or "1")
        pp = int(m.group(2))
        exp = int(m.group(3) or "1")
        if pp != int(p):
            raise ValueError(f"unexpected E({pp}) in token for p={p}")
        if exp % p == 0:
            const += sign * coeff
        else:
            nonzero += sign * coeff

    # Trace: (p-1)*const + (-1)*nonzero
    return (p - 1) * const - nonzero


def build_monster_charcols_from_ctbllib(ctomonst_tbl: Path) -> dict[str, object]:
    txt = ctomonst_tbl.read_text(encoding="utf-8", errors="ignore")
    args = _parse_mot_args(txt, "M")

    centralizers = ast.literal_eval(args[1].replace("\n", " "))
    if not isinstance(centralizers, list) or len(centralizers) != 194:
        raise ValueError("unexpected centralizers list")

    pow_items = _split_top_level_list_items(args[2])
    # exponent p lives at index p-1 in the list (index 0 is the empty '1' slot)
    pm29 = ast.literal_eval(pow_items[28].replace("\n", " "))
    if not isinstance(pm29, list) or len(pm29) != 194:
        raise ValueError("unexpected powermap(29)")

    idx29_candidates = [
        i + 1 for i, (c, p) in enumerate(zip(centralizers, pm29)) if c == 87 and p == 1
    ]
    if idx29_candidates != [97]:
        raise ValueError(f"unexpected 29A candidates: {idx29_candidates}")
    idx29 = 97

    pm41 = ast.literal_eval(pow_items[40].replace("\n", " "))
    if not isinstance(pm41, list) or len(pm41) != 194:
        raise ValueError("unexpected powermap(41)")

    idx41_candidates = [
        i + 1 for i, (c, p) in enumerate(zip(centralizers, pm41)) if c == 41 and p == 1
    ]
    if idx41_candidates != [127]:
        raise ValueError(f"unexpected 41A candidates: {idx41_candidates}")
    idx41 = 127

    def _prime_class_candidates(*, centralizer: int, prime: int) -> list[int]:
        pm = ast.literal_eval(pow_items[prime - 1].replace("\n", " "))
        if not isinstance(pm, list) or len(pm) != 194:
            raise ValueError(f"unexpected powermap({prime})")
        return [
            i + 1
            for i, (c, pwr) in enumerate(zip(centralizers, pm))
            if int(c) == int(centralizer) and int(pwr) == 1
        ]

    idx31_candidates = _prime_class_candidates(centralizer=186, prime=31)
    if idx31_candidates != [105, 106]:
        raise ValueError(f"unexpected 31A candidates: {idx31_candidates}")
    idx31a, idx31b = idx31_candidates

    idx47_candidates = _prime_class_candidates(centralizer=94, prime=47)
    if idx47_candidates != [139, 140]:
        raise ValueError(f"unexpected 47A candidates: {idx47_candidates}")
    idx47a, idx47b = idx47_candidates

    idx59_candidates = _prime_class_candidates(centralizer=59, prime=59)
    if idx59_candidates != [152, 153]:
        raise ValueError(f"unexpected 59A candidates: {idx59_candidates}")
    idx59a, idx59b = idx59_candidates

    idx71_candidates = _prime_class_candidates(centralizer=71, prime=71)
    if idx71_candidates != [169, 170]:
        raise ValueError(f"unexpected 71A candidates: {idx71_candidates}")
    idx71a, idx71b = idx71_candidates

    idx5a = _prime_class_candidates(centralizer=1365154560000000, prime=5)
    if idx5a != [11]:
        raise ValueError(f"unexpected 5A candidates: {idx5a}")
    idx5a = idx5a[0]

    idx5b = _prime_class_candidates(centralizer=94500000000, prime=5)
    if idx5b != [12]:
        raise ValueError(f"unexpected 5B candidates: {idx5b}")
    idx5b = idx5b[0]

    idx7a = _prime_class_candidates(centralizer=28212710400, prime=7)
    if idx7a != [19]:
        raise ValueError(f"unexpected 7A candidates: {idx7a}")
    idx7a = idx7a[0]

    idx7b = _prime_class_candidates(centralizer=84707280, prime=7)
    if idx7b != [20]:
        raise ValueError(f"unexpected 7B candidates: {idx7b}")
    idx7b = idx7b[0]

    idx11a = _prime_class_candidates(centralizer=1045440, prime=11)
    if idx11a != [34]:
        raise ValueError(f"unexpected 11A candidates: {idx11a}")
    idx11a = idx11a[0]

    idx13a = _prime_class_candidates(centralizer=73008, prime=13)
    if idx13a != [45]:
        raise ValueError(f"unexpected 13A candidates: {idx13a}")
    idx13a = idx13a[0]

    idx13b = _prime_class_candidates(centralizer=52728, prime=13)
    if idx13b != [46]:
        raise ValueError(f"unexpected 13B candidates: {idx13b}")
    idx13b = idx13b[0]

    idx17a = _prime_class_candidates(centralizer=2856, prime=17)
    if idx17a != [57]:
        raise ValueError(f"unexpected 17A candidates: {idx17a}")
    idx17a = idx17a[0]

    idx19a = _prime_class_candidates(centralizer=1140, prime=19)
    if idx19a != [63]:
        raise ValueError(f"unexpected 19A candidates: {idx19a}")
    idx19a = idx19a[0]

    idx23_candidates = _prime_class_candidates(centralizer=552, prime=23)
    if idx23_candidates != [76, 77]:
        raise ValueError(f"unexpected 23A candidates: {idx23_candidates}")
    idx23a, idx23b = idx23_candidates

    rows = _split_top_level_list_items(args[3])
    if len(rows) != 194:
        raise ValueError(f"expected 194 irreps, got {len(rows)}")

    cols_needed = [
        1,
        2,
        3,
        4,
        5,
        6,
        idx29,
        idx41,
        idx31a,
        idx31b,
        idx47a,
        idx47b,
        idx59a,
        idx59b,
        idx71a,
        idx71b,
        idx5a,
        idx5b,
        idx7a,
        idx7b,
        idx11a,
        idx13a,
        idx13b,
        idx17a,
        idx19a,
        idx23a,
        idx23b,
    ]
    extracted = [_extract_cols(r, cols_needed) for r in rows]

    # Expand GALOIS rows: for these columns (orders 2,3,29), values are integers,
    # so the Galois action is trivial and we can copy the base row values.
    for i, d in enumerate(extracted, start=1):
        if "GALOIS" in d:
            base, _k = d["GALOIS"]
            extracted[i - 1] = extracted[base - 1].copy()

    irreps: list[dict[str, int]] = []
    for i, d in enumerate(extracted, start=1):
        irreps.append(
            {
                "index": i,
                "deg": int(d[1]),
                "2A": int(d[2]),
                "2B": int(d[3]),
                "3A": int(d[4]),
                "3B": int(d[5]),
                "3C": int(d[6]),
                "29A": int(d[idx29]),
                "41A": int(d[idx41]),
                "31A_trace": _prime_cyclotomic_trace(d[idx31a], p=31),
                "31B_trace": _prime_cyclotomic_trace(d[idx31b], p=31),
                "47A_trace": _prime_cyclotomic_trace(d[idx47a], p=47),
                "47B_trace": _prime_cyclotomic_trace(d[idx47b], p=47),
                "59A_trace": _prime_cyclotomic_trace(d[idx59a], p=59),
                "59B_trace": _prime_cyclotomic_trace(d[idx59b], p=59),
                "71A_trace": _prime_cyclotomic_trace(d[idx71a], p=71),
                "71B_trace": _prime_cyclotomic_trace(d[idx71b], p=71),
                "5A": int(d[idx5a]),
                "5B": int(d[idx5b]),
                "7A": int(d[idx7a]),
                "7B": int(d[idx7b]),
                "11A": int(d[idx11a]),
                "13A": int(d[idx13a]),
                "13B": int(d[idx13b]),
                "17A": int(d[idx17a]),
                "19A": int(d[idx19a]),
                "23A_trace": _prime_cyclotomic_trace(d[idx23a], p=23),
                "23B_trace": _prime_cyclotomic_trace(d[idx23b], p=23),
            }
        )

    return {
        "source": {
            "ctbllib_version": CTBLLIB_VERSION,
            "source_archive_url": CTBLLIB_URL,
            "table_file": "ctbllib-1.3.11/data/ctomonst.tbl",
            "table_id": "M",
        },
        "classes": {
            "1A": {"ctbllib_index": 1},
            "2A": {"ctbllib_index": 2},
            "2B": {"ctbllib_index": 3},
            "3A": {"ctbllib_index": 4},
            "3B": {"ctbllib_index": 5},
            "3C": {"ctbllib_index": 6},
            "5A": {"ctbllib_index": idx5a},
            "5B": {"ctbllib_index": idx5b},
            "7A": {"ctbllib_index": idx7a},
            "7B": {"ctbllib_index": idx7b},
            "11A": {"ctbllib_index": idx11a},
            "13A": {"ctbllib_index": idx13a},
            "13B": {"ctbllib_index": idx13b},
            "17A": {"ctbllib_index": idx17a},
            "19A": {"ctbllib_index": idx19a},
            "29A": {"ctbllib_index": idx29},
            "41A": {"ctbllib_index": idx41},
        },
        "trace_classes": {
            "23A": {"ctbllib_index": idx23a, "prime": 23},
            "23B": {"ctbllib_index": idx23b, "prime": 23},
            "31A": {"ctbllib_index": idx31a, "prime": 31},
            "31B": {"ctbllib_index": idx31b, "prime": 31},
            "47A": {"ctbllib_index": idx47a, "prime": 47},
            "47B": {"ctbllib_index": idx47b, "prime": 47},
            "59A": {"ctbllib_index": idx59a, "prime": 59},
            "59B": {"ctbllib_index": idx59b, "prime": 59},
            "71A": {"ctbllib_index": idx71a, "prime": 71},
            "71B": {"ctbllib_index": idx71b, "prime": 71},
        },
        "n_irreps": len(irreps),
        "irreps": irreps,
    }


def main() -> None:
    archive = (
        Path("outputs") / "ctbllib_cache" / f"gap-ctbllib_{CTBLLIB_VERSION}.tar.xz"
    )
    extracted_root = Path("outputs") / "ctbllib_cache"

    _download(CTBLLIB_URL, archive)
    member = f"ctbllib-{CTBLLIB_VERSION}/data/ctomonst.tbl"
    tbl_path = _extract_member(archive, member, extracted_root)

    payload = build_monster_charcols_from_ctbllib(tbl_path)
    out_path = Path("data") / "monster_ctbllib_charcols.json"
    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
