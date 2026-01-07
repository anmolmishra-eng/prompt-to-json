#!/usr/bin/env python3
import subprocess
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("Testing Mobile Health Endpoint")
print("="*60)

# Test without auth first
print("\n[1/2] Testing without authentication...")
health_cmd = ['curl', '-X', 'GET', 'http://localhost:8000/api/v1/mobile/health', '-s']
result = subprocess.run(health_cmd, capture_output=True, text=True)
response = json.loads(result.stdout)
print(f"Response: {json.dumps(response, indent=2)}")

# If auth required, test with auth
if 'error' in response:
    print("\n[2/2] Testing with authentication...")
    auth_cmd = ['curl', '-X', 'POST', 'http://localhost:8000/api/v1/auth/login',
                '-H', 'Content-Type: application/x-www-form-urlencoded',
                '-d', 'username=admin&password=bhiv2024', '-s']
    auth_result = subprocess.run(auth_cmd, capture_output=True, text=True)
    token = json.loads(auth_result.stdout)['access_token']

    health_auth_cmd = ['curl', '-X', 'GET', 'http://localhost:8000/api/v1/mobile/health',
                       '-H', f'Authorization: Bearer {token}', '-s']
    result = subprocess.run(health_auth_cmd, capture_output=True, text=True)
    response = json.loads(result.stdout)
    print(f"Response: {json.dumps(response, indent=2)}")

# Save response
with open('mobile_health_response.json', 'w', encoding='utf-8') as f:
    json.dump(response, f, indent=2)

print(f"\n[OK] Response saved to mobile_health_response.json")
print("="*60)
