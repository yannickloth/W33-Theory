#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "usage: ./run_sage.sh <script-or-command> [args...]" >&2
  exit 2
fi

if ! command -v sage >/dev/null 2>&1; then
  echo "sage executable not found" >&2
  exit 127
fi

target="$1"
shift

if [[ "$target" == *.py ]]; then
  exec sage -python "$target" "$@"
fi

exec sage "$target" "$@"
