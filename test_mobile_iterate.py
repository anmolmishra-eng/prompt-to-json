#!/usr/bin/env python3
import subprocess
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("Testing Mobile Iterate Endpoint")
print("="*60)

# Authenticate
print("\n[1/4] Authenticating...")
auth_cmd = ['curl', '-X', 'POST', 'http://localhost:8000/api/v1/auth/login',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-d', 'username=admin&password=bhiv2024', '-s']
auth_result = subprocess.run(auth_cmd, capture_output=True, text=True)
token = json.loads(auth_result.stdout)['access_token']
print(f"[OK] Token: {token[:20]}...")

# Test mobile iterate
print("\n[2/4] Testing mobile iterate endpoint...")
payload = {
    "user_id": "mobile_test_user",
    "spec_id": "spec_bd6c4566f93d",
    "strategy": "auto_optimize"
}

iterate_cmd = ['curl', '-X', 'POST', 'http://localhost:8000/api/v1/mobile/iterate',
               '-H', f'Authorization: Bearer {token}',
               '-H', 'Content-Type: application/json',
               '-d', json.dumps(payload),
               '-s', '-w', '\\nHTTP_CODE:%{http_code}']

iterate_result = subprocess.run(iterate_cmd, capture_output=True, text=True)
output = iterate_result.stdout

if 'HTTP_CODE:' in output:
    response_text, status = output.rsplit('HTTP_CODE:', 1)
    status_code = status.strip()
else:
    response_text = output
    status_code = 'unknown'

print(f"Status: {status_code}")

# Save response
print("\n[3/4] Saving response locally...")
with open('mobile_iterate_response.json', 'w', encoding='utf-8') as f:
    f.write(response_text)
print(f"[OK] Saved to mobile_iterate_response.json")

# Verify
print("\n[4/4] Verifying response...")
try:
    response_data = json.loads(response_text)
    print(f"[OK] Iteration completed")
    print(f"     New Spec ID: {response_data.get('new_spec_id', 'N/A')}")
    print(f"     Version: {response_data.get('new_version', 'N/A')}")
    print(f"     Iteration ID: {response_data.get('iteration_id', 'N/A')}")

    # Verify new spec in database
    if 'new_spec_id' in response_data:
        verify_cmd = ['curl', '-X', 'GET',
                      f'http://localhost:8000/api/v1/specs/{response_data["new_spec_id"]}',
                      '-H', f'Authorization: Bearer {token}', '-s']
        verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
        verify_data = json.loads(verify_result.stdout)
        if 'spec_id' in verify_data:
            print(f"[OK] New spec verified in database")
except Exception as e:
    print(f"[ERROR] {e}")
    print(f"Response: {response_text}")

print("\n" + "="*60)
print("Response:", json.dumps(json.loads(response_text), indent=2))
print("="*60)
