const vscode = require('vscode');

/**
 * Minimal helper: copy selection to clipboard and open ChatGPT web.
 */
function activate(context) {
  let disposable = vscode.commands.registerCommand('sendToChatGPT.sendSelection', async function () {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showWarningMessage('No active editor found. Open a file and select text to send.');
      return;
    }

    let text = editor.document.getText(editor.selection);
    if (!text || text.trim() === '') {
      const choice = await vscode.window.showWarningMessage('Selection is empty — use entire file?', 'Yes', 'No');
      if (choice !== 'Yes') {
        return;
      }
      text = editor.document.getText();
    }

    try {
      await vscode.env.clipboard.writeText(text);
    } catch (err) {
      vscode.window.showErrorMessage('Failed to write to clipboard: ' + String(err));
      return;
    }

    // Open ChatGPT web (new chat) in default browser
    await vscode.env.openExternal(vscode.Uri.parse('https://chat.openai.com/chat'));

    vscode.window.showInformationMessage('Copied selection to clipboard and opened ChatGPT web. Paste into the chat input (Ctrl+V), select GPT‑5.2, and send to save in your ChatGPT history.');
  });

  context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = { activate, deactivate };
