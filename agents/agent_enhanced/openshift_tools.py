"""
Enhanced OpenShift Cluster Tools with Node Management
Adds node labeling, cluster info display, and node selection
"""
import subprocess
import json
from typing import Dict, Any, Optional, List, Tuple


class OpenShiftClusterTool:
    """Query OpenShift cluster resources"""
    
    def __init__(self):
        self.name = "openshift_cluster_query"
        self.description = "Query OpenShift cluster resources (pods, deployments, services, routes, nodes)"
    
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


class OpenShiftNodeTool:
    """Manage OpenShift nodes and labels"""
    
    def __init__(self):
        self.name = "openshift_node_manager"
        self.description = "Manage OpenShift nodes, labels, and workload distribution"
    
    def get_nodes_info(self) -> List[Dict[str, Any]]:
        """Get detailed information about all nodes"""
        try:
            cmd = ["oc", "get", "nodes", "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return []
            
            data = json.loads(result.stdout)
            nodes_info = []
            
            for node in data.get("items", []):
                node_name = node["metadata"]["name"]
                labels = node["metadata"].get("labels", {})
                
                # Get pod count on this node
                pod_count = self._get_pod_count_on_node(node_name)
                
                # Get node capacity and allocatable resources
                capacity = node["status"].get("capacity", {})
                allocatable = node["status"].get("allocatable", {})
                
                # Get node conditions
                conditions = node["status"].get("conditions", [])
                ready = False
                for condition in conditions:
                    if condition.get("type") == "Ready":
                        ready = condition.get("status") == "True"
                        break
                
                nodes_info.append({
                    "name": node_name,
                    "labels": labels,
                    "pod_count": pod_count,
                    "ready": ready,
                    "capacity": capacity,
                    "allocatable": allocatable,
                    "roles": self._get_node_roles(labels)
                })
            
            return nodes_info
            
        except Exception as e:
            print(f"Error getting nodes info: {str(e)}")
            return []
    
    def _get_pod_count_on_node(self, node_name: str) -> int:
        """Get number of pods running on a specific node"""
        try:
            cmd = ["oc", "get", "pods", "--all-namespaces", 
                   "--field-selector", f"spec.nodeName={node_name}",
                   "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return 0
            
            data = json.loads(result.stdout)
            return len(data.get("items", []))
            
        except:
            return 0
    
    def _get_node_roles(self, labels: Dict[str, str]) -> List[str]:
        """Extract node roles from labels"""
        roles = []
        for key in labels:
            if key.startswith("node-role.kubernetes.io/"):
                role = key.replace("node-role.kubernetes.io/", "")
                roles.append(role)
        return roles if roles else ["worker"]
    
    def find_node_with_least_workload(self, exclude_masters: bool = True) -> Optional[Dict[str, Any]]:
        """Find the node with the least number of pods"""
        nodes = self.get_nodes_info()
        
        if not nodes:
            return None
        
        # Filter out master nodes if requested
        if exclude_masters:
            nodes = [n for n in nodes if "master" not in n["roles"] and "control-plane" not in n["roles"]]
        
        if not nodes:
            return None
        
        # Find node with minimum pod count
        return min(nodes, key=lambda x: x["pod_count"])
    
    def label_node(self, node_name: str, label_key: str, label_value: str) -> Tuple[bool, str]:
        """Add a label to a node"""
        try:
            label = f"{label_key}={label_value}"
            cmd = ["oc", "label", "node", node_name, label, "--overwrite"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return False, f"Failed to label node: {result.stderr}"
            
            return True, f"Successfully labeled node {node_name} with {label}"
            
        except Exception as e:
            return False, f"Error labeling node: {str(e)}"
    
    def get_nodes_with_label(self, label_key: str, label_value: str = None) -> List[str]:
        """Get all nodes with a specific label"""
        try:
            label_selector = f"{label_key}={label_value}" if label_value else label_key
            cmd = ["oc", "get", "nodes", "-l", label_selector, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return []
            
            data = json.loads(result.stdout)
            return [node["metadata"]["name"] for node in data.get("items", [])]
            
        except:
            return []
    
    def remove_label_from_node(self, node_name: str, label_key: str) -> Tuple[bool, str]:
        """Remove a label from a node"""
        try:
            cmd = ["oc", "label", "node", node_name, f"{label_key}-"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return False, f"Failed to remove label: {result.stderr}"
            
            return True, f"Successfully removed label {label_key} from node {node_name}"
            
        except Exception as e:
            return False, f"Error removing label: {str(e)}"


class OpenShiftClusterInfoTool:
    """Get comprehensive cluster information"""
    
    def __init__(self):
        self.name = "openshift_cluster_info"
        self.description = "Get comprehensive OpenShift cluster information"
    
    def get_cluster_overview(self, namespace: str = "") -> Dict[str, Any]:
        """Get a comprehensive overview of the cluster"""
        overview = {}
        
        # Get nodes information
        node_tool = OpenShiftNodeTool()
        nodes = node_tool.get_nodes_info()
        overview["nodes"] = {
            "total": len(nodes),
            "ready": sum(1 for n in nodes if n["ready"]),
            "details": nodes
        }
        
        # Get cluster operators
        overview["cluster_operators"] = self._get_cluster_operators()
        
        # Get namespaces
        overview["namespaces"] = self._get_namespaces()
        
        # Get cluster version
        overview["cluster_version"] = self._get_cluster_version()
        
        # If namespace specified, get namespace-specific info
        if namespace:
            overview["namespace_info"] = self._get_namespace_info(namespace)
        
        return overview
    
    def _get_cluster_operators(self) -> Dict[str, Any]:
        """Get cluster operators status"""
        try:
            cmd = ["oc", "get", "clusteroperators", "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {"error": "Failed to get cluster operators"}
            
            data = json.loads(result.stdout)
            operators = []
            
            for op in data.get("items", []):
                name = op["metadata"]["name"]
                conditions = op["status"].get("conditions", [])
                
                available = False
                progressing = False
                degraded = False
                
                for condition in conditions:
                    if condition["type"] == "Available":
                        available = condition["status"] == "True"
                    elif condition["type"] == "Progressing":
                        progressing = condition["status"] == "True"
                    elif condition["type"] == "Degraded":
                        degraded = condition["status"] == "True"
                
                operators.append({
                    "name": name,
                    "available": available,
                    "progressing": progressing,
                    "degraded": degraded
                })
            
            return {
                "total": len(operators),
                "available": sum(1 for o in operators if o["available"]),
                "degraded": sum(1 for o in operators if o["degraded"]),
                "operators": operators[:10]  # Show first 10
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_namespaces(self) -> Dict[str, Any]:
        """Get namespaces count"""
        try:
            cmd = ["oc", "get", "namespaces", "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {"error": "Failed to get namespaces"}
            
            data = json.loads(result.stdout)
            namespaces = [ns["metadata"]["name"] for ns in data.get("items", [])]
            
            return {
                "total": len(namespaces),
                "list": namespaces[:20]  # Show first 20
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_cluster_version(self) -> str:
        """Get OpenShift cluster version"""
        try:
            cmd = ["oc", "version", "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return "Unknown"
            
            data = json.loads(result.stdout)
            return data.get("openshiftVersion", "Unknown")
            
        except:
            return "Unknown"
    
    def _get_namespace_info(self, namespace: str) -> Dict[str, Any]:
        """Get detailed information about a specific namespace"""
        try:
            info = {}
            
            # Get pods count
            cmd = ["oc", "get", "pods", "-n", namespace, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                info["pods_count"] = len(data.get("items", []))
            
            # Get deployments count
            cmd = ["oc", "get", "deployments", "-n", namespace, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                info["deployments_count"] = len(data.get("items", []))
            
            # Get services count
            cmd = ["oc", "get", "services", "-n", namespace, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                info["services_count"] = len(data.get("items", []))
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def format_cluster_overview(self, overview: Dict[str, Any]) -> str:
        """Format cluster overview for display"""
        output = []
        output.append("=" * 80)
        output.append("🔍 OPENSHIFT CLUSTER OVERVIEW")
        output.append("=" * 80)
        
        # Cluster version
        output.append(f"\n📦 Cluster Version: {overview.get('cluster_version', 'Unknown')}")
        
        # Nodes information
        nodes = overview.get("nodes", {})
        output.append(f"\n🖥️  NODES:")
        output.append(f"   Total Nodes: {nodes.get('total', 0)}")
        output.append(f"   Ready Nodes: {nodes.get('ready', 0)}")
        
        if nodes.get("details"):
            output.append("\n   Node Details:")
            for node in nodes["details"]:
                status = "✅" if node["ready"] else "❌"
                output.append(f"   {status} {node['name']}")
                output.append(f"      Roles: {', '.join(node['roles'])}")
                output.append(f"      Running Pods: {node['pod_count']}")
                if node.get("labels"):
                    custom_labels = {k: v for k, v in node["labels"].items() 
                                   if not k.startswith("node-role.kubernetes.io/") 
                                   and not k.startswith("kubernetes.io/")
                                   and not k.startswith("node.openshift.io/")}
                    if custom_labels:
                        output.append(f"      Custom Labels: {custom_labels}")
        
        # Cluster operators
        operators = overview.get("cluster_operators", {})
        if not operators.get("error"):
            output.append(f"\n⚙️  CLUSTER OPERATORS:")
            output.append(f"   Total: {operators.get('total', 0)}")
            output.append(f"   Available: {operators.get('available', 0)}")
            output.append(f"   Degraded: {operators.get('degraded', 0)}")
        
        # Namespaces
        namespaces = overview.get("namespaces", {})
        if not namespaces.get("error"):
            output.append(f"\n📁 NAMESPACES:")
            output.append(f"   Total: {namespaces.get('total', 0)}")
        
        # Namespace-specific info
        ns_info = overview.get("namespace_info")
        if ns_info:
            output.append(f"\n🎯 CURRENT NAMESPACE INFO:")
            output.append(f"   Pods: {ns_info.get('pods_count', 0)}")
            output.append(f"   Deployments: {ns_info.get('deployments_count', 0)}")
            output.append(f"   Services: {ns_info.get('services_count', 0)}")
        
        output.append("=" * 80)
        
        return "\n".join(output)


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
