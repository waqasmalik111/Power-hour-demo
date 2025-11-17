"""
Enhanced Flask API for AI Code Generation Agent
Includes cluster awareness and deployment capabilities
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add paths for importing enhanced agent
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.join(current_dir, '..', 'agents')
agent_enhanced_dir = os.path.join(current_dir, '..', 'agents', 'agent_enhanced')

sys.path.insert(0, agents_dir)
sys.path.insert(0, agent_enhanced_dir)

# Import enhanced agent
from enhanced_react_agent import create_enhanced_agent

app = Flask(__name__)
CORS(app)

# Create enhanced agent with cluster awareness
agent = create_enhanced_agent(verbose=False)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "agent": "ready",
        "cluster_aware": True
    }), 200


@app.route('/agent/execute', methods=['POST'])
def execute_agent():
    """
    Execute agent for code generation
    
    Request body:
    {
        "query": "Create a Flask API with greeting endpoint",
        "language": "python"  (optional)
    }
    
    Response:
    {
        "success": true,
        "answer": "generated code...",
        "history": [...],
        "cluster_context": {...},
        "query": "original query"
    }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                "success": False,
                "error": "No query provided"
            }), 400
        
        # Run the agent
        result = agent.run(query)
        
        return jsonify({
            "success": True,
            "answer": result.get("answer", ""),
            "history": result.get("history", []),
            "cluster_context": result.get("cluster_context", {}),
            "query": query
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/agent/validate', methods=['POST'])
def validate_code():
    """
    Validate code for production readiness
    
    Request body:
    {
        "code": "your code here",
        "language": "python"
    }
    
    Response:
    {
        "success": true,
        "report": "validation report...",
        "history": [...]
    }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({
                "success": False,
                "error": "No code provided for validation"
            }), 400
        
        # Run validation
        result = agent.run({
            "mode": "validate",
            "code": code,
            "language": language
        })
        
        return jsonify({
            "success": True,
            "report": result.get("answer", ""),
            "history": result.get("history", []),
            "cluster_context": result.get("cluster_context", {})
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/agent/deploy', methods=['POST'])
def deploy_app():
    """
    Generate and deploy telco application to OpenShift
    
    Request body:
    {
        "description": "telco messaging application",
        "app_name": "my-telco-app",
        "namespace": "telco-demo"
    }
    
    Response:
    {
        "success": true,
        "generated_code": "...",
        "deployment_result": "...",
        "app_name": "...",
        "namespace": "..."
    }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        description = data.get('description', 'telco messaging application')
        app_name = data.get('app_name', 'ai-telco-app')
        namespace = data.get('namespace', 'telco-demo')
        
        print(f"[API] Starting deployment: {app_name} in {namespace}")
        
        # Deploy the application
        result = agent.deploy_telco_app(
            description=description,
            app_name=app_name,
            namespace=namespace
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[API] Deployment error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/agent/cluster-info', methods=['GET'])
def cluster_info():
    """
    Get current OpenShift cluster information
    
    Query params:
    - namespace (optional): specific namespace to query
    
    Response:
    {
        "success": true,
        "namespace": "current-namespace",
        "pods": "...",
        "deployments": "..."
    }
    """
    try:
        from openshift_tools import get_current_namespace, OpenShiftClusterTool
        
        namespace = request.args.get('namespace', '') or get_current_namespace()
        cluster_tool = OpenShiftClusterTool()
        
        # Get pods
        pods = cluster_tool.execute("pods", namespace=namespace, output_format="json")
        
        # Get deployments
        deployments = cluster_tool.execute("deployments", namespace=namespace, output_format="json")
        
        return jsonify({
            "success": True,
            "namespace": namespace,
            "pods": pods,
            "deployments": deployments,
            "cluster_aware": True
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/agent/deployment-status/<app_name>', methods=['GET'])
def deployment_status(app_name):
    """
    Check status of a deployed application
    
    Query params:
    - namespace (optional): namespace where app is deployed
    
    Response:
    {
        "success": true,
        "app_name": "...",
        "namespace": "...",
        "url": "https://...",
        "pods": "...",
        "status": "..."
    }
    """
    try:
        from openshift_tools import get_current_namespace, OpenShiftClusterTool
        import subprocess
        
        namespace = request.args.get('namespace', '') or get_current_namespace()
        cluster_tool = OpenShiftClusterTool()
        
        # Get deployment info
        deployment = cluster_tool.execute(
            "deployment",
            namespace=namespace,
            name=app_name,
            output_format="json"
        )
        
        # Get pods
        pods = cluster_tool.execute(
            "pods",
            namespace=namespace,
            labels=f"app={app_name}",
            output_format="json"
        )
        
        # Get route
        route_result = subprocess.run(
            ["oc", "get", "route", app_name, "-n", namespace, "-o", "jsonpath={.spec.host}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        url = f"https://{route_result.stdout.strip()}" if route_result.returncode == 0 and route_result.stdout else None
        
        return jsonify({
            "success": True,
            "app_name": app_name,
            "namespace": namespace,
            "url": url,
            "deployment": deployment,
            "pods": pods
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/', methods=['GET'])
def index():
    """
    API documentation and information
    """
    return jsonify({
        "name": "Enhanced AI Code Generation Agent API",
        "version": "2.0.0",
        "description": "AI-powered code generation with OpenShift cluster awareness and deployment",
        "features": [
            "Code generation from natural language",
            "Code validation and security checks",
            "OpenShift cluster awareness",
            "Direct deployment to OpenShift",
            "Telco messaging application generation"
        ],
        "endpoints": {
            "GET /": "API documentation (this page)",
            "GET /health": "Health check",
            "POST /agent/execute": "Generate code from prompt",
            "POST /agent/validate": "Validate code quality and security",
            "POST /agent/deploy": "Generate and deploy application to OpenShift",
            "GET /agent/cluster-info": "Get cluster information",
            "GET /agent/deployment-status/<app_name>": "Check deployment status"
        },
        "examples": {
            "generate_code": {
                "method": "POST",
                "endpoint": "/agent/execute",
                "body": {
                    "query": "Create a Flask API with greeting endpoint"
                }
            },
            "validate_code": {
                "method": "POST",
                "endpoint": "/agent/validate",
                "body": {
                    "code": "from flask import Flask\napp = Flask(__name__)",
                    "language": "python"
                }
            },
            "deploy_app": {
                "method": "POST",
                "endpoint": "/agent/deploy",
                "body": {
                    "description": "telco messaging application",
                    "app_name": "my-telco-app",
                    "namespace": "telco-demo"
                }
            }
        },
        "cluster_aware": True,
        "status": "ready"
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print("=" * 60)
    print("Enhanced AI Code Generation Agent API")
    print("=" * 60)
    print(f"Starting server on port {port}")
    print(f"Cluster-aware: Yes")
    print(f"Deployment capable: Yes")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)