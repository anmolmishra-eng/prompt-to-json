import subprocess
import json
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bhiv_db")

print("="*70)
print("CURL TEST: /api/v1/generate Endpoint Verification")
print("="*70)

# Step 1: Login
print("\nStep 1: Login with curl...")
login_cmd = 'curl -s -X POST "http://127.0.0.1:8000/api/v1/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=bhiv2024"'
login_result = subprocess.run(login_cmd, shell=True, capture_output=True, text=True)

try:
    login_data = json.loads(login_result.stdout)
    token = login_data.get("access_token")
    if token:
        print(f"SUCCESS: Token obtained")
    else:
        print("FAILED: No token in response")
        print(f"Response: {login_result.stdout}")
        exit(1)
except Exception as e:
    print(f"FAILED: Login error - {e}")
    print(f"Response: {login_result.stdout}")
    exit(1)

# Step 2: Generate design
print("\nStep 2: Generate design with curl...")
generate_cmd = f'curl -s -X POST "http://127.0.0.1:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer {token}" -d "{{\\"user_id\\":\\"admin\\",\\"prompt\\":\\"Design a modern 2BHK apartment\\",\\"project_id\\":\\"test_001\\"}}"'

generate_result = subprocess.run(generate_cmd, shell=True, capture_output=True, text=True)

try:
    generate_data = json.loads(generate_result.stdout)

    if "error" in generate_data:
        print(f"FAILED: {generate_data['error']}")
        exit(1)

    spec_id = generate_data.get("spec_id")
    estimated_cost = generate_data.get("estimated_cost", 0)
    preview_url = generate_data.get("preview_url")

    print(f"SUCCESS: Design generated!")
    print(f"  Spec ID: {spec_id}")
    print(f"  Cost: Rs.{estimated_cost:,.0f}")
    print(f"  Preview: {preview_url}")

except Exception as e:
    print(f"FAILED: Parse error - {e}")
    print(f"Response: {generate_result.stdout}")
    exit(1)

# Step 3: Verify database
print("\nStep 3: Verify database storage...")
try:
    from sqlalchemy import create_engine, text
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, user_id, prompt, estimated_cost FROM specs WHERE id = :spec_id"),
            {"spec_id": spec_id}
        )
        row = result.fetchone()

        if row:
            print(f"SUCCESS: Found in database!")
            print(f"  ID: {row[0]}")
            print(f"  User: {row[1]}")
            print(f"  Prompt: {row[2][:40]}...")
        else:
            print("FAILED: NOT found in database!")
except Exception as e:
    print(f"WARNING: Database check failed - {e}")

# Step 4: Verify local files
print("\nStep 4: Verify local file storage...")
paths_to_check = [
    f"backend/data/specs/{spec_id}.json",
    f"data/specs/{spec_id}.json",
    f"backend/data/geometry_outputs/{spec_id}.glb",
    f"data/geometry_outputs/{spec_id}.glb"
]

found = False
for path in paths_to_check:
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"SUCCESS: Found {path} ({size} bytes)")
        found = True

if not found:
    print("WARNING: No local files found (may be cloud-only)")

# Step 5: Retrieve spec
print("\nStep 5: Retrieve spec via API...")
get_cmd = f'curl -s -X GET "http://127.0.0.1:8000/api/v1/specs/{spec_id}" -H "Authorization: Bearer {token}"'
get_result = subprocess.run(get_cmd, shell=True, capture_output=True, text=True)

try:
    get_data = json.loads(get_result.stdout)
    if get_data.get("spec_id") == spec_id:
        print(f"SUCCESS: Spec retrieved successfully!")
    else:
        print(f"FAILED: Retrieval failed")
except:
    print(f"FAILED: Retrieval parse failed")
    print(f"Response: {get_result.stdout[:200]}")

print("\n" + "="*70)
print("CURL TEST COMPLETED")
print("="*70)
