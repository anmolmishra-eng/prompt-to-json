"""
Simple schema verification
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_schema_fields():
    """Test schema fields"""
    print("Testing Schema Fields...")

    try:
        from app.schemas import GenerateRequest, GenerateResponse

        # Test with sample data
        sample_request = {
            "user_id": "user_123",
            "prompt": "Modern 2BHK apartment with open kitchen and balcony",
            "city": "Mumbai",
            "constraints": {"budget": 5000000},
            "style": "modern"
        }

        request = GenerateRequest(**sample_request)
        print(f"SUCCESS: GenerateRequest created with city: {request.city}")

        # Test response
        sample_response = {
            "spec_id": "spec_123",
            "spec_json": {"objects": []},
            "preview_url": "https://example.com/preview.glb",
            "created_at": "2024-11-25T12:00:00Z",
            "spec_version": 1,
            "user_id": "user_123",
            "estimated_cost": 150000.0,
            "city": "Mumbai"
        }

        response = GenerateResponse(**sample_response)
        print(f"SUCCESS: GenerateResponse created with cost: {response.estimated_cost}")

        return True

    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_schema_fields()
    print(f"\nResult: {'PASS' if success else 'FAIL'}")

    if success:
        print("Schemas are working correctly with enhanced fields!")
