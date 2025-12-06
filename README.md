# 🚀 Agentic Orchestration - Cluster-Aware Code Generation & Telco Deployment

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![OpenShift](https://img.shields.io/badge/OpenShift-4.x-red.svg)](https://www.openshift.com/)
[![ReAct](https://img.shields.io/badge/Pattern-ReAct-orange.svg)](https://react-lm.github.io/)
[![License](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](LICENSE)

> **Enterprise-grade AI agent for automated code generation, validation, and cluster-aware deployment on Red Hat OpenShift.** Built specifically for Telco workloads with intelligent node selection, real-time cluster awareness, and Model-as-a-Service integration.

---

## 🎯 Overview

This project implements an **Enhanced ReAct Agent** that combines AI-powered code generation with deep OpenShift cluster awareness to automate the complete development-to-deployment workflow for Telco applications.

### The Strategic Value

**Four Critical Capabilities in One Unified Platform:**

1. **🧠 Code Generation** - Not just snippets, but production-ready microservices from natural language
2. **🤖 Agentic AI** - Intelligent system that plans, reasons, and makes autonomous decisions
3. **📡 Telco Focus** - Built specifically for telecom workloads, CNF/VNF deployments
4. **🎯 Cluster Awareness** - Agent understands your cluster state and makes intelligent deployment decisions

---

## ✨ Key Features

### 🎯 Cluster-Aware Deployment (T0 → T3 Timeline)

The agent implements a sophisticated 4-stage deployment workflow:

**T0: Request Received**
- Agent scans entire cluster status
- Analyzes node workloads (Worker-1: 18 pods, Worker-0: 23 pods, Worker-2: 25 pods)
- Identifies optimal deployment target

**T1: Node Selection**
- Evaluation complete: System targets Worker-1 (lowest workload)
- Prepares node for deployment based on resource availability

**T2: Labeling**
- Executes: `oc label node worker-1 deployment=telco-app`
- Node becomes discoverable for targeted deployment
- Label verified and ready

**T3: Deployment**
- Kubernetes scheduler sees nodeSelector
- Pod successfully scheduled to Worker-1
- Application launched and accessible

### 🧠 AI-Powered Development

- **Automated Boilerplate**: Instantly scaffolds microservices, YAML configs, Dockerfiles
- **Cluster Context**: Generated code pre-configured for your specific OpenShift environment
- **Model Choice**: Best model for each task (Granite for Ansible, Llama for Python, Mistral for general)
- **Privacy First**: 100% on-premises inference - code never leaves your secure boundary

### 🔒 Secure On-Prem Validation

- **Private & Compliant**: All validation runs locally on OpenShift
- **Syntax & Linting Verification**: Automated code quality checks
- **SAST**: Static Application Security Testing
- **Enterprise Compliance Rules**: Custom rule enforcement

### 🎮 DevSpaces Integration

- Native VS Code extension for seamless IDE experience
- Interactive prompts with keyboard shortcuts
- Real-time cluster dashboard
- Zero-configuration cloud development environments

---

## 📁 Project Structure

```
agent-orchestrator-openshift/
├── 📱 app/                              # Flask API Backend
│   ├── app.py                          # Main REST API server (v3.0)
│   ├── requirements.txt                # Python dependencies
│   └── README.md                       # Backend documentation
│
├── 🤖 agents/                          # AI Agent Core
│   ├── react_agent.py                  # Base ReAct agent
│   ├── agent_enhanced/                 # Enhanced cluster-aware agent
│   │   ├── enhanced_react_agent.py    # Main enhanced agent
│   │   ├── openshift_tools.py         # Cluster interaction tools
│   │   └── deployment_tool.py         # Deployment automation
│   └── README.md                       # Agent documentation
│
├── 🌐 devspaces-agent-extension/       # VS Code Extension
│   ├── extension.js                    # Extension logic
│   ├── package.json                    # Extension manifest
│   └── devspaces-agent-extension.vsix  # Packaged extension
│
├── 🧪 scripts-api-test/                # Testing & Validation
│   ├── mistral_api_test.py            # Model API connectivity tests
│   └── README.md                       # Test documentation
│
├── 🔧 scripts-for-codegen/             # Utility Scripts
│   ├── generate.sh                     # Code generation script
│   └── validate.sh                     # Validation script
│
├── 🐳 Containerfile                    # Container build definition
├── 📦 deployment.yaml                  # OpenShift deployment manifest
├── 🌍 index.html                       # Web dashboard UI
└── 📖 README.md                        # This file
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required
✅ Python 3.9+
✅ OpenShift 4.x cluster access
✅ oc CLI tool installed and configured
✅ Model-as-a-Service endpoint (Mistral/Granite/Llama)

# Optional but Recommended
✨ Red Hat OpenShift AI
✨ Red Hat DevSpaces
✨ Git
```

### Installation

**1. Clone the Repository**
```bash
git clone https://github.com/your-org/agent-orchestrator-openshift.git
cd agent-orchestrator-openshift
```

**2. Set Up Python Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install Dependencies**
```bash
cd app
pip install -r requirements.txt --break-system-packages
```

**4. Configure Environment**
```bash
cat > .env << EOF
# Model-as-a-Service Configuration
API_KEY=your_model_api_key
MODEL_ENDPOINT=https://your-model-endpoint.com/v1
MODEL_NAME=mistral-large-latest

# Flask Configuration
PORT=8080
FLASK_ENV=production

# OpenShift Configuration
OC_NAMESPACE=telco-demo
EOF
```

**5. Verify OpenShift Access**
```bash
oc whoami
oc project telco-demo  # Create if needed: oc new-project telco-demo
```

### Running the Application

#### **Option 1: Local Development**
```bash
cd app
python app.py
```
Server starts at `http://localhost:8080`

```
============================================================
Enhanced AI Code Generation Agent API v3.0
============================================================
Starting server on port 8080
Cluster-aware: Yes
Node selection: Yes
Auto-labeling: Yes
Deployment capable: Yes
============================================================
```

#### **Option 2: OpenShift Deployment**
```bash
# Deploy to OpenShift
oc apply -f deployment.yaml

# Verify deployment
oc get pods -l app=agent-orchestrator

# Get route
oc get route agent-orchestrator
```

#### **Option 3: DevSpaces Extension**
```bash
# Install the VS Code extension
code --install-extension devspaces-agent-extension/devspaces-agent-extension.vsix

# Or in DevSpaces:
# 1. Open Extensions panel (Ctrl+Shift+X)
# 2. Click "..." → "Install from VSIX"
# 3. Select devspaces-agent-extension-0.0.3.vsix
```

---

## 📚 API Documentation

### Core Endpoints

| Endpoint | Method | Description | Cluster-Aware |
|----------|--------|-------------|---------------|
| `/health` | GET | Health check and feature status | ✅ |
| `/agent/execute` | POST | Generate code from natural language | ✅ |
| `/agent/validate` | POST | Validate code quality and security | ✅ |
| `/agent/cluster-overview` | GET | Comprehensive cluster state | ✅ |
| `/agent/nodes` | GET | List all cluster nodes with metrics | ✅ |
| `/agent/nodes/least-workload` | GET | Find optimal deployment node | ✅ |
| `/agent/nodes/label` | POST | Label a specific node | ✅ |
| `/agent/nodes/check-label` | GET | Verify label existence | ✅ |
| `/agent/deploy` | POST | **Full T0→T3 deployment workflow** | ✅ |
| `/agent/deployment-status/<app>` | GET | Check deployment status | ✅ |

### Complete Deployment Workflow Example

The `/agent/deploy` endpoint executes the entire T0→T3 timeline automatically:

**Request:**
```bash
curl -X POST http://localhost:8080/agent/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "description": "real-time P2P messaging application",
    "app_name": "telco-messenger",
    "namespace": "telco-demo",
    "node_label_key": "deployment",
    "node_label_value": "telco-app"
  }'
```

**Response:**
```json
{
  "success": true,
  "cluster_overview": "CLUSTER OVERVIEW\n...\nNodes: 3 (1 master, 2 workers)\n  worker-0: 23 pods\n  worker-1: 18 pods ← SELECTED (least workload)\n  worker-2: 25 pods",
  "node_selection": {
    "requested": true,
    "label": {"deployment": "telco-app"},
    "nodes": ["worker-1"],
    "status": "Label created",
    "pod_count": 18
  },
  "generated_code": "from flask import Flask...",
  "deployment_result": "DEPLOYMENT SUCCESSFUL\nPod: telco-messenger-xxxxx\nNode: worker-1\nStatus: Running",
  "app_name": "telco-messenger",
  "namespace": "telco-demo"
}
```

---

## 🎯 Usage Scenarios

### Scenario 1: Generate Production Code

```python
import requests

response = requests.post('http://localhost:8080/agent/execute', json={
    "query": "Create a Flask API for Telco messaging with health check, send message, and get messages endpoints"
})

code = response.json()['answer']
with open('app.py', 'w') as f:
    f.write(code)
```

### Scenario 2: Validate Existing Code

```python
with open('my_code.py', 'r') as f:
    code = f.read()

response = requests.post('http://localhost:8080/agent/validate', json={
    "code": code,
    "language": "python"
})

report = response.json()['report']
print(report)
```

### Scenario 3: Intelligent Cluster-Aware Deployment

```python
# This executes the complete T0→T3 timeline automatically
response = requests.post('http://localhost:8080/agent/deploy', json={
    "description": "5G messaging service with WebSocket support and real-time updates",
    "app_name": "5g-messenger",
    "namespace": "telco-demo",
    "node_label_key": "deployment",
    "node_label_value": "5g-app"
})

result = response.json()

print(f"✅ Deployment: {result['success']}")
print(f"📍 Deployed to Node: {result['node_selection']['nodes'][0]}")
print(f"📊 Node had {result['node_selection']['pod_count']} pods (lowest workload)")
print(f"🏷️  Label Applied: {result['node_selection']['label']}")

# Check deployment status
status_response = requests.get(f"http://localhost:8080/agent/deployment-status/5g-messenger?namespace=telco-demo")
print(f"🌐 Access URL: {status_response.json()['url']}")
```

---

## 🏗️ Architecture Deep Dive

### The Agentic Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                                     │
│              "Deploy a messaging app to OpenShift"                       │
└────────────────────────────┬────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  DevSpaces UI    │
                    │  (VS Code Ext)   │
                    └────────┬─────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Flask API       │
                    │  (REST Endpoint) │
                    └────────┬─────────┘
                              │
                              ▼
        ╔═══════════════════════════════════════════════════╗
        ║        ENHANCED REACT AGENT (Brain)               ║
        ║                                                   ║
        ║  ┌──────────────────────────────────────────┐   ║
        ║  │ Intent Handler & Planner                 │   ║
        ║  │ • Analyze request                        │   ║
        ║  │ • Plan multi-step workflow               │   ║
        ║  │ • Coordinate tool calls                  │   ║
        ║  └──────────────┬───────────────────────────┘   ║
        ║                  │                               ║
        ║                  ▼                               ║
        ║   ┌──────────────────────────────────────────┐  ║
        ║   │         Tool Orchestration                │  ║
        ║   │                                           │  ║
        ║   │  ┌──────────────┐  ┌──────────────┐     │  ║
        ║   │  │ Code Gen     │  │ Code         │     │  ║
        ║   │  │ Handler      │  │ Validation   │     │  ║
        ║   │  └──────────────┘  └──────────────┘     │  ║
        ║   │                                           │  ║
        ║   │  ┌──────────────┐  ┌──────────────┐     │  ║
        ║   │  │ OCP API      │  │ Deployment   │     │  ║
        ║   │  │ Handler      │  │ Handler      │     │  ║
        ║   │  └──────────────┘  └──────────────┘     │  ║
        ║   │                                           │  ║
        ║   │  ┌──────────────┐                        │  ║
        ║   │  │ GitOps       │                        │  ║
        ║   │  │ Handler      │                        │  ║
        ║   │  └──────────────┘                        │  ║
        ║   └──────────────┬───────────────────────────┘  ║
        ║                  │                               ║
        ╚══════════════════╪═══════════════════════════════╝
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │ Model-as-a-  │  │  OpenShift   │  │  Deployed    │
  │  Service     │  │  Cluster     │  │  Telco App   │
  │              │  │              │  │              │
  │ • Mistral    │  │ • Nodes      │  │ • Running    │
  │ • Granite    │  │ • Pods       │  │ • Accessible │
  │ • Llama      │  │ • Routes     │  │ • Monitored  │
  └──────────────┘  └──────────────┘  └──────────────┘
```

### ReAct Pattern in Action

The agent uses **Reasoning and Acting (ReAct)** to solve complex tasks:

**Iteration 1: Understanding**
- **Thought**: "User wants to deploy a messaging app. I need cluster state first."
- **Action**: Call `OpenShiftClusterInfoTool.get_cluster_overview()`
- **Observation**: "3 nodes, worker-1 has 18 pods (least busy)"

**Iteration 2: Planning**
- **Thought**: "No label 'deployment=telco-app' exists. Need to create it."
- **Action**: Call `OpenShiftNodeTool.label_node(worker-1, deployment, telco-app)`
- **Observation**: "Label created successfully"

**Iteration 3: Code Generation**
- **Thought**: "Need Flask app code for messaging with WebSockets"
- **Action**: Call `CodeGenTool.generate(prompt)`
- **Observation**: "Generated 450 lines of production code"

**Iteration 4: Deployment**
- **Thought**: "Code ready, node labeled, can deploy now"
- **Action**: Call `OpenShiftDeploymentTool.execute(code, app_name, namespace, node_selector)`
- **Observation**: "Deployment successful, pod running on worker-1"

---

## 🔧 Advanced Configuration

### Model-as-a-Service Setup

Configure multiple LLM backends for different tasks:

```bash
# .env configuration
MODEL_ENDPOINT_MISTRAL=https://mistral-endpoint.com/v1
MODEL_ENDPOINT_GRANITE=https://granite-endpoint.com/v1
MODEL_ENDPOINT_LLAMA=https://llama-endpoint.com/v1

# Default model
MODEL_NAME=mistral-large-latest

# Task-specific models
MODEL_ANSIBLE=granite-20b-code
MODEL_PYTHON=llama-3-70b-instruct
```

### Custom Deployment Templates

Create custom deployment templates in `agents/agent_enhanced/deployment_tool.py`:

```python
TELCO_DEPLOYMENT_TEMPLATE = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  namespace: {namespace}
  labels:
    app: {app_name}
    telco-workload: "true"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      nodeSelector:
        {node_selector}
      containers:
      - name: {app_name}
        image: {image}
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
          requests:
            cpu: "1"
            memory: "2Gi"
"""
```

---

## 🧪 Testing & Validation

### Run API Tests

```bash
cd scripts-api-test
python mistral_api_test.py

# Output:
# ✅ Model API: Connected
# ✅ Code Generation: Working
# ✅ Response Time: 1.2s
```

### Validate Generated Code

```bash
cd scripts-for-codegen
./validate.sh path/to/generated_code.py

# Runs:
# • Syntax check (pylint)
# • Security scan (bandit)
# • Complexity analysis
# • Dependency check
```

### Integration Tests

```bash
pytest tests/ -v

# Tests:
# test_cluster_awareness.py::test_node_selection ✅
# test_deployment.py::test_full_workflow ✅
# test_code_generation.py::test_flask_generation ✅
```

---

## 📊 Monitoring & Observability

### Health Check

```bash
curl http://localhost:8080/health

{
  "status": "healthy",
  "agent": "ready",
  "cluster_aware": true,
  "features": [
    "cluster_overview",
    "node_selection",
    "auto_labeling",
    "intelligent_deployment"
  ]
}
```

### Deployment Metrics

```bash
# Check agent performance
oc logs deployment/agent-orchestrator | grep "DEPLOYMENT SUCCESSFUL"

# Monitor cluster decisions
oc logs deployment/agent-orchestrator | grep "Node Selection"
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Clone and setup
git clone https://github.com/your-org/agent-orchestrator-openshift.git
cd agent-orchestrator-openshift
python3 -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run linters
flake8 app/ agents/
black --check app/ agents/

# Run tests
pytest tests/ -v --cov=app --cov=agents
```

### Contribution Guidelines

1. **Fork** the repository
2. Create a **feature branch**: `git checkout -b feature/amazing-feature`
3. Make changes with **clear commit messages**
4. Add **tests** for new functionality
5. Ensure **all tests pass**: `pytest`
6. Update **documentation** if needed
7. Submit a **pull request**

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 🔒 Security & Compliance

### Security Features

- ✅ 100% air-gapped operation (no external data transfer)
- ✅ Built-in SAST scanning before deployment
- ✅ OpenShift RBAC integration
- ✅ Secrets managed via OpenShift Secrets
- ✅ Network policies enforced
- ✅ Container image vulnerability scanning

### Reporting Security Issues

Found a security vulnerability? Please email **security@yourcompany.com** instead of creating a public issue.

---

## 🙏 Acknowledgments

- [**Red Hat OpenShift**](https://www.openshift.com/) - Enterprise Kubernetes platform
- [**Red Hat OpenShift AI**](https://www.redhat.com/en/technologies/cloud-computing/openshift/openshift-ai) - AI/ML platform
- [**Mistral AI**](https://mistral.ai/) - LLM capabilities
- [**ReAct Paper**](https://react-lm.github.io/) - Agent architecture inspiration
- [**Flask**](https://flask.palletsprojects.com/) - Python web framework
- **Telco Engineering Teams** - Use case validation and feedback
- **Red Hat Demo Platform** - Fast environment provisioning

---

## 📞 Support & Resources

### Documentation
- 📖 [Wiki](https://github.com/your-org/agent-orchestrator-openshift/wiki) - Extended docs
- 📚 [API Docs](https://github.com/your-org/agent-orchestrator-openshift/blob/main/API.md) - Complete API reference
- 🎓 [Tutorials](https://github.com/your-org/agent-orchestrator-openshift/blob/main/TUTORIALS.md) - Step-by-step guides

### Community
- 💬 [Discussions](https://github.com/your-org/agent-orchestrator-openshift/discussions) - Ask questions
- 🐛 [Issues](https://github.com/your-org/agent-orchestrator-openshift/issues) - Report bugs
- 📊 [Projects](https://github.com/your-org/agent-orchestrator-openshift/projects) - Roadmap

### Contact
- **Email**: support@yourcompany.com
- **Slack**: #agentic-orchestration
- **Twitter**: @AgenticOrch

---

<p align="center">
  <strong>Built with ❤️ by the Agentic Orchestration Team</strong><br>
  <sub>Empowering Telco developers with AI-driven automation on OpenShift</sub>
</p>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-api-documentation">API</a> •
  <a href="#-usage-scenarios">Examples</a> •
  <a href="#-architecture-deep-dive">Architecture</a> •
  <a href="#-contributing">Contributing</a>
</p>
