const vscode = require('vscode');
const fetch = require('node-fetch');

function getConfig() {
  const cfg = vscode.workspace.getConfiguration('agent');
  const routeCfg = (cfg.get('route') || '').trim();
  const routeEnv = (process.env.AGENT_ROUTE || '').trim();
  const route = (routeCfg || routeEnv).replace(/\/+$/, '');
  const defaultLanguage = cfg.get('defaultLanguage') || 'python';
  if (!route) {
    vscode.window.showErrorMessage('Agent route is not set. Configure "agent.route" in Settings or set env AGENT_ROUTE.');
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

  const body = { code, language: defaultLanguage };
  const out = vscode.window.createOutputChannel('Agent Validation'); out.clear(); out.show(true); out.appendLine('Validating…\n');

  try {
    const res = await fetch(`${route}/agent/validate`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    });
    const json = await res.json().catch(() => ({}));
    out.appendLine((json.report || json.error || 'No answer').toString());
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

async function deployToOpenShift() {
  const { route } = getConfig();
  if (!route) return;

  // Get deployment parameters
  const description = await vscode.window.showInputBox({
    title: 'Application Description',
    prompt: 'Describe the telco application to deploy',
    value: 'real-time messaging application with web UI',
    placeHolder: 'e.g., SMS gateway with rate limiting, customer support ticketing system'
  });
  if (!description) return;

  const appName = await vscode.window.showInputBox({
    title: 'Application Name',
    prompt: 'Enter application name (lowercase, no spaces)',
    value: 'telco-app',
    placeHolder: 'e.g., telco-sms, support-tickets'
  });
  if (!appName) return;

  const namespace = await vscode.window.showInputBox({
    title: 'OpenShift Namespace',
    prompt: 'Enter target namespace',
    value: 'telco-demo',
    placeHolder: 'e.g., telco-demo, production'
  });
  if (!namespace) return;

  // Show progress
  const out = vscode.window.createOutputChannel('Agent Deploy');
  out.clear();
  out.show(true);
  out.appendLine('🚀 Deploying to OpenShift...\n');
  out.appendLine(`Description: ${description}`);
  out.appendLine(`App Name: ${appName}`);
  out.appendLine(`Namespace: ${namespace}\n`);
  out.appendLine('Generating code and deploying...\n');

  try {
    const res = await fetch(`${route}/agent/deploy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description, app_name: appName, namespace })
    });

    const json = await res.json().catch(() => ({}));

    if (json.success) {
      out.appendLine('✅ DEPLOYMENT SUCCESSFUL!\n');
      out.appendLine(json.deployment_result || '');
      
      // Get route URL
      const statusRes = await fetch(`${route}/agent/deployment-status/${appName}?namespace=${namespace}`);
      const statusJson = await statusRes.json().catch(() => ({}));
      
      if (statusJson.url) {
        out.appendLine(`\n🌐 Application URL: ${statusJson.url}`);
        
        // Ask if user wants to open in browser
        const openInBrowser = await vscode.window.showInformationMessage(
          `Deployment successful! Open ${appName}?`,
          'Open in Browser',
          'Copy URL',
          'Close'
        );
        
        if (openInBrowser === 'Open in Browser') {
          vscode.env.openExternal(vscode.Uri.parse(statusJson.url));
        } else if (openInBrowser === 'Copy URL') {
          vscode.env.clipboard.writeText(statusJson.url);
          vscode.window.showInformationMessage('URL copied to clipboard!');
        }
      }
      
      out.appendLine('\n📦 Check deployment status:');
      out.appendLine(`   oc get pods -n ${namespace}`);
      out.appendLine(`   oc logs -f deployment/${appName} -n ${namespace}`);
      
    } else {
      out.appendLine('❌ DEPLOYMENT FAILED\n');
      out.appendLine(json.error || json.deployment_result || 'Unknown error');
    }
  } catch (e) {
    out.appendLine(`\n❌ Request failed: ${e.message}`);
    vscode.window.showErrorMessage(`Deployment failed: ${e.message}`);
  }
}

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand('agent.validateSelection', validateSelection),
    vscode.commands.registerCommand('agent.generateCode', generateCode),
    vscode.commands.registerCommand('agent.deployToOpenShift', deployToOpenShift)
  );
}

function deactivate() {}
module.exports = { activate, deactivate };