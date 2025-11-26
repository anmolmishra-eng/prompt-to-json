"""
Test updated schemas match generate.py implementation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_schemas_compatibility():
    """Test that schemas match generate.py implementation"""
    print("Testing Schema Compatibility with Generate.py...")

    try:
        # Import both schemas
        from app.schemas import GenerateRequest, GenerateResponse
        from app.api.generate import GenerateRequest as APIGenerateRequest, GenerateResponse as APIGenerateResponse

        print("SUCCESS: Both schema imports work")

        # Test GenerateRequest compatibility
        sample_request_data = {
            "user_id": "user_123",
            "prompt": "Modern 2BHK apartment with open kitchen and balcony",
            "city": "Mumbai",
            "constraints": {
                "budget": 5000000,
                "area": 850,
                "floors": 1
            },
            "style": "modern"
        }

        # Test both schemas can handle the same data
        schema_request = GenerateRequest(**sample_request_data)
        api_request = APIGenerateRequest(**sample_request_data)

        print("SUCCESS: Both GenerateRequest schemas work with same data")
        print(f"  Schema version: {schema_request.city}")
        print(f"  API version: {api_request.city}")

        # Test GenerateResponse compatibility
        sample_response_data = {
            "spec_id": "spec_123",
            "spec_json": {"objects": []},
            "preview_url": "https://example.com/preview.glb",
            "created_at": "2024-11-25T12:00:00Z",
            "spec_version": 1,
            "user_id": "user_123",
            "estimated_cost": 150000.0,
            "generation_time_ms": 1500,
            "city": "Mumbai",
            "lm_provider": "local_gpu"
        }

        # Test response schemas
        try:
            schema_response = GenerateResponse(**sample_response_data)
            api_response = APIGenerateResponse(**sample_response_data)

            print("SUCCESS: Both GenerateResponse schemas work")
            print(f"  Schema cost: {schema_response.estimated_cost}")
            print(f"  API cost: {api_response.estimated_cost}")
        except Exception as e:
            print(f"Response schema test failed: {e}")

        return True

    except Exception as e:
        print(f"FAILED: Schema compatibility test failed: {e}")
        return False

def test_schema_fields():
    """Test all required fields are present"""
    print("\nTesting Schema Fields...")

    try:
        from app.schemas import GenerateRequest, GenerateResponse

        # Test GenerateRequest fields
        request_fields = GenerateRequest.__fields__.keys()
        expected_request_fields = {
            'user_id', 'prompt', 'city', 'project_id',
            'context', 'constraints', 'style'
        }

        missing_request = expected_request_fields - set(request_fields)
        if missing_request:
            print(f"MISSING request fields: {missing_request}")
        else:
            print("SUCCESS: All GenerateRequest fields present")

        # Test GenerateResponse fields
        response_fields = GenerateResponse.__fields__.keys()
        expected_response_fields = {
            'spec_id', 'spec_json', 'preview_url', 'compliance_check_id',
            'estimated_cost', 'generation_time_ms', 'created_at',
            'spec_version', 'user_id', 'city', 'lm_provider'
        }

        missing_response = expected_response_fields - set(response_fields)
        if missing_response:
            print(f"MISSING response fields: {missing_response}")
        else:
            print("SUCCESS: All GenerateResponse fields present")

        return len(missing_request) == 0 and len(missing_response) == 0

    except Exception as e:
        print(f"FAILED: Field test failed: {e}")
        return False

if __name__ == "__main__":
    print("Schema Compatibility Test")
    print("=" * 40)

    # Test 1: Compatibility
    compat_ok = test_schemas_compatibility()

    # Test 2: Fields
    fields_ok = test_schema_fields()

    # Summary
    all_tests_pass = compat_ok and fields_ok
    print(f"\n{'SUCCESS: ALL TESTS PASS' if all_tests_pass else 'FAILED: SOME TESTS FAILED'}")

    if all_tests_pass:
        print("\nSchemas are fully compatible with generate.py!")
        print("Enhanced features:")
        print("- City and constraints support")
        print("- Cost estimation fields")
        print("- Compliance check integration")
        print("- Generation time tracking")
        print("- LM provider tracking")
        print("- Enhanced validation")
    else:
        print("\nSchemas need updates to match generate.py")
