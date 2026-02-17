"""Fetch CTblLib and export minimal Monster character columns to JSON.

This script downloads a pinned CTblLib source archive (used by GAP's CTblLib
package), extracts the Monster ordinary character table `M` from
`ctomonst.tbl`, and exports a small subset of integer columns needed for
offline, deterministic tests and analyses:

  - 1A (degree)
  - 2A
  - 3B
  - 29A
  - 41A
  - 31A (trace only)
  - 47A (trace only)
  - 59A (trace only)
  - 71A (trace only)

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
    idx31 = idx31_candidates[0]

    idx47_candidates = _prime_class_candidates(centralizer=94, prime=47)
    if idx47_candidates != [139, 140]:
        raise ValueError(f"unexpected 47A candidates: {idx47_candidates}")
    idx47 = idx47_candidates[0]

    idx59_candidates = _prime_class_candidates(centralizer=59, prime=59)
    if idx59_candidates != [152, 153]:
        raise ValueError(f"unexpected 59A candidates: {idx59_candidates}")
    idx59 = idx59_candidates[0]

    idx71_candidates = _prime_class_candidates(centralizer=71, prime=71)
    if idx71_candidates != [169, 170]:
        raise ValueError(f"unexpected 71A candidates: {idx71_candidates}")
    idx71 = idx71_candidates[0]

    rows = _split_top_level_list_items(args[3])
    if len(rows) != 194:
        raise ValueError(f"expected 194 irreps, got {len(rows)}")

    cols_needed = [1, 2, 5, idx29, idx41, idx31, idx47, idx59, idx71]
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
                "3B": int(d[5]),
                "29A": int(d[idx29]),
                "41A": int(d[idx41]),
                "31A_trace": _prime_cyclotomic_trace(d[idx31], p=31),
                "47A_trace": _prime_cyclotomic_trace(d[idx47], p=47),
                "59A_trace": _prime_cyclotomic_trace(d[idx59], p=59),
                "71A_trace": _prime_cyclotomic_trace(d[idx71], p=71),
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
            "3B": {"ctbllib_index": 5},
            "29A": {"ctbllib_index": idx29},
            "41A": {"ctbllib_index": idx41},
        },
        "trace_classes": {
            "31A": {"ctbllib_index": idx31, "prime": 31},
            "47A": {"ctbllib_index": idx47, "prime": 47},
            "59A": {"ctbllib_index": idx59, "prime": 59},
            "71A": {"ctbllib_index": idx71, "prime": 71},
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
