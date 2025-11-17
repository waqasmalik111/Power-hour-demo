import requests
import json

print("🚀 Deploying Telco Messaging App...")

response = requests.post(
    "http://127.0.0.1:8080/agent/deploy",
    json={
        "description": "telco messaging application",
        "app_name": "telco-demo-app",
        "namespace": "telco-demo"
    },
    timeout=600
)

result = response.json()
print(json.dumps(result, indent=2))
