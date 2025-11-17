#!/usr/bin/env python3
"""
Test all API endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_endpoint(name, method, endpoint, data=None):
    """Test an endpoint and print results"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

# Test 1: Health Check
test_endpoint("Health Check", "GET", "/health")

# Test 2: Cluster Info
test_endpoint("Cluster Info", "GET", "/agent/cluster-info")

# Test 3: Code Generation
test_endpoint(
    "Code Generation", 
    "POST", 
    "/agent/execute",
    data={"query": "Create a simple Flask API with a greeting endpoint"}
)

# Test 4: Code Validation
test_endpoint(
    "Code Validation",
    "POST",
    "/agent/validate",
    data={
        "code": "from flask import Flask\napp = Flask(__name__)",
        "language": "python"
    }
)

print("\n" + "="*60)
print("All basic tests completed!")
print("="*60)
