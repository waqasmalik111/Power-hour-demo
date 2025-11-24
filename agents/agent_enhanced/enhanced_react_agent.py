"""
Enhanced wrapper around your existing ReActAgent
Adds cluster awareness, node selection, and intelligent deployment
"""
import sys
import os

# Add parent directory to path to import react_agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from react_agent import ReActAgent, CodeGenTool, CodeValidateTool
from openshift_tools import (
    OpenShiftClusterTool, 
    OpenShiftLogsTool, 
    OpenShiftNodeTool,
    OpenShiftClusterInfoTool,
    check_openshift_login, 
    get_current_namespace
)
from deployment_tool import OpenShiftDeploymentTool


class EnhancedReActAgent(ReActAgent):
    """Enhanced agent with cluster awareness, node selection, and intelligent deployment"""
    
    def __init__(self, tools=None, **kwargs):
        # Add new tools to existing ones
        if tools is None:
            tools = [
                CodeGenTool(),
                CodeValidateTool(),
                OpenShiftClusterTool(),
                OpenShiftLogsTool(),
                OpenShiftDeploymentTool(),
            ]
        
        super().__init__(tools, **kwargs)
        self.cluster_context = {}
        self.node_tool = OpenShiftNodeTool()
        self.cluster_info_tool = OpenShiftClusterInfoTool()
    
    def run(self, query):
        """Enhanced run with cluster context"""
        # Gather cluster context
        self.cluster_context = self._gather_cluster_context()
        
        # Call original run
        result = super().run(query)
        
        # Add cluster context to result
        result["cluster_context"] = self.cluster_context
        
        return result
    
    def _gather_cluster_context(self):
        """Gather cluster information"""
        context = {}
        try:
            if not check_openshift_login():
                context["logged_in"] = False
                return context
            
            namespace = get_current_namespace()
            context["namespace"] = namespace
            context["logged_in"] = True
            
            # Get pod count
            oc_tool = OpenShiftClusterTool()
            pods = oc_tool.execute("pods", namespace=namespace, output_format="json")
            try:
                import json
                data = json.loads(pods)
                context["pods_count"] = len(data.get("items", []))
            except:
                context["pods_count"] = 0
        except Exception as e:
            context["error"] = str(e)
        
        return context
    
    def get_cluster_overview(self, namespace: str = "") -> str:
        """Get and format comprehensive cluster overview"""
        try:
            overview = self.cluster_info_tool.get_cluster_overview(namespace)
            return self.cluster_info_tool.format_cluster_overview(overview)
        except Exception as e:
            return f"Error getting cluster overview: {str(e)}"
    
    def prepare_node_for_deployment(self, label_key: str = "deployment", 
                                   label_value: str = "telco-app") -> dict:
        """
        Find node with least workload and label it for deployment
        
        Returns:
            dict with:
                - success: bool
                - node_name: str
                - label: dict
                - message: str
        """
        try:
            # Find node with least workload
            target_node = self.node_tool.find_node_with_least_workload(exclude_masters=True)
            
            if not target_node:
                return {
                    "success": False,
                    "message": "No suitable worker nodes found in cluster"
                }
            
            # Label the node
            success, message = self.node_tool.label_node(
                target_node["name"], 
                label_key, 
                label_value
            )
            
            if success:
                return {
                    "success": True,
                    "node_name": target_node["name"],
                    "label": {label_key: label_value},
                    "pod_count": target_node["pod_count"],
                    "message": f"Node {target_node['name']} labeled successfully (current pods: {target_node['pod_count']})"
                }
            else:
                return {
                    "success": False,
                    "message": message
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error preparing node: {str(e)}"
            }
    
    def check_node_label_exists(self, label_key: str, label_value: str = None) -> dict:
        """
        Check if nodes with specified label exist
        
        Returns:
            dict with:
                - exists: bool
                - nodes: list of node names
                - count: int
        """
        try:
            nodes = self.node_tool.get_nodes_with_label(label_key, label_value)
            return {
                "exists": len(nodes) > 0,
                "nodes": nodes,
                "count": len(nodes)
            }
        except Exception as e:
            return {
                "exists": False,
                "nodes": [],
                "count": 0,
                "error": str(e)
            }
    
    def deploy_telco_app(self, 
                        description: str, 
                        app_name: str = "telco-app",
                        namespace: str = "telco-demo",
                        node_label_key: str = None,
                        node_label_value: str = None) -> dict:
        """
        Complete workflow: Display Cluster Info → Generate Code → Validate → Deploy with Node Selection
        
        Args:
            description: Description of the telco app to build
            app_name: Name of the application
            namespace: Target namespace
            node_label_key: Node label key for deployment (e.g., "deployment")
            node_label_value: Node label value for deployment (e.g., "telco-app")
        """
        result = {
            "success": False,
            "cluster_overview": "",
            "node_selection": {},
            "generated_code": "",
            "deployment_result": "",
            "app_name": app_name,
            "namespace": namespace
        }
        
        try:
            # Step 1: Display cluster overview
            print("\n" + "="*80)
            print("STEP 1: Gathering Cluster Information")
            print("="*80)
            
            cluster_overview = self.get_cluster_overview(namespace)
            result["cluster_overview"] = cluster_overview
            print(cluster_overview)
            
            # Step 2: Handle node selection
            print("\n" + "="*80)
            print("STEP 2: Node Selection for Deployment")
            print("="*80)
            
            node_selector = None
            
            if node_label_key and node_label_value:
                # Check if label exists
                label_check = self.check_node_label_exists(node_label_key, node_label_value)
                
                if label_check["exists"]:
                    print(f"✅ Found {label_check['count']} node(s) with label {node_label_key}={node_label_value}")
                    print(f"   Nodes: {', '.join(label_check['nodes'])}")
                    node_selector = {node_label_key: node_label_value}
                    result["node_selection"] = {
                        "requested": True,
                        "label": node_selector,
                        "nodes": label_check['nodes'],
                        "status": "Label exists"
                    }
                else:
                    print(f"⚠️  Label {node_label_key}={node_label_value} not found on any nodes")
                    print(f"🔍 Creating label on node with least workload...")
                    
                    # Auto-label a node
                    prep_result = self.prepare_node_for_deployment(node_label_key, node_label_value)
                    
                    if prep_result["success"]:
                        print(f"✅ {prep_result['message']}")
                        node_selector = prep_result["label"]
                        result["node_selection"] = {
                            "requested": True,
                            "label": node_selector,
                            "nodes": [prep_result["node_name"]],
                            "status": "Label created",
                            "pod_count": prep_result["pod_count"]
                        }
                    else:
                        print(f"❌ {prep_result['message']}")
                        print(f"⚠️  Deployment will proceed without node selector")
                        result["node_selection"] = {
                            "requested": True,
                            "label": {node_label_key: node_label_value},
                            "status": "Failed to create label",
                            "error": prep_result["message"]
                        }
            else:
                print("ℹ️  No node selector specified. Deployment will use default scheduling.")
                result["node_selection"] = {
                    "requested": False,
                    "status": "No node selector"
                }
            
            # Step 3: Generate code
            print("\n" + "="*80)
            print("STEP 3: Generating Application Code")
            print("="*80)
            
            gen_prompt = f"""Generate production Python code for Flask telco {description}.

Requirements:
- Single file with Flask + Flask-SocketIO
- REST endpoints: /send (POST), /messages (GET), /health (GET)
- Embedded HTML/CSS/JS in Python string
- Real-time messaging with WebSocket
- Listen on 0.0.0.0:8080

Critical rules:
- Output ONLY valid Python code, no markdown
- Use: socketio.run(app, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
- Jinja2 syntax: use consistent variable names (e.g., msg not message)
- Match all template variables to render_template_string context

Example pattern:
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
messages = []
HTML = '''<!DOCTYPE html><html><body>
<div>{{% for msg in messages %}}<p>{{{{msg.sender}}}}: {{{{msg.content}}}}</p>{{% endfor %}}</div>
<form id="form"><input id="sender" placeholder="Name"><input id="msg" placeholder="Message"><button>Send</button></form>
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script>
const socket = io();
socket.on('new_message', (data) => {{
  const div = document.querySelector('div');
  div.innerHTML += '<p>' + data.sender + ': ' + data.content + '</p>';
}});
document.getElementById('form').onsubmit = (e) => {{
  e.preventDefault();
  fetch('/send', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{
      sender: document.getElementById('sender').value,
      content: document.getElementById('msg').value
    }})
  }});
  document.getElementById('msg').value = '';
}};
</script>
</body></html>'''
@app.route('/')
def index():
    return render_template_string(HTML, messages=messages)
@app.route('/send', methods=['POST'])
def send():
    data = request.get_json()
    msg = {{'sender': data.get('sender', 'Anonymous'), 'content': data.get('content', '')}}
    messages.append(msg)
    socketio.emit('new_message', msg)
    return jsonify({{'status': 'ok'}})
@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(messages)
@app.route('/health', methods=['GET'])
def health():
    return jsonify({{'status': 'healthy'}})
@socketio.on('connect')
def handle_connect():
    emit('connected', {{'data': 'Connected'}})
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)

Generate similar complete code now."""
            
            print(f"[AGENT] Generating code for: {description}")
            gen_result = self.run(gen_prompt)
            code = gen_result.get("answer", "")
            
            # Clean up code
            code = self._clean_generated_code(code)
            
            if not code or "error" in code.lower()[:100]:
                result["error"] = "Code generation failed"
                return result
            
            if "Summary verdict:" in code or "Tests to add:" in code:
                result["error"] = "Agent generated validation instead of code"
                return result
            
            print(f"✅ Generated {len(code)} characters of code")
            result["generated_code"] = code
            
            # Step 4: Deploy
            print("\n" + "="*80)
            print("STEP 4: Deploying to OpenShift")
            print("="*80)
            print(f"[AGENT] Deploying {app_name} to namespace {namespace}...")
            
            if node_selector:
                print(f"[AGENT] Using node selector: {node_selector}")
            
            deploy_tool = OpenShiftDeploymentTool()
            deploy_result = deploy_tool.execute(
                code=code,
                app_name=app_name,
                namespace=namespace,
                language="python",
                node_selector=node_selector
            )
            
            result["deployment_result"] = deploy_result
            result["success"] = "SUCCESSFUL" in deploy_result
            
            print(deploy_result)
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Error: {str(e)}")
            return result
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean up generated code by removing markdown and fixing common issues"""
        code = code.strip()
        
        # Remove opening fences
        if code.startswith("```python"):
            code = code[len("```python"):].strip()
        elif code.startswith("```"):
            code = code[len("```"):].strip()
        
        # Remove closing fences
        if code.endswith("```"):
            code = code[:-3].strip()
        
        # Remove any remaining triple backticks
        code = code.replace("```", "")
        
        # Remove lines that are just backticks
        lines = code.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip() in ['```', '```python', '```py']:
                continue
            cleaned_lines.append(line)
        code = '\n'.join(cleaned_lines)
        
        # Fix Flask-SocketIO allow_unsafe_werkzeug
        if 'socketio.run(' in code and 'allow_unsafe_werkzeug' not in code:
            code = code.replace(
                'socketio.run(app, host=',
                'socketio.run(app, allow_unsafe_werkzeug=True, host='
            )
        
        # Fix common Jinja2 template variable mismatches
        if 'render_template_string' in code:
            if '{% for message in messages %}' in code and '{{ msg.' in code:
                code = code.replace('{% for message in messages %}', '{% for msg in messages %}')
                code = code.replace('{{ message.', '{{ msg.')
            if '{% for msg in messages %}' in code and '{{ message.' in code:
                code = code.replace('{{ message.', '{{ msg.')
        
        return code


def create_enhanced_agent(verbose=False):
    """Create enhanced agent"""
    return EnhancedReActAgent(verbose=False)
