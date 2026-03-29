#!/usr/bin/env python3
"""Call the local Qiskit-tuned Ollama model from WSL via curl.exe.

This is the practical path for using the same local model that backs the VS
Code Qiskit Code Assistant, but without relying on the editor UI.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


DEFAULT_URL = "http://localhost:11434"
DEFAULT_TIMEOUT = 180


def run_curl(args: list[str], payload: bytes | None = None, timeout: int = DEFAULT_TIMEOUT) -> Any:
    cmd = ["curl.exe", "-sS", "-m", str(timeout), *args]
    result = subprocess.run(
        cmd,
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(stderr or f"curl.exe failed with exit code {result.returncode}")
    body = result.stdout.decode("utf-8", errors="replace")
    return json.loads(body)


def list_model_ids(url: str) -> list[str]:
    payload = run_curl([f"{url}/v1/models"])
    return [entry["id"] for entry in payload.get("data", [])]


def choose_model(url: str, requested: str | None) -> str:
    if requested:
        return requested
    model_ids = list_model_ids(url)
    if not model_ids:
        raise RuntimeError("No models available from local Ollama /v1/models")
    if len(model_ids) == 1:
        return model_ids[0]

    preferred = [model_id for model_id in model_ids if "qiskit" in model_id.lower()]
    if len(preferred) == 1:
        return preferred[0]

    raise RuntimeError(
        "Could not auto-select a model. Available models: "
        + ", ".join(model_ids)
        + ". Pass --model explicitly."
    )


def complete(url: str, model: str, prompt: str, max_tokens: int, temperature: float, timeout: int) -> dict[str, Any]:
    request = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    return run_curl(
        [
            "-X",
            "POST",
            f"{url}/v1/completions",
            "-H",
            "Content-Type: application/json",
            "--data-binary",
            "@-",
        ],
        payload=json.dumps(request).encode("utf-8"),
        timeout=timeout,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Call the local Qiskit-tuned Ollama model through /v1/completions.")
    parser.add_argument("--prompt", default=None, help="Prompt to send to the model")
    parser.add_argument("--model", default=None, help="Explicit model id; auto-detects if omitted")
    parser.add_argument("--url", default=DEFAULT_URL, help="OpenAI-compatible endpoint base URL")
    parser.add_argument("--max-tokens", type=int, default=256, help="Maximum completion tokens")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="curl timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Print the full JSON response")
    parser.add_argument("--list-models", action="store_true", help="List models from /v1/models and exit")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.list_models:
        print(json.dumps({"models": list_model_ids(args.url)}, indent=2))
        return
    if not args.prompt:
        raise RuntimeError("Provide --prompt, or use --list-models.")
    model = choose_model(args.url, args.model)
    response = complete(args.url, model, args.prompt, args.max_tokens, args.temperature, args.timeout)

    if args.json:
        print(json.dumps({"selected_model": model, "response": response}, indent=2))
        return

    choices = response.get("choices", [])
    text = choices[0].get("text", "") if choices else ""
    print(text.rstrip())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        sys.exit(1)
