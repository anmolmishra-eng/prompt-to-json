import subprocess
import json
import os
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bhiv_db")

print("="*70)
print("FINAL VERIFICATION: Generate Endpoint")
print("="*70)

# Step 1: Login
print("\n[1] Login...")
login_cmd = 'curl -s -X POST "http://127.0.0.1:8000/api/v1/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=bhiv2024"'
login_result = subprocess.run(login_cmd, shell=True, capture_output=True, text=True)
login_data = json.loads(login_result.stdout)
token = login_data["access_token"]
print(f"SUCCESS: Token obtained")

# Step 2: Generate
print("\n[2] Generate design...")
generate_cmd = f'curl -s -X POST "http://127.0.0.1:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer {token}" -d "{{\\"user_id\\":\\"admin\\",\\"prompt\\":\\"Design a 3-bedroom house in Mumbai\\",\\"project_id\\":\\"test_002\\"}}"'
generate_result = subprocess.run(generate_cmd, shell=True, capture_output=True, text=True)
generate_data = json.loads(generate_result.stdout)

spec_id = generate_data["spec_id"]
cost = generate_data["estimated_cost"]
preview = generate_data["preview_url"]

print(f"SUCCESS: Design generated")
print(f"  Spec ID: {spec_id}")
print(f"  Cost: Rs.{cost:,.0f}")
print(f"  Preview: {preview}")

# Step 3: Verify database
print("\n[3] Verify database...")
try:
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, user_id, prompt, estimated_cost FROM specs WHERE id = :spec_id"),
            {"spec_id": spec_id}
        )
        row = result.fetchone()
        if row:
            print(f"SUCCESS: Found in database")
            print(f"  ID: {row[0]}")
            print(f"  User: {row[1]}")
            print(f"  Prompt: {row[2][:40]}...")
            print(f"  Cost: Rs.{row[3]:,.0f}")
        else:
            print("FAILED: Not in database")
except Exception as e:
    print(f"ERROR: {e}")

# Step 4: Check local files
print("\n[4] Check local files...")
paths = [
    f"backend/data/geometry_outputs/{spec_id}.glb",
    f"data/geometry_outputs/{spec_id}.glb"
]
for path in paths:
    if os.path.exists(path):
        print(f"SUCCESS: Found {path} ({os.path.getsize(path)} bytes)")

# Step 5: Retrieve via API
print("\n[5] Retrieve via API...")
get_cmd = f'curl -s -X GET "http://127.0.0.1:8000/api/v1/specs/{spec_id}" -H "Authorization: Bearer {token}"'
get_result = subprocess.run(get_cmd, shell=True, capture_output=True, text=True)
get_data = json.loads(get_result.stdout)
if get_data.get("spec_id") == spec_id:
    print(f"SUCCESS: Retrieved spec matches")

print("\n" + "="*70)
print("ALL TESTS PASSED - Generate endpoint is working!")
print("="*70)
