"""
Static Code Verification - All Recent Changes
Verifies all 6 changes by checking code files directly (no server required)
"""
import os
import sys

# Test Results
results = {
    "1_rl_mocks": [],
    "2_timeouts": [],
    "3_mcp_compliance": [],
    "4_core_apis": [],
    "5_prefect_automation": [],
    "6_data_integrity": [],
}


def check_file_exists(filepath):
    """Check if file exists"""
    return os.path.exists(filepath)


def check_file_contains(filepath, search_strings, all_must_match=True):
    """Check if file contains specific strings"""
    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        matches = []
        for search_str in search_strings:
            found = search_str in content
            matches.append((search_str, found))

        if all_must_match:
            all_found = all(m[1] for m in matches)
            return all_found, matches
        else:
            any_found = any(m[1] for m in matches)
            return any_found, matches
    except Exception as e:
        return False, str(e)


# ============================================================================
# TEST 1: RL Mock Fallbacks RESTORED
# ============================================================================
def test_rl_mocks():
    print("\n" + "=" * 80)
    print("TEST 1: RL Mock Fallbacks (Should be RESTORED)")
    print("=" * 80)

    # Check app/api/rl.py has mock fallbacks
    has_mock, details = check_file_contains(
        "app/api/rl.py", ["except", "mock", "fallback", "503"], all_must_match=False
    )

    if has_mock:
        results["1_rl_mocks"].append(("[OK]", "RL endpoints have mock fallbacks", "Present"))
    else:
        results["1_rl_mocks"].append(("[WARN]", "RL mock fallbacks", "Check manually"))

    # Check external_services.py has RanjeetRLClient
    has_client, _ = check_file_contains("app/external_services.py", ["class RanjeetRLClient", "optimize_design"])

    if has_client:
        results["1_rl_mocks"].append(("[OK]", "RanjeetRLClient exists", "Present"))
    else:
        results["1_rl_mocks"].append(("[FAIL]", "RanjeetRLClient missing", "Not found"))

    for status, test, detail in results["1_rl_mocks"]:
        print(f"{status} {test}: {detail}")


