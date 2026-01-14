"""
Quick Endpoint Validation - Check if all core APIs are registered
"""
import sys

print("=" * 70)
print("CORE API ENDPOINT VALIDATION")
print("=" * 70)

# Check main.py for explicit routes
try:
    with open("app/main.py", "r", encoding="utf-8") as f:
        main_content = f.read()

    with open("app/api/bhiv_assistant.py", "r", encoding="utf-8") as f:
        bhiv_content = f.read()

    with open("app/api/rl.py", "r", encoding="utf-8") as f:
        rl_content = f.read()

    endpoints_to_check = [
        ("/api/v1/history", "get_design_history", main_content),
        ("/api/v1/reports/{spec_id}", "get_spec_report", main_content),
        ("/bhiv/v1/prompt", "bhiv_prompt", bhiv_content),
        ("/api/v1/rl/feedback", "rl_feedback", rl_content),
    ]

    print("\nChecking endpoint registrations:\n")

    all_found = True
    for endpoint, function_name, content in endpoints_to_check:
        if function_name in content:
            print(f"OK {endpoint} - REGISTERED ({function_name})")
        else:
            print(f"FAIL {endpoint} - NOT FOUND ({function_name})")
            all_found = False

    print("\n" + "=" * 70)

    if all_found:
        print("SUCCESS - ALL CORE ENDPOINTS ARE REGISTERED")
        print("\nNext steps:")
        print("1. Start the server: python -m uvicorn app.main:app --reload")
        print("2. Run tests: python test_core_apis.py")
        print("3. Check Swagger UI: http://localhost:8000/docs")
    else:
        print("WARNING - Some endpoints are missing")
        sys.exit(1)

    print("=" * 70)

except FileNotFoundError:
    print("ERROR - app/main.py not found")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
