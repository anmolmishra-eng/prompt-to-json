"""Test Meshy AI Integration"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('backend/.env')

async def test_meshy():
    from app.meshy_3d_generator import generate_3d_with_meshy

    prompt = "Modern 3BHK apartment with marble flooring and modular kitchen"
    dimensions = {"width": 12, "length": 10, "height": 3}

    print("=" * 60)
    print("TESTING MESHY AI INTEGRATION")
    print("=" * 60)
    print(f"Prompt: {prompt}")
    print(f"Dimensions: {dimensions}")
    print()
    print("Generating 3D model (this takes 1-2 minutes)...")
    print("Please wait...")
    print()

    try:
        result = await generate_3d_with_meshy(prompt, dimensions)

        if result:
            print("=" * 60)
            print(f"SUCCESS! Generated {len(result):,} bytes")
            print("=" * 60)

            # Save to file
            output_file = "test_meshy_output.glb"
            with open(output_file, "wb") as f:
                f.write(result)
            print(f"Saved to: {output_file}")
            print()
            print("Meshy AI integration is working!")
            return True
        else:
            print("=" * 60)
            print("FAILED: No content returned")
            print("=" * 60)
            return False

    except Exception as e:
        print("=" * 60)
        print(f"ERROR: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_meshy())
    sys.exit(0 if success else 1)
