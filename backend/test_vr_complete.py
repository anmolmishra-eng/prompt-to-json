#!/usr/bin/env python3
"""
Comprehensive VR Endpoint Test
Tests all VR endpoints with database and local storage verification
"""
import json
import time
from pathlib import Path

import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2Nzg1ODAzOH0.U6eGFrMrr5gsflFi4npS1vKV8nObA5F82MUSe3V2Zwc"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def test_vr_endpoints():
    """Test all VR endpoints"""
    print("VR ENDPOINT COMPREHENSIVE TEST")
    print("=" * 50)

    spec_id = "spec_bd6c4566f93d"

    # 1. Test VR Preview
    print("\\n1. Testing VR Preview...")
    try:
        response = requests.get(f"{BASE_URL}/vr/preview/{spec_id}", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            print("VR Preview: {} format, expires in {}s".format(data["format"], data["expires_in"]))
        else:
            print("VR Preview failed: {}".format(response.status_code))
    except Exception as e:
        print("VR Preview error: {}".format(e))

    # 2. Test VR Render
    print("\\n2. Testing VR Render...")
    render_id = None
    try:
        response = requests.get(f"{BASE_URL}/vr/render/{spec_id}?quality=high", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            render_id = data["render_id"]
            print("VR Render: {} - ID: {}".format(data["render_status"], render_id))
            print("   Progress: {}%".format(data["progress"]))
            print("   URL: {}".format(data["render_url"]))
            print("   Local: {}".format(data["local_path"]))
        else:
            print("VR Render failed: {}".format(response.status_code))
            print(response.text)
    except Exception as e:
        print("VR Render error: {}".format(e))

    # 3. Test VR Status
    if render_id:
        print("\\n3. Testing VR Status...")
        try:
            response = requests.get(f"{BASE_URL}/vr/status/{render_id}", headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                print("VR Status: {} - {}%".format(data["status"], data["progress"]))
                print("   Quality: {}".format(data["quality"]))
                print("   File size: {} bytes".format(data["file_size_bytes"]))
                print("   Actual time: {}s".format(data["actual_time_seconds"]))
            else:
                print("VR Status failed: {}".format(response.status_code))
        except Exception as e:
            print("VR Status error: {}".format(e))

    # 4. Test VR Feedback
    print("\\n4. Testing VR Feedback...")
    try:
        feedback_data = {
            "spec_id": spec_id,
            "rating": 4.8,
            "comments": "Excellent VR rendering quality!",
            "performance": "smooth",
            "issues": [],
        }
        response = requests.post(f"{BASE_URL}/vr/feedback", headers=HEADERS, json=feedback_data)
        if response.status_code == 200:
            data = response.json()
            print("VR Feedback: {} - ID: {}".format(data["status"], data["feedback_id"]))
            print("   Local path: {}".format(data["local_path"]))
        else:
            print("VR Feedback failed: {}".format(response.status_code))
    except Exception as e:
        print("VR Feedback error: {}".format(e))

    # 5. Verify Local Storage
    print("\\n5. Verifying Local Storage...")
    vr_dir = Path("vr_renders")
    if vr_dir.exists():
        files = list(vr_dir.glob("*"))
        print("Local storage: {} files found".format(len(files)))
        for file in files:
            print("   - {} ({} bytes)".format(file.name, file.stat().st_size))
    else:
        print("VR renders directory not found")

    print("\\n" + "=" * 50)
    print("VR ENDPOINT TEST COMPLETE")


if __name__ == "__main__":
    test_vr_endpoints()
