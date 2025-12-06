# 🤖 Agentic Orchestration – Cluster-Aware Code Generation & Telco Deployment

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Framework](https://img.shields.io/badge/Framework-Flask-orange)
![Platform](https://img.shields.io/badge/Platform-Red%20Hat%20OpenShift-red)
![AI](https://img.shields.io/badge/AI-Agentic%20ReAct-green)
![Domain](https://img.shields.io/badge/Telco-CNF%2FVNF-purple)
![License](https://img.shields.io/badge/License-Apache--2.0-yellow)

> **Enterprise-grade agent that generates, validates, and deploys production-ready code on Red Hat OpenShift.**  
> Purpose-built for Telco workloads with real-time cluster awareness, intelligent node selection,  
> and secure on-prem Model-as-a-Service integration.

---

## 📘 Overview

This project implements an **Enhanced ReAct Agent** that brings together:

- AI-powered code generation  
- Deep OpenShift cluster introspection  
- Fully automated deployment flows  
- Telco domain optimizations  

The goal is to automate the entire **development → validation → deployment** lifecycle on OpenShift.

---

## 🌍 The Strategic Value

### **Four Critical Capabilities in One Platform**

| Capability | Description |
|-----------|-------------|
| **Code Generation** | Not snippets — full microservices, manifests, Dockerfiles |
| **Agentic AI** | Plans, reasons, validates, and acts autonomously |
| **Telco Focus** | Optimized for CNF/VNF-style deployments |
| **Cluster Awareness** | Reads node workloads, labels nodes, selects optimal placement |

---

# ✨ Key Features

## 🛰️ Cluster-Aware Deployment (T0 → T3 Timeline)

The agent performs an automated 4-stage deployment workflow:

### **T0 – Request Received**
- Scans full cluster state  
- Reads node workloads  
- Example:  
  - Worker-1 → **18 pods**  
  - Worker-0 → **23 pods**  
  - Worker-2 → **25 pods**  
- Identifies optimal node  

---

### **T1 – Node Selection**
- Chooses the node with the lowest workload (e.g., Worker-1)  
- Ensures resource availability  

---

### **T2 – Labeling**
Executes:

```bash
oc label node worker-1 deployment=telco-app

