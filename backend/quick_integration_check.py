#!/usr/bin/env python3
"""
Quick Integration Check - No External Calls
Validates integration setup without making slow HTTP requests
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def check_imports():
    """Check if all integration modules can be imported"""
    print("🔍 CHECKING IMPORTS...")

    try:
        from app.external_services import ranjeet_client, service_manager, sohum_client

        print("   ✅ External services module imported")
    except Exception as e:
        print(f"   ❌ External services import failed: {e}")
        return False

    try:
        from app.prefect_integration_enhanced import check_workflow_status, trigger_pdf_workflow

        print("   ✅ Enhanced Prefect integration imported")
    except Exception as e:
        print(f"   ❌ Prefect integration import failed: {e}")
        return False

    try:
        from app.api.workflow_management import router

        print("   ✅ Workflow management API imported")
    except Exception as e:
        print(f"   ❌ Workflow management API import failed: {e}")
        return False

    try:
        from app.api.bhiv_integrated import call_ranjeet_rl, call_sohum_compliance

        print("   ✅ BHIV integrated API imported")
    except Exception as e:
        print(f"   ❌ BHIV integrated API import failed: {e}")
        return False

    return True


def check_configuration():
    """Check configuration setup"""
    print("\n⚙️ CHECKING CONFIGURATION...")

    try:
        from app.config import settings

        # Check external service URLs
        sohum_url = getattr(settings, "SOHUM_MCP_URL", None)
        ranjeet_url = getattr(settings, "RANJEET_RL_URL", None)

        print(f"   Sohum MCP URL: {sohum_url}")
        print(f"   Ranjeet RL URL: {ranjeet_url}")

        if sohum_url:
            print("   ✅ Sohum MCP configured")
        else:
            print("   ⚠️  Sohum MCP URL not configured")

        if ranjeet_url:
            print("   ✅ Ranjeet RL configured")
        else:
            print("   ⚠️  Ranjeet RL URL not configured")

        return True

    except Exception as e:
        print(f"   ❌ Configuration check failed: {e}")
        return False


def check_mock_responses():
    """Test mock response generation"""
    print("\n🎭 CHECKING MOCK RESPONSES...")

    try:
        from app.external_services import ranjeet_client, sohum_client

        # Test Sohum mock response
        test_case = {"city": "Mumbai", "project_id": "test_001"}
        mock_compliance = sohum_client.get_mock_compliance_response(test_case)

        if mock_compliance.get("case_id"):
            print("   ✅ Sohum mock response generated")
        else:
            print("   ❌ Sohum mock response failed")
            return False

        # Test Ranjeet mock response
        test_spec = {"objects": [{"id": "test", "type": "room"}]}
        mock_rl = ranjeet_client.get_mock_rl_response(test_spec, "Mumbai")

        if mock_rl.get("confidence"):
            print("   ✅ Ranjeet mock response generated")
        else:
            print("   ❌ Ranjeet mock response failed")
            return False

        return True

    except Exception as e:
        print(f"   ❌ Mock response check failed: {e}")
        return False


def check_workflow_setup():
    """Check workflow system setup"""
    print("\n🔄 CHECKING WORKFLOW SETUP...")

    try:
        from app.prefect_integration_enhanced import PREFECT_AVAILABLE, PREFECT_CONFIGURED

        print(f"   Prefect Available: {PREFECT_AVAILABLE}")
        print(f"   Prefect Configured: {PREFECT_CONFIGURED}")

        if PREFECT_AVAILABLE:
            print("   ✅ Prefect is available")
        else:
            print("   ⚠️  Prefect not installed (will use direct execution)")

        if PREFECT_CONFIGURED:
            print("   ✅ Prefect is configured")
        else:
            print("   ⚠️  Prefect not configured (will use direct execution)")

        return True

    except Exception as e:
        print(f"   ❌ Workflow setup check failed: {e}")
        return False


def main():
    """Run quick integration check"""
    print("=" * 60)
    print("QUICK INTEGRATION CHECK - NO EXTERNAL CALLS")
    print("=" * 60)

    checks = [check_imports(), check_configuration(), check_mock_responses(), check_workflow_setup()]

    passed = sum(checks)
    total = len(checks)

    print("\n" + "=" * 60)
    print("INTEGRATION CHECK SUMMARY")
    print("=" * 60)
    print(f"Checks Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 ALL INTEGRATION CHECKS PASSED!")
        print("✅ System is ready for external service integration")
        return True
    else:
        print("⚠️  Some integration checks failed")
        print("❌ Fix issues before proceeding")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
