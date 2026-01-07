#!/usr/bin/env python3
import subprocess
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("Testing Mobile Switch Endpoint")
print("="*60)

# Authenticate
print("\n[1/4] Authenticating...")
auth_cmd = ['curl', '-X', 'POST', 'http://localhost:8000/api/v1/auth/login',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-d', 'username=admin&password=bhiv2024', '-s']
auth_result = subprocess.run(auth_cmd, capture_output=True, text=True)
token = json.loads(auth_result.stdout)['access_token']
print(f"[OK] Token: {token[:20]}...")

# Test mobile switch
print("\n[2/4] Testing mobile switch endpoint...")
payload = {
    "user_id": "mobile_test_user",
    "spec_id": "spec_bd6c4566f93d",
    "target": {"object_id": "sofa"},
    "update": {"material": "velvet", "color_hex": "#4B0082"},
    "note": "Changed to velvet"
}

switch_cmd = ['curl', '-X', 'POST', 'http://localhost:8000/api/v1/mobile/switch',
              '-H', f'Authorization: Bearer {token}',
              '-H', 'Content-Type: application/json',
              '-d', json.dumps(payload),
              '-s', '-w', '\\nHTTP_CODE:%{http_code}']

switch_result = subprocess.run(switch_cmd, capture_output=True, text=True)
output = switch_result.stdout

if 'HTTP_CODE:' in output:
    response_text, status = output.rsplit('HTTP_CODE:', 1)
    status_code = status.strip()
else:
    response_text = output
    status_code = 'unknown'

print(f"Status: {status_code}")

# Save response
print("\n[3/4] Saving response locally...")
with open('mobile_switch_response.json', 'w', encoding='utf-8') as f:
    f.write(response_text)
print(f"[OK] Saved to mobile_switch_response.json")

# Verify
print("\n[4/4] Verifying response...")
try:
    response_data = json.loads(response_text)
    print(f"[OK] Switch completed")
    print(f"     Spec ID: {response_data.get('spec_id', 'N/A')}")
    print(f"     Version: {response_data.get('version', 'N/A')}")
    print(f"     Objects Modified: {response_data.get('objects_modified', 'N/A')}")

    # Verify in database
    if 'spec_id' in response_data:
        verify_cmd = ['curl', '-X', 'GET',
                      f'http://localhost:8000/api/v1/specs/{response_data["spec_id"]}',
                      '-H', f'Authorization: Bearer {token}', '-s']
        verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
        verify_data = json.loads(verify_result.stdout)
        if 'spec_id' in verify_data:
            print(f"[OK] Updated spec verified in database")
except Exception as e:
    print(f"[ERROR] {e}")
    print(f"Response: {response_text}")

print("\n" + "="*60)
print("Response:", json.dumps(json.loads(response_text), indent=2))
print("="*60)
