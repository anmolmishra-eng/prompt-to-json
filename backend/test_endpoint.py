#!/usr/bin/env python3
import json

import requests

# Test the upload-preview endpoint
url = "http://localhost:8000/api/v1/upload-preview"
params = {"spec_id": "spec_e30672ca"}
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2MzgxMjMzMn0.9ftXHcaHAo-cEepgZ02PC-N7LepW_TxqhFLCkfhxdRo"
}

# Create a fake JPG file
files = {"file": ("room.jpg", b"fake jpg data", "image/jpeg")}

try:
    response = requests.post(url, params=params, headers=headers, files=files)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", e)
