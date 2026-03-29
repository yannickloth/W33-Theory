#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path


BUNDLES = [
    Path("/mnt/c/Users/wiljd/.vscode/extensions/qiskit.qiskit-vscode-0.16.1/out/extension.js"),
    Path("/mnt/c/Users/wiljd/.vscode-insiders/extensions/qiskit.qiskit-vscode-0.16.1/out/extension.js"),
]


def replace_once(text: str, old: str, new: str, label: str, skip: tuple[str, ...] = ()) -> tuple[str, bool]:
    if new in text or any(marker in text for marker in skip):
        return text, False
    if old not in text:
        raise RuntimeError(f"missing block for {label}")
    return text.replace(old, new, 1), True


def patch_bundle(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    changed = False

    text, did = replace_once(
        text,
        """        if (AUTH_ERROR_CODES.includes(response.status)) {\n          msg = `API Token is not authorized or is incorrect: ${msg}`;\n          if (response.status === 403 && msg.toLowerCase().includes("disclaimer")) {\n            msg = DISCLAIMER_ERROR_MSG;\n          }\n        }\n""",
        """        if (AUTH_ERROR_CODES.includes(response.status)) {\n          const serviceUrl = `${vscode2.workspace.getConfiguration("qiskitCodeAssistant").get("url") || ""}`.toLowerCase();\n          if (serviceUrl.includes("qiskit-code-assistant.quantum.ibm.com")) {\n            msg = `API Token is not authorized or is incorrect: ${msg}`;\n            if (response.status === 403 && msg.toLowerCase().includes("disclaimer")) {\n              msg = DISCLAIMER_ERROR_MSG;\n            }\n          } else {\n            msg = `Authorization failed: ${msg}`;\n          }\n        }\n""",
        "auth wording",
        skip=("Authorization failed:",),
    )
    changed = changed or did

    text, did = replace_once(
        text,
        """  initializationPromise = (async () => {\n    try {\n      const response = await ServiceAPI.runFetch("/", { "method": "GET" });\n""",
        """  initializationPromise = (async () => {\n    try {\n      const normalizedServiceUrl = `${currentServiceUrl || ""}`.toLowerCase();\n      if (normalizedServiceUrl && !normalizedServiceUrl.includes("qiskit-code-assistant.quantum.ibm.com")) {\n        activeService = new OpenAIService();\n        await activeService.checkForToken();\n        lastServiceUrl = currentServiceUrl;\n        return activeService;\n      }\n      const response = await ServiceAPI.runFetch("/", { "method": "GET" });\n""",
        "service selection",
        skip=("normalizedServiceUrl", "localCompatibleService"),
    )
    changed = changed or did

    text, did = replace_once(
        text,
        """async function promptCredentialSelectionIfNeeded(context) {\n  try {\n    const neverPrompt = context.globalState.get(STATE_KEY_NEVER_PROMPT, false);\n""",
        """async function promptCredentialSelectionIfNeeded(context) {\n  try {\n    const serviceUrl = `${vscode3.workspace.getConfiguration(CONFIG_SECTION).get("url") || ""}`.toLowerCase();\n    if (serviceUrl && !serviceUrl.includes("qiskit-code-assistant.quantum.ibm.com")) {\n      return false;\n    }\n    const neverPrompt = context.globalState.get(STATE_KEY_NEVER_PROMPT, false);\n""",
        "credential prompt",
        skip=('const config2 = vscode3.workspace.getConfiguration(CONFIG_SECTION);',),
    )
    changed = changed or did

    text, did = replace_once(
        text,
        """async function requiresToken() {\n  const context = getExtensionContext();\n""",
        """async function requiresToken() {\n  const serviceUrl = `${vscode4.workspace.getConfiguration("qiskitCodeAssistant").get("url") || ""}`.toLowerCase();\n  if (serviceUrl && !serviceUrl.includes("qiskit-code-assistant.quantum.ibm.com")) {\n    vscode4.commands.executeCommand("setContext", "qiskit-vscode.api-token-set", false);\n    return;\n  }\n  const context = getExtensionContext();\n""",
        "requires token",
        skip=("vscode4.workspace.getConfiguration(\"qiskitCodeAssistant\")",),
    )
    changed = changed or did

    text, did = replace_once(
        text,
        """  await initApiToken(context);\n  const credentialWasSelected = await promptCredentialSelectionIfNeeded(context);\n  if (!credentialWasSelected) {\n    await initModels(context);\n  }\n""",
        """  const serviceUrl = `${vscode24.workspace.getConfiguration("qiskitCodeAssistant").get("url") || ""}`.toLowerCase();\n  const useIBMCloudService = serviceUrl.includes("qiskit-code-assistant.quantum.ibm.com");\n  let credentialWasSelected = false;\n  if (useIBMCloudService) {\n    await initApiToken(context);\n    credentialWasSelected = await promptCredentialSelectionIfNeeded(context);\n  }\n  if (!credentialWasSelected) {\n    await initModels(context);\n  }\n""",
        "background init",
        skip=("useIBMCloudService",),
    )
    changed = changed or did

    if changed:
        backup = path.with_suffix(path.suffix + ".local-mode.bak")
        if not backup.exists():
            shutil.copy2(path, backup)
        path.write_text(text, encoding="utf-8")
    return changed


def main() -> int:
    bundles = [p for p in BUNDLES if p.exists()]
    if not bundles:
        print("No installed Qiskit extension bundles found.", file=sys.stderr)
        return 1

    exit_code = 0
    for bundle in bundles:
        try:
            changed = patch_bundle(bundle)
            print(f"{'patched' if changed else 'already-patched'}: {bundle}")
        except Exception as exc:
            exit_code = 1
            print(f"failed: {bundle}: {exc}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
