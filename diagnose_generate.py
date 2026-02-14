import sys
import traceback
sys.path.insert(0, 'backend')

print("="*70)
print("DIAGNOSING GENERATE ENDPOINT FAILURE")
print("="*70)

# Test 1: Check database connection
print("\n[1] Testing database connection...")
try:
    from sqlalchemy import text
    from app.database import SessionLocal
    db = SessionLocal()
    result = db.execute(text("SELECT 1"))
    db.close()
    print("SUCCESS: Database connection OK")
except Exception as e:
    print(f"FAILED: Database connection - {e}")

# Test 2: Check LM adapter
print("\n[2] Testing LM adapter...")
try:
    import asyncio
    from app.lm_adapter import lm_run

    async def test_lm():
        result = await lm_run("Design a simple kitchen", {"user_id": "test"})
        return result

    result = asyncio.run(test_lm())
    print(f"SUCCESS: LM adapter OK - Provider: {result.get('provider')}")
    print(f"  Design type: {result.get('spec_json', {}).get('design_type')}")
except Exception as e:
    print(f"FAILED: LM adapter - {e}")
    traceback.print_exc()

# Test 3: Check storage
print("\n[3] Testing storage...")
try:
    from app.spec_storage import save_spec, get_spec
    test_data = {"test": "data"}
    save_spec("test_123", test_data)
    retrieved = get_spec("test_123")
    if retrieved:
        print("SUCCESS: In-memory storage OK")
    else:
        print("FAILED: Storage retrieval failed")
except Exception as e:
    print(f"FAILED: Storage - {e}")

# Test 4: Check models
print("\n[4] Testing database models...")
try:
    from app.models import User, Spec
    from app.database import SessionLocal
    db = SessionLocal()
    user_count = db.query(User).count()
    spec_count = db.query(Spec).count()
    db.close()
    print(f"SUCCESS: Models OK - Users: {user_count}, Specs: {spec_count}")
except Exception as e:
    print(f"FAILED: Models - {e}")

# Test 5: Direct generate function test
print("\n[5] Testing generate function directly...")
try:
    from app.schemas import GenerateRequest
    from app.api.generate import generate_design
    import asyncio

    async def test_generate():
        request = GenerateRequest(
            user_id="admin",
            prompt="Design a simple kitchen",
            project_id="test_001"
        )
        result = await generate_design(request)
        return result

    result = asyncio.run(test_generate())
    print(f"SUCCESS: Generate function OK")
    print(f"  Spec ID: {result.spec_id}")
    print(f"  Cost: Rs.{result.estimated_cost:,.0f}")
except Exception as e:
    print(f"FAILED: Generate function - {e}")
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "="*70)
print("DIAGNOSIS COMPLETE")
print("="*70)
