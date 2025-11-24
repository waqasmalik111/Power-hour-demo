
"""
OpenShift Cluster Tools - Query and interact with OpenShift
"""
import subprocess
import json
from typing import Dict, Any, Optional


class OpenShiftClusterTool:
    """Query OpenShift cluster resources"""
    
    def __init__(self):
        self.name = "openshift_cluster_query"
        self.description = "Query OpenShift cluster resources (pods, deployments, services, routes)"
    
    def execute(self, resource_type: str = "pods", namespace: str = "", 
                name: str = "", output_format: str = "json", labels: str = "") -> str:
        """Execute oc get commands"""
        try:
            cmd = ["oc", "get", resource_type]
            
            if namespace:
                cmd.extend(["-n", namespace])
            if name:
                cmd.append(name)
            if labels:
                cmd.extend(["-l", labels])
            if output_format:
                cmd.extend(["-o", output_format])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            
            return result.stdout or "No resources found"
            
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error executing oc command: {str(e)}"


class OpenShiftLogsTool:
    """Fetch logs from OpenShift pods"""
    
    def __init__(self):
        self.name = "openshift_logs"
        self.description = "Fetch logs from pods to debug issues"
    
    def execute(self, pod_name: str = "", namespace: str = "", 
                container: str = "", tail: int = 100) -> str:
        """Fetch pod logs"""
        try:
            cmd = ["oc", "logs"]
            
            if namespace:
                cmd.extend(["-n", namespace])
            if pod_name:
                cmd.append(pod_name)
            else:
                return "Error: pod_name is required"
            if container:
                cmd.extend(["-c", container])
            
            cmd.extend(["--tail", str(tail)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            
            return result.stdout or "No logs found"
            
        except Exception as e:
            return f"Error fetching logs: {str(e)}"


def check_openshift_login() -> bool:
    """Check if logged in to OpenShift"""
    try:
        result = subprocess.run(
            ["oc", "whoami"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False


def get_current_namespace() -> str:
    """Get current OpenShift namespace"""
    try:
        result = subprocess.run(
            ["oc", "project", "-q"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return "default"