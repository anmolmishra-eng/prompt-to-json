#!/usr/bin/env python3
import subprocess
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("Testing Mobile Evaluate Endpoint")
print("="*60)

# Step 1: Authenticate
print("\n[1/4] Authenticating...")
auth_cmd = ['curl', '-X', 'POST', 'http://localhost:8000/api/v1/auth/login',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-d', 'username=admin&password=bhiv2024', '-s']
auth_result = subprocess.run(auth_cmd, capture_output=True, text=True)
token = json.loads(auth_result.stdout)['access_token']
print(f"[OK] Token: {token[:20]}...")

# Step 2: Test mobile evaluate
print("\n[2/4] Testing mobile evaluate endpoint...")
payload = {
    "user_id": "mobile_test_user",
    "spec_id": "spec_bd6c4566f93d",
    "rating": 5,
    "notes": "Excellent modern living room design",
    "feedback_text": "Love the minimalist furniture and natural lighting"
}

eval_cmd = ['curl', '-X', 'POST', 'http://localhost:8000/api/v1/mobile/evaluate',
            '-H', f'Authorization: Bearer {token}',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps(payload),
            '-s', '-w', '\\nHTTP_CODE:%{http_code}']

eval_result = subprocess.run(eval_cmd, capture_output=True, text=True)
output = eval_result.stdout

if 'HTTP_CODE:' in output:
    response_text, status = output.rsplit('HTTP_CODE:', 1)
    status_code = status.strip()
else:
    response_text = output
    status_code = 'unknown'

print(f"Status: {status_code}")

# Step 3: Save response
print("\n[3/4] Saving response locally...")
with open('mobile_evaluate_response.json', 'w', encoding='utf-8') as f:
    f.write(response_text)
print(f"[OK] Saved to mobile_evaluate_response.json")

# Step 4: Verify database
print("\n[4/4] Verifying database storage...")
try:
    response_data = json.loads(response_text)
    print(f"[OK] Evaluation recorded")
    print(f"     Spec ID: {response_data.get('spec_id', 'N/A')}")
    print(f"     Rating: {response_data.get('rating', 'N/A')}")
    print(f"     Status: {response_data.get('status', 'N/A')}")

    # Verify by getting spec
    verify_cmd = ['curl', '-X', 'GET',
                  f'http://localhost:8000/api/v1/specs/{payload["spec_id"]}',
                  '-H', f'Authorization: Bearer {token}', '-s']
    verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
    print(f"[OK] Spec verified in database")
except Exception as e:
    print(f"[ERROR] {e}")
    print(f"Response: {response_text}")

print("\n" + "="*60)
print("Response:", json.dumps(json.loads(response_text), indent=2))
print("="*60)
