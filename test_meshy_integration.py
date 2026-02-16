"""Test Meshy AI Integration"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_meshy():
    from app.meshy_3d_generator import generate_3d_with_meshy

    prompt = "Modern 3BHK apartment with marble flooring and modular kitchen"
    dimensions = {"width": 12, "length": 10, "height": 3}

    print("🚀 Testing Meshy AI Integration")
    print(f"📝 Prompt: {prompt}")
    print(f"📐 Dimensions: {dimensions}")
    print("⏳ Generating 3D model (this takes 1-2 minutes)...\n")

    try:
        result = await generate_3d_with_meshy(prompt, dimensions)

        if result:
            print(f"✅ SUCCESS! Generated {len(result):,} bytes")

            # Save to file
            output_file = "test_meshy_output.glb"
            with open(output_file, "wb") as f:
                f.write(result)
            print(f"💾 Saved to: {output_file}")
            print("\n🎉 Meshy AI integration is working!")
        else:
            print("❌ FAILED: No content returned")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_meshy())
