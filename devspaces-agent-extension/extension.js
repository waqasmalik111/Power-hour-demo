const vscode = require('vscode');
const fetch = require('node-fetch');

function getConfig() {
  const cfg = vscode.workspace.getConfiguration('agent');
  const routeCfg = (cfg.get('route') || '').trim();
  const routeEnv = (process.env.AGENT_ROUTE || '').trim();
  const route = (routeCfg || routeEnv).replace(/\/+$/, '');
  const defaultLanguage = cfg.get('defaultLanguage') || 'python';
  if (!route) {
    vscode.window.showErrorMessage('Agent route is not set. Configure “agent.route” in Settings or set env AGENT_ROUTE.');
  }
  return { route, defaultLanguage };
}

async function validateSelection() {
  const { route, defaultLanguage } = getConfig();
  if (!route) return;

  const editor = vscode.window.activeTextEditor;
  if (!editor) return vscode.window.showWarningMessage('No active editor.');
  const sel = editor.selection;
  const code = editor.document.getText(sel);
  if (!code || !code.trim()) return vscode.window.showWarningMessage('Select some code first.');

  const body = { query: { mode: 'validate', language: defaultLanguage, code } };
  const out = vscode.window.createOutputChannel('Agent Validation'); out.clear(); out.show(true); out.appendLine('Validating…\n');

  try {
    const res = await fetch(`${route}/agent/validate`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    });
    const json = await res.json().catch(() => ({}));
    out.appendLine((json.answer || json.error || 'No answer').toString());
  } catch (e) {
    out.appendLine(`Request failed: ${e.message}`);
  }
}

async function generateCode() {
  const { route, defaultLanguage } = getConfig();
  if (!route) return;

  const prompt = await vscode.window.showInputBox({
    title: 'Code Generation Prompt',
    prompt: 'Describe the code to generate',
    value: 'Create a function to add two numbers with a docstring and unit test'
  });
  if (!prompt) return;

  const out = vscode.window.createOutputChannel('Agent Generate'); out.clear(); out.show(true); out.appendLine('Generating…\n');

  try {
    const res = await fetch(`${route}/agent/execute`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: prompt })
    });
    const json = await res.json().catch(() => ({}));
    const answer = (json.answer || json.error || '').toString();
    if (!answer) return out.appendLine('No answer returned.');

    // Insert at cursor or open a new doc
    const editor = vscode.window.activeTextEditor;
    if (editor) {
      await editor.edit(b => b.insert(editor.selection.active, answer + '\n'));
    } else {
      const doc = await vscode.workspace.openTextDocument({ content: answer, language: defaultLanguage });
      await vscode.window.showTextDocument(doc, { preview: false });
    }
    out.appendLine('Done.');
  } catch (e) {
    out.appendLine(`Request failed: ${e.message}`);
  }
}

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand('agent.validateSelection', validateSelection),
    vscode.commands.registerCommand('agent.generateCode', generateCode)
  );
}
function deactivate() {}
module.exports = { activate, deactivate };
