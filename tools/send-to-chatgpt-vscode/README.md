Send to ChatGPT (Web) — VS Code helper
======================================

What this does
--------------
- Copies the editor selection (or the whole file if you choose) to your OS clipboard and opens https://chat.openai.com/chat in your default browser.
- It does NOT send text to OpenAI by itself — you paste and send the message manually in the web UI so it becomes part of your ChatGPT history (and memory, if your plan supports that).

Why useful
----------
- On Windows there is no official "Work with Apps" integration that syncs VS Code messages to ChatGPT history. This helper speeds the manual workflow: select -> press key -> paste & send in ChatGPT web.

How to try it (development host)
--------------------------------
1. In VS Code open this folder: `tools/send-to-chatgpt-vscode`.
2. Press `F5` to launch an Extension Development Host with the command available.
3. In the host window open a code file, select some text and run the command `Send Selection to ChatGPT (Web)` (or press `Ctrl+Alt+G`).

How to install for daily use
----------------------------
- Option A (fast dev): Keep the extension folder and use `F5` when you need it.
- Option B (stable): Package and install a VSIX: `npm i -g vsce` then `vsce package` inside this folder; then in VS Code: `Extensions: Install from VSIX...`.

Notes & security
----------------
- This only copies text to your clipboard and opens ChatGPT in your browser; nothing leaves your machine until you paste and send to chat.openai.com.
- Use GPT‑5.2 in the ChatGPT web app (Plus/Pro/Business/Enterprise) to have the conversation saved in your ChatGPT account and memory.
