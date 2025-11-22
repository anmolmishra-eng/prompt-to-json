"""
Validate BHIV Assistant API code without running server
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

try:
    print("Validating BHIV Assistant API...")

    # Test imports
    print("\n[1/4] Testing imports...")
    from app.bhiv_layer.assistant_api import BHIVAssistant, DesignRequest
    from config.integration_config import IntegrationConfig

    print("[OK] All imports successful")

    # Test configuration
    print("\n[2/4] Testing configuration...")
    config = IntegrationConfig()
    print(f"[OK] Task 7 URL: {config.task7.base_url}")
    print(f"[OK] Sohum URL: {config.sohum.base_url}")
    print(f"[OK] Ranjeet URL: {config.ranjeet.base_url}")
    print(f"[OK] BHIV Port: {config.bhiv.api_port}")

    # Test assistant initialization
    print("\n[3/4] Testing assistant initialization...")
    assistant = BHIVAssistant()
    print("[OK] BHIV Assistant initialized")

    # Test request model
    print("\n[4/4] Testing request models...")
    request = DesignRequest(user_id="test_user", prompt="modern apartment", city="Mumbai", project_id="test_001")
    print(f"[OK] Request model: {request.user_id}, {request.city}")

    print("\n[SUCCESS] All validations passed!")
    print("[OK] BHIV Assistant API is ready to run")
    print("\nTo start the server:")
    print("  cd bhiv-assistant")
    print("  python app/main.py")

except Exception as e:
    print(f"[ERROR] Validation failed: {e}")
    import traceback

    traceback.print_exc()
