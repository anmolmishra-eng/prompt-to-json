import requests

# Use the token from Swagger UI
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc3MDg5MTczMX0.JON0ifNQt3xAYyJg6fwkkKStBXtYIE9jRLdxESkAcT4"

response = requests.post(
    "http://127.0.0.1:8000/api/v1/generate",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={
        "user_id": "admin",
        "prompt": "Design a 3-bedroom residential building in Mumbai with 2000 sq ft area",
        "project_id": "proj_001",
        "context": {
            "city": "Mumbai",
            "plot_area": 2000,
            "building_type": "residential"
        }
    }
)

print(f"Status: {response.status_code}")
print(f"Response:\n{response.text}")
