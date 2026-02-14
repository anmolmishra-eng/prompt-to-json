import requests
import json
import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

# Database connection
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bhiv_db")

print("="*60)
print("🎨 TESTING /api/v1/generate ENDPOINT")
print("="*60)

# Step 1: Register admin user
print("\n1️⃣ Registering admin user...")
try:
    register = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin",
            "full_name": "Admin User"
        }
    )
    if register.status_code in [200, 201]:
        print("✅ Admin registered")
    else:
        print(f"⚠️ Register response: {register.status_code} - {register.text}")
except Exception as e:
    print(f"⚠️ Register failed (user may exist): {e}")

# Step 2: Login
print("\n2️⃣ Logging in...")
login = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    data={"username": "admin", "password": "admin"}
)
if login.status_code != 200:
    print(f"❌ Login failed: {login.status_code} - {login.text}")
    exit(1)

token = login.json()["access_token"]
print(f"✅ Logged in, token: {token[:20]}...")

# Step 3: Test generate
print("\n3️⃣ Testing generate endpoint...")
response = requests.post(
    f"{BASE_URL}/api/v1/generate",
    headers={"Authorization": f"Bearer {token}"},
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

print(f"\n📊 Response Status: {response.status_code}")
print(f"\n📄 Response Body:")
print(json.dumps(response.json() if response.status_code == 201 else {"error": response.text}, indent=2))

if response.status_code == 201:
    data = response.json()
    spec_id = data.get('spec_id')

    print("\n" + "="*60)
    print("✅ SUCCESS! Design generated")
    print("="*60)
    print(f"\n📋 Spec ID: {spec_id}")
    print(f"💰 Cost: ₹{data.get('estimated_cost'):,.0f}")
    print(f"🔗 Preview URL: {data.get('preview_url')}")
    print(f"✅ Compliance Check ID: {data.get('compliance_check_id')}")
    print(f"📅 Created At: {data.get('created_at')}")

    # Step 4: Verify database storage
    print("\n4️⃣ Verifying database storage...")
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, user_id, prompt, city, estimated_cost, created_at FROM specs WHERE id = :spec_id"),
                {"spec_id": spec_id}
            )
            row = result.fetchone()

            if row:
                print("✅ Spec found in database!")
                print(f"   - ID: {row[0]}")
                print(f"   - User ID: {row[1]}")
                print(f"   - Prompt: {row[2][:50]}...")
                print(f"   - City: {row[3]}")
                print(f"   - Cost: ₹{row[4]:,.0f}")
                print(f"   - Created: {row[5]}")
            else:
                print("❌ Spec NOT found in database!")
    except Exception as e:
        print(f"⚠️ Database verification failed: {e}")

    # Step 5: Verify local file storage
    print("\n5️⃣ Verifying local file storage...")
    local_paths = [
        f"backend/data/specs/{spec_id}.json",
        f"data/specs/{spec_id}.json",
        f"backend/data/geometry_outputs/{spec_id}.glb",
        f"data/geometry_outputs/{spec_id}.glb"
    ]

    found_files = []
    for path in local_paths:
        if os.path.exists(path):
            found_files.append(path)
            size = os.path.getsize(path)
            print(f"✅ Found: {path} ({size} bytes)")

    if not found_files:
        print("⚠️ No local files found (may be using cloud storage only)")

    # Step 6: Test retrieval
    print("\n6️⃣ Testing spec retrieval...")
    get_response = requests.get(
        f"{BASE_URL}/api/v1/specs/{spec_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    if get_response.status_code == 200:
        print("✅ Spec retrieved successfully!")
        retrieved_data = get_response.json()
        print(f"   - Spec ID matches: {retrieved_data.get('spec_id') == spec_id}")
        print(f"   - Cost matches: {retrieved_data.get('estimated_cost') == data.get('estimated_cost')}")
    else:
        print(f"❌ Retrieval failed: {get_response.status_code}")

    print("\n" + "="*60)
    print("🎉 ALL TESTS COMPLETED")
    print("="*60)
else:
    print("\n" + "="*60)
    print("❌ GENERATION FAILED!")
    print("="*60)
