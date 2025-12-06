# 🤖 Agentic Orchestration – Cluster-Aware Code Generation & Telco Deployment

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Framework](https://img.shields.io/badge/Framework-Flask-orange)
![Platform](https://img.shields.io/badge/Platform-Red%20Hat%20OpenShift-red)
![Domain](https://img.shields.io/badge/Domain-Telco%20CNF%2FVNF-purple)
![Pattern](https://img.shields.io/badge/Pattern-ReAct-brightgreen)
![License](https://img.shields.io/badge/License-Apache--2.0-yellow)

> **Enterprise-grade AI agent for automated code generation, validation,  
> and cluster-aware deployment on Red Hat OpenShift.**  
> Built specifically for Telco workloads with intelligent node selection,  
> real-time cluster awareness, and Model-as-a-Service integration.

---

## 📚 Overview

This project implements an **Enhanced ReAct Agent** that combines AI-powered code generation with deep OpenShift cluster awareness to automate the complete development-to-deployment workflow for Telco applications.

---

## 🌍 The Strategic Value

**Four Critical Capabilities in One Unified Platform:**

- **Code Generation** – Not just snippets, but production-ready microservices from natural language  
- **Agentic AI** – Intelligent system that plans, reasons, and makes autonomous decisions  
- **Telco Focus** – Built specifically for telecom workloads, CNF/VNF deployments  
- **Cluster Awareness** – Agent understands your cluster state and makes intelligent deployment decisions  

---

## ✨ Key Features

### 🛰️ Cluster-Aware Deployment (T0 → T3 Timeline)

The agent implements a sophisticated 4-stage deployment workflow:

**T0: Request Received**

- Agent scans entire cluster status  
- Analyzes node workloads (e.g. Worker-1: 18 pods, Worker-0: 23 pods, Worker-2: 25 pods)  
- Identifies optimal deployment target  

**T1: Node Selection**

- Evaluation complete: system targets `worker-1` (lowest workload)  
- Prepares node for deployment based on resource availability  

**T2: Labeling**

- Executes: `oc label node worker-1 deployment=telco-app`  
- Node becomes discoverable for targeted deployment  
- Label verified and ready  

**T3: Deployment**

- Kubernetes scheduler sees `nodeSelector`  
- Pod successfully scheduled to `worker-1`  
- Application launched and accessible  

---

### 🧠 AI-Powered Development

- **Automated Boilerplate** – Instantly scaffolds microservices, YAML configs, Dockerfiles  
- **Cluster Context** – Generated code pre-configured for your specific OpenShift environment  
- **Model Choice** – Best model for each task (Granite for Ansible, Llama for Python, Mistral for general)  
- **Privacy First** – 100% on-premises inference – code never leaves your secure boundary  

---

### 🛡️ Secure On-Prem Validation

- **Private & Compliant** – All validation runs locally on OpenShift  
- **Syntax & Linting Verification** – Automated code quality checks  
- **SAST** – Static Application Security Testing  
- **Enterprise Compliance Rules** – Custom rule enforcement  

---

### 🧑‍💻 DevSpaces Integration

- Native VS Code extension for seamless IDE experience  
- Interactive prompts with keyboard shortcuts  
- Real-time cluster dashboard  
- Zero-configuration cloud development environments  

---

## 🗂️ Project Structure

```text
agent-orchestrator-openshift/
├── 📱 app/                              # Flask API Backend
│   ├── app.py                          # Main REST API server (v3.0)
│   ├── requirements.txt                # Python dependencies
│   └── README.md                       # Backend documentation
│
├── 🤖 agents/                          # AI Agent Core
│   ├── react_agent.py                  # Base ReAct agent
│   ├── agent_enhanced/                 # Enhanced cluster-aware agent
│   │   ├── enhanced_react_agent.py     # Main enhanced agent
│   │   ├── openshift_tools.py          # Cluster interaction tools
│   │   └── deployment_tool.py          # Deployment automation
│   └── README.md                       # Agent documentation
│
├── 🌐 devspaces-agent-extension/       # VS Code Extension
│   ├── extension.js                    # Extension logic
│   ├── package.json                    # Extension manifest
│   └── devspaces-agent-extension.vsix  # Packaged extension
│
├── 🧪 scripts-api-test/                # Testing & Validation
│   ├── mistral_api_test.py             # Model API connectivity tests
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

