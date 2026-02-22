Quick guide: use ChatGPT 5.2 with VS Code on Windows
===================================================

Short answer
------------
There is no official way on Windows right now to have VS Code chat messages automatically saved to your ChatGPT account memory. The macOS "Work‑with‑Apps" integration is the only supported path that writes IDE interactions to your ChatGPT history. On Windows the safest and most reliable approach is to use the ChatGPT web app (GPT‑5.2) and paste selected code or upload files there; those chats are saved to your account.

Two practical helpers included in this repo
-----------------------------------------
1. Lightweight VS Code extension: `tools/send-to-chatgpt-vscode`
   - Command: **Send Selection to ChatGPT (Web)** (`Ctrl+Alt+G` by default)
   - Copies selection (or whole file if you choose) to the clipboard and opens `https://chat.openai.com/chat` for you to paste & send.
   - This does not send anything automatically — you control what is sent to the web UI (best for security & explicit consent).

2. PowerShell fallback script: `scripts/send_to_chatgpt.ps1`
   - Usage: `Get-Content file.py | .\scripts\send_to_chatgpt.ps1 -Open` or `.\scripts\send_to_chatgpt.ps1 "Explain this" -Open`
   - Copies input to the clipboard and optionally opens ChatGPT web.

Why this approach
------------------
- Official Work‑with‑Apps (which saves IDE interactions into your ChatGPT history) is macOS‑only currently.
- Full browser automation (scripts that log into chat.openai.com and post messages for you) is possible but brittle and has security risks (handling your credentials/2FA). If you want that, tell me and I can prepare an explicit opt‑in Playwright automation script with security caveats.

How to get started
------------------
- If you want a quick demo: open `tools/send-to-chatgpt-vscode` in VS Code and press `F5` to start an Extension Development Host. Select some code, press `Ctrl+Alt+G`, then paste into ChatGPT web and send using GPT‑5.2.
- If you prefer automation, ask and I’ll prepare a Playwright script and a careful security checklist.

Safety note
-----------
- Anything you paste/send to chat.openai.com becomes part of your chat history. If your account/memory settings are enabled, it will be stored and may influence future responses. Avoid sending secrets (API keys, private data) unless you are sure it's safe to do so.
