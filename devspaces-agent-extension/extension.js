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

  // Create output channel
  const out = vscode.window.createOutputChannel('Agent Deploy');
  out.clear();
  out.show(true);

  try {
    // Step 1: Show cluster overview
    out.appendLine('🔍 STEP 1: Fetching Cluster Information...\n');
    
    const overviewRes = await fetch(`${route}/agent/cluster-overview`);
    const overviewJson = await overviewRes.json().catch(() => ({}));
    
    if (overviewJson.success && overviewJson.overview) {
      out.appendLine(overviewJson.overview);
      out.appendLine('\n');
    } else {
      out.appendLine('⚠️  Could not fetch cluster overview\n');
    }

    // Step 2: Get deployment parameters
    out.appendLine('📝 STEP 2: Deployment Configuration\n');
    
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

    // Step 3: Node selection
    out.appendLine('\n🎯 STEP 3: Node Selection\n');
    
    const useNodeSelector = await vscode.window.showQuickPick(
      ['Yes - Deploy to specific node', 'No - Use default scheduling'],
      {
        title: 'Node Selection',
        placeHolder: 'Do you want to deploy to a specific node?'
      }
    );

    let nodeLabelKey = null;
    let nodeLabelValue = null;

    if (useNodeSelector && useNodeSelector.startsWith('Yes')) {
      nodeLabelKey = await vscode.window.showInputBox({
        title: 'Node Label Key',
        prompt: 'Enter the label key for node selection',
        value: 'deployment',
        placeHolder: 'e.g., deployment, workload-type, app-tier'
      });

      if (!nodeLabelKey) {
        out.appendLine('⚠️  No label key provided. Using default scheduling.\n');
      } else {
        nodeLabelValue = await vscode.window.showInputBox({
          title: 'Node Label Value',
          prompt: `Enter the value for label "${nodeLabelKey}"`,
          value: appName,
          placeHolder: 'e.g., telco-app, backend, frontend'
        });

        if (!nodeLabelValue) {
          out.appendLine('⚠️  No label value provided. Using default scheduling.\n');
          nodeLabelKey = null;
        } else {
          out.appendLine(`✅ Will deploy to nodes with label: ${nodeLabelKey}=${nodeLabelValue}\n`);
          
          // Check if label exists
          const checkRes = await fetch(
            `${route}/agent/nodes/check-label?label_key=${nodeLabelKey}&label_value=${nodeLabelValue}`
          );
          const checkJson = await checkRes.json().catch(() => ({}));
          
          if (checkJson.exists) {
            out.appendLine(`✅ Found ${checkJson.count} node(s) with this label`);
            out.appendLine(`   Nodes: ${checkJson.nodes.join(', ')}\n`);
          } else {
            out.appendLine(`ℹ️  Label not found. Agent will automatically:`);
            out.appendLine(`   1. Find node with least workload`);
            out.appendLine(`   2. Label that node with ${nodeLabelKey}=${nodeLabelValue}`);
            out.appendLine(`   3. Deploy to the labeled node\n`);
          }
        }
      }
    } else {
      out.appendLine('ℹ️  Using default Kubernetes scheduling\n');
    }

    // Show summary
    out.appendLine('=' * 80);
    out.appendLine('📋 DEPLOYMENT SUMMARY');
    out.appendLine('=' * 80);
    out.appendLine(`Application: ${description}`);
    out.appendLine(`Name: ${appName}`);
    out.appendLine(`Namespace: ${namespace}`);
    if (nodeLabelKey && nodeLabelValue) {
      out.appendLine(`Node Selector: ${nodeLabelKey}=${nodeLabelValue}`);
    } else {
      out.appendLine(`Node Selector: None (default scheduling)`);
    }
    out.appendLine('=' * 80 + '\n');

    // Step 4: Deploy
    out.appendLine('🚀 STEP 4: Starting Deployment...\n');
    
    const deployBody = {
      description,
      app_name: appName,
      namespace
    };

    if (nodeLabelKey && nodeLabelValue) {
      deployBody.node_label_key = nodeLabelKey;
      deployBody.node_label_value = nodeLabelValue;
    }

    const res = await fetch(`${route}/agent/deploy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(deployBody)
    });

    const json = await res.json().catch(() => ({}));

    if (json.success) {
      // Show cluster overview if available
      if (json.cluster_overview) {
        out.appendLine('\n' + json.cluster_overview + '\n');
      }

      // Show node selection info
      if (json.node_selection) {
        out.appendLine('\n' + '=' * 80);
        out.appendLine('🎯 NODE SELECTION RESULTS');
        out.appendLine('=' * 80);
        
        const ns = json.node_selection;
        if (ns.requested) {
          if (ns.status === 'Label exists') {
            out.appendLine(`✅ Deployed to existing labeled nodes:`);
            out.appendLine(`   Label: ${JSON.stringify(ns.label)}`);
            out.appendLine(`   Nodes: ${ns.nodes.join(', ')}`);
          } else if (ns.status === 'Label created') {
            out.appendLine(`✅ Automatically labeled node for deployment:`);
            out.appendLine(`   Label: ${JSON.stringify(ns.label)}`);
            out.appendLine(`   Node: ${ns.nodes[0]}`);
            out.appendLine(`   Previous pod count: ${ns.pod_count}`);
          } else {
            out.appendLine(`⚠️  ${ns.status}`);
            if (ns.error) {
              out.appendLine(`   Error: ${ns.error}`);
            }
          }
        } else {
          out.appendLine(`ℹ️  Default scheduling used (no node selector)`);
        }
        out.appendLine('=' * 80 + '\n');
      }

      // Show deployment result
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

      if (nodeLabelKey && nodeLabelValue) {
        out.appendLine(`\n🏷️  Check node labels:`);
        out.appendLine(`   oc get nodes -l ${nodeLabelKey}=${nodeLabelValue}`);
      }

    } else {
      out.appendLine('\n❌ DEPLOYMENT FAILED\n');
      out.appendLine(json.error || json.deployment_result || 'Unknown error');
      
      vscode.window.showErrorMessage(`Deployment failed: ${json.error || 'Unknown error'}`);
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