"""
Test Supabase storage upload
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_supabase_upload():
    try:
        from app.config import settings
        from supabase import create_client

        print(f"Supabase URL: {settings.SUPABASE_URL}")
        print(f"Supabase Key: {settings.SUPABASE_KEY[:20]}...")

        # Create client
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print("Supabase client created")

        # List buckets
        try:
            buckets = supabase.storage.list_buckets()
            print(f"Buckets found: {[b.name for b in buckets]}")
        except Exception as e:
            print(f"Bucket list failed: {e}")

        # Test upload
        from app.geometry_generator_real import generate_real_glb

        spec = {"objects": [{"id": "test", "type": "cabinet", "dimensions": {"width": 1, "depth": 1, "height": 1}}]}

        glb_data = generate_real_glb(spec)
        print(f"Generated GLB: {len(glb_data)} bytes")

        # Upload to geometry bucket
        try:
            result = supabase.storage.from_("geometry").upload(
                "test_upload.glb", glb_data, file_options={"content-type": "model/gltf-binary"}
            )
            print(f"Upload result: {result}")

            # Get public URL
            url = supabase.storage.from_("geometry").get_public_url("test_upload.glb")
            print(f"SUCCESS: File uploaded to {url}")

            return True

        except Exception as e:
            print(f"Upload failed: {e}")
            return False

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing Supabase Upload...")
    success = test_supabase_upload()
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
