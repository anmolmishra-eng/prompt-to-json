#!/usr/bin/env python3
import subprocess
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("Testing Mobile Generate Endpoint with CURL")
print("="*60)

# Step 1: Authenticate
print("\n[1/4] Authenticating...")
auth_cmd = [
    'curl', '-X', 'POST',
    'http://localhost:8000/api/v1/auth/login',
    '-H', 'Content-Type: application/x-www-form-urlencoded',
    '-d', 'username=admin&password=bhiv2024',
    '-s'
]
auth_result = subprocess.run(auth_cmd, capture_output=True, text=True)
auth_data = json.loads(auth_result.stdout)
token = auth_data['access_token']
print(f"[OK] Token: {token[:20]}...")

# Step 2: Test mobile generate
print("\n[2/4] Testing mobile generate endpoint...")
payload = {
    "user_id": "mobile_test_user",
    "prompt": "Create a modern living room with minimalist furniture",
    "project_id": "proj_mobile_001",
    "context": {"device": "android"}
}

gen_cmd = [
    'curl', '-X', 'POST',
    'http://localhost:8000/api/v1/mobile/generate',
    '-H', f'Authorization: Bearer {token}',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(payload),
    '-s', '-w', '\\nHTTP_CODE:%{http_code}'
]

gen_result = subprocess.run(gen_cmd, capture_output=True, text=True)
output = gen_result.stdout

if 'HTTP_CODE:' in output:
    response_text, status = output.rsplit('HTTP_CODE:', 1)
    status_code = status.strip()
else:
    response_text = output
    status_code = 'unknown'

print(f"Status: {status_code}")

# Step 3: Save response
print("\n[3/4] Saving response locally...")
with open('mobile_response.json', 'w', encoding='utf-8') as f:
    f.write(response_text)
print(f"[OK] Saved to mobile_response.json")

# Step 4: Verify database
print("\n[4/4] Verifying database storage...")
try:
    response_data = json.loads(response_text)
    if 'spec_id' in response_data:
        spec_id = response_data['spec_id']
        print(f"[CHECK] Spec ID: {spec_id}")

        verify_cmd = [
            'curl', '-X', 'GET',
            f'http://localhost:8000/api/v1/specs/{spec_id}',
            '-H', f'Authorization: Bearer {token}',
            '-s'
        ]
        verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
        verify_data = json.loads(verify_result.stdout)

        if 'spec_id' in verify_data:
            print(f"[OK] Found in database")
            print(f"     User: {verify_data.get('user_id')}")
            print(f"     Cost: ₹{verify_data.get('estimated_cost', 0):,.0f}")
        else:
            print(f"[FAIL] Not found in database")
    else:
        print(f"[FAIL] No spec_id in response")
        print(f"Response: {response_text}")
except Exception as e:
    print(f"[ERROR] {e}")
    print(f"Response: {response_text}")

print("\n" + "="*60)
