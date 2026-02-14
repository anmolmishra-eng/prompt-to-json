import sys
sys.path.insert(0, r'c:\Users\Anmol\Desktop\Backend\backend')

from app.lm_adapter import lm_run
import asyncio

async def test_generate():
    print("Testing LM generation directly...")

    try:
        result = await lm_run(
            "Design a 3-bedroom residential building in Mumbai with 2000 sq ft area",
            {
                "user_id": "test",
                "city": "Mumbai",
                "context": {"plot_area": 2000}
            }
        )

        print(f"✅ Success!")
        print(f"Provider: {result.get('provider')}")
        print(f"Design type: {result['spec_json'].get('design_type')}")
        print(f"Objects: {len(result['spec_json'].get('objects', []))}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_generate())