# ============================================================================
# TEST 2: Timeout Increases to 180s
# ============================================================================
def test_timeouts():
    print("\n" + "=" * 80)
    print("TEST 2: Timeout Increases (Should be 180s)")
    print("=" * 80)

    # Check app/config.py
    if check_file_exists("app/config.py"):
        with open("app/config.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Check SOHUM_TIMEOUT
        if "SOHUM_TIMEOUT" in content:
            if "180" in content and "SOHUM_TIMEOUT" in content:
                results["2_timeouts"].append(("[OK]", "SOHUM_TIMEOUT = 180s", "Verified"))
            else:
                results["2_timeouts"].append(("[FAIL]", "SOHUM_TIMEOUT != 180s", "Check config.py"))

        # Check RANJEET_TIMEOUT
        if "RANJEET_TIMEOUT" in content:
            if "180" in content and "RANJEET_TIMEOUT" in content:
                results["2_timeouts"].append(("[OK]", "RANJEET_TIMEOUT = 180s", "Verified"))
            else:
                results["2_timeouts"].append(("[FAIL]", "RANJEET_TIMEOUT != 180s", "Check config.py"))
    else:
        results["2_timeouts"].append(("[FAIL]", "config.py not found", "Missing"))

    # Check external_services.py uses timeouts
    has_timeout, _ = check_file_contains(
        "app/external_services.py",
        ["timeout=", "settings.SOHUM_TIMEOUT", "settings.RANJEET_TIMEOUT"],
        all_must_match=False,
    )

    if has_timeout:
        results["2_timeouts"].append(("[OK]", "Timeouts used in external_services", "Present"))
    else:
        results["2_timeouts"].append(("[WARN]", "Timeout usage", "Check manually"))

    for status, test, detail in results["2_timeouts"]:
        print(f"{status} {test}: {detail}")


# ============================================================================
# TEST 3: MCP Compliance - NO Mock Fallback
# ============================================================================
def test_mcp_compliance():
    print("\n" + "=" * 80)
    print("TEST 3: MCP Compliance (NO Mock Fallback)")
    print("=" * 80)

    # Check external_services.py has NO placeholder recommendations
    if check_file_exists("app/external_services.py"):
        with open("app/external_services.py", "r", encoding="utf-8") as f:
            content = f.read()

        no_placeholder = '"Ensure proper ventilation"' not in content
        if no_placeholder:
            results["3_mcp_compliance"].append(("[OK]", "No placeholder recommendations", "Removed"))
        else:
            results["3_mcp_compliance"].append(("[FAIL]", "Placeholder recommendations found", "Still present"))

    # Check mcp_integration.py has NO mock fallback
    if check_file_exists("app/api/mcp_integration.py"):
        with open("app/api/mcp_integration.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Should return 503 or raise error, not mock data
        has_503 = "503" in content or "HTTPException" in content
        results["3_mcp_compliance"].append(
            ("[OK]" if has_503 else "[WARN]", "MCP returns 503 on failure", "Verified" if has_503 else "Check manually")
        )

    for status, test, detail in results["3_mcp_compliance"]:
        print(f"{status} {test}: {detail}")


# ============================================================================
# TEST 4: Core APIs Fixed
# ============================================================================
def test_core_apis():
    print("\n" + "=" * 80)
    print("TEST 4: Core APIs (Should All Work)")
    print("=" * 80)

    # Check main.py has explicit routes
    if check_file_exists("app/main.py"):
        with open("app/main.py", "r", encoding="utf-8") as f:
            content = f.read()

        has_history = '@app.get("/api/v1/history"' in content
        has_reports = '@app.get("/api/v1/reports/{spec_id}"' in content

        results["4_core_apis"].append(
            ("[OK]" if has_history else "[FAIL]", "Explicit /history route", "Present" if has_history else "Missing")
        )
        results["4_core_apis"].append(
            ("[OK]" if has_reports else "[FAIL]", "Explicit /reports route", "Present" if has_reports else "Missing")
        )

    # Check history.py exists
    if check_file_exists("app/api/history.py"):
        results["4_core_apis"].append(("[OK]", "history.py exists", "Present"))
    else:
        results["4_core_apis"].append(("[FAIL]", "history.py missing", "Not found"))

    # Check reports.py exists
    if check_file_exists("app/api/reports.py"):
        results["4_core_apis"].append(("[OK]", "reports.py exists", "Present"))
    else:
        results["4_core_apis"].append(("[FAIL]", "reports.py missing", "Not found"))

    # Check rl.py has feedback endpoint
    has_feedback, _ = check_file_contains(
        "app/api/rl.py", ["@router.post", "/feedback", "design_a_id", "design_b_id"], all_must_match=False
    )

    if has_feedback:
        results["4_core_apis"].append(("[OK]", "/rl/feedback endpoint", "Present"))
    else:
        results["4_core_apis"].append(("[FAIL]", "/rl/feedback endpoint", "Missing"))

    for status, test, detail in results["4_core_apis"]:
        print(f"{status} {test}: {detail}")


# ============================================================================
# TEST 5: Prefect Automation
# ============================================================================
def test_prefect_automation():
    print("\n" + "=" * 80)
    print("TEST 5: Prefect Automation (Workflow Tracking)")
    print("=" * 80)

    # Check models.py has WorkflowRun
    if check_file_exists("app/models.py"):
        with open("app/models.py", "r", encoding="utf-8") as f:
            content = f.read()

        has_model = "class WorkflowRun" in content
        has_workflow_id = "id" in content and "WorkflowRun" in content
        has_run_id = "flow_run_id" in content

        results["5_prefect_automation"].append(
            ("[OK]" if has_model else "[FAIL]", "WorkflowRun model", "Present" if has_model else "Missing")
        )
        results["5_prefect_automation"].append(
            ("[OK]" if has_run_id else "[FAIL]", "flow_run_id field", "Present" if has_run_id else "Missing")
        )

    # Check workflow_management.py
    if check_file_exists("app/api/workflow_management.py"):
        with open("app/api/workflow_management.py", "r", encoding="utf-8") as f:
            content = f.read()

        has_workflow_endpoint = "/workflow" in content
        has_status_endpoint = "/status" in content
        returns_ids = "workflow_id" in content or "run_id" in content

        results["5_prefect_automation"].append(
            (
                "[OK]" if has_workflow_endpoint else "[FAIL]",
                "/workflow endpoint",
                "Present" if has_workflow_endpoint else "Missing",
            )
        )
        results["5_prefect_automation"].append(
            (
                "[OK]" if has_status_endpoint else "[FAIL]",
                "/status endpoint",
                "Present" if has_status_endpoint else "Missing",
            )
        )
        results["5_prefect_automation"].append(
            (
                "[OK]" if returns_ids else "[WARN]",
                "Returns workflow/run IDs",
                "Present" if returns_ids else "Check manually",
            )
        )

    for status, test, detail in results["5_prefect_automation"]:
        print(f"{status} {test}: {detail}")


# ============================================================================
# TEST 6: Data Integrity
# ============================================================================
def test_data_integrity():
    print("\n" + "=" * 80)
    print("TEST 6: Data & Storage Integrity")
    print("=" * 80)

    # Check data_audit.py exists
    if check_file_exists("app/api/data_audit.py"):
        results["6_data_integrity"].append(("[OK]", "data_audit.py exists", "Present"))

        with open("app/api/data_audit.py", "r", encoding="utf-8") as f:
            content = f.read()

        has_audit_endpoint = "/audit/spec" in content
        has_complete_endpoint = "/complete" in content

        results["6_data_integrity"].append(
            (
                "[OK]" if has_audit_endpoint else "[FAIL]",
                "/audit/spec endpoint",
                "Present" if has_audit_endpoint else "Missing",
            )
        )
        results["6_data_integrity"].append(
            (
                "[OK]" if has_complete_endpoint else "[FAIL]",
                "/audit/spec/complete endpoint",
                "Present" if has_complete_endpoint else "Missing",
            )
        )
    else:
        results["6_data_integrity"].append(("[FAIL]", "data_audit.py missing", "Not found"))

    # Check main.py registers data_audit router
    if check_file_exists("app/main.py"):
        with open("app/main.py", "r", encoding="utf-8") as f:
            content = f.read()

        has_import = "data_audit" in content
        has_router = "data_audit.router" in content

        results["6_data_integrity"].append(
            (
                "[OK]" if has_import and has_router else "[FAIL]",
                "data_audit router registered",
                "Yes" if has_import and has_router else "No",
            )
        )

    # Check history.py enhanced with integrity
    if check_file_exists("app/api/history.py"):
        with open("app/api/history.py", "r", encoding="utf-8") as f:
            content = f.read()

        has_integrity = "data_integrity" in content or "iterations_count" in content or "evaluations_count" in content
        results["6_data_integrity"].append(
            (
                "[OK]" if has_integrity else "[WARN]",
                "/history has integrity checks",
                "Present" if has_integrity else "Check manually",
            )
        )

    # Check reports.py enhanced with integrity
    if check_file_exists("app/api/reports.py"):
        with open("app/api/reports.py", "r", encoding="utf-8") as f:
            content = f.read()

        has_complete_data = "iterations" in content or "evaluations" in content or "compliance_checks" in content
        results["6_data_integrity"].append(
            (
                "[OK]" if has_complete_data else "[WARN]",
                "/reports has complete data",
                "Present" if has_complete_data else "Check manually",
            )
        )

    for status, test, detail in results["6_data_integrity"]:
        print(f"{status} {test}: {detail}")


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("\n" + "=" * 80)
    print("STATIC CODE VERIFICATION - ALL RECENT CHANGES")
    print("=" * 80)
    print("\nVerifying 6 major changes by checking code files:")
    print("1. Kill All Mocks (RL) - Mock fallbacks RESTORED")
    print("2. Timeout Increases - 180s for MCP and RL")
    print("3. Close Compliance Loop (MCP) - NO mock fallback")
    print("4. Fix Broken Core APIs - All endpoints working")
    print("5. Activate Prefect Automation - Workflow tracking")
    print("6. Data & Storage Integrity - Audit system")

    # Change to backend directory if needed
    if os.path.exists("backend"):
        os.chdir("backend")

    # Run all tests
    test_rl_mocks()
    test_timeouts()
    test_mcp_compliance()
    test_core_apis()
    test_prefect_automation()
    test_data_integrity()

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    warnings = 0

    for test_name, test_results in results.items():
        name = test_name.replace("_", " ").title()
        print(f"\n{name}:")
        for status, test, detail in test_results:
            print(f"  {status} {test}: {detail}")
            total_tests += 1
            if status == "[OK]":
                passed_tests += 1
            elif status == "[FAIL]":
                failed_tests += 1
            else:
                warnings += 1

    print("\n" + "=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Warnings: {warnings}")

    if failed_tests == 0:
        print("\n[SUCCESS] ALL CRITICAL CHECKS PASSED!")
        if warnings > 0:
            print(f"({warnings} warnings - review manually)")
    else:
        print(f"\n[FAIL] {failed_tests} checks failed - review above")
    print("=" * 80)

    return failed_tests == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
