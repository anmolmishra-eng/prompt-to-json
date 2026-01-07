#!/usr/bin/env python3
import subprocess
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Authenticate
auth_cmd = ['curl', '-X', 'POST', 'http://localhost:8000/api/v1/auth/login',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-d', 'username=admin&password=bhiv2024', '-s']
auth_result = subprocess.run(auth_cmd, capture_output=True, text=True)
token = json.loads(auth_result.stdout)['access_token']

# Test regular switch
payload = {
    "user_id": "mobile_test_user",
    "spec_id": "spec_bd6c4566f93d",
    "target": {"object_id": "sofa"},
    "update": {"material": "velvet", "color_hex": "#4B0082"},
    "note": "Changed to velvet",
    "expected_version": 1
}

switch_cmd = ['curl', '-X', 'POST', 'http://localhost:8000/api/v1/switch',
              '-H', f'Authorization: Bearer {token}',
              '-H', 'Content-Type: application/json',
              '-d', json.dumps(payload), '-s']

result = subprocess.run(switch_cmd, capture_output=True, text=True)
print(json.dumps(json.loads(result.stdout), indent=2))
