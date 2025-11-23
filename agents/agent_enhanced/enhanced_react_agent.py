"""
Enhanced wrapper around your existing ReActAgent
Adds cluster awareness without modifying original
"""
import sys
import os

# Add parent directory to path to import react_agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from react_agent import ReActAgent, CodeGenTool, CodeValidateTool
from openshift_tools import OpenShiftClusterTool, OpenShiftLogsTool, check_openshift_login, get_current_namespace
from deployment_tool import OpenShiftDeploymentTool


class EnhancedReActAgent(ReActAgent):
    """Enhanced agent with cluster awareness and deployment"""
    
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
    
    def deploy_telco_app(self, description: str, app_name: str = "telco-app", 
                         namespace: str = "telco-demo"):
        """
        Complete workflow: Generate → Validate → Deploy
        """
        # IMPROVED: Explicit prompt with example to avoid template errors
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
        
        # IMPROVED: More aggressive markdown fence removal
        code = code.strip()
        
        # Remove opening fences
        if code.startswith("```python"):
            code = code[len("```python"):].strip()
        elif code.startswith("```"):
            code = code[len("```"):].strip()
        
        # Remove closing fences
        if code.endswith("```"):
            code = code[:-3].strip()
        
        # Remove any remaining triple backticks that might be in the middle
        code = code.replace("```", "")
        
        # Remove any lines that are just backticks
        lines = code.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip lines that are just backticks
            if line.strip() in ['```', '```python', '```py']:
                continue
            cleaned_lines.append(line)
        code = '\n'.join(cleaned_lines)
        
        # FIX: Add allow_unsafe_werkzeug=True for production Flask-SocketIO
        if 'socketio.run(' in code and 'allow_unsafe_werkzeug' not in code:
            code = code.replace(
                'socketio.run(app, host=',
                'socketio.run(app, allow_unsafe_werkzeug=True, host='
            )
        
        # FIX: Common Jinja2 template variable mismatches
        if 'render_template_string' in code:
            # Fix {% for message in messages %} with {{ msg.xxx }}
            if '{% for message in messages %}' in code and '{{ msg.' in code:
                code = code.replace('{% for message in messages %}', '{% for msg in messages %}')
                code = code.replace('{{ message.', '{{ msg.')
            # Fix {% for msg in messages %} with {{ message.xxx }}
            if '{% for msg in messages %}' in code and '{{ message.' in code:
                code = code.replace('{{ message.', '{{ msg.')
        
        # DEBUG: Print what we got
        print("=" * 80)
        print(f"[DEBUG] Generated code length: {len(code)}")
        print(f"[DEBUG] First 500 characters:")
        print(code[:500])
        print("=" * 80)
        print(f"[DEBUG] Last 300 characters:")
        print(code[-300:] if len(code) > 300 else code)
        print("=" * 80)
        
        if not code or "error" in code.lower()[:100]:
            return {"success": False, "error": "Code generation failed"}
        
        # Check if we got validation output instead of code
        if "Summary verdict:" in code or "Tests to add:" in code:
            print("[ERROR] Got validation output instead of code!")
            return {"success": False, "error": "Agent generated validation instead of code"}
        
        print(f"[AGENT] Generated {len(code)} characters of code")
        
        # Deploy
        print(f"[AGENT] Deploying to {namespace}...")
        deploy_tool = OpenShiftDeploymentTool()
        deploy_result = deploy_tool.execute(
            code=code,
            app_name=app_name,
            namespace=namespace,
            language="python"
        )
        
        return {
            "success": "SUCCESSFUL" in deploy_result,
            "generated_code": code,
            "deployment_result": deploy_result,
            "app_name": app_name,
            "namespace": namespace
        }


def create_enhanced_agent(verbose=False):
    """Create enhanced agent"""
    return EnhancedReActAgent(verbose=False)