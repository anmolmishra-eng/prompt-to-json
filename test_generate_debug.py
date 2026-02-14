import requests
import traceback

# Get token
try:
    login = requests.post(
        "http://127.0.0.1:8000/api/v1/auth/login",
        data={"username": "admin", "password": "admin"}
    )
    token = login.json()["access_token"]
    print(f"✅ Got token: {token[:20]}...")
except Exception as e:
    print(f"❌ Login failed: {e}")
    exit(1)

# Test generate
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": "user123",
            "prompt": "Design a 3-bedroom residential building in Mumbai with 2000 sq ft area",
            "project_id": "proj_001",
            "context": {
                "city": "Mumbai",
                "plot_area": 2000,
                "building_type": "residential"
            }
        }
    )

    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📄 Response Headers: {dict(response.headers)}")
    print(f"📝 Response Body:\n{response.text}\n")

    if response.status_code == 201:
        print("✅ SUCCESS!")
        print(response.json())
    else:
        print("❌ FAILED!")

except Exception as e:
    print(f"❌ Request failed: {e}")
    traceback.print_exc()
