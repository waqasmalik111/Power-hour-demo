
"""
OpenShift Deployment Tool - Deploy generated code using S2I
"""
import os
import subprocess
import tempfile
import shutil
from typing import Dict, Any


class OpenShiftDeploymentTool:
    """Deploy generated code directly to OpenShift cluster using S2I"""
    
    def __init__(self):
        self.name = "deploy_to_openshift"
        self.description = "Deploy generated code directly to OpenShift cluster"
        self.temp_dirs = []
    
    def execute(self, 
                code: str = "",
                app_name: str = "ai-generated-app",
                namespace: str = "",
                language: str = "python",
                requirements: str = "") -> str:
        """Deploy code to OpenShift using S2I"""
        try:
            # Strip markdown code fences
            code = code.strip()
            if code.startswith("```python"):
                code = code[len("```python"):].strip()
            elif code.startswith("```"):
                code = code[len("```"):].strip()
            
            if code.endswith("```"):
                code = code[:-3].strip()
            
            if not code.strip():
                return "Error: No code provided for deployment"
            
            # Check OpenShift login
            if not self._check_oc_login():
                return "Error: Not logged in to OpenShift. Run 'oc login' first."
            
            # Get or create namespace
            namespace = namespace or self._get_current_namespace()
            if not self._ensure_namespace(namespace):
                return f"Error: Could not access namespace {namespace}"
            
            # Create temp deployment directory
            deploy_dir = self._create_deployment_dir(code, app_name, requirements)
            
            # Deploy to OpenShift
            result = self._deploy_to_openshift(deploy_dir, app_name, namespace, language)
            
            # Cleanup
            self._cleanup(deploy_dir)
            
            return result
            
        except Exception as e:
            return f"Deployment failed: {str(e)}"
    
    def _check_oc_login(self) -> bool:
        """Check if logged in to OpenShift"""
        try:
            result = subprocess.run(["oc", "whoami"], capture_output=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def _get_current_namespace(self) -> str:
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
    
    def _ensure_namespace(self, namespace: str) -> bool:
        """Ensure namespace exists"""
        try:
            result = subprocess.run(["oc", "project", namespace], capture_output=True, timeout=10)
            if result.returncode == 0:
                return True
            
            # Try to create it
            result = subprocess.run(["oc", "create", "namespace", namespace], capture_output=True, timeout=10)
            if result.returncode == 0:
                subprocess.run(["oc", "project", namespace], timeout=10)
                return True
        except:
            pass
        return False
    
    def _create_deployment_dir(self, code: str, app_name: str, requirements: str) -> str:
        """Create temporary directory with deployment files"""
        deploy_dir = tempfile.mkdtemp(prefix=f"deploy_{app_name}_")
        self.temp_dirs.append(deploy_dir)
        
        # Write application code
        with open(os.path.join(deploy_dir, "app.py"), "w") as f:
            f.write(code)
        
        # Create requirements.txt
        if not requirements:
            requirements = self._detect_requirements(code)
        
        with open(os.path.join(deploy_dir, "requirements.txt"), "w") as f:
            f.write(requirements)
        
        return deploy_dir
    
    def _detect_requirements(self, code: str) -> str:
        """Auto-detect Python dependencies"""
        requirements = []
        
        if "flask" in code.lower():
            requirements.append("Flask==3.0.0")
            if "CORS" in code or "cors" in code.lower():
                requirements.append("Flask-CORS==4.0.0")
            requirements.append("gunicorn==21.2.0")
        
        if "fastapi" in code.lower():
            requirements.append("fastapi==0.104.0")
            requirements.append("uvicorn[standard]==0.24.0")
        
        return "\n".join(requirements) if requirements else "Flask==3.0.0\ngunicorn==21.2.0"
    
    def _deploy_to_openshift(self, deploy_dir: str, app_name: str, 
                            namespace: str, language: str) -> str:
        """Deploy application to OpenShift using S2I"""
        output = []
        output.append(f"🚀 Deploying {app_name} to namespace: {namespace}\n")
        
        base_image = "registry.access.redhat.com/ubi9/python-311" if language == "python" else "python:3.11"
        
        # Clean up existing
        subprocess.run(["oc", "delete", "all", "-l", f"app={app_name}", "-n", namespace],
                      capture_output=True, timeout=30)
        
        # Create build
        output.append("🏗️  Creating build configuration...\n")
        subprocess.run([
            "oc", "new-build", base_image,
            f"--name={app_name}",
            "--binary=true",
            "--strategy=source",
            "-n", namespace
        ], capture_output=True, timeout=30)
        
        # Start build
        output.append("🔨 Building application...\n")
        result = subprocess.run([
            "oc", "start-build", app_name,
            f"--from-dir={deploy_dir}",
            "--follow",
            "-n", namespace
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            output.append(f"❌ Build failed: {result.stderr}\n")
            return "".join(output)
        
        output.append("✅ Build completed\n")
        
        # Create deployment
        output.append("🚢 Creating deployment...\n")
        subprocess.run(["oc", "new-app", app_name, "-n", namespace],
                      capture_output=True, timeout=30)
        
        # Expose route
        output.append("🌐 Creating route...\n")
        subprocess.run(["oc", "expose", f"service/{app_name}", "-n", namespace],
                      capture_output=True, timeout=30)
        
        # Wait for deployment
        subprocess.run([
            "oc", "wait", "--for=condition=available",
            "--timeout=180s", f"deployment/{app_name}",
            "-n", namespace
        ], capture_output=True, timeout=200)
        
        # Get route
        route_result = subprocess.run([
            "oc", "get", "route", app_name,
            "-n", namespace,
            "-o", "jsonpath={.spec.host}"
        ], capture_output=True, text=True, timeout=10)
        
        if route_result.returncode == 0 and route_result.stdout:
            url = f"https://{route_result.stdout.strip()}"
            output.append(f"\n✅ DEPLOYMENT SUCCESSFUL!\n")
            output.append(f"🌍 Application URL: {url}\n")
            output.append(f"📦 Namespace: {namespace}\n")
        
        return "".join(output)
    
    def _cleanup(self, deploy_dir: str):
        """Clean up temporary directory"""
        try:
            if deploy_dir and os.path.exists(deploy_dir):
                shutil.rmtree(deploy_dir)
        except:
            pass
